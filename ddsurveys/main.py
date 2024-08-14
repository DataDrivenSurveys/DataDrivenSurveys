#!/usr/bin/env python3
"""This module serves as the entry point for the Data-Driven Surveys Flask application. It initializes the Flask app by
calling the `create_app` function from the `app` module and then runs the app. This setup is designed to facilitate
the deployment and execution of the Flask application in a production or development environment.

The `create_app` function is responsible for configuring the Flask application, initializing app components, and
registering routes. Once the app is created and configured, it is run using Flask's built-in server, making the
Data-Driven Surveys platform accessible via a web interface.

Usage:
    Execute this script directly from the command line to start the Flask application:
    ```
    $ python this_script.py
    ```
"""

from typing import TYPE_CHECKING

from ddsurveys.app import create_app

if TYPE_CHECKING:
    from flask import Flask


def main() -> None:
    """The main function serves as the entry point for the Flask application. It creates an instance of the Flask app
    by calling the `create_app` function and then runs the app on the local development server.
    """
    app: Flask = create_app()
    app.run()


if __name__ == '__main__':
    main()
