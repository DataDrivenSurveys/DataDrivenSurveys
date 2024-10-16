"""This module contains classes that are specs for important types and data standards, type declarations,
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

from __future__ import annotations

import re
from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, ClassVar, TypeVar

from ddsurveys.get_logger import get_logger

if TYPE_CHECKING:
    from ddsurveys.typings.variable_types import OperatorDict, OperatorsDict


__all__: list[str] = [
    # Enum class exports
    "Operator",
    "VariableType",
    "VariableDataType",
    # Data type class exports
    "Data",
    "Date",
    "Number",
    "Text",
    #
    "TDataClass",
    "TData",
]


logger = get_logger(__name__)


class Operator(Enum):
    """Enum representing various operators used for filtering and comparison.

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
    """Enum for defining the types of variables.

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
    """Enum for defining the data types of variables.

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
class Data:
    """Base class for data types in the system. It provides a registry for data type classes,
    methods to register and retrieve data type classes, and abstract methods for subclasses to implement
    specific behaviors.

    Attributes:
        _registry (dict[str, type]): A class-level dictionary that maps `VariableDataType` enum values to
            corresponding data type classes.
        operators (OperatorsDict): A class-level dictionary that stores operators
            and their metadata or functions for filtering and comparison.
    """

    _registry: ClassVar[dict[VariableDataType, TDataClass]] = {}
    operators: ClassVar[OperatorsDict] = {}

    @staticmethod
    def register(data_type: VariableDataType, class_: TDataClass) -> None:
        """Registers a data type class to the `_registry` using its `VariableDataType` enum as the key.

        Parameters:
            data_type (VariableDataType): The enum value representing the data type.
            class_ (type): The class to be registered for the specified data type.
        """
        Data._registry[data_type] = class_

    @staticmethod
    def get_class_by_type(data_type: VariableDataType) -> Any:
        """Retrieves a registered data type class from the `_registry` based on the `VariableDataType` enum.

        Parameters:
            data_type (VariableDataType): The enum value representing the data type.

        Returns:
            Any: The class registered under the specified `VariableDataType` enum.
        """
        return Data._registry[data_type]

    @classmethod
    def get_filter_operators(cls, operator: str = "") -> list[dict[str, Any]]:
        """Converts the operators dictionary to a list format suitable for filtering operations.

        Parameters:
            operator (Optional[str]): An optional operator string to filter the operators list by. If not provided,
                                      all operators are returned.

        Returns:
            list[dict[str, Any]]: A list of dictionaries, each representing an operator with its label and value.
        """
        if operator != "":
            return [
                {"label": op_info["label"], "value": op_key}
                for op_key, op_info in cls.operators.items()
                if op_key == operator
            ]
        # Convert the operators dictionary to the desired list format
        return [{"label": op_info["label"], "value": op_key} for op_key, op_info in cls.operators.items()]

    @classmethod
    def is_this_data_type(cls, data: Any) -> bool:
        """Checks if the given data is an instance of a class that inherits from `Data`.

        Parameters:
            data: The data to check.

        Returns:
            bool: True if `data` is an instance of a class that inherits from `Data`, False otherwise.
        """
        return isinstance(data, cls)

    @staticmethod
    def determine_type(value: Any) -> type[list | dict] | TDataClass:
        """Determines the data type class for the given value based on its type or content.

        Parameters:
            value: The value whose data type class is to be determined.

        Returns:
            TDataClass | type: The data type class that best matches the given value.
        """
        if Data.is_this_data_type(value):
            return Data
        if isinstance(value, list):
            return list
        if isinstance(value, dict):
            return dict
        if Date.is_this_data_type(value):
            return Date
        if Number.is_this_data_type(value):
            return Number
        if Text.is_this_data_type(value):
            return Text
        logger.error("Unable to determine data type for value: %s", value)
        return Text

    @classmethod
    def get_all_filter_operators(cls) -> dict[str, Any]:
        """Retrieves all filter operators for each registered data type class.

        Returns:
            dict[Any, Any]: A dictionary mapping data type names to their respective filter operators.
        """
        result = {}
        for data_type, class_ in cls._registry.items():
            result[data_type.value] = class_.get_filter_operators()
        return result

    @classmethod
    def get_operator(cls, operator: str) -> OperatorDict:
        """Retrieves the operator function and metadata based on the operator name.

        Parameters:
            operator (str): The string identifier of the operator.

        Returns:
            dict[str, OperatorDict]: The operator's metadata or function.

        Raises:
            KeyError: If the operator is not found in the `operators` dictionary.
        """
        if operator in cls.operators:
            return cls.operators[operator]

        msg = f"Unknown operator: {operator}"
        raise KeyError(msg)


