#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# test_data_provider.py
# (.venv) C:\UNIL\DataDrivenSurveys\ddsurveys>python -m pytest
import pytest
from flask import Flask

from ddsurveys.data_providers.bases import CustomVariable, DataProvider
from ddsurveys.data_providers.fitbit import Activities, FitbitDataProvider
from ddsurveys.data_providers.instagram import InstagramDataProvider

from ..utils.custom_variables_scenarios_data import get_scenarios
from ..utils.functions import assert_has_value
from ..utils.mock_data import fitbit_mock_properties

app = Flask(__name__)


def variable_to_qualname(variable, v_type = "builtin") -> str:
    """Return the qualified name of a variable."""
    qual_name = f"dds.{variable['data_provider']}.{v_type}.{variable['category'].lower()}.{variable['name']}"
    if variable["is_indexed_variable"]:
        qual_name += f"[{variable['index']}]"

    return qual_name

@pytest.fixture
def abstract_data_provider() -> DataProvider:
    """Return an instance of the abstract DataProvider class."""
    return DataProvider()

@pytest.fixture
def fitbit_data_provider() -> FitbitDataProvider:
    """Return an instance of the FitbitDataProvider class."""
    return FitbitDataProvider()

@pytest.fixture
def instagram_data_provider() -> InstagramDataProvider:
    """Return an instance of the InstagramDataProvider class."""
    return InstagramDataProvider()

def data_category_to_custom_variable(data_category, data_provider_name, filters, selection):# -> dict[str, Any]:
    """Return the custom variable format based on a data category."""

    return {
        "id": 9,
        "cv_attributes": [
            {**attribute_dict, 'enabled': True} for attribute_dict in data_category["cv_attributes"]
        ],
        "data_category": data_category["value"],
        "data_provider": data_provider_name,
        "filters": filters,
        "selection": selection,
        "type": "Custom",
        "variable_name": "act1",
        "enabled": True
    }


@pytest.mark.parametrize(
    "label, filters, selection, expected_attribute_value",
    get_scenarios(),
    ids=[scenario[0] for scenario in get_scenarios()]
)
def test_custom_variables_processing_single_filter(mocker, fitbit_data_provider, label, filters, selection, expected_attribute_value):
    """
        Test the data extraction of the custom variables.
        Testing the filter and selection on the list of data.
        Filtering tested using a single filter at a time.
        All operators and data types are tested.
        All selection operators are tested.
        Mock the FitbitDataProvider activities_frequent property with the mock data.
        Check that the data is extracted correctly.
        Check the variable values are properly computed and the data to upload is properly formatted.
    """

    def find_name_by_attr(data_category, expected_attribute_value):
        # Iterate over each cv_attribute in activity's cv_attributes list
        for cv_attribute in data_category.get("cv_attributes", []):
            # Check if the attribute key of cv_attribute matches the attr of expected_attribute_value
            if cv_attribute.get("attribute") == expected_attribute_value.get("attr"):
                return cv_attribute.get("name")
        return None

    ctx = app.app_context()
    ctx.push()


    mocker.patch.object(FitbitDataProvider, 'activity_logs', new_callable=mocker.PropertyMock, return_value=fitbit_mock_properties["activity_logs"])

    # get all the attributes of the Activities class as dict
    activity = Activities.to_dict()

    assert len(fitbit_data_provider.activity_logs["activities"]) == 3, "There should be 3 most frequent activities."

    custom_var = data_category_to_custom_variable(
                data_category=activity,
                data_provider_name="fitbit",
                filters=filters,
                selection=selection
            )

    data_to_upload = fitbit_data_provider.calculate_variables(
        project_builtin_variables=[],
        project_custom_variables=[
            custom_var
        ],
    )

    cv_attribute_name = find_name_by_attr(activity, expected_attribute_value)

    def assert_value_by_key_suffix(data_to_upload, key_suffix, expected_value):
        for key, value in data_to_upload.items():
            if key.endswith(key_suffix):
                if expected_value is None: # Random selection on multiple rows
                    return

                if str(expected_value) != str(value):
                    print(f"Expected value for key '{key}' is {expected_value}, but got {value}")

                assert str(value) == str(expected_value), f"Expected value for key '{key}' is {expected_value}, but got {value}"
                return
        raise KeyError(f"No key ending with '{key_suffix}' found in the data_to_upload dictionary.")

    # Check the data to upload
    assert_value_by_key_suffix(data_to_upload, cv_attribute_name, expected_attribute_value.get("value"))


    ctx.pop()


