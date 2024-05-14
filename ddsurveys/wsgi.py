#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This script serves as the entry point for a Flask application. It initializes the application
using a factory pattern and runs the server if the script is executed directly.
"""
from flask import Flask

from .app import create_app

app: Flask = create_app()

if __name__ == "__main__":
    app.run()
