#!/usr/bin/env python3
"""This module is a template file that can be used as a starting point for creating your own data providers.
You will need to replace the elipses (...) with the correct classes and code.

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
@author: Stefan Teofanovic (stefan.teofanovic@heig-vd.ch)
"""
__all__ = ["TemplateDataProvider"]

from collections.abc import Callable
from functools import cached_property
from typing import Any, ClassVar

from data_providers.data_categories import DataCategory

from ddsurveys.data_providers.bases import FormField, OAuthDataProvider
from ddsurveys.data_providers.variables import BuiltInVariable, CVAttribute
from ddsurveys.get_logger import get_logger
from ddsurveys.variable_types import TVariableFunction, VariableDataType

# Import the required libraries to make this work

logger = get_logger(__name__)


# This is an example of a data category.
# In practice, each endpoint can be turned into a data category.
# 'self' in extractor functions will be an instance of the data provider class.
class ExampleDataCategory(DataCategory):

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
        return self.api.get_user()

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


class TemplateDataProvider(OAuthDataProvider):
    # Class attributes that need be re-declared or redefined in child classes
    # The following attributes need to be re-declared in child classes.
    # You can copy and paste them into the child class body.
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
    # Just enter the names of the classes.
    data_categories: ClassVar[tuple[type[DataCategory], ...]] = (
        ExampleDataCategory,
     )

    # In the functions below, update the elipses (...) with the correct classes and code.

    def __init__(self, **kwargs):
        """Initialization function.

        Args:
            client_id:
            client_secret:
            access_token:
            refresh_token:
            **kwargs:
        """
        super().__init__(**kwargs)
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

    def request_token(self, data: dict[str, Any]) -> dict[str, Any]: ...

    def revoke_token(self, token: str) -> bool: ...

    # DataProvider methods
    def test_connection_before_extraction(self) -> bool: ...

    def test_connection(self) -> bool: ...

    def repositories_by_stars(self, idx: int) -> str: ...

    @cached_property
    def account_creation_date(self) -> str: ...
