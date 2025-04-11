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
from collections import Counter
import base64
import requests
from urllib.parse import urlencode
from typing import TYPE_CHECKING, Any, ClassVar, Literal, final, override
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from ddsurveys.data_providers.spotify.account import Account
from ddsurveys.data_providers.spotify.devices import Devices
from ddsurveys.data_providers.spotify.playlist import Playlist
from ddsurveys.data_providers.spotify.artist import Artist
from ddsurveys.data_providers.spotify.shows import Shows
from ddsurveys.data_providers.spotify.genres import Genres
from ddsurveys.data_providers.spotify.episode import Episode
from ddsurveys.data_providers.data_categories import DataCategory

from ddsurveys.data_providers.bases import FormField, OAuthDataProvider
from ddsurveys.data_providers.variables import BuiltInVariable, CVAttribute
from ddsurveys.get_logger import get_logger
from ddsurveys.variable_types import TVariableFunction, VariableDataType

# Import the required libraries to make this work

logger = get_logger(__name__)

# In practice, each endpoint can be turned into a data category.
# 'self' in extractor functions will be an instance of the data provider class.


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
    'playlist-read-private ',         # 0 Read private playlists (necessary for playlists hence artists/genres)
    'playlist-read-collaborative ',   # 1 Read collaborative playlists (necessary for playlists hence artists/genres)
    'user-read-playback-state ',      # 2 Read playback state (necessary for devices)
    'user-library-read ',             # 3 Read user's saved tracks and albums (necessary for tracks and episodes and shows)
    'user-read-recently-played ',     # 4 Access user's recently played tracks (necessary for tracks)
    'user-top-read ',                 # 5 Read user's top artists and tracks
    'user-read-private '             #  6 Read user's profile info
    )

    #'playlist-modify-public '        # Create and edit public playlists
    #'playlist-modify-private '       # Create and edit private playlists
    #'user-library-modify '           # Add/remove tracks to user's library

    # See other classes for examples of how to fill these attributes. You may not need to fill them (You definitely need to fill them)
    _categories_scopes = {'Playlist': _scopes[0] + _scopes[1], 
                          'Account': _scopes[2] + _scopes[6],
                          'Devices': _scopes[2],
                          'Episode': _scopes[3],
                          'Artist': _scopes[0] + _scopes[1],
                          'Shows': _scopes[3],
                          'Genres': _scopes[0] + _scopes[1],} 

    # Form fields that will be displayed in the frontend. Only update them if the data provider uses different
    # terminology for this information.
    form_fields = [
        FormField(name="client_id", type="text", required=True, data={}),
        FormField(name="client_secret", type="text", required=True, data={}),
    ]

    # List all the data categories that this data provider supports.
    # Just enter the names of the classes.
    data_categories: ClassVar[tuple[type[DataCategory["SpotifyDataProvider"]], ...]] = (
        Playlist,
        Account,
        Devices,
        Episode,
        Artist,
        Shows,
        Genres,
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

        self.api_client = spotipy.Spotify(auth=self.access_token, oauth_manager=self.oauth_client) # to get the playlists and so on, we only need to use an access_token
        if refresh_token:
            self.oauth_client.refresh_access_token(refresh_token)

    def init_oauth_client(self, *args, **kwargs) -> None:
        required_scopes: list[str] = self.get_required_scopes(self.builtin_variables, self.custom_variables)
        logger.debug("Required scopes for spotify: ", required_scopes)

        if len(required_scopes) == 0:
            required_scopes = list(self.__class__._scopes)

        # Profile is always required for the verifications done in other methods.
        if "user-read-private" not in required_scopes:
            required_scopes.append("user-read-private")
        self.oauth_client = SpotifyOAuth(client_id=self.client_id, client_secret=self.client_secret, redirect_uri=self.redirect_uri, scope=required_scopes, cache_handler=None, cache_path=None)

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
            token_info = self.oauth_client.get_access_token(code, as_dict=True, check_cache=False)
            access_token = token_info['access_token']
            self.api_client = spotipy.Spotify(auth=access_token, oauth_manager=self.oauth_client)
            user = self.api_client.current_user()

            if not user:
                logger.exception("Error in Spotify API call. User was null.")
                return {
                    "success": False,
                    "message_id": "api.data_provider.exchange_code_error.general_error",
                }
            
            refresh_token = token_info['refresh_token']
            self.oauth_client.refresh_access_token(refresh_token)
            user_info = {
                'username': user['display_name'],
                'user_id': user['id']
            }

            if not user_info['user_id']:
                logger.exception("Error in Spotify API call. UserId was null.")
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

    # Account related variables 
    @cached_property
    def subscription_level(self):
        user = self.api_client.current_user()
        logger.debug(f"User in subscription level: {user}")
        return user['product']

    @cached_property
    def total_follower_count(self):
        user = self.api_client.current_user()
        return user['followers']['total']
    
    @cached_property
    def user_profile(self):
        return self.api_client.current_user()
    
    # Device related variables. ONLY currently connected devices are visible
    def devices(self, idx: int) -> str | None:
        devices = self.api_client.devices()['devices']
        if len(devices) > idx - 1:
            return f"{devices[idx-1]["type"]} ({devices[idx-1]["name"]})"
        return None
    
    @cached_property
    def playlist_count(self):
        self.playlists = self.api_client.current_user_playlists()
        return len(self.playlists['items'])
    
    @cached_property
    def top_artist(self):
        playlists = self.api_client.current_user_playlists()
        playlist_items = []
        artist_names = []
        # iterate over every playlist p
        for p in playlists['items']:
            playlist_items.append(self.api_client.playlist_items(p['id'], additional_types=('track')))
            tracks_in_playlist = playlist_items[-1]['items']
            for track in tracks_in_playlist:
                artists = track['track']['album']['artists']
                for artist in artists:
                    #artist_ids.append(artist['id'])
                    artist_names.append(artist['name'])

        counter = Counter(artist_names)
        # Find most common artist
        most_common_element = counter.most_common(1)[0][0]        
        return most_common_element
    
    def genres(self, idx: int): # idx is one or two
        def get_spotify_artist(artist_id, access_token):
            url = f"https://api.spotify.com/v1/artists/{artist_id}"
            headers = {
                "Authorization": f"Bearer {access_token}"
            }
            
            response = requests.get(url, headers=headers)
            # list  of genres
            return response.json()['genres']
    
        playlists = self.api_client.current_user_playlists()
        genres_ = []
        # iterate over every playlist p
        for p in playlists['items']:
            tracks_in_playlist = self.api_client.playlist_items(p['id'], additional_types=('track'))['items']
            for track in tracks_in_playlist:
                artists = track['track']['album']['artists']
                for artist in artists:
                    genres_ += get_spotify_artist(artist['id'], self.access_token)
        counter = Counter(genres_)

        # Find most common artist
        most_common_genre = counter.most_common(2)[idx-1][0]
        return most_common_genre
    
    @cached_property
    def episode_cnt(self):
        episodes = self.api_client.current_user_saved_episodes()
        return len(episodes['items'])
    
    @cached_property
    def shows_cnt(self):
        episodes = self.api_client.current_user_saved_episodes()
        return len(episodes['items'])