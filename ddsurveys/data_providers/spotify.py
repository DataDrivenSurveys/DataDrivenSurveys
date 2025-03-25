#!/usr/bin/env python3
"""This module is a template file that can be used as a starting point for creating your own data providers.
You will need to replace the elipses (...) with the correct classes and code.

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
@author: Stefan Teofanovic (stefan.teofanovic@heig-vd.ch)
"""
__all__ = ["SpotifyDataProvider"]

from collections.abc import Callable
from functools import cached_property
from typing import Any, ClassVar
import base64
import requests
from urllib.parse import urlencode
from data_providers.data_categories import DataCategory

from ddsurveys.data_providers.bases import FormField, OAuthDataProvider
from ddsurveys.data_providers.variables import BuiltInVariable, CVAttribute
from ddsurveys.get_logger import get_logger
from ddsurveys.variable_types import TVariableFunction, VariableDataType

# Import the required libraries to make this work

logger = get_logger(__name__)


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


# This is an example of a data category.
# In practice, each endpoint can be turned into a data category.
# 'self' in extractor functions will be an instance of the data provider class.
class PlaylistDataCategory(DataCategory["SpotifyDataProvider"]):

    data_origin = [
        {
            "method": "get_playlist",
            "endpoint": "https://api.spotify.com/v1/me/playlists",
            "documentation": "https://developer.spotify.com/documentation/web-api/reference/get-playlist",
        }
    ]

    custom_variables_enabled = False

    api = None

    def fetch_data(self) -> list[dict[str, Any]]:
        return self.data_provider.playlist

    cv_attributes = [
        CVAttribute(
            name="playlist",
            label="Users Playlist",
            description="The name of the playlist.",
            attribute="playlist",
            data_type=VariableDataType.TEXT,
            test_value_placeholder="Playlist",
            info="A playlist of the user.",
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
    app_creation_url: str = "https://developer.spotify.com/dashboard/create"  # e.g., "https://dataprovider.com/settings/apps/new"
    instructions_helper_url: str = "https://developer.spotify.com/documentation/web-api/concepts/apps"  # e.g., "https://docs.dataprovider.com/en/apps/creating-dataprovider-apps/"

    # Unique class attributes go here
    _scopes = []

    # See other classes for examples of how to fill these attributes. You may not need to fill them
    _categories_scopes = {}

    # Form fields that will be displayed in the frontend. Only update them if the data provider uses different
    # terminology for this information.
    form_fields = [
        FormField(name="client_id", type="text", required=True, data={}),
        FormField(name="client_secret", type="text", required=True, data={}),
    ]

    # List all the data categories that this data provider supports.
    # Just enter the names of the classes.
    data_categories: ClassVar[tuple[type[DataCategory['SpotifyDataProvider']], ...]] = (
        PlaylistDataCategory,
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
        self.api_client: SpotifyAPIClient
        self.oauth_client: SpotifyOAuthClient
        self.redirect_uri = self.get_redirect_uri()
        self.playlist = None

        self.init_oauth_client()

        if self.access_token is not None and self.refresh_token is not None:
            self.init_api_client(self.access_token, self.refresh_token)

    # OAuthBase methods
    def init_api_client(
        self, access_token: str | None = None, refresh_token: str | None = None, code: str | None = None
    ) -> None:

        self.api_client = SpotifyAPIClient(access_token=access_token)

    def init_oauth_client(self, *args, **kwargs) -> None:
        self.oauth_client = SpotifyOAuthClient(client_id=self.client_id, client_secret=self.client_secret, redirect_uri=self.redirect_uri)


    def get_authorize_url(
        self, builtin_variables: list[dict], custom_variables: list[dict] | None = None
    ) -> str: 
        return self.oauth_client.get_authorization_url()

    def get_client_id(self) -> str: ...

    def request_token(self, data: dict[str, Any]) -> dict[str, Any]: 
        return self.oauth_client.exchange_code_for_token(data)

    def revoke_token(self, token: str) -> bool: 
        ...
    
    def get_playlist(self):
        self.playlist = self.api_client.get_user_playlists()

    # DataProvider methods
    def test_connection_before_extraction(self) -> bool: ...

    def test_connection(self) -> bool: ...

    def repositories_by_stars(self, idx: int) -> str: ...

    @cached_property
    def account_creation_date(self) -> str: ...


####### Added 
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