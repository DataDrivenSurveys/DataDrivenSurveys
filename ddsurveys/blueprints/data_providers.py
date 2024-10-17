#!/usr/bin/env python
"""This module provides blueprints for handling data providers.

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
@author: Stefan Teofanovic (stefan.teofanovic@heig-vd.ch).
"""

from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING, cast

from flask import Blueprint, g, jsonify, request
from flask import Response as FlaskResponse
from flask_jwt_extended import get_jwt_identity, jwt_required

from ddsurveys.blueprints._common import get_project, get_project_data_connection
from ddsurveys.data_providers import DataProvider
from ddsurveys.get_logger import get_logger
from ddsurveys.models import DataConnection, DataProviderName, DBManager, Project
from ddsurveys.models import DataProvider as DataProviderModel

if TYPE_CHECKING:
    from flask.typing import ResponseReturnValue
    from werkzeug.sansio.response import Response

    from ddsurveys.api_responses import APIResponseValue

logger = get_logger(__name__)

data_providers = Blueprint("data-providers", __name__)


# Create
@data_providers.route("/", methods=["POST"])
@jwt_required()
def add_data_provider_to_project() -> ResponseReturnValue:
    """Adds a data provider to a project.

    This function handles the addition of a data provider to a project.
    It validates the provided data, checks if the data provider exists,
    and creates a new data connection if it does not already exist.

    Returns:
        ResponseReturnValue: A JSON response indicating the result of the operation.
            Possible status codes are:
            - HTTPStatus.CREATED: Data connection created successfully.
            - HTTPStatus.BAD_REQUEST: Bad request, e.g., missing data provider or data
                connection already exists.
            - HTTPStatus.NOT_FOUND: Data provider not found or not supported.
    """
    logger.debug("Adding data provider to project")

    with DBManager.get_db() as db:
        project_id = g.get("project_id")

        user = get_jwt_identity()

        project: Project | FlaskResponse
        project, status_code = get_project(db, user)
        if status_code is not None:
            project = cast(FlaskResponse, project)
            status_code = cast(int, status_code)
            # Case where the user or project could not be found
            return project, status_code

        data = request.get_json()

        selected_data_provider = data.get("selected_data_provider")

        if not selected_data_provider:
            logger.error("No data provider selected")
            return (
                jsonify(
                    {
                        "message": {
                            "id": "api.data_provider.is_required",
                            "text": "Data provider is required",
                        }
                    }
                ),
                HTTPStatus.BAD_REQUEST,
            )

        provider_class = DataProvider.get_class_by_name(selected_data_provider["label"])

        if not provider_class:
            logger.error("Data provider %s not found", selected_data_provider["value"])
            return (
                jsonify(
                    {
                        "message": {
                            "id": "api.data_provider.not_supported",
                            "text": "Data provider is not supported",
                        }
                    }
                ),
                HTTPStatus.NOT_FOUND,
            )

        fields_data = data.get("fields", [])
        fields_dict = {field["name"]: field["value"] for field in fields_data}

        provider_instance = provider_class(**fields_dict)

        status: bool = provider_instance.test_connection()

        # check if the data provider already exists
        logger.debug("%s", selected_data_provider)
        logger.debug("%s, %s, %s", provider_class.name, provider_class.label, provider_class.provider_type)
        data_provider = (
            db.query(DataProviderModel)
            .filter_by(
                name=selected_data_provider["label"],
                data_provider_name=provider_class.name,
            )
            .first()
        )

        if not data_provider:
            data_provider = DataProviderModel(
                name=selected_data_provider["label"],
                data_provider_type=provider_class.provider_type,
                data_provider_name=provider_class.name,
            )
            db.add(data_provider)
            db.commit()

        # check if the data connection already exists
        data_connection = (
            db.query(DataConnection)
            .filter_by(
                project_id=project.id,
                data_provider_name=data_provider.data_provider_name,
            )
            .first()
        )

        if data_connection:
            logger.info("Data connection with %s already exists for project %s", data_provider.name, project_id)
            return (
                jsonify(
                    {
                        "message": {
                            "id": "api.data_provider.connection_already_exists",
                            "text": "Data connection already exists",
                        }
                    }
                ),
                HTTPStatus.BAD_REQUEST,
            )

        provider_class = DataProvider.get_class_by_name(data_provider.name)

        if not provider_class:
            logger.error("Data provider %s not found", data_provider.name)
            return (
                jsonify(
                    {
                        "message": {
                            "id": "api.data_provider.not_supported",
                            "text": "Data provider is not supported",
                        }
                    }
                ),
                HTTPStatus.NOT_FOUND,
            )

        # add variables related to the data provider
        variables = provider_class.get_builtin_variables()

        # add enabled: False to the variables
        variables = [{**variable, "enabled": False} for variable in variables]

        # append the variables to the project variables JSON field
        project.variables = project.variables + variables

        # create the data connection
        data_connection = DataConnection(
            project_id=project.id,
            data_provider_name=data_provider.data_provider_name,
            fields=fields_dict,
        )

        db.add(data_connection)
        db.commit()

        return jsonify(data_connection.to_dict()), HTTPStatus.CREATED


