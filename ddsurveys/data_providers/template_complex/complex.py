#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2024-05-12 20:52

@author: Lev Velykoivanenko (velykoivanenko.lev@gmail.com)
"""
__all__ = ["TemplateComplexDataProvider"]

from functools import cached_property
from typing import Any, Callable, Dict

import requests

from ...get_logger import get_logger
from ...variable_types import TVariableFunction, VariableDataType
from ..bases import FormField, OAuthDataProvider
from ..data_categories import DataCategory
from ..variables import BuiltInVariable, CVAttribute

# Import the required libraries to make this work
from .api import MyAPI

logger = get_logger(__name__)


# This is an example of a data category.
# In practice, each endpoint can be turned into a data category.
class ExampleAccount(DataCategory):

    data_origin = [
        {
            "method": "get_user",
            "endpoint": "https://api.dataprovider.com/account",
            "documentation": "https://docs.dataprovider.com/en/rest/reference/account",
        }
    ]

    custom_variables_enabled = False

    api = None

    def fetch_data(self) -> list[dict[str, Any]]:
        user = self.api.get_user()
        return user

    cv_attributes = [
        CVAttribute(
            name="name",
            label="Users Name",
            description="The name of the user.",
            attribute="name",
            data_type=VariableDataType.TEXT,
            test_value_placeholder="Username",
            info="The name of the user.",
        ),
        CVAttribute(
            label="Creation Date",
            description="The date the repository was created.",
            attribute="created_at",
            name="creation_date",
            data_type=VariableDataType.DATE,
            test_value_placeholder="2023-01-10T12:00:00.000",
            info="The date the account was created.",
        ),
    ]

    builtin_variables = [
        BuiltInVariable.create_instances(
            name="creation_date",
            label="Account creation date",
            description="The date the user created their account.",
            test_value_placeholder="2020-01-01",
            data_type=VariableDataType.DATE,
            info="The date the account was created. It will be in the format YYYY-MM-DD.",
            is_indexed_variable=False,
            extractor_func=lambda self: self.account_creation_date,
            data_origin=[],
        )
    ]


class TemplateComplexDataProvider(OAuthDataProvider):
    # Class attributes that need be redeclared or redefined in child classes
    # The following attributes need to be redeclared in child classes.
    # You can just copy and paste them into the child class body.
    # When copying a template file, leave them unchanged.
    all_initial_funcs: dict[str, Callable] = {}
    factory_funcs: dict[str, Callable] = {}
    variable_funcs: dict[str, TVariableFunction] = {}
    fields: list[dict[str, Any]] = {}

    # Update the following attributes:
    app_creation_url: str = "https://dataprovider.com/settings/apps/new"
    instructions_helper_url: str = (
        "https://docs.dataprovider.com/en/apps/creating-dataprovider-apps/"
    )

    # Unique class attributes go here
    _scopes = []

    # See other classes for examples of how to fill these attributes. You may not need to fill them
    _categories_scopes = {}

    # Form fields that will be displayed in the frontend. Only update them if the data provider uses different
    # terminology for this information.
    form_fields = [
        FormField(name="client_id", type="text", required=True, data={}),
        FormField(name="client_secret", type="text", required=True, data={}),
    ]

    # List all the data categories that this data provider supports.
    # Enter the names of the classes.
    data_categories = [
        ExampleAccount,
    ]

    # In the functions below, update the elipses (...) with the correct classes and code.
    def __init__(self, **kwargs):
        """

        Args:
            client_id:
            client_secret:
            access_token:
            refresh_token:
            **kwargs:
        """
        super().__init__(**kwargs)
        self.api_client: ...
        self.oauth_client: ...
        self.redirect_uri = self.get_redirect_uri()

        self.init_oauth_client()

        if self.access_token is not None and self.refresh_token is not None:
            self.init_api_client(self.access_token, self.refresh_token)

    # OAuthBase methods
    def init_api_client(
        self, access_token: str = None, refresh_token: str = None, code: str = None
    ) -> None:
        ...

        self.api_client = ...

    def init_oauth_client(self, *args, **kwargs) -> None:
        ...

        self.oauth_client = ...

    def get_authorize_url(
        self, builtin_variables: list[dict], custom_variables: list[dict] = None
    ) -> str: ...

    def get_client_id(self) -> str: ...

    def request_token(self, code: str) -> Dict[str, Any]: ...

    def revoke_token(self, token: str) -> bool: ...

    # DataProvider methods
    def test_connection_before_extraction(self) -> bool: ...

    def test_connection(self) -> bool: ...

    @cached_property
    def get_user_repositories(self) -> list: ...

    def repositories_by_stars(self, idx: int) -> str: ...

    @cached_property
    def account_creation_date(self) -> str: ...

