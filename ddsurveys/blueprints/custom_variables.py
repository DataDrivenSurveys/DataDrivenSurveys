#!/usr/bin/env python
"""This module provides blueprints for handling custom variables.

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
@author: Stefan Teofanovic (stefan.teofanovic@heig-vd.ch).
"""

import traceback
from keyword import iskeyword
from typing import TYPE_CHECKING

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy.orm.attributes import flag_modified

from ddsurveys.blueprints._common import get_project
from ddsurveys.get_logger import get_logger
from ddsurveys.models import DBManager, Project

if TYPE_CHECKING:
    from flask.typing import ResponseReturnValue

logger = get_logger(__name__)


custom_variables = Blueprint("custom-variabls", __name__)
"""location: /projects/<project_id>/custom-variables
"""


@custom_variables.route("/", methods=["GET"])
@jwt_required()
def get_project_custom_variables():
    logger.debug("Getting project custom variables")
    with DBManager.get_db() as db:

        user = get_jwt_identity()

        project, status = get_project(db, user)
        if status is not None:
            project: ResponseReturnValue
            # Case where the user or project could not be found
            return project, status
        project: Project

        return jsonify(project.custom_variables), 200


def is_valid_variable_name(variable_name: str) -> tuple[bool, str, str]:
    """Validate if the given variable name adheres to Python naming conventions.
    Returns a triple (is_valid, message_id, text).
    """
    # Shortcut for valid variable names
    if variable_name.isidentifier():
        return True, "", ""

    if not variable_name:
        return (
            False,
            "api.custom_variables.error.name_required",
            "Variable name is required.",
        )

    if not variable_name[0].isalpha() and variable_name[0] != "_":
        return (
            False,
            "api.custom_variables.error.must_start_with_letter_or_underscore",
            "Variable names must start with a letter or underscore.",
        )

    if not all(char.isalnum() or char == "_" for char in variable_name):
        return (
            False,
            "api.custom_variables.error.only_alphanumeric_and_underscore",
            "Variable names can only contain alpha-numeric characters and underscores.",
        )

    if iskeyword(variable_name):
        return (
            False,
            "api.custom_variables.error.cannot_be_python_keyword",
            "Variable name cannot be a Python keyword.",
        )

    return True, "", ""


def check_custom_variable_data(data):
    """Check if the custom variable data is valid.
    Returns a triple (is_valid, message_id, text).
    """
    # Check if variable name is valid
    is_valid, message_id, validation_msg = is_valid_variable_name(
        data.get("variable_name")
    )
    if not is_valid:
        return False, message_id, validation_msg

    # Check if the data provider is set
    if not data.get("data_provider"):
        return (
            False,
            "api.custom_variables.error.data_provider_required",
            "Data provider is required.",
        )

    # Check if the data category is set
    if not data.get("data_category"):
        return (
            False,
            "api.custom_variables.error.data_category_required",
            "Data category is required.",
        )

    # Check if the attributes are set
    if not data.get("cv_attributes"):
        return (
            False,
            "api.custom_variables.error.attributes_required",
            "Attributes are required.",
        )

    # Check if the selection is set
    if not data.get("selection"):
        return (
            False,
            "api.custom_variables.error.selection_required",
            "Selection is required.",
        )

    if data.get("selection"):
        selection = data.get("selection")
        if not selection.get("operator"):
            return (
                False,
                "api.custom_variables.error.selection_operator_required",
                "Selection operator is required.",
            )

        if selection.get("operator") != "random" and not selection.get("attr"):
            return (
                False,
                "api.custom_variables.error.selection_attr_required",
                "Selection attribute is required.",
            )

    # Check if the filters are set
    if data.get("filters"):
        filters = data.get("filters")
        for filter in filters:
            if not filter.get("attr"):
                return (
                    False,
                    "api.custom_variables.error.filter_attr_required",
                    "Filter attribute is required.",
                )
            if not filter.get("operator"):
                return (
                    False,
                    "api.custom_variables.error.filter_operator_required",
                    "Filter operator is required.",
                )
            if not filter.get("value"):
                return (
                    False,
                    "api.custom_variables.error.filter_value_required",
                    "Filter value is required.",
                )

    return True, "", ""


