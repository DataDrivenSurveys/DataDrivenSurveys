#!/usr/bin/env python3
"""Created on 2023-04-27 13:48.

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
@author: Stefan Teofanovic (stefan.teofanovic@heig-vd.ch)
"""
import functools
import os
import re
from datetime import datetime

import requests

from ddsurveys.get_logger import get_logger
from ddsurveys.survey_platforms.qualtrics.api.exceptions import (
    AuthorizationError,
    BadRequestError,
    MissingAPIToken,
    NotFoundError,
    ServerError,
    UnhandledStatusCodeError,
)

logger = get_logger(__name__)


class QualtricsDataCenter:
    """References:
    ----------
    `API Documentation <https://api.qualtrics.com/60d24f6897737-qualtrics-survey-api>`_
    """

    data_centers = {
        "Canadian Data Center": "https://yul1.qualtrics.com/API/v3",
        "Washington, DC Area Data Center": "https://iad1.qualtrics.com/API/v3",
        "San Jose, California Data Center": "https://sjc1.qualtrics.com/API/v3",
        "European Union Data Center": "https://fra1.qualtrics.com/API/v3",
        "London United Kingdom Data Center": "https://lhr1.qualtrics.com/API/v3",
        "Sydney Australia Data Center": "https://syd1.qualtrics.com/API/v3",
        "Singapore Data Center": "https://sin1.qualtrics.com/API/v3",
        "Tokyo, Japan Data Center": "https://hnd1.qualtrics.com/API/v3",
        "US Government Data Center": "https://gov1.qualtrics.com/API/v3",
        "Mock Server": "https://stoplight.io/mocks/qualtricsv2/publicapidocs/60936",
    }

    extra_keys = {
        "Canadian Data Center": ["CA", "Canada"],
        "Washington, DC Area Data Center": ["Washington", "DC", "US East"],
        "San Jose, California Data Center": ["San Jose", "California", "US West"],
        "European Union Data Center": ["EU"],
        "London United Kingdom Data Center": ["London", "UK"],
        "Sydney Australia Data Center": ["Sydney", "Australia", "AU"],
        "Singapore Data Center": ["Singapore", "SG"],
        "Tokyo, Japan Data Center": ["Tokyo", "JP", "Japan"],
        "US Government Data Center": ["US Gov"],
        "Mock Server": ["Mock"],
    }

    @classmethod
    def get_datacenter_url(cls, datacenter_name_or_location: str) -> str:
        key = None
        for datacenter_name, abbreviations in cls.extra_keys.items():
            if (
                datacenter_name_or_location == datacenter_name
                or datacenter_name_or_location in abbreviations
            ):
                key = datacenter_name
                break
        if key is None:
            msg = (
                f"Could not identify the requested datacenter: {datacenter_name_or_location}\n"
                f"Here is a list of complete datacenter names and abbreviations to select them:\n"
                f"{cls.extra_keys}"
            )
            raise ValueError(
                msg
            )
        return cls.data_centers[key]


