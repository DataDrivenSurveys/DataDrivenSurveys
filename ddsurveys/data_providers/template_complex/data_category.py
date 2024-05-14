#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2024-05-14 11:40

@author: Lev Velykoivanenko (lev.velykoivanenko@gmail.com)
"""

from typing import Any, Callable, Dict

from ...get_logger import get_logger
from ..data_categories import DataCategory
from ..variables import BuiltInVariable, CVAttribute
from ...variable_types import TVariableFunction, VariableDataType

# Import the required libraries to make this work
from .api import MyAPI

logger = get_logger(__name__)


# This is an example of a data category.
# In practice, each endpoint can be turned into a data category.
class ExampleDataCategory(DataCategory):

    data_origin = [
        {
            "method": "get_user",
            "endpoint": "https://api.dataprovider.com/account",
            "documentation": "https://docs.dataprovider.com/en/rest/reference/account",
        }
    ]

    custom_variables_enabled = False

    api = None

    def fetch_data(self) -> list[dict[str, Any]]:
        user = self.api.get_user()
        return user

    cv_attributes = [
        CVAttribute(
            name="name",
            label="Users Name",
            description="The name of the user.",
            attribute="name",
            data_type=VariableDataType.TEXT,
            test_value_placeholder="Username",
            info="The name of the user.",
        ),
        CVAttribute(
            label="Creation Date",
            description="The date the repository was created.",
            attribute="created_at",
            name="creation_date",
            data_type=VariableDataType.DATE,
            test_value_placeholder="2023-01-10T12:00:00.000",
            info="The date the account was created.",
        ),
    ]

    builtin_variables = [
        BuiltInVariable.create_instances(
            name="creation_date",
            label="Account creation date",
            description="The date the user created their account.",
            test_value_placeholder="2020-01-01",
            data_type=VariableDataType.DATE,
            info="The date the account was created. It will be in the format YYYY-MM-DD.",
            is_indexed_variable=False,
            extractor_func=lambda self: self.account_creation_date,
            data_origin=[],
        )
    ]
