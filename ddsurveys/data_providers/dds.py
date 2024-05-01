#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2023-08-31 16:59

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
@author: Stefan Teofanovic (stefan.teofanovic@heig-vd.ch)
"""

__all__ = ["DDSDataProvider"]

import base64
from datetime import datetime
from functools import cached_property
from typing import Any, Callable, Dict

from ..get_logger import get_logger
from ..variable_types import TVariableValue, VariableDataType
from .bases import FormTextBlock, FrontendDataProvider
from .data_categories import DataCategory
from .variables import BuiltInVariable, CVAttribute

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
            extractor_func=lambda variable, data: (
                "Yes"
                if variable["qualified_name"] in data
                and data[variable["qualified_name"]]["count"] > 0
                else "No"
            ),
            data_origin=[{"documentation": "Monitored by the frontend application."}],
        )
    ]


class DDSDataProvider(FrontendDataProvider):

    # Class attributes go here
    app_required: bool = False

    fields: list[dict[str, Any]] = {}

    # Form fields declarations go here
    form_fields = [FormTextBlock(name="information", content="information")]

    # DataCategory declarations go here
    data_categories = [FrontendActivity]
