#!/usr/bin/env python3
"""Created on 2023-04-27 16:02.

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
@author: Stefan Teofanovic (stefan.teofanovic@heig-vd.ch)
"""
from requests import Response


def extract_qualtrics_error(resp: Response) -> str:
    json_meta = resp.json()["meta"]
    status = json_meta["httpStatus"]

    # Extract error message
    json_error = json_meta.get("error", {})
    error_message = json_error.get("errorMessage", "")
    specific_error = json_error.get("messsage", "")
    detailed_errors = []

    if "validationErrors" in json_error:
        for error in json_error["validationErrors"]:
            text = (
                f"{error['Context']} had the value '{error['Value']}', which failed to be validated with the "
                f"following message:\n"
                f"{error['Description']}"
            )
            detailed_errors.append(text)

    detailed_errors = "\n".join(detailed_errors)

    return f"Status: '{status}', Error message: '{error_message}' due to a '{specific_error}'. Detailed errors:\n{detailed_errors}"


class MissingAPIToken(Exception):
    _default_message = (
        "No Qualtrics token was passed. Pass it as the 'api_token' constructor parameter, or set the "
        "'QUALTRICS_API_TOKEN' environment variable equal to it."
    )

    def __init__(self, message=None):
        if message is None:
            message = self.__class__._default_message
        super().__init__(message)


class MissingMailingListID(Exception):
    _default_message = "No _survey_id was passed and self._survey_id is None.\nPass a _survey_id or set self._survey_id"

    def __init__(self, message=None):
        if message is None:
            message = self.__class__._default_message
        super().__init__(message)


class MissingSurveyID(Exception):
    _default_message = "No _survey_id was passed and self._survey_id is None.\nPass a _survey_id or set self._survey_id"

    def __init__(self, message=None):
        if message is None:
            message = self.__class__._default_message
        super().__init__(message)


class FailedQualtricsRequest(Exception):
    def __init__(self, resp: Response, message: str = ""):
        qualtrics_error = extract_qualtrics_error(resp)
        msg = f"Request failed with status code: {resp.status_code}.\n"
        if message != "":
            msg += f"{message}\n"
        msg += f"Qualtrics error message:\n{qualtrics_error}"
        super().__init__(msg)


class BadRequestError(FailedQualtricsRequest):
    """Exception raised when a HTTPStatus.BAD_REQUEST Bad Request error occurs."""

    def __init__(self, resp: Response):
        message = "Possible cause: Your request is malformed. Check the syntax and structure of your request."
        super().__init__(resp, message)


class AuthorizationError(FailedQualtricsRequest):
    """Exception raised when a HTTPStatus.UNAUTHORIZED Unauthorized error occurs."""

    def __init__(self, resp: Response):
        message = "Possible cause: You're not authenticated or don't have permission to access the requested resource."
        super().__init__(resp, message)


class NotFoundError(FailedQualtricsRequest):
    """Exception raised when a HTTPStatus.NOT_FOUND Not Found error occurs."""

    def __init__(self, resp: Response):
        message = "Possible cause: The requested resource could not be found."
        super().__init__(resp, message)


class ServerError(FailedQualtricsRequest):
    """Exception raised when a HTTPStatus.INTERNAL_SERVER_ERROR Internal Server Error occurs."""

    def __init__(self, resp: Response):
        message = "Possible cause: The server encountered an internal error."
        super().__init__(resp, message)


class UnhandledStatusCodeError(FailedQualtricsRequest):
    """Exception raised when an unhandled status code is returned."""

    def __init__(self, resp: Response):
        super().__init__(resp)