# Update
@data_providers.route("/<string:data_provider_name>", methods=["PUT"])
@jwt_required()
def update_data_provider(data_provider_name: str) -> APIResponseValue:
    """Updates the data provider for a project.

    This function handles the update of a data provider for a project.
    It validates the provided data, checks if the data provider exists,
    and updates the data connection if it does.

    Args:
        data_provider_name: The name of the data provider to be updated.

    Returns:
        ResponseReturnValue: A JSON response indicating the result of the operation.
            Possible status codes are:
            - HTTPStatus.OK: Data provider updated successfully.
            - HTTPStatus.BAD_REQUEST: Bad request, e.g., missing data provider.
            - HTTPStatus.NOT_FOUND: Data provider not found or not supported.
    """
    logger.debug("Updating data provider")

    with DBManager.get_db() as db:
        user = get_jwt_identity()

        project_response: Project | FlaskResponse
        data_connection_int: DataConnection | HTTPStatus
        project_response, data_connection_int = get_project_data_connection(
            db=db,
            user=user,
            data_provider_name=data_provider_name,
        )
        if isinstance(data_connection_int, int):
            project_response = cast(FlaskResponse, project_response)
            # Case where something could not be found in the database
            return project_response, data_connection_int
        data_connection: DataConnection = data_connection_int

        data = request.get_json()
        fields_data = data.get("fields", [])
        fields_dict = {field["name"]: field["value"] for field in fields_data}

        selected_data_provider = data.get("selected_data_provider")

        if not selected_data_provider:
            logger.error("No data provider selected")
            return (
                jsonify(
                    {
                        "message": {
                            "id": "api.data_provider.is_required",
                            "text": "Data provider is required",
                        }
                    }
                ),
                HTTPStatus.BAD_REQUEST,
            )

        provider_class = DataProvider.get_class_by_name(selected_data_provider["label"])

        if not provider_class:
            logger.error("Data provider %s not found", selected_data_provider["label"])
            return (
                jsonify(
                    {
                        "message": {
                            "id": "api.data_provider.not_supported",
                            "text": "Data provider is not supported",
                        }
                    }
                ),
                HTTPStatus.NOT_FOUND,
            )

        provider_instance = provider_class(**fields_dict)

        status: bool = provider_instance.test_connection()

        # check if status is successful
        if HTTPStatus(status).is_success:
            data_connection.connected = True
            db.commit()
        else:
            data_connection.connected = False
            db.commit()

        # check if the data provider already exists
        data_provider = (
            db.query(DataProviderModel)
            .filter_by(
                name=selected_data_provider["label"],
                data_provider_name=DataProviderName(selected_data_provider["value"]),
            )
            .first()
        )

        if not data_provider:
            logger.error("Data provider '%s' does not exist", selected_data_provider["value"])
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

        # update the data connection
        data_connection.fields = fields_dict

        db.commit()

        return (
            jsonify(
                {
                    "message": {
                        "id": "api.data_provider.updated",
                        "text": "Data provider updated",
                    }
                }
            ),
            HTTPStatus.OK,
        )


