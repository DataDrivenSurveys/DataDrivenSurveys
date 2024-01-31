#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from flask import Flask

from .app import create_app

def main():
    app: Flask = create_app()
    app.run()


if __name__ == '__main__':
    main()
