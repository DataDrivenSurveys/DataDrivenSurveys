"""This module provides blueprints for respondent backend requests.

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
@author: Stefan Teofanovic (stefan.teofanovic@heig-vd.ch).
"""

from __future__ import annotations

import traceback
from http import HTTPStatus
from typing import TYPE_CHECKING, cast

from flask import Blueprint, Response, g, jsonify, request
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.attributes import flag_modified

from ddsurveys.blueprints._common import abbreviate_variable_name
from ddsurveys.blueprints._common import AppManagement
from ddsurveys.data_providers import DataProvider
from ddsurveys.data_providers.bases import (
    TOAuthDataProvider,
    TOAuthDataProviderClass,
)
from ddsurveys.get_logger import get_logger
from ddsurveys.models import (
    DataConnection,
    DataProviderAccess,
    DataProviderName,
    DataProviderType,
    DBManager,
    Distribution,
    Project,
    Respondent,
)
from ddsurveys.models import DataProvider as DataProviderModel
from ddsurveys.survey_platforms import SurveyPlatform
from ddsurveys.typings.models import SurveyPlatformFieldsDict

if TYPE_CHECKING:
    from collections.abc import Generator

    from ddsurveys.api_responses import APIResponseValue
    from ddsurveys.data_providers.bases import (
        OAuthDataProvider,
        TDataProviderClass,
        TFrontendDataProvider,
        TFrontendDataProviderClass,
    )
    from ddsurveys.survey_platforms.bases import TSurveyPlatform, TSurveyPlatformClass
    from ddsurveys.typings.data_providers.variables import ComputedVariableDict

logger = get_logger(__name__)

respondent = Blueprint("respondent", __name__)
"""location: /projects/<project_id>/respondent
All of the endpoints in blueprint file are public
"""


def get_project(db, short_id) -> Project:
    """Get a project by its short ID."""
    return db.query(Project).filter_by(short_id=short_id).first()


def get_used_data_providers(
    project: Project, respondent: Respondent
) -> Generator[tuple[OAuthDataProvider, DataProviderAccess, None, None], None, None] | tuple[None, None, Response, int]:
    """Get used data providers for a specific project and respondent."""
    # TODO: Update this function to return only two values.
    #       This should make code that uses this function easier to read and understand.
    data_provider: DataProviderAccess
    for data_provider in respondent.data_provider_accesses:
        data_provider_name = data_provider.data_provider_name.value
        access_token = data_provider.access_token
        refresh_token = data_provider.refresh_token

        if not access_token:
            logger.error("Missing access token for data provider: %s", data_provider_name)
            return (
                None,
                None,
                jsonify(
                    {
                        "message": {
                            "id": "api.data_provider.missing_tokens",
                            "text": "Missing data provider tokens",
                        }
                    }
                ),
                HTTPStatus.BAD_REQUEST,
            )

        # Get the correct data provider from the project.
        # We need its fields to create an instance of the data provider.
        project_data_connection = next(
            (dc for dc in project.data_connections if dc.data_provider.data_provider_name.value == data_provider_name),
            None,
        )

        if not project_data_connection:
            logger.error("Data provider not found: %s", data_provider_name)
            return (
                None,
                None,
                jsonify(
                    {
                        "message": {
                            "id": "api.data_provider.not_found",
                            "text": "Data provider not found",
                        }
                    }
                ),
                HTTPStatus.NOT_FOUND,
            )

        fields = project_data_connection.fields

        fields.update({"access_token": access_token, "refresh_token": refresh_token})

        user_data_provider: TOAuthDataProvider = cast(
            TOAuthDataProviderClass, DataProvider.get_class_by_value(data_provider_name)
        )(**fields)

        yield user_data_provider, data_provider, None, None