# delete
@data_providers.route("/<string:data_provider_name>", methods=["DELETE"])
@jwt_required()
def delete_data_provider(data_provider_name: str) -> ResponseReturnValue:
    """Deletes a data provider from a project.

    This function handles the deletion of a data provider from a project.
    It validates the provided data, checks if the data provider exists,
    and deletes the data connection if it does.

    Args:
        data_provider_name: The name of the data provider to be deleted.

    Returns:
        ResponseReturnValue: A JSON response indicating the result of the operation.
            Possible status codes are:
            - HTTPStatus.OK: Data connection deleted successfully.
            - HTTPStatus.BAD_REQUEST: Bad request, e.g., missing data provider.
            - HTTPStatus.NOT_FOUND: Data provider not found or not supported.
    """
    logger.debug("Deleting data provider")

    with DBManager.get_db() as db:
        user = get_jwt_identity()

        project_response, data_connection_int = get_project_data_connection(
            db=db,
            user=user,
            data_provider_name=data_provider_name,
        )
        if isinstance(data_connection_int, int):
            project_response: cast(Response, project_response)
            # Case where something could not be found in the database
            return project_response, data_connection_int
        project: Project = project_response
        data_connection: DataConnection = data_connection_int

        # delete the variables related to the data connection
        if project.variables is not None and isinstance(project.variables, list | tuple):
            project.variables = [
                variable
                for variable in project.variables
                if variable["data_provider"] != data_connection.data_provider.data_provider_name.value
            ]

        # delete the custom variables related to the data connection
        if project.custom_variables is not None and isinstance(project.custom_variables, list | tuple):
            project.custom_variables = [
                variable
                for variable in project.custom_variables
                if variable["data_provider"] != data_connection.data_provider.data_provider_name.value
            ]

        # delete the data connection and update the project variables
        db.delete(data_connection)
        db.commit()

        return (
            jsonify(
                {
                    "message": {
                        "id": "api.data_provider.connection_deleted",
                        "text": "Data connection deleted successfully",
                    }
                }
            ),
            HTTPStatus.OK,
        )


# Check Connection
@data_providers.route("/<string:data_provider_name>/check-connection", methods=["GET"])
@jwt_required()
def check_dataprovider_connection(data_provider_name: str) -> ResponseReturnValue:
    """Checks the connection status of a data provider.

    This function handles the checking of a data provider's connection status for a
    project.
    It validates the provided data, checks if the data provider exists, and tests the
    connection.

    Args:
        data_provider_name: The name of the data provider to check the connection for.

    Returns:
        ResponseReturnValue: A JSON response indicating the result of the operation.
            Possible status codes are:
            - HTTPStatus.OK: Data connection is successful.
            - HTTPStatus.BAD_REQUEST: Data connection failed.
            - HTTPStatus.NOT_FOUND: Data provider not found or not supported.
    """
    logger.debug("Checking data provider connection")

    with DBManager.get_db() as db:
        user = get_jwt_identity()

        project_response, data_connection_int = get_project_data_connection(
            db=db,
            user=user,
            data_provider_name=data_provider_name,
        )
        if isinstance(data_connection_int, int):
            project_response: cast(Response, project_response)
            # Case where something could not be found in the database
            return project_response, data_connection_int
        data_connection: DataConnection = data_connection_int

        # check the connection
        data_provider = db.query(DataProviderModel).get(data_provider_name)

        provider_class = DataProvider.get_class_by_name(data_provider.name)
        provider_instance: DataProvider = provider_class(**data_connection.fields)
        success = provider_instance.test_connection()

        db.commit()
        return jsonify(
            {
                "message": {
                    "id": "api.data_provider.connection_status",
                    "text": "Data connection status",
                }
            }
        ), (HTTPStatus.OK if success else HTTPStatus.BAD_REQUEST)
