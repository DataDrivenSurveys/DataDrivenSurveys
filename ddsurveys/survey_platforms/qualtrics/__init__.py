#!/usr/bin/env python3
"""Created on 2023-04-27 13:48.

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
@author: Stefan Teofanovic (stefan.teofanovic@heig-vd.ch)
"""
from __future__ import annotations

import traceback
from typing import Any, ClassVar
from urllib.parse import quote_plus

from ddsurveys.get_logger import get_logger
from ddsurveys.survey_platforms.bases import FormField, SurveyPlatform

# API related classes
from ddsurveys.survey_platforms.qualtrics.api import (
    AuthorizationError,
    DistributionsAPI,
    FailedQualtricsRequest,
    SurveysAPI,
)

# Classes used to conveniently create objects that get sent to Qualtrics
from ddsurveys.survey_platforms.qualtrics.embedded_data import EmbeddedDataBlock
from ddsurveys.survey_platforms.qualtrics.flow import Flow

# Main platform class
# from .qualtrics_platform import QualtricsSI

__all__ = ["QualtricsSurveyPlatform"]


logger = get_logger(__name__)


class QualtricsSurveyPlatform(SurveyPlatform):
    """Qualtrics survey platform class.

    This class provides the methods needed to integrate and interact with the Qualtrics
    survey platform.
    """

    # Form fields declarations go here
    form_fields: ClassVar = [
        FormField(
            name="survey_id",
            data_type="text",
            required=False,
            data={"helper_url": "https://host.qualtrics.com/survey-builder/{ID}/edit"},
        ),
        FormField(
            name="survey_platform_api_key",
            data_type="text",
            required=True,
            data={
                "helper_url": "https://api.qualtrics.com/ZG9jOjg3NjYzMg-api-key-authentication"
            },
        ),
    ]

    def __init__(
        self, survey_id: str | None = None, survey_platform_api_key: str | None = None, **kwargs
    ) -> None:
        """Initialize the QualtricsSurveyPlatform instance.

        This constructor initializes the QualtricsSurveyPlatform with the provided
        survey ID and API key.
        It also sets up the necessary API clients for interacting with the Qualtrics
        platform.

        Args:
            survey_id: The ID of the survey.
                Default is None.
            survey_platform_api_key: The API key for accessing the Qualtrics platform.
                Default is None.
            **kwargs: Additional keyword arguments passed to the parent class
                constructor.
        """
        super().__init__(**kwargs)
        self.survey_id = survey_id
        self.survey_platform_api_key = survey_platform_api_key

        self.surveys_api = SurveysAPI(api_token=self.survey_platform_api_key)
        self.distributions_api = DistributionsAPI(
            api_token=self.survey_platform_api_key
        )

    def fetch_survey_platform_info(self) -> tuple[int, str | None, dict[str, Any]]:
        survey_platform_info = {
            "connected": False,
            "active": False,
            "exists": False,
            "survey_name": None,
            "survey_status": "unknown",
        }

        message_id = None

        if not self.surveys_api.survey_exists(self.survey_id):
            return (
                400,
                "api.survey_platforms.connection_failed",
                survey_platform_info,
            )

        try:
            survey_info = self.surveys_api.get_survey(self.survey_id).json()
            survey_active = survey_info["result"]["SurveyStatus"] == "Active"

            survey_platform_info["survey_name"] = survey_info["result"][
                "SurveyName"
            ]
            survey_platform_info["active"] = survey_active
            survey_platform_info["survey_status"] = (
                "active" if survey_active else "inactive"
            )
            survey_platform_info["exists"] = True
            survey_platform_info["connected"] = True
        except FailedQualtricsRequest:
            return 400, None, survey_platform_info
        else:
            return 200, message_id, survey_platform_info

    def handle_project_creation(
        self, project_name: str, *, use_existing_survey: bool = False
    ) -> tuple[int, str, str, str | None, dict[str, Any]]:
        # survey_platform_fields to update project.survey_platform_fields
        logger.debug("Creating project with name: %s", project_name)

        survey_platform_fields = {
            "survey_id": self.survey_id,
            "survey_platform_api_key": self.survey_platform_api_key,
            "survey_name": None,
            "base_url": None,
        }

        if use_existing_survey:
            if not self.survey_id:
                return 400, "api.survey.missing_id", "Survey ID is required", None, {}

            try:
                survey_info = self.surveys_api.get_survey(self.survey_id).json()
                survey_name = survey_info["result"]["SurveyName"]
                base_url = survey_info["result"]["BrandBaseURL"]
                survey_platform_fields["survey_name"] = survey_name
                survey_platform_fields["base_url"] = base_url

                if not project_name:
                    project_name = survey_name

            except AuthorizationError:
                return (
                    400,
                    "api.survey.failed_to_retrieve_survey_name",
                    "Failed to retrieve survey name, please check your API key and survey ID",
                    None,
                    {},
                )
            except FailedQualtricsRequest:
                return (
                    400,
                    "api.survey.unknown_error_occurred",
                    "Unknown error occurred, please check your API key and survey ID",
                    None,
                    {},
                )

        else:
            try:
                response = self.surveys_api.create_survey(
                    survey_name=project_name
                ).json()

                if "result" in response:
                    # Must get the survey info to get the base url
                    survey_info = self.surveys_api.get_survey(
                        response["result"]["SurveyID"]
                    ).json()
                    # survey_name = survey_info["result"]["SurveyName"]
                    survey_id = response["result"]["SurveyID"]
                    base_url = survey_info["result"]["BrandBaseURL"]

                    self.survey_id = survey_id
                    survey_platform_fields["survey_id"] = survey_id
                    survey_platform_fields["survey_name"] = project_name
                    survey_platform_fields["base_url"] = base_url
                else:
                    logger.error("Failed to create survey")
                    return (
                        400,
                        "api.survey.unknown_error_occurred",
                        "Unknown error occurred, please check your API key and survey ID",
                        None,
                        {},
                    )

            except FailedQualtricsRequest:
                logger.exception("Failed to create survey: %s")
                logger.debug(traceback.format_exc())
                return (
                    400,
                    "api.survey.create_failed",
                    "Failed to create survey",
                    None,
                    {},
                )

        return 200, "", "", project_name, survey_platform_fields

    def handle_variable_sync(self, enabled_variables) -> tuple[int, str, str]:
        """Handle the syncing of variables for the given survey."""
        # Get the initial flow
        try:
            flow = Flow(self.surveys_api.get_flow(self.survey_id).json()["result"])

            ed_block = EmbeddedDataBlock.from_variables(
                flow_id=flow.custom_variables_block_id, variables=enabled_variables
            )

            # Add the new variables to the flow
            flow.custom_variables.overwrite_custom_variables(ed_block)

            # Update the variables on Qualtrics
            resp = self.surveys_api.update_flow(self.survey_id, flow.to_dict())
            if resp.status_code != 200:
                return (
                    400,
                    "api.ddsurveys.survey_platforms.variables_sync.failed",
                    "Failed to sync variables!",
                )
        except (FailedQualtricsRequest, PermissionError):
            logger.exception("Failed to sync Qualtrics variables: %s")
            logger.debug("Failed to sync variables for survey %s", self.survey_id)
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
        """Handle the preparation of the survey for data collection."""
        try:
            status, _, survey_platform_info = self.fetch_survey_platform_info()

            mailing_list_id = survey_platform_fields.get("mailing_list_id")
            directory_id = survey_platform_fields.get("directory_id")

            if status != 200:
                return False, None

            if not survey_platform_info["active"]:
                return False, None

            if not mailing_list_id or not directory_id:
                # the first respondent will create the mailing list and directory
                directory_id = self.distributions_api.get_first_directory_id()

                if not mailing_list_id:
                    # Get the user id of the account making API calls
                    user_id = self.distributions_api.get_user_id()
                    # Create a new mailing list for the survey in the first directory
                    mailing_list_id = self.distributions_api.create_mailing_list(
                        directory_id,
                        f"DataDrivenSurveys -- ${project_short_id}",
                        user_id,
                    ).json()["result"]["id"]

                    # update the survey_platform_fields
                    survey_platform_fields["mailing_list_id"] = mailing_list_id
                    survey_platform_fields["directory_id"] = directory_id
            # Create a new contact in the mailing list
            new_contact_dict = self.distributions_api.create_contact(
                directory_id, mailing_list_id, embedded_data
            )
            contact_lookup_id = new_contact_dict["contactLookupId"]

            survey_id = survey_platform_fields.get("survey_id")

            # Create a unique distribution link for the contact
            if survey_id and mailing_list_id and contact_lookup_id:
                try:
                    unique_url = self.distributions_api.create_unique_distribution_link(
                        survey_id, mailing_list_id, contact_lookup_id
                    )
                except FailedQualtricsRequest:
                    return False, None

                if unique_url:
                    return True, unique_url

            else:
                return False, None

        except FailedQualtricsRequest:
            logger.debug("Failed to prepare survey for data collection")
            return False, None

    def handle_export_survey_responses(self) -> tuple[int, str, str, bytes | str | None]:
        """Handle the downloading of responses from the survey platform."""
        try:
            content = self.surveys_api.export_survey_responses(self.survey_id)
            if content:
                return (
                    200,
                    "api.ddsurveys.survey_platforms.export_survey_responses.success",
                    "Exported survey responses successfully!",
                    content,
                )
            return (
                400,
                "api.ddsurveys.survey_platforms.export_survey_responses.failed",
                "Failed to export survey responses!",
                None,
            )

        except FailedQualtricsRequest:
            return (
                400,
                "api.ddsurveys.survey_platforms.export_survey_responses.request_failed",
                "Failed to process export request. Please check your API key and survey ID.",
                None,
            )

    @staticmethod
    def get_preview_link(
        survey_platform_fields: dict, enabled_variables: list[dict]
    ) -> tuple[int, str, str, str]:
        if (
            "base_url" not in survey_platform_fields
            or "survey_id" not in survey_platform_fields
        ):
            return (
                400,
                "api.ddsurveys.survey_platforms.get_preview_link.error",
                "Failed to get preview link. Please check your survey ID and base URL.",
                None,
            )

        base_url = survey_platform_fields["base_url"]
        survey_id = survey_platform_fields["survey_id"]

        url_params = "&".join(
            [
                f"{quote_plus(var['qualified_name'])}={quote_plus(var['test_value'])}"
                for var in enabled_variables
            ]
        )

        link = f"{base_url}/jfe/preview/{survey_id}?Q_CHL=preview&Q_SurveyVersionID=current&{url_params}"

        return (
            200,
            "api.ddsurveys.survey_platforms.get_preview_link.success",
            "Preview link retrieved successfully!",
            link,
        )
