"""This module provides blueprints for managing projects.

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
@author: Stefan Teofanovic (stefan.teofanovic@heig-vd.ch).
"""

from __future__ import annotations

import datetime
from http import HTTPStatus
from io import BytesIO
from typing import TYPE_CHECKING, Any, TypedDict, cast

from flask import Blueprint, g, jsonify, request, send_file
from flask import Response as FlaskResponse
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.attributes import flag_modified

from ddsurveys.api_responses import APIResponses, APIResponseValue
from ddsurveys.blueprints._common import abbreviate_variable_name, get_researcher, insert_exists_variables
from ddsurveys.blueprints.custom_variables import custom_variables
from ddsurveys.blueprints.data_providers import data_providers
from ddsurveys.blueprints.respondent import respondent
from ddsurveys.data_providers.variables import CustomVariable
from ddsurveys.get_logger import get_logger
from ddsurveys.models import (
    Collaboration,
    DataConnection,
    DBManager,
    Project,
    Researcher,
    Respondent,
    SurveyPlatformFieldsDict,
    SurveyStatus,
)
from ddsurveys.survey_platforms.bases import SurveyPlatform, TSurveyPlatform

if TYPE_CHECKING:
    from flask import Response
    from flask.typing import ResponseReturnValue

    from ddsurveys.survey_platforms.bases import SurveyPlatformInfoDict, TSurveyPlatformClass
    from ddsurveys.typings.data_providers.variables import BuiltinVariableDict, CustomVariableUploadDict

logger = get_logger(__name__)


class ProjectCreationDict(TypedDict):
    name: str
    survey_platform_name: str
    fields: SurveyPlatformFieldsDict
    use_existing_survey: bool


class JWTUserDict(TypedDict):
    id: int
    firstname: str
    lastname: str
    email: str


projects = Blueprint("projects", __name__)
projects.register_blueprint(blueprint=data_providers, url_prefix="/<string:project_id>/data-providers")
projects.register_blueprint(blueprint=respondent, url_prefix="/<string:project_short_id>/respondent")
projects.register_blueprint(blueprint=custom_variables, url_prefix="/<string:project_id>/custom-variables")


@projects.url_value_preprocessor
def get_project_id(endpoint: str, values: dict[str, Any] | None) -> None:
    if values is not None and "project_id" in values:
        g.project_id = values.pop("project_id")


@projects.url_value_preprocessor
def get_project_short_id(endpoint: str, values: dict[str, Any] | None) -> None:
    if values is not None and "project_short_id" in values:
        g.project_short_id = values.pop("project_short_id")


# List
@projects.route("/", methods=["GET"])
@jwt_required()
def list_projects() -> ResponseReturnValue | tuple[Researcher | Response, HTTPStatus]:
    logger.debug("Listing projects")

    with DBManager.get_db() as db:
        user = get_jwt_identity()

        researcher: ResponseReturnValue | Researcher
        researcher, status = get_researcher(db, user)
        if status is not None:
            # Case where the user could not be found
            return researcher, status

        researcher = cast(Researcher, researcher)

        # get the projects
        projects: list[Project] = (
            db.query(Project).join(Collaboration).filter(Collaboration.researcher_id == researcher.id).all()
        )

        return jsonify([project.to_dict() for project in projects]), HTTPStatus.OK


