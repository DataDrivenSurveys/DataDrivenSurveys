#!/usr/bin/env python3
"""Created on 2024-07-24 13:44.

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, TypeAlias, TypedDict, TypeVar

from ddsurveys.variable_types import Data

if TYPE_CHECKING:
    from collections.abc import Callable

__all__ = [
    # TypedDict exports
    "OperatorDict",
    "OperatorsDict",

    # Variable specification class exports
    "Variable",
    "VariableFunction",

    # Type and TypeVar exports
    "TData",
    "TDataClass",
    "TVariable",
    "TVariableFunction",
    "TVariableValue",
]


class OperatorDict(TypedDict):
    label: str
    func: Callable[[TVariableValue, TVariableValue], bool]


OperatorsDict: TypeAlias = dict[str, OperatorDict]


class VariableFunction(ABC):
    """This class is used for type hinting only and should not be used directly.

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
        index_start: int | None = None,
        index_end: int | None = None,
        *,
        is_indexed_variable: bool = False,
        fully_indexed: bool = False,
        **kwargs: Any,
    ) -> None:
        """Initializes a new instance of the VariableFunction class.

        Parameters:
            variable_name (str): The name of the variable to be calculated. Defaults to an empty string.
            is_indexed_variable (bool, optional): Flag indicating whether the variable is indexed. Defaults to None.
            index_start (int, optional): The starting index for indexed variables. Defaults to None.
            index_end (int, optional): The ending index for indexed variables. Defaults to None.
            fully_indexed (bool): Flag indicating whether all indexed references of the variable have been fully added. Defaults to False.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        super().__init__(**kwargs)
        self.variable_name: str = variable_name
        self.is_indexed_variable: bool = is_indexed_variable
        self.index_start: int = index_start
        self.index_end: int = index_end
        self.fully_indexed: bool = fully_indexed

    @abstractmethod
    def __call__(self, *args: Any, **kwargs: Any) -> TVariableValue:
        """Abstract method that when implemented, should calculate and return the value of the variable.

        This method must be overridden by subclasses to provide the specific logic for calculating the variable's value.

        Parameters:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            TVariableValue: The calculated value of the variable. This can be of type Union[str, float, int, bool, None].
        """
        ...


class Variable(ABC):
    """A class to define the structure and behavior of variables within a data provider context.

    This class is designed to encapsulate the attributes and functionalities of variables that are used in data
    processing and analysis. It allows for the standardized handling of variables, including their definition,
    categorization, and value computation. Variables can be either built-in or custom-defined, and they may also
    be indexed to represent a series of values rather than a single value.

    Attributes:
        data_provider (str): Identifier for the data provider to which the variable belongs.
        category (str): A classification or grouping for the variable, aiding in its organization.
        type_ (str): Specifies whether the variable is 'Builtin' or 'Custom', indicating its origin.
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
        type_: str = "",
        name: str = "",
        description: str = "",
        data_type: str = "",
        value: TVariableValue | None = None,
        test_value_placeholder: str = "",
        info: str = "",
        *,
        is_indexed_variable: bool = False,
        index_start: int | None = 0,
        index_end: int | None = 5,
    ) -> None:
        """Initializes a new instance of the Variable class with the provided attributes.

        Parameters:
            data_provider (str): The identifier for the data provider.
            category (str): The category or group to which the variable belongs.
            type_ (str): Indicates if the variable is 'Builtin' or 'Custom'.
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
        self.type_: str = type_
        self.name: str = name
        self.description: str = description
        self.data_type: str = data_type
        self.value: TVariableValue | None = value
        self.test_value_placeholder: str = test_value_placeholder
        self.info: str = info
        self.is_indexed_variable: bool = is_indexed_variable
        self.index_start: int | None = index_start
        self.index_end: int | None = index_end

    def to_dict(self) -> dict[str, Any]:
        """Converts the variable's attributes into a dictionary.

        This method facilitates the serialization of the variable's attributes, making it easier to store or
        transmit the variable's definition.

        Returns:
            dict[str, Any]: A dictionary containing the variable's attributes as key-value pairs.
        """
        return {
            "data_provider": self.data_provider,
            "category": self.category,
            "type": self.type_,
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
    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """An abstract method that, when implemented, computes or retrieves the variable's value.

        This method must be overridden in subclasses to provide the specific logic for calculating or retrieving
        the variable's value based on the given arguments.

        Parameters:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            The computed or retrieved value of the variable.
        """
        ...


# Class types (used for type hinting that something is that class object)
TDataClass = type[Data]

# TypeVars (used for type hinting that something is an instance of that class)
TVariableValue: TypeAlias = str | float | int | bool | None
TVariableFunction = TypeVar("TVariableFunction", bound=VariableFunction)
TVariable = TypeVar("TVariable", bound=Variable)
TData = TypeVar("TData", bound=Data)
