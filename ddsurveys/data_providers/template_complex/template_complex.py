#!/usr/bin/env python3
"""Created on 2024-05-12 20:52
You will need to replace the elipses (...) with the correct classes and code.

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
"""
__all__ = ["TemplateComplexDataProvider"]

from collections.abc import Callable
from functools import cached_property
from typing import Any

from ddsurveys.data_providers.bases import FormField, OAuthDataProvider

# Import the required libraries to make this work
from ddsurveys.data_providers.template_complex.data_category import ExampleDataCategory
from ddsurveys.get_logger import get_logger
from ddsurveys.variable_types import TVariableFunction

logger = get_logger(__name__)


class TemplateComplexDataProvider(OAuthDataProvider):
    # Class attributes that need be re-declared or redefined in child classes
    # The following attributes need to be re-declared in child classes.
    # You can just copy and paste them into the child class body.
    # When copying a template file, leave them unchanged.
    all_initial_funcs: dict[str, Callable] = {}  # Leave unchanged.
    factory_funcs: dict[str, Callable] = {}  # Leave unchanged.
    variable_funcs: dict[str, TVariableFunction] = {}  # Leave unchanged.
    fields: list[dict[str, Any]] = {}  # Leave unchanged.

    # Update the following attributes:
    app_creation_url: str = ...  # e.g., "https://dataprovider.com/settings/apps/new"
    instructions_helper_url: str = ...  # e.g., "https://docs.dataprovider.com/en/apps/creating-dataprovider-apps/"

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
        ExampleDataCategory,
    ]

    # In the functions below, update the elipses (...) with the correct classes and code.
    def __init__(self, **kwargs):
        """Args:
        client_id:
        client_secret:
        access_token:
        refresh_token:
        **kwargs:
        """
        super().__init__(**kwargs)
        # Declare the instance annotations for the API and OAuth clients
        self.api_client: ...  # e.g.,  MyAPI
        self.oauth_client: ...  # e.g., MyAPIOAuthClient
        self.redirect_uri = self.get_redirect_uri()

        self.init_oauth_client()

        if self.access_token is not None and self.refresh_token is not None:
            self.init_api_client(self.access_token, self.refresh_token)

    # OAuthBase methods
    def init_api_client(
        self, access_token: str | None = None, refresh_token: str | None = None, code: str | None = None
    ) -> None:

        self.api_client = ...

    def init_oauth_client(self, *args, **kwargs) -> None:

        self.oauth_client = ...

    def get_authorize_url(
        self, builtin_variables: list[dict], custom_variables: list[dict] | None = None
    ) -> str: ...

    def get_client_id(self) -> str: ...

    def request_token(self, code: str) -> dict[str, Any]: ...

    def revoke_token(self, token: str) -> bool: ...

    # DataProvider methods
    def test_connection_before_extraction(self) -> bool: ...

    def test_connection(self) -> bool: ...

    def repositories_by_stars(self, idx: int) -> str: ...

    @cached_property
    def account_creation_date(self) -> str: ...
