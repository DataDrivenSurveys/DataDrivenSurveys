#!/bin/sh

export DOLLAR='$'
. /.env.deploy.local
export DDS_WEBSITE_URL="${DDS_WEBSITE_URL}"
export BACKEND_SERVICE_NAME="${BACKEND_SERVICE_NAME}"

if [ "$SELF_SIGNED_SSL" = "true" ]; then
  export SSL_CERTIFICATE="/etc/self-signed-ssl/fullchain.pem"
  export SSL_CERTIFICATE_KEY="/etc/self-signed-ssl/privkey.pem"
else
  export SSL_CERTIFICATE="/etc/letsencrypt/live/${DDS_WEBSITE_URL}-0002/fullchain.pem"
  export SSL_CERTIFICATE_KEY="/etc/letsencrypt/live/${DDS_WEBSITE_URL}-0002/privkey.pem"
fi

envsubst </etc/nginx/nginx.conf.template >/etc/nginx/nginx.conf
# && nginx -g 'daemon off;'

# Start NGINX
echo "Starting NGINX..."
nginx

# Check if NGINX is running
if [ $? -ne 0 ]; then
  echo "NGINX failed to start!"
  exit 1
fi

echo "NGINX started!"

# Loop indefinitely
while :; do
  # Sleep for a day
  sleep 1d

  echo "Reloading NGINX..."
  # Restart the service to reload the configuration and certificates
  nginx -s reload
done
