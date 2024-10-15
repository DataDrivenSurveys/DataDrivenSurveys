"""Constants used throughout the project.

Created on 2024-10-14 20:51

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from http import HTTPStatus
from typing import TYPE_CHECKING, TypedDict

import flask

if TYPE_CHECKING:
    from werkzeug.sansio.response import Response as WerkzeugResponse

    APIResponseValue = tuple[WerkzeugResponse, HTTPStatus]

if flask.has_app_context():
    from flask import jsonify
else:

    def jsonify(data: dict) -> WerkzeugResponse:
        return data


class ResponseMessageDict(TypedDict):
    id: str
    text: str


class ResponseDict(TypedDict):
    message: ResponseMessageDict


@dataclass
class APIResponseMixin:
    """Mixin for API responses containing message ID, text, and status code."""

    id: str
    text: str
    status: HTTPStatus

    @property
    def response_value(self) -> tuple[ResponseDict, HTTPStatus]:
        return {"message": {"id": self.id, "text": self.text}}, self.status

    @property
    def response(self) -> APIResponseValue:
        """Returns a JSON response with the provided data."""
        return jsonify({"message": {"id": self.id, "text": self.text}}), self.status


class APIResponseEnum(APIResponseMixin, Enum):
    """Base class for API responses enums."""


class Authorization(APIResponseEnum):
    """Authorization responses."""

    EMAIL_REQUIRED = ("api.auth.email_required", "Email is required", HTTPStatus.BAD_REQUEST)
    FIRSTNAME_REQUIRED = ("api.auth.firstname_required", "First name is required", HTTPStatus.BAD_REQUEST)
    INVALID_USERNAME_OR_PASSWORD = (
        "api.auth.invalid_username_or_password",
        "Invalid username or password",
        HTTPStatus.UNAUTHORIZED,
    )
    LASTNAME_REQUIRED = ("api.auth.lastname_required", "Last name is required", HTTPStatus.BAD_REQUEST)
    PASSWORD_REQUIRED = ("api.auth.password_required", "Password is required", HTTPStatus.BAD_REQUEST)
    REGISTERED_SUCCESSFULLY = (
        "api.auth.registered_successfully",
        "Registered successfully",
        HTTPStatus.CREATED,
    )
    REGISTRATION_FAILED = ("registration_failed", "Failed to register", HTTPStatus.INTERNAL_SERVER_ERROR)
    USER_ALREADY_EXISTS = ("api.auth.user_already_exists", "User already exists", HTTPStatus.CONFLICT)
    UNAUTHORIZED = ("api.auth.unauthorized", "Unauthorized", HTTPStatus.UNAUTHORIZED)


class CustomVariables(APIResponseEnum):
    """/custom-variables/ endpoint responses."""


class DataProvider(APIResponseEnum):
    """/data-providers endpoint responses."""

    CONNECTION_NOT_FOUND = (
        "api.data_providers.connection_not_found",
        "Data connection not found",
        HTTPStatus.NOT_FOUND,
    )


class Projects(APIResponseEnum):
    """/projects/ endpoint responses."""

    NOT_FOUND = ("api.projects.not_found", "Project not found", HTTPStatus.NOT_FOUND)


class APIResponses(Enum):
    """DDSurveys API responses."""

    def __get__(self, instance, owner):
        return self.value

    AUTHORIZATION = Authorization
    CUSTOM_VARIABLES = CustomVariables
    DATA_PROVIDER = DataProvider
    PROJECTS = Projects