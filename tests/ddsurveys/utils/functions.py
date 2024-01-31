#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import validators
import re
import random
import string
from ddsurveys.data_providers.bases import DataProvider


def random_string(length=8):
    """Generate a random string of fixed length."""
    letters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(letters) for _ in range(length))


def random_number(length=8):
    """Generate a random number of fixed length."""
    return ''.join(random.choice(string.digits) for _ in range(length))


def replace_placeholder(match):
    placeholder = match.group(1)

    # Replace specific placeholders with appropriate values
    if placeholder == "user-id":
        return random_number(length=5)  # Assuming user IDs are 5-digit numbers
    else:
        # Default to replacing with a random string
        return random_string(length=8)


"""
Replace placeholders in URL with random values and validate URL.
"""


def validate_url(url):
    """Validate URL."""
    url = re.sub(r'\[(.*?)]', replace_placeholder, url)
    return validators.url(url)


def assert_has_value(d, key, message):
    """Asserts that the dictionary has a key with a non-empty value."""
    assert d.get(key), message


def variable_to_qualname(variable, v_type="builtin", cv_attribute=None):
    """Return the qualified name of a variable."""
    qual_name = ""
    if v_type.lower() == "builtin":
        qual_name = (f"dds.{variable['data_provider']}.{v_type.lower()}.{variable['category'].lower()}."
                     f"{variable['name']}")
        if variable["is_indexed_variable"]:
            qual_name += f"[{variable['index']}]"
    elif v_type.lower() == "custom":
        qual_name = f"dds.{variable['data_provider']}.{v_type.lower()}.{variable[('data_category')].lower()}.{variable['variable_name']}.{cv_attribute['name']}"

    return qual_name


def generate_builtin_variables(data_provider: str = "fitbit"):
    """Prepare the builtin variables for the test."""
    # Simulate all enabled builtin variables for the fitbit data provider
    data_provider_class = DataProvider.get_class_by_value(data_provider)
    data_provider_instance = data_provider_class()
    project_buitin_variables = data_provider_instance.get_builtin_variables()

    for variable in project_buitin_variables:
        variable["enabled"] = True

    return project_buitin_variables


def generate_custom_variables(data_provider: str = "fitbit"):
    # Simulate all enabled custom variables for the instagram data provider
    data_provider_class = DataProvider.get_class_by_value(data_provider)
    data_provider_instance = data_provider_class()
    project_custom_variables = data_provider_instance.get_data_categories()

    # filter out all categories that don't have any attributes
    project_custom_variables = [cv for cv in project_custom_variables if len(cv["cv_attributes"]) > 0]

    for index, custom_var in enumerate(project_custom_variables):
        for attribute in custom_var["cv_attributes"]:
            attribute["enabled"] = True

        attribute_for_selection = custom_var["cv_attributes"][0]

        # find the attribute of data_type Date
        date_attribute_for_filter = next((attr for attr in custom_var["cv_attributes"] if attr["data_type"] == "Date"),
                                         None)

        if date_attribute_for_filter is None:
            raise Exception(
                "Could not find a Date attribute for filtering, make sure you have a Date attribute in your data "
                "category.")

        custom_var["data_category"] = custom_var["value"]
        custom_var["data_provider"] = custom_var["data_provider_type"].lower()
        custom_var["type"] = "Custom"
        custom_var["enabled"] = True

        custom_var["variable_name"] = f"custom-variable-{index}"

        custom_var["filters"] = [{
            "attr": date_attribute_for_filter["attribute"],
            "operator": "__gt__",
            "value": "2023-01-01T12:00:00.000"
        }]

        custom_var["selection"] = {
            "attr": attribute_for_selection["attribute"],
            "operator": "min"
        }

        del custom_var["value"]
        del custom_var["data_provider_type"]
        del custom_var["label"]

    return project_custom_variables
