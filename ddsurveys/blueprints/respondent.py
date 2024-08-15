#!/usr/bin/env python
"""@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
@author: Stefan Teofanovic (stefan.teofanovic@heig-vd.ch)
"""
import traceback
from typing import Any

from flask import Blueprint, g, jsonify, request
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.attributes import flag_modified

from ..data_providers import DataProvider, OAuthDataProvider, TOAuthDataProviderClass
from ..get_logger import get_logger
from ..models import (
    DataConnection,
    DataProviderAccess,
    DataProviderName,
    DataProviderType,
    Distribution,
    Project,
    Respondent,
    get_db,
)
from ..models import DataProvider as DataProviderModel
from ..survey_platforms import SurveyPlatform

# from ._common import get_project_data_connection

logger = get_logger(__name__)


respondent = Blueprint("respondent", __name__)
"""location: /projects/<project_id>/respondent
All of the endpoints in blueprint file are public
"""


def get_project(db, short_id) -> Project:
    return db.query(Project).filter_by(short_id=short_id).first()


@respondent.route("/", methods=["GET"])
def get_public_project():
    """READ public project data.
    It also checks the readiness of the project by checking the connection status of all data providers and the survey platform.
    The survey must also be active.
    It does not give any detailed explanation of why the project is not ready.

    """
    with get_db() as db:

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
            logger.error(f"Project with id {project_short_id} not found.")
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

        response_dict = project.to_public_dict()
        response_status = 200

        all_data_connections_connected = (
            True  # Assume all are connected until proven otherwise
        )
        survey_platform_connected = False

        platform_class = SurveyPlatform.get_class_by_value(project.survey_platform_name)

        if not platform_class:
            logger.error(f"Unknown Survey Platform: {project.survey_platform_name}")
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
                    f"Survey on {project.survey_platform_name} {project.id} does not exist or there was an error "
                    f"fetching its info."
                )
                response_status = 400
                all_data_connections_connected = False

        project_dict = project.to_dict()

        variables_per_data_provider = DataProvider.get_used_variables(
            project_dict["variables"], project_dict["custom_variables"]
        )

        for data_connection in response_dict["data_connections"]:
            provider_type = data_connection["data_provider"]["data_provider_name"]
            provider_class = DataProvider.get_class_by_value(provider_type)

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

        has_oauth_data_providers = any(
            dc.data_provider.data_provider_type == DataProviderType.oauth
            for dc in project.data_connections
        )

        project_ready = (
            all_data_connections_connected
            and survey_platform_connected
            and survey_active
            and has_oauth_data_providers
        )
        response_dict["project_ready"] = project_ready
        response_dict["used_variables"] = variables_per_data_provider

        return jsonify(response_dict), response_status


@respondent.route("/data-providers", methods=["GET"])
def get_public_data_providers():
    """Provides the details necessary to connect a respondent to data providers that are linked to a project. (using OAuth2 Code Flow)

    This is a public endpoint, so no authentication is required. This endpoint should not provide any sensitive information.
    The respondent is
    """
    with get_db() as db:

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
def exchange_code_for_tokens():
    """Exchanges the code for an access token. (using OAuth2 Code Flow)

    This is a public endpoint, so no authentication is required.
    This endpoint should not provide any sensitive information.
    """
    with get_db() as db:

        data = request.get_json()

        data_provider_name = data.get("data_provider_name")

        project_short_id = g.get("project_short_id")

        # Get project and its associated data connections.
        project = get_project(db, project_short_id)

        if not project:
            logger.error(f"No project found for project_short_id: {project_short_id}")
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

        # Get the correct data provider from the project (we need its fields to create an instance of the data provider)
        project_data_connection = next(
            (
                dc
                for dc in project.data_connections
                if dc.data_provider.data_provider_name.value == data_provider_name
            ),
            None,
        )

        if not project_data_connection:
            logger.error(f"No data connection for data provider: {data_provider_name}")
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
                            "entity": response,
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
                            "id": response["message_id"],
                            "text": response.get("text", "Full scope not granted"),
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
                            "id": "api.data_provider.exchange_code_error",
                            "text": "Error exchanging code for tokens",
                        },
                    }
                ),
                500,
            )


@respondent.route("/data-provider/was-used", methods=["POST"])
def was_data_provider_used():
    with get_db() as db:
        project_short_id = g.get("project_short_id")

        # Get project and its associated data connections.
        project = get_project(db, project_short_id)

        if not project:
            logger.error(f"Project not found: {project_short_id}")
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
        else:
            return jsonify({"was_used": False}), 404


