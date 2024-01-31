#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# test_data_provider.py
# (.venv) C:\UNIL\DataDrivenSurveys\ddsurveys>python -m pytest
import pytest

from ddsurveys.data_providers.bases import DataProvider
from ddsurveys.data_providers.fitbit import FitbitDataProvider
from ddsurveys.data_providers.instagram import InstagramDataProvider


from ..utils.mock_data import fitbit_mock_data, instagram_mock_data
from ..utils.functions import generate_builtin_variables, generate_custom_variables, variable_to_qualname, validate_url

from flask import Flask

app = Flask(__name__)

REGISTERED_DATAPROVIDERS = [k for k in DataProvider.get_registry().keys()]


@pytest.mark.parametrize('provider_name', REGISTERED_DATAPROVIDERS)
def test_get_redirect_uri(provider_name, monkeypatch):
    """Test the get_redirect_uri method."""
    monkeypatch.setenv("FRONTEND_URL", "http://testurl.com")

    provider_class = DataProvider.get_class_by_value(provider_name.lower())

    assert provider_class.get_redirect_uri() == "http://testurl.com/dist/redirect/" + provider_name.lower(), f"The redirect URI for {provider_name} is incorrect."


VARIABLES = [
    {"enabled": True, "data_provider": "fitbit"},
    {"enabled": False, "data_provider": "fitbit"},
    {"enabled": False, "data_provider": "instagram"},
    {"enabled": True, "data_provider": "instagram"},
    {"enabled": True, "data_provider": "github"},
    {"enabled": False, "data_provider": "github"},
]

EXPECTED_RESULTS = {
    'Fitbit': [
        {"enabled": True, "data_provider": "fitbit"}
    ],
    'Instagram': [
        {"enabled": True, "data_provider": "instagram"}
    ],
    'GitHub': [
        {"enabled": True, "data_provider": "github"}
    ],
}

PARAMETERIZED_PROVIDERS = [(provider, EXPECTED_RESULTS[provider]) for provider in REGISTERED_DATAPROVIDERS]

@pytest.mark.parametrize("provider_name, expected_result", PARAMETERIZED_PROVIDERS)
def test_select_relevant_variables(provider_name, expected_result):
    """Test the select_relevant_variables method."""
    # Access the data_provider fixture using the provider name.
    data_provider = DataProvider.get_class_by_value(provider_name.lower())()

    result = data_provider.select_relevant_variables(VARIABLES)
    assert result == expected_result, f"The {provider_name} DataProvider should return the expected variables."


"""
 Test the UI feeder methods.
 DataProvider.get_all_form_fields()
"""
def test_get_all_form_fields():
    """
    Validate the retrieval of all form fields for DataProviders.
    """

    # Retrieve the form fields using the superclass method
    data_provider_data = DataProvider.get_all_form_fields()

    # Define the required keys for the main structure, fields, and inside each field
    main_keys = ['fields', 'instructions', 'label', 'value']
    field_keys = ['helper_text', 'label', 'name', 'required', 'type']

    for provider_form in data_provider_data:
        # Check main structure
        provider_name = provider_form['value'].lower()

        for key in main_keys:
            assert key in provider_form, f"Key {key} missing in provider {provider_form.get('label', 'Unknown')}."
            assert provider_form[key], f"Key {key} in provider {provider_form.get('label', 'Unknown')} has empty or None value."

        # Check if 'instructions' follow the expected pattern
        expected_instruction_pattern = f"api.ddsurveys.data_providers.{provider_name}.instructions.text"
        assert provider_form['instructions'] == expected_instruction_pattern, \
            f"Instructions pattern mismatch for provider {provider_name}. Expected: {expected_instruction_pattern}, Got: {provider_form['instructions']}."

        # Check fields
        for field in provider_form['fields']:
            for f_key in field_keys:
                assert f_key in field, f"Key {f_key} missing in field {field.get('name', 'Unknown')} of provider {provider_form.get('label', 'Unknown')}."
                assert field[f_key], f"Key {f_key} in field {field.get('name', 'Unknown')} of provider {provider_form.get('label', 'Unknown')} has empty or None value."

            # Check if type is one of the known types, e.g., "text". Add more if needed.
            assert field['type'] in ['text'], f"Unknown field type {field['type']} in field {field.get('name', 'Unknown')} of provider {provider_form.get('label', 'Unknown')}."

            # Check if 'label' and 'helper_text' follow the expected pattern
            expected_label_pattern = f"api.ddsurveys.data_providers.{provider_name}.{field['name']}.label"
            expected_helper_pattern = f"api.ddsurveys.data_providers.{provider_name}.{field['name']}.helper_text"

            assert field['label'] == expected_label_pattern, \
                f"Label pattern mismatch in field {field['name']} of provider {provider_name}. Expected: {expected_label_pattern}, Got: {field['label']}."

            assert field['helper_text'] == expected_helper_pattern, \
                f"Helper text pattern mismatch in field {field['name']} of provider {provider_name}. Expected: {expected_helper_pattern}, Got: {field['helper_text']}."

