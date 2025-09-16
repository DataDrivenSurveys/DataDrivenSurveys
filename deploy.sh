#!/bin/bash

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
DEPLOYMENT_DIR="$SCRIPT_DIR/deployment"

# Predefine some variables

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

# Clone the project
git clone git@github.com:DataDrivenSurveys/DataDrivenSurveysInternal.git deployment

cd deployment || exit 1

echo "Generate .env.production.local for ddsurveys and frontend."

echo DATABASE_URL="${DATABASE_URL}" >ddsurveys/.env.production.local
echo JWT_SECRET_KEY="${JWT_SECRET_KEY}" >>ddsurveys/.env.production.local
echo FRONTEND_URL="${FRONTEND_URL}" >>ddsurveys/.env.production.local
echo APP_SURVEY_MONKEY_CLIENT_ID="${APP_SURVEY_MONKEY_CLIENT_ID}" >>ddsurveys/.env.production.local
echo APP_SURVEY_MONKEY_CLIENT_SECRET="${APP_SURVEY_MONKEY_CLIENT_SECRET}" >>ddsurveys/.env.production.local
echo REACT_APP_API_URL="${REACT_APP_API_URL}" >frontend/.env
echo REACT_APP_FRONTEND_URL="${FRONTEND_URL}" >>frontend/.env
echo REACT_APP_API_URL="${REACT_APP_API_URL}" >frontend/.env.production.local
echo REACT_APP_FRONTEND_URL="${FRONTEND_URL}" >>frontend/.env.production.local

echo "Generate .env.deploy.local"
for var in "${vars[@]}"; do
  echo "${var}=${!var}" >>.env.deploy.local
done

# Build frontend
echo "Build docker container"
docker compose --env-file .env.deploy.local -f compose.deploy.yml up --build -d

# echo "Stop deployment docker and remove old project files/directories"
# passphrase: ${{ secrets.SERVER_SSH_KEY_PASSPHRASE }} # Passphrase for the private key
# ssh -i "${SERVER_SSH_KEY}" "${ssh_address}" <<EOF
# cd /home/admin/dds
# sudo docker compose down
# cd /home/admin
# mv dds/volumes ./
# sudo rm -rf ./dds
# mkdir dds
# mv ./volumes ./dds/
# EOF

echo "Pushing new container to remote"
docker save dds | ssh -C -i "${SERVER_SSH_KEY}" "${ssh_address}" docker load

ssh -i "${SERVER_SSH_KEY}" "${ssh_address}" "sudo docker system prune -a -f"