@projects.route("/", methods=["POST"])
@jwt_required()
def create_project() -> ResponseReturnValue:
    logger.debug("Creating a new project")

    with DBManager.get_db() as db:
        data: ProjectCreationDict = request.get_json()

        user: JWTUserDict = get_jwt_identity()
        logger.info("Creating project for user %s", user)

        use_existing_survey: bool = data.get("use_existing_survey")
        project_name: str | None = data.get("name")
        survey_platform_name: str = data.get("survey_platform_name")

        if not use_existing_survey and (project_name is None or project_name == ""):
            logger.error("No project name specified")
            return (
                jsonify({
                    "message": {
                        "id": "api.projects.name_is_required",
                        "text": "Project name is required",
                    }
                }),
                HTTPStatus.BAD_REQUEST,
            )

        fields = {field.get("name"): field.get("value", None) for field in data.get("fields")}

        # survey_id becomes required if use_existing_survey is True
        override_required = ["survey_id"] if use_existing_survey else []

        platform_class: TSurveyPlatformClass | None = SurveyPlatform.get_class_by_value(survey_platform_name)

        if not platform_class:
            logger.error("Unknown Survey Platform: %s", survey_platform_name)
            return (
                jsonify({
                    "message": {
                        "id": "api.survey.platform_not_supported",
                        "text": "Unknown Survey Platform",
                    }
                }),
                HTTPStatus.BAD_REQUEST,
            )

        # Validate fields using check_inputs method
        are_fields_valid, missing_field_key = platform_class.check_input_fields(
            fields=fields,
            override_required_fields=override_required,
            class_=SurveyPlatform,
        )

        if not are_fields_valid:
            logger.error("Missing required field: %s", missing_field_key)
            return (
                jsonify({
                    "message": {
                        "id": f"{missing_field_key}.missing",
                        # Append .missing to the full name key for the error id
                        "text": f"Field '{missing_field_key}' is required",
                    }
                }),
                HTTPStatus.BAD_REQUEST,
            )

        # get the researcher
        researcher, status = get_researcher(db, user)
        if status is not None:
            researcher = cast(FlaskResponse, researcher)
            # Case where the user could not be found
            return researcher, status
        researcher = cast(Researcher, researcher)

        # create an instance of the survey platform
        survey_platform: TSurveyPlatform = cast(TSurveyPlatform, platform_class(**fields))

        # Handle the project creation
        status, message_id, text_message, project_name, survey_platform_fields = (
            survey_platform.handle_project_creation(project_name, use_existing_survey=use_existing_survey)
        )

        # Check if an error occurred
        if status != HTTPStatus.OK:
            logger.error("Error during project creation: %s", text_message)
            return (
                jsonify({"message": {"id": message_id, "text": text_message}}),
                status,
            )

        new_project: Project = Project(
            name=project_name,
            survey_platform_name=survey_platform_name,
            survey_platform_fields=survey_platform_fields,
        )

        new_collaboration = Collaboration(researcher_id=researcher.id, project=new_project)

        db.add(new_collaboration)
        db.add(new_project)

        try:
            db.commit()
            return (
                jsonify({
                    "message": {
                        "id": "api.projects.project_created_successfully",
                        "text": "Project created successfully",
                    },
                    "entity": new_project.to_dict(),
                }),
                HTTPStatus.CREATED,
            )
        except SQLAlchemyError:
            logger.exception("An error occurred while creating the project. Rolling back changes.")
            db.rollback()
            return (
                jsonify({
                    "message": {
                        "id": "api.projects.failed_to_create_project",
                        "text": "Failed to create project",
                    }
                }),
                HTTPStatus.BAD_REQUEST,
            )


# Read
@projects.route("/<string:id_>", methods=["GET"])
@jwt_required()
def get_project(id_: str) -> ResponseReturnValue:
    """Retrieves the details of a specific project based on its unique identifier.

    Args:
        id_: The unique identifier of the project to be retrieved.

    Returns:
        Response: A JSON response containing the project details if found.
        - HTTPStatus.OK: If the project is successfully retrieved.
        - HTTPStatus.UNAUTHORIZED: If the user is unauthorized.
        - HTTPStatus.NOT_FOUND: If the project is not found.
    """
    logger.debug("Getting project with id: %s", id_)

    with DBManager.get_db() as db:
        user = get_jwt_identity()

        # get the researcher
        researcher: Researcher | None = db.query(Researcher).filter_by(email=user["email"]).first()
        if not researcher:
            # return (
            #     jsonify({"message": {"id": "api.unauthorized", "text": "Unauthorized"}}),
            #     HTTPStatus.UNAUTHORIZED,
            # )
            return APIResponses.AUTHORIZATION.UNAUTHORIZED.response

        # get the project by id if it is in the collaborations
        project: Project | None = (
            db.query(Project)
            .options(
                joinedload(Project.data_connections).joinedload(DataConnection.data_provider),
            )
            .join(Collaboration)
            .filter(Collaboration.researcher_id == researcher.id, Project.id == id_)
            .first()
        )

        if not project:
            return (
                jsonify({
                    "message": {
                        "id": "api.projects.not_found",
                        "text": "Project not found",
                    }
                }),
                HTTPStatus.NOT_FOUND,
            )

        return jsonify(project.to_dict()), HTTPStatus.OK