@respondent.route("/", methods=["GET"])
def get_public_project() -> APIResponseValue:
    """Reads public project data and checks the readiness of the project.

    This function checks the connection status of all data providers and the survey
    platform.
    The survey must also be active.
    It does not provide any detailed explanation of why the project is not ready.

    Returns:
        APIResponseValue:
            A JSON response containing the public project data and readiness status.
            Possible status codes are:
            - HTTPStatus.OK: Successfully retrieved project data.
            - HTTPStatus.BAD_REQUEST: Bad request, e.g., unknown survey platform.
            - HTTPStatus.NOT_FOUND: Project not found.
    """
    with DBManager.get_db() as db:
        project_short_id = g.get("project_short_id")
        project: Project | None = (
            db.query(Project)
            .options(
                joinedload(Project.data_connections).joinedload(DataConnection.data_provider),
            )
            .filter(Project.short_id == project_short_id)
            .first()
        )

        if not project:
            logger.error("Project with id %s not found.", project_short_id)
            return (
                jsonify(
                    {
                        "message": {
                            "id": "api.projects.not_found",
                            "text": "Project not found",
                        }
                    }
                ),
                HTTPStatus.NOT_FOUND,
            )

        response_dict = project.to_public_dict()
        response_status = HTTPStatus.OK

        all_data_connections_connected = True  # Assume all are connected until proven otherwise
        survey_platform_connected = False

        platform_class = SurveyPlatform.get_class_by_value(project.survey_platform_name)

        if not platform_class:
            logger.error("Unknown Survey Platform: %s", project.survey_platform_name)
            response_status = HTTPStatus.BAD_REQUEST
            all_data_connections_connected = False
        else:
            survey_platform = platform_class(**project.survey_platform_fields)

            # Fetch survey platform info using the platform method
            status, _, survey_platform_info = survey_platform.fetch_survey_platform_info()

            if status == HTTPStatus.OK:
                survey_platform_connected = survey_platform_info["connected"]
                survey_active = survey_platform_info["active"]
            else:
                logger.error(
                    "Survey on %s %s does not exist or there was an error fetching its info.",
                    project.survey_platform_name,
                    project.id,
                )
                response_status = HTTPStatus.BAD_REQUEST
                all_data_connections_connected = False

        project_dict = project.to_dict()

        variables_per_data_provider = DataProvider.get_used_variables(
            project_dict["variables"], project_dict["custom_variables"]
        )

        for data_connection in response_dict["data_connections"]:
            provider_type = data_connection["data_provider"]["data_provider_name"]
            provider_class: TDataProviderClass = DataProvider.get_class_by_value(provider_type)

            project_data_connections = project_dict["data_connections"]
            project_data_connection = next(
                (dc for dc in project_data_connections if dc["data_provider"]["data_provider_name"] == provider_type),
                None,
            )

            if not project_data_connection:
                all_data_connections_connected = False
                continue

            fields = project_data_connection["fields"]
            provider_instance = provider_class(**fields)
            if not provider_instance.test_connection():
                all_data_connections_connected = False

        has_oauth_data_providers = any(
            dc.data_provider.data_provider_type == DataProviderType.oauth for dc in project.data_connections
        )

        project_ready = (
            all_data_connections_connected and survey_platform_connected and survey_active and has_oauth_data_providers
        )
        response_dict["project_ready"] = project_ready
        response_dict["used_variables"] = variables_per_data_provider

        return jsonify(response_dict), response_status


