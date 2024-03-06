# Update the database schema with the new migration

We are using Alembic to manage the database migrations. It is necessary to communiocate the changes in the models with other developers to avoid conflicts.

### You pulled the latest changes from the repo

If you pulled the latest changes from the repo, you need to run the following command:

```bash
alembic upgrade head
```

This will make sure your database schema is up to date with the latest changes.

### You chnaged the models and want to update the database schema

To reflect your changes in the database schema, you need to run the following command:

```bash

# make sure the backend container is running and check the docker compose name and container name

docker exec -it dds-dev-backend-1 bash

cd /app/ddsurveys

# Detect the changes in the models and generate a new migration
alembic revision --autogenerate -m "Your message"

# you should see some detected changes in the models displayed in the console
# a new miration file should be created in the folder ddsurvey/alembic/versions with a name similar to this one: 2a3b4c5d6e7f_your_message.py

# Apply the migration to the database
alembic upgrade head
```

Make sure to commit the migration file to the repo.

### Rollback a migration

To rollback a revision in Alembic, you can use the alembic downgrade command followed by the revision identifier. The revision identifier is the alphanumeric string at the start of the migration file's name.

If you want to rollback the last revision, you can use:

```bash
alembic downgrade -1
```	
This command tells Alembic to downgrade one step from the current database version.

If you know the exact revision identifier you want to downgrade to, you can use:

```bash
alembic downgrade <revision_id>
```	

### Reapply a migration

First, you need to rollback the migration you want to reapply. Then, you can apply it again.

```bash
alembic downgrade <revision_id>
alembic upgrade head
```
Now update the revision script in the alembic/versions folder and commit it to the repo.

Apply the updated migration to the database

```bash
alembic upgrade head
# or
alembic upgrade <revision_id>
```

### Failed database migration

You can delete the database volume in : ./volumes/db

```bash
docker-compose -f docker-compose.dev.yml down
rm -rf ./volumes/db # unix
rd /s /q .\volumes\db # windows
docker-compose -f docker-compose.dev.yml up 
# re run the backend since it will fail to start the first time (db not initialised)

```