# Update
@projects.route("/<string:id_>", methods=["PUT"])
@jwt_required()
def update_project(id_: str) -> ResponseReturnValue:
    """Updates the details of an existing project.

    Args:
        id_: The unique identifier of the project to be updated.

    Returns:
        Response: A JSON response indicating the result of the update operation.
        - HTTPStatus.OK: If the project is successfully updated.
        - HTTPStatus.UNAUTHORIZED: If the user is unauthorized.
        - HTTPStatus.NOT_FOUND: If the project is not found.
    """
    logger.debug("Updating project with id: %s", id_)

    with DBManager.get_db() as db:
        data = request.get_json()
        user = get_jwt_identity()
        researcher: Researcher | None = db.query(Researcher).filter_by(email=user["email"]).first()
        if not researcher:
            # return (
            #     jsonify({"message": {"id": "api.unauthorized", "text": "Unauthorized"}}),
            #     HTTPStatus.UNAUTHORIZED,
            # )
            return APIResponses.AUTHORIZATION.UNAUTHORIZED.response

        # get the project
        project: Project | None = (
            db.query(Project)
            .join(Collaboration)
            .filter(Collaboration.researcher_id == researcher.id, Project.id == id_)
            .first()
        )

        if project:
            for key, value in data.items():
                # is it the JSON field?
                current_value = getattr(project, key, None)
                if current_value is None:
                    logger.warning("Project does not have attribute %s", key)
                    continue
                if isinstance(current_value, dict):
                    for k, v in value.items():
                        current_value[k] = v

                    flag_modified(project, key)
                else:
                    setattr(project, key, value)
            db.commit()
            return (
                jsonify({
                    "message": {
                        "id": "api.projects.updated_successfully",
                        "text": "Project updated successfully",
                    }
                }),
                HTTPStatus.OK,
            )

        return (
            jsonify({
                "message": {
                    "id": "api.projects.project_not_found",
                    "text": "Project not found",
                }
            }),
            HTTPStatus.NOT_FOUND,
        )


# Delete
@projects.route("/<string:id_>", methods=["DELETE"])
@jwt_required()
def delete_project(id_: str) -> ResponseReturnValue:
    """Deletes a project and its associated collaboration.

    Args:
        id_: The unique identifier of the project to be deleted.

    Returns:
        Response: A JSON response indicating the result of the deletion operation.
        - HTTPStatus.OK: If the project and collaboration are successfully deleted.
        - HTTPStatus.UNAUTHORIZED: If the user is unauthorized.
        - HTTPStatus.NOT_FOUND: If the project or collaboration is not found.
    """
    logger.debug("Deleting project with id: %s", id_)

    with DBManager.get_db() as db:
        # Get the current researcher's identity
        user = get_jwt_identity()
        researcher: Researcher | None = db.query(Researcher).filter_by(email=user["email"]).first()
        if not researcher:
            # return (
            #     jsonify({"message": {"id": "api.unauthorized", "text": "Unauthorized"}}),
            #     HTTPStatus.UNAUTHORIZED,
            # )
            return APIResponses.AUTHORIZATION.UNAUTHORIZED.response

        # Get the project and collaboration
        project: Project | None = db.query(Project).get(id_)
        collaboration = db.query(Collaboration).filter_by(project_id=id_, researcher_id=researcher.id).first()

        if project and collaboration:
            db.delete(collaboration)
            db.delete(project)
            db.commit()
            return (
                jsonify({
                    "message": {
                        "id": "api.projects.project_and_collaboration_deleted_successfully",
                        "text": "Project and collaboration deleted successfully",
                    }
                }),
                HTTPStatus.OK,
            )

        return (
            jsonify({
                "message": {
                    "id": "api.projects.project_and_collaboration_not_found",
                    "text": "Project and collaboration not found",
                }
            }),
            HTTPStatus.NOT_FOUND,
        )