class QualtricsRequests:
    """Wrapper class that simplifies making requests to the Qualtrics API.

    It provides various methods that child classes can use to conveniently make different REST requests.
    """

    _endpoint: str = ""
    _headers: dict[str, str] = {
        "Content-Type": "application/json",
        "X-API-TOKEN": "",
    }

    _re_datacenter_redirect = re.compile(r".*: (.+?\.qualtrics.com)$")

    _session = requests.Session()

    def __init__(
        self,
        api_token: str = "",
        datacenter_location: str = "EU",
        accept_datacenter_redirect: bool = True,
    ) -> None:
        self.accept_datacenter_redirect: bool = accept_datacenter_redirect
        self.base_url: str = QualtricsDataCenter.get_datacenter_url(datacenter_location)
        self._api_token: str = ""

        if api_token != "":
            self.api_token = api_token
        else:
            # Try to get token from environment variables
            self.api_token = os.environ.get("QUALTRICS_API_TOKEN", "")

        if not self.api_token:
            raise MissingAPIToken

        self.headers.update(
            {
                "X-API-TOKEN": self.api_token,
            }
        )

        self.session.headers.update(self.headers)

    def update_datacenter_on_redirect(
        self, response: requests.Response
    ) -> requests.Response:
        if self.accept_datacenter_redirect:
            resp_json = response.json()
            redirect_info_str = (
                "Request proxied. For faster response times, use this host instead:"
            )
            if (
                "notice" in resp_json["meta"]
                and redirect_info_str in resp_json["meta"]["notice"]
            ):
                match = self.__class__._re_datacenter_redirect.match(
                    resp_json["meta"]["notice"]
                )
                if match is not None:
                    self.base_url = f"https://{match.group(1)}/API/v3"
                else:
                    logger.error("Failed to extract the redirected datacenter.")
        return response

    @staticmethod
    def update_datacenter_wrapper(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            return self.update_datacenter_on_redirect(func(self, *args, **kwargs))

        return wrapper

    @staticmethod
    def handle_response_status(acceptable_statuses: tuple = (200, 201, 202, 204)):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                resp: requests.Response = func(*args, **kwargs)
                if resp.status_code not in acceptable_statuses:
                    if resp.status_code == 400:
                        raise BadRequestError(resp)
                    elif resp.status_code == 404:
                        raise NotFoundError(resp)
                    elif resp.status_code == 401:
                        raise AuthorizationError(resp)
                    elif resp.status_code == 403:
                        raise PermissionError(resp)
                    elif resp.status_code >= 500:
                        raise ServerError(resp)
                    else:
                        raise UnhandledStatusCodeError(resp)
                return resp

            return wrapper

        return decorator

    @property
    def api_token(self) -> str:
        return self._api_token

    @api_token.setter
    def api_token(self, value: str) -> None:
        self._api_token = value

    @property
    def headers(self) -> dict:
        return QualtricsRequests._headers

    @headers.setter
    def headers(self, value: dict) -> None:
        QualtricsRequests._headers = value

    @property
    def endpoint(self) -> str:
        return self.__class__._endpoint

    @property
    def session(self) -> requests.Session:
        return QualtricsRequests._session

    @handle_response_status()
    @update_datacenter_wrapper
    def get(
        self, endpoint=None, data=None, json=None, *args, **kwargs
    ) -> requests.Response:
        endpoint = endpoint or self.endpoint
        return self.session.get(
            f"{self.base_url}/{endpoint}", data=data, json=json, *args, **kwargs
        )


    @handle_response_status()
    @update_datacenter_wrapper
    def put(
        self, endpoint=None, data=None, json=None, *args, **kwargs
    ) -> requests.Response:
        endpoint = endpoint or self.endpoint
        return self.session.put(
            f"{self.base_url}/{endpoint}", data=data, json=json, *args, **kwargs
        )


    @handle_response_status()
    @update_datacenter_wrapper
    def post(
        self, endpoint=None, data=None, json=None, *args, **kwargs
    ) -> requests.Response:
        endpoint = endpoint or self.endpoint
        return self.session.post(
            f"{self.base_url}/{endpoint}", data=data, json=json, *args, **kwargs
        )


    @handle_response_status()
    @update_datacenter_wrapper
    def delete(
        self, endpoint=None, data=None, json=None, *args, **kwargs
    ) -> requests.Response:
        endpoint = endpoint or self.endpoint
        return self.session.delete(
            f"{self.base_url}/{endpoint}", data=data, json=json, *args, **kwargs
        )


    @staticmethod
    def to_iso8601(dt: datetime) -> str:
        return dt.strftime("%Y-%m-%dT%H:%M:%sZ")


if __name__ == "__main__":
    q_requests = QualtricsRequests("", "EU")
    data = {
        "SurveyName": "api-test-survey",
        "Language": "EN",
        "ProjectCategory": "CORE",
    }

    r = q_requests.get("survey-definitions/SV_e3OyJozlSuFHdzw")