@respondent.route("/data-providers", methods=["GET"])
def get_public_data_providers() -> APIResponseValue:
    """Provides the data providers information linked to a project.

    The data provider information enables a respondent to data providers linked to a
    project using the OAuth2 Code Flow.

    This is a public endpoint, so no authentication is required.
    This endpoint should not provide any sensitive information.

    Returns:
        APIResponseValue: A JSON response containing the details of data providers
            linked to the project.
            Possible status codes are:
            - HTTPStatus.OK: Successfully retrieved data providers.
            - HTTPStatus.NOT_FOUND: Project not found.
    """
    with DBManager.get_db() as db:
        project = get_project(db, g.get("project_short_id"))
        if not project:
            return (
                jsonify(
                    {
                        "message": {
                            "id": "api.projects.not_found",
                            "text": "Project not found",
                        }
                    }
                ),
                HTTPStatus.NOT_FOUND,
            )

        # Get all data providers linked to the project.
        data_providers = []
        for data_connection in project.data_connections:
            data_provider = data_connection.data_provider

            cunstructor_fields = data_connection.fields
            cunstructor_fields["builtin_variables"] = project.variables
            cunstructor_fields["custom_variables"] = project.custom_variables

            provider_class: TOAuthDataProviderClass = DataProvider.get_class_by_value(
                data_provider.data_provider_name.value
            )
            provider_instance: OAuthDataProvider = provider_class(**cunstructor_fields)

            dp_public_dict = provider_instance.to_public_dict()
            if dp_public_dict["type"] == "oauth":
                # Include data_connection.fields in the data provider dictionary.
                data_providers.append(dp_public_dict)

        return jsonify(data_providers), HTTPStatus.OK


@respondent.route("/exchange-code", methods=["POST"])
def exchange_code_for_tokens() -> APIResponseValue:
    """Exchanges the code for an access token. (using OAuth2 Code Flow).

    This is a public endpoint, so no authentication is required.
    This endpoint should not provide any sensitive information.
    """
    with DBManager.get_db() as db:
        data = request.get_json()

        data_provider_name = data.get("data_provider_name")

        project_short_id = g.get("project_short_id")

        # Get project and its associated data connections.
        project: Project = get_project(db, project_short_id)

        if not project:
            logger.error("No project found for project_short_id: %s", project_short_id)
            return (
                jsonify(
                    {
                        "message": {
                            "id": "api.projects.not_found",
                            "text": "Project not found",
                        }
                    }
                ),
                HTTPStatus.NOT_FOUND,
            )

        # Get the correct data provider from the project
        # (we need its fields to create an instance of the data provider)
        project_data_connection: DataConnection = next(
            (dc for dc in project.data_connections if dc.data_provider.data_provider_name.value == data_provider_name),
            None,
        )

        if not project_data_connection or project_data_connection is None:
            logger.error("No data connection for data provider: %s", data_provider_name)
            return (
                jsonify(
                    {
                        "message": {
                            "id": "api.data_provider.not_found",
                            "text": "Data provider not found",
                        }
                    }
                ),
                HTTPStatus.NOT_FOUND,
            )

        try:
            # Create an instance of the data provider
            provider_class = DataProvider.get_class_by_value(
                project_data_connection.data_provider.data_provider_name.value
            )
            provider_instance: OAuthDataProvider = provider_class(**project_data_connection.fields)

            # Exchange the code for an access token
            provider_instance.get_required_scopes(project.variables, project.custom_variables)
            logger.debug(data)
            response = provider_instance.request_token(data)

            if not response["success"]:
                logger.error("Error exchanging code for tokens for: %s", data_provider_name)
                return (
                    jsonify(
                        {
                            "message": {
                                "id": response.get(
                                    "message_id", "api.data_provider.exchange_code_error.unexpected_error"
                                ),
                                "text": response.get("text", "An unknown error occurred"),
                                "required_scopes": response.get("required_scopes", []),
                                "accepted_scopes": response.get("accepted_scopes", []),
                                "data_provider_name": provider_instance.name,
                            },
                        }
                    ),
                    HTTPStatus.BAD_REQUEST,
                )
        except Exception:
            logger.exception("Error exchanging code for tokens for: %s", data_provider_name)
            return (
                jsonify(
                    {
                        "message": {
                            "id": "api.data_provider.exchange_code_error.generic",
                            "text": "Error exchanging code for tokens",
                            "data_provider_name": provider_instance.name,
                        },
                    }
                ),
                HTTPStatus.INTERNAL_SERVER_ERROR,
            )
        else:
            logger.info("Successfully exchanged code for tokens for: %s", data_provider_name)
            return (
                jsonify(
                    {
                        "message": {
                            "id": "api.data_provider.exchange_code_success",
                            "text": "Successfully exchanged code for tokens",
                        },
                        "tokens": response,
                        "data_provider_name": provider_instance.name,
                    }
                ),
                HTTPStatus.OK,
            )


