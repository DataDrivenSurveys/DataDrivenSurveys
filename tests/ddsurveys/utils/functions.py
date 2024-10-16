#!/usr/bin/env python3
"""This module provides utility functions used for various tests."""

from __future__ import annotations

import random
import re
import string
from typing import TYPE_CHECKING, Any, Literal

import validators

from ddsurveys.data_providers.bases import DataProvider

if TYPE_CHECKING:
    from collections.abc import Hashable

    from ddsurveys.typings.data_providers.variables import CVAttributeDict
    from ddsurveys.typings.models import BuiltinVariableDict_, CustomVariableDict


def random_string(length: int = 8) -> str:
    """Generate a random string of fixed length."""
    letters = string.ascii_lowercase + string.digits
    return "".join(random.choice(letters) for _ in range(length))


def random_number(length: int = 8) -> str:
    """Generate a random number of fixed length."""
    return "".join(random.choice(string.digits) for _ in range(length))


def replace_placeholder(match: re.Match[str]) -> str:
    """This function replaces placeholders in a given string with random values.

    Params:
        match (re.Match[str]): A match object representing a placeholder in the input
            string. The placeholder is contained in the first match group.

    Returns:
        str: The input string with the placeholder replaced by a random value.
            If the placeholder is "user-id", a random 5-digit number is returned.
            Otherwise, a random string of length 8 is returned.
    """
    placeholder = match.group(1)

    # Replace specific placeholders with appropriate values
    if placeholder == "user-id":
        return random_number(length=5)  # Assuming user IDs are 5-digit numbers

    # Default to replacing with a random string
    return random_string(length=8)


def validate_url(url: str) -> validators.ValidationError | bool:
    """Validate URL."""
    url = re.sub(r"\[(.*?)]", replace_placeholder, url)
    return validators.url(url)


def assert_has_value(d: dict[Hashable, Any], key: Hashable, message: str) -> None:
    """Asserts that the given dictionary contains the specified key with a non-empty value.

    Args:
        d (dict[Hashable, Any]): The dictionary to check.
        key (Hashable): The key to look for in the dictionary.
        message (str): The message to display if the assertion fails.

    Raises:
        AssertionError: If the key is not found in the dictionary or its value is None.
    """
    assert d.get(key) is not None, message


def builtin_variable_to_qualname(variable: BuiltinVariableDict_) -> str:
    qual_name = f"dds.{variable['data_provider']}.builtin.{variable['category'].lower()}." f"{variable['name']}"
    if variable["is_indexed_variable"]:
        qual_name += f"{variable.get('index', '')}"
    return qual_name


def custom_variable_to_qualname(variable: CustomVariableDict, cv_attribute: CVAttributeDict) -> str:
    qual_name = f"dds.{variable['data_provider']}.custom.{variable[('data_category')].lower()}.{variable['variable_name']}.{cv_attribute['name']}"

    return qual_name


def generate_builtin_variables(data_provider: str = "fitbit"):
    """Prepare the builtin variables for the test."""
    # Simulate all enabled builtin variables for the fitbit data provider
    data_provider_class = DataProvider.get_class_by_value(data_provider)
    data_provider_instance = data_provider_class()
    project_builtin_variables = data_provider_instance.get_builtin_variables()

    for variable in project_builtin_variables:
        variable["enabled"] = True

    return project_builtin_variables


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
        date_attribute_for_filter = next(
            (attr for attr in custom_var["cv_attributes"] if attr["data_type"] == "Date"), None
        )

        if date_attribute_for_filter is not None:
            custom_var["filters"] = [
                {
                    "attr": date_attribute_for_filter["attribute"],
                    "operator": "__gt__",
                    "value": date_attribute_for_filter["test_value_placeholder"],
                }
            ]

        custom_var["data_category"] = custom_var["value"]
        custom_var["data_provider"] = custom_var["data_provider_name"].lower()
        custom_var["type"] = "Custom"
        custom_var["enabled"] = True

        custom_var["variable_name"] = f"custom-variable-{index}"

        custom_var["selection"] = {"attr": attribute_for_selection["attribute"], "operator": "min"}

        del custom_var["value"]
        del custom_var["data_provider_name"]
        del custom_var["label"]

    return project_custom_variables
