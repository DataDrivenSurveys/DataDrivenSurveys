#!/usr/bin/env python3
"""Created on 2024-07-24 13:12.

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
"""
from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict, TypeVar

from ddsurveys.data_providers.data_categories import DataCategory

if TYPE_CHECKING:
    from ddsurveys.typings.data_providers.variables import (
        BuiltinVariableDict,
        CVAttributeDict,
        DataOriginDict,
    )


class DataCategoryDict(TypedDict):
    label: str
    value: str
    custom_variables_enabled: bool
    builtin_variables: list[BuiltinVariableDict]
    cv_attributes: list[CVAttributeDict]
    data_origin: list[DataOriginDict]


TDataCategoryClass = type[DataCategory]
TDataCategory = TypeVar("TDataCategory", bound=DataCategory)
