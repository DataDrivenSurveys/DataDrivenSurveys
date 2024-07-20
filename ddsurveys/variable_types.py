#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This module contains classes that are specs for important types and data standards, type declarations,
and Data types used for variables.

The module is designed to provide a structured way to define and interact with variables within a data processing
and analysis context. It includes abstract base classes and concrete implementations for handling different types
of variables, such as numeric, textual, and date variables. Additionally, it defines enums and type hints to
facilitate clear and consistent type declarations throughout the codebase.

Created on 2023-08-31 16:54

Authors:
    - Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
    - Stefan Teofanovic (stefan.teofanovic@heig-vd.ch)
"""
__all__: list[str] = [
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
from typing import Any, Optional, TypeAlias, TypeVar, TypedDict, Union

from .get_logger import get_logger

logger = get_logger(__name__)


# Class types (used for type hinting that something is that class object)
TDataClass = type["Data"]

# TypeVars (used for type hinting that something is an instance of that class)
TVariableValue = Union[str, float, int, bool, None]
TVariableFunction = TypeVar("TVariableFunction", bound="VariableFunction")
TVariable = TypeVar("TVariable", bound="Variable")
TData = TypeVar("TData", bound="Data")


class OperatorDict(TypedDict):
    label: str
    func: Callable[[TVariableValue, TVariableValue], bool]


OperatorsDict: TypeAlias = dict[str, OperatorDict]


class VariableFunction(Callable):
    """
    This class is used for type hinting only and should not be used directly.

    Functions that calculate variable values have additional attributes that this class describes.

    Attributes:
        variable_name (str): The name of the variable that gets calculated.
        is_indexed_variable (bool): Whether the variable is indexed or not.
        index_start (int): The start index of the variable.
        index_end (int): The end index of the variable.
        fully_indexed (bool): Whether all indexed references of the variable have been added to a `DataProvider`'s variable_funcs dictionary.
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
        """
        Initializes a new instance of the VariableFunction class.

        Parameters:
            variable_name (str): The name of the variable to be calculated. Defaults to an empty string.
            is_indexed_variable (bool, optional): Flag indicating whether the variable is indexed. Defaults to None.
            index_start (int, optional): The starting index for indexed variables. Defaults to None.
            index_end (int, optional): The ending index for indexed variables. Defaults to None.
            fully_indexed (bool): Flag indicating whether all indexed references of the variable have been fully added. Defaults to False.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        super().__init__(*args, **kwargs)
        self.variable_name: str = variable_name
        self.is_indexed_variable: bool = is_indexed_variable
        self.index_start: int = index_start
        self.index_end: int = index_end
        self.fully_indexed: bool = fully_indexed

    @abstractmethod
    def __call__(self, *args, **kwargs) -> TVariableValue:
        """
        Abstract method that when implemented, should calculate and return the value of the variable.

        This method must be overridden by subclasses to provide the specific logic for calculating the variable's value.

        Parameters:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            TVariableValue: The calculated value of the variable. This can be of type Union[str, float, int, bool, None].
        """
        ...


class Variable(Callable):
    """
    A class to define the structure and behavior of variables within a data provider context.

    This class is designed to encapsulate the attributes and functionalities of variables that are used in data
    processing and analysis. It allows for the standardized handling of variables, including their definition,
    categorization, and value computation. Variables can be either built-in or custom-defined, and they may also
    be indexed to represent a series of values rather than a single value.

    Attributes:
        data_provider (str): Identifier for the data provider to which the variable belongs.
        category (str): A classification or grouping for the variable, aiding in its organization.
        type (str): Specifies whether the variable is 'Builtin' or 'Custom', indicating its origin.
        name (str): The unique name of the variable, used for identification.
        description (str): A brief description of the variable, explaining its purpose or usage.
        data_type (str): The type of data the variable represents (e.g., 'Number', 'Text', 'Date').
        test_value_placeholder (str): A placeholder value used for testing or in documentation, which may include
            an index for indexed variables.
        info (str): Additional information about the variable, typically displayed in a UI element like an info bubble.
        is_indexed_variable (bool): Indicates whether the variable is indexed, meaning it can represent multiple
            values based on an index range.
        index_start (Optional[int]): The starting index for indexed variables, defaulting to 0 if not specified.
        index_end (Optional[int]): The ending index for indexed variables, defaulting to 5 if not specified.
        value (Optional[TVariableValue]): The computed or assigned value of the variable, which can be of various
            types including string, float, int, bool, or None.

    Methods:
        __init__: Initializes a new instance of the Variable class with specified attributes.
        to_dict: Converts the variable's attributes into a dictionary format.
        __call__: An abstract method that must be implemented by subclasses to define how the variable's value
            is computed or retrieved.
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
        """
        Initializes a new instance of the Variable class with the provided attributes.

        Parameters:
            data_provider (str): The identifier for the data provider.
            category (str): The category or group to which the variable belongs.
            type (str): Indicates if the variable is 'Builtin' or 'Custom'.
            name (str): The name of the variable.
            description (str): A brief description of the variable.
            data_type (str): The type of data (e.g., 'Number', 'Text', 'Date').
            test_value_placeholder (str): A placeholder for the variable's test value.
            info (str): Additional information about the variable.
            is_indexed_variable (bool): Flag indicating if the variable is indexed.
            index_start (Optional[int]): The starting index for indexed variables.
            index_end (Optional[int]): The ending index for indexed variables.
            value (Optional[TVariableValue]): The value of the variable.

        Returns:
            None
        """
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
        """
        Converts the variable's attributes into a dictionary.

        This method facilitates the serialization of the variable's attributes, making it easier to store or
        transmit the variable's definition.

        Returns:
            dict[str, Any]: A dictionary containing the variable's attributes as key-value pairs.
        """
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
            "value": self.value,
        }

    @abstractmethod
    def __call__(self, *args, **kwargs):
        """
        An abstract method that, when implemented, computes or retrieves the variable's value.

        This method must be overridden in subclasses to provide the specific logic for calculating or retrieving
        the variable's value based on the given arguments.

        Parameters:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            The computed or retrieved value of the variable.
        """
        ...


