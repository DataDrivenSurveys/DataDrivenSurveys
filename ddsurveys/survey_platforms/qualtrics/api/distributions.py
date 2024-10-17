#!/usr/bin/env python3
"""Created on 2023-06-05 14:42.

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
@author: Stefan Teofanovic (stefan.teofanovic@heig-vd.ch)
"""
import functools
from datetime import date

from dateutil.relativedelta import relativedelta

from ddsurveys.get_logger import get_logger
from ddsurveys.survey_platforms.qualtrics.api.exceptions import MissingMailingListID, MissingSurveyID
from ddsurveys.survey_platforms.qualtrics.api.qualtrics_requests import QualtricsRequests

logger = get_logger(__name__)


class DistributionsAPI(QualtricsRequests):
    _endpoint = "distributions"

    def __init__(
        self,
        api_token="",
        data_center_location: str = "EU",
        mailing_list_id: str | None = None,
        *,
        accept_data_center_redirect: bool = True,
    ):
        super().__init__(api_token=api_token, data_center_location=data_center_location, accept_data_center_redirect=accept_data_center_redirect)
        self.mailing_list_id = mailing_list_id

    @staticmethod
    def directory_id_wrapper(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            args_0 = args[0] if len(args) > 0 else None
            mailing_list_id = args_0 or kwargs.get("_survey_id") or self.mailing_list_id
            if mailing_list_id is None:
                raise MissingMailingListID
            self.mailing_list_id = mailing_list_id
            return func(self, *args, **kwargs)

        return wrapper

    @staticmethod
    def survey_id_wrapper(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            args_0 = args[0] if len(args) > 0 else None
            survey_id = args_0 or kwargs.get("survey_id") or self._survey_id
            if survey_id is None:
                raise MissingSurveyID
            self._survey_id = survey_id
            return func(self, *args, **kwargs)

        return wrapper

    def get_user_id(self):
        return self.get("whoami").json()["result"]["userId"]

    def list_directories(self):
        return self.get("directories").json()["result"]["elements"]

    def get_first_directory_id(self):
        return self.list_directories()[0]["directoryId"]

    def create_mailing_list(
        self,
        directory_id: str,
        name: str,
        owner_id: str,
        prioritize_list_metadata: bool = True,
    ):
        payload = {
            "name": name,
            "ownerId": owner_id,
            "prioritizeListMetadata": prioritize_list_metadata,
        }
        return self.post(f"directories/{directory_id}/mailinglists", json=payload)

    def create_contact(
        self,
        directory_id: str,
        mailing_list_id: str,
        embedded_data: dict,
        first_name: str = "",
        last_name: str = "",
        email: str = "",
        phone: str = "",
        ext_ref: str = "",
        language: str = "",
        unsubscribed: bool = False,
    ):

        data = {}
        for k, v in embedded_data.items():
            if isinstance(v, bool):
                data[k] = str(v)
            elif v is None:
                # Ensure the variable is uploaded. Qualtrics does not save embedded data if they have a value of
                # None (null in JSON format) or if it's empty string.
                data[k] = "None"
            else:
                data[k] = v

        payload = {"embeddedData": data, "unsubscribed": unsubscribed}

        if first_name != "":
            payload["firstName"] = first_name

        if last_name != "":
            payload["lastName"] = last_name

        if email != "":
            payload["email"] = email

        if phone != "":
            payload["phone"] = phone

        if ext_ref != "":
            payload["extRef"] = ext_ref

        if language != "":
            payload["detected_language"] = language

        resp = self.post(
            f"directories/{directory_id}/mailinglists/{mailing_list_id}/contacts",
            json=payload,
        )

        return resp.json()["result"]

    def create_unique_distribution_link(
        self, survey_id: str, mailing_list_id: str, contact_lookup_id: str
    ) -> str:
        one_month = date.today() + relativedelta(months=+1)

        payload = {
            "surveyId": survey_id,
            "linkType": "Individual",
            "description": "distribution " + one_month.strftime("%Y-%m-%d %H:%M:%S"),
            "action": "CreateDistribution",
            "expirationDate": one_month.strftime("%Y-%m-%d %H:%M:%S"),
            "mailingListId": mailing_list_id,
            "contactId": contact_lookup_id,
        }

        resp = self.post("distributions", json=payload)

        distribution_id = resp.json()["result"]["id"]

        resp = self.get(f"distributions/{distribution_id}/links?surveyId={survey_id}")

        return resp.json()["result"]["elements"][0]["link"]

    def get_preview_survey_url(self, survey_id: str, mailing_list_id: str) -> str:
        payload = {"surveyId": survey_id, "mailingListId": mailing_list_id}
        resp = self.post("distributions/preview", json=payload)
        return resp.json()["result"]["previewLink"]