@respondent.route("/data-provider/was-used", methods=["POST"])
def was_data_provider_used() -> APIResponseValue:
    with DBManager.get_db() as db:
        project_short_id = g.get("project_short_id")

        # Get project and its associated data connections.
        project = get_project(db, project_short_id)

        if not project:
            logger.error("Project not found: %s", project_short_id)
            return (
                jsonify(
                    {
                        "message": {
                            "id": "api.projects.project_not_found",
                            "text": "Project not found",
                        }
                    }
                ),
                HTTPStatus.NOT_FOUND,
            )

        data = request.get_json()

        data_provider_name = DataProviderName(data.get("data_provider_name"))  # Converting the string to Enum.

        user_id = data.get("user_id")

        data_provider_access = (
            db.query(DataProviderAccess)
            .filter(
                DataProviderAccess.project_id == project.id,
                DataProviderAccess.data_provider_name == data_provider_name,
                DataProviderAccess.user_id == user_id,
            )
            .first()
        )

        if data_provider_access:
            return jsonify({"was_used": True}), HTTPStatus.OK
        return jsonify({"was_used": False}), HTTPStatus.OK


@respondent.route("/prepare-survey", methods=["POST"])
def prepare_survey() -> APIResponseValue:
    """Prepares a survey for a respondent.

     A survey is prepared by creating a unique distribution link and the handling data
     provider tokens.

    This function performs the following steps:
    1. Retrieves the project and respondent information from the database.
    2. Checks if the respondent already has a distribution link.
    3. Verifies if the survey is active on the specified survey platform.
    4. Collects and processes data from various data providers.
    5. Creates a unique distribution link for the respondent.

    Returns:
        APIResponseValue: A JSON response containing the distribution link or an error
            message.
            Possible status codes are:
            - HTTPStatus.OK: Successfully created a unique distribution link.
            - HTTPStatus.BAD_REQUEST: Missing respondent ID or unsupported survey
                platform.
            - HTTPStatus.NOT_FOUND: Project or respondent not found, or survey not
                active.
            - HTTPStatus.INTERNAL_SERVER_ERROR: Error preparing the survey.
    """
    try:
        with DBManager.get_db() as db:
            project_short_id = g.get("project_short_id")

            project: Project = get_project(db=db, short_id=project_short_id)

            if not project:
                logger.error("Project not found: %s", project_short_id)
                return (
                    jsonify(
                        {
                            "message": {
                                "id": "api.projects.not_found",
                                "text": "Project not found",
                            }
                        }
                    ),
                    HTTPStatus.NOT_FOUND,
                )

            data = request.get_json()

            respondent_id = data.get("respondent_id")
            frontend_variables = data.get("frontend_variables")

            if not respondent_id:
                logger.error("Missing respondent id.")
                return (
                    jsonify(
                        {
                            "message": {
                                "id": "api.respondent.missing_id",
                                "text": "Missing respondent id",
                            }
                        }
                    ),
                    HTTPStatus.BAD_REQUEST,
                )

            respondent: Respondent | None = (
                db.query(Respondent)
                .filter(
                    and_(
                        Respondent.id == respondent_id,
                        Respondent.project_id == project.id,
                    )
                )
                .first()
            )

            if not respondent:
                logger.error("Respondent not found.")
                return (
                    jsonify(
                        {
                            "message": {
                                "id": "api.respondent.not_found",
                                "text": "Respondent not found",
                            }
                        }
                    ),
                    HTTPStatus.NOT_FOUND,
                )

            # check if the respondent already has a distribution
            if respondent.distribution:
                logger.info("Respondent already has a distribution url.")

                for user_data_provider, data_provider, response, error_status in get_used_data_providers(
                    project, respondent
                ):
                    if response is not None and error_status is not None:
                        return response, error_status

                    # revoke the access tokens
                    try:
                        user_data_provider.revoke_token(data_provider.access_token)
                        logger.info("Revoked access token for data provider '%s'\n", user_data_provider.name)
                    except Exception:
                        logger.exception(
                            "Failed to revoke access token for data provider '%s'\n", user_data_provider.name
                        )
                        logger.debug(traceback.format_exc())

                    # set the data provider access tokens to Null
                    data_provider.access_token = None
                    data_provider.refresh_token = None

                    db.commit()

                # return the distribution url
                return (
                    jsonify(
                        {
                            "message": {
                                "id": "api.respondent.existing_distribution_url",
                                "text": "Respondent already has a distribution url",
                            },
                            "entity": respondent.distribution.to_dict(),
                        }
                    ),
                    HTTPStatus.OK,
                )

            # check if the survey is active
            # Get the platform class
            survey_platform_class: TSurveyPlatformClass = SurveyPlatform.get_class_by_value(
                project.survey_platform_name
            )

            if not survey_platform_class:
                logger.error("Unknown Survey Platform: %s", project.survey_platform_name)
                return (
                    jsonify(
                        {
                            "message": {
                                "id": "api.survey.platform_not_supported",
                                "text": "Survey platform not supported",
                            }
                        }
                    ),
                    HTTPStatus.BAD_REQUEST,
                )

            # Create an instance of the platform
            survey_platform: TSurveyPlatform = survey_platform_class(
                **cast(SurveyPlatformFieldsDict, project.survey_platform_fields)
            )

            survey_platform_status, _, survey_platform_info = survey_platform.fetch_survey_platform_info()

            if survey_platform_status != HTTPStatus.OK and not survey_platform_info.get("active", False):
                logger.error(
                    "Survey on %s %s does not exist or there was an error fetching its info.",
                    project.survey_platform_name,
                    project.id,
                )
                return (
                    jsonify(
                        {
                            "message": {
                                "id": "api.survey.not_active",
                                "text": "Survey not not active",
                            }
                        }
                    ),
                    HTTPStatus.NOT_FOUND,
                )

            # Create the data_to_upload dictionary outside the loop
            data_to_upload: ComputedVariableDict = {}

            # So that participants can revoke access later
            app_manage_urls: list[str | None] = []

            for user_data_provider, data_provider, response, error_status in get_used_data_providers(
                project, respondent
            ):
                if response is not None and error_status is not None:
                    return response, error_status

                app_manage_urls.append(AppManagement.app_urls.get(data_provider.to_dict()['data_provider_name'], None))

                data_to_upload.update(
                    user_data_provider.calculate_variables(project.variables, project.custom_variables)
                )

                # revoke the access tokens
                try:
                    user_data_provider.revoke_token(data_provider.access_token)
                except Exception:
                    logger.exception("Failed to revoke access token for data provider '%s'.", user_data_provider.name)

                # set the data provider access tokens to Null
                data_provider.access_token = None
                data_provider.refresh_token = None

                db.commit()

            frontend_data_providers: list[DataConnection] = [
                dc
                for dc in project.data_connections
                if dc.data_provider.data_provider_type == DataProviderType.frontend
            ]

            logger.debug('Length of frontend data providers %s', len(frontend_data_providers))
            for dc in frontend_data_providers:
                data_provider_name = dc.data_provider.data_provider_name.value
                logger.debug('Provider name is here %s', data_provider_name)

                provider_class: TFrontendDataProviderClass = DataProvider.get_class_by_value(data_provider_name)
                provider_instance: TFrontendDataProvider = provider_class()

                data_to_upload.update(
                    provider_instance.calculate_variables(
                        project_builtin_variables=project.variables,
                        data=frontend_variables,
                    )
                )
            logger.debug("Data to upload: %s", data_to_upload)

            data_to_upload = {
                abbreviate_variable_name(
                    variable_name=variable_name,
                    first_apply="dp",
                    strategy="full",
                    max_length=survey_platform.max_variable_name_length,
                ): value
                for variable_name, value in data_to_upload.items()
            }

            success_preparing_survey, unique_url = survey_platform.handle_prepare_survey(
                project_short_id=project_short_id,
                survey_platform_fields=project.survey_platform_fields,
                embedded_data=data_to_upload,
            )

            if success_preparing_survey:
                logger.debug("Preparing survey successful.")
                distribution = None
                if unique_url:
                    # create the related distribution for the respondent
                    distribution = Distribution(url=unique_url)

                    respondent.distribution = distribution

                    db.add(respondent)

                flag_modified(project, "survey_platform_fields")
                db.commit()
                logger.debug('App manage urls are %s', app_manage_urls[0])
                if survey_platform_status == HTTPStatus.OK:
                    return (
                        jsonify(
                            {
                                "message": {
                                    "id": "api.respondent.survey.distribution_link_created",
                                    "text": "Successfully created a unique distribution link",
                                },
                                "entity": distribution.to_dict(),
                                "app_manage": app_manage_urls,
                            }
                        ),
                        HTTPStatus.OK,
                    )
            else:
                logger.error("Failed to prepare survey.")
                if survey_platform_status == HTTPStatus.OK:
                    survey_platform_status = HTTPStatus.INTERNAL_SERVER_ERROR
                return (
                    jsonify(
                        {
                            "message": {
                                "id": "api.respondent.survey.failed_distribution_link",
                                "text": "Failed to create a unique distribution link",
                            },
                        }
                    ),
                    survey_platform_status,
                )

    except Exception:
        logger.exception("Error preparing survey.")
        return (
            jsonify(
                {
                    "message": {
                        "id": "api.respondent.survey.error",
                        "text": "Error preparing survey",
                    }
                }
            ),
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )


