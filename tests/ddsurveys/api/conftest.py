#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
from ddsurveys.app import create_app
from ddsurveys.models import Base, get_engine
import os
from dotenv import load_dotenv

load_dotenv()


@pytest.fixture
def client():
    # Override DATABASE_URL with testing database
    os.environ['FLASK_ENV'] = "testing"
    os.environ['DATABASE_URL'] = "sqlite:///:memory:"

    app = create_app()
    # Force the schema to be created
    Base.metadata.create_all(get_engine(app))
    app.config['TESTING'] = True

    with app.test_client() as client:
        yield client
