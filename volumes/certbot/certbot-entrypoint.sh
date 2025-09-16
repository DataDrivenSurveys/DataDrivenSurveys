#!/bin/sh

# Source deployment variables
. /.env.deploy.local

# Path to the live certificate
live_cert="/etc/letsencrypt/live/${DDS_WEBSITE_URL}/fullchain.pem"

cert_obtained=true

if [ ! -f "$live_cert" ]; then
  echo "Certificate does not exist, attempting to obtain a new one..."
  certbot certonly --webroot -w /var/www/letsencrypt --agree-tos --email "${DDS_EMAIL}" -d "${DDS_WEBSITE_URL}"
  if [ $? -eq 0 ]; then
    cert_obtained=true
  else
    cert_obtained=false
  fi
fi

if [ "$cert_obtained" = true ]; then
  while :; do
    # If the certificate does exist, attempt to renew it
    echo "Certificate exists, checking for renewal..."
    certbot renew --webroot -w /var/www/letsencrypt

    # Sleep for 24h hours
    sleep 24h
  done
else
  echo "Failed to obtain a certificate, stopping..."
fi
