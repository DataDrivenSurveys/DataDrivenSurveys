#!/usr/bin/env python3
"""Created on 2023-10-31 13:53.

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
@author: Stefan Teofanovic (stefan.teofanovic@heig-vd.ch)
"""
from __future__ import annotations

__all__ = ["SurveyMonkeySurveyPlatform"]

import json
import os
import traceback
import uuid
from typing import Any, ClassVar, Optional

import requests
from surveymonkey.client import Client as SMClient
from surveymonkey.exceptions import (
    AuthorizationError,
    BadRequestError,
    InternalServerError,
    PermissionError,
    RateLimitReachedError,
    RequestEntityTooLargeError,
    ResourceConflictError,
    ResourceNotFoundError,
    UnknownError,
    UserDeletedError,
    UserSoftDeletedError,
)

from ddsurveys.get_logger import get_logger
from ddsurveys.survey_platforms.bases import FormButton, FormField, OAuthSurveyPlatform

logger = get_logger(__name__)


class SurveyMonkeySurveyPlatform(OAuthSurveyPlatform):
    API_URL = "https://api.surveymonkey.com/v3"

    # Form fields declarations go here
    form_fields: ClassVar = [
        FormField(
                name="survey_id",
                data_type="text",
                required=False,
                data={"helper_url": "Update me"},
        ),
        FormField(
                name="access_token",
                data_type="text",
                required=True,
                disabled=True,
                visibility_conditions={
                    "show": [{"field": "access_token", "operator": "is_not_empty"}],
                    "hide": [{"field": "access_token", "operator": "is_empty"}],
                },
        ),
        FormButton(
                name="authorize",
                on_click={
                    "action": "open_authorize_url",
                    "args": {
                        "auth_url": "https://api.surveymonkey.com/oauth/authorize?client_id={"
                                    "url:client_id}&response_type=code"
                    },
                },
                visibility_conditions={
                    "hide": [{"field": "access_token", "operator": "is_not_empty"}]
                },
        ),
        FormButton(
                name="re-authorize",
                on_click={
                    "action": "open_authorize_url",
                    "args": {
                        "auth_url": "https://api.surveymonkey.com/oauth/authorize?client_id={"
                                    "url:client_id}&response_type=code"
                    },
                },
                visibility_conditions={
                    "hide": [{"field": "access_token", "operator": "is_empty"}]
                },
        ),
    ]

    def __init__(
            self,
            survey_id: str = "",
            client_id: str = "",
            client_secret: str = "",
            access_token: str = "",
            **kwargs,
    ) -> None:
        """Args:
        client_id:
        client_secret:
        access_token:
        refresh_token:
        **kwargs:
        """
        super().__init__(**kwargs)

        self.survey_id: str = survey_id
        self.client_id: str = client_id
        self.client_secret: str = client_secret
        self.access_token: str = access_token
        self.redirect_uri: str = kwargs.get("redirect_uri", None)

        if self.redirect_uri is None:
            self.redirect_uri = self.get_redirect_uri()

        self.api_client: SMClient
        self.init_api_client(self.client_id, self.client_secret)

    # OAuthSurveyPlatform methods
    def init_api_client(
            self,
            client_id: str,
            client_secret: str,
            redirect_uri: str | None = None,
            access_token: str | None = None,
            *args,
            **kwargs,
    ) -> None:
        self.client_id: str = client_id
        self.client_secret: str = client_secret

        self.api_client = SMClient(
                client_id=self.client_id,
                client_secret=self.client_secret,
                redirect_uri=self.redirect_uri,
                access_token=self.access_token if self.access_token else None,
        )

    def init_oauth_client(self, *args, **kwargs) -> None:
        pass

    @classmethod
    def get_app_credentials(cls) -> dict[str, str]:
        return {
            "client_id": os.getenv("APP_SURVEY_MONKEY_CLIENT_ID", ""),
            "client_secret": os.getenv("APP_SURVEY_MONKEY_CLIENT_SECRET", ""),
        }

    @classmethod
    def get_authorize_url(cls) -> str:
        app_credentials = cls.get_app_credentials()
        sm_client = SMClient(**app_credentials, redirect_uri=cls.get_redirect_uri())
        return sm_client.get_authorization_url()

    def get_client_id(self) -> str:
        ...

    def request_token(self, code: str) -> dict[str, Any]:

        token = self.api_client.exchange_code(code=code)

        if token is False:
            return {"success": False, "message": "Error exchanging code for tokens"}

        return {"success": True, "data": json.loads(token)}

    def revoke_token(self, token: str) -> bool:
        ...

    # SurveyPlatform methods
    def fetch_survey_platform_info(self) -> tuple[int, str | None, dict[str, Any]]:
        survey_platform_info = {
            "connected": False,
            "active": False,
            "exists": False,
            "survey_name": None,
            "survey_status": "unknown",
        }

        message_id = None

        try:
            survey_info = self.get_specific_survey(self.survey_id)

            logger.debug("SurveyMonkeySurveyPlatform survey_info: %s", survey_info)

            survey_platform_info["survey_name"] = survey_info["title"]
            survey_platform_info["active"] = True
            survey_platform_info["survey_status"] = "active"
            survey_platform_info["exists"] = True
            survey_platform_info["connected"] = True
        except Exception:
            logger.exception("Error fetching survey platform info: %s")
            logger.debug(traceback.format_exc())
            return 400, "api.survey_platforms.connection_failed", survey_platform_info
        else:
            return 200, message_id, survey_platform_info

    def handle_project_creation(
            self, project_name: str, *, use_existing_survey: bool = False
    ) -> tuple[int, str, str, str, dict[str, Any]]:
        survey_platform_fields = {
            "survey_id": self.survey_id,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "access_token": self.access_token,
            "survey_status": "unknown",
        }

        if use_existing_survey:
            if not self.survey_id:
                return 400, "api.survey.missing_id", "Survey ID is required", None, {}

            try:
                survey_info = self.get_specific_survey(self.survey_id)
                logger.debug("SurveyMonkeySurveyPlatform survey_info: %s", survey_info)
                survey_name = survey_info["title"]

                survey_platform_fields["survey_name"] = survey_name
                survey_platform_fields["survey_status"] = "active"
            except Exception:
                logger.exception("Error creating a new survey: %s")
                logger.debug(traceback.format_exc())
                return (
                    400,
                    "api.survey.unknown_error_occurred",
                    "Unknown error occurred, please check your App Credentials",
                    None,
                    {},
                )
            else:
                return (
                    200,
                    "api.survey_platforms.project_creation_success",
                    "Project created successfully",
                    survey_name,
                    survey_platform_fields,
                )
        else:
            try:
                # create a survey in SurveyMonkey
                new_survey = self.api_client.create_new_blank_survey(title=project_name)

                self.survey_id = new_survey["id"]
                survey_platform_fields["survey_id"] = self.survey_id
                survey_platform_fields["survey_name"] = project_name

            except Exception:
                logger.exception("Error creating a new survey: %s")
                logger.debug(traceback.format_exc())
                return (
                    400,
                    "api.survey.unknown_error_occurred",
                    "Unknown error occurred, please check your App Credentials",
                    None,
                    {},
                )

        return 200, "", "", project_name, survey_platform_fields

    def handle_variable_sync(self, enabled_variables: dict) -> tuple[int, str, str]:

        variables: dict[str, str] = {
            variable["qualified_name"]: variable["test_value_placeholder"]
            for variable in enabled_variables
        }

        modified_variables = {
            key.replace(".", "_").replace("[", "_").replace("]", ""): value
            for key, value in variables.items()
        }

        try:
            response = self.modify_specific_survey(
                    self.survey_id, custom_variables=modified_variables
            )
            logger.debug("SurveyMonkeySurveyPlatform response: %s", response)

            if response.get("error"):
                return (
                    400,
                    "api.ddsurveys.survey_platforms.variables_sync.failed",
                    "Failed to sync variables!",
                )
        except Exception:
            logger.exception("Error syncing variables: %s")
            logger.debug(traceback.format_exc())
            return (
                401,
                "api.ddsurveys.survey_platforms.variables_sync.request_failed",
                "Failed to process sync request. Please check your API key and survey ID.",
            )
        else:
            return (
                200,
                "api.ddsurveys.survey_platforms.variables_sync.success",
                "Variables synced successfully!",
            )

    def handle_prepare_survey(
            self, project_short_id: str, survey_platform_fields: dict, embedded_data: dict
    ) -> tuple[bool, str | None]:
        """Handle the preparation of the survey for data collection in SurveyMonkey."""
        status, _, survey_platform_info = self.fetch_survey_platform_info()

        contact_list_id = survey_platform_fields.get("contact_list_id")

        if status != 200:
            return False, None

        if not survey_platform_info["active"]:
            return False, None

        if not contact_list_id:

            # Create a new contact list for the survey
            new_contact_list = self.create_contact_list(
                    list_name=f"DataDrivenSurveys -- {project_short_id}"
            )

            contact_fields = self.get_contact_fields()
            contact_field_ids = [
                field["id"] for field in contact_fields.get("data", [])
            ]

            field_id_to_key_map = {}
            for field_id, (key, _value) in zip(contact_field_ids, embedded_data.items(), strict=False):
                self.update_contact_field(field_id, key)
                field_id_to_key_map[field_id] = key

            contact_list_id = new_contact_list.get("id")

            # update the survey_platform_fields
            survey_platform_fields["contact_list_id"] = contact_list_id
            survey_platform_fields["contact_fields"] = field_id_to_key_map

        contact_fields = survey_platform_fields.get("contact_fields")

        filled_contact_fields = {
            field_id: embedded_data.get(label)
            for field_id, label in contact_fields.items()
        }

        new_contact_id = self.create_contact(
                contact_list_id, filled_contact_fields
        ).get("id")

        survey_id = survey_platform_fields.get("survey_id")

        # Update the contact with custom fields (embedded data)
        if survey_id and contact_list_id and new_contact_id:
            collector = self.create_or_get_collector(survey_id)

            # Generate a unique link for the survey
            unique_link = collector.get("url")

            return True, unique_link
        else:
            return False, None

    def handle_export_survey_responses(self) -> tuple[bool, str, None]:
        """Handle the downloading of responses from the survey platform."""
        raise NotImplementedError

    @staticmethod
    def get_preview_link(
            survey_platform_fields, enabled_variables
    ) -> tuple[int, str, str, str]:
        """Handle the previewing of the survey."""
        raise NotImplementedError

    # Temporary Survey Monkdey SDK methods
    # using these function because the SM SDK does not handle errors properly, it only works well for 200 responses
    def get_specific_survey(self, survey_id: str) -> dict:
        # https://api.surveymonkey.com/v3/docs#api-endpoints-surveys-id-
        logger.debug(
                "SurveyMonkeySurveyPlatform.get_specific_survey: %s", self.access_token
        )
        endpoint = f"/surveys/{survey_id}"
        url = SurveyMonkeySurveyPlatform.API_URL + endpoint
        _headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.get(url, headers=_headers)
        return response.json()

    def modify_specific_survey(
            self, survey_id: str, custom_variables: dict[str, str]
    ) -> dict:
        # https://api.surveymonkey.com/v3/docs#api-endpoints-patch-surveys-id-
        endpoint = f"/surveys/{survey_id}"
        url = SurveyMonkeySurveyPlatform.API_URL + endpoint
        _headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        _data = {"custom_variables": custom_variables}
        response = requests.patch(url, headers=_headers, data=json.dumps(_data))
        return response.json()

    def get_contact_fields(self) -> dict:
        url = self.API_URL + "/contact_fields"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
        }
        response = requests.get(url, headers=headers)
        return response.json()

    def update_contact_field(self, field_id: str, new_label: str) -> None:
        url = f"{self.API_URL}/contact_fields/{field_id}"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        data = {"label": new_label}
        requests.patch(url, headers=headers, json=data)

    def create_contact_list(self, list_name: str) -> dict:
        """Create a new contact list in SurveyMonkey.

        Args:
            access_token (str): The OAuth access token for authentication.
            list_name (str): The name of the new contact list.

        Returns:
            dict: The response from the SurveyMonkey API.
        """
        endpoint = "/contact_lists"
        url = SurveyMonkeySurveyPlatform.API_URL + endpoint
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        data = {"name": list_name}
        response = requests.post(url, headers=headers, json=data)

        # Check for successful response
        if response.status_code == 201:
            return response.json()
        logger.error("Failed to create contact list: %s", response.text)
        return {}

    def create_or_get_collector(self, survey_id: str) -> dict:
        """Create or get a web link collector for a SurveyMonkey survey.

        Args:
            survey_id (str): The ID of the survey for which the collector is needed.

        Returns:
            dict: The response from the SurveyMonkey API with collector details.
        """
        # Endpoint to check for existing collectors
        check_endpoint = f"/surveys/{survey_id}/collectors"
        check_url = SurveyMonkeySurveyPlatform.API_URL + check_endpoint
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        # Check for existing collectors
        check_response = requests.get(check_url, headers=headers, timeout=10)
        if check_response.status_code == 200:
            collectors = check_response.json().get("data", [])
            if collectors:
                # Fetch the full details of the first existing collector
                collector_id = collectors[0]["id"]
                details_endpoint: str = f"/collectors/{collector_id}"
                details_url: str = SurveyMonkeySurveyPlatform.API_URL + details_endpoint
                details_response: requests.Response = requests.get(details_url, headers=headers, timeout=10)
                if details_response.status_code == 200:
                    return details_response.json()

        # No existing collector found, create a new one
        create_endpoint = f"/surveys/{survey_id}/collectors"
        create_url = SurveyMonkeySurveyPlatform.API_URL + create_endpoint

        data = {
            "type": "weblink",  # Assuming a web link collector is needed
            "name": f"Collector for Survey {survey_id}",
        }

        create_response = requests.post(create_url, headers=headers, json=data, timeout=10)

        if create_response.status_code == 201:
            return create_response.json()
        logger.error("Failed to create or get collector: %s", create_response.text)
        return {}

    def create_contact(self, contact_list_id: str, filled_contact_fields: dict) -> dict:
        """Create a new contact in a specified contact list in SurveyMonkey.

        Args:
            access_token (str): The OAuth access token for authentication.
            contact_list_id (str): The ID of the contact list where the contact will be added.
            contact_data (dict): The data for the new contact.

        Returns:
            dict: The response from the SurveyMonkey API.
        """
        endpoint = f"/contact_lists/{contact_list_id}/contacts"
        url = SurveyMonkeySurveyPlatform.API_URL + endpoint
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        # generate an unique email for the contact
        contact_email = f"{uuid.uuid4()}@{contact_list_id}.com"

        # replace None values with empty strings
        filled_contact_fields = {
            key: (
                str(value).lower()
                if isinstance(value, bool)
                else ("" if value is None else str(value))
            )
            for key, value in filled_contact_fields.items()
        }

        data = {
            "email": contact_email,
            "custom_fields": filled_contact_fields,
        }

        response: requests.Response = requests.post(url, headers=headers, json=data, timeout=10)

        # Check for successful response
        if response.status_code == 201:
            return response.json()

        logger.error("Failed to create contact: %s", response.text)
        return {}
