#!/bin/bash
# Script to build and deploy DDS to a generic server that can run docker

# Prompt user for remote sudo password
echo "Enter remote sudo password (SERVER_SUDO_PASSWORD). If there is no password, just press ENTER"
echo -n "Remote sudo password: "
read -s -r SERVER_SUDO_PASSWORD
echo

# Export variables if they were loaded from the deployment env file
if [ -f .env.deploy.local ]; then
  source .env.deploy.local
  # Variables for configuring the platform
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
  # Variables for ssh
  export SERVER_SSH_KEY
  export SERVER_USERNAME
  export SERVER_HOST
  # Variables for deployment
  export DEPLOY_BRANCH
  export FRESH_CLONE
fi

# Set variables with default values
export FRONTEND_URL="${FRONTEND_URL:-https://$DDS_WEBSITE_URL}"
export REACT_APP_API_URL="${REACT_APP_API_URL:-https://$DDS_WEBSITE_URL/api}"
export REACT_APP_FRONTEND_URL="${REACT_APP_FRONTEND_URL:-https://$DDS_WEBSITE_URL}"
export SELF_SIGNED_SSL="${SELF_SIGNED_SSL:-true}"
export DEPLOY_BRANCH="${DEPLOY_BRANCH:-main}"
export FRESH_CLONE="${FRESH_CLONE:-false}"

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
  # Variables for deployment
  "DEPLOY_BRANCH"
  "FRESH_CLONE"
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

# Clone the project using current clone for faster cloning
echo "Cloning project"
if [ "${FRESH_CLONE:-true}" = "true" ] && [ -d deployment ]; then
  rm -rf deployment
fi

# Update deployment or clone repo for deployment
if [ -d deployment ]; then
  cd deployment || exit 1
  echo "Pulling latest changes"
  git reset --hard HEAD
  git pull
else
  git clone --branch "${DEPLOY_BRANCH}" --single-branch .git deployment
  cd deployment || exit 1
fi

echo "Create .env.deploy.local for deployment"
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
EOF

echo "Generate .env.production.local for backend and frontend"
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
# The frontend is built outside of docker because running snap didn't work in docker.
# Without running snap, static pages aren't generated so the frontend doesn't work correctly.
echo "Build frontend"
cd frontend || exit 1

if [ -d build ]; then
  rm -rf build
  mkdir build
fi

npm run build-full

cd .. || exit 1

echo "Build docker container"
docker compose --env-file .env.deploy.local -f compose.yml build || exit 1

echo "Stop deployment docker and remove old project files/directories"
ssh -i "${SERVER_SSH_KEY}" "${ssh_address}" <<EOF
mkdir -p dds/volumes/db dds/volumes/self-signed-ssl dds/volumes/nginx
cd dds

if [ -f compose.yml ]; then
  echo '$SERVER_SUDO_PASSWORD' | sudo -S docker compose -f compose.yml down
fi
EOF

echo "Exporting docker containers"
if [[ -x $(command -v tqdm 2>/dev/null) ]]; then
  image="dds/backend:latest"
  name="dds_backend"
  echo "$image, $name"
  docker save "$image" | tqdm --desc "Saving $image image" --bytes --total "$(docker image inspect "$image" --format='{{.Size}}')" >"$name.tar"

  image="dds/frontend:latest"
  name="dds_frontend"
  echo "$image, $name"
  docker save "$image" | tqdm --desc "Saving $image image" --bytes --total "$(docker image inspect "$image" --format='{{.Size}}')" >"$name.tar"

  image="dds/certbot:latest"
  name="dds_certbot"
  echo "$image, $name"
  docker save "$image" | tqdm --desc "Saving $image image" --bytes --total "$(docker image inspect "$image" --format='{{.Size}}')" >"$name.tar"

  image="mariadb:latest"
  name="dds_mariadb"
  echo "$image, $name"
  docker save "$image" | tqdm --desc "Saving $image image" --bytes --total "$(docker image inspect "$image" --format='{{.Size}}')" >"$name.tar"
else
  image="dds/backend:latest"
  name="dds_backend"
  echo "Saving $image image"
  docker save "$image" >"$name.tar"

  image="dds/frontend:latest"
  name="dds_frontend"
  echo "Saving $image image"
  docker save "$image" >"$name.tar"

  image="dds/certbot:latest"
  name="dds_certbot"
  echo "Saving $image image"
  docker save "$image" >"$name.tar"

  image="mariadb:latest"
  name="dds_mariadb"
  echo "Saving $image image"
  docker save "$image" >"$name.tar"
fi

echo "Copying files to server"
rsync -ravz --exclude 'node_modules' --exclude '.git' --exclude '.gitignore' --exclude '.gitattributes' -e "ssh -o BatchMode=yes -i '${SERVER_SSH_KEY}'" . "${ssh_address}":dds/

ssh -o BatchMode=yes -i "${SERVER_SSH_KEY}" "${ssh_address}" <<EOF
cd dds

echo "Loading backend container"
echo '$SERVER_SUDO_PASSWORD' | sudo -S bash -c "cat dds_backend.tar | docker load"

echo "Loading frontend container"
echo '$SERVER_SUDO_PASSWORD' | sudo -S bash -c "cat dds_frontend.tar | docker load"

echo "Loading certbot container"
echo '$SERVER_SUDO_PASSWORD' | sudo -S bash -c "cat dds_certbot.tar | docker load"

echo "Loading mariadb container"
echo '$SERVER_SUDO_PASSWORD' | sudo -S bash -c "cat dds_mariadb.tar | docker load"

echo '$SERVER_SUDO_PASSWORD' | sudo -S bash -c "docker compose --env-file .env.deploy.local -f compose.yml up -d"
echo '$SERVER_SUDO_PASSWORD' | sudo -S bash -c "docker system prune -a -f"
EOF
