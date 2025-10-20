#!/bin/sh

# Source deployment variables
. /.env.deploy.local

if [ "${SELF_SIGNED_SSL}" = "true" ]; then
  CERT_DIR="/etc/self-signed-ssl"
  PRIVKEY_PATH="$CERT_DIR/privkey.pem"
  FULLCHAIN_PATH="$CERT_DIR/fullchain.pem"
  DAYS_VALID=365

  while true; do
    if [ -f "$PRIVKEY_PATH" ] && [ -f "$FULLCHAIN_PATH" ]; then
      # Certificate exists, check if expiring within 10 days
      EXPIRY_DATE_STR="$(openssl x509 -in "$FULLCHAIN_PATH" -noout -checkend 864000)"

      # Check if renewal is needed
      if [ "$EXPIRY_DATE_STR" = "Certificate will expire" ]; then
        echo "Renewal threshold reached. Renewing certificate..."

        # Generate new certificate
        openssl req -x509 -nodes -days "$DAYS_VALID" -newkey rsa:4096 -keyout "$PRIVKEY_PATH" -out "$FULLCHAIN_PATH" -subj "/CN=localhost"

        echo "Certificate renewed."
      else
        echo "Certificate is still valid. No renewal needed."
      fi
    else
      # Certificate does not exist, generate it
      echo "Certificate not found. Generating new certificate..."
      mkdir -p "$CERT_DIR"

      openssl req -x509 -nodes -days "$DAYS_VALID" -newkey rsa:4096 -keyout "$PRIVKEY_PATH" -out "$FULLCHAIN_PATH" -subj "/CN=localhost"

      echo "New certificate generated."
    fi

    echo "Sleeping for 1 day..."
    sleep 1d
  done
else
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
fi
