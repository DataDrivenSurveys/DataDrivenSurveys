#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2023-08-31 16:59

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
"""

__all__ = "FitbitDataProvider"

import base64
from datetime import datetime
from typing import Callable, Dict, Any
from functools import cached_property

import requests

from ..get_logger import get_logger
from .bases import DataProvider, FormTextBlock
from .variables import CVAttribute, BuiltInVariable, BuiltInVariable
from ..variable_types import TVariableFunction, VariableDataType
from .data_categories import DataCategory

logger = get_logger(__name__)

class FrontendActivity(DataCategory):
    """Represents a category of data related to frontend user activities."""

    builtin_variables = [
       BuiltInVariable.create_instances(
            name="open_transparency_table",
            label="Open Transparency Table",
            description="Indicates whether the respondent has accessed the transparency table.",
            data_type=VariableDataType.TEXT,
            test_value_placeholder="Yes",
            info="This variable reflects access to the transparency table, set to 'Yes' if accessed and 'No' otherwise.",
            data_origin=[{
                "documentation":"Monitored by the frontend application."
            }]
        )
    ]


class DDSDataProvider(DataProvider):

    # Class attributes go here
    app_required: bool = False
   
    fields: list[dict[str, Any]] = {}

    # Form fields declarations go here
    form_fields = [
        FormTextBlock(
            name="information",
            content="information"
        )
    ]

    # DataCategory declarations go here
    data_categories = [
        FrontendActivity
    ]

    # Standard class methods go here
    def __init__(self, **kwargs):
       
        super().__init__(**kwargs)
       

    def test_connection(self) -> bool:
        return True

