#!/usr/bin/env python3
"""Created on 2023-08-31 16:59.

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
@author: Stefan Teofanovic (stefan.teofanovic@heig-vd.ch)
"""
from __future__ import annotations

import base64
import re
import urllib.parse
from datetime import date, datetime, timedelta
from functools import cache, cached_property
from typing import TYPE_CHECKING, Any, ClassVar

import requests
from dateutil.relativedelta import relativedelta
from fitbit.api import Fitbit, FitbitOauth2Client

from ddsurveys.data_providers.bases import FormField, OAuthDataProvider
from ddsurveys.data_providers.data_categories import DataCategory
from ddsurveys.data_providers.date_ranges import ensure_date, get_isoweek, range_date
from ddsurveys.data_providers.fitbit.activity_log import Activity, ActivityLog
from ddsurveys.data_providers.fitbit.daily_time_series import (
    AggregationFunctions,
    GroupingFunctions,
    group_time_series,
    merge_time_series,
)
from ddsurveys.data_providers.variables import BuiltInVariable, CVAttribute
from ddsurveys.get_logger import get_logger
from ddsurveys.variable_types import VariableDataType

if TYPE_CHECKING:
    from collections.abc import Callable, Generator

    from data_providers.fitbit.api_response_dicts import (
        ActiveZoneMinutesSeriesResponseDict,
        ActivitiesListResponseDict,
        ActivityTimeSeriesResponseDict,
        DeviceDict,
        FavoriteActivityDict,
        FrequentActivityDict,
        UserDict,
    )

    from ddsurveys.typings.variable_types import TVariableFunction

__all__ = ["FitbitDataProvider"]

logger = get_logger(__name__)


class Account(DataCategory):
    def fetch_data(self) -> list[dict[str, Any]]:
        pass

    builtin_variables: ClassVar = [
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
        ),
        BuiltInVariable.create_instances(
            name="account_created_at_least_1_year_ago",
            label="Account Created at Least 1 Year Ago",
            description="Account Created at Least 1 Year Ago.",
            data_type=VariableDataType.TEXT,
            test_value_placeholder="True",
            info="This will be 'True' if the account was created at least 1 year ago, otherwise 'False'.",
            extractor_func=lambda self: self.account_created_at_least_1_year_ago,
            data_origin=[
                {
                    "method": "user_profile",
                    "endpoint": "https://api.fitbit.com/1/user/[user-id]/profile.json",
                    "documentation": "https://dev.fitbit.com/build/reference/web-api/user/get-profile/",
                },
            ],
        )
    ]


