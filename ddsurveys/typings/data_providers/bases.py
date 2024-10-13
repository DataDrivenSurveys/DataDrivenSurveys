"""Created on 2024-07-24 13:53.

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
"""
from typing import TYPE_CHECKING, TypeVar

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
]





