"""This script serves as the entry point for a Flask application.

It initializes the application using a factory pattern and runs the server
if the script is executed directly.
"""
from ddsurveys.app import app

if __name__ == "__main__":
    app.run()