class Operator(Enum):
    """
    Enum representing various operators used for filtering and comparison.

    Attributes:
        IS: Represents the equality operator.
        IS_NOT: Represents the inequality operator.
        IS_GREATER_THAN: Represents the greater than operator.
        IS_GREATER_THAN_OR_EQUAL_TO: Represents the greater than or equal to operator.
        IS_LESS_THAN: Represents the less than operator.
        IS_LESS_THAN_OR_EQUAL_TO: Represents the less than or equal to operator.
        CONTAINS: Represents the containment operator.
        DOES_NOT_CONTAIN: Represents the non-containment operator.
        BEGINS_WITH: Represents the begins with operator for string comparison.
        ENDS_WITH: Represents the ends with operator for string comparison.
        REGEXP: Represents the regular expression matching operator.
    """

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
    """
    Enum for defining the types of variables.

    This enumeration defines two types of variables:
    - BUILTIN: Represents a variable that is built into the system.
    - CUSTOM: Represents a variable that is defined by the user.

    Attributes:
        BUILTIN (str): A string value representing a built-in variable.
        CUSTOM (str): A string value representing a custom-defined variable.
    """

    BUILTIN = "Builtin"
    CUSTOM = "Custom"


class VariableDataType(Enum):
    """
    Enum for defining the data types of variables.

    This enumeration classifies variables into three fundamental data types:
    - NUMBER: Represents numeric data, including integers and floating-point numbers.
    - TEXT: Represents textual data.
    - DATE: Represents dates, stored in various date and time formats.

    Attributes:
        NUMBER (str): A string value representing a numeric data type.
        TEXT (str): A string value representing a textual data type.
        DATE (str): A string value representing a date data type.
    """

    NUMBER = "Number"
    TEXT = "Text"
    DATE = "Date"


