# Dockerfile
FROM python:3.11

# Install dos2unix
RUN apt-get update && apt-get install -y dos2unix

WORKDIR /app

# Copy only the necessary files for installation
# This includes pyproject.toml, and other relevant files
COPY pyproject.toml LICENSE ./
# If you have other directories or files needed for the setup, copy them too
COPY ddsurveys/ ddsurveys/

# Install the application
RUN pip install -e .

# Set the PYTHONPATH environment variable (if necessary)
ENV PYTHONPATH=/app

RUN dos2unix /app/ddsurveys/entrypoint.sh && chmod +x /app/ddsurveys/entrypoint.sh


# Set the entry point script
ENTRYPOINT ["sh", "/app/ddsurveys/entrypoint.sh"]


# Default command runs Gunicorn
CMD ["gunicorn", "ddsurveys.wsgi:app", "--bind", "0.0.0.0:4000", "--reload"]
