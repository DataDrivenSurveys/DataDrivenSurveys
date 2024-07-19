#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from abc import abstractmethod
from functools import cached_property
from typing import Any, TypeVar

__all__ = ["DataCategory"]


TDataCategoryClass = type["DataCategory"]
TDataCategory = TypeVar("TDataCategory", bound="DataCategory")


class DataCategoryBase(type):
    def __new__(mcs, name, bases, attrs):
        # Code partially based on django.db.models.base.ModelBase
        super_new = super().__new__

        # Also ensure initialization is only performed for subclasses of Model
        # (excluding Model class itself).
        parents = [b for b in bases if isinstance(b, DataCategoryBase)]
        if len(parents) == 0:
            return super_new(mcs, name, bases, attrs)

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

        return super().__new__(mcs, name, bases, attrs)


class DataCategory(metaclass=DataCategoryBase):
    data_origin: list[dict[str, Any]] = []
    """Data origin of the fetch_data method"""

    custom_variables_enabled: bool = True
    """Whether custom variables should be enabled in the frontend UI.
    If cv_attributes is empty, this will automatically be set to False.
    If custom_variables_enabled was manually set to False, it will not be overridden."""

    label: str = ""
    value: str = ""

    api = None
    """Instance of the API from the container DataProvider class."""

    cv_attributes: list[TDataCategory] = []
    builtin_variables: list[list[TDataCategory]] = []

    def __init__(self, data_provider) -> None:
        self.data_provider = data_provider

    def __str__(self):
        return f"{self.__class__.__name__}(data_provider={self.data_provider})"

    __repr__ = __str__

    @cached_property
    @abstractmethod
    def fetch_data(self) -> list[dict[str, Any]]:
        return []

    @classmethod
    def get_by_value(cls, value: str) -> TDataCategoryClass:
        for subclass in cls.__subclasses__():
            if subclass.value == value:
                return subclass

    @classmethod
    def to_dict(cls):
        data_category_name = cls.__name__

        return {
            "label": cls.label,
            "value": cls.value,
            "custom_variables_enabled": cls.custom_variables_enabled,
            "cv_attributes": [
                cls._include_data_category(prop.to_dict(), data_category_name)
                for prop in cls.cv_attributes
            ],
            "builtin_variables": [
                cls._include_data_category(variable.to_dict(), data_category_name)
                for variables in cls.builtin_variables
                for variable in variables
            ],
            "data_origin": cls.data_origin,
        }

    @staticmethod
    def _include_data_category(variable_dict, data_category_name):
        variable_dict["category"] = data_category_name
        return variable_dict

    @classmethod
    def get_custom_variable_by_name(cls, name):
        # Check in custom attributes
        for var in cls.cv_attributes:
            if var.name == name:
                return var

        # If not found
        raise ValueError(f"Variable {name} not found in {cls.__name__}")

    @classmethod
    def get_builtin_variable_by_name(cls, name):
        # Check in builtin attributes
        for var_list in cls.builtin_variables:
            for var in var_list:
                if var.name == name:
                    return var

        # If not found
        raise ValueError(f"Variable {name} not found in {cls.__name__}")