# DELETE all respondents for a project
@projects.route("/<string:id_>/respondents", methods=["DELETE"])
@jwt_required()
def delete_respondents(id_: str) -> ResponseReturnValue:
    """Deletes all respondents associated with a specific project.

    Args:
        id_: The unique identifier of the project.

    Returns:
        Response: A JSON response indicating the result of the deletion operation.
        - HTTPStatus.OK: If all respondents are successfully deleted.
        - HTTPStatus.UNAUTHORIZED: If the user is unauthorized.
        - HTTPStatus.NOT_FOUND: If the project is not found.
    """
    logger.debug("Received delete respondents request for project with id: '%s'", id_)

    with DBManager.get_db() as db:
        user = get_jwt_identity()
        researcher: Researcher | None = db.query(Researcher).filter_by(email=user["email"]).first()

        if not researcher:
            # return (
            #     jsonify({"message": {"id": "api.unauthorized", "text": "Unauthorized"}}),
            #     HTTPStatus.UNAUTHORIZED,
            # )
            return APIResponses.AUTHORIZATION.UNAUTHORIZED.response

        project: Project | None = (
            db.query(Project)
            .join(Collaboration)
            .filter(Collaboration.researcher_id == researcher.id, Project.id == id_)
            .first()
        )

        if not project:
            logger.warning("Project not found with id: %s", id_)
            return (
                jsonify({
                    "message": {
                        "id": "api.projects.not_found",
                        "text": "Project not found",
                    }
                }),
                HTTPStatus.NOT_FOUND,
            )

        respondents = (
            db.query(Respondent)
            .filter(
                Respondent.project_id == id_,
            )
            .all()
        )

        logger.info("Deleting %s respondents for project with id: %s", len(respondents), id_)

        for respondent in respondents:
            db.delete(respondent)

        db.commit()

        return (
            jsonify({
                "message": {
                    "id": "api.projects.respondents.deleted_successfully",
                    "text": "All project respondents deleted",
                }
            }),
            HTTPStatus.OK,
        )


def get_survey_platform_connection(project: Project) -> tuple[HTTPStatus, str, SurveyPlatformInfoDict]:
    survey_platform_info: SurveyPlatformInfoDict = SurveyPlatform.get_default_survey_status_dict()
    survey_platform_info["survey_platform_name"] = project.survey_platform_name

    platform_class: TSurveyPlatformClass | None = SurveyPlatform.get_class_by_value(project.survey_platform_name)

    if platform_class is None:
        survey_platform_info["id"] = "api.survey.platform_not_supported"
        return HTTPStatus.BAD_REQUEST, "api.survey.platform_not_supported", survey_platform_info

    try:
        platform: TSurveyPlatform = cast(TSurveyPlatform, platform_class(**project.survey_platform_fields))
        return platform.fetch_survey_platform_info()
    except Exception:
        logger.exception("Failed to check connection with survey platform")
        return HTTPStatus.BAD_REQUEST, "api.survey.failed_to_check_connection", survey_platform_info


