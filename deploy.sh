#!/bin/bash
# Script to build and deploy DDS to a generic server that can run docker

# Export variables if they were loaded from the deployment env file
if [ -f .env.deploy.local ]; then
  source .env.deploy.local
  export DDS_WEBSITE_URL
  export NODE_ENV
  export DDS_ENV
  export DDS_WEBSITE_URL
  export DDS_EMAIL
  export DATABASE_URL
  export JWT_SECRET_KEY
  export FRONTEND_URL
  export APP_SURVEY_MONKEY_CLIENT_ID
  export APP_SURVEY_MONKEY_CLIENT_SECRET
  export REACT_APP_API_URL
  export REACT_APP_FRONTEND_URL
  export SELF_SIGNED_SSL
  export SERVER_SSH_KEY
  export SERVER_USERNAME
  export SERVER_HOST
fi

FRONTEND_URL='https://${DDS_WEBSITE_URL}'
REACT_APP_API_URL='https://${DDS_WEBSITE_URL}/api'
REACT_APP_FRONTEND_URL='https://${DDS_WEBSITE_URL}'

ssh_address="${SERVER_USERNAME}@${SERVER_HOST}"

# Check that all required environment variables are set
vars=(
  # Variables for configuring the platform
  "NODE_ENV"
  "DDS_ENV"
  "DDS_WEBSITE_URL"
  "DDS_EMAIL"
  "DATABASE_URL"
  "JWT_SECRET_KEY"
  "FRONTEND_URL"
  "APP_SURVEY_MONKEY_CLIENT_ID"
  "APP_SURVEY_MONKEY_CLIENT_SECRET"
  "REACT_APP_API_URL"
  "REACT_APP_FRONTEND_URL"
  "SELF_SIGNED_SSL"
  # Variables for ssh
  "SERVER_SSH_KEY"
  "SERVER_USERNAME"
  "SERVER_HOST"
)
missing_vars=()

for var in "${vars[@]}"; do
  if ! env | grep -q '^'"$var"'='; then
    missing_vars+=("$var")
  fi
done

if (("${#missing_vars[@]}" > 0)); then
  echo "The following environment variables must be set:"

  for var in "${missing_vars[@]}"; do
    echo "$var"
  done

  exit 1
fi

# Create .env.deploy.local in case it doesn't exist
cat >.env.deploy.local <<EOF
# Variables for configuring the platform
NODE_ENV="${NODE_ENV}"
DDS_ENV="${DDS_ENV}"
DDS_WEBSITE_URL="${DDS_WEBSITE_URL}"
DDS_EMAIL="${DDS_EMAIL}"
DATABASE_URL="${DATABASE_URL}"
JWT_SECRET_KEY="${JWT_SECRET_KEY}"
FRONTEND_URL="${FRONTEND_URL}"
APP_SURVEY_MONKEY_CLIENT_ID="${APP_SURVEY_MONKEY_CLIENT_ID}"
APP_SURVEY_MONKEY_CLIENT_SECRET="${APP_SURVEY_MONKEY_CLIENT_SECRET}"
REACT_APP_API_URL="${REACT_APP_API_URL}"
REACT_APP_FRONTEND_URL="${REACT_APP_FRONTEND_URL}"
SELF_SIGNED_SSL="${SELF_SIGNED_SSL}"
# Variables for ssh
SERVER_SSH_KEY="${SERVER_SSH_KEY}"
SERVER_USERNAME="${SERVER_USERNAME}"
SERVER_HOST="${SERVER_HOST}"
EOF

# Clone the project
# git clone --branch deploy-script --single-branch git@github.com:DataDrivenSurveys/DataDrivenSurveysInternal.git deployment

# cd deployment || exit 1

echo "Generate .env.production.local for ddsurveys and frontend."

