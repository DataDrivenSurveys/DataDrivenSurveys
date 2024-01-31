#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
from ddsurveys.app import create_app
import os
from dotenv import load_dotenv

load_dotenv()


@pytest.fixture
def client():
    # Override DATABASE_URL with testing database
    os.environ['FLASK_ENV'] = "testing"
    os.environ['DATABASE_URL'] = "sqlite:///:memory:"

    app = create_app()
    app.config['TESTING'] = True

    with app.test_client() as client:
        yield client
