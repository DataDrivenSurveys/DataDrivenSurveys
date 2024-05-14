#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2023-08-31 16:59

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
@author: Stefan Teofanovic (stefan.teofanovic@heig-vd.ch)
"""

__all__ = ["FitbitDataProvider"]

import base64
from datetime import datetime
from functools import cached_property
from typing import Any, Callable, Dict

import requests
from fitbit.api import Fitbit, FitbitOauth2Client

from ..get_logger import get_logger
from ..variable_types import TVariableFunction, VariableDataType
from .bases import FormField, OAuthDataProvider
from .data_categories import DataCategory
from .variables import BuiltInVariable, CVAttribute

logger = get_logger(__name__)


class Account(DataCategory):
    supports_custom_variables = False

    def fetch_data(self) -> list[dict[str, Any]]:
        return []

    cv_attributes = []

    builtin_variables = [
        BuiltInVariable.create_instances(
            name="creation_date",
            label="Account Creation Date",
            description="Date of account creation.",
            data_type=VariableDataType.DATE,
            test_value_placeholder="2020-01-01",
            info="This will be the date that the respondent's Fitbit account was created. It will be in YYYY-MM-DD "
            "format.",
            extractor_func=lambda self: self.user_profile["memberSince"],
            data_origin=[
                {
                    "method": "user_profile",
                    "endpoint": "https://api.fitbit.com/1/user/[user-id]/profile.json",
                    "documentation": "https://dev.fitbit.com/build/reference/web-api/user/get-profile/",
                }
            ],
        )
    ]


class Activities(DataCategory):

    data_origin = [
        {
            "method": "activities_frequent",
            "endpoint": "https://api.fitbit.com/1/user/[user-id]/activities/frequent.json",
            "documentation": "https://dev.fitbit.com/build/reference/web-api/activity/get-frequent-activities/",
        }
    ]

    def fetch_data(self) -> list[dict[str, Any]]:
        data = self.data_provider.activity_logs
        if "activities" in data:
            return data["activities"]
        return []

    cv_attributes = [
        CVAttribute(
            name="duration",
            label="Activity Duration",
            description="The duration of the activity in seconds.",
            attribute="duration",
            data_type=VariableDataType.NUMBER,
            test_value_placeholder="100",
            info="The duration of the activity in seconds",
            unit="seconds",
        ),
        CVAttribute(
            name="calories",
            label="Calories Burned",
            description="The number of calories burned during the activity in kcal.",
            attribute="calories",
            data_type=VariableDataType.NUMBER,
            test_value_placeholder="100",
            info="The number of calories burned during the activity",
            unit="kcal",
        ),
        CVAttribute(
            label="Date",
            description="The date of the activity.",
            attribute="originalStartTime",
            name="date",
            data_type=VariableDataType.DATE,
            test_value_placeholder="2023-01-10T12:00:00.000",
            info="The date of the activity",
        ),
        CVAttribute(
            label="Distance",
            name="distance",
            description="The distance traveled during the activity in meters.",
            attribute="distance",
            data_type=VariableDataType.NUMBER,
            test_value_placeholder="100",
            info="The distance traveled during the activity",
            unit="meters",
        ),
        CVAttribute(
            label="Activity Type",
            description="The type of the activity.",
            attribute="activityName",
            name="type",
            data_type=VariableDataType.TEXT,
            test_value_placeholder="Walk",
            info="The type of activity",
        ),
    ]

    builtin_variables = [
        BuiltInVariable.create_instances(
            name="by_frequency",
            label="Activities by Frequency",
            description="Activities sorted from most frequent to least frequent. Index 1 "
            "is  the most frequent activity, index 2 is the second most frequent activity, "
            "and so on.",
            test_value_placeholder="Walk",
            data_type=VariableDataType.TEXT,
            info="Activities sorted from most frequent to least frequent. Index 1 is  the most frequent activity, ",
            is_indexed_variable=True,
            index_start=1,
            index_end=5,
            extractor_func=lambda self, idx: self.activities_by_frequency(idx),
            data_origin=[
                {
                    "method": "activities_frequent",
                    "endpoint": "https://api.fitbit.com/1/user/[user-id]/activities/frequent.json",
                    "documentation": "https://dev.fitbit.com/build/reference/web-api/activity/get-frequent-activities/",
                }
            ],
        )
    ]


class Steps(DataCategory):

    def fetch_data(self) -> list[dict[str, Any]]:
        return []

    cv_attributes = []

    builtin_variables = [
        BuiltInVariable.create_instances(
            name="average",
            label="Average Lifetime Steps",
            description="Average lifetime steps. If steps on only active days is not available, this will calculate "
            "the average step count using the account creation date and total lifetime steps.",
            data_type=VariableDataType.NUMBER,
            test_value_placeholder="10000",
            unit="steps",
            info="Average lifetime steps. ",
            extractor_func=lambda self: self.average_lifetime_steps(),
            data_origin=[
                {
                    "method": "activities_frequent",
                    "endpoint": "https://api.fitbit.com/1/user/[user-id]/profile.json",
                    "documentation": "https://dev.fitbit.com/build/reference/web-api/user/get-profile/",
                },
                {
                    "method": "lifetime_stats",
                    "endpoint": "https://api.fitbit.com/1/user/[user-id]/activities.json",
                    "documentation": "https://dev.fitbit.com/build/reference/web-api/activity/create-activity-log/",
                },
            ],
        ),
        BuiltInVariable.create_instances(
            name="highest",
            label="Highest Lifetime Steps",
            description="Highest step count achieved on a single day. This includes wearable activity tracker data "
            "only.",
            data_type=VariableDataType.NUMBER,
            test_value_placeholder="20000",
            unit="steps",
            info="Highest step count achieved on a single day. ",
            extractor_func=lambda self: self.highest_lifetime_steps(),
            data_origin=[
                {
                    "method": "lifetime_stats",
                    "endpoint": "https://api.fitbit.com/1/user/[user-id]/activities.json",
                    "documentation": "https://dev.fitbit.com/build/reference/web-api/activity/create-activity-log/",
                }
            ],
        ),
    ]


class Badges(DataCategory):

    data_origin = [
        {
            "method": "user_badges",
            "endpoint": "https://api.fitbit.com/1/user/[user-id]/badges.json",
            "documentation": "https://dev.fitbit.com/build/reference/web-api/user/get-badges/",
        }
    ]

    cv_attributes = [
        CVAttribute(
            label="Date",
            description="The date the badge was earned.",
            attribute="dateTime",
            name="date",
            data_type=VariableDataType.DATE,
            test_value_placeholder="2023-01-10T12:00:00.000",
            info="The date the badge was earned",
        ),
        CVAttribute(
            label="Badge Name",
            description="The name of the badge.",
            attribute="badgeName",
            name="name",
            data_type=VariableDataType.TEXT,
            test_value_placeholder="Walk",
            info="The name of the badge",
        ),
    ]

    builtin_variables = []

    def fetch_data(self) -> list[dict[str, Any]]:
        data = self.data_provider.user_badges
        return data or []


class FitbitDataProvider(OAuthDataProvider):
    # These attributes need to be overridden
    token_url: str = "https://api.fitbit.com/oauth2/token"
    revoke_url: str = "https://api.fitbit.com/oauth2/revoke"

    instructions_helper_url: str = (
        "https://dev.fitbit.com/build/reference/web-api/developer-guide/getting-started/"
    )

    app_creation_url: str = (
        "https://dev.fitbit.com/apps/new?name={project_name}"
        "&description={application_description}"
        "&url={dds_about_url}"
        # "&organization={organization_name}"
        # "&organizationUrl={organization_url}"
        "&tosUrl={dds_tos_url}"
        "&privacyPolicy={dds_privacy_policy_url}"
        "&callback={callback_url}"
    )

    # Class attributes that need be redeclared or redefined in child classes
    # The following attributes need to be redeclared in child classes.
    # You can just copy and paste them into the child class body.
    all_initial_funcs: dict[str, Callable] = {}
    factory_funcs: dict[str, Callable] = {}
    variable_funcs: dict[str, TVariableFunction] = {}
    fields: list[dict[str, Any]] = {}

    # Unique class attributes go here
    _scopes = [
        "activity",
        "heartrate",
        "location",
        "nutrition",
        "PROFILE",
        "settings",
        "sleep",
        "social",
        "weight",
    ]

    # TODO: finish this dictionary
    # TODO: implement a cleaner version
    _categories_scopes = {
        "Account": "profile",
        "Activities": "activity",
        "activities": "activity",
        "badges": "profile",
        "Badges": "profile",
        "Steps": "activity",
        "Body": "weight",
    }

    # Form fields declarations go here
    form_fields = [
        FormField(
            name="client_id",
            type="text",
            required=True,
            data={
                # "helper_url": "https://dev.fitbit.com/build/reference/web-api/developer-guide/getting-started/"
            },
        ),
        FormField(
            name="client_secret",
            type="text",
            required=True,
            data={
                # "helper_url": "https://dev.fitbit.com/build/reference/web-api/developer-guide/getting-started/"
            },
        ),
    ]

    # DataCategory declarations go here
    data_categories = [Activities, Account, Steps, Badges]

    # Standard class methods go here
    def __init__(self, **kwargs):
        """

        Args:
            client_id:
            client_secret:
            access_token:
            refresh_token:
            **kwargs:
        """
        super().__init__(**kwargs)
        self.api_client: Fitbit
        self.oauth_client: FitbitOauth2Client
        self.redirect_uri = self.get_redirect_uri()

        if self.client_id is not None or self.client_secret is not None:
            self.init_oauth_client()
            if self.access_token is not None and self.refresh_token is not None:
                self.init_api_client()

    # Methods that child classes must implement
    def init_api_client(
        self, access_token: str = None, refresh_token: str = None
    ) -> None:
        if access_token is not None:
            self.access_token = access_token
        if refresh_token is not None:
            self.refresh_token = refresh_token
        self.api_client: Fitbit = Fitbit(
            self.client_id,
            self.client_secret,
            access_token=self.access_token,
            refresh_token=self.refresh_token,
        )

    def init_oauth_client(self) -> None:
        self.oauth_client: FitbitOauth2Client = FitbitOauth2Client(
            self.client_id, self.client_secret
        )

    def get_authorize_url(
        self, builtin_variables: list[dict] = None, custom_variables: list[dict] = None
    ) -> str:
        required_scopes = self.get_required_scopes(builtin_variables, custom_variables)
        logger.info(f"Fitbit redirect_uri: {self.redirect_uri}")
        if len(required_scopes) == 0:
            required_scopes = self.__class__._scopes
        return self.oauth_client.authorize_token_url(
            scope=required_scopes, redirect_uri=self.redirect_uri
        )

    def get_client_id(self) -> str:
        return self.client_id

    def request_token(self, code: str) -> Dict[str, Any]:
        """
        Exchange the authorization code for an access token and retrieve the user's Fitbit profile.

        Args:
            code (str): The authorization code provided by Fitbit upon user's consent.

        Returns:
            dict: A dictionary containing the result, which includes tokens, user information,
                or an error message in case of failure.
        """
        try:
            token = self.oauth_client.fetch_access_token(code, self.redirect_uri)

            # Use the access token to fetch the user's profile information
            access_token = token["access_token"]
            refresh_token = token["refresh_token"]
            accepted_scopes = token["scope"]
            user_id = token["user_id"]

            fitbit = Fitbit(
                client_id=self.client_id,
                client_secret=self.client_secret,
                access_token=access_token,
                refresh_token=refresh_token,
            )

            profile = fitbit.user_profile_get()

            # check if all scopes are authorized
            if set(self.required_scopes) != set(accepted_scopes):
                logger.error(
                    f"Incomplete Fitbit scopes: {accepted_scopes} required: {self.required_scopes}"
                )
                # if not all scopes are authorized, revoke the token
                self.revoke_token(access_token)
                return {
                    "success": False,
                    "message_id": "api.data_provider.exchange_code_error.incomplete_scopes",
                    "required_scopes": self.scopes,
                    "accepted_scopes": accepted_scopes,
                }

            return {
                "success": True,
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user_id": user_id,
                "user_name": profile["user"]["displayName"],
            }
        except Exception as e:
            logger.error(f"Error exchanging Fitbit code for token: {e}")
            return {
                "success": False,
                "message_id": "api.data_provider.exchange_code_error.general_error",
            }

    def revoke_token(self, token: str) -> bool:
        """
        Revoke a token using Fitbit's OAuth 2.0 revoke endpoint.
        The Fitbit SDK do not provide a method for revoking tokens.
        Thus, we need to make a request to the revoke endpoint ourselves.

        Args:
            token:

        Returns:

        """
        headers = {
            "Authorizatio"
            "n": f"Basic {base64.b64encode(f'{self.client_id}:{self.client_secret}'.encode('utf-8')).decode('utf-8')}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {"token": token}

        response = requests.post(self.revoke_url, headers=headers, data=data)

        if response.status_code == 200:
            logger.info(f"Fitbit access_token revoked.")
            return True
        else:
            logger.error(f"Error revoking Fitbit access_token.")
            return False

    def test_connection_before_extraction(self) -> bool:
        try:
            profile = self.api_client.user_profile_get()
            if not profile:
                return False
        except Exception as e:
            logger.error(f"Error connecting to Fitbit: {e}")
            return False
        return True

    def test_connection(self) -> bool:
        # using client credentials flow to check if the client id and secret are valid

        authorization_header = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode("utf-8")
        ).decode("utf-8")

        headers = {
            "Authorization": f"Basic {authorization_header}",
            "accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

        response = requests.post(self.token_url, headers=headers, data=data)
        return response.status_code == 200

    # Properties to access class attributes
    @property
    def scopes(self) -> list[str]:
        return self.__class__._scopes

    # Class methods

    # Instance properties

    # Instance methods

    # Extractor functions
    def activities_by_frequency(self, idx):
        if len(self.activities_frequent) > idx - 1:
            return self.activities_frequent[idx - 1]["name"]
        return None

    def average_lifetime_steps(self):
        average_steps = self.user_profile["averageDailySteps"]
        if average_steps == 0:
            total_steps = self.lifetime_stats["lifetime"]["tracker"]["steps"]
            account_creation_date = datetime.strptime(
                self.user_profile["memberSince"], "%Y-%m-%d"
            )
            now = datetime.now()
            delta = (now - account_creation_date).days
            average_steps = int(total_steps / delta)
        return average_steps

    def highest_lifetime_steps(self):
        try:
            return (
                self.lifetime_stats.get("best", {})
                .get("tracker", {})
                .get("steps", {})
                .get("value", None)
            )
        except AttributeError:
            return None

    # Cached API responses
    @cached_property
    def user_profile(self):
        return self.api_client.user_profile_get()["user"]

    @cached_property
    def activities_favorite(self):
        return self.api_client.activity_stats(qualifier="favorite")

    @cached_property
    def activities_frequent(self):
        return self.api_client.activity_stats(qualifier="frequent")

    @cached_property
    def activities_recent(self):
        return self.api_client.activity_stats(qualifier="recent")

    @cached_property
    def user_badges(self):
        return []

    @property
    def activity_logs(self):
        # Assuming you want to fetch activities before the current date in descending order
        before_date = datetime.now().strftime("%Y-%m-%d")
        sort_order = "desc"  # Use 'asc' if using afterDate
        limit = 100  # Maximum or any other preferred value
        offset = 0  # Starting point

        # Construct the URL with all required query parameters
        url = "{0}/{1}/user/{2}/activities/list.json?beforeDate={3}&sort={4}&limit={5}&offset={6}".format(
            *self.api_client._get_common_args(), before_date, sort_order, limit, offset
        )
        return self.api_client.make_request(url)

    @cached_property
    def lifetime_stats(self):
        """

        Returns:

        Examples:
            {
              "best": {
                "total": {
                  "distance": {
                    "date": "2021-01-01",
                    "value": 15.33423820935418
                  },
                  "floors": {
                    "date": "2016-01-01",
                    "value": 140.00000029608
                  },
                  "steps": {
                    "date": "2021-01-01",
                    "value": 30123
                  }
                },
                "tracker": {
                  "distance": {
                    "date": "2021-01-01",
                    "value": 15.33423820935418
                  },
                  "floors": {
                    "date": "2016-01-01",
                    "value": 140.00000029608
                  },
                  "steps": {
                    "date": "2021-01-01",
                    "value": 30123
                  }
                }
              },
              "lifetime": {
                "total": {
                  "activeScore": -1,
                  "caloriesOut": -1,
                  "distance": 1234,
                  "floors": 9876,
                  "steps": 7654321
                },
                "tracker": {
                  "activeScore": -1,
                  "caloriesOut": -1,
                  "distance": 1234,
                  "floors": 9876,
                  "steps": 1234567
                }
              }
            }
        """
        url = "{0}/{1}/user/{2}/activities.json".format(
            *self.api_client._get_common_args()
        )
        return self.api_client.make_request(url)

    # Extractor functions

    # Extractor functions for factories
