import json
from http import HTTPStatus

import pytest

from tests.ddsurveys.api.mocks import mock_surveys_api
from tests.ddsurveys.api.utils.auth import authenticate_test_user, users

project_endpoint = "/projects/"
fields_valid = [
    {"name": "survey_id", "value": "survey_id"},
    {"name": "survey_platform_api_key", "value": "survey_platform_api_key"},
]

fields_missing_survey_id = fields_valid[1:]
fields_missing_survey_platform_api_key = fields_valid[:1]


@pytest.mark.parametrize(
    ("name", "use_existing_survey", "survey_platform_name", "fields", "expected_status_code", "expected_message_id"),
    [
        (
            "Test Project",
            False,
            "qualtrics",
            fields_valid,
            HTTPStatus.CREATED,
            "api.projects.project_created_successfully",
        ),
        (
            "Test Project",
            False,
            "qualtrics",
            fields_missing_survey_id,
            HTTPStatus.CREATED,
            "api.projects.project_created_successfully",
        ),
        (
            "Test Project",
            False,
            "qualtrics",
            fields_missing_survey_platform_api_key,
            HTTPStatus.BAD_REQUEST,
            "api.ddsurveys.survey_platforms.bases.survey_platform_api_key.missing",
        ),
        (
            "Test Project",
            True,
            "qualtrics",
            fields_valid,
            HTTPStatus.CREATED,
            "api.projects.project_created_successfully",
        ),
        (None, True, "qualtrics", fields_valid, HTTPStatus.CREATED, "api.projects.project_created_successfully"),
        (
            None,
            True,
            "qualtrics",
            fields_missing_survey_id,
            HTTPStatus.BAD_REQUEST,
            "api.ddsurveys.survey_platforms.bases.survey_id.missing",
        ),
        (
            None,
            True,
            "qualtrics",
            fields_missing_survey_platform_api_key,
            HTTPStatus.BAD_REQUEST,
            "api.ddsurveys.survey_platforms.bases.survey_platform_api_key.missing",
        ),
        ("Test Project", False, "unknown", fields_valid, HTTPStatus.BAD_REQUEST, "api.survey.platform_not_supported"),
    ],
)
def test_create_project(
    *,
    client,
    mock_surveys_api,
    name: str,
    use_existing_survey: bool,
    survey_platform_name: str,
    fields: list[dict[str, str]],
    expected_status_code: int,
    expected_message_id: str,
):
    """Test the /projects/ [POST] endpoint.

    Using parametrize to test various scenarios.
    """
    headers = authenticate_test_user(client=client, test_user=users.get("jane_doe"))

    project_data = {
        "use_existing_survey": use_existing_survey,
        "name": name,
        "survey_platform_name": survey_platform_name,
        "fields": fields,
    }

    response = client.post(
        project_endpoint, headers=headers, data=json.dumps(project_data), content_type="application/json"
    )

    assert (
        response.status_code == expected_status_code
    ), f"The status code was not as expected. Expected: {expected_status_code}, Actual: {response.status_code}"
    assert json.loads(response.data)["message"]["id"] == expected_message_id, (
        f"The message id was not as expected. Expected: {expected_message_id}, Actual: "
        f"{json.loads(response.data)['message']['id']}"
    )
