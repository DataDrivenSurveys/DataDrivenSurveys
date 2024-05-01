#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This module contains classes that are specs for important types and data standards, type declarations,
and Data types used for variables.

Created on 2023-08-31 16:54

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
@author: Stefan Teofanovic (stefan.teofanovic@heig-vd.ch)
"""
__all__ = [
    # Type and TypeVar exports
    "TData",
    "TDataClass",
    "TVariableValue",
    "TVariable",
    "TVariableFunction",
    # Variable specification class exports
    "Variable",
    "VariableFunction",
    # Enum class exports
    # "Operators",
    "VariableType",
    "VariableDataType",
    # Data type class exports
    "Data",
    "Date",
    "Number",
    "Text",
]

import re
from abc import ABC, abstractmethod
from collections.abc import Callable
from datetime import date, datetime
from enum import Enum
from typing import Any, Optional, Type, TypeVar, Union

from .get_logger import get_logger

logger = get_logger(__name__)


# Class types (used for type hinting that something is that class object)
TDataClass = Type["Data"]

# TypeVars (used for type hinting that something is an instance of that class)
TVariableValue = Union[str, float, int, bool, None]
TVariableFunction = TypeVar("TVariableFunction", bound="VariableFunction")
TVariable = TypeVar("TVariable", bound="Variable")
TData = TypeVar("TData", bound="Data")

class VariableFunction(Callable):
    """
    This class is used for type hinting only and should not be used directly.

    Functions that calculate variable values have additional attributes that this class describes.

    Attributes:
        variable_name: The name of the variable that gets calculated.
        is_indexed_variable: Whether the variable is indexed or not.
        index_start: The start index of the variable.
        index_end: The end index of the variable.
        fully_indexed: Whether all indexed references of the variable have been added to a `DataProvider`'s variable_funcs dictionary.
    """
    def __init__(
        self,
        variable_name: str = "",
        is_indexed_variable: bool = None,
        index_start: int = None,
        index_end: int = None,
        fully_indexed: bool = False,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.variable_name: str = variable_name
        self.is_indexed_variable: bool = is_indexed_variable
        self.index_start: int = index_start
        self.index_end: int = index_end
        self.fully_indexed: bool = fully_indexed

    @abstractmethod
    def __call__(self, *args, **kwargs) -> TVariableValue:
        ...


class Variable(Callable):
    """This class standardizes the attributes that a variable should have.

    TVariables that are implemented in DataProvider classes should be Callable and be capable of calculating the value
    of a variable when called.

    Indexed TVariables should take a single argument when called, which is the index of the variable that should be
    returned.

    DataProvider classes should create dictionaries that conform to the attributes of this class. Attributes and
    their values correspond to dictionary key/value pairs.

    SurveyPlatform classes should be able to receive a variable or list of variables and be capable of converting
    them to whatever format is required.

    Attributes:
        data_provider: The data provider that the variable belongs to.
        category: The category of the variable.
        type: The type of the variable. Allowed values are "Builtin" and "Custom".
        name: The name of the variable.
        description: The description of the variable as will be shown in the variables table.
        data_type: The data type of the variable. Allowed values are "Number", "Text", and "Date".
        test_value_placeholder:
            The placeholder for the test value in the variables table.
            Indexed variables will append the number corresponding to the index to the end of the placeholder variable.
        info: The information that will be shown in the variables table info bubble.
        is_indexed_variable:
            Whether the variable is indexed or not. An indexed variable will generate multiple
            versions of the variable corresponding to the indices specified by `index_start` and `index_end`.
        index_start:
            Starting index for indexed variables. If a variable is indexed but no index_start is specified,
            it should default to 0.
        index_end:
            Ending index for indexed variables. If a variable is indexed but no index_end is specified,
            it should default to 5.
        value: The calculated value of the variable that gets uploaded to a SurveyPlatform.
    """
    def __init__(
        self,
        data_provider: str = "",
        category: str = "",
        type: str = "",
        name: str = "",
        description: str = "",
        data_type: str = "",
        test_value_placeholder: str = "",
        info: str = "",
        is_indexed_variable: bool = False,
        index_start: Optional[int] = 0,
        index_end: Optional[int] = 5,
        value: Optional[TVariableValue] = None,
    ) -> None:
        self.data_provider: str = data_provider
        self.category: str = category
        self.type: str = type
        self.name: str = name
        self.description: str = description
        self.data_type: str = data_type
        self.test_value_placeholder: str = test_value_placeholder
        self.info: str = info
        self.is_indexed_variable: bool = is_indexed_variable
        self.index_start: Optional[int] = index_start
        self.index_end: Optional[int] = index_end
        self.value: Optional[TVariableValue] = value

    def to_dict(self) -> dict[str, Any]:
        return {
            "data_provider": self.data_provider,
            "category": self.category,
            "type": self.type,
            "name": self.name,
            "description": self.description,
            "data_type": self.data_type,
            "test_value_placeholder": self.test_value_placeholder,
            "info": self.info,
            "is_indexed_variable": self.is_indexed_variable,
            "index_start": self.index_start,
            "index_end": self.index_end,
            "value": self.value
        }

    @abstractmethod
    def __call__(self, *args, **kwargs):
        ...


class Operator(Enum):
    IS = "__eq__"
    IS_NOT = "__ne__"
    IS_GREATER_THAN = "__gt__"
    IS_GREATER_THAN_OR_EQUAL_TO = "__ge__"
    IS_LESS_THAN = "__lt__"
    IS_LESS_THAN_OR_EQUAL_TO = "__le__"
    CONTAINS = "__contains__"
    DOES_NOT_CONTAIN = "__not_contains__"
    BEGINS_WITH = "startswith"
    ENDS_WITH = "endswith"
    REGEXP = "regexp"


class VariableType(Enum):
    BUILTIN = "Builtin"
    CUSTOM = "Custom"

class VariableDataType(Enum):
    NUMBER = "Number"
    TEXT = "Text"
    DATE = "Date"


# TODO: make Data inherit from Registry
class Data(ABC):

    _registry = {}

    operators: dict = None

    @staticmethod
    def register(data_type: VariableDataType, cls) -> None:
        Data._registry[data_type] = cls

    @staticmethod
    def get_class_by_type(data_type: VariableDataType) -> Any:
        return Data._registry[data_type]

    @classmethod
    @abstractmethod
    def get_filter_operators(cls):
        ...

    @staticmethod
    def is_this_data_type(data) -> bool:
        return isinstance(type(data), Data)

    @staticmethod
    def determine_type(value) -> TDataClass | type:
        if Data.is_this_data_type(value):  # Check for Data type
            return type(value)
        elif isinstance(value, list):  # Check for List type
            return type(value)
        elif isinstance(value, dict):  # Check for Object (dictionary) type
            return type(value)
        elif Date.is_this_data_type(value):  # Check for Date type
            return Date
        elif Number.is_this_data_type(value):  # Check for Number type
            return Number
        else:  # Default to Text type
            if not Text.is_this_data_type(value):
                logger.error(f"Unable to determine data type for value: {value}")
            return Text

    @staticmethod
    def get_all_filter_operators():
        result = {}
        for data_type, cls in Data._registry.items():
            result[data_type.value] = cls.get_filter_operators()
        return result

    @classmethod
    def get_operator(cls, operator: str = None):
        # check if operators has the key corresponding to the operator
        if operator in cls.operators:
            return cls.operators[operator]
        else:
            raise ValueError(f"Unknown operator: {operator}")


class Date(Data):

    @staticmethod
    def is_this_data_type(data: str) -> bool:
        try:
            Date._parse_date(data)
            return True
        except ValueError:
            return False

    @staticmethod
    def _parse_date(date_str: str) -> date:
        formats = [
            "%Y-%m-%d",
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%S.%f%z",
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M:%S.%f",
            "%Y%m%d"
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue

        raise ValueError(f"Unknown date format: {date_str}")


    operators = {
        Operator.IS.value: {
            "label": "api.custom_variables.filters.operators.date.is",
            "lambda": lambda a, b: Date._parse_date(a) == Date._parse_date(b)
        },
        Operator.IS_NOT.value: {
            "label": "api.custom_variables.filters.operators.date.is_not",
            "lambda": lambda a, b:Date._parse_date(a) != Date._parse_date(b)
        },
        Operator.IS_GREATER_THAN.value: {
            "label": "api.custom_variables.filters.operators.date.is_after",
            "lambda": lambda a, b: Date._parse_date(a) > Date._parse_date(b)
        },
        Operator.IS_GREATER_THAN_OR_EQUAL_TO.value: {
            "label": "api.custom_variables.filters.operators.date.is_on_or_after",
            "lambda": lambda a, b: Date._parse_date(a) >= Date._parse_date(b)
        },
        Operator.IS_LESS_THAN.value: {
            "label": "api.custom_variables.filters.operators.date.is_before",
            "lambda": lambda a, b: Date._parse_date(a) < Date._parse_date(b)
        },
        Operator.IS_LESS_THAN_OR_EQUAL_TO.value: {
            "label": "api.custom_variables.filters.operators.date.is_on_or_before",
            "lambda": lambda a, b: Date._parse_date(a) <= Date._parse_date(b)
        },
    }

    @classmethod
    def get_filter_operators(cls):
        # Convert the operators dictionary to the desired list format
        return [{"label": op_info["label"], "value": op_key} for op_key, op_info in cls.operators.items()]


class Number(Data):

    @staticmethod
    def is_this_data_type(data) -> bool:
        try:
            float(data)
            return True
        except ValueError:
            return False

    @staticmethod
    def _parse_number(numeric_value: Union[int, float, str]) -> Union[int, float]:

        if isinstance(numeric_value, int) or isinstance(numeric_value, float):
            return numeric_value

        return int(numeric_value) if numeric_value.isnumeric() else float(numeric_value)

    operators = {
        Operator.IS.value: {
            "label": "api.custom_variables.filters.operators.number.is",
            "lambda": lambda a, b: Number._parse_number(a) == Number._parse_number(b)
        },
        Operator.IS_NOT.value: {
            "label": "api.custom_variables.filters.operators.number.is_not",
            "lambda": lambda a, b: Number._parse_number(a) != Number._parse_number(b)
        },
        Operator.IS_GREATER_THAN.value: {
            "label": "api.custom_variables.filters.operators.number.is_greater_than",
            "lambda": lambda a, b: Number._parse_number(a) > Number._parse_number(b)
        },
        Operator.IS_GREATER_THAN_OR_EQUAL_TO.value: {
            "label": "api.custom_variables.filters.operators.number.is_greater_than_or_equal_to",
            "lambda": lambda a, b: Number._parse_number(a) >= Number._parse_number(b)
        },
        Operator.IS_LESS_THAN.value: {
            "label": "api.custom_variables.filters.operators.number.is_less_than",
            "lambda": lambda a, b: Number._parse_number(a) < Number._parse_number(b)
        },
        Operator.IS_LESS_THAN_OR_EQUAL_TO.value: {
            "label": "api.custom_variables.filters.operators.number.is_less_than_or_equal_to",
            "lambda": lambda a, b: Number._parse_number(a) <= Number._parse_number(b)
        }
    }

    @classmethod
    def get_filter_operators(cls):
        return [{"label": op_info["label"], "value": op_key} for op_key, op_info in cls.operators.items()]


class Text(Data):

    @staticmethod
    def is_this_data_type(data) -> bool:
        return isinstance(data, str)

    operators = {
        Operator.IS.value: {
            "label": "api.custom_variables.filters.operators.text.is",
            "lambda": lambda a, b: a == b
        },
        Operator.IS_NOT.value: {
            "label": "api.custom_variables.filters.operators.text.is_not",
            "lambda": lambda a, b: a != b
        },
        Operator.CONTAINS.value: {
            "label": "api.custom_variables.filters.operators.text.contains",
            "lambda": lambda a, b: b in a
        },
        Operator.DOES_NOT_CONTAIN.value: {
            "label": "api.custom_variables.filters.operators.text.does_not_contain",
            "lambda": lambda a, b: b not in a
        },
        Operator.BEGINS_WITH.value: {
            "label": "api.custom_variables.filters.operators.text.begins_with",
            "lambda": lambda a, b: a.startswith(b)
        },
        Operator.ENDS_WITH.value: {
            "label": "api.custom_variables.filters.operators.text.ends_with",
            "lambda": lambda a, b: a.endswith(b)
        },
        Operator.REGEXP.value: {
            "label": "api.custom_variables.filters.operators.text.regexp",
            "lambda": lambda a, b: re.match(b, a)
        }
    }

    @classmethod
    def get_filter_operators(cls):
        return [{"label": op_info["label"], "value": op_key} for op_key, op_info in cls.operators.items()]


Data.register(VariableDataType.DATE, Date)
Data.register(VariableDataType.NUMBER, Number)
Data.register(VariableDataType.TEXT, Text)
