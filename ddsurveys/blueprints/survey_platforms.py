#!/usr/bin/env python
"""This module provides blueprints for handling survey platforms.

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
@author: Stefan Teofanovic (stefan.teofanovic@heig-vd.ch).
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from ddsurveys.get_logger import get_logger
from ddsurveys.survey_platforms import SurveyPlatform

if TYPE_CHECKING:
    from flask.typing import ResponseReturnValue

logger = get_logger(__name__)

survey_platforms = Blueprint("survey-platforms", __name__)


@jwt_required()
@survey_platforms.route("/<string:survey_platform>/exchange-code", methods=["POST"])
def exchange_code_for_tokens(survey_platform: str) -> ResponseReturnValue:
    """Exchanges the code for an access token using OAuth2 Code Flow.

    This is a public endpoint, so no authentication is required.
    This endpoint should not provide any sensitive information.

    Args:
        survey_platform (str): The name of the survey platform.

    Returns:
        ResponseReturnValue: A JSON response indicating the result of the operation.
            Possible status codes are:
            - 200: Successfully exchanged code for tokens.
            - 400: Bad request, e.g., missing survey platform or code.
            - 500: Internal server error, e.g., error exchanging code for tokens.
    """
    data = request.get_json()

    survey_platform_type = survey_platform

    code = data.get("code")

    if not survey_platform_type:
        return (
            jsonify(
                {
                    "message": {
                        "id": "api.ddsurveys.survey_platforms.exchange_code.error",
                        "text": "Error exchanging code for tokens",
                    },
                }
            ),
            400,
        )

    if not code:
        return (
            jsonify(
                {
                    "message": {
                        "id": "api.ddsurveys.survey_platforms.exchange_code.error",
                        "text": "Error exchanging code for tokens",
                    },
                }
            ),
            400,
        )

    try:
        # Create an instance of the data provider
        survey_platform_class = SurveyPlatform.get_class_by_value(survey_platform_type)

        if not survey_platform_class:
            logger.error(
                "Error exchanging code for tokens for: %s", survey_platform_type
            )
            return (
                jsonify(
                    {
                        "message": {
                            "id": "api.ddsurveys.survey_platforms.exchange_code.error",
                            "text": "Error exchanging code for tokens",
                        },
                    }
                ),
                400,
            )

        app_credentials: dict[str, str] = survey_platform_class.get_app_credentials()

        provider_instance = survey_platform_class(
            **app_credentials,
            redirect_uri=survey_platform_class.get_redirect_uri(),
        )

        # Exchange the code for an access token
        response = provider_instance.request_token(code)

        if response["success"]:
            logger.info(
                "Successfully exchanged code for tokens for: %s", survey_platform_type
            )
            return (
                jsonify(
                    {
                        "message": {
                            "id": "api.ddsurveys.survey_platforms.exchange_code.success",
                            "text": "Successfully exchanged code for tokens",
                        },
                        "entity": response,
                    }
                ),
                200,
            )
        else:
            logger.error(
                "Error exchanging code for tokens for: %s", survey_platform_type
            )
            return (
                jsonify(
                    {
                        "message": {
                            "id": response["message_id"],
                            "text": "Full scope not granted",
                        },
                    }
                ),
                500,
            )
    except Exception:
        logger.exception("Error exchanging code for tokens for: %s\n", survey_platform_type)
        return (
            jsonify(
                {
                    "message": {
                        "id": "api.ddsurveys.survey_platforms.exchange_code.error",
                        "text": "Error exchanging code for tokens",
                    },
                }
            ),
            500,
        )
