#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
@author: Stefan Teofanovic (stefan.teofanovic@heig-vd.ch)
"""

import datetime
import tempfile
import traceback
from io import BytesIO

from flask import Blueprint, g, jsonify, request, send_file
from flask.typing import ResponseReturnValue
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.attributes import flag_modified

from ..data_providers.bases import CustomVariable
from ..get_logger import get_logger
from ..models import Collaboration, DataConnection, Project, Researcher, Respondent, get_db
from ..survey_platforms.qualtrics import SurveyPlatform
from ._common import get_researcher
from .custom_variables import custom_variables
from .data_providers import data_providers
from .respondent import respondent

logger = get_logger(__name__)


projects = Blueprint("projects", __name__)
projects.register_blueprint(
    data_providers, url_prefix="/<string:project_id>/data-providers"
)
projects.register_blueprint(
    respondent, url_prefix="/<string:project_short_id>/respondent"
)
projects.register_blueprint(
    custom_variables, url_prefix="/<string:project_id>/custom-variables"
)


@projects.url_value_preprocessor
def get_project_id(endpoint, values):
    if values is not None and "project_id" in values:
        g.project_id = values.pop("project_id")


@projects.url_value_preprocessor
def get_project_short_id(endpoint, values):
    if values is not None and "project_short_id" in values:
        g.project_short_id = values.pop("project_short_id")


# List
@projects.route("/", methods=["GET"])
@jwt_required()
def list_projects():
    logger.debug("Listing projects")

    with get_db() as db:
        user = get_jwt_identity()

        researcher, status = get_researcher(db, user)
        if status is not None:
            researcher: ResponseReturnValue
            # Case where the user could not be found
            return researcher, status
        researcher: Researcher

        # get the projects
        projects = (
            db.query(Project)
            .join(Collaboration)
            .filter(Collaboration.researcher_id == researcher.id)
            .all()
        )

        return jsonify([project.to_dict() for project in projects]), 200


@projects.route("/", methods=["POST"])
@jwt_required()
def create_project():
    logger.debug("Creating a new project")

    with get_db() as db:
        data = request.get_json()

        user = get_jwt_identity()

        use_existing_survey = data.get("use_existing_survey")
        project_name = data.get("name")
        survey_platform_name = data.get("survey_platform_name")

        if not use_existing_survey and (project_name is None or project_name == ""):
            logger.error(f"No project name specified")
            return (
                jsonify(
                    {
                        "message": {
                            "id": "api.projects.name_is_required",
                            "text": "Project name is required",
                        }
                    }
                ),
                400,
            )

        fields = {
            field.get("name"): field.get("value", None) for field in data.get("fields")
        }

        if use_existing_survey:
            # survey_id becomes required if use_existing_survey is True
            override_required = ["survey_id"]
        else:
            override_required = []

        platform_class = SurveyPlatform.get_class_by_value(survey_platform_name)

        if not platform_class:
            logger.error(f"Unknown Survey Platform: {survey_platform_name}")
            return (
                jsonify(
                    {
                        "message": {
                            "id": "api.survey.platform_not_supported",
                            "text": "Unknown Survey Platform",
                        }
                    }
                ),
                400,
            )

        # Validate fields using check_inputs method
        are_fields_valid, missing_field_key = platform_class.check_input_fields(
            fields, override_required, SurveyPlatform
        )

        if not are_fields_valid:
            logger.error(f"Missing required field: {missing_field_key}")
            return (
                jsonify(
                    {
                        "message": {
                            "id": f"{missing_field_key}.missing",  # Append .missing to the full name key for the error id
                            "text": f"Field '{missing_field_key}' is required",
                        }
                    }
                ),
                400,
            )

        # get the researcher
        researcher, status = get_researcher(db, user)
        if status is not None:
            researcher: ResponseReturnValue
            # Case where the user could not be found
            return researcher, status
        researcher: Researcher

        # create an instance of the survey platform
        survey_platform = platform_class(**fields)

        # Handle the project creation
        status, message_id, text_message, project_name, survey_platform_fields = (
            survey_platform.handle_project_creation(project_name, use_existing_survey)
        )

        # Check if an error occurred
        if status != 200:
            logger.error(f"Error during project creation: {text_message}")
            return (
                jsonify({"message": {"id": message_id, "text": text_message}}),
                status,
            )

        new_project = Project(
            name=project_name,
            survey_platform_name=survey_platform_name,
            survey_platform_fields=survey_platform_fields,
        )

        new_collaboration = Collaboration(
            researcher_id=researcher.id, project=new_project
        )

        db.add(new_collaboration)
        db.add(new_project)

        try:
            db.commit()
            return (
                jsonify(
                    {
                        "message": {
                            "id": "api.projects.project_created_successfully",
                            "text": "Project created successfully",
                        },
                        "entity": new_project.to_dict(),
                    }
                ),
                201,
            )
        except SQLAlchemyError:
            import traceback

            logger.info(traceback.format_exc())
            db.rollback()
            return (
                jsonify(
                    {
                        "message": {
                            "id": "api.projects.failed_to_create_project",
                            "text": "Failed to create project",
                        }
                    }
                ),
                400,
            )


# Read
@projects.route("/<string:id>", methods=["GET"])
@jwt_required()
def get_project(id):
    logger.debug(f"Getting project with id: {id}")

    with get_db() as db:

        user = get_jwt_identity()

        # get the researcher
        researcher = db.query(Researcher).filter_by(email=user["email"]).first()
        if not researcher:
            return (
                jsonify(
                    {"message": {"id": "api.unauthorised", "text": "Unauthorised"}}
                ),
                401,
            )

        # get the project by id if it is in the collaborations
        project = (
            db.query(Project)
            .options(
                joinedload(Project.data_connections).joinedload(
                    DataConnection.data_provider
                ),
            )
            .join(Collaboration)
            .filter(Collaboration.researcher_id == researcher.id, Project.id == id)
            .first()
        )

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

        return jsonify(project.to_dict()), 200


# Update
@projects.route("/<string:id>", methods=["PUT"])
@jwt_required()
def update_project(id):
    logger.debug(f"Updating project with id: {id}")

    with get_db() as db:
        data = request.get_json()
        user = get_jwt_identity()
        researcher = db.query(Researcher).filter_by(email=user["email"]).first()
        if not researcher:
            return (
                jsonify(
                    {"message": {"id": "api.unauthorised", "text": "Unauthorised"}}
                ),
                401,
            )

        # get the project
        project = (
            db.query(Project)
            .join(Collaboration)
            .filter(Collaboration.researcher_id == researcher.id, Project.id == id)
            .first()
        )

        if project:
            for key, value in data.items():
                # is it the JSON field ?
                current_value = getattr(project, key, None)
                if current_value is None:
                    logger.warning(f"Project does not have attribute {key}")
                    continue
                if isinstance(current_value, dict):
                    for k, v in value.items():
                        current_value[k] = v

                    flag_modified(project, key)
                else:
                    setattr(project, key, value)
            db.commit()
            return (
                jsonify(
                    {
                        "message": {
                            "id": "api.projects.updated_successfully",
                            "text": "Project updated successfully",
                        }
                    }
                ),
                200,
            )
        else:
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


# Delete
@projects.route("/<string:id>", methods=["DELETE"])
@jwt_required()
def delete_project(id):
    logger.debug(f"Deleting project with id: {id}")

    with get_db() as db:

        # Get the current researcher's identity
        user = get_jwt_identity()
        researcher = db.query(Researcher).filter_by(email=user["email"]).first()
        if not researcher:
            return (
                jsonify(
                    {"message": {"id": "api.unauthorised", "text": "Unauthorised"}}
                ),
                401,
            )

        # Get the project and collaboration
        project = db.query(Project).get(id)
        collaboration = (
            db.query(Collaboration)
            .filter_by(project_id=id, researcher_id=researcher.id)
            .first()
        )

        if project and collaboration:
            db.delete(collaboration)
            db.delete(project)
            db.commit()
            return (
                jsonify(
                    {
                        "message": {
                            "id": "api.projects.project_and_collaboration_deleted_successfully",
                            "text": "Project and collaboration deleted successfully",
                        }
                    }
                ),
                200,
            )
        else:
            return (
                jsonify(
                    {
                        "message": {
                            "id": "api.projects.project_and_collaboration_not_found",
                            "text": "Project and collaboration not found",
                        }
                    }
                ),
                404,
            )


# DELETE all respondents for a project
@projects.route("/<string:id>/respondents", methods=["DELETE"])
@jwt_required()
def delete_respondents(id):
    logger.debug(f"Deleting project with id: {id}")

    with get_db() as db:

        user = get_jwt_identity()
        researcher = db.query(Researcher).filter_by(email=user["email"]).first()

        if not researcher:
            return (
                jsonify(
                    {"message": {"id": "api.unauthorised", "text": "Unauthorised"}}
                ),
                401,
            )

        project = (
            db.query(Project)
            .join(Collaboration)
            .filter(Collaboration.researcher_id == researcher.id, Project.id == id)
            .first()
        )

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

        respondents = (
            db.query(Respondent)
            .filter(
                Respondent.project_id == id,
            )
            .all()
        )

        for respondent in respondents:
            db.delete(respondent)

        db.commit()

        return (
            jsonify(
                {
                    "message": {
                        "id": "api.projects.respondents.deleted_successfully",
                        "text": "All project respondents deleted",
                    }
                }
            ),
            200,
        )


def get_survey_platform_connection(project):

    survey_platform_info = {
        "survey_platform_name": project.survey_platform_name,
        "connected": False,
        "exists": False,
        "survey_name": None,
        "survey_status": "unknown",
    }

    platform_class = SurveyPlatform.get_class_by_value(project.survey_platform_name)

    if not platform_class:
        survey_platform_info["id"] = "api.survey.platform_not_supported"
        return (400, "api.survey.platform_not_supported", survey_platform_info)

    try:
        platform = platform_class(**project.survey_platform_fields)
        return platform.fetch_survey_platform_info()
    except Exception as e:
        return (400, "api.survey.failed_to_check_connection", survey_platform_info)


@projects.route("/<string:id>/survey_platform/check_connection", methods=["GET"])
@jwt_required()
def check_survey_platform_connection(id):
    logger.debug(f"Checking survey platform connection for project with id: {id}")

    with get_db() as db:
        user = get_jwt_identity()
        researcher = db.query(Researcher).filter_by(email=user["email"]).first()
        if not researcher:
            return (
                jsonify(
                    {"message": {"id": "api.unauthorised", "text": "Unauthorised"}}
                ),
                401,
            )

        project = (
            db.query(Project)
            .join(Collaboration)
            .filter(Collaboration.researcher_id == researcher.id, Project.id == id)
            .first()
        )

        if not project:
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

        status, message_id, survey_platform_info = get_survey_platform_connection(
            project
        )

        if status != 200:
            return (
                jsonify(
                    {
                        "message": {
                            "id": message_id,
                            "text": "Failed to check survey platform connection",
                        }
                    }
                ),
                status,
            )

        if project.survey_platform_fields is None:
            project.survey_platform_fields = {}

        # Set the survey_status
        project.survey_platform_fields["survey_status"] = survey_platform_info.get(
            "survey_status"
        )

        # Check for the existence of the survey in the survey platform info
        if survey_platform_info.get("exists"):
            # If the survey name from the survey platform info doesn't match the current survey name in project.survey_platform_fields, update it
            if survey_platform_info.get(
                "survey_name"
            ) != project.survey_platform_fields.get("survey_name"):
                project.survey_platform_fields["survey_name"] = (
                    survey_platform_info.get("survey_name")
                )
        else:
            # If the survey doesn't exist in the survey platform info, set the survey_name in project.survey_platform_fields to None
            project.survey_platform_fields["survey_name"] = None

        # Commit the changes to the database
        flag_modified(project, "survey_platform_fields")
        db.commit()

        survey_platform_info["id"] = message_id
        return jsonify(survey_platform_info), status


@projects.route("/<string:id>/sync_variables", methods=["POST"])
@jwt_required()
def sync_variables(id):
    logger.debug(f"Syncing variables for project with id: {id}")

    with get_db() as db:
        user = get_jwt_identity()
        researcher = db.query(Researcher).filter_by(email=user["email"]).first()
        if not researcher:
            return (
                jsonify(
                    {"message": {"id": "api.unauthorised", "text": "Unauthorised"}}
                ),
                401,
            )

        project = (
            db.query(Project)
            .join(Collaboration)
            .filter(Collaboration.researcher_id == researcher.id, Project.id == id)
            .first()
        )

        if not project:
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

        enabled_variables = []
        if project.variables:
            enabled_variables = [
                variable for variable in project.variables if variable["enabled"]
            ]
        if project.custom_variables:
            enabled_custom_variables = CustomVariable.custom_variables_as_list(
                [
                    variable
                    for variable in project.custom_variables
                    if variable.get("enabled", False)
                ]
            )
            enabled_variables.extend(enabled_custom_variables)

        platform_class = SurveyPlatform.get_class_by_value(project.survey_platform_name)

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

        survey_platform = platform_class(**project.survey_platform_fields)

        status, message_id, text_message = survey_platform.handle_variable_sync(
            enabled_variables
        )

        # Check if an error occurred
        if status != 200:
            logger.error(f"Error during variable syncing: {text_message}")
            return (
                jsonify({"message": {"id": message_id, "text": text_message}}),
                status,
            )

        # If no error, update the last synced timestamp and commit the changes
        project.last_synced = datetime.datetime.now()
        db.commit()
        return jsonify({"message": {"id": message_id, "text": text_message}}), status


@projects.route("/<string:id>/export_survey_responses", methods=["POST"])
@jwt_required()
def export_survey_responses(id):
    logger.debug(f"Exporting survey responses for project with id: {id}")

    with get_db() as db:
        user = get_jwt_identity()
        researcher = db.query(Researcher).filter_by(email=user["email"]).first()
        if not researcher:
            return (
                jsonify(
                    {"message": {"id": "api.unauthorised", "text": "Unauthorised"}}
                ),
                401,
            )

        project = (
            db.query(Project)
            .join(Collaboration)
            .filter(Collaboration.researcher_id == researcher.id, Project.id == id)
            .first()
        )

        if not project:
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

        platform_class = SurveyPlatform.get_class_by_value(project.survey_platform_name)

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

        survey_platform = platform_class(**project.survey_platform_fields)

        status, message_id, text_message, content = (
            survey_platform.handle_export_survey_responses()
        )

        # Check if an error occurred
        if status != 200:
            logger.error(f"Error during survey response export: {text_message}")
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
            jsonify(
                {
                    "message": {
                        "id": "api.survey.export_failed",
                        "text": "Failed to export survey responses",
                    }
                }
            ),
            500,
        )


@projects.route("/<string:id>/preview_survey", methods=["GET"])
@jwt_required()
def preview_survey(id):
    logger.debug(f"Previewing survey for project with id: {id}")

    with get_db() as db:
        user = get_jwt_identity()
        researcher = db.query(Researcher).filter_by(email=user["email"]).first()
        if not researcher:
            return (
                jsonify(
                    {"message": {"id": "api.unauthorised", "text": "Unauthorised"}}
                ),
                401,
            )

        project = (
            db.query(Project)
            .join(Collaboration)
            .filter(Collaboration.researcher_id == researcher.id, Project.id == id)
            .first()
        )

        if not project:
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

        platform_class = SurveyPlatform.get_class_by_value(project.survey_platform_name)

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

        enabled_variables = []
        if project.variables:
            enabled_variables = [
                variable for variable in project.variables if variable["enabled"]
            ]
        if project.custom_variables:
            enabled_custom_variables = CustomVariable.custom_variables_as_list(
                [
                    variable
                    for variable in project.custom_variables
                    if variable.get("enabled", False)
                ]
            )
            enabled_variables.extend(enabled_custom_variables)

        survey_platform_fields = project.survey_platform_fields

        status, message_id, message, link = platform_class.get_preview_link(
            survey_platform_fields, enabled_variables
        )

        if status != 200:
            logger.error(f"Error during survey preview: {link}")
            return jsonify({"message": {"id": message_id, "text": message}}), status

        return link, status
