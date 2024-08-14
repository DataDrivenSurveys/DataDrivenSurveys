#!/usr/bin/env python3
import pytest

from ddsurveys.app import create_app
from ddsurveys.models import Base, DBManager


@pytest.fixture
def client():
    app = create_app()
    # Force the schema to be created
    Base.metadata.create_all(DBManager.get_engine(app))
    app.config['TESTING'] = True

    with app.test_client() as client:
        yield client
