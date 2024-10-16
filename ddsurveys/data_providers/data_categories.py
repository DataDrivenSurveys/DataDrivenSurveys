"""This module defines the DataCategory class and related types.

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
@author: Stefan Teofanovic (stefan.teofanovic@heig-vd.ch).
"""

from __future__ import annotations

from abc import ABC, ABCMeta, abstractmethod
from typing import TYPE_CHECKING, Any, ClassVar, TypedDict, TypeVar

from ddsurveys.get_logger import get_logger

if TYPE_CHECKING:
    from ddsurveys.data_providers.bases import DataProvider
    from ddsurveys.data_providers.variables import BuiltInVariable, CVAttribute
    from ddsurveys.typings.data_providers.variables import BuiltinVariableDict, CVAttributeDict, DataOriginDict

__all__ = [
    "DataCategory",
    #
    "DataCategoryDict",
    "TDataCategoryClass",
    "TDataCategory",
]

logger = get_logger(__name__)


class DataCategoryDict(TypedDict):
    label: str
    value: str
    custom_variables_enabled: bool
    builtin_variables: list[BuiltinVariableDict]
    cv_attributes: list[CVAttributeDict]
    data_origin: list[DataOriginDict]


class DataCategoryBase(ABCMeta):
    def __new__(cls, name: str, bases: tuple[type], attrs: dict[str, Any]):
        # Code partially based on django.db.models.base.ModelBase
        super_new = super().__new__

        # Also ensure initialization is only performed for subclasses of Model
        # (excluding Model class itself).
        parents = [b for b in bases if isinstance(b, DataCategoryBase)]
        if len(parents) == 0:
            return super_new(cls, name, bases, attrs)

        attrs["label"] = name
        attrs["value"] = name.lower()

        # Set custom_variables_enabled based on cv_attributes attribute.
        if "cv_attributes" in attrs:
            if attrs.get("custom_variables_enabled", False):
                attrs["custom_variables_enabled"] = len(attrs["cv_attributes"]) > 0
            else:
                attrs["custom_variables_enabled"] = len(attrs["cv_attributes"]) > 0
        elif len(bases) == 1:
            attrs["custom_variables_enabled"] = False

        return super().__new__(cls, name, bases, attrs)


class DataCategory(ABC, metaclass=DataCategoryBase):
    data_origin: ClassVar[list[DataOriginDict]] = []
    """Data origin of the fetch_data method"""

    custom_variables_enabled: bool = True
    """Whether custom variables should be enabled in the frontend UI.
    If cv_attributes is empty, this will automatically be set to False.
    If custom_variables_enabled was manually set to False, it will not be overridden."""

    label: str = ""
    value: str = ""

    api: ClassVar[DataProvider] = None
    """Instance of the API from the container DataProvider class."""

    # data_provider: ClassVar[DataProvider] = None
    # """Instance of the DataProvider class."""

    cv_attributes: ClassVar[list[CVAttribute]] = []
    builtin_variables: ClassVar[list[list[BuiltInVariable]]] = []

    def __init__(self, data_provider: DataProvider) -> None:
        self.data_provider: DataProvider = data_provider
        # self.__class__.data_provider = data_provider

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(data_provider={self.data_provider})"

    __repr__ = __str__

    @abstractmethod
    def fetch_data(self) -> list[dict[str, Any]]: ...

    @classmethod
    def get_by_value(cls, value: str) -> TDataCategoryClass:
        for subclass in cls.__subclasses__():
            if subclass.value == value:
                return subclass
        msg: str = f"DataCategory with value {value} not found"
        logger.error(msg)
        raise ValueError(msg)

    @classmethod
    def to_dict(cls) -> DataCategoryDict:
        return {
            "label": cls.label,
            "value": cls.value,
            "custom_variables_enabled": cls.custom_variables_enabled,
            "builtin_variables": [
                cls._include_builtin_variable_category(variable.to_dict(), cls.label)
                for variables in cls.builtin_variables
                for variable in variables
            ],
            "cv_attributes": [
                cls._include_cv_attribute_category(cv_attribute.to_dict(), cls.label)
                for cv_attribute in cls.cv_attributes
            ],
            "data_origin": cls.data_origin,
        }

    @staticmethod
    def _include_builtin_variable_category(d_: BuiltinVariableDict, category: str) -> BuiltinVariableDict:
        d_["category"] = category
        return d_

    @staticmethod
    def _include_cv_attribute_category(d_: CVAttributeDict, category: str) -> CVAttributeDict:
        d_["category"] = category
        return d_

    @classmethod
    def get_custom_variable_by_name(cls, name: str) -> CVAttribute:
        # Check in custom attributes
        for var in cls.cv_attributes:
            if var.name == name:
                return var

        # If not found
        msg: str = f"Variable {name} not found in {cls.__name__}"
        raise ValueError(msg)

    @classmethod
    def get_builtin_variable_by_name(cls, name: str) -> BuiltInVariable:
        # Check in builtin attributes
        for var_list in cls.builtin_variables:
            for var in var_list:
                if var.name == name:
                    return var

        # If not found
        msg: str = f"Variable {name} not found in {cls.__name__}"
        raise ValueError(msg)


# Type hint for subclasses of DataCategory
TDataCategoryClass = type[DataCategory]
TDataCategory = TypeVar("TDataCategory", bound=DataCategory)
