"""Created on 2023-08-31 16:59.

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
@author: Stefan Teofanovic (stefan.teofanovic@heig-vd.ch)
"""

from __future__ import annotations

import base64
import re
import urllib.parse
from datetime import date, datetime
from enum import IntEnum
from functools import cache, cached_property
from http import HTTPStatus
from typing import TYPE_CHECKING, Any, ClassVar, Literal, final, override

import requests
from dateutil.relativedelta import relativedelta
from fitbit.api import Fitbit, FitbitOauth2Client
from fitbit.exceptions import HTTPForbidden
from oauthlib.oauth2.rfc6749.errors import InvalidGrantError

from ddsurveys.data_providers.bases import FormButton, FormField, OAuthDataProvider
from ddsurveys.data_providers.date_ranges import get_isoweek
from ddsurveys.data_providers.fitbit.account import Account
from ddsurveys.data_providers.fitbit.active_minutes import ActiveMinutes
from ddsurveys.data_providers.fitbit.activities import Activities
from ddsurveys.data_providers.fitbit.activity_log import Activity
from ddsurveys.data_providers.fitbit.api_response_dicts import (
    ActivitiesListResponseDict,
)
from ddsurveys.data_providers.fitbit.badges import Badges
from ddsurveys.data_providers.fitbit.daily import Daily
from ddsurveys.data_providers.fitbit.daily_time_series import (
    AggregationFunctions,
    GroupingFunctions,
    group_time_series,
    merge_time_series,
)
from ddsurveys.data_providers.fitbit.steps import Steps
from ddsurveys.get_logger import get_logger

if TYPE_CHECKING:
    from collections.abc import Generator, Sequence
    from logging import Logger

    from ddsurveys.data_providers.data_categories import DataCategory, DC_BuiltinVariables
    from ddsurveys.data_providers.fitbit.api_response_dicts import (
        ActiveZoneMinutesSeriesResponseDict,
        ActivitiesListResponseDict,
        ActivityTimeSeriesResponseDict,
        DeviceDict,
        FavoriteActivityDict,
        FrequentActivityDict,
        UserDict,
    )
    from ddsurveys.typings.data_providers.variables import (
        BuiltinVariableDict,
        CustomVariableDict,
        CustomVariableUploadDict,
        QualifiedBuiltInVariableDict,
    )

    type FB_DC_BuiltinVariables = DC_BuiltinVariables["FitbitDataProvider"]

__all__ = ["FitbitDataProvider"]

logger: Logger = get_logger(__name__)


class DailyStatsMaxDateRange(IntEnum):
    """Maximum range for daily stats requests in Fitbit API."""

    activityCalories = 30
    OTHER = 1095


