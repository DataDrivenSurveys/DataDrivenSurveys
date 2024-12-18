"""This module provides the Flask application.

Created on 2023-05-23 15:41.

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
@author: Stefan Teofanovic (stefan.teofanovic@heig-vd.ch)
"""

from __future__ import annotations

import datetime
import json
from ast import Str
from collections.abc import Callable
from enum import Enum, IntEnum, StrEnum
from functools import wraps
from http import HTTPStatus
from typing import Any

# Import installed libraries
import flask
from flask import Flask, jsonify
from flask.json.provider import DefaultJSONProvider
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required

from ddsurveys.blueprints.auth import auth
from ddsurveys.blueprints.projects import projects
from ddsurveys.blueprints.survey_platforms import survey_platforms
from ddsurveys.data_providers.bases import DataProvider

# Import project libraries
from ddsurveys.get_logger import get_logger, only_log_ddsurveys, set_logger_level
from ddsurveys.models import DBManager, EnumJSONEncoder
from ddsurveys.survey_platforms.bases import SurveyPlatform
from ddsurveys.utils import handle_env_file
from ddsurveys.variable_types import Data, VariableDataType

__all__ = ["app"]

logger = get_logger(__name__)

# Load environment variables
env = handle_env_file()

# Configure logging
if env.get("DDS_SET_LEVEL_FOR_ALL_LOGGERS", "true").casefold() == "true":
    set_logger_level(
        "ddsurveys",
        env.get("DDS_LOG_LEVEL", "DEBUG"),
        recursive=True,
        include_root=True,
    )

if env.get("DDS_ONLY_LOG_DDS", "true").casefold() == "true":
    only_log_ddsurveys()

logger.debug("Loaded environment variables: %s", env)

# Flask app config
APP_CONFIG = {
    # DDS specific settings
    # Custom option to set logging to show only output for ddsurveys modules
    "DDS_ONLY_LOG_DDS": env.get("DDS_ONLY_LOG_DDS", "true").casefold() == "true",
    # Set all loggers to the same level
    "DDS_SET_LEVEL_FOR_ALL_LOGGERS": env.get("DDS_SET_LEVEL_FOR_ALL_LOGGERS", "true").casefold() == "true",
    # Flask settings
    "LOG_LEVEL": env.get("DDS_LOG_LEVEL", "DEBUG"),
    # JWT Configuration
    "JWT_TOKEN_LOCATION": ["headers"],
    "JWT_HEADER_NAME": "Authorization",
    "JWT_HEADER_TYPE": "Bearer",
    "JWT_ACCESS_TOKEN_EXPIRES": datetime.timedelta(days=1),
    "JWT_SECRET_KEY": env.get("JWT_SECRET_KEY", "dummy_secret_key_for_testing"),
    "JWT_ERROR_MESSAGE_KEY": "message",  # We use 'message' instead of 'msg' in our frontend
    # eventually set up the blacklisting of tokens for sign out
    # will require a database model for the blacklisted tokens
    # "JWT_BLACKLIST_ENABLED": True,
    # "JWT_BLACKLIST_TOKEN_CHECKS": ['access','refresh']
}

JWT_FUNCTIONS_TO_WRAP: list[str] = [
    "default_expired_token_callback",
    "default_invalid_token_callback",
    "default_unauthorized_callback",
    "default_needs_fresh_token_callback",
    "default_revoked_token_callback",
    "default_user_lookup_error_callback",
    "default_token_verification_failed_callback",
]


def jwt_callback_wrapper(func):
    """Wrapper to format default JWT function return values.

    Args:
        func: Function to be wrapped.

    Returns:
        Wrapped function that outputs the expected format:
        ({"message": {"id": resources_key, "text": message_text}}, status_code)

    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        result, status = func(*args, **kwargs)
        name = func.__name__
        if name.startswith("default_"):
            name = name[8:]
        if name.endswith("_callback"):
            name = name[:-9]
        new_result = {"message": {"id": f"api.jwt.{name}", "text": result.json["message"]}}
        return jsonify(new_result), status

    return wrapper


def default_json_encoder(o: Any) -> Any:
    """Default JSON encoder function that can also encode Enums."""
    if isinstance(o, Enum):
        return o.value
    return DefaultJSONProvider.default(o)


class JSONProvider(DefaultJSONProvider):
    """A custom JSON provider that can encode Enums."""

    default: Callable[[Any], Any] = staticmethod(default_json_encoder)


# def create_app() -> Flask:
app: Flask = Flask(__name__)

# Use our custom JSON provider
app.json = JSONProvider(app=app)

app.config.from_mapping(APP_CONFIG)

DBManager.init_session(app=app)  # Initialize the database session

jwt = JWTManager(app)  # initializing the JWTManager

CORS(app, resources={r"/*": {"origins": ["http://localhost:3000"]}})

# Wrap JWT functions that need to be wrapped
for func_name in JWT_FUNCTIONS_TO_WRAP:
    fname = func_name.replace("default", "")
    func = getattr(jwt, fname)
    func = jwt_callback_wrapper(func)
    setattr(jwt, fname, func)


# App configuration
@app.before_request
def create_db_session() -> None:
    flask.g.db = DBManager.get_db()  # Store the database session in the Flask global context


@app.teardown_appcontext
def shutdown_session(response_or_exc) -> None:
    db = flask.g.pop("db", None)
    if db is not None:
        db.close()  # This should now work without errors


app.register_blueprint(auth, url_prefix="/auth")
app.register_blueprint(projects, url_prefix="/projects")
app.register_blueprint(survey_platforms, url_prefix="/survey-platforms")

# declare_app_routes(app)

# return app


# def declare_app_routes(app) -> None:

# TODO : Discuss eventual migration of these routes into respective blueprints


@app.route("/survey-platforms", methods=["GET"])
@jwt_required()
def list_survey_platforms():
    return SurveyPlatform.get_all_form_fields(), HTTPStatus.OK


@app.route("/data-providers", methods=["GET"])
@jwt_required()
def list_data_providers():
    return DataProvider.get_all_form_fields(), HTTPStatus.OK


@app.route("/data-providers/data-categories", methods=["GET"])
def list_data_categories():
    return DataProvider.get_all_data_categories(), HTTPStatus.OK


@app.route("/custom-variables/filter-operators/<data_type>", methods=["GET"])
def list_filter_operators(data_type):
    data_type = VariableDataType(data_type)
    data_class = Data.get_class_by_type(data_type)
    return data_class.get_filter_operators(), HTTPStatus.OK


@app.route("/custom-variables/filter-operators", methods=["GET"])
def list_all_filter_operators():
    return Data.get_all_filter_operators(), HTTPStatus.OK
