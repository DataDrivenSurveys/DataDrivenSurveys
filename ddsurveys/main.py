"""This module serves as the entry point for the Data-Driven Surveys Flask application.

It initializes the Flask app by calling the `create_app` function from the `app` module
and then runs the app. This setup is designed to facilitate the deployment and execution
of the Flask application in a production or development environment.

The `create_app` function is responsible for configuring the Flask application,
initializing app components, and registering routes.
Once the app is created and configured, it is run using Flask's built-in server, making
the Data-Driven Surveys platform accessible via a web interface.

Usage:
    Execute this script directly from the command line to start the Flask application:
    ```
    $ python this_script.py
    ```
"""


def main() -> None:
    """The main function serves as the entry point for the Flask application.

    It creates a Flask application by importing it and then runs it.
    """
    from ddsurveys.app import app
    app.run()


if __name__ == '__main__':
    main()