@final
class FitbitDataProvider(OAuthDataProvider):
    """FitbitDataProvider integrates with the Fitbit API.

    FitbitDataProvider is a class that handles the integration with the Fitbit API using
    OAuth2 for authentication.
    It provides methods to initialize the API client, request tokens, revoke tokens, and
    fetch various user data such as activities, profile information, and lifetime
    statistics.
    """

    # These attributes need to be overridden
    token_url: str = "https://api.fitbit.com/oauth2/token"  # noqa: S105
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

    # Unique class attributes go here
    _scopes: ClassVar[tuple[str, ...]] = (
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
    form_fields: ClassVar[Sequence[FormField | FormButton]] = [
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
    data_categories: ClassVar[tuple[type[DataCategory[FitbitDataProvider]], ...]] = (
        Account,
        ActiveMinutes,
        Activities,
        Badges,
        Daily,
        Steps,
    )

    # Standard class methods go here
    @override
    def __init__(
        self,
        client_id: str | None = None,
        client_secret: str | None = None,
        access_token: str | None = None,
        refresh_token: str | None = None,
        builtin_variables: list[QualifiedBuiltInVariableDict] | None = None,
        custom_variables: list[CustomVariableUploadDict] | None = None,
        **kwargs: dict[str, Any],
    ) -> None:
        """Initialize the FitbitDataProvider.

        This constructor sets up the FitbitDataProvider with the necessary clients and
        tokens for API communication.
        It initializes the OAuth client if client credentials are provided, and the API
        client if access and refresh tokens are available.

        Args:
            client_id (str, optional): The client ID for the Fitbit API.
            client_secret (str, optional): The client secret for the Fitbit API.
            access_token (str, optional): The OAuth2 access token for authenticated
                requests.
            refresh_token (str, optional): The OAuth2 refresh token to obtain a new
                access token when it expires.
            builtin_variables:
            custom_variables:
            **kwargs: Additional keyword arguments passed to the parent class
                constructor.

        Returns:
            None
        """
        super().__init__(
            client_id=client_id,
            client_secret=client_secret,
            access_token=access_token,
            refresh_token=refresh_token,
            builtin_variables=builtin_variables,
            custom_variables=custom_variables,
            **kwargs,
        )
        self.api_client: Fitbit
        self.oauth_client: FitbitOauth2Client
        self.redirect_uri = self.get_redirect_uri()

        # self.activity_log: ActivityLog = ActivityLog()

        if self.client_id is not None or self.client_secret is not None:
            self.init_oauth_client()
            if self.access_token is not None and self.refresh_token is not None:
                self.init_api_client()

    # Methods that child classes must implement
    @override
    def init_api_client(
        self,
        access_token: str | None = None,
        refresh_token: str | None = None,
    ) -> None:
        if access_token is not None:
            self.access_token = access_token
        if refresh_token is not None:
            self.refresh_token = refresh_token
        self.api_client = Fitbit(
            client_id=self.client_id,
            client_secret=self.client_secret,
            access_token=self.access_token,
            refresh_token=self.refresh_token,
        )

    @override
    def init_oauth_client(self) -> None:
        self.oauth_client = FitbitOauth2Client(
            client_id=self.client_id,
            client_secret=self.client_secret,
        )

    @override
    def get_authorize_url(
        self,
        builtin_variables: list[BuiltinVariableDict] | None = None,
        custom_variables: list[CustomVariableDict] | None = None,
    ) -> str:
        required_scopes: list[str] = self.get_required_scopes(builtin_variables, custom_variables)
        logger.debug("Fitbit redirect_uri: %s", self.redirect_uri)

        if len(required_scopes) == 0:
            required_scopes = list(self.__class__._scopes)

        # Profile is always required for the verifications done in other methods.
        if "profile" not in required_scopes:
            required_scopes.append("profile")
        return self.oauth_client.authorize_token_url(
            scope=required_scopes,
            redirect_uri=self.redirect_uri,
        )[0]

    @override
    def get_client_id(self) -> str:
        return self.client_id

    @override
    def request_token(self, data: dict[str, Any]) -> dict[str, Any]:
        """Exchange the authorization code for an access token.

         After getting the access token the function retrieves the user's Fitbit
         profile to test if the Fitbit API can be accessed.

        Args:
            data: The authorization code provided by Fitbit upon user's consent.

        Returns:
            dict: A dictionary containing the result, which includes tokens, user information,
                or an error message in case of failure.
        """
        url_params = data["url_params"]
        code: str | None = url_params.get("code", None)

        if code is None:
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
            # When using react in dev mode this method will be re-run twice, even though the token
            # was revoked the first time.
            token = self.oauth_client.fetch_access_token(code=code, redirect_uri=self.redirect_uri)

            # Use the access token to fetch the user's profile information
            access_token = token["access_token"]
            refresh_token = token["refresh_token"]
            accepted_scopes = token["scope"]
            user_id = token["user_id"]

            # check if all scopes are authorized
            if not set(self.required_scopes).issubset(set(accepted_scopes)):
                logger.error(
                    "Incomplete Fitbit scopes: %s required: %s",
                    accepted_scopes,
                    self.required_scopes,
                )
                # if all scopes were not authorized, revoke the token
                self.revoke_token(access_token)
                return {
                    "success": False,
                    "message_id": "api.data_provider.exchange_code_error.incomplete_scopes",
                    "required_scopes": self.required_scopes,
                    "accepted_scopes": accepted_scopes,
                }

            fitbit = Fitbit(
                client_id=self.client_id,
                client_secret=self.client_secret,
                access_token=access_token,
                refresh_token=refresh_token,
            )

            try:
                profile = fitbit.user_profile_get()
            except HTTPForbidden:
                pass
            else:
                return {
                    "success": True,
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user_id": user_id,
                    "user_name": profile["user"]["displayName"],
                }
        except (InvalidGrantError, Exception):
            logger.exception("Error exchanging Fitbit code for token.")
            return {
                "success": False,
                "message_id": "api.data_provider.exchange_code_error.general_error",
            }

        logger.error("Error exchanging Fitbit code for token.")
        return {
            "success": False,
            "message_id": "api.data_provider.exchange_code_error.general_error",
        }

    @override
    def revoke_token(self, token: str | None = None) -> bool:
        """Revoke a token using Fitbit's OAuth 2.0 revoke endpoint.

        The Fitbit SDK do not provide a method for revoking tokens.
        Thus, we need to make a request to the revoke endpoint ourselves.

        Args:
            token: The access token to be revoked.

        Returns:
            True if the token was revoked successfully, False otherwise.
        """
        authorization_header = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode(),
        ).decode("utf-8")

        headers = {
            "Authorization": f"Basic {authorization_header}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {"token": token}

        response = requests.post(url=self.revoke_url, headers=headers, data=data, timeout=5)

        if response.status_code == HTTPStatus.OK:
            logger.info("Fitbit access_token revoked.")
            return True

        logger.error("Error revoking Fitbit access_token.")
        return False

    @override
    def test_connection_before_extraction(self) -> bool:
        try:
            profile = self.api_client.user_profile_get()
            if not profile:
                return False
        except Exception:
            logger.exception("Error connecting to Fitbit: %s")
            return False
        return True

    @override
    def test_connection(self) -> bool:
        # using client credentials flow to check if the client id and secret are valid

        authorization_header = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode(),
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

        response = requests.post(url=self.token_url, headers=headers, data=data, timeout=5)
        return response.status_code == HTTPStatus.OK

    # Properties to access class attributes
    @property
    @override
    def scopes(self) -> list[str]:
        return self.__class__._scopes

    # Class methods

    # Instance properties

    # Instance methods

    # Extractor functions
    def activities_by_frequency(self, idx: int) -> str | None:
        if len(self.activities_frequent) > idx - 1:
            return self.activities_frequent[idx - 1]["name"]
        return None

    @cached_property
    def average_lifetime_steps(self) -> int:
        average_steps = self.user_profile.get("averageDailySteps")
        if average_steps is None or average_steps == 0:
            total_steps = self.lifetime_stats["lifetime"]["tracker"]["steps"]
            account_creation_date = datetime.strptime(self.user_profile["memberSince"], "%Y-%m-%d")
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
        data = self.api_client.make_request("https://api.fitbit.com/1/user/-/profile.json")
        if isinstance(data, dict):
            return data.get("user", {})
        return {}

    @cached_property
    def activities_favorite(self) -> list[FavoriteActivityDict]:
        data = self.api_client.make_request(
            "https://api.fitbit.com/1/user/-/activities/favorite.json",
        )
        if isinstance(data, list):
            return data
        return []

    @cached_property
    def activities_frequent(self) -> list[FrequentActivityDict]:
        data = self.api_client.make_request(
            "https://api.fitbit.com/1/user/-/activities/frequent.json",
        )
        if isinstance(data, list):
            return data
        return []

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
        url = (
            f"https://api.fitbit.com/1/user/-/activities/list.json?{urllib.parse.urlencode(params)}"
        )
        return self.api_client.make_request(url)

    @cache
    def get_activity_logs(
        self,
        before_date: datetime | None = None,
        after_date: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
        sort: Literal["asc", "desc"] = "desc",
    ) -> ActivitiesListResponseDict:
        """Fetches acitivy logs from the Fitbit API.

        Args:
            before_date:
                The date before which activities should be returned.
                This date is exclusive.
            after_date:
                The date after which activities should be returned.
                This date is inclusive.
            limit:
                The number of activities to return. Maximum 100.
            offset:
                The offset for returning large numbers of activities.
            sort:
                How to sort activities based on time.

        Returns:
            A list of API responses.
        """
        limit = int(limit)
        if not 0 < limit <= 100:
            msg = f"The limit must be between 0 and 100. Received: {limit}"
            raise ValueError(msg)
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

        url = (
            f"https://api.fitbit.com/1/user/-/activities/list.json?{urllib.parse.urlencode(params)}"
        )
        return self.api_client.make_request(url)

    @cached_property
    def all_activity_logs(self):
        """Fetch all activity logs from Fitbit for the user."""
        before_date = datetime.now()
        return list(self.get_activity_log_generator(before_date=before_date))
        # activities_logs = []
        # for activity in self.get_activity_log_generator(before_date=before_date):
        #     activities_logs.append(activity)
        # return activities_logs

    def get_activity_log_generator(
        self,
        before_date: datetime | None = None,
        after_date: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
        sort: Literal["asc", "desc"] = "desc",
    ) -> Generator[Activity, None, None]:
        """Generate a stream of Activity objects from Fitbit activity logs.

        This is a generator that yields Activity objects from Fitbit activity logs.
        It handles pagination automatically, fetching additional data as needed.

        Args:
            before_date: The date to retrieve data before.
                Defaults to None.
            after_date: The date to retrieve data after.
                Defaults to None.
            limit: The number of records to retrieve per request.
                Defaults to 100.
            offset: The offset to start retrieving records from.
                Defaults to 0.
            sort: The sort order for the activities.
                Defaults to 'desc'.

        Yields:
            Activity: An Activity object representing a single activity log entry.

        Note:
            This generator will continue to yield activities until all available data
            has been retrieved.
        """
        has_more = True
        while has_more:
            data = self.get_activity_logs(
                before_date=before_date,
                after_date=after_date,
                limit=limit,
                offset=offset,
                sort=sort,
            )
            # self.activity_log.integrate_activities_list(data["activities"], continuous=True)

            for activity in data["activities"]:
                try:
                    yield Activity(**activity)
                except TypeError as e:
                    logger.exception("Error processing activity log")
                    logger.debug("Activity data: %s", activity)
                    logger.debug("Missing required fields: %s", str(e.args))
                    raise TypeError from e

            if data["pagination"].get("next", "") != "":
                offset = int(re.search(r"offset=(\d+)", data["pagination"]["next"]).group(1))
                has_more = True
            else:
                has_more = False

    @cache
    def get_activities_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        min_duration: float = 15_000.0,
    ) -> list[Activity]:
        """Fetches activities within a specified date range."""
        activities_logs: list[Activity] = []

        # If activities are not in the activity log, fetch activities from Fitbit API
        for activity in self.get_activity_log_generator(before_date=end_date):
            # activity_date = datetime.fromisoformat(activity.start_date)
            duration: int | None = activity.duration or activity.originalDuration
            if duration and duration < min_duration:
                continue
            if activity.start_date < start_date:
                break
            activities_logs.append(activity)

        activities_logs.sort()

        return activities_logs

    @cached_property
    def lifetime_stats(self):
        """Fetches the user's lifetime statistics.

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
        url = "https://api.fitbit.com/1/user/-/activities.json"
        return self.api_client.make_request(url)

    @cache
    def daily_stats(
        self,
        activity: Literal[
            "activityCalories",
            "calories",
            "caloriesBMR",
            "distance",
            "elevation",
            "floors",
            "minutesSedentary",
            "minutesLightlyActive",
            "minutesFairlyActive",
            "minutesVeryActive",
            "steps",
            "swimming-strokes",
            "tracker/activityCalories",
            "tracker/calories",
            "tracker/distance",
            "tracker/elevation",
            "tracker/floors",
            "tracker/minutesSedentary",
            "tracker/minutesLightlyActive",
            "tracker/minutesFairlyActive",
            "tracker/minutesVeryActive",
            "tracker/steps",
        ],
        start_date: datetime,
        end_date: datetime,
    ) -> ActivityTimeSeriesResponseDict | ActiveZoneMinutesSeriesResponseDict:
        """Fetches the user's daily activity statistics.

        Args:
            activity: The type of activity to retrieve.
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
        """
        #  /1/user/[user-id]/activities/[resource-path]/date/[start-date]/[end-date].json
        #  GET https://api.fitbit.com/1/user/-/activities/steps/date/2019-01-01/2019-01-07.json
        if activity == "activityCalories" or (
            activity == "tracker/activityCalories"
            and (end_date - start_date).days > DailyStatsMaxDateRange.activityCalories
        ):
            msg = f"Maximum range for {activity} is 30 days. Received {(end_date - start_date).days} days."
            raise ValueError(msg)
        if (end_date - start_date).days > DailyStatsMaxDateRange.OTHER:
            msg = f"Maximum range for {activity} is 1095 days. Received {(end_date - start_date).days} days."
            raise ValueError(msg)

        url = f"https://api.fitbit.com/1/user/-/activities/{activity}/date/{start_date:%Y-%m-%d}/{end_date:%Y-%m-%d}.json"
        return self.api_client.make_request(url)

    @cached_property
    def activities_last_whole_month(self) -> list[Activity]:
        """Returns the list of activity records from the last whole month."""
        today: date = date.today()
        first_day_of_current_month: datetime = datetime(
            year=today.year,
            month=today.month,
            day=1,
            hour=12,
            minute=0,
            second=0,
        )
        start_date: datetime = first_day_of_current_month - relativedelta(months=1)
        end_date: datetime = first_day_of_current_month

        return self.get_activities_date_range(start_date.date(), end_date.date())

    # Variable calculation functions/properties
    @cached_property
    def daily_step_counts_last_6_months(self) -> dict[str, list[dict[str, str]]]:
        end_date = date.today()
        start_date = end_date - relativedelta(months=6)
        # return self.daily_step_counts("tracker/steps", start_date, end_date)
        return self.daily_stats("steps", start_date, end_date)

    @cached_property
    def highest_daily_steps_last_6_months_date_steps(
        self,
    ) -> tuple[datetime, int] | tuple[None, None]:
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
        return None, None

    @cached_property
    def average_weekly_heart_zone_time_last_6_months(self) -> float | None:
        end_date: datetime = date.today()
        start_date: datetime = end_date - relativedelta(months=6)

        data = {
            key: [value["activeZoneMinutes"] for value in values]
            for key, values in group_time_series(
                self.daily_stats("active-zone-minutes", start_date, end_date),
                GroupingFunctions.by_calendar_week,
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
            "tracker/minutesLightlyActive",
            "tracker/minutesFairlyActive",
            "tracker/minutesVeryActive",
        ]
        data = merge_time_series([
            group_time_series(
                self.daily_stats(activity_type, start_date, end_date),
                GroupingFunctions.by_calendar_week,
            )
            for activity_type in activity_types
        ])

        average = sum(AggregationFunctions.sum(data).values()) / 26
        if average > 0:
            return round(average, 1)
        return None

    @cached_property
    def average_weekly_active_time_all_sources_last_6_months(self) -> float | None:
        end_date: datetime = date.today()
        start_date: datetime = end_date - relativedelta(months=6)
        activity_types = [
            "minutesLightlyActive",
            "minutesFairlyActive",
            "minutesVeryActive",
        ]
        data = merge_time_series([
            group_time_series(
                self.daily_stats(activity=activity_type, start_date=start_date, end_date=end_date),
                GroupingFunctions.by_calendar_week,
            )
            for activity_type in activity_types
        ])

        average = sum(AggregationFunctions.sum(data).values()) / 26
        if average > 0:
            return round(average, 1)
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
            sum(sum(durations) for durations in weekly_stats.values()) / 26 / 60_000
            # convert milliseconds to minutes
        )
        if average > 0:
            return round(average, 1)
        return None

    @cached_property
    def devices(self) -> list[DeviceDict]:
        url = "https://api.fitbit.com/1/user/-/devices.json"
        return self.api_client.make_request(url)

    @cached_property
    def account_created_at_least_6_months_ago(self) -> bool:
        user = self.user_profile
        creation_date = datetime.strptime(user["memberSince"], "%Y-%m-%d").date()
        return creation_date <= date.today() - relativedelta(months=6)

    @cached_property
    def has_activities_last_whole_month(self) -> bool:
        return len(self.activities_last_whole_month_counts) > 0

    @cached_property
    def activities_last_whole_month_counts(self) -> dict[str, int]:
        """The number of times each activity was done over the last entire month."""
        activity_counts: dict[str, int] = {}
        for activity in self.activities_last_whole_month:
            name: str = activity.activityName or ""
            if name in activity_counts:
                activity_counts[name] += 1
            else:
                activity_counts[name] = 1

        return activity_counts

    @cached_property
    def activities_last_whole_month_total(self) -> int | None:
        total = sum(self.activities_last_whole_month_counts.values())
        if total > 0:
            return total
        return None

    @cached_property
    def activities_last_whole_month_walk_distance(self) -> float | None:
        walks = [
            act.distance or 0.0
            for act in self.activities_last_whole_month
            if (name := act.activityName or "") and "walk" in name.casefold()
        ]
        if len(walks) > 0:
            return round(sum(walks) / len(walks), 1)
        return None

    @cached_property
    def activities_last_whole_month_run_gps(self) -> int | None:
        runs = [
            act
            for act in self.activities_last_whole_month
            if (name := act.activityName or "")
            and "run" in name.casefold()
            and act.tcxLink is not None
            and act.tcxLink != ""
        ]
        num_runs: int = len(runs)
        if num_runs > 0:
            return num_runs
        return None

    @cached_property
    def activities_last_whole_month_workout_duration(self) -> float | None:
        workout_durations = [
            act.duration or 0.0
            for act in self.activities_last_whole_month
            if (name := act.activityName or "") and name.casefold() == "workout"
        ]
        num_workouts: int = len(workout_durations)
        if num_workouts > 0:
            return round(sum(workout_durations) / num_workouts / 60_000, 1)
        return None
