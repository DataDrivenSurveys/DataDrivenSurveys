#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from functools import cached_property
from typing import Any, Type, TypeVar, List, Dict
from abc import abstractmethod

__all__ = [
   "DataCategory"
]


TDataCategoryClass = Type["DataCategory"]
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
        return super().__new__(mcs, name, bases, attrs)


class DataCategory(metaclass=DataCategoryBase):
    """data origin of the fetch_data method """
    data_origin: List[Dict[str, Any]] = []

    custom_variables_enabled: bool = True
    """Whether custom variables should be enabled in the frontend UI."""

    label: str = ""
    value: str = ""

    api = None
    """Instance of the API from the container DataProvider class."""

    cv_attributes: list[TDataCategory] = []
    builtin_variables: list[list[TDataCategory]] = []

    def __init__(self, data_provider):
        self.data_provider = data_provider

    @abstractmethod
    @cached_property
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
            "cv_attributes": [cls._include_data_category(prop.to_dict(), data_category_name) for prop in cls.cv_attributes],
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
