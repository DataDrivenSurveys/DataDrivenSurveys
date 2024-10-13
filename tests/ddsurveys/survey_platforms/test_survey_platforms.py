#!/usr/bin/env python3
"""Test the UI feeder methods.

SurveyPlatform.get_all_form_fields()
"""
import pytest
from flask import Flask

from ddsurveys.survey_platforms.bases import SurveyPlatform

app = Flask(__name__)

REGISTERED_SURVEY_PLATFORMS = list(SurveyPlatform.get_registry().keys())


def test_get_all_form_fields():
    """Validate the retrieval of all form fields for SurveyPlatforms."""
    # Retrieve the form fields using the superclass method
    survey_platforms_form_fields = SurveyPlatform.get_all_form_fields()

    field_types = ["text", "button"]

    # Define the required keys for the main structure, fields, and inside each field
    main_keys = ['fields', 'instructions', 'label', 'value']
    text_keys = ['helper_text', 'label', 'name', 'required', 'data_type']
    button_keys = ['onClick', 'name']
    field_key_mappings  = {
        'text': text_keys,
        'button': button_keys
    }

    # Base pattern for survey platforms
    base_pattern = "api.ddsurveys.survey_platforms"
    # TODO : Fix the __package__ issue for survey platforms

    for survey_platform_form_fields in survey_platforms_form_fields:
        # Extract the name from the value for use in string pattern checks
        platform_name = survey_platform_form_fields['value'].lower()

        # Check main structure
        for key in main_keys:
            assert key in survey_platform_form_fields, f"Key {key} missing in survey platform {survey_platform_form_fields.get('label', 'Unknown')}."
            assert survey_platform_form_fields[key], f"Key {key} in survey platform {survey_platform_form_fields.get('label', 'Unknown')} has empty or None value."

        # Check if 'instructions' follow the expected pattern
        expected_instruction_pattern = f"{base_pattern}.{platform_name}.instructions.text"
        assert survey_platform_form_fields['instructions'] == expected_instruction_pattern, \
            f"Instructions pattern mismatch for survey platform {platform_name}. Expected: {expected_instruction_pattern}, Got: {survey_platform_form_fields['instructions']}."

        # Check fields
        for field in survey_platform_form_fields['fields']:
            required_keys = field_key_mappings.get(field["data_type"], [])
            for f_key in required_keys:
                assert f_key in field, f"Key {f_key} missing in field {field.get('name', 'Unknown')} of survey platform {survey_platform_form_fields.get('label', 'Unknown')}."
                assert field[f_key] is not None, f"Key {f_key} in field {field.get('name', 'Unknown')} of survey platform {survey_platform_form_fields.get('label', 'Unknown')} has empty or None value."

            # Check if data_type is one of the known types, e.g., "text".
            assert field['data_type'] in field_types, f"Unknown field data_type {field['data_type']} in field {field.get('name', 'Unknown')} of survey platform {survey_platform_form_fields.get('label', 'Unknown')}."

            # Check if 'label' and 'helper_text' follow the expected pattern
            expected_label_pattern = f"{base_pattern}.{platform_name}.{field['name']}.label"
            expected_helper_pattern = f"{base_pattern}.{platform_name}.{field['name']}.helper_text"

            assert field['label'] == expected_label_pattern, \
                f"Label pattern mismatch in field {field['name']} of survey platform {platform_name}. Expected: {expected_label_pattern}, Got: {field['label']}."

            assert field['helper_text'] == expected_helper_pattern, \
                f"Helper text pattern mismatch in field {field['name']} of survey platform {platform_name}. Expected: {expected_helper_pattern}, Got: {field['helper_text']}."



"""
    Test the UI feeder methods.
    That the required form_fields for each survey platform are present.
    Using parametrize to test all survey platform.
"""
# Fields that are required for each SurveyPlatform
# This dictionary is structured with the SurveyPlatform name as the key and a list of required field names as the value
REQUIRED_FIELDS = {
    'Qualtrics': ['survey_platform_api_key'],
    # ... Add other survey platforms and their required fields as needed
}

@pytest.mark.parametrize('survey_platform_name', REGISTERED_SURVEY_PLATFORMS)
def test_survey_platform_required_fields(survey_platform_name):
    """Validate the required fields for each SurveyPlatform.
    Checks that the required form fields for each data providers are present, well-defined, and have non-empty or non-None values.
    """
    form_fields = SurveyPlatform.get_all_form_fields()
    lower_name = survey_platform_name.lower()

    # Extract the survey platforms's fields from the list
    survey_platform_data = next((item for item in form_fields if item["value"] == lower_name), None)

    assert survey_platform_data, f"Missing survey platform information for {survey_platform_name}."

    provided_field_names = [field['name'] for field in survey_platform_data['fields']]

    field_structure_keys = ['helper_text', 'label', 'name', 'required', 'data_type']

    for required_field in REQUIRED_FIELDS.get(survey_platform_name, []):
        assert required_field in provided_field_names, f"Missing required field {required_field} for {survey_platform_name}."

        # Check if the field is well-defined (i.e., has a non-empty or non-None value)
        field_data = next((field for field in survey_platform_data['fields'] if field["name"] == required_field), None)
        assert field_data, f"Field {required_field} for {survey_platform_name} is not well-defined."
        for key in field_structure_keys:
            assert key in field_data, f"Key '{key}' missing in field {required_field} of survey platform {survey_platform_name}."
            assert field_data[key], f"Key '{key}' in field {required_field} of survey platform {survey_platform_name} has empty or None value."


"""
 Test if each survey platform declares the required abstract methods.
"""
@pytest.mark.parametrize('survey_platform_name', REGISTERED_SURVEY_PLATFORMS)
def test_survey_platform_defined_methods(survey_platform_name):
    platform_class = SurveyPlatform.get_class_by_value(survey_platform_name.lower())

    platform_instance = platform_class(
        survey_id="test",
        survey_platform_api_key="test",
    )

    assert platform_class, f"Missing survey platform class for {survey_platform_name}."

    # Check if the required abstract methods are defined
    required_methods = ['fetch_survey_platform_info', 'handle_project_creation', 'handle_variable_sync', 'handle_prepare_survey']
    for method_name in required_methods:
        assert hasattr(platform_instance, method_name), f"Missing required method {method_name} for {survey_platform_name}."
        method = getattr(platform_instance, method_name)

        assert callable(method), f"Method {method_name} for {survey_platform_name} is not callable."
        is_abstract = hasattr(method, '__isabstractmethod__') and method.__isabstractmethod__

        assert not is_abstract, f"Method {method_name} for {survey_platform_name} is not implemented."
