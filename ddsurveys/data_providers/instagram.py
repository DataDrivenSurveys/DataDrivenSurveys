"""This module provides the InstagramDataProvider class.

Created on 2023-08-31 16:59.

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
@author: Stefan Teofanovic (stefan.teofanovic@heig-vd.ch)
"""

from __future__ import annotations

from functools import cached_property
from http import HTTPStatus
from typing import TYPE_CHECKING, Any, ClassVar, final, override

import requests

from ddsurveys.data_providers.bases import FormField, OAuthDataProvider
from ddsurveys.data_providers.data_categories import DataCategory
from ddsurveys.data_providers.variables import BuiltInVariable
from ddsurveys.get_logger import get_logger
from ddsurveys.variable_types import VariableDataType

if TYPE_CHECKING:
    from collections.abc import Callable

    from ddsurveys.data_providers.variables import CVAttribute
    from ddsurveys.typings.shared_bases import FormFieldDict
    from ddsurveys.variable_types import TVariableFunction

__all__ = ["InstagramDataProvider"]

logger = get_logger(__name__)


class Media(DataCategory["InstagramDataProvider"]):
    def fetch_data(self) -> list[dict[str, Any]]:
        return []

    cv_attributes: ClassVar[list[CVAttribute]] = []
    builtin_variables: ClassVar[list[list[BuiltInVariable["InstagramDataProvider"]]]] = [
        BuiltInVariable["InstagramDataProvider"].create_instances(
            name="media_count",
            label="Media Count",
            description="Number of media posts.",
            data_type=VariableDataType.NUMBER,
            test_value_placeholder="2020-01-01",
            info="This will be the date that the respondent's Instagram account was created. It will be in YYYY-MM-DD format.",
            extractor_func=lambda self: self.media_count,
            data_origin=[
                {
                    "method": "media_count",
                    "endpoint": "https://graph.instagram.com/v11/me?fields=media_count&access_token=[access_token]",
                    "documentation": "https://developers.facebook.com/docs/instagram-basic-display-api/reference/user#fields",
                }
            ],
        )
    ]


@final
class InstagramDataProvider(OAuthDataProvider):
    # General class attributes

    # These attributes need to be overridden
    app_creation_url: str = "https://developers.facebook.com/apps/creation/"
    dds_app_creation_instructions: str = ""

    token_url = "https://api.instagram.com/oauth/access_token"  # noqa: S105
    base_authorize_url = "https://api.instagram.com/oauth/authorize"

    # Unique class attributes go here

    # Form fields declarations go here
    form_fields: ClassVar = [
        FormField(
            name="client_id",
            type="text",
            required=True,
            data={
                # "helper_url": "https://developers.facebook.com/docs/instagram-basic-display-api/getting-started"
            },
        ),
        FormField(
            name="client_secret",
            type="text",
            required=True,
            data={
                # "helper_url": "https://developers.facebook.com/docs/instagram-basic-display-api/getting-started"
            },
        ),
    ]

    data_categories: ClassVar[tuple[type[DataCategory["InstagramDataProvider"]], ...]] = (Media,)

    # Assuming the use of the latest API version (as of September 2021)
    api_version = "v11.0"
    user_id = "me"  # You can adjust this if needed

    @cached_property
    def media_count(self):
        try:
            media_count_url = f"https://graph.instagram.com/{self.api_version}/{self.user_id}?fields=media_count&access_token={self.access_token}"

            response = requests.get(media_count_url)
            response.raise_for_status()

            data = response.json()
            return data.get("media_count")
        except Exception:
            logger.exception("Error fetching media count from Instagram.\n")
            return None

    # Standard/builtin class methods go here
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    # Methods that child classes must implement
    def init_api_client(self, *args, **kwargs) -> None:
        pass

    def init_oauth_client(self, *args, **kwargs) -> None:
        pass

    def get_authorize_url(
        self,
        builtin_variables: list[dict] | None = None,
        custom_variables: list[dict] | None = None,
    ) -> str:
        """Returns the authorize url.

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
        return requests.Request("GET", self.base_authorize_url, params=params).prepare().url

    def get_client_id(self) -> str:
        return self.client_id

    def request_token(self, data: dict[str, Any]) -> dict[str, Any]:
        """Exchange the authorization code for an Instagram User Access Token and retrieve the user's profile.

        Args:
            data: The authorization code provided by Instagram upon user's consent.

        Returns:
            dict: A dictionary containing the result, which includes tokens, user information,
                or an error message in case of failure.
        """
        url_params = data["url_params"]
        code: str | None = url_params.get("code", None)
        if code is None:
            return {
                "success": False,
                "message_id": "api.data_provider.exchange_code_error",
                "text": "Failed to get the access to the data provider.",
            }

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
                    "message_id": "api.data_provider.exchange_code_error.general_error",
                    "text": "Full scope not granted",
                }

            # At this point, for Instagram, we know the user has accepted the full scope.
            # Fetch user_name using Basic Display API
            profile_url = (
                f"https://graph.instagram.com/me?fields=username&access_token={access_token}"
            )
            profile_response = requests.get(profile_url)
            profile_response.raise_for_status()

            profile_data = profile_response.json()

            user_name = profile_data.get("username")

            if not user_name:
                return {
                    "success": False,
                    "message_id": "api.data_provider.exchange_code_error.general_error",
                }

            return {
                "success": True,
                "access_token": access_token,
                "refresh_token": None,  # Instagram doesn't provide refresh token in this flow
                "user_id": user_id,
                "user_name": user_name,
            }

        except requests.HTTPError:
            logger.exception(
                "HTTP error when exchanging Instagram code for token. Status code: %s",
                response.status_code,
            )
            return {
                "success": False,
                "message_id": "api.data_provider.exchange_code_error.general_error",
            }
        except Exception as e:
            logger.exception("Error exchanging Instagram code for token: %s", e)
            return {
                "success": False,
                "message_id": "api.data_provider.exchange_code_error.general_error",
            }

    @override
    def revoke_token(self, token: str | None = None) -> bool:
        return False

    @override
    def test_connection_before_extraction(self) -> bool:
        try:
            # Use the access token to fetch the user's profile information
            profile_url = (
                f"https://graph.instagram.com/me?fields=username&access_token={self.access_token}"
            )
            profile_response = requests.get(profile_url)
            profile_response.raise_for_status()

            profile_data = profile_response.json()
            user_name = profile_data.get("username")

            if not user_name:
                return False

        except Exception as e:
            logger.exception("Error connecting to Instagram: %s", e)
            return False
        return True

    @override
    def test_connection(self) -> bool:
        # Using client credentials flow to check if the app id and secret are valid
        headers: dict[str, str] = {
            "accept": "application/json",
        }
        data: dict[str, str] = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "authorization_code",
            "redirect_uri": self.get_redirect_uri(),
            "code": "<test-code>",  # replace with a test code
        }
        try:
            response: requests.Response = requests.post(
                self.token_url, headers=headers, data=data, timeout=5
            )
            success: bool = response.status_code == HTTPStatus.OK
            if response.status_code != HTTPStatus.OK:
                error = response.json().get("error_message")
                success = error not in ("Invalid platform app", "Invalid Client ID")
        except Exception:
            logger.exception("Error connecting to Instagram.")
            return False
        else:
            return success  # Returns the status code. In real use, you'd want to handle different response codes differently.

    # Properties to access class attributes

    # Class methods

    # Instance properties

    # Instance methods

    # Cached API responses
    # API calls should be wrapped in properties using @cached_property decorators

    # Extractor functions
    # These are functions that extract user data from the API
