"""This module provides blueprints for respondent backend requests.

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
@author: Stefan Teofanovic (stefan.teofanovic@heig-vd.ch).
"""
from __future__ import annotations

import traceback
from typing import TYPE_CHECKING, Any

from flask import Blueprint, Response, g, jsonify, request
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.attributes import flag_modified

from ddsurveys.blueprints import _responses
from ddsurveys.blueprints._common import abbreviate_variable_name
from ddsurveys.data_providers import DataProvider, OAuthDataProvider
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

if TYPE_CHECKING:
    from collections.abc import Generator

    from data_providers.bases import TFrontendDataProviderClass
    from flask.typing import ResponseReturnValue

    from ddsurveys.data_providers.bases import TDataProviderClass, TOAuthDataProviderClass
    from ddsurveys.typings.data_providers.variables import ProjectVariableDict
    from ddsurveys.typings.models import ProjectPublicDict

logger = get_logger(__name__)

respondent = Blueprint("respondent", __name__)
"""location: /projects/<project_id>/respondent
All of the endpoints in blueprint file are public
"""


def get_project(db, short_id) -> Project:
    return db.query(Project).filter_by(short_id=short_id).first()


def get_used_data_providers(
        project: Project,
        respondent: Respondent
) -> Generator[tuple[OAuthDataProvider, DataProviderAccess, None, None], None, tuple[None, None, Response, int]]:
    data_provider: DataProviderAccess
    for data_provider in respondent.data_provider_accesses:
        data_provider_name = data_provider.data_provider_name.value
        access_token = data_provider.access_token
        refresh_token = data_provider.refresh_token

        if not access_token:
            logger.error(
                    "Missing access token for data provider: %s", data_provider_name
            )
            return (
                None,
                None,
                jsonify(
                        {
                            "message": {
                                "id": "api.data_provider.missing_tokens",
                                "text": "Missing data provider tokens",
                            }
                        }),
                400
            )

        # Get the correct data provider from the project.
        # We need its fields to create an instance of the data provider.
        project_data_connection = next(
                (dc for dc in project.data_connections
                 if dc.data_provider.data_provider_name.value == data_provider_name),
                None,
        )

        if not project_data_connection:
            logger.error("Data provider not found: %s", data_provider_name)
            return (
                None,
                None,
                jsonify({
                    "message": {
                        "id": "api.data_provider.not_found",
                        "text": "Data provider not found",
                    }
                }),
                404,
            )

        fields = project_data_connection.fields

        fields.update(
                {"access_token": access_token, "refresh_token": refresh_token}
        )

        user_data_provider: OAuthDataProvider = DataProvider.get_class_by_value(
                data_provider_name
        )(**fields)

        yield user_data_provider, data_provider, None, None


