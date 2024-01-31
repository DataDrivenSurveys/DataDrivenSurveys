#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest

from ddsurveys.survey_platforms.qualtrics.api import SurveysAPI
from unittest.mock import patch, Mock

dummy_qualtrics_active_survey = {
    "SurveyID": "SV_123456789",
    "SurveyName": "Mock Survey Name",
    "SurveyStatus": "Active"
}


@pytest.fixture
def mock_surveys_api():
    with patch.object(SurveysAPI, 'survey_exists', return_value=True) as mock_survey_exists, \
         patch.object(SurveysAPI, 'get_survey') as mock_get_survey, \
         patch.object(SurveysAPI, 'create_survey') as mock_create_survey:

        # Mock response for get_survey
        mock_response_get = Mock()
        mock_response_get.json.return_value = {"result": dummy_qualtrics_active_survey}
        mock_get_survey.return_value = mock_response_get

        # Mock response for create_survey
        mock_response_create = Mock()
        mock_response_create.json.return_value = {"result": dummy_qualtrics_active_survey}
        mock_create_survey.return_value = mock_response_create

        yield
