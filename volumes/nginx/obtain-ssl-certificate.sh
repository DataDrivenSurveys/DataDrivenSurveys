#!/bin/sh
# Wait for the Certbot service to finish fetching the certificate
sleep 5

# Check if the certificate exists
if [ ! -f /etc/letsencrypt/live/www.datadrivensurvey.com/fullchain.pem ]; then
   # Check if the directory for the certificate exists
    if [ ! -d /etc/letsencrypt/live/www.datadrivensurvey.com ]; then
        mkdir -p /etc/letsencrypt/live/www.datadrivensurvey.com
    fi
    # Generate the certificate using certbot
    certbot certonly --webroot -w /var/www/certbot -d www.datadrivensurvey.com --email no-reply@datadrivensurvey.com --agree-tos --no-eff-email --force-renewal
    sleep 10
fi
