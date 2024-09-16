#!/usr/bin/env python3
"""Created on 2024-07-24 13:53.

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
"""
from typing import TYPE_CHECKING, TypedDict, TypeVar

from typings.data_providers.variables import BuiltinVariableDict, CVAttributeDict, DataOriginDict

if TYPE_CHECKING:
    from ddsurveys.data_providers.bases import DataProvider, OAuthDataProvider

    TDataProviderClass = type[DataProvider]
    TDataProvider = TypeVar("TDataProvider", bound=DataProvider)
    TOAuthDataProviderClass = type[OAuthDataProvider]

    TOAuthDataProvider = TypeVar("TOAuthDataProvider", bound=OAuthDataProvider)

__all__ = [
    "TDataProviderClass",
    "TOAuthDataProviderClass",
    "TDataProvider",
    "TOAuthDataProvider",

    "DataProviderDataCategoryDict"
]


class DataProviderDataCategoryDict(TypedDict):
    label: str
    value: str
    custom_variables_enabled: bool
    builtin_variables: list[BuiltinVariableDict]
    cv_attributes: list[CVAttributeDict]
    data_origin: list[DataOriginDict]
    data_provider_name: str