@projects.route("/<string:id_>/survey_platform/check_connection", methods=["GET"])
@jwt_required()
def check_survey_platform_connection(id_: str) -> ResponseReturnValue:
    """Checks the connection status of the survey platform for a given project.

    Args:
        id_: The unique identifier of the project.

    Returns:
        Response: A JSON response indicating the result of the connection check.
        - HTTPStatus.OK: If the connection check is successful.
        - HTTPStatus.BAD_REQUEST: If the survey platform is not supported or there is a
            failure in checking the connection.
        - HTTPStatus.UNAUTHORIZED: If the user is unauthorized.
        - HTTPStatus.NOT_FOUND: If the project is not found.
    """
    logger.debug("Checking survey platform connection for project with id: %s", id_)

    with DBManager.get_db() as db:
        user = get_jwt_identity()
        researcher: Researcher | None = db.query(Researcher).filter_by(email=user["email"]).first()
        if researcher is None:
            # return (
            #     jsonify({"message": {"id": "api.unauthorized", "text": "Unauthorized"}}),
            #     HTTPStatus.UNAUTHORIZED,
            # )
            return APIResponses.AUTHORIZATION.UNAUTHORIZED.response

        project: Project | None = (
            db.query(Project)
            .join(Collaboration)
            .filter(Collaboration.researcher_id == researcher.id, Project.id == id_)
            .first()
        )

        if project is None:
            return (
                jsonify({
                    "message": {
                        "id": "api.projects.project_not_found",
                        "text": "Project not found",
                    }
                }),
                HTTPStatus.NOT_FOUND,
            )
        status: int
        message_id: str
        survey_platform_info: SurveyPlatformInfoDict
        status, message_id, survey_platform_info = get_survey_platform_connection(project)

        if status != HTTPStatus.OK:
            return (
                jsonify({
                    "message": {
                        "id": message_id,
                        "text": "Failed to check survey platform connection",
                    }
                }),
                status,
            )

        if project.survey_platform_fields is None:
            project.survey_platform_fields = cast(SurveyPlatformFieldsDict, {})

        # Set the survey_status
        survey_status: SurveyStatus = survey_platform_info.get("survey_status", SurveyStatus.Unknown)
        project.survey_platform_fields["survey_status"] = survey_status
        project.survey_status = survey_status

        # Update the survey_name in project.survey_platform_fields
        project.survey_platform_fields["survey_name"] = survey_platform_info.get("survey_name", "")

        # Commit the changes to the database
        flag_modified(project, "survey_platform_fields")
        try:
            db.commit()
        except Exception:
            logger.exception("Failed to update project with id: %s", id_)
            return jsonify({
                "message": {
                    "id": "api.ddsurveys.database.commit_error",
                    "text": "Failed to commit changes to the database",
                }
            }), HTTPStatus.INTERNAL_SERVER_ERROR
        else:
            survey_platform_info["id"] = message_id
            survey_platform_info["survey_status"] = survey_status
            logger.debug("Survey platform info: %s", survey_platform_info)
            return jsonify(survey_platform_info), status


