# Development Setup

We are using an approach of running the developement environment inside Docker using Docker Compose. The reason for this is that the Flask API uses gunicorn that is not compatible with Windows. 

The hot reload feature is insured by mounting the project root directory as volume in the container. 

It is possible to run the frontend locally and the backend inside the container. The frontend will be able to communicate with the backend using the `localhost` address. The eventual frontend container should be stopped to avoid port conflicts.

## Create .env files

#### Backend

Create a `.env` file in the `./ddssurveys` folder and add in the following variables:

The DATABASE_URL depends on the OS you are using. For UNIX, the host is `dds-db` and for Windows, the host is `localhost`.

The JWT_SECRET_KEY length depends on the algorithm you are using. We are using `HS256` algorithm, the length of the secret key should be 32 bytes. You can generate a secret key using the following command:

```bash
# generate a secret key of length 32 bytes
python -c "import os; import binascii; print(binascii.hexlify(os.urandom(32)))"
```

```bash
# for more detailed logs
FLASK_ENV="development"  
# both containers must be on the same network
FRONTEND_URL="http://localhost:3000"
DATABASE_URL="mysql+pymysql://root:root@db:3306/dds"

JWT_SECRET_KEY="please generate a secret key"
```

#### Frontend

Create a `.env` file in the `./frontend` folder and add in the following variables:

```bash
REACT_APP_API_URL="http://localhost:4000"
```

#### Run de development environment

Make sure you have pulled the latest changes from the repo. The docker compose will automatically run eventually database migrations.

Make sure no other running containers, or on host services, are using on any of the following ports: `4000`, `3000`, `3306`. You can just stop them.

NB: we might not port-map the db port in the future as its not necessary for it to be accessible from the host.

```bash
docker-compose -f docker-compose.dev.yml down # eventually

docker-compose -f docker-compose.dev.yml up
```

It might happen that the backend starts before the db is ready. In that case the backend will fail to start. Just restart the backend container.

#### Run command in backend

```bash
docker exec -it dds-dev-backend-1 bash
```

#### Run the Frontend on host

Make sure the .env file is created in the `./frontend` folder. As described above.

```bash
cd frontend # eventually

npm install # eventually

npm run start

```






