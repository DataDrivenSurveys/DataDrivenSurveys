#!/usr/bin/env python3
"""This module is a template file that can be used as a starting point for creating your own data providers.
You will need to replace the elipses (...) with the correct classes and code.

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
@author: Stefan Teofanovic (stefan.teofanovic@heig-vd.ch)
"""
__all__ = ["SpotifyDataProvider"]

from collections.abc import Callable
from functools import cached_property
from http import HTTPStatus
from typing import Any, ClassVar
import base64
import requests
from urllib.parse import urlencode
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from ddsurveys.data_providers.data_categories import DataCategory

from ddsurveys.data_providers.bases import FormField, OAuthDataProvider
from ddsurveys.data_providers.variables import BuiltInVariable, CVAttribute
from ddsurveys.get_logger import get_logger
from ddsurveys.variable_types import TVariableFunction, VariableDataType

# Import the required libraries to make this work

logger = get_logger(__name__)

# In practice, each endpoint can be turned into a data category.
# 'self' in extractor functions will be an instance of the data provider class.
class PlaylistCount(DataCategory["SpotifyDataProvider"]):

    data_origin = [
        {
            "method": "playlist_count",
            "endpoint": "https://api.spotify.com/v1/me/playlists",
            "documentation": "https://developer.spotify.com/documentation/web-api/reference/get-playlist",
        }
    ]

    def fetch_data(self) -> list[dict[str, Any]]:
        pass

    builtin_variables = [
        BuiltInVariable.create_instances(
            name="spotify_playlist_count",
            label="User's playlist count",
            description="The number of playlists the user has.",
            test_value_placeholder="2020-01-01",
            data_type=VariableDataType.NUMBER,
            info="This shows the number of playlists the user has.",
            extractor_func=lambda self: self.playlist_count,
            data_origin=[
                {
                    "method": "playlists",
                    "endpoint": "https://api.fitbit.com/1/user/[user-id]/profile.json",
                    "documentation": "https://dev.fitbit.com/build/reference/web-api/user/get-profile/",
                },
            ],
        )
    ]