"""
    Test the UI feeder methods.
    That the required form_fields for each data providers are present.
    Using parametrize to test all data providers.
"""
# Fields that are required for each DataProvider
# This dictionary is structured with the DataProvider name as the key and a list of required field names as the value
REQUIRED_FIELDS = {
    'Fitbit': ['client_id', 'client_secret'],
    'Instagram': ['client_id', 'client_secret']
    # ... Add other providers and their required fields as needed
}

@pytest.mark.parametrize('provider_name', REGISTERED_DATAPROVIDERS)
def test_data_provider_required_fields(provider_name):
    """
    Validate the required fields for each DataProvider.
    Checks that the required form fields for each data providers are present, well-defined, and have non-empty or non-None values.
    """
    form_fields = DataProvider.get_all_form_fields()
    lower_name = provider_name.lower()

    # Extract the data provider's fields from the list
    provider_data = next((item for item in form_fields if item["value"] == lower_name), None)

    assert provider_data, f"Missing data provider information for {provider_name}."

    provided_field_names = [field['name'] for field in provider_data['fields']]

    field_structure_keys = ['helper_text', 'label', 'name', 'required', 'type']

    for required_field in REQUIRED_FIELDS.get(provider_name, []):
        assert required_field in provided_field_names, f"Missing required field {required_field} for {provider_name}."

        # Check if the field is well-defined (i.e., has a non-empty or non-None value)
        field_data = next((field for field in provider_data['fields'] if field["name"] == required_field), None)
        assert field_data, f"Field {required_field} for {provider_name} is not well-defined."
        for key in field_structure_keys:
            assert key in field_data, f"Key {key} missing in field {required_field} of provider {provider_name}."
            assert field_data[key], f"Key {key} in field {required_field} of provider {provider_name} has empty or None value."



"""
Testing the builtin variables of each registered data provider.
"""
# Only need the provider_name from the registry for this test
@pytest.mark.parametrize("provider_name", REGISTERED_DATAPROVIDERS)
def test_builtin_variables(provider_name):
    provider_class = DataProvider.get_class_by_value(provider_name.lower())
    data_provider = provider_class()  # Assuming you instantiate the class here

    builtin_variables = data_provider.get_builtin_variables()

    assert len(builtin_variables) > 0, f"{provider_name} should have at least one builtin variable."

    required_fields = [
        'label', 'name', 'description', 'data_type', 'category',
        'qualified_name', 'data_provider', 'test_value_placeholder',
        'info', 'type'
    ]

    for variable in builtin_variables:
        var_name = variable.get("name", "Unknown variable")  # Default to 'Unknown variable' if 'name' isn't present
        for field in required_fields:
            assert field in variable, f"Provider: {provider_name}, Variable: {var_name}, missing key: {field}."
            assert variable[field], f"Provider: {provider_name}, Variable: {var_name}, key: {field} has empty or None value."

        assert variable["type"] == "Builtin", "The type of the builtin variables should be builtin."
        assert variable["qualified_name"] == variable_to_qualname(variable, "builtin"), "The qualified name should be the data provider name concatenated with the variable name."
        assert variable["data_provider"] == provider_name.lower(), f"The data provider of the builtin variables should be {provider_name.lower()}."


