#!/bin/sh
# Wait for the Certbot service to finish fetching the certificate
sleep 5

live_cert="/etc/letsencrypt/live/${DDS_WEBSITE_URL}/fullchain.pem"

# Check if the certificate exists
if [ ! -f "$live_cert" ]; then
  # Check if the directory for the certificate exists
  if [ ! -d "/etc/letsencrypt/live/${DDS_WEBSITE_URL}" ]; then
    mkdir -p "/etc/letsencrypt/live/${DDS_WEBSITE_URL}"
  fi
  # Generate the certificate using certbot
  certbot certonly --webroot -w /var/www/certbot -d "${DDS_WEBSITE_URL}" --email "${DDS_EMAIL}" --agree-tos --no-eff-email --force-renewal
  sleep 10
fi
