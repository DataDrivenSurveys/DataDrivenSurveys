#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2023-04-26 12:18

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)

References
----------
`Qualtrics Survey API Documentation <https://api.qualtrics.com/60d24f6897737-qualtrics-survey-api>`_
"""
import functools
import re
from datetime import datetime
from typing import Optional

import requests

from ddsurveys.get_logger import get_logger
from .qualtrics_requests import QualtricsRequests
from .exceptions import MissingSurveyID, FailedQualtricsRequest, BadRequestError, AuthorizationError, NotFoundError, ServerError, UnhandledStatusCodeError


logger = get_logger(__name__)


class SurveysAPI(QualtricsRequests):
    """
    References
    ----------
    `API Documentation <https://api.qualtrics.com/41ff4dba22c75-create-survey>`_
    """
    # TODO: Convert methods to return results or raise exceptions if requests fail.
    _endpoint = "survey-definitions"
    _re_survey_id = re.compile(r'^SV_[a-zA-Z0-9]{11,15}$')

    def __init__(self, api_token: str = "", datacenter_location: str = "EU", accept_datacenter_redirect: bool = True,
                 survey_id: Optional[str] = None):
        super().__init__(api_token, datacenter_location, accept_datacenter_redirect)
        self._survey_id = survey_id

    @property
    def survey_url(self) -> str:
        if self._survey_id is not None:
            return f"{self.base_url}/{self._survey_id}"
        else:
            logger.warning("No survey id is currently set. Set it by setting the `survey_id` property.")
            return f"{self.base_url}/"

    @property
    def survey_id(self):
        return self._survey_id

    @survey_id.setter
    def survey_id(self, value):
        assert self.__class__._re_survey_id.match(value) is not None
        self._survey_id = value

    def get_survey_url(self, survey_id: Optional[str] = None):
        survey_id = survey_id or self.survey_id
        if survey_id is None:
            raise MissingSurveyID("No survey id is currently set. Set it by setting the `survey_id` property.")

        survey = self.get_survey(survey_id)
        base_url = survey.json()["result"]["BrandBaseURL"]
        return f"{base_url}/survey-builder/{survey_id}/edit?Tab=Builder"

    @staticmethod
    def survey_id_wrapper(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            if len(args) > 0:
                args_0 = args[0]
            else:
                args_0 = None
            survey_id = args_0 or kwargs.get("survey_id") or self._survey_id
            if survey_id is None:
                raise MissingSurveyID()
            self._survey_id = survey_id
            return func(self, *args, **kwargs)
        return wrapper

    def create_survey(self, survey_name: str, language: str = "EN",
                      project_category: str = "CORE") -> requests.Response:
        """
        Creates a new survey on Qualtrics.

        Parameters
        ----------
        survey_name
        language
        project_category

        Returns
        -------

        References
        ----------
        `API Documentation <https://api.qualtrics.com/41ff4dba22c75-create-survey>`_
        """
        json_data = {"SurveyName": survey_name, "Language": language, "ProjectCategory": project_category}
        return self.post(json=json_data)

    def survey_exists(self, survey_id: str) -> bool:
        """
        Checks if a survey exists in Qualtrics.

        Parameters
        ----------
        survey_id

        Returns
        -------
        Boolean - True if the survey exists, False otherwise.
        """
        try:
            # We use the get method provided by the base class
            response = self.get(endpoint=f"surveys/{survey_id}")

            # Check if the response was successful
            if response.status_code == 200:
                return True
        except FailedQualtricsRequest:
            pass

        return False

    @survey_id_wrapper
    def get_survey(self, survey_id: str = None, get_qsf_format: bool = False) -> requests.Response:
        """
        Gets the survey information from the Qualtrics platform for a given survey.

        Parameters
        ----------
        survey_id
        get_qsf_format

        Returns
        -------


        References
        ----------
        `API Documentation <https://api.qualtrics.com/9d0928392673d-get-survey>`_
        """
        params = dict()
        if get_qsf_format:
            params = {"format": "qsf"}

        return self.get(f"{self.endpoint}/{survey_id}", params=params)

    @survey_id_wrapper
    def delete_survey(self, survey_id: str = None) -> requests.Response:
        """
        Deletes a given survey on the Qualtrics platform.

        Parameters
        ----------
        survey_id

        Returns
        -------

        References
        ----------
        `API Documentation <https://api.qualtrics.com/6d155f86c65ae-delete-survey>`_
        """
        return self.delete(f"{self.endpoint}/{survey_id}")

    @survey_id_wrapper
    def get_survey_metadata(self, survey_id: str) -> requests.Response:
        """

        Parameters
        ----------
        survey_id

        Returns
        -------

        References
        ----------
        `API Documentation <https://api.qualtrics.com/a92bfbc7e58fe-get-survey-metadata>`_
        """
        return self.get(f"{self.endpoint}/{survey_id}/metadata")

    @survey_id_wrapper
    def update_metadata(self, survey_id: str, survey_name: str, survey_status: str,
                        survey_start_date: datetime, survey_expiration_date: datetime,
                        survey_description: Optional[str] = None) -> requests.Response:
        """

        Parameters
        ----------
        survey_id
        survey_name
        survey_status
        survey_start_date
        survey_expiration_date
        survey_description

        Returns
        -------

        References
        ----------
        `API Documentation <https://api.qualtrics.com/ae7f40bbcb91a-update-metadata>`_
        """
        assert survey_status in ["Active", "Inactive"]
        assert isinstance(survey_start_date, datetime) and isinstance(survey_expiration_date, datetime)

        survey_id = survey_id or self._survey_id
        payload = {
            "SurveyName": survey_name,
            "SurveyDescription": survey_description,
            "SurveyStatus": survey_status,
            "SurveyStartDate": self.to_iso8601(survey_start_date),
            "SurveyExpirationDate": self.to_iso8601(survey_expiration_date)
        }

        return self.put(f"{self.endpoint}/{survey_id}/metadata", json=payload)

    # Survey Flows
    @survey_id_wrapper
    def get_flow(self, survey_id: str = None) -> requests.Response:
        """

        Parameters
        ----------
        survey_id

        Returns
        -------

        References
        ----------
        `API Documentation <https://api.qualtrics.com/773d3d5865ca9-get-flow>`_
        """
        return self.get(f"{self.endpoint}/{survey_id}/flow")

    @survey_id_wrapper
    def update_flow(self, survey_id: str = None, flow: dict = None) -> requests.Response:
        """
        Update a survey flow.

        The previous flow is overwritten by the new one. If updating an existing survey, make sure to use a flow that
        contains all the previous blocks to avoid deleting everything except for the custom variables block.


        Arguments:
            survey_id
            flow

        Returns:

        References:
            `API Documentation <https://api.qualtrics.com/be14598374903-update-flow>`_
        """
        return self.put(f"{self.endpoint}/{survey_id}/flow", json=flow)

    # @survey_id_wrapper
    # def update_flow_element_definition(self, _survey_id: str = None, flow: Union[Flow, dict, list] = None) -> requests.Response:
    #     """
    #
    #     Parameters
    #     ----------
    #     _survey_id
    #     flow
    #
    #     Returns
    #     -------
    #
    #     References
    #     ----------
    #     `API Documentation <https://api.qualtrics.com/be14598374903-update-flow>`_
    #     """
    #     if isinstance(flow, Flow):
    #         flow = [flow._custom_variables]
    #     elif isinstance(flow, dict):
    #         flow = [flow]
    #     return self.put(f"{self.endpoint}/{_survey_id}/flow", json=flow)


if __name__ == "__main__":
    token = ""
    surveys = SurveysAPI(token)
    # qrequests = QualtricsRequests(api_token)

    # data = {"SurveyName": "api-test-survey",
    #         "Language": "EN",
    #         "ProjectCategory": "CORE"}

    # resp = qrequests.post("survey-definitions", json=data)

    # r = resp

    # print(r.json())

