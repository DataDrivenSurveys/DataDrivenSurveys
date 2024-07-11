#!/bin/bash
set -e

# Optional: Wait for the database to be ready
# Example using nc (netcat), ensure it's installed in your Docker image
# while ! nc -z db 3306; do
#   echo "Waiting for database..."
#   sleep 1
# done

# Run Alembic migrations
echo "Running Alembic migrations..."
cd /app/ddsurveys
{
  alembic upgrade head
} || {
  echo "Probably failed to connect to the database."
  echo "Waiting 3 seconds before retrying"
  sleep 3
  alembic upgrade head
}


cd /app

# Start the application
echo "Starting application..."
exec gunicorn "ddsurveys.wsgi:app" --bind "0.0.0.0:4000" --reload