def check_data_provider_access_tokens(project_id, data_provider_name, access_token, refresh_token):
    with DBManager.get_db() as db:
        # Get project and its associated data connections.
        project = db.query(Project).get(project_id)
        if not project:
            logger.error("Project not found: %s", project_id)
            return False

        data_connection = (
            db.query(DataConnection).filter_by(project_id=project_id, data_provider_name=data_provider_name).first()
        )

        if not data_connection:
            logger.error("Data connection not found for: %s", data_provider_name)
            return False

        data_provider_name = data_connection.data_provider.data_provider_name.value

        fields: dict = data_connection.fields

        fields.update({"access_token": access_token, "refresh_token": refresh_token})

        provider_class = DataProvider.get_class_by_value(data_provider_name)

        if not provider_class:
            logger.error("Data provider type not found: %s", data_provider_name)
            return False

        user_data_provider: OAuthDataProvider = provider_class(**fields)

        return user_data_provider.test_connection_before_extraction()


@respondent.route("/connect", methods=["POST"])
def connect_respondent() -> APIResponseValue:
    """This function checks each data provider that it receives.

    This function receives a JSON array of data providers and performs checks
    for each one.

    If all data providers exist, it will return the already existing respondent.
    If some exist and some do not, it will return a bad request.
    If none exist, it will create an associated data providers and a new respondent
    and return it.
    It will check that each data provider access token is valid before updating or
    creating.
    """
    project_short_id = g.get("project_short_id")
    data_providers = request.get_json().get("data_providers")

    with DBManager.get_db() as db:
        # Get project and its associated data connections.
        project = get_project(db, project_short_id)
        if not project:
            logger.error("Project %s not found", project_short_id)
            return (
                jsonify(
                    {
                        "message": {
                            "id": "api.project.not_found",
                            "text": "Project not found",
                        }
                    }
                ),
                HTTPStatus.NOT_FOUND,
            )

        new_data_provider_accesses = []
        existing_data_provider_accesses = []
        respondent = None

        for data in data_providers:
            data_provider_name = DataProviderName(data.get("data_provider_name"))  # Converting the string to Enum.

            # Get the data provider
            data_provider: DataProviderModel = db.query(DataProviderModel).get(data_provider_name)
            if not data_provider:
                logger.warning("Data provider not found: %s", data_provider_name)
                return (
                    jsonify(
                        {
                            "message": {
                                "id": "api.data_provider.not_found",
                                "text": "Data provider not found",
                            }
                        }
                    ),
                    HTTPStatus.NOT_FOUND,
                )

            token = data.get("token")

            user_id = token.get("user_id")
            access_token = token.get("access_token")
            refresh_token = token.get("refresh_token")

            if not check_data_provider_access_tokens(project.id, data_provider_name, access_token, refresh_token):
                logger.error("Invalid token for data provider: %s", data_provider_name)
                return (
                    jsonify(
                        {
                            "message": {
                                "id": "api.data_provider.invalid_tokens",
                                "text": "Invalid token",
                            }
                        }
                    ),
                    HTTPStatus.BAD_REQUEST,
                )

            # Check if DataProviderAccess exists
            existing_data_provider_access: DataProviderAccess = (
                db.query(DataProviderAccess)
                .filter_by(
                    user_id=user_id,
                    project_id=project.id,
                    data_provider_name=data_provider_name,
                )
                .first()
            )

            if existing_data_provider_access:
                # Update the tokens with the new ones provided
                existing_data_provider_access.access_token = access_token
                existing_data_provider_access.refresh_token = refresh_token
                existing_data_provider_accesses.append(existing_data_provider_access)
            else:
                new_data_provider_access = DataProviderAccess(
                    data_provider_name=data_provider_name,
                    user_id=user_id,
                    project_id=project.id,
                    access_token=access_token,
                    refresh_token=refresh_token,
                )
                new_data_provider_accesses.append(new_data_provider_access)

        if new_data_provider_accesses and existing_data_provider_accesses:
            return (
                jsonify(
                    {
                        "message": {
                            "id": "api.respondent.resume_failed_different_data_providers",
                            "text": "Some data providers are different from the previous session",
                        }
                    }
                ),
                HTTPStatus.BAD_REQUEST,
            )
        if existing_data_provider_accesses:
            # All data providers already exist; update tokens and return the respondent
            try:
                db.commit()
                logger.info("Updated existing DataProviderAccess tokens.")
            except IntegrityError:
                db.rollback()
                logger.exception("Error updating tokens for existing DataProviderAccess entries.")
                return (
                    jsonify(
                        {
                            "message": {
                                "id": "api.respondent.resume_failed",
                                "text": "Failed to resume the respondent",
                            }
                        }
                    ),
                    HTTPStatus.INTERNAL_SERVER_ERROR,
                )

            respondent = existing_data_provider_accesses[0].respondent
            return (
                jsonify(
                    {
                        "message": {
                            "id": "api.respondent.resume_success",
                            "text": "Successfully resumed the respondent",
                        },
                        "entity": respondent.to_dict(),
                    }
                ),
                HTTPStatus.OK,
            )

        # Handle new data provider accesses
        respondent = Respondent(project_id=project.id)
        db.add(respondent)
        db.flush()  # This will populate the respondent_id which we can use below

        # Now we can use respondent.id for new_data_provider_accesses
        for data_provider_access in new_data_provider_accesses:
            data_provider_access.respondent_id = respondent.id

        db.add_all(new_data_provider_accesses)
        try:
            db.commit()
            logger.info("Successfully created a new respondent.")
            return (
                jsonify(
                    {
                        "message": {
                            "id": "api.respondent.created",
                            "text": "Successfully created a new respondent",
                        },
                        "entity": respondent.to_dict(),
                    }
                ),
                HTTPStatus.CREATED,
            )
        except IntegrityError:
            db.rollback()
            logger.exception("Error creating a new respondent:\n%s", traceback.format_exc())
            return (
                jsonify(
                    {
                        "message": {
                            "id": "api.data_provider.already_exists",
                            "text": "Data provider access already exists for this user, data provider and project.",
                        }
                    }
                ),
                HTTPStatus.BAD_REQUEST,
            )
