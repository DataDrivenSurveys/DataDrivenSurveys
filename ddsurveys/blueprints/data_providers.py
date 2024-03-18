#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

"""

from flask import Blueprint, request, jsonify, g
from flask.typing import ResponseReturnValue
from flask_jwt_extended import jwt_required, get_jwt_identity

from ._common import get_project, get_project_data_connection
from ..models import Project, DataConnection, DataProvider as DataProviderModel, DataProviderName, get_db
from ..get_logger import get_logger
from ..data_providers import DataProvider


logger = get_logger(__name__)

data_providers = Blueprint('data-providers', __name__)


# Create
@data_providers.route('/', methods=['POST'])
@jwt_required()
def add_data_provider_to_project():
    """

    Returns:

    """
    logger.debug("Adding data provider to project")

    with get_db() as db:

        project_id = g.get('project_id')

        user = get_jwt_identity()

        project, status = get_project(db, user)
        if status is not None:
            project: ResponseReturnValue
            # Case where the user or project could not be found
            return project, status
        project: Project

        data = request.get_json()

        selected_data_provider = data.get('selected_data_provider')

        if not selected_data_provider:
            logger.error("No data provider selected")
            return jsonify({"message": {
                "id": "api.data_provider.is_required",
                "text": "Data provider is required"
            }}), 400

        provider_class = DataProvider.get_class_by_value(selected_data_provider["value"])

        if not provider_class:
            logger.error(f"Data provider {selected_data_provider['value']} not found")
            return jsonify({"message": {
                "id": "api.data_provider.not_supported",
                "text": "Data provider is not supported"
            }}), 404

        fields_data = data.get('fields', [])
        fields_dict = {field['name']: field['value'] for field in fields_data}

        provider_instance = provider_class(**fields_dict)

        status = provider_instance.test_connection()

        # check if the data provider already exists
        data_provider = db.query(DataProviderModel).filter_by(
            name=selected_data_provider["label"],
            data_provider_name=DataProviderName(selected_data_provider["value"])
        ).first()

        if not data_provider:
            data_provider = DataProviderModel(
                name=selected_data_provider["label"],
                data_provider_name=DataProviderName(selected_data_provider["value"]),
                data_provider_type=provider_class.provider_type
            )
            db.add(data_provider)
            db.commit()

        # check if the data connection already exists
        data_connection = db.query(DataConnection).filter_by(
            project_id=project.id,
            data_provider_name=data_provider.data_provider_name
        ).first()

        if data_connection:
            logger.info(f"Data connection with {data_provider.data_provider_name} already exists for project "
                        f"{project_id}")
            return jsonify({"message": {
                "id": "api.data_provider.connection_already_exists",
                "text": "Data connection already exists"
            }}), 400

        provider_class = DataProvider.get_class_by_value(data_provider.data_provider_name.value)

        if not provider_class:
            logger.error(f"Data provider {data_provider.data_provider_name} not found")
            return jsonify({"message": {
                "id": "api.data_provider.not_supported",
                "text": "Data provider is not supported"
            }}), 404

        # add variables related to the data provider
        variables = provider_class.get_builtin_variables()

        # add enables : false to the variables
        variables = [{**variable, "enabled": False} for variable in variables]

        # append the variables to the project variables JSON field
        project.variables = project.variables + variables

        # create the data connection
        data_connection = DataConnection(
            project_id=project.id,
            data_provider_name=data_provider.data_provider_name,
            fields=fields_dict
        )

        db.add(data_connection)
        db.commit()

        return jsonify(data_connection.to_dict()), 201


# Update
@data_providers.route('/<string:data_provider_name>', methods=['PUT'])
@jwt_required()
def update_data_provider(data_provider_name):
    logger.debug("Updating data provider")

    with get_db() as db:
        user = get_jwt_identity()

        project, data_connection, status = get_project_data_connection(db, user, data_provider_name)
        if status is not None:
            data_connection: ResponseReturnValue
            # Case where something could not be found in the database
            return data_connection, status
        data_connection: DataConnection

        data = request.get_json()
        fields_data = data.get('fields', [])
        fields_dict = {field['name']: field['value'] for field in fields_data}

        selected_data_provider = data.get('selected_data_provider')

        if not selected_data_provider:
            logger.error(f"No data provider selected")
            return jsonify({"message": {
                "id": "api.data_provider.is_required",
                "text": "Data provider is required"
            }}), 400

        provider_class = DataProvider.get_class_by_value(selected_data_provider["value"])

        if not provider_class:
            logger.error(f"Data provider {selected_data_provider['value']} not found")
            return jsonify({"message": {
                "id": "api.data_provider.not_supported",
                "text": "Data provider is not supported"
            }}), 404

        provider_instance = provider_class(**fields_dict)

        status = provider_instance.test_connection()

        # check if status is between 200 and 299
        if 200 <= status < 300:
            data_connection.connected = True
            db.commit()
        else:
            data_connection.connected = False
            db.commit()

        # check if the data provider already exists
        data_provider = db.query(DataProviderModel).filter_by(
            name=selected_data_provider["label"],
            data_provider_name=DataProviderName(selected_data_provider["value"])
        ).first()

        if not data_provider:
            logger.error(f"Data provider '{selected_data_provider['value']}' does not exist")
            return jsonify({"message": {
                "id": "api.data_provider.not_found",
                "text": "Data provider not found"
            }}), 404

        # update the data connection
        data_connection.fields = fields_dict

        db.commit()

        return jsonify({ "message": {
            "id": "api.data_provider.updated",
            "text": "Data provider updated"
        }}), 200


# delete
@data_providers.route('/<string:data_provider_name>', methods=['DELETE'])
@jwt_required()
def delete_data_provider(data_provider_name):
    logger.debug("Deleting data provider")

    with get_db() as db:
        user = get_jwt_identity()

        project, data_connection, status = get_project_data_connection(db, user, data_provider_name)
        if status is not None:
            data_connection: ResponseReturnValue
            # Case where something could not be found in the database
            return data_connection, status
        data_connection: DataConnection

        # delete the variables related to the data connection
        if project.variables is not None and isinstance(project.variables, (list, tuple)):
            project.variables = [variable for variable in project.variables if variable["data_provider"] != data_connection.data_provider.data_provider_name.value]

        # delete the custom variables related to the data connection
        if project.custom_variables is not None and isinstance(project.custom_variables, (list, tuple)):
            project.custom_variables = [variable for variable in project.custom_variables if variable["data_provider"] != data_connection.data_provider.data_provider_name.value]

        # delete the data connection and update the project variables
        db.delete(data_connection)
        db.commit()

        return jsonify({"message": {
            "id": "api.data_provider.connection_deleted",
            "text": "Data connection deleted successfully"
        }}), 200


# Check Connection
@data_providers.route('/<string:data_provider_name>/check-connection', methods=['GET'])
@jwt_required()
def check_dataprovider_connection(data_provider_name):
    logger.debug("Checking data provider connection")

    with get_db() as db:
        user = get_jwt_identity()

        project, data_connection, status = get_project_data_connection(db, user, data_provider_name)
        if status is not None:
            data_connection: ResponseReturnValue
            # Case where something could not be found in the database
            return data_connection, status
        data_connection: DataConnection

        # check the connection
        data_provider = db.query(DataProviderModel).get(data_provider_name)

        provider_class = DataProvider.get_class_by_value(data_provider.data_provider_name.value)
        provider_instance: DataProvider = provider_class(**data_connection.fields)
        success = provider_instance.test_connection()

        db.commit()
        return jsonify({"message": {
            "id": "api.data_provider.connection_status",
            "text": "Data connection status",
        }}), 200 if success else 400
