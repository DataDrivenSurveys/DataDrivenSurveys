#!/usr/bin/env python3
"""Created on 2023-05-05 11:14.

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
@author: Stefan Teofanovic (stefan.teofanovic@heig-vd.ch)
"""

from http import HTTPStatus

import pytest

from ddsurveys.survey_platforms.qualtrics import SurveysAPI


@pytest.fixture(scope="class")
def survey_api():
    return SurveysAPI()


@pytest.fixture(scope="class")
def survey_id():
    return "SV_dd3PBVMgHt4UcTA"


@pytest.mark.qualtrics
class TestQualtricsSurveyAPI:
    def test_create_delete_survey(self, survey_api, survey_id):
        resp = survey_api.create_survey("Test Surveys API")
        created_survey_id = resp.json()["result"]["SurveyID"]
        assert resp.status_code == HTTPStatus.OK

        resp2 = survey_api.delete_survey(created_survey_id)
        assert resp2.status_code == HTTPStatus.OK

    def test_get_survey(self, survey_api, survey_id):
        resp = survey_api.get_survey(survey_id)
        assert resp.status_code == HTTPStatus.OK

    def test_get_survey_metadata(self, survey_api, survey_id):
        resp = survey_api.get_survey_metadata(survey_id)
        assert resp.status_code == HTTPStatus.OK

    def test_get_flow(self, survey_api, survey_id):
        resp = survey_api.get_flow(survey_id)
        assert resp.status_code == HTTPStatus.OK
