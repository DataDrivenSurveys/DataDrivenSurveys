#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

from .utils.auth import signup_endpoint, signin_endpoint, me_endpoint, get_user


def test_auth_signup(client):
    # Arrange
    jane_doe = get_user("jane_doe")
    # Act: Sign up with the test data
    response = client.post(signup_endpoint, data=json.dumps(jane_doe), content_type='application/json')

    # Assert
    assert response.status_code == 200
    assert json.loads(response.data)['message']['id'] == 'api.auth.registered_successfully'

    # Try signing up again with the same email
    response = client.post(signup_endpoint, data=json.dumps(jane_doe), content_type='application/json')
    assert response.status_code == 409
    assert json.loads(response.data)['message']['id'] == 'api.auth.user_already_exists'


def test_auth_signin(client):
    # Sign up first
    jane_doe = get_user("jane_doe")

    client.post(signup_endpoint, data=json.dumps(jane_doe), content_type='application/json')

    # Act: Sign in with the test data
    response = client.post(signin_endpoint, data=json.dumps(jane_doe), content_type='application/json')

    # Assert
    assert response.status_code == 200
    assert 'token' in json.loads(response.data)

    # Try signing in with an incorrect password
    # copy the dict so we don't modify the original
    jane_doe = get_user("jane_doe")
    jane_doe['password'] = "wrongPassword123"
    response = client.post(signin_endpoint, data=json.dumps(jane_doe), content_type='application/json')
    assert response.status_code == 401
    assert json.loads(response.data)['message']['id'] == 'api.auth.invalid_username_or_password'


def test_auth_me(client):
    # Sign up and Sign in first

    alice_smith = get_user("alice_smith")

    client.post(signup_endpoint, data=json.dumps(alice_smith), content_type='application/json')
    signin_response = client.post(signin_endpoint, data=json.dumps(alice_smith), content_type='application/json')
    token = json.loads(signin_response.data)['token']

    headers = {
        "Authorization": f"Bearer {token}"
    }

    # Act: Access /me with the valid token
    response = client.get(me_endpoint, headers=headers)

    # Assert
    assert response.status_code == 200
    user_data = json.loads(response.data)['logged_in_as']
    assert user_data['email'] == alice_smith['email']

    # Access /me without a token
    response = client.get(me_endpoint)
    assert response.status_code == 401
