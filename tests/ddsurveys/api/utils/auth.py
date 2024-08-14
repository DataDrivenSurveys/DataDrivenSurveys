#!/usr/bin/env python3

import json

signup_endpoint = '/auth/signup'
signin_endpoint = '/auth/signin'
me_endpoint = '/auth/me'

users = {
    "jane_doe": {
       "firstname": "John",
        "lastname": "Doe",
        "email": "johndoe@example.com",
        "password": "securePassword123"
    },
    "alice_smith": {
        "firstname": "Alice",
        "lastname": "Smith",
        "email": "alicesmith@example.com",
        "password": "securePassword789"
    }
}

def get_user(lastname):
    # Return a copy of the user dict so we don't modify the original
    return users.get(lastname).copy()

# Utility function for signing up and signing in a test user.
def authenticate_test_user(client, test_user=users.get("jane_doe")):
    client.post(signup_endpoint, data=json.dumps(test_user), content_type='application/json')
    signin_response = client.post(signin_endpoint, data=json.dumps(test_user), content_type='application/json')
    token = json.loads(signin_response.data)['token']

    return {
        "Authorization": f"Bearer {token}"
    }
