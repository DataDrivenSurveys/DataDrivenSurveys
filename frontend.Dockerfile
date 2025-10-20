# This Dockerfile should build a frontend container image.

# Here we will use node as the base image.
FROM nginx:latest

# create a working directory inside the container.
WORKDIR /app

# Copy files from repo into container
ADD ./volumes/nginx/nginx.conf.template /etc/nginx/nginx.conf.template
ADD ./.env.deploy.local /.env.deploy.local
ADD ./frontend/build /var/www/frontend
ADD ./volumes/nginx/nginx-entrypoint.sh /nginx-entrypoint.sh

RUN apt update && apt install dos2unix

RUN dos2unix /nginx-entrypoint.sh && chmod +x /nginx-entrypoint.sh