@pytest.mark.parametrize(
    "data_provider_class, mock_properties, expected_upload_data",
    [
        (
            FitbitDataProvider,
            {
                'user_profile': fitbit_mock_data["user_profile"],
                'activities_favorite': fitbit_mock_data["activities_favorite"],
                'activities_frequent': fitbit_mock_data["activities_frequent"],
                'activities_recent': fitbit_mock_data["activities_recent"],
                'lifetime_stats': fitbit_mock_data["lifetime_stats"]
            },
            {
                "dds.fitbit.builtin.steps.average.exists": True,
                "dds.fitbit.builtin.steps.average": 8000,
                "dds.fitbit.builtin.steps.highest.exists": True,
                "dds.fitbit.builtin.steps.highest": 30123,
                "dds.fitbit.builtin.activities.by_frequency[1].exists": True,
                "dds.fitbit.builtin.activities.by_frequency[1]": "Walk",
                "dds.fitbit.builtin.activities.by_frequency[2].exists": True,
                "dds.fitbit.builtin.activities.by_frequency[2]": "Sport",
                "dds.fitbit.builtin.activities.by_frequency[3].exists": True,
                "dds.fitbit.builtin.activities.by_frequency[3]": "Outdoor Bike",
                "dds.fitbit.builtin.activities.by_frequency[4].exists": False,
                "dds.fitbit.builtin.activities.by_frequency[4]": None,
                "dds.fitbit.builtin.activities.by_frequency[5].exists": False,
                "dds.fitbit.builtin.activities.by_frequency[5]": None,
                "dds.fitbit.builtin.account.creation_date.exists": True,
                "dds.fitbit.builtin.account.creation_date": "2018-05-05",
                # ... include all other expected key-value pairs here
            }
        ),
        (
            InstagramDataProvider,
            {
                'media_count': instagram_mock_data["media_count"]
            },
            {
                "dds.instagram.builtin.media.media_count.exists": True,
                "dds.instagram.builtin.media.media_count": 1234,
                # ... include all other expected key-value pairs here
            }
        )
    ],
    ids=lambda param: param.name_lower if isinstance(param, type) and issubclass(param, DataProvider) else type(param).__name__
)
def test_data_extraction_builtin_variables(mocker, data_provider_class, mock_properties, expected_upload_data):
    """
    Test the data extraction of the builtin variables for multiple data providers.
    """
    ctx = app.app_context()
    ctx.push()

    # Mock the properties
    for prop, value in mock_properties.items():
        mocker.patch.object(data_provider_class, prop, new_callable=mocker.PropertyMock, return_value=value)

    data_provider_instance = data_provider_class()

    data_provider_type = data_provider_instance.name_lower

    builtin_variables = generate_builtin_variables(data_provider_type)
    custom_variables = generate_custom_variables(data_provider_type)

    data_to_upload = data_provider_instance.calculate_variables(
        project_builtin_variables=builtin_variables,
        project_custom_variables=custom_variables
    )


    # filters keys that contain .builtin
    builtin_data_to_upload = {k: v for k, v in data_to_upload.items() if ".builtin" in k}

    # filters keys that contain .custom
    custom_data_to_upload = {k: v for k, v in data_to_upload.items() if ".custom" in k}

    # count the number of attributes for each custom variable (2 times the number of attributes + the global .exists for the custom variable)
    custom_variables_attributes_count = sum([len(cv["cv_attributes"] * 2) for cv in custom_variables]) + len(custom_variables)

    assert len(builtin_data_to_upload) == len(builtin_variables) * 2, f"Check the total number of builtin variables to upload for {data_provider_type}, including .exists."
    assert len(custom_data_to_upload) == custom_variables_attributes_count, f"Check the total number of custom variables to upload for {data_provider_type}, including .exists."

    for variable in builtin_variables:
        qual_name = variable_to_qualname(variable, "builtin")
        assert qual_name in data_to_upload, f"Check that the variable {qual_name} is in the data to upload for {data_provider_type}."
        assert f"{qual_name}.exists" in data_to_upload, f"Check that the variable {qual_name}.exists is in the data to upload for {data_provider_type}."

    for variable in custom_variables:
        for attribute in variable["cv_attributes"]:
            qual_name = variable_to_qualname(variable, "custom", attribute)
            assert qual_name in data_to_upload, f"Check that the variable {qual_name} is in the data to upload for {data_provider_type}."
            assert f"{qual_name}.exists" in data_to_upload, f"Check that the variable {qual_name}.exists is in the data to upload for {data_provider_type}."

    # Asserting the data_to_upload values
    for key, expected_value in expected_upload_data.items():
        assert data_to_upload.get(key) == expected_value, f"For {data_provider_type}, {key} should be {expected_value}."

    ctx.pop()