@projects.route("/<string:id_>/sync_variables", methods=["POST"])
@jwt_required()
def sync_variables(id_: str) -> ResponseReturnValue:
    """Synchronizes the variables for a specific project with the survey platform.

    Args:
        id_ : The unique identifier of the project.

    Returns:
        Response: A JSON response indicating the result of the synchronization
            operation.
        - HTTPStatus.OK: If the variables are successfully synchronized.
        - HTTPStatus.BAD_REQUEST: If the survey platform is not supported.
        - HTTPStatus.UNAUTHORIZED: If the user is unauthorized.
        - HTTPStatus.NOT_FOUND: If the project is not found.
    """
    logger.debug("Syncing variables for project with id: %s", id_)

    with DBManager.get_db() as db:
        user = get_jwt_identity()
        researcher: Researcher | None = db.query(Researcher).filter_by(email=user["email"]).first()
        if not researcher:
            return APIResponses.AUTHORIZATION.UNAUTHORIZED.response

        project: Project | None = (
            db.query(Project)
            .join(Collaboration)
            .filter(Collaboration.researcher_id == researcher.id, Project.id == id_)
            .first()
        )

        if project is None:
            return (
                jsonify({
                    "message": {
                        "id": "api.projects.project_not_found",
                        "text": "Project not found",
                    }
                }),
                HTTPStatus.NOT_FOUND,
            )

        enabled_variables: list[BuiltinVariableDict | CustomVariableUploadDict] = []
        if project.variables:
            enabled_variables = [variable for variable in project.variables if variable["enabled"]]
        if project.custom_variables:
            enabled_custom_variables = CustomVariable.custom_variables_as_list([
                variable for variable in project.custom_variables if variable.get("enabled", False)
            ])
            logger.info("Stored custom variables: %s", project.custom_variables)
            logger.info("Upload custom variables: %s", enabled_custom_variables)
            enabled_variables.extend(enabled_custom_variables)

        platform_class: TSurveyPlatformClass | None = SurveyPlatform.get_class_by_value(project.survey_platform_name)

        if not platform_class:
            logger.error("Unknown Survey Platform: %s", project.survey_platform_name)
            return (
                jsonify({
                    "message": {
                        "id": "api.survey.platform_not_supported",
                        "text": "Survey platform not supported",
                    }
                }),
                HTTPStatus.BAD_REQUEST,
            )

        survey_platform: TSurveyPlatform = platform_class(**project.survey_platform_fields)

        enabled_variables = insert_exists_variables(enabled_variables)
        for variable in enabled_variables:
            variable["qualified_name"] = abbreviate_variable_name(
                variable_name=variable["qualified_name"],
                first_apply="dp",
                strategy="full",
                max_length=survey_platform.max_variable_name_length,
            )

        status, message_id, text_message = survey_platform.handle_variable_sync(enabled_variables)

        # Check if an error occurred
        if status != HTTPStatus.OK:
            logger.error("Error during variable syncing: %s", text_message)
            return (
                jsonify({"message": {"id": message_id, "text": text_message}}),
                status,
            )

        # If no error, update the last synced timestamp and commit the changes
        project.last_synced = datetime.datetime.now()
        db.commit()
        return jsonify({"message": {"id": message_id, "text": text_message}}), status


@projects.route("/<string:id_>/export_survey_responses", methods=["POST"])
@jwt_required()
def export_survey_responses(id_: str) -> ResponseReturnValue:
    """Exports survey responses for a specific project.

    Args:
        id_ (str): The unique identifier of the project.

    Returns:
        Response: A JSON response indicating the result of the export operation.
        - HTTPStatus.OK: If the survey responses are successfully exported and the file is sent.
        - HTTPStatus.BAD_REQUEST: If the survey platform is not supported.
        - HTTPStatus.UNAUTHORIZED: If the user is unauthorized.
        - HTTPStatus.NOT_FOUND: If the project is not found.
        - HTTPStatus.INTERNAL_SERVER_ERROR: If there is an error during the export process.
    """
    logger.debug("Exporting survey responses for project with id: %s", id_)

    with DBManager.get_db() as db:
        user = get_jwt_identity()
        researcher: Researcher | None = db.query(Researcher).filter_by(email=user["email"]).first()
        if not researcher:
            # return (
            #     jsonify({"message": {"id": "api.unauthorized", "text": "Unauthorized"}}),
            #     HTTPStatus.UNAUTHORIZED,
            # )
            return APIResponses.AUTHORIZATION.UNAUTHORIZED.response

        project: Project | None = (
            db.query(Project)
            .join(Collaboration)
            .filter(Collaboration.researcher_id == researcher.id, Project.id == id_)
            .first()
        )

        if not project:
            return (
                jsonify({
                    "message": {
                        "id": "api.projects.project_not_found",
                        "text": "Project not found",
                    }
                }),
                HTTPStatus.NOT_FOUND,
            )

        platform_class = SurveyPlatform.get_class_by_value(project.survey_platform_name)

        if not platform_class:
            logger.error("Unknown Survey Platform: %s", project.survey_platform_name)
            return (
                jsonify({
                    "message": {
                        "id": "api.survey.platform_not_supported",
                        "text": "Survey platform not supported",
                    }
                }),
                HTTPStatus.BAD_REQUEST,
            )

        survey_platform = platform_class(**project.survey_platform_fields)

        status, message_id, text_message, content = survey_platform.handle_export_survey_responses()

        # Check if an error occurred
        if status != HTTPStatus.OK:
            logger.error("Error during survey response export: %s", text_message)
            return (
                jsonify({"message": {"id": message_id, "text": text_message}}),
                status,
            )

        # Assuming content is the bytes of the file to be downloaded
        if content:
            # Create a BytesIO object with your zip content
            zip_in_memory = BytesIO(content)

            # Reset the cursor of the BytesIO object to the beginning
            zip_in_memory.seek(0)

            # Send the file-like object to the client
            return send_file(
                zip_in_memory,
                download_name=f"{project.name}_survey_responses.zip",
                as_attachment=True,
                mimetype="application/zip",
            )

        # If there is no content for some reason, return an appropriate message
        return (
            jsonify({
                "message": {
                    "id": "api.survey.export_failed",
                    "text": "Failed to export survey responses",
                }
            }),
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )


