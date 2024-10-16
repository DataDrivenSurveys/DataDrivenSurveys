from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from ddsurveys.models import Base, DBManager

if TYPE_CHECKING:
    from collections.abc import Generator

    from flask import Flask


@pytest.fixture
def client() -> Generator[Flask, None, None]:
    from ddsurveys.app import app

    # Create the database schema
    Base.metadata.create_all(DBManager.get_engine(app))
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client
