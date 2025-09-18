FROM certbot/certbot

ADD ./.env.deploy.local /.env.deploy.local
ADD ./volumes/certbot/certbot-entrypoint.sh /certbot-entrypoint.sh

RUN dos2unix /certbot-entrypoint.sh
RUN chmod +x /certbot-entrypoint.sh