class Activities(DataCategory):
    data_origin: ClassVar = [
        {
            "method": "activities_frequent",
            "endpoint": "https://api.fitbit.com/1/user/[user-id]/activities/frequent.json",
            "documentation": "https://dev.fitbit.com/build/reference/web-api/activity/get-frequent-activities/",
        }
    ]

    def fetch_data(self) -> list[dict[str, Any]]:
        self.data_provider: FitbitDataProvider
        data = self.data_provider.activity_logs
        if "activities" in data:
            return data["activities"]
        return []

    cv_attributes: ClassVar = [
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
            test_value_placeholder="2023-01-10T12:00:00.000+02:00",
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

    builtin_variables: ClassVar = [
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


class ActiveMinutes(DataCategory):
    def fetch_data(self) -> list[dict[str, Any]]:
        pass

    builtin_variables: ClassVar = [
        BuiltInVariable.create_instances(
            name="average_weekly_heart_zone_time_last_6_months",
            label="Average Weekly Heart Zone Minutes Last 6 Months",
            description="Average weekly heart zone minutes",
            data_type=VariableDataType.NUMBER,
            test_value_placeholder="120",
            unit="minutes",
            info="Average weekly heart zone minutes over the last 6 months.",
            extractor_func=lambda self: self.average_weekly_heart_zone_time_last_6_months,
            data_origin=[
                {
                    "method": "",
                    "endpoint": "https://api.fitbit.com/1/user/[user-id]/activities/active-zone-minutes/date/[start-date]/[end-date].json",
                    "documentation": "https://dev.fitbit.com/build/reference/web-api/active-zone-minutes-timeseries/get-azm-timeseries-by-interval/",
                }
            ],
        ),
        BuiltInVariable.create_instances(
            name="average_weekly_active_time_last_6_months",
            label="Average Weekly Active Minutes Last 6 Months",
            description="Average weekly active minutes",
            data_type=VariableDataType.NUMBER,
            test_value_placeholder="120",
            unit="minutes",
            info="Average weekly active minutes over the last 6 months.",
            extractor_func=lambda self: self.average_weekly_active_time_last_6_months,
            data_origin=[
                {
                    "method": "",
                    "endpoint": "https://api.fitbit.com/1/user/[user-id]/activities/[activityType]/date/[start-date]/[end-date].json",
                    "documentation": "https://dev.fitbit.com/build/reference/web-api/activity-timeseries/get-activity-timeseries-by-date-range/",
                }
            ],
        ),
        BuiltInVariable.create_instances(
            name="average_weekly_activity_time_last_6_months",
            label="Average Weekly Activity Time Last 6 Months",
            description="Average weekly minutes spend doing activities",
            data_type=VariableDataType.NUMBER,
            test_value_placeholder="120",
            unit="minutes",
            info="Average weekly minutes spend doing activities over the last 6 months.",
            extractor_func=lambda self: self.average_weekly_activity_time_last_6_months,
            data_origin=[
                {
                    "method": "",
                    "endpoint": "https://api.fitbit.com /1/user/[user-id]/activities/list.json ",
                    "documentation": "https://dev.fitbit.com/build/reference/web-api/activity/get-activity-log-list/",
                }
            ],
        ),
    ]


class Daily(DataCategory):
    def fetch_data(self) -> list[dict[str, Any]]:
        pass

    builtin_variables: ClassVar = [
        BuiltInVariable.create_instances(
            name="highest_steps_last_6_months_steps",
            label="Highest Daily Step Count in Last 6 Months",
            description="Highest step count achieved on a single day within the last 6 months. This includes wearable "
                        "activity tracker data only.",
            data_type=VariableDataType.NUMBER,
            test_value_placeholder="20000",
            unit="steps",
            info="Highest daily step count in last 6 months.",
            extractor_func=lambda self: self.highest_daily_steps_last_6_months_date_steps[1],
            data_origin=[
                {
                    "method": "",
                    "endpoint": "https://api.fitbit.com/1/user/[user-id]/activities/tracker/steps/date/[start-date]/[end-date].json",
                    "documentation": "https://dev.fitbit.com/build/reference/web-api/activity-timeseries/get-activity-timeseries-by-date-range/",
                }
            ],
        ),
        BuiltInVariable.create_instances(
            name="highest_steps_last_6_months_date",
            label="Date of Highest Daily Step Count in Last 6 Months",
            description="Date of step count achieved on a single day within the last 6 months. This includes wearable "
                        "activity tracker data only.",
            data_type=VariableDataType.DATE,
            test_value_placeholder="2020-01-01",
            unit="date",
            info="Date of highest daily step count in last 6 months.",
            extractor_func=lambda self: self.highest_daily_steps_last_6_months_date_steps[0].strftime("%Y-%m-%d"),
            data_origin=[
                {
                    "method": "",
                    "endpoint": "https://api.fitbit.com/1/user/[user-id]/activities/tracker/steps/date/[start-date]/[end-date].json",
                    "documentation": "https://dev.fitbit.com/build/reference/web-api/activity-timeseries/get-activity-timeseries-by-date-range/",
                }
            ],
        ),
    ]


class Steps(DataCategory):
    def fetch_data(self) -> list[dict[str, Any]]:
        return []

    builtin_variables: ClassVar = [
        BuiltInVariable.create_instances(
            name="average",
            label="Average Lifetime Steps",
            description="Average lifetime steps. If steps on only active days is not available, this will calculate "
                        "the average step count using the account creation date and total lifetime steps.",
            data_type=VariableDataType.NUMBER,
            test_value_placeholder="10000",
            unit="steps",
            info="Average lifetime steps. ",
            extractor_func=lambda self: self.average_lifetime_steps,
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
            extractor_func=lambda self: self.highest_lifetime_steps,
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
    data_origin: ClassVar = [
        {
            "method": "user_badges",
            "endpoint": "https://api.fitbit.com/1/user/[user-id]/badges.json",
            "documentation": "https://dev.fitbit.com/build/reference/web-api/user/get-badges/",
        }
    ]

    cv_attributes: ClassVar = [
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

    builtin_variables: ClassVar = []

    def fetch_data(self) -> list[dict[str, Any]]:
        data = self.data_provider.user_badges
        return data or []


class FitbitDataProvider(OAuthDataProvider):
    """FitbitDataProvider integrates with the Fitbit API.

    FitbitDataProvider is a class that handles the integration with the Fitbit API using
    OAuth2 for authentication.
    It provides methods to initialize the API client, request tokens, revoke tokens, and
    fetch various user data such as activities, profile information, and lifetime
    statistics.
    """
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

    # Class attributes that need be re-declared or redefined in child classes
    # The following attributes need to be re-declared in child classes.
    # You can just copy and paste them into the child class body.
    all_initial_funcs: ClassVar[dict[str, Callable]] = {}
    factory_funcs: ClassVar[dict[str, Callable]] = {}
    variable_funcs: ClassVar[dict[str, TVariableFunction]] = {}
    fields: ClassVar[list[dict[str, Any]]] = {}

    # Unique class attributes go here
    _scopes = (
        "activity",
        "heartrate",
        "location",
        "nutrition",
        "profile",
        "settings",
        "sleep",
        "social",
        "weight",
    )

    # TODO: finish this dictionary
    # TODO: implement a cleaner version
    _categories_scopes: ClassVar[dict[str, str]] = {
        "Account": "profile",
        "Activities": "activity",
        "activities": "activity",
        "ActiveMinutes": "activity",
        "activeminutes": "activity",
        "badges": "profile",
        "Badges": "profile",
        "Daily": "activity",
        "Steps": "activity",
        "Body": "weight",
    }

    # Form fields declarations go here
    form_fields: ClassVar[list[FormField]] = [
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
    data_categories: ClassVar[list[DataCategory]] = [Activities, Account, ActiveMinutes, Daily, Steps, Badges]

    # Standard class methods go here
    def __init__(self, **kwargs):
        """Args:
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

        self.activity_log: ActivityLog = ActivityLog()

        if self.client_id is not None or self.client_secret is not None:
            self.init_oauth_client()
            if self.access_token is not None and self.refresh_token is not None:
                self.init_api_client()

    # Methods that child classes must implement
    def init_api_client(
        self, access_token: str | None = None, refresh_token: str | None = None
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
        self, builtin_variables: list[dict] | None = None, custom_variables: list[dict] | None = None
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

    def request_token(self, code: str) -> dict[str, Any]:
        """Exchange the authorization code for an access token and retrieve the user's Fitbit profile.

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
            if not set(self.required_scopes).issubset(set(accepted_scopes)):
                logger.error(
                    f"Incomplete Fitbit scopes: {accepted_scopes} required: {self.required_scopes}"
                )
                # if all scopes were not authorized, revoke the token
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
            logger.exception(f"Error exchanging Fitbit code for token: {e}")
            return {
                "success": False,
                "message_id": "api.data_provider.exchange_code_error.general_error",
            }

    def revoke_token(self, token: str) -> bool:
        """Revoke a token using Fitbit's OAuth 2.0 revoke endpoint.
        The Fitbit SDK do not provide a method for revoking tokens.
        Thus, we need to make a request to the revoke endpoint ourselves.

        Args:
            token:

        Returns:

        """
        headers = {
            "Authorization": f"Basic {base64.b64encode(f'{self.client_id}:{self.client_secret}'.encode()).decode('utf-8')}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {"token": token}

        response = requests.post(self.revoke_url, headers=headers, data=data)

        if response.status_code == 200:
            logger.info("Fitbit access_token revoked.")
            return True
        else:
            logger.error("Error revoking Fitbit access_token.")
            return False

    def test_connection_before_extraction(self) -> bool:
        try:
            profile = self.api_client.user_profile_get()
            if not profile:
                return False
        except Exception as e:
            logger.exception(f"Error connecting to Fitbit: {e}")
            return False
        return True

    def test_connection(self) -> bool:
        # using client credentials flow to check if the client id and secret are valid

        authorization_header = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode()
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
    def activities_by_frequency(self, idx) -> str | None:
        if len(self.activities_frequent) > idx - 1:
            return self.activities_frequent[idx - 1]["name"]
        return None

    @cached_property
    def average_lifetime_steps(self) -> int:
        average_steps = self.user_profile.get("averageDailySteps")
        if average_steps is None or average_steps == 0:
            total_steps = self.lifetime_stats["lifetime"]["tracker"]["steps"]
            account_creation_date = datetime.strptime(
                self.user_profile["memberSince"], "%Y-%m-%d"
            )
            now = datetime.now()
            delta = (now - account_creation_date).days
            average_steps = int(total_steps / delta)
        return average_steps

    @cached_property
    def highest_lifetime_steps(self) -> int | None:
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
    def user_profile(self) -> UserDict:
        url = "https://api.fitbit.com/1/user/-/profile.json"
        return self.api_client.make_request(url)["user"]

    @cached_property
    def activities_favorite(self) -> list[FavoriteActivityDict]:
        return self.api_client.make_request("https://api.fitbit.com/1/user/-/activities/favorite.json")

    @cached_property
    def activities_frequent(self) -> list[FrequentActivityDict]:
        return self.api_client.make_request("https://api.fitbit.com/1/user/-/activities/frequent.json")

    @cached_property
    def activities_recent(self):
        return self.api_client.activity_stats(qualifier="recent")

    @cached_property
    def user_badges(self):
        return []

    @cached_property
    def activity_logs(self) -> ActivitiesListResponseDict:
        # Assuming you want to fetch activities before the current date in descending order
        before_date = datetime.now().strftime("%Y-%m-%d")
        sort_order = "desc"  # Use 'asc' if using afterDate
        limit = 100  # Maximum or any other preferred value
        offset = 0  # Starting point

        # Construct the URL with all required query parameters
        params = {"beforeDate": before_date, "sort": sort_order, "limit": limit, "offset": offset}
        url = f"https://api.fitbit.com/1/user/-/activities/list.json?{urllib.parse.urlencode(params)}"
        return self.api_client.make_request(url)

    @cache
    def get_activity_logs(
        self,
        before_date: datetime | None = None,
        after_date: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
        sort: str = "desc"
    ) -> ActivitiesListResponseDict:
        if before_date is None and after_date is None:
            msg = "Either before_date or after_date must be provided."
            raise ValueError(msg)

        if before_date is not None and after_date is not None:
            msg = "Only one of before_date or after_date can be provided."
            raise ValueError(msg)

        params: dict[str, int | str] = {"limit": limit, "offset": offset, "sort": sort}
        if before_date is not None:
            params["beforeDate"] = before_date.strftime("%Y-%m-%d")
        elif after_date is not None:
            params["afterDate"] = after_date.strftime("%Y-%m-%d")

        url = f"https://api.fitbit.com/1/user/-/activities/list.json?{urllib.parse.urlencode(params)}"
        return self.api_client.make_request(url)

    @cached_property
    def all_activity_logs(self):
        before_date = datetime.now()
        activities_logs = []
        for activity in self.get_activity_log_generator(before_date=before_date):
            activities_logs.append(activity)
        return activities_logs

    def get_activity_log_generator(
        self,
        before_date: datetime | None = None,
        after_date: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
        sort: str = "desc"
    ) -> Generator[Activity, None, None]:
        has_more = True
        while has_more:
            data = self.get_activity_logs(before_date=before_date, after_date=after_date, limit=limit, offset=offset,
                                          sort=sort)
            self.activity_log.integrate_activities_list(data["activities"], continuous=True)

            for activity in data["activities"]:
                # yield activity
                yield self.activity_log.id_activities[activity["logId"]]

            if data["pagination"].get("next", "") != "":
                offset = int(re.search(r"offset=(\d+)", data["pagination"]["next"]).group(1))
                has_more = True
            else:
                has_more = False

    def get_activities_date_range(self, start_date: datetime, end_date: datetime) -> list[Activity]:
        start_date = ensure_date(start_date)
        end_date = ensure_date(end_date)

        activities_logs: list[Activity] = []

        # If the dates are already in the activity log, return all activities within the range
        if self.activity_log.date_ranges.range_in_ranges(start_date, end_date):
            for date_ in range_date(start_date, end_date + timedelta(days=1)):
                activities_logs.extend(self.activity_log.date_ranges.activities_in_range(date_))
            return activities_logs

        # If activities are not in the activity log, fetch activities from Fitbit API
        for activity in self.get_activity_log_generator(before_date=end_date):
            # activity_date = datetime.fromisoformat(activity.start_date)
            if activity.start_date < start_date:
                break
            activities_logs.append(activity)

        activities_logs.sort()

        return activities_logs

    @cached_property
    def lifetime_stats(self):
        """Returns:

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
        url = "{}/{}/user/{}/activities.json".format(
            *self.api_client._get_common_args()
        )
        return self.api_client.make_request(url)

    @cache
    def daily_stats(
        self, activity: str, start_date: datetime, end_date: datetime
    ) -> ActivityTimeSeriesResponseDict | ActiveZoneMinutesSeriesResponseDict:
        """Args:
            activity: The type of activity to retrieve.
                Allowed values are: 'activityCalories', 'calories', 'caloriesBMR', 'distance', 'elevation', 'floors',
                'minutesSedentary', 'minutesLightlyActive', 'minutesFairlyActive', 'minutesVeryActive', and 'steps'.
                You can add 'tracker/' before the activity name to only get data collected with a tracker.
            start_date: Start date of the range for which to retrieve data.
                'activityCalories' has a maximum range of 30 days.
                All other activities have a maximum range of 1095 days.
            end_date: End date of the range for which to retrieve data.

        Returns:
            dict with the following structure:
                {
                    "activities-[`activity`]": [
                        {
                            "dateTime": "2018-12-26",
                            "value": "[value]"
                        }
                    ]
                }
            If activity is 'steps', the response will be:
                {
                  "activities-steps": [
                    {
                      "dateTime": "2018-12-26",
                      "value": "2504"
                    },
                    {
                      "dateTime": "2018-12-27",
                      "value": "3723"
                    },
                    {
                      "dateTime": "2018-12-28",
                      "value": "8304"
                    }
                  ]
                }

        Examples:


        """
        #  /1/user/[user-id]/activities/[resource-path]/date/[start-date]/[end-date].json
        #  GET https://api.fitbit.com/1/user/-/activities/steps/date/2019-01-01/2019-01-07.json
        if activity == "activityCalories" or activity == "tracker/activityCalories" and (
            end_date - start_date).days > 30:
            msg = f"Maximum range for {activity} is 30 days. Received {(end_date - start_date).days} days."
            raise ValueError(msg)
        if (end_date - start_date).days > 1095:
            msg = f"Maximum range for {activity} is 1095 days. Received {(end_date - start_date).days} days."
            raise ValueError(msg)

        url = (
            f"https://api.fitbit.com/1/user/-/activities/{activity}/date/{start_date.strftime('%Y-%m-%d')}/"
            f"{end_date.strftime('%Y-%m-%d')}.json"
        )
        return self.api_client.make_request(url)

    # Variable calculation functions/properties
    @cached_property
    def daily_step_counts_last_6_months(self) -> dict[str, list[dict[str, str]]]:
        end_date = date.today()
        start_date = end_date - relativedelta(months=6)
        # return self.daily_step_counts("tracker/steps", start_date, end_date)
        return self.daily_stats("steps", start_date, end_date)

    @cached_property
    def highest_daily_steps_last_6_months_date_steps(self) -> tuple[datetime, int] | tuple[None, None]:
        steps: list[dict[str, str]]
        if "activities-tracker-steps" in self.daily_step_counts_last_6_months:
            steps = self.daily_step_counts_last_6_months["activities-tracker-steps"]
        else:
            steps = self.daily_step_counts_last_6_months["activities-steps"]
        day_steps = max(steps, key=lambda x: int(x["value"]))
        day = datetime.strptime(day_steps["dateTime"], "%Y-%m-%d").date()
        steps = int(day_steps["value"])
        if steps > 0:
            return day, steps
        else:
            return None, None

    @cached_property
    def average_weekly_heart_zone_time_last_6_months(self) -> float | None:
        end_date: datetime = date.today()
        start_date: datetime = end_date - relativedelta(months=6)

        data = {
            key: [value["activeZoneMinutes"] for value in values]
            for key, values in group_time_series(
                self.daily_stats("active-zone-minutes", start_date, end_date),
                GroupingFunctions.by_calendar_week
            ).items()
        }

        average = sum(AggregationFunctions.sum(data, convert=False).values()) / 26
        if average > 0:
            return round(average, 1)
        return None

    @cached_property
    def average_weekly_active_time_last_6_months(self) -> float | None:
        end_date: datetime = date.today()
        start_date: datetime = end_date - relativedelta(months=6)
        activity_types = [
            # "minutesLightlyActive",
            # "minutesFairlyActive",
            # "minutesVeryActive",
            "tracker/minutesLightlyActive",
            "tracker/minutesFairlyActive",
            "tracker/minutesVeryActive",
        ]
        data = merge_time_series([
            group_time_series(
                self.daily_stats(activity_type, start_date, end_date),
                GroupingFunctions.by_calendar_week
            )
            for activity_type in activity_types
        ])

        average = sum(AggregationFunctions.sum(data).values()) / 26
        if average > 0:
            return round(average, 1)
        else:
            return None

    @cached_property
    def average_weekly_activity_time_last_6_months(self) -> float | None:
        end_date: datetime = date.today()
        start_date: datetime = end_date - relativedelta(months=6)

        activities: list[Activity] = self.get_activities_date_range(start_date, end_date)

        weekly_stats: dict[tuple[int, int], list[int]] = {}
        for activity in activities:
            week = get_isoweek(activity.start_date)
            weekly_stats.setdefault(week, []).append(activity.activeDuration)
        average = (
            sum(sum(durations) for durations in weekly_stats.values())
            / 26
            / 60_000  # convert miliseconds to minutes
        )
        if average > 0:
            return round(average, 1)
        else:
            return None

    @cached_property
    def devices(self) -> list[DeviceDict]:
        url = "https://api.fitbit.com/1/user/-/devices.json"
        return self.api_client.make_request(url)

    @cached_property
    def account_created_at_least_1_year_ago(self) -> bool:
        user = self.user_profile
        creation_date = datetime.strptime(user["memberSince"], "%Y-%m-%d").date()
        return creation_date <= date.today() - relativedelta(years=1)