echo DATABASE_URL="${DATABASE_URL}" >ddsurveys/.env.production.local
echo JWT_SECRET_KEY="${JWT_SECRET_KEY}" >>ddsurveys/.env.production.local
echo FRONTEND_URL="https://${DDS_WEBSITE_URL}" >>ddsurveys/.env.production.local
echo APP_SURVEY_MONKEY_CLIENT_ID="${APP_SURVEY_MONKEY_CLIENT_ID}" >>ddsurveys/.env.production.local
echo APP_SURVEY_MONKEY_CLIENT_SECRET="${APP_SURVEY_MONKEY_CLIENT_SECRET}" >>ddsurveys/.env.production.local
echo REACT_APP_API_URL="https://${DDS_WEBSITE_URL}/api" >frontend/.env.local
echo REACT_APP_FRONTEND_URL="https://${DDS_WEBSITE_URL}" >>frontend/.env.local
echo REACT_APP_API_URL="https://${DDS_WEBSITE_URL}/api" >frontend/.env.production.local
echo REACT_APP_FRONTEND_URL="https://${DDS_WEBSITE_URL}" >>frontend/.env.production.local

# Build frontend
echo "Build docker container"
dos2unix volumes/certbot/certbot-entrypoint.sh
dos2unix volumes/nginx/nginx-entrypoint.sh
dos2unix ddsurveys/entrypoint.sh
chmod +x volumes/certbot/certbot-entrypoint.sh
chmod +x volumes/nginx/nginx-entrypoint.sh
chmod +x ddsurveys/entrypoint.sh

docker compose --env-file .env.deploy.local -f compose.deploy.yml build || exit 1
# docker compose --env-file .env.deploy.local -f compose.deploy.yml build --pull --no-cache || exit 1

echo "Stop deployment docker and remove old project files/directories"
ssh -i "${SERVER_SSH_KEY}" "${ssh_address}" <<EOF
cd /home/admin/dds
sudo docker compose down
EOF
# cd /home/admin
# mv dds/volumes ./
# sudo rm -rf ./dds
# mkdir dds
# mv ./volumes ./dds/

echo "Creating production directory structure"
ssh -o BatchMode=yes -i "${SERVER_SSH_KEY}" "${ssh_address}" <<EOF
mkdir -p dds/volumes/db dds/volumes/self-signed-ssl
EOF

echo "Pushing new container to remote"
declare -A docker_images
docker_images=(
  ["dds_backend"]="dds/backend:latest"
  ["dds_frontend"]="dds/frontend:latest"
  ["dds_certbot"]="certbot/certbot"
  ["dds_mariadb"]="mariadb:latest"
)
docker_exported_images=()

if [[ -x $(command -v tqdm 2>/dev/null) ]]; then
  for name in "${!docker_images[@]}"; do
    image="${docker_images[${name}]}"
    echo "$image, $name"
    docker_exported_images+=("$name.tar")
    docker save "$image" | tqdm --desc "Saving $image image" --bytes --total "$(docker image inspect "$image" --format='{{.Size}}')" >"$name.tar"
  done
else
  for name in "${!docker_images[@]}"; do
    image="${docker_images[${name}]}"
    docker_exported_images+=("$name.tar")
    echo "Saving $image image"
    docker save "$image" >"$name.tar"
  done
fi

scp -o BatchMode=yes -B -i "${SERVER_SSH_KEY}" -p compose.deploy.yml .env.deploy.local "${docker_exported_images[@]}" "${ssh_address}":dds/
scp -o BatchMode=yes -B -i "${SERVER_SSH_KEY}" -r -p volumes/certbot volumes/nginx "${ssh_address}":dds/volumes
scp -o BatchMode=yes -B -i "${SERVER_SSH_KEY}" -r -p ddsurveys "${ssh_address}":dds/

ssh -o BatchMode=yes -i "${SERVER_SSH_KEY}" "${ssh_address}" <<EOF
cd dds
sudo bash -c "cat dds_backend.tar | docker load"
sudo bash -c "cat dds_frontend.tar | docker load"
sudo bash -c "cat dds_certbot.tar | docker load"
sudo bash -c "cat dds_mariadb.tar | docker load"
sudo bash -c "docker compose --env-file .env.deploy.local -f compose.deploy.yml up -d"
sudo bash -c "sudo docker system prune -a -f"
EOF
