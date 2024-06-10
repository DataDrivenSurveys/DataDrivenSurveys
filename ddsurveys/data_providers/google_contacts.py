#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This module is a template file that can be used as a starting point for creating your own data providers.
You will need to replace the elipses (...) with the correct classes and code.

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
@author: Stefan Teofanovic (stefan.teofanovic@heig-vd.ch)
"""
__all__ = ["GoogleContactsDataProvider"]

import traceback
from functools import cached_property, cache
from typing import Any, Callable, Dict

import requests
from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import Resource, build
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
class People(DataCategory):
    data_origin = [
        {
            "method": "get",
            "endpoint": "https://people.googleapis.com/v1/resourceName=people/me",
            "documentation": "https://developers.google.com/people/api/rest/v1/people/get",
        }
    ]

    custom_variables_enabled = False

    api: "GoogleContactsDataProvider" = None
    self: "GoogleContactsDataProvider"

    def __init__(self, data_provider: "GoogleContactsDataProvider"):
        super().__init__(data_provider)
        self.data_provider: "GoogleContactsDataProvider"

    def fetch_data(self) -> list[dict[str, Any]]:
        contacts = self.data_provider.contacts
        return contacts

    cv_attributes = []

    builtin_variables = [
        BuiltInVariable.create_instances(
            name="total_contacts",
            label="Total number of contacts",
            description="The total number of contacts that a respondent has.",
            test_value_placeholder="100",
            data_type=VariableDataType.NUMBER,
            info="The total number of contacts that a respondent has. It will always be a whole number greater or "
                 "equal to 0.",
            is_indexed_variable=False,
            extractor_func=lambda self: self.num_contacts,
            data_origin=[],
        ),
        BuiltInVariable.create_instances(
            name="num_with_first_name",
            label="Number of contacts with a first name",
            description="The number of contacts that a respondent has with a first name.",
            test_value_placeholder="100",
            data_type=VariableDataType.NUMBER,
            info="The number of contacts that a respondent has with a first name. It will always be a whole number "
                 "greater or equal to 0.",
            is_indexed_variable=False,
            extractor_func=lambda self: self.num_with_first_name,
            data_origin=[],
        ),
        BuiltInVariable.create_instances(
            name="num_with_nickname",
            label="Number of contacts with a nickname",
            description="The number of contacts that a respondent has with a nickname.",
            test_value_placeholder="100",
            data_type=VariableDataType.NUMBER,
            info="The number of contacts that a respondent has with a nickname. It will always be a whole number "
                 "greater or equal to 0.",
            is_indexed_variable=False,
            extractor_func=lambda self: self.num_with_nickname,
            data_origin=[],
        ),
        BuiltInVariable.create_instances(
            name="num_with_organization",
            label="Number of contacts with a company name",
            description="The number of contacts that a respondent has with an organization.",
            test_value_placeholder="100",
            data_type=VariableDataType.NUMBER,
            info="The number of contacts that a respondent has with an organization. It will always be a whole number "
                 "greater or equal to 0.",
            is_indexed_variable=False,
            extractor_func=lambda self: self.num_with_organization,
            data_origin=[],
        ),
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
    app_creation_url: str = (
        "https://console.cloud.google.com/apis/credentials/oauthclient"
    )
    instructions_helper_url: str = (
        "https://developers.google.com/people/quickstart/python"
    )

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
        People,
    ]

    _person_fields_list = [
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

    _person_fields = ",".join(_person_fields_list)

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
        client_secret: str = None,
    ) -> None:
        if token is not None:
            self.access_token = token
        if refresh_token is not None:
            self.refresh_token = refresh_token
        if client_id is not None:
            self.client_id = client_id
        if client_secret is not None:
            self.client_secret = client_secret
        info = {
            "token": self.access_token,
            "refresh_token": self.refresh_token,
            "token_uri": "https://oauth2.googleapis.com/token",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        creds = Credentials.from_authorized_user_info(info=info, scopes=self.scopes)

        self.api_client = build("people", "v1", credentials=creds)

    def init_oauth_client(
        self, client_id: str = None, client_secret: str = None
    ) -> None:
        client_config = {
            "web": {
                "client_id": client_id,
                "project_id": "dab-idp-dds",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_secret": client_secret,
                "redirect_uris": [self.redirect_uri],
            }
        }

        self.oauth_client = Flow.from_client_config(
            client_config=client_config, scopes=self.scopes
        )

    def get_authorize_url(
        self, builtin_variables: list[dict], custom_variables: list[dict] = None
    ) -> str:
        ...

    def get_client_id(self) -> str:
        ...

    def request_token(self, code: str) -> Dict[str, Any]:
        ...

    def revoke_token(self, token: str) -> bool:
        ...

    # DataProvider methods
    def test_connection_before_extraction(self) -> bool:
        ...

    def test_connection(self) -> bool:
        """
        Tests the connection to the Google People API using the provided OAuth credentials.

        This method verifies the client credentials by attempting to list the connections
        of the authenticated user. It checks the validity of the client ID, client secret,
        and refresh token in the following order:
        1. Client ID
        2. Client Secret
        3. Refresh Token

        Returns:
            bool: True if the connection is successful and the credentials are valid, False otherwise.

        Raises:
            RefreshError: If there is an issue with the OAuth credentials.
        """
        credentials = {
            "client_id": self.client_id,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": self.client_secret,
            "refresh_token": "...",
        }

        creds = Credentials.from_authorized_user_info(credentials)
        service = build("people", "v1", credentials=creds)

        try:
            service.people().connections().list(resourceName="people/me").execute()
        except RefreshError as e:
            error = e.args[1].get("error", "")
            description = e.args[1].get("error_description", "")
            if error == "invalid_client" and (
                description.casefold() == "The OAuth client was not found.".casefold()
                or description.casefold == "Unauthorized".casefold()
            ):
                return False
            elif (
                error == "invalid_grant"
                and description.casefold() == "Bad Request".casefold()
            ):
                return True
            else:
                raise e
        except Exception as e:
            logger.error(
                f"An unexpected error occurred when verifying the client credentials: {e}"
            )
            logger.debug(traceback.format_exc())
            return False

    @property
    def person_fields(self) -> str:
        return self.__class__._person_fields

    @cached_property
    def contacts(self) -> list[dict]:
        # Fetch all contacts from the API and return them as a list of dictionaries.
        connections: list[dict] = list()
        has_next_page = True
        next_page_token = None
        while has_next_page:
            results = (
                self.api_client.people()
                .connections()
                .list(
                    resourceName="people/me",
                    pageSize=1000,
                    personFields=self.person_fields,
                    pageToken=next_page_token,
                )
                .execute()
            )

            connections.extend(results.get("connections"))

            if "nextPageToken" in results:
                next_page_token = results["nextPageToken"]
            else:
                has_next_page = False

        return connections

    # Functions to calculate variables
    @cache
    def with_category(self, category: str) -> list[dict]:
        return [
            c
            for c in self.contacts
            if (cat := c.get(category, [])) and len(cat) > 0
        ]

    @cache
    def with_category_subcategory(self, category: str, subcategory: str) -> list[dict]:
        return [
            c
            for c in self.contacts
            if
            (cat := c.get(category, [])) and len(cat) > 0 and any([subcat.get(subcategory, "") != "" for subcat in cat])
        ]

    @cached_property
    def with_first_name(self) -> list[dict]:
        return self.with_category_subcategory("names", "givenName")

    @cached_property
    def with_last_name(self) -> list[dict]:
        return [
            c
            for c in self.contacts
            if (names := c.get("names", [])) and len(names) > 0 and names[0].get("familyName", "") != ""
        ]

    @cached_property
    def with_nickname(self) -> list[dict]:
        return [
            c
            for c in self.contacts
            if (names := c.get("nicknames", [])) and len(names) > 0 and names[0].get("value", "") != ""
        ]

    @cached_property
    def with_company(self) -> int:
        return self.with_category_subcategory("organizations", "name")

    @cached_property
    def with_job_title(self) -> list[dict]:
        return self.with_category_subcategory("organizations", "title")

    @cached_property
    def with_company_or_job_title(self) -> list[dict]:
        return [
                c
                for c in self.contacts
                if (organizations := c.get("organizations", []))
                and len(organizations) > 0
                and any([org.get("name", "") != "" or org.get("title", "") != "" for org in organizations])
            ]

    # Number of contacts with specific values
    @cached_property
    def num_with_company(self) -> int:
        return len(self.with_company)

    @cached_property
    def num_with_job_title(self) -> int:
        return len(self.with_category_subcategory("organizations", "title"))

    @cached_property
    def num_with_company_or_title(self) -> int:
        return len(self.with_company_or_job_title)

    @cached_property
    def num_contacts(self) -> int:
        return len(self.contacts)

    @cache
    def num_with_category(self, category: str) -> int:
        return len(self.with_category(category))

    @cached_property
    def num_with_first_name(self) -> int:
        return len(self.with_first_name)

    @cached_property
    def num_with_last_name(self) -> int:
        return len(self.with_last_name)

    @cached_property
    def num_with_nickname(self) -> int:
        return len(self.with_nickname)

    @cached_property
    def num_with_organization(self) -> int:
        return self.num_with_category("organizations")

    @cached_property
    def num_with_relations(self) -> int:
        return len(self.with_category("relations"))

    @cached_property
    def num_with_email_addresses(self) -> int:
        return len(self.with_category("emailAddresses"))

    @cached_property
    def num_with_phone_numbers(self) -> int:
        return len(self.with_category("phoneNumbers"))

    @cached_property
    def num_with_phone_numbers_stats(self) -> list[list[int]]:
        pass
