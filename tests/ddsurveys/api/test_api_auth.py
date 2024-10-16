from __future__ import annotations

import json
from http import HTTPStatus
from typing import TYPE_CHECKING

from .utils.auth import get_user, me_endpoint, signin_endpoint, signup_endpoint

if TYPE_CHECKING:
    from flask.testing import FlaskClient


def test_auth_signup(client: FlaskClient):
    """Test the signup functionality of the authentication system.

    This function tests the following scenarios:
    1. Successful signup with valid user data.
    2. Attempt to signup with an already registered email.

    Args:
        client (FlaskClient): The test client used to make requests to the application.

    Returns:
        None
    """
    # Arrange
    jane_doe = get_user("jane_doe")
    # Act: Sign up with the test data
    response = client.post(signup_endpoint, data=json.dumps(jane_doe), content_type="application/json")

    # Assert
    assert response.status_code == HTTPStatus.OK
    assert json.loads(response.data)["message"]["id"] == "api.auth.registered_successfully"

    # Try signing up again with the same email
    response = client.post(signup_endpoint, data=json.dumps(jane_doe), content_type="application/json")
    assert response.status_code == 409
    assert json.loads(response.data)["message"]["id"] == "api.auth.user_already_exists"


def test_auth_signin(client):
    # Sign up first
    jane_doe = get_user("jane_doe")

    client.post(signup_endpoint, data=json.dumps(jane_doe), content_type="application/json")

    # Act: Sign in with the test data
    response = client.post(signin_endpoint, data=json.dumps(jane_doe), content_type="application/json")

    # Assert
    assert response.status_code == HTTPStatus.OK
    assert "token" in json.loads(response.data)

    # Try signing in with an incorrect password
    # copy the dict so we don't modify the original
    jane_doe = get_user("jane_doe")
    jane_doe["password"] = "wrongPassword123"
    response = client.post(signin_endpoint, data=json.dumps(jane_doe), content_type="application/json")
    assert response.status_code == 401
    assert json.loads(response.data)["message"]["id"] == "api.auth.invalid_username_or_password"


def test_auth_me(client: FlaskClient):
    """Test the /me endpoint of the authentication system.

    This function tests the following scenarios:
    1. Accessing the /me endpoint with a valid token.
    2. Attempting to access the /me endpoint without a token.

    Args:
        client (FlaskClient): The test client used to make requests to the application.

    Returns:
        None
    """
    # Sign up and Sign in first
    alice_smith = get_user("alice_smith")

    client.post(signup_endpoint, data=json.dumps(alice_smith), content_type="application/json")
    signin_response = client.post(signin_endpoint, data=json.dumps(alice_smith), content_type="application/json")
    token = json.loads(signin_response.data)["token"]

    headers = {"Authorization": f"Bearer {token}"}

    # Act: Access /me with the valid token
    response = client.get(me_endpoint, headers=headers)

    # Assert
    assert response.status_code == HTTPStatus.OK
    user_data = json.loads(response.data)["logged_in_as"]
    assert user_data["email"] == alice_smith["email"]

    # Access /me without a token
    response = client.get(me_endpoint)
    assert response.status_code == 401