@projects.route("/<string:id_>/preview_survey", methods=["GET"])
@jwt_required()
def preview_survey(id_: str) -> ResponseReturnValue:
    """Generates a preview link for a survey associated with a specific project.

    Args:
        id_: The unique identifier of the project.

    Returns:
        Response: A JSON response containing the preview link if successful.
        - HTTPStatus.OK: If the preview link is successfully generated.
        - HTTPStatus.BAD_REQUEST: If the survey platform is not supported.
        - HTTPStatus.UNAUTHORIZED: If the user is unauthorized.
        - HTTPStatus.NOT_FOUND: If the project is not found.
    """
    logger.debug("Previewing survey for project with id: %s", id_)

    with DBManager.get_db() as db:
        user = get_jwt_identity()
        researcher: Researcher | None = db.query(Researcher).filter_by(email=user["email"]).first()
        if not researcher:
            # return (
            #     jsonify({"message": {"id": "api.unauthorized", "text": "Unauthorized"}}),
            #     HTTPStatus.UNAUTHORIZED,
            # )
            return APIResponses.AUTHORIZATION.UNAUTHORIZED.response

        project: Project | None = (
            db.query(Project)
            .join(Collaboration)
            .filter(Collaboration.researcher_id == researcher.id, Project.id == id_)
            .first()
        )

        if not project:
            return (
                jsonify({
                    "message": {
                        "id": "api.projects.project_not_found",
                        "text": "Project not found",
                    }
                }),
                HTTPStatus.NOT_FOUND,
            )

        platform_class = SurveyPlatform.get_class_by_value(project.survey_platform_name)

        if not platform_class:
            logger.error("Unknown Survey Platform: %s", project.survey_platform_name)
            return (
                jsonify({
                    "message": {
                        "id": "api.survey.platform_not_supported",
                        "text": "Survey platform not supported",
                    }
                }),
                HTTPStatus.BAD_REQUEST,
            )

        enabled_variables = []
        if project.variables:
            enabled_variables = [variable for variable in project.variables if variable["enabled"]]
        if project.custom_variables:
            enabled_custom_variables = CustomVariable.custom_variables_as_list([
                variable for variable in project.custom_variables if variable.get("enabled", False)
            ])
            enabled_variables.extend(enabled_custom_variables)

        survey_platform_fields = project.survey_platform_fields

        status, message_id, message, link = platform_class.get_preview_link(survey_platform_fields, enabled_variables)

        if status != HTTPStatus.OK:
            logger.error("Error during survey preview: %s", link)
            return jsonify({"message": {"id": message_id, "text": message}}), status

        return link, status
