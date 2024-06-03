#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This module is a template file that can be used as a starting point for creating your own data providers.
You will need to replace the elipses (...) with the correct classes and code.

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
@author: Stefan Teofanovic (stefan.teofanovic@heig-vd.ch)
"""
__all__ = ["GoogleContactsDataProvider"]

from functools import cached_property
from typing import Any, Callable, Dict

import requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build, Resource
from googleapiclient.errors import HttpError


from ..get_logger import get_logger
from ..variable_types import TVariableFunction, VariableDataType
from .bases import FormField, OAuthDataProvider
from .data_categories import DataCategory
from .variables import BuiltInVariable, CVAttribute

# Import the required libraries to make this work

logger = get_logger(__name__)


# This is an example of a data category.
# In practice, each endpoint can be turned into a data category.
class PeopleDataCategory(DataCategory):

    data_origin = [
        {
            "method": "get",
            "endpoint": "https://people.googleapis.com/v1/resourceName=people/me",
            "documentation": "https://developers.google.com/people/api/rest/v1/people/get",
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


class GoogleContactsDataProvider(OAuthDataProvider):
    # Class attributes that need be redeclared or redefined in child classes
    # The following attributes need to be redeclared in child classes.
    # You can copy and paste them into the child class body.
    # When copying a template file, leave them unchanged.
    all_initial_funcs: dict[str, Callable] = {}  # Leave unchanged.
    factory_funcs: dict[str, Callable] = {}  # Leave unchanged.
    variable_funcs: dict[str, TVariableFunction] = {}  # Leave unchanged.
    fields: list[dict[str, Any]] = {}  # Leave unchanged.

    # Update the following attributes:
    app_creation_url: str = "https://console.cloud.google.com/apis/credentials/oauthclient"
    instructions_helper_url: str = "https://developers.google.com/people/quickstart/python"

    # Unique class attributes go here
    _scopes = ["https://www.googleapis.com/auth/contacts.readonly"]

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
    data_categories = [
        PeopleDataCategory,
    ]

    person_fields_list = [
        "addresses",
        "ageRanges",
        "biographies",
        "birthdays",
        "calendarUrls",
        "clientData",
        "coverPhotos",
        "emailAddresses",
        "events",
        "externalIds",
        "genders",
        "imClients",
        "interests",
        "locales",
        "locations",
        "memberships",
        "metadata",
        "miscKeywords",
        "names",
        "nicknames",
        "occupations",
        "organizations",
        "phoneNumbers",
        "photos",
        "relations",
        "sipAddresses",
        "skills",
        "urls",
        "userDefined",
    ]

    person_fields = ",".join(person_fields_list)

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
        self.api_client: Resource
        self.oauth_client: Flow
        self.redirect_uri = self.get_redirect_uri()

        self.init_oauth_client()

        if self.client_id is not None and self.client_secret is not None:
            self.init_api_client(self.access_token, self.refresh_token)

    # OAuthBase methods
    def init_api_client(
        self,
        token: str = None,
        refresh_token: str = None,
        client_id: str = None,
        client_secret: str = None
    ) -> None:
        info = {
            "token": token,
            "refresh_token": refresh_token,
            "token_uri": "https://oauth2.googleapis.com/token",
            "client_id": client_id,
            "client_secret": client_secret,
        }
        creds = Credentials.from_authorized_user_info(info=info, scopes=self.scopes)

        self.api_client = build("people", "v1", credentials=creds)

    def init_oauth_client(self, client_id: str = None, client_secret: str = None) -> None:
        client_config = {
            "web": {
                "client_id": client_id,
                "project_id": "dab-idp-dds",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_secret": client_secret,
                "redirect_uris": [
                  self.redirect_uri
                ]
              }
        }

        self.oauth_client = Flow.from_client_config(client_config=client_config, scopes=self.scopes)

    def get_authorize_url(
        self, builtin_variables: list[dict], custom_variables: list[dict] = None
    ) -> str: ...

    def get_client_id(self) -> str: ...

    def request_token(self, code: str) -> Dict[str, Any]: ...

    def revoke_token(self, token: str) -> bool: ...

    # DataProvider methods
    def test_connection_before_extraction(self) -> bool: ...

    def test_connection(self) -> bool: ...

    def repositories_by_stars(self, idx: int) -> str: ...

    @cached_property
    def account_creation_date(self) -> str: ...

    @cached_property
    def get_contacts(self) -> list[dict]:
        connections = ...
