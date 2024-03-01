#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2023-08-31 16:59

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
"""

__all__ = "FitbitDataProvider"

from typing import Any
from functools import cached_property

from ..get_logger import get_logger
from ..variable_types import VariableDataType
from .bases import DataProvider
from .variables import BuiltInVariable
from .data_categories import DataCategory

logger = get_logger(__name__)


class UserBehaviour(DataCategory):
    supports_custom_variables = False

    def fetch_data(self) -> list[dict[str, Any]]:
        return []

    cv_attributes = []

    builtin_variables = [
        BuiltInVariable.create_instances(
            name="view_transparency_grid",
            label="View Transparency Grid",
            description="Whether the user has viewed the transparency grid.",
            data_type=VariableDataType.TEXT,
            test_value_placeholder="false",
            info="Whether the user has viewed the transparency grid.",
            extractor_func=None
        )
    ]

class DDSDataProvider(DataProvider):
   
    data_categories = [
        UserBehaviour
    ]

    # DataCategory declarations go here
    # TODO: replace this with external classes after splitting the classes into modules

    # Standard class methods go here
    def __init__(self, **kwargs):
       pass

    