#Here we will use node as the base image.
FROM node:20

#create a working directory inside the container.
WORKDIR /app

#Environment variables.
ENV PATH /app/node_modules/.bin:$PATH

#copy the files from the host to the container.
COPY package.json ./
COPY package-lock.json ./

#install npm and react versions.
RUN npm install --silent
RUN npm install react-scripts@5.0.1 -g --silent

#install nodemon to provide hot-reloading functionality.
RUN npm install nodemon --save-dev

# Update browserslist database
RUN npx update-browserslist-db@latest

COPY . ./

#use nodemon to run the react application using npm.
CMD ["nodemon", "--exec", "npm", "start"]
