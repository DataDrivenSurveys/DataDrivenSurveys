#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
from ddsurveys.data_providers.bases import DataCategory, DataProvider
from ddsurveys.data_providers.fitbit import Activities, Account, Steps, Badges
from ddsurveys.data_providers.instagram import Media


def test_get_all_data_categories():
    """
    Validate the retrieval of all data categories in form of dictionary.
    Used to send data categories to the frontend.
    """
    # Ensure the data categories are returned in the expected order.
    data_categories = DataProvider.get_all_data_categories()

    for data_category in data_categories:
        assert 'label' in data_category, "The label should be included in the DataCategory dict."
        assert 'value' in data_category, "The value should be included in the DataCategory dict."
        assert 'builtin_variables' in data_category, "The builtin variables should be included in the DataCategory dict."
        assert 'cv_attributes' in data_category, "The custom variables should be included in the DataCategory dict."
        assert 'data_provider_type' in data_category, "The data provider type should be included in the DataCategory dict."

        assert len(data_category['cv_attributes']) >= 0, "The custom variables should be included in the DataCategory dict."
        assert len(data_category['builtin_variables']) >= 0, "The builtin variables should be included in the DataCategory dict."

        builtin_variable_attributes = [
            'label', 'name', 'description', 'data_type', 'category',
            'qualified_name', 'data_provider', 'test_value_placeholder',
            'info', 'type'
        ]

        cv_attribute_fields = [
            'label', 'name', 'description', 'data_type', 'category',
            'test_value_placeholder', 'info'
        ]

        for variable in data_category["builtin_variables"]:
            for attribute in builtin_variable_attributes:
                assert attribute in variable, f"The {attribute} should be included in the builtin variable dict."
                assert variable[attribute], f"Builtin Variable {variable.get('name', 'Unknown')} in DataCategory {data_category.get('label', 'Unknown')} has empty or None for {attribute}."

        for attribute in data_category["cv_attributes"]:
            for field in cv_attribute_fields:
                assert field in attribute, f"The {field} should be included in the custom variable dict."
                assert attribute[field], f"Custom Variable {attribute.get('name', 'Unknown')} in DataCategory {data_category.get('label', 'Unknown')} has empty or None for {field}."

        # a data category must have at least some builtin variables or some custom variables
        assert len(data_category['cv_attributes']) > 0 or len(data_category['builtin_variables']) > 0, "A data category must have at least some builtin variables or some custom variables"