@respondent.route("/", methods=["GET"])
def get_public_project() -> _responses.MessageDict:
    """Reads public project data and checks the readiness of the project.

    This function checks the connection status of all data providers and the survey
    platform.
    The survey must also be active.
    It does not provide any detailed explanation of why the project is not ready.

    Returns:
        ResponseReturnValue:
            A JSON response containing the public project data and readiness status.
            Possible status codes are:
            - 200: Successfully retrieved project data.
            - 400: Bad request, e.g., unknown survey platform.
            - 404: Project not found.
    """
    with DBManager.get_db() as db:

        project_short_id = g.get("project_short_id")
        project: Project = (
            db.query(Project)
            .options(
                    joinedload(Project.data_connections).joinedload(
                            DataConnection.data_provider
                    ),
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
                404,
            )

        response_dict: ProjectPublicDict = project.to_public_dict()
        response_status = 200

        all_data_connections_connected = (
            True  # Assume all are connected until proven otherwise
        )
        survey_platform_connected = False

        platform_class = SurveyPlatform.get_class_by_value(project.survey_platform_name)

        if not platform_class:
            logger.error("Unknown Survey Platform: %s", project.survey_platform_name)
            response_status = 400
            all_data_connections_connected = False
        else:
            survey_platform = platform_class(**project.survey_platform_fields)

            # Fetch survey platform info using the platform method
            status, _, survey_platform_info = (
                survey_platform.fetch_survey_platform_info()
            )

            if status == 200:
                survey_platform_connected = survey_platform_info["connected"]
                survey_active = survey_platform_info["active"]
            else:
                logger.error(
                        "Survey on %s %s does not exist or there was an error fetching its info.",
                        project.survey_platform_name, project.id
                )
                response_status = 400
                all_data_connections_connected = False

        project_dict = project.to_dict()

        variables_per_data_provider: list[ProjectVariableDict] = DataProvider.get_used_variables(
                project_dict["variables"], project_dict["custom_variables"]
        )

        for data_connection in response_dict["data_connections"]:
            provider_type = data_connection["data_provider"]["data_provider_name"]
            provider_class: TDataProviderClass = DataProvider.get_class_by_value(provider_type)

            project_data_connections = project_dict["data_connections"]
            project_data_connection = next(
                    (
                        dc
                        for dc in project_data_connections
                        if dc["data_provider"]["data_provider_name"] == provider_type
                    ),
                    None,
            )

            if not project_data_connection:
                all_data_connections_connected = False
                continue

            fields = project_data_connection["fields"]
            provider_instance = provider_class(**fields)
            if not provider_instance.test_connection():
                all_data_connections_connected = False

        has_oauth_data_providers: bool = any(
                dc.data_provider.data_provider_type == DataProviderType.oauth
                for dc in project.data_connections
        )

        project_ready: bool = (
                all_data_connections_connected
                and survey_platform_connected
                and survey_active
                and has_oauth_data_providers
        )

        response_dict: _responses.Projects.GetPublicProjectDict
        response_dict["project_ready"] = project_ready
        response_dict["used_variables"] = variables_per_data_provider

        return jsonify(response_dict), response_status


@respondent.route("/data-providers", methods=["GET"])
def get_public_data_providers() -> ResponseReturnValue:
    """Provides the data providers information linked to a project.

    The data provider information enables a respondent to data providers linked to a
    project using the OAuth2 Code Flow.

    This is a public endpoint, so no authentication is required.
    This endpoint should not provide any sensitive information.

    Returns:
        ResponseReturnValue: A JSON response containing the details of data providers
            linked to the project.
            Possible status codes are:
            - 200: Successfully retrieved data providers.
            - 404: Project not found.
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
                404,
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

        return jsonify(data_providers), 200


@respondent.route("/exchange-code", methods=["POST"])
def exchange_code_for_tokens() -> ResponseReturnValue:
    """Exchanges the code for an access token. (using OAuth2 Code Flow).

    This is a public endpoint, so no authentication is required.
    This endpoint should not provide any sensitive information.
    """
    with DBManager.get_db() as db:

        data = request.get_json()

        data_provider_name = data.get("data_provider_name")

        project_short_id = g.get("project_short_id")

        # Get project and its associated data connections.
        project = get_project(db, project_short_id)

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
                404,
            )

        # Get the correct data provider from the project
        # (we need its fields to create an instance of the data provider)
        project_data_connection = next(
                (
                    dc
                    for dc in project.data_connections
                    if dc.data_provider.data_provider_name.value == data_provider_name
                ),
                None,
        )

        if not project_data_connection:
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
                404,
            )

        try:
            # Create an instance of the data provider
            provider_class = DataProvider.get_class_by_value(
                    project_data_connection.data_provider.data_provider_name.value
            )
            provider_instance: OAuthDataProvider = provider_class(
                    **project_data_connection.fields
            )

            # Exchange the code for an access token
            provider_instance.get_required_scopes(
                    project.variables, project.custom_variables
            )
            logger.debug(data)
            response = provider_instance.request_token(data)

            if response["success"]:
                logger.info(
                        "Successfully exchanged code for tokens for: %s", data_provider_name
                )
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
                    200,
                )
            logger.error(
                    "Error exchanging code for tokens for: %s", data_provider_name
            )
            return (
                jsonify(
                        {
                            "message": {
                                "id": response.get("message_id",
                                                   "api.data_provider.exchange_code_error.unexpected_error"),
                                "text": response.get("text", "An unknown error occurred"),
                                "required_scopes": response.get("required_scopes", []),
                                "accepted_scopes": response.get("accepted_scopes", []),
                                "data_provider_name": provider_instance.name,
                            },
                        }
                ),
                400,
            )
        except Exception:
            logger.exception("Error exchanging code for tokens for: %s\n", data_provider_name)
            logger.debug(traceback.format_exc())
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
                500,
            )


@respondent.route("/data-provider/was-used", methods=["POST"])
def was_data_provider_used() -> ResponseReturnValue:
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
                404,
            )

        data = request.get_json()

        data_provider_name = DataProviderName(
                data.get("data_provider_name")
        )  # Converting the string to Enum.

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
            return jsonify({"was_used": True}), 200
        return jsonify({"was_used": False}), 200


@respondent.route("/prepare-survey", methods=["POST"])
def prepare_survey() -> ResponseReturnValue:
    """Prepares a survey for a respondent by creating a unique distribution link and handling data provider tokens.

    This function performs the following steps:
    1. Retrieves the project and respondent information from the database.
    2. Checks if the respondent already has a distribution link.
    3. Verifies if the survey is active on the specified survey platform.
    4. Collects and processes data from various data providers.
    5. Creates a unique distribution link for the respondent.

    Returns:
        ResponseReturnValue: A JSON response containing the distribution link or an error message.
            Possible status codes are:
            - 200: Successfully created a unique distribution link.
            - 400: Missing respondent ID or unsupported survey platform.
            - 404: Project or respondent not found, or survey not active.
            - 500: Error preparing the survey.
    """
    try:
        with DBManager.get_db() as db:

            project_short_id = g.get("project_short_id")

            project = get_project(db, project_short_id)

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
                    404,
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
                    400,
                )

            respondent: Respondent = (
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
                    404,
                )

            # check if the respondent already has a distribution
            if respondent.distribution:
                logger.info("Respondent already has a distribution url.")

                for dp_instance, dp_access, response, error_status in get_used_data_providers(project,
                                                                                              respondent):
                    if response is not None and error_status is not None:
                        return response, error_status

                    # revoke the access tokens
                    try:
                        dp_instance.revoke_token(dp_access.access_token)
                        logger.info("Revoked access token for data provider '%s'\n", dp_instance.name)
                    except Exception:
                        logger.exception(
                                "Failed to revoke access token for data provider '%s'\n", dp_instance.name
                        )
                        logger.debug(traceback.format_exc())

                    # set the data provider access tokens to Null
                    dp_access.access_token = None
                    dp_access.refresh_token = None

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
                    200,
                )

            # check if the survey is active
            # Get the platform class
            platform_class = SurveyPlatform.get_class_by_value(
                    project.survey_platform_name
            )

            if not platform_class:
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
                    400,
                )

            # Create an instance of the platform
            platform_instance = platform_class(**project.survey_platform_fields)

            survey_platform_status, _, survey_platform_info = (
                platform_instance.fetch_survey_platform_info()
            )

            if survey_platform_status != 200 and not survey_platform_info.get("active", False):
                logger.error(
                        "Survey on %s %s does not exist or there was an error fetching its info.",
                        project.survey_platform_name, project.id
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
                    404,
                )

            # Create the data_to_upload dictionary outside the loop
            data_to_upload: dict[str, Any] = {}

            for dp_instance, dp_access, response, error_status in get_used_data_providers(project, respondent):
                if response is not None and error_status is not None:
                    return response, error_status

                dp_instance: OAuthDataProvider
                dp_access: DataProviderAccess

                data_to_upload.update(
                        dp_instance.calculate_variables(
                                project.variables, project.custom_variables
                        )
                )

                # revoke the access tokens
                try:
                    dp_instance.revoke_token(dp_access.access_token)
                except Exception:
                    logger.exception("Failed to revoke access token for data provider '%s'\n", dp_instance.name)
                    logger.debug(traceback.format_exc())

                # set the data provider access tokens to Null
                dp_access.access_token = None
                dp_access.refresh_token = None

                db.commit()

            frontend_data_providers = [
                dc
                for dc in project.data_connections
                if dc.data_provider.data_provider_type == DataProviderType.frontend
            ]
            for dc in frontend_data_providers:
                data_provider_name = dc.data_provider.data_provider_name.value

                provider_class: TFrontendDataProviderClass = DataProvider.get_class_by_value(data_provider_name)
                provider_instance = provider_class()

                data_to_upload.update(
                        provider_instance.calculate_variables(
                                project_builtin_variables=project.variables,
                                data=frontend_variables,
                        )
                )

            data_to_upload = {
                abbreviate_variable_name(variable_name, "dp", "full"): value
                for variable_name, value in data_to_upload.items()
            }

            success_preparing_survey, unique_url = (
                platform_instance.handle_prepare_survey(
                        project_short_id=project_short_id,
                        survey_platform_fields=project.survey_platform_fields,
                        embedded_data=data_to_upload,
                )
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

                if survey_platform_status == 200:
                    return (
                        jsonify(
                                {
                                    "message": {
                                        "id": "api.respondent.survey.distribution_link_created",
                                        "text": "Successfully created a unique distribution link",
                                    },
                                    "entity": distribution.to_dict(),
                                }
                        ),
                        200,
                    )
            else:
                logger.error("Failed to prepare survey.")
                if survey_platform_status == 200:
                    survey_platform_status = 500
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
        logger.exception("Error preparing survey.\n")
        logger.debug("Error traceback: %s", traceback.format_exc())
        return (
            jsonify(
                    {
                        "message": {
                            "id": "api.respondent.survey.error",
                            "text": "Error preparing survey",
                        }
                    }
            ),
            500,
        )


def check_data_provider_access_tokens(
        project_id, data_provider_name, access_token, refresh_token
):
    with DBManager.get_db() as db:
        # Get project and its associated data connections.
        project = db.query(Project).get(project_id)
        if not project:
            logger.error("Project not found: %s", project_id)
            return False

        data_connection = (
            db.query(DataConnection)
            .filter_by(project_id=project_id, data_provider_name=data_provider_name)
            .first()
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
def connect_respondent() -> ResponseReturnValue:
    """This function receives a JSON array of data providers and perform checks for each one.

    If all data providers exist, it will return the already existing respondent.
    If some exist and some do not, it will return a bad request.
    If none exist, it will create an associated data providers and a new respondent and return it.
    It will check that each data provider access token is valid before updating or creating.
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
                404,
            )

        new_data_provider_accesses = []
        existing_data_provider_accesses = []

        for data in data_providers:
            data_provider_name = DataProviderName(
                    data.get("data_provider_name")
            )  # Converting the string to Enum.

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
                    404,
                )

            token = data.get("token")

            user_id = token.get("user_id")
            access_token = token.get("access_token")
            refresh_token = token.get("refresh_token")

            if not check_data_provider_access_tokens(
                    project.id, data_provider_name, access_token, refresh_token
            ):
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
                    400,
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
                400,
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
                    500,
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
                200,
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
                201,
            )
        except IntegrityError:
            db.rollback()
            logger.exception(
                    "Error creating a new respondent:\n%s", traceback.format_exc()
            )
            return (
                jsonify(
                        {
                            "message": {
                                "id": "api.data_provider.already_exists",
                                "text": "Data provider access already exists for this user, data provider and project.",
                            }
                        }
                ),
                400,
            )