class SpotifyDataProvider(OAuthDataProvider):
    # Class attributes that need be re-declared or redefined in child classes
    # The following attributes need to be re-declared in child classes.
    # You can copy and paste them into the child class body.
    # When copying a template file, leave them unchanged.
    all_initial_funcs: dict[str, Callable] = {}  # Leave unchanged.
    factory_funcs: dict[str, Callable] = {}  # Leave unchanged.
    variable_funcs: dict[str, TVariableFunction] = {}  # Leave unchanged.
    fields: list[dict[str, Any]] = {}  # Leave unchanged.

    # Update the following attributes:
    app_creation_url: str = "https://developer.spotify.com/dashboard/create"  
    instructions_helper_url: str = "https://developer.spotify.com/documentation/web-api/concepts/apps"  

    # Unique class attributes go here
    _scopes: ClassVar[tuple[str,...]] = (
    'playlist-read-private '         # Read private playlists
    'playlist-read-collaborative '   # Read collaborative playlists
    'playlist-modify-public '        # Create and edit public playlists
    'playlist-modify-private '       # Create and edit private playlists
    'user-library-read '             # Read user's saved tracks and albums
    'user-library-modify '           # Add/remove tracks to user's library
    'user-read-recently-played '     # Access user's recently played tracks
    'user-top-read '                 # Read user's top artists and tracks
    'user-read-private '             # Read user's private info
    'user-read-email ',              # Read user's email address
    )

    # See other classes for examples of how to fill these attributes. You may not need to fill them (You definitely need to fill them)
    _categories_scopes = {'PlaylistCount': _scopes[0]}

    # Form fields that will be displayed in the frontend. Only update them if the data provider uses different
    # terminology for this information.
    form_fields = [
        FormField(name="client_id", type="text", required=True, data={}),
        FormField(name="client_secret", type="text", required=True, data={}),
    ]

    # List all the data categories that this data provider supports.
    # Just enter the names of the classes.
    data_categories: ClassVar[tuple[type[DataCategory["SpotifyDataProvider"]], ...]] = (
        PlaylistCount,
     )

    # In the functions below, update the elipses (...) with the correct classes and code.

    def __init__(self, **kwargs):
        """Initialization function.

        Args:
            client_id:
            client_secret:
            access_token:
            refresh_token:
            **kwargs:
        """
        super().__init__(**kwargs)
        self.api_client: spotipy.Spotify
        self.oauth_client: SpotifyOAuth
        self.redirect_uri = self.get_redirect_uri()
        self.playlists: dict[str, Any] = {}

        if self.client_id is not None or self.client_secret is not None:
            self.init_oauth_client()
            if self.access_token is not None and self.refresh_token is not None:
                self.init_api_client(self.access_token, self.refresh_token)

    # OAuthBase methods
    def init_api_client(
        self, access_token: str | None = None, refresh_token: str | None = None, code: str | None = None
    ) -> None:
        
        if access_token is not None:
            self.access_token = access_token
        if refresh_token is not None:
            self.refresh_token = refresh_token

        self.api_client = spotipy.Spotify(auth=self.access_token) # to get the playlists and so on, we only need to use an access_token

    def init_oauth_client(self, *args, **kwargs) -> None:
        self.oauth_client = SpotifyOAuth(client_id=self.client_id, client_secret=self.client_secret, redirect_uri=self.redirect_uri, scope=self.__class__._scopes[0])

    def get_authorize_url(
        self, builtin_variables: list[dict], custom_variables: list[dict] | None = None
    ) -> str: 
        return self.oauth_client.get_authorize_url()

    def get_client_id(self) -> str: 
        return self.client_id

    def request_token(self, data: dict[str, Any]) -> dict[str, Any]: 
        url_params = data["url_params"]
        code: str | None = url_params.get("code", None)

        if code is None:
            logger.debug('Spotify: code was None')
            response = {
                "success": False,
                "message_id": "api.data_provider.exchange_code_error.no_code",
                "text": "Failed to get the access to the data provider.",
            }

            error = url_params.get("error", "")
            error_description = url_params.get("error_description", "")

            if error == "access_denied" and error_description == "The user denied the request.":
                response["message_id"] = "api.data_provider.exchange_code_error.access_denied"
                response["text"] = error_description

            return response
        try:
            token_info = self.oauth_client.get_access_token(code, as_dict=True)
            access_token = token_info['access_token']
            self.api_client = spotipy.Spotify(auth=access_token)
            user = self.api_client.current_user()
            refresh_token = token_info['refresh_token']
            user_info = {
                'username': user['display_name'],
                'user_id': user['id']
            }

            if not user or not user_info['user_id']:
                logger.exception("Error in Spotify API call. User or userId was null.")
                return {
                    "success": False,
                    "message_id": "api.data_provider.exchange_code_error.general_error",
                }
        except requests.HTTPError:
            logger.exception("HTTP error when exchanging Fitbit code for token. Status code.")
            return {
                "success": False,
                "message_id": "api.data_provider.exchange_code_error.general_error",
            }
        
        except Exception as e:
            logger.exception("Error exchanging Spotify code for token: %s", e)
            return {
                    "success": False,
                    "message_id": "api.data_provider.exchange_code_error.general_error",
                }

        return {
                "success": True,
                "access_token": access_token,
                "refresh_token": refresh_token,  # Instagram doesn't provide refresh token in this flow
                "user_id": user_info['user_id'],
                "user_name": user_info['username'],
            }

    def revoke_token(self, token: str) -> bool: 
        return False
    
    @cached_property
    def playlist_count(self):
        self.playlists = self.api_client.current_user_playlists()
        return len(self.playlists['items'])

    # DataProvider methods
    def test_connection_before_extraction(self) -> bool: 
        return self.test_connection()

    def test_connection(self) -> bool: 
        # send request for access token
        auth_str = f"{self.client_id}:{self.client_secret}"
        b64_auth_str = base64.b64encode(auth_str.encode()).decode()

        # Step 1: Get access token
        token_url = 'https://accounts.spotify.com/api/token'
        headers = {
            'Authorization': f'Basic {b64_auth_str}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {
            'grant_type': 'client_credentials'
        }
        response = requests.post(token_url, headers=headers, data=data)
        return response.status_code == HTTPStatus.OK

    @cached_property
    def account_creation_date(self) -> str: ...


####### Added 

"""
class SpotifyAPIClient:
    API_BASE = "https://api.spotify.com/v1"

    def __init__(self, access_token: str):
        self.access_token = access_token

    def _headers(self):
        return {"Authorization": f"Bearer {self.access_token}"}

    # returns list of dictionaries
    def get_user_playlists(self):
        print("We called get_user_playlists")
        url = f"{self.API_BASE}/me/playlists"
        response = requests.get(url, headers=self._headers())
        response.raise_for_status()
        return response.json().get("items", [])

    # returns list of dictionaries
    def get_user(self):  # matches the method in ExampleDataCategory
        return self.get_user_playlists()
    

class SpotifyOAuthClient:
    AUTH_URL = "https://accounts.spotify.com/authorize"
    TOKEN_URL = "https://accounts.spotify.com/api/token"

    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

    def get_authorization_url(self, scopes: list[str]) -> str:
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "scope": " ".join(scopes),
            "redirect_uri": self.redirect_uri,
        }
        return f"{self.AUTH_URL}?{urlencode(params)}"

    def exchange_code_for_token(self, code: str):
        auth_header = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
        headers = {
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri
        }
        response = requests.post(self.TOKEN_URL, data=data, headers=headers)
        response.raise_for_status()
        return response.json()

    def refresh_token(self, refresh_token: str):
        auth_header = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
        headers = {
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }
        response = requests.post(self.TOKEN_URL, data=data, headers=headers)
        response.raise_for_status()
        return response.json()
"""