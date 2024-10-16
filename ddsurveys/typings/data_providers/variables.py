"""Created on 2024-07-24 13:11.

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
"""

from __future__ import annotations

from typing import TYPE_CHECKING, NotRequired, TypedDict

from ddsurveys.typings.variable_types import TVariableValue

if TYPE_CHECKING:
    from ddsurveys.data_providers.data_categories import DataCategoryDict


class DataOriginDict(TypedDict):
    method: str
    endpoint: str
    documentation: str


class AttributeDict(TypedDict):
    name: str
    label: str
    data_type: str
    description: str
    info: str
    test_value: str
    test_value_placeholder: str
    unit: str
    data_origin: list[DataOriginDict]


class BuiltinVariableDict(AttributeDict):
    is_indexed_variable: bool
    index: int
    category: str


class QualifiedBuiltInVariableDict(BuiltinVariableDict):
    data_provider: str
    qualified_name: str
    type: str


class CVAttributeDict(AttributeDict):
    attribute: str
    enabled: bool
    category: str


class SelectionStrategyDict(TypedDict):
    strategy: str
    operator: str


class SelectionDict(TypedDict):
    attr: str
    operator: str


class CVSelectionDict(TypedDict):
    operator: SelectionStrategyDict
    attribute: AttributeDict | None


DataDict = dict[str, TVariableValue]


class CVFilterDict(TypedDict):
    attribute: CVAttributeDict
    operator: str
    value: str


class CustomVariableDict(TypedDict):
    variable_name: str
    qualified_name: str
    data_category: DataCategoryDict
    attributes: list[CVAttributeDict]
    filters: list[CVFilterDict]
    selection: CVSelectionDict


class CustomVariableUploadDict(TypedDict):
    category: str
    data_provider: str
    data_type: str
    description: str
    info: str
    variable_name: str
    qualified_name: str
    value: NotRequired[TVariableValue]
    test_value_placeholder: str
    type: str


ComputedVariableDict = dict[str, TVariableValue]