@respondent.route("/prepare-survey", methods=["POST"])
def prepare_survey():
    try:
        with get_db() as db:

            project_short_id = g.get("project_short_id")

            project = get_project(db, project_short_id)

            if not project:
                logger.error(f"Project not found: {project_short_id}")
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

            respondent = (
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
                logger.error(f"Unknown Survey Platform: {project.survey_platform_name}")
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

            status, _, survey_platform_info = (
                platform_instance.fetch_survey_platform_info()
            )

            if status != 200 and not survey_platform_info.get("active", False):
                logger.error(
                    f"Survey on {project.survey_platform_name} {project.id} does not exist or there was an error "
                    f"fetching its info."
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

            oauth_data_providers = respondent.data_provider_accesses

            # Create the data_to_upload dictionary outside the loop
            data_to_upload: dict[str, Any] = {}

            data_provider: DataProviderAccess
            for data_provider in oauth_data_providers:

                data_provider_name = data_provider.data_provider_name.value
                access_token = data_provider.access_token
                refresh_token = data_provider.refresh_token

                if not access_token:
                    logger.error(
                        f"Missing access token for data provider: {data_provider_name}"
                    )
                    return (
                        jsonify(
                            {
                                "message": {
                                    "id": "api.data_provider.missing_tokens",
                                    "text": "Missing data provider tokens",
                                }
                            }
                        ),
                        400,
                    )

                # Get the correct data provider from the project (we need its fields to create an instance of the data provider)
                project_data_connection = next(
                    (dc for dc in project.data_connections
                        if dc.data_provider.data_provider_name.value == data_provider_name),
                    None,
                )

                if not project_data_connection:
                    logger.error(f"Data provider not found: {data_provider_name}")
                    return (
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
                logger.debug(f"Data provider fields: {fields}")

                user_data_provider: OAuthDataProvider = DataProvider.get_class_by_value(
                    data_provider_name
                )(**fields)
                data_to_upload.update(
                    user_data_provider.calculate_variables(
                        project.variables, project.custom_variables
                    )
                )

                # revoke the access tokens
                try:
                    user_data_provider.revoke_token(data_provider.access_token)
                except Exception as e:
                    logger.error(f"Failed to revoke access token for data provider '{data_provider_name}': {e}", exc_info=True)
                    logger.debug(traceback.format_exc())

                # set the data provider access tokens to Null
                data_provider.access_token = None
                data_provider.refresh_token = None

                db.commit()

            frontend_data_providers = [
                dc
                for dc in project.data_connections
                if dc.data_provider.data_provider_type == DataProviderType.frontend
            ]
            for dc in frontend_data_providers:
                data_provider_name = dc.data_provider.data_provider_name.value

                provider_class = DataProvider.get_class_by_value(data_provider_name)
                provider_instance = provider_class()

                data_to_upload.update(
                    provider_instance.calculate_variables(
                        project_builtin_variables=project.variables,
                        data=frontend_variables,
                    )
                )
            # logger.debug(f"Project variables: {project.variables}")
            # logger.debug(f"Project custom variables: {project.custom_variables}")
            # logger.debug(f"Data to upload: {data_to_upload}")

            success_preparing_survey, unique_url = (
                platform_instance.handle_prepare_survey(
                    project_short_id=project_short_id,
                    survey_platform_fields=project.survey_platform_fields,
                    embedded_data=data_to_upload,
                )
            )

            if success_preparing_survey:
                distribution = None
                if unique_url:
                    # create the related distribution for the respondent
                    distribution = Distribution(url=unique_url)

                    respondent.distribution = distribution

                    db.add(respondent)

                flag_modified(project, "survey_platform_fields")
                db.commit()

                if status == 200:
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
                return (
                    jsonify(
                        {
                            "message": {
                                "id": "api.respondent.survey.failed_distribution_link",
                                "text": "Failed to create a unique distribution link",
                            }
                        }
                    ),
                    status,
                )

    except Exception as e:
        logger.error(f"Error preparing survey: {e}")
        logger.debug(f"Error traceback: {traceback.format_exc()}")
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
    with get_db() as db:
        # Get project and its associated data connections.
        project = db.query(Project).get(project_id)
        if not project:
            logger.debug(f"Project not found: {project_id}")
            return False

        data_connection = (
            db.query(DataConnection)
            .filter_by(project_id=project_id, data_provider_name=data_provider_name)
            .first()
        )

        if not data_connection:
            logger.debug(f"Data connection not found for: {data_provider_name}")
            return False

        data_provider_name = data_connection.data_provider.data_provider_name.value

        fields: dict = data_connection.fields

        fields.update({"access_token": access_token, "refresh_token": refresh_token})

        provider_class = DataProvider.get_class_by_value(data_provider_name)

        if not provider_class:
            logger.error(f"Data provider type not found: {data_provider_name}")
            return False

        user_data_provider: OAuthDataProvider = provider_class(**fields)

        return user_data_provider.test_connection_before_extraction()


@respondent.route("/connect", methods=["POST"])
def connect_respondent():
    """This function receives a JSON array of data providers and perform checks for each one.
    If all data providers exist, it will return the already existing respondent.
    If some exist and some do not, it will return a bad request.
    If none exist, it will create an associated data providers and a new respondent and return it.
    It will check that each data provider access token is valid before updating or creating.
    """
    project_short_id = g.get("project_short_id")
    data_providers = request.get_json().get("data_providers")

    with get_db() as db:
        # Get project and its associated data connections.
        project = get_project(db, project_short_id)
        if not project:
            logger.error(f"Project {project_short_id} not found")
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
        respondent = None

        for data in data_providers:
            data_provider_name = DataProviderName(
                data.get("data_provider_name")
            )  # Converting the string to Enum.

            # Get the data provider
            data_provider = db.query(DataProviderModel).get(data_provider_name)
            if not data_provider:
                logger.warning(f"Data provider not found: {data_provider_name}")
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
                logger.error(f"Invalid token for data provider: {data_provider_name}")
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
            existing_data_provider_access = (
                db.query(DataProviderAccess)
                .filter_by(
                    user_id=user_id,
                    project_id=project.id,
                    data_provider_name=data_provider_name,
                )
                .first()
            )

            if existing_data_provider_access:
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
        elif existing_data_provider_accesses:
            # all data providers already exists, so we can just return the respondent
            respondent: Respondent = (
                db.query(Respondent).filter_by(project_id=project.id).first()
            )  # There should only be one respondent per project
            logger.info("Found existing respondent.")
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
        else:
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
                logger.error(
                    f"Error creating a new respondent: {traceback.format_exc()}"
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
