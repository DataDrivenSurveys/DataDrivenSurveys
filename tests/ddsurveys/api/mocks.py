#!/usr/bin/env python3

from unittest.mock import Mock, patch

import pytest

from ddsurveys.survey_platforms.qualtrics.api import SurveysAPI

dummy_qualtrics_active_survey = {
    "SurveyID": "SV_123456789",
    "SurveyName": "Mock Survey Name",
    "SurveyStatus": "Active",
    "BrandBaseURL": "https://unil.qualtrics.com/jfe/form/SV_123456789"
}


@pytest.fixture
def mock_surveys_api():
    with patch.object(SurveysAPI, 'survey_exists', return_value=True), \
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