class Date(Data):
    """A subclass of Data that represents date data types and provides functionality for date comparison and validation.

    Attributes:
        operators (dict): A dictionary mapping operator strings to their respective label and lambda function for
                          performing the comparison operation between two date values.
    """

    operators: ClassVar[OperatorsDict] = {
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

    @classmethod
    def is_this_data_type(cls, data: str) -> bool:
        """Determines if the given data can be parsed as a date.

        Parameters:
            data (str): The data to be checked.

        Returns:
            bool: True if the data can be parsed as a date, False otherwise.
        """
        try:
            cls._parse_date(data)
        except ValueError:
            return False
        else:
            return True

    @staticmethod
    def _parse_date(date_str: str) -> datetime:
        """Parses a string into a datetime object using predefined date formats.

        Parameters:
            date_str (str): The date string to be parsed.

        Returns:
            datetime: A datetime object representing the parsed date.

        Raises:
            ValueError: If the date string does not match any of the predefined formats.
        """
        if isinstance(date_str, int):
            try:
                return datetime.fromtimestamp(date_str, tz=UTC)
            except ValueError:
                pass

        try:
            return datetime.fromisoformat(date_str)
        except ValueError:
            pass

        formats = [
            "%Y-%m-%d",
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M:%S.%f",
            "%Y%m%d",
        ]

        formats_with_tz = [
            "%Y-%m-%dT%H:%M:%S.%f%z",
            "%Y-%m-%dT%H:%M:%S%z",
        ]

        for fmt_with_tz in formats_with_tz:
            try:
                return datetime.strptime(date_str, fmt_with_tz)  # noqa: DTZ007
            except ValueError:
                pass

        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt).replace(tzinfo=UTC)
            except ValueError:
                pass
        msg = f"Unknown date format: {date_str}"
        raise ValueError(msg)


class Number(Data):
    """Represents numeric data types and provides functionality for numeric comparison and validation.

    This class inherits from the abstract base class `Data` and implements methods and properties specific to numeric data types.
    It defines a set of operators for numeric comparison and provides methods to check if a given data is a numeric type and to parse numeric values.
    """

    operators: ClassVar[OperatorsDict] = {
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

    @classmethod
    def is_this_data_type(cls, data: Any) -> bool:
        """Checks if the given data can be parsed as a numeric value.

        Parameters:
            data: The data to be checked, which can be of any type.

        Returns:
            bool: True if the data can be parsed as a numeric value, False otherwise.
        """
        try:
            float(data)
        except ValueError:
            return False
        else:
            return True

    @staticmethod
    def _parse_number(numeric_value: float | str) -> int | float:
        """Parses the given numeric value to an integer or float.

        Parameters:
            numeric_value (Union[int, float, str]): The numeric value to be parsed, which can be an integer, float, or string.

        Returns:
            Union[int, float]: The parsed numeric value as an integer or float, depending on the input value.

        Note:
            If the input is a string that represents an integer, it will be converted to an integer.
            Otherwise, it will be converted to a float.
        """
        if isinstance(numeric_value, float | int):
            return numeric_value

        return int(numeric_value) if numeric_value.isnumeric() else float(numeric_value)


class Text(Data):
    """Represents textual data types and provides functionality for text comparison and validation.

    This class inherits from the abstract base class `Data` and implements methods and properties specific to textual data types.
    It defines a set of operators for text comparison and provides methods to check if a given data is a textual type and to perform text-specific operations.
    """

    operators: ClassVar[OperatorsDict] = {
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
            "func": lambda a, b: re.match(b, a) is not None,
        },
    }

    @classmethod
    def is_this_data_type(cls, data: Any) -> bool:
        """Determines if the given data is of textual type.

        Parameters:
            data: The data to be checked, which can be of any type.

        Returns:
            bool: True if the data is a string, indicating it is of textual type; False otherwise.
        """
        return isinstance(data, str | Text)


# Register the specific data type classes with the Data class.
# This registration process maps the `VariableDataType` enum values (DATE, NUMBER, TEXT) to their corresponding
# data type classes (Date, Number, Text). This mapping is essential for the system to dynamically identify and
# utilize the correct data type class based on the variable's data type during runtime.
Data.register(VariableDataType.DATE, Date)
Data.register(VariableDataType.NUMBER, Number)
Data.register(VariableDataType.TEXT, Text)

TDataClass = type[Data]
TData = TypeVar("TData", bound=Data)