@custom_variables.route("/", methods=["POST"])
@jwt_required()
def add_custom_variable_to_project():
    logger.debug("Adding custom variable")
    with DBManager.get_db() as db:

        user = get_jwt_identity()

        project, status = get_project(db, user)
        if status is not None:
            project: ResponseReturnValue
            # Case where the user or project could not be found
            return project, status
        project: Project

        data = request.get_json()

        # Validate variable name using the new function
        is_valid, message_id, validation_msg = check_custom_variable_data(data)
        if not is_valid:
            logger.error("Failed to add custom variable: %s", validation_msg)
            return jsonify({"message": {"id": message_id, "text": validation_msg}}), 400

        # Check if variable name already exists
        current_custom_variables = project.custom_variables or []
        existing_variable_names = [
            var["variable_name"] for var in current_custom_variables
        ]

        # Check if a new variable has an assigned ID, if not, assign a non-conflicting ID
        if data.get("id", -1) == -1:
            # merge both builtin and custom variables
            all_variables = project.variables + current_custom_variables
            # max id
            max_id = max([var.get("id", 0) for var in all_variables])
            # assign new id
            data["id"] = max_id + 1

        # Enabling all the custom variables attributes by default
        for attr in data["cv_attributes"]:
            attr["enabled"] = True

        variable_name = data.get("variable_name")

        if variable_name in existing_variable_names:
            logger.debug("Variable name '%s' already exists.", variable_name)
            return (
                jsonify(
                    {
                        "message": {
                            "id": "api.projects.custom_variables.variable_exists",
                            "text": f"Variable name '{variable_name}' already exists. Use a different name.",
                        }
                    }
                ),
                400,
            )

        try:
            current_custom_variables.append(data)
            project.custom_variables = current_custom_variables
            flag_modified(
                project, "custom_variables"
            )  # This is required to notify SQLAlchemy that the custom_variables field has changed
            db.commit()

        except Exception as e:
            logger.critical("This error should be excepted correctly: %s", e)
            logger.exception("Failed to add custom variable:\n%s\n", traceback.format_exc())
            return (
                jsonify(
                    {
                        "message": {
                            "id": "api.projects.custom_variables.failed_to_add",
                            "text": "Failed to add custom variable",
                        }
                    }
                ),
                500,
            )

        return jsonify(project.custom_variables), 200


@custom_variables.route("/<int:variable_id>", methods=["GET"])
@jwt_required()
def get_project_custom_variable(variable_id):
    with DBManager.get_db() as db:

        user = get_jwt_identity()

        project, status = get_project(db, user)
        if status is not None:
            project: ResponseReturnValue
            # Case where the user or project could not be found
            return project, status
        project: Project

        variable = next(
            (
                var
                for var in project.custom_variables
                if var.get("id", -1) == variable_id
            ),
            None,
        )
        if not variable:
            return (
                jsonify(
                    {
                        "message": {
                            "id": "api.projects.custom_variables.not_found",
                            "text": "Custom variable not found",
                        }
                    }
                ),
                404,
            )

        return jsonify(variable), 200


@custom_variables.route("/<int:variable_id>", methods=["PUT"])
@jwt_required()
def update_project_custom_variable(variable_id):
    with DBManager.get_db() as db:
        user = get_jwt_identity()

        project, status = get_project(db, user)
        if status is not None:
            project: ResponseReturnValue
            # Case where the user or project could not be found
            return project, status
        project: Project

        variable = next(
            (
                var
                for var in project.custom_variables
                if var.get("id", -1) == variable_id
            ),
            None,
        )
        if not variable:
            return (
                jsonify(
                    {
                        "message": {
                            "id": "api.projects.custom_variables.not_found",
                            "text": "Custom variable not found",
                        }
                    }
                ),
                404,
            )

        new_variable_data = request.get_json()

        # Validate variable name using the new function
        is_valid, message_id, validation_msg = check_custom_variable_data(
            new_variable_data
        )
        if not is_valid:
            logger.error(
                "Failed to update custom variable: %s: %s", message_id, validation_msg
            )
            return jsonify({"message": {"id": message_id, "text": validation_msg}}), 400

        new_variable_data["id"] = variable["id"]
        new_variable_data["enabled"] = variable.get("enabled", False)

        # Is same data category
        if variable["data_category"] == new_variable_data["data_category"]:
            # Recover the attributes enabled state and test_value from the previous
            old_attributes = variable["cv_attributes"]
            new_attributes = new_variable_data["cv_attributes"]
            for idx, attr in enumerate(new_attributes):
                old_attr = old_attributes[idx]
                if old_attr:
                    attr["enabled"] = old_attr.get("enabled", False)
                    attr["test_value"] = old_attr.get("test_value", None)

        # Update the existing variable with new data
        index = project.custom_variables.index(variable)

        project.custom_variables[index] = new_variable_data

        flag_modified(
            project, "custom_variables"
        )  # This is required to notify SQLAlchemy that the custom_variables field has changed

        db.commit()

        return jsonify(project.custom_variables), 200


@custom_variables.route("/<int:variable_id>", methods=["DELETE"])
@jwt_required()
def delete_project_custom_variable(variable_id):
    logger.debug("Deleting custom variable: %s", variable_id)
    with DBManager.get_db() as db:
        user = get_jwt_identity()

        project, status = get_project(db, user)
        if status is not None:
            project: ResponseReturnValue
            # Case where the user or project could not be found
            return project, status
        project: Project

        variable = next(
            (
                var
                for var in project.custom_variables
                if var.get("id", -1) == variable_id
            ),
            None,
        )
        if not variable:
            logger.error("Variable not found: %s", variable_id)
            return (
                jsonify(
                    {
                        "message": {
                            "id": "api.projects.custom_variables.not_found",
                            "text": "Custom variable not found",
                        }
                    }
                ),
                404,
            )

        # Delete the variable from the custom_variables list
        project.custom_variables.remove(variable)

        flag_modified(
            project, "custom_variables"
        )  # This is required to notify SQLAlchemy that the custom_variables field has changed

        db.commit()

        logger.debug("Deleted custom variable: %s", variable_id)
        return jsonify(project.custom_variables), 200