@pytest.mark.parametrize(
    "label, filters, selection, expected_attribute_value",
    get_scenarios(),
    ids=[scenario[0] for scenario in get_scenarios()]
)
def test_custom_variable_dictionary(mocker, fitbit_data_provider, label, filters, selection, expected_attribute_value):
    """Test the custom variable to phrase conversion."""
    ctx = app.app_context()
    ctx.push()

    mocker.patch.object(FitbitDataProvider, 'activity_logs', new_callable=mocker.PropertyMock, return_value=fitbit_mock_properties["activity_logs"])

    custom_variable_instance = CustomVariable(
        data_provider=fitbit_data_provider,
        custom_variable=data_category_to_custom_variable(
            data_category=Activities.to_dict(),
            data_provider_name="fitbit",
            filters=filters,
            selection=selection
        )
    )

    def assert_attribute(attribute):
        assert_has_value(attribute, 'label', "The attribute label should be set.")
        assert_has_value(attribute, 'description', "The attribute description should be set.")
        assert_has_value(attribute, 'name', "The attribute name should be set.")
        assert_has_value(attribute, 'data_type', "The attribute data_type should be set.")
        assert_has_value(attribute, 'info', "The attribute info should be set.")
        assert_has_value(attribute, 'test_value_placeholder', "The attribute test_value_placeholder should be set.")

        if attribute.get('data_type') == "Number":
            assert_has_value(attribute, 'unit', "The attribute unit should be set.")

        assert_has_value(attribute, 'attribute', "The attribute attribute should be set.")
        assert_has_value(attribute, 'enabled', "The attribute enabled should be set.")

    def assert_filter(filter):
        assert_has_value(filter, 'attribute', "The filter attribute should be set.")
        assert_attribute(filter.get('attribute'))
        assert_has_value(filter, 'operator', "The filter operator should be set.")
        assert_has_value(filter, 'value', "The filter value should be set.")

    def assert_selection(selection):
        operator = selection.get('operator')
        assert_has_value(selection, 'operator', "The selection operator should be set.")
        assert_has_value(selection, 'attribute', "The selection attribute should be set.")
        assert_attribute(selection.get('attribute'))

        # Check the selection operator
        assert_has_value(operator, 'strategy', "The selection operator strategy should be set.")
        assert_has_value(operator, 'operator', "The selection operator should be set.")

    cv_dict = custom_variable_instance.to_dict()

    assert_has_value(cv_dict, 'variable_name', "The variable_name should be set.")
    assert_has_value(cv_dict, 'data_category', "The data_category should be set.")
    assert_has_value(cv_dict, 'attributes', "The attributes should be set.")
    assert_has_value(cv_dict, 'filters', "The filters should be set.")
    assert_has_value(cv_dict, 'selection', "The selection should be set.")

    # Check the data category
    assert_has_value(cv_dict.get('data_category'), 'label', "The data_category label should be set.")
    assert_has_value(cv_dict.get('data_category'), 'value', "The data_category value should be set.")

    # Check the attributes
    attributes = cv_dict.get('attributes')
    assert len(attributes) == len(custom_variable_instance.data_category.cv_attributes), "The number of attributes should match the number of cv_attributes."

    for attribute in attributes:
        assert_attribute(attribute)

    # Check the filters
    filters = cv_dict.get('filters')
    assert len(filters) == len(custom_variable_instance.filters), "The number of filters should match the number of filters."
    for filter in filters:
        assert_filter(filter)

    # Check the selection
    selection = cv_dict.get('selection')
    assert_selection(selection)

    ctx.pop()
