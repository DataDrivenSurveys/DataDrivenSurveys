# Dockerfile
FROM python:3.11

WORKDIR /app

# Copy only the necessary files for installation
# This includes setup.py, setup.cfg, and other relevant files
COPY setup.py setup.cfg ./
# If you have other directories or files needed for the setup, copy them too
COPY ddsurveys/ ddsurveys/

# Install the application
RUN pip install -e .

# Set the PYTHONPATH environment variable (if necessary)
ENV PYTHONPATH=/app

RUN chmod +x /app/ddsurveys/entrypoint.sh

# Set the entry point script
ENTRYPOINT ["/app/ddsurveys/entrypoint.sh"]

# Default command runs Gunicorn
CMD ["gunicorn", "ddsurveys.wsgi:app", "--bind", "0.0.0.0:4000", "--reload"]