@pytest.mark.parametrize("provider_name", REGISTERED_DATAPROVIDERS)
def test_get_used_variables(provider_name):
    """
    Test the get_used_variables method.
    This method is used to present the variables used in the project to the respondent.
    """

    project_buitin_variables = generate_builtin_variables(provider_name.lower())
    project_custom_variables = generate_custom_variables(provider_name.lower())

    used_variables = DataProvider.get_used_variables(
        project_builtin_variables=project_buitin_variables,
        project_custom_variables=project_custom_variables
    )

    for used_variable in used_variables:

        variable = None

        if used_variable.get("type") == "Builtin":

            variable = next((v for v in project_buitin_variables if v.get("qualified_name") == used_variable.get("variable_name")), None)
            assert variable, f"Could not find the builtin variable {used_variable['variable_name']}."
    
            assert used_variable["data_provider"] == provider_name.lower(), f"The data provider of the used variables should be {provider_name}."
            
            qual_name = variable_to_qualname(variable, used_variable.get("type"))
            
            assert used_variable["variable_name"] == qual_name, f"Wrong qualified name for the used variable {used_variable['qualified_name']}."

            assert len(used_variable["description"]) > 0, "The description of the used variables should not be empty."
            

        if used_variable.get("type") == "Custom":
            # the last part of the qual name
            variable_name = used_variable.get("variable_name").split(".")[-1]
            variable = next((v for v in project_custom_variables if v.get("variable_name") == variable_name), None)

            assert variable, f"Could not find the custom variable {used_variable['variable_name']}."

            assert used_variable["data_provider"] == provider_name.lower(), f"The data provider of the used variables should be {provider_name}."

            assert used_variable["data"] is not None, f"The data of the used variables should not be None."
        
        

        # must have "data_origin" that is an array of at least one element
        assert variable["data_origin"] and len(variable["data_origin"]) > 0, f"Missing data origin for the used variable {used_variable['variable_name']}."

        # each data origin must have an "enpoint" and "documentation" specified and each must be a valid url
        for data_origin in variable["data_origin"]:
            assert data_origin["endpoint"], f"Missing endpoint for the used variable {used_variable['variable_name']}."
            assert data_origin["documentation"], f"Missing documentation for the used variable {used_variable['variable_name']}."

            assert validate_url(data_origin["endpoint"]), f"Invalid endpoint url for the used variable {used_variable['variable_name']}."
            assert validate_url(data_origin["documentation"]), f"Invalid documentation url for the used variable {used_variable['variable_name']}."



"""
def test_get_the_github_token_from_refresh_token():


    client_id = "Iv1.8227a9c24d394f95"
    client_secret = "de1c6b38f695ae296cf32b1a1d679b2f2b0bf2a7"
    access_token = "ghu_MPbyRZiwpQQJcFJ4xwYUcHMYaADREF28DtH9"
    refresh_token = "ghr_PUUXjkWS1uS3XKiyZjZx8FCHxts6Rmo7p5r015mBLkCYpsrTdZTEYCXf3EnqhBXRajH2vq4JKz96"

    auth = Auth.Token(access_token)
    g = Github(auth=auth)

    user = g.get_user()

    orgs = user.get_orgs()
    repos = user.get_repos()
    stared = user.get_starred()

    for org in orgs:
        print(org.login)

    # Convert organizations into a list of dictionaries
    # orgs_list = [{"login": org.login, "description": org.description, "url": org.url} for org in orgs]

    # Convert repositories into a list of dictionaries
    repos_list = [{
        "name": repo.name,
        "description": repo.description,
        "url": repo.html_url,
        "owner": repo.owner.login,
        "forks_count": repo.forks_count,
        "has_wiki": repo.has_wiki,
        "open_issues_count": repo.open_issues_count,
        "stargazers_count": repo.stargazers_count
    } for repo in repos]



    # Convert starred repositories into a list of dictionaries
    starred_list = [{"name": star.name, "description": star.description, "url": star.html_url, "stars": star.stargazers_count} for star in stared]


    # Get the access token object
    token = g._Github__requester._Requester__oauth_token
"""