# TODO: make Data inherit from Registry
class Data(ABC):
    """
    Abstract base class for data types in the system. It provides a registry for data type classes,
    methods to register and retrieve data type classes, and abstract methods for subclasses to implement
    specific behaviors.

    Attributes:
        _registry (dict[str, type]): A class-level dictionary that maps `VariableDataType` enum values to
            corresponding data type classes.
        operators (OperatorsDict): A class-level dictionary that stores operators
            and their metadata or functions for filtering and comparison.
    """

    _registry: dict[VariableDataType, "Data"] = {}
    operators: OperatorsDict = {}

    @staticmethod
    def register(data_type: VariableDataType, cls) -> None:
        """
        Registers a data type class to the `_registry` using its `VariableDataType` enum as the key.

        Parameters:
            data_type (VariableDataType): The enum value representing the data type.
            cls (type): The class to be registered for the specified data type.
        """
        Data._registry[data_type] = cls

    @staticmethod
    def get_class_by_type(data_type: VariableDataType) -> Any:
        """
        Retrieves a registered data type class from the `_registry` based on the `VariableDataType` enum.

        Parameters:
            data_type (VariableDataType): The enum value representing the data type.

        Returns:
            Any: The class registered under the specified `VariableDataType` enum.
        """
        return Data._registry[data_type]

    @classmethod
    @abstractmethod
    def get_filter_operators(cls) -> list[dict[str, Any]]:
        """
        An abstract method that subclasses should implement to return their specific filter operators.
        """
        ...

    @staticmethod
    def is_this_data_type(data) -> bool:
        """
        Checks if the given data is an instance of a class that inherits from `Data`.

        Parameters:
            data: The data to check.

        Returns:
            bool: True if `data` is an instance of a class that inherits from `Data`, False otherwise.
        """
        return isinstance(type(data), Data)

    @staticmethod
    def determine_type(value) -> TDataClass | type:
        """
        Determines the data type class for the given value based on its type or content.

        Parameters:
            value: The value whose data type class is to be determined.

        Returns:
            TDataClass | type: The data type class that best matches the given value.
        """
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

    @classmethod
    def get_all_filter_operators(cls) -> dict[Any, Any]:
        """
        Retrieves all filter operators for each registered data type class.

        Returns:
            dict[Any, Any]: A dictionary mapping data type names to their respective filter operators.
        """
        result = {}
        for data_type, class_ in cls._registry.items():
            result[data_type.value] = class_.get_filter_operators()
        return result

    @classmethod
    def get_operator(cls, operator: str) -> dict[str, str | Callable]:
        """
        Retrieves the operator function or metadata based on the operator string.

        Parameters:
            operator (str): The string identifier of the operator.

        Returns:
            dict[str, str | Callable]: The operator's metadata or function.

        Raises:
            ValueError: If the operator is not found in the `operators` dictionary.
        """
        # check if operators has the key corresponding to the operator
        if operator in cls.operators:
            return cls.operators[operator]
        else:
            raise ValueError(f"Unknown operator: {operator}")


