from unittest.mock import Mock, patch

import pytest

from ddsurveys.survey_platforms.qualtrics.api import SurveysAPI

dummy_qualtrics_active_survey = {
    "SurveyID": "SV_123456789",
    "SurveyName": "Mock Survey Name",
    "SurveyStatus": "Active",
    "BrandBaseURL": "https://unil.qualtrics.com/jfe/form/SV_123456789",
}


@pytest.fixture
def mock_surveys_api():
    """A pytest fixture that mocks the SurveysAPI class for testing purposes.

    This fixture patches three methods of the SurveysAPI class:
    - survey_exists: Always returns True
    - get_survey: Returns a mock response with dummy survey data
    - create_survey: Returns a mock response with dummy survey data

    The fixture uses the context manager to apply the patches and yields control
    back to the test function. After the test function completes, the patches
    are automatically removed.

    Returns:
    None
        This fixture doesn't return a value, but sets up the mocked environment
        for the test function to use.
    """
    with (
        patch.object(SurveysAPI, "survey_exists", return_value=True),
        patch.object(SurveysAPI, "get_survey") as mock_get_survey,
        patch.object(SurveysAPI, "create_survey") as mock_create_survey,
    ):
        # Mock response for get_survey
        mock_response_get = Mock()
        mock_response_get.json.return_value = {"result": dummy_qualtrics_active_survey}
        mock_get_survey.return_value = mock_response_get

        # Mock response for create_survey
        mock_response_create = Mock()
        mock_response_create.json.return_value = {"result": dummy_qualtrics_active_survey}
        mock_create_survey.return_value = mock_response_create

        yield
