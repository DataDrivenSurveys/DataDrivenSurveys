#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2023-08-31 16:59

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
"""

__all__ = "InstagramDataProvider"

from typing import Callable, Dict, Any

import requests

from .bases import OAuthDataProvider, FormField
from .variables import BuiltInVariable
from .data_categories import DataCategory
from ..get_logger import get_logger
from ..variable_types import TVariableFunction, VariableDataType


logger = get_logger(__name__)

class Media(DataCategory):

   cv_attributes = []
   builtin_variables = [
      BuiltInVariable.create_instances(
        name="media_count",
        label="Media Count",
        description="Number of media posts.",
        data_type=VariableDataType.NUMBER,
        test_value_placeholder="2020-01-01",
        info="This will be the date that the respondent's Instagram account was created. It will be in YYYY-MM-DD format.",
        extractor_func= lambda self: self.media_count,
        data_origin=[{
            "method": "media_count",
            "endpoint": "https://graph.instagram.com/v11/me?fields=media_count&access_token=[access_token]",
            "documentation": "https://developers.facebook.com/docs/instagram-basic-display-api/reference/user#fields"
        }]
      )
    ]


class InstagramDataProvider(OAuthDataProvider):
    # General class attributes


    # These attributes need to be overridden
    app_creation_url: str = "https://developers.facebook.com/apps/creation/"
    dds_app_creation_instructions: str = ""

    token_url = "https://api.instagram.com/oauth/access_token"
    base_authorize_url = "https://api.instagram.com/oauth/authorize"

    # Class attributes that need be redeclared or redefined in child classes
    # The following attributes need to be redeclared in child classes.
    # You can just copy and paste them into the child class body.
    all_initial_funcs: dict[str, Callable] = {}
    factory_funcs: dict[str, Callable] = {}
    variable_funcs: dict[str, TVariableFunction] = {}
    fields: list[dict[str, Any]] = {}
    variables: list[dict[str, Any]] = {}

    # Unique class attributes go here

    # Form fields declarations go here
    form_fields = [
        FormField(
            name="client_id",
            type="text",
            required=True,
            data={
                # "helper_url": "https://developers.facebook.com/docs/instagram-basic-display-api/getting-started"
            }
        ),
        FormField(
            name="client_secret",
            type="text",
            required=True,
            data={
                # "helper_url": "https://developers.facebook.com/docs/instagram-basic-display-api/getting-started"
            }
        ),
    ]

    data_categories = [
        Media
    ]

    # Assuming the use of the latest API version (as of September 2021)
    api_version = "v11.0"
    user_id = "me"  # You can adjust this if needed


    def media_count(self):
        try:

            media_count_url = f"https://graph.instagram.com/{api_version}/{user_id}?fields=media_count&access_token={self.access_token}"

            response = requests.get(media_count_url)
            response.raise_for_status()

            data = response.json()
            return data.get("media_count")
        except Exception as e:
            logger.error(f"Error fetching media count from Instagram: {e}")
            return None


    # Standard/builtin class methods go here
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    # Methods that child classes must implement
    def init_api_client(self, *args, **kwargs) -> None:
        pass

    def init_oauth_client(self, *args, **kwargs) -> None:
        pass

    def get_authorize_url(self, builtin_variables: list[dict] = None, custom_variables: list[dict] = None) -> str:
        """
        Returns the authorize url.

        Args:
            builtin_variables (list[dict], optional): A list of builtin variables. Defaults to None.
            custom_variables (list[dict], optional): A list of custom variables. Defaults to None.

        Returns:
            str: The authorize url.
        """
        # Construct the 'authorize' url
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": "user_profile,user_media",
            "response_type": "code",
        }
        url = requests.Request('GET', self.base_authorize_url, params=params).prepare().url
        return url

    def get_client_id(self) -> str:
        return self.client_id

    def request_token(self, code: str) -> Dict[str, Any]:
        """
        Exchange the authorization code for an Instagram User Access Token and retrieve the user's profile.

        Args:
            code (str): The authorization code provided by Instagram upon user's consent.

        Returns:
            dict: A dictionary containing the result, which includes tokens, user information,
                or an error message in case of failure.
        """
        try:
            # Exchange the authorization code for a short-lived Instagram User Access Token.
            headers = {
                "accept": "application/json",
            }
            data = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "authorization_code",
                "redirect_uri": self.get_redirect_uri(),
                "code": code,
            }
            response = requests.post(self.token_url, headers=headers, data=data)
            response.raise_for_status()  # raises an HTTPError if the HTTP request returned an unsuccessful status code

            token_data = response.json()

            access_token = token_data.get("access_token")
            user_id = token_data.get("user_id")

            if not access_token or not user_id:
                return {
                    "success": False,
                    "message_id": "api.data_provider.exchange_code_error.general_error"
                }

            # At this point, for Instagram, we know the user has accepted the full scope.
            # Fetch user_name using Basic Display API
            profile_url = f"https://graph.instagram.com/me?fields=username&access_token={access_token}"
            profile_response = requests.get(profile_url)
            profile_response.raise_for_status()

            profile_data = profile_response.json()

            logger.info(f"Instagram profile_data: {profile_data}")

            user_name = profile_data.get("username")

            if not user_name:
                return {
                    "success": False,
                    "message_id": "api.data_provider.exchange_code_error.general_error"
                }

            return {
                "success": True,
                "access_token": access_token,
                "refresh_token": None,  # Instagram doesn't provide refresh token in this flow
                "user_id": user_id,
                "user_name": user_name
            }

        except requests.HTTPError:
            logger.error(
                    f"HTTP error when exchanging Instagram code for token. Status code: {response.status_code}")
            return {
                "success": False,
                "message_id": "api.data_provider.exchange_code_error.general_error"
            }
        except Exception as e:
            logger.error(f"Error exchanging Instagram code for token: {e}")
            return {
                "success": False,
                "message_id": "api.data_provider.exchange_code_error.general_error"
            }

    def revoke_token(self, token: str) -> bool:
        pass

    def test_connection_before_extraction(self) -> bool:
        try:
            # Use the access token to fetch the user's profile information
            profile_url = f"https://graph.instagram.com/me?fields=username&access_token={self.access_token}"
            profile_response = requests.get(profile_url)
            profile_response.raise_for_status()

            profile_data = profile_response.json()
            user_name = profile_data.get("username")

            logger.info(f"Instagram profile_data: {profile_data}")

            if not user_name:
                return False

        except Exception as e:
            logger.error(f"Error connecting to Instagram: {e}")
            return False
        return True

    def test_connection(self) -> bool:
        # Using client credentials flow to check if the app id and secret are valid
        headers = {
            "accept": "application/json",
        }
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "authorization_code",
            "redirect_uri": self.get_redirect_uri(),
            "code": "<test-code>",  # replace with a test code
        }
        try:
            response = requests.post(self.token_url, headers=headers, data=data)
            logger.debug(f"Instagram connect response: {response.json()}")
            success = response.status_code == 200
            if response.status_code != 200:
                error = response.json().get("error_message")
                if error == 'Invalid platform app' or error == 'Invalid Client ID':
                    success = False
                else:
                    success = True
            return success  # Returns the status code. In real use, you'd want to handle different response codes differently.
        except Exception as e:
            logger.error(f"Error connecting to Instagram: {e}")
            return False

    # Properties to access class attributes

    # Class methods

    # Instance properties

    # Instance methods

    # Cached API responses
    # API calls should be wrapped in properties using @cached_property decorators

    # Extractor functions
    # These are functions that extract user data from the API