class Date(Data):
    """
    A subclass of Data that represents date data types and provides functionality for date comparison and validation.

    Attributes:
        operators (dict): A dictionary mapping operator strings to their respective label and lambda function for
                          performing the comparison operation between two date values.
    """

    operators: OperatorsDict = {
        Operator.IS.value: {
            "label": "api.custom_variables.filters.operators.date.is",
            "func": lambda a, b: Date._parse_date(a) == Date._parse_date(b),
        },
        Operator.IS_NOT.value: {
            "label": "api.custom_variables.filters.operators.date.is_not",
            "func": lambda a, b: Date._parse_date(a) != Date._parse_date(b),
        },
        Operator.IS_GREATER_THAN.value: {
            "label": "api.custom_variables.filters.operators.date.is_after",
            "func": lambda a, b: Date._parse_date(a) > Date._parse_date(b),
        },
        Operator.IS_GREATER_THAN_OR_EQUAL_TO.value: {
            "label": "api.custom_variables.filters.operators.date.is_on_or_after",
            "func": lambda a, b: Date._parse_date(a) >= Date._parse_date(b),
        },
        Operator.IS_LESS_THAN.value: {
            "label": "api.custom_variables.filters.operators.date.is_before",
            "func": lambda a, b: Date._parse_date(a) < Date._parse_date(b),
        },
        Operator.IS_LESS_THAN_OR_EQUAL_TO.value: {
            "label": "api.custom_variables.filters.operators.date.is_on_or_before",
            "func": lambda a, b: Date._parse_date(a) <= Date._parse_date(b),
        },
    }

    @staticmethod
    def is_this_data_type(data: str) -> bool:
        """
        Determines if the given data can be parsed as a date.

        Parameters:
            data (str): The data to be checked.

        Returns:
            bool: True if the data can be parsed as a date, False otherwise.
        """
        try:
            Date._parse_date(data)
            return True
        except ValueError:
            return False

    @staticmethod
    def _parse_date(date_str: str) -> datetime:
        """
        Parses a string into a datetime object using predefined date formats.

        Parameters:
            date_str (str): The date string to be parsed.

        Returns:
            datetime: A datetime object representing the parsed date.

        Raises:
            ValueError: If the date string does not match any of the predefined formats.
        """
        if isinstance(date_str, int):
            try:
                return datetime.fromtimestamp(date_str)
            except ValueError:
                pass

        try:
            return datetime.fromisoformat(date_str)
        except ValueError:
            pass


        formats = [
            "%Y-%m-%d",
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%S.%f%z",
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M:%S.%f",
            "%Y%m%d",
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                pass
        raise ValueError(f"Unknown date format: {date_str}")

    @classmethod
    def get_filter_operators(cls, operator=None) -> list[dict[str, Any]]:
        """
        Converts the operators dictionary to a list format suitable for filtering operations.

        Parameters:
            operator (Optional[str]): An optional operator string to filter the operators list by. If not provided,
                                      all operators are returned.

        Returns:
            list[dict[str, Any]]: A list of dictionaries, each representing an operator with its label and value.
        """
        # Convert the operators dictionary to the desired list format
        return [
            {"label": op_info["label"], "value": op_key}
            for op_key, op_info in cls.operators.items()
        ]


class Number(Data):
    """
    Represents numeric data types and provides functionality for numeric comparison and validation.

    This class inherits from the abstract base class `Data` and implements methods and properties specific to numeric data types.
    It defines a set of operators for numeric comparison and provides methods to check if a given data is a numeric type and to parse numeric values.
    """

    operators: OperatorsDict = {
        Operator.IS.value: {
            "label": "api.custom_variables.filters.operators.number.is",
            "func": lambda a, b: Number._parse_number(a) == Number._parse_number(b),
        },
        Operator.IS_NOT.value: {
            "label": "api.custom_variables.filters.operators.number.is_not",
            "func": lambda a, b: Number._parse_number(a) != Number._parse_number(b),
        },
        Operator.IS_GREATER_THAN.value: {
            "label": "api.custom_variables.filters.operators.number.is_greater_than",
            "func": lambda a, b: Number._parse_number(a) > Number._parse_number(b),
        },
        Operator.IS_GREATER_THAN_OR_EQUAL_TO.value: {
            "label": "api.custom_variables.filters.operators.number.is_greater_than_or_equal_to",
            "func": lambda a, b: Number._parse_number(a) >= Number._parse_number(b),
        },
        Operator.IS_LESS_THAN.value: {
            "label": "api.custom_variables.filters.operators.number.is_less_than",
            "func": lambda a, b: Number._parse_number(a) < Number._parse_number(b),
        },
        Operator.IS_LESS_THAN_OR_EQUAL_TO.value: {
            "label": "api.custom_variables.filters.operators.number.is_less_than_or_equal_to",
            "func": lambda a, b: Number._parse_number(a) <= Number._parse_number(b),
        },
    }

    @staticmethod
    def is_this_data_type(data) -> bool:
        """
        Checks if the given data can be parsed as a numeric value.

        Parameters:
            data: The data to be checked, which can be of any type.

        Returns:
            bool: True if the data can be parsed as a numeric value, False otherwise.
        """
        try:
            float(data)
            return True
        except ValueError:
            return False

    @staticmethod
    def _parse_number(numeric_value: Union[int, float, str]) -> Union[int, float]:
        """
        Parses the given numeric value to an integer or float.

        Parameters:
            numeric_value (Union[int, float, str]): The numeric value to be parsed, which can be an integer, float, or string.

        Returns:
            Union[int, float]: The parsed numeric value as an integer or float, depending on the input value.

        Note:
            If the input is a string that represents an integer, it will be converted to an integer.
            Otherwise, it will be converted to a float.
        """
        if isinstance(numeric_value, int) or isinstance(numeric_value, float):
            return numeric_value

        return int(numeric_value) if numeric_value.isnumeric() else float(numeric_value)

    @classmethod
    def get_filter_operators(cls, operator=None) -> list[dict[str, Any]]:
        """
        Converts the operators dictionary to a list format suitable for filtering operations.

        Parameters:
            operator (Optional[str]): An optional operator string to filter the operators list by. If not provided,
                                      all operators are returned.

        Returns:
            list[dict[str, Any]]: A list of dictionaries, each representing an operator with its label and value.
        """
        return [
            {"label": op_info["label"], "value": op_key}
            for op_key, op_info in cls.operators.items()
        ]


class Text(Data):
    """
    Represents textual data types and provides functionality for text comparison and validation.

    This class inherits from the abstract base class `Data` and implements methods and properties specific to textual data types.
    It defines a set of operators for text comparison and provides methods to check if a given data is a textual type and to perform text-specific operations.
    """

    operators: OperatorsDict = {
        Operator.IS.value: {
            "label": "api.custom_variables.filters.operators.text.is",
            "func": lambda a, b: a == b,
        },
        Operator.IS_NOT.value: {
            "label": "api.custom_variables.filters.operators.text.is_not",
            "func": lambda a, b: a != b,
        },
        Operator.CONTAINS.value: {
            "label": "api.custom_variables.filters.operators.text.contains",
            "func": lambda a, b: b in a,
        },
        Operator.DOES_NOT_CONTAIN.value: {
            "label": "api.custom_variables.filters.operators.text.does_not_contain",
            "func": lambda a, b: b not in a,
        },
        Operator.BEGINS_WITH.value: {
            "label": "api.custom_variables.filters.operators.text.begins_with",
            "func": lambda a, b: a.startswith(b),
        },
        Operator.ENDS_WITH.value: {
            "label": "api.custom_variables.filters.operators.text.ends_with",
            "func": lambda a, b: a.endswith(b),
        },
        Operator.REGEXP.value: {
            "label": "api.custom_variables.filters.operators.text.regexp",
            "func": lambda a, b: re.match(b, a),
        },
    }

    @staticmethod
    def is_this_data_type(data) -> bool:
        """
        Determines if the given data is of textual type.

        Parameters:
            data: The data to be checked, which can be of any type.

        Returns:
            bool: True if the data is a string, indicating it is of textual type; False otherwise.
        """
        return isinstance(data, str)

    @classmethod
    def get_filter_operators(cls, operator=None) -> list[dict[str, Any]]:
        """
        Converts the operators dictionary to a list format suitable for filtering operations.

        Parameters:
            operator (Optional[str]): An optional operator string to filter the operators list by. If not provided,
                                      all operators are returned.

        Returns:
            list[dict[str, Any]]: A list of dictionaries, each representing an operator with its label and value.
        """
        return [
            {"label": op_info["label"], "value": op_key}
            for op_key, op_info in cls.operators.items()
        ]


# Register the specific data type classes with the Data class.
# This registration process maps the `VariableDataType` enum values (DATE, NUMBER, TEXT) to their corresponding
# data type classes (Date, Number, Text). This mapping is essential for the system to dynamically identify and
# utilize the correct data type class based on the variable's data type during runtime.
Data.register(VariableDataType.DATE, Date)
Data.register(VariableDataType.NUMBER, Number)
Data.register(VariableDataType.TEXT, Text)
