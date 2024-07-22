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
import operator
from collections import namedtuple
from functools import cached_property, cache
from typing import Any, Callable

import requests
from google.auth.exceptions import RefreshError
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import Resource, build

from ..utils.text_structure_analyzer import SpacyTextStructureAnalyzer
# from textblob import TextBlob

from ...get_logger import get_logger
from ...variable_types import TVariableFunction
from ..bases import FormField, OAuthDataProvider

from .api_response_dicts import *
from .people import People


logger = get_logger(__name__)


# This is an example of a data category.
# In practice, each endpoint can be turned into a data category.


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
    _scopes = [
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/contacts.readonly"
    ]

    # See other classes for examples of how to fill these attributes. You may not need to fill them
    _categories_scopes = {
    }

    # Form fields that will be displayed in the frontend. Only update them if the data provider uses different
    # terminology for this information.
    form_fields = [
        FormField(name="client_id", type="text", required=True, data={}),
        FormField(name="client_secret", type="text", required=True, data={}),
        FormField(name="project_id", type="text", required=True, data={}),
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

        self.project_id: str = kwargs.get("project_id")
        self.state = None
        self.credentials: Credentials = None

        self.init_oauth_client()

        if self.client_id is not None and self.client_secret is not None:
            self.init_oauth_client(self.client_id, self.client_secret)

        if self.client_id is not None and self.client_secret is not None:
            self.init_api_client(self.access_token, self.refresh_token, self.client_id, self.client_secret)

        self.text_structure_analyzer = SpacyTextStructureAnalyzer(preload_models=False)

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
        self.credentials = Credentials.from_authorized_user_info(info=info, scopes=self.scopes)

        self.api_client = build("people", "v1", credentials=self.credentials)

    def init_oauth_client(
        self, client_id: str = None, client_secret: str = None, project_id: str = None
    ) -> None:
        client_config = {
            "web": {
                "client_id": client_id or self.client_id,
                "project_id": project_id or self.project_id,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_secret": client_secret or self.client_secret,
                "redirect_uris": [self.redirect_uri],
            }
        }

        self.oauth_client = Flow.from_client_config(
            client_config=client_config, scopes=self.scopes
        )

        # Set redirect_uri
        self.oauth_client.redirect_uri = self.redirect_uri

    def get_authorize_url(
        self, builtin_variables: list[dict], custom_variables: list[dict] = None
    ) -> str:
        url, state = self.oauth_client.authorization_url(
            # Recommended, enable offline access so that you can refresh an access token without
            # re-prompting the user for permission. Recommended for web server apps.
            access_type="offline",

            # Optional, enable incremental authorization. Recommended as a best practice.
            include_granted_scopes='true',

            # Optional, set prompt to 'consent' will prompt the user for consent
            prompt='consent',
        )
        self.state = state
        return url

    def get_client_id(self) -> str:
        return self.client_id

    def get_required_scopes(
        self, builtin_variables: list[dict] = None, custom_variables: list[dict] = None
    ) -> list[str]:
        self.required_scopes = self.__class__._scopes
        return self.required_scopes

    def request_token(self, code: str) -> dict[str, Any]:
        logger.info(f"Requesting token")
        exchange_failed = False
        try:
            self.oauth_client.fetch_token(authorization_response=f"{self.redirect_uri}?code={code}")
            credentials = self.oauth_client.credentials
        except Warning as e:
            logger.warning(f"Warning when exchanging tokens: {e}")
            # Create mock credentials object to fail the granted scopes check
            credentials = namedtuple("Credentials", ["granted_scopes"])(granted_scopes=[""])
            exchange_failed = True

        if exchange_failed or not set(self.required_scopes).issubset(set(credentials.granted_scopes)):
            logger.error(f"The required scopes were not granted.")
            self.revoke_token(credentials.token)
            return {
                "success": False,
                "message_id": "api.data_provider.exchange_code_error.incomplete_scopes",
                "required_scopes": self.scopes,
                "accepted_scopes": credentials.granted_scopes,
            }

        self.init_api_client(credentials.token, credentials.refresh_token, credentials.client_id,
                             credentials.client_secret)

        people_service = build("people", "v1", credentials=credentials)
        profile = people_service.people().get(resourceName='people/me', personFields='names').execute()

        logger.info(f"Profile: {profile}")
        self.credentials = credentials

        return {
            "success": True,
            "access_token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "user_id": profile["resourceName"].split("/")[-1],
            "user_name": profile["names"][0]["displayName"],
        }

    def revoke_token(self, token: str) -> bool:

        if self.credentials is None:
            self.credentials = self.oauth_client.credentials

        r = requests.post(
            "https://oauth2.googleapis.com/revoke",
            params={"token": self.credentials.token},
            headers={"content-type": "application/x-www-form-urlencoded"},
        )

        if r.status_code == 200:
            logger.info(f"Successfully revoked google token")
            return True
        else:
            logger.error(f"Failed to revoke google token: {r.status_code}")
            logger.error(f"Response: {r.content}")
            return False

    # DataProvider methods
    def test_connection_before_extraction(self) -> bool:
        self.init_api_client()
        results = (
            self.api_client.people()
            .connections()
            .list(
                resourceName="people/me",
                pageSize=10,
                personFields=self._person_fields,
            )
            .execute()
        )
        if results.get("connections") is None:
            return False
        return True

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
    def contacts(self) -> list[ContactDict]:
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
    def with_category(self, category: str) -> list[ContactDict]:
        return self.with_category_count(
            category=category,
            operator_=operator.gt,
            count=0,
        )

    @cache
    def with_category_subcategory(self, category: str, subcategory: str) -> list[ContactDict]:
        return [
            c
            for c in self.contacts
            if ((cat := c.get(category, [])) or True)
               and len(cat) > 0
               and any([subcat.get(subcategory, "") != "" for subcat in cat])
        ]

    @cache
    def with_category_count(self, category: str, operator_: callable = operator.gt, count: int = 0) -> list[ContactDict]:
        return [
            c
            for c in self.contacts
            if ((cat := c.get(category, [])) or True) and operator_(len(cat), count)
        ]

    @cached_property
    def with_first_name(self) -> list[ContactDict]:
        return self.with_category_subcategory("names", "givenName")

    @cached_property
    def with_last_name(self) -> list[ContactDict]:
        return [
            c
            for c in self.contacts
            if ((names := c.get("names", [])) or True) and len(names) > 0 and names[0].get("familyName", "") != ""
        ]

    @cached_property
    def with_nickname(self) -> list[ContactDict]:
        return [
            c
            for c in self.contacts
            if ((names := c.get("nicknames", [])) or True)
               and len(names) > 0
               and names[0].get("value", "") != ""
        ]

    @cached_property
    def with_company(self) -> list[ContactDict]:
        return self.with_category_subcategory("organizations", "name")

    @cached_property
    def with_job_title(self) -> list[ContactDict]:
        return self.with_category_subcategory("organizations", "title")

    @cached_property
    def with_company_or_job_title(self) -> list[ContactDict]:
        return [
                c
                for c in self.contacts
                if ((organizations := c.get("organizations", [])) or True)
                and len(organizations) > 0
                and any([org.get("name", "") != "" or org.get("title", "") != "" for org in organizations])
            ]

    @cached_property
    def with_birthday_year(self) -> list[ContactDict]:
        return [
            c
            for c in self.contacts
            if ((birthdays := c.get("birthdays", [])) or True)
            and len(birthdays) > 0
            and birthdays[0].get("date", {}).get("year") is not None
        ]

    @cached_property
    def count_num_contacts_by_biography_length(self) -> dict[str, int]:
        counts = {"few words": 0, "few sentences": 0, "few paragraphs": 0}
        for c in self.with_category("biographies"):
            type_ = self.classify_text(
                c["biographies"][0]["value"]
            )
            counts[type_] += 1

        return counts

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
    def num_with_relations(self) -> int:
        return len(self.with_category("relations"))

    @cached_property
    def num_with_photos(self) -> int:
        return len(self.with_category("photos"))

    @cached_property
    def num_with_birthday(self) -> int:
        return len(self.with_category("birthdays"))

    @cached_property
    def num_with_addresses(self) -> int:
        return len(self.with_category("addresses"))

    @cached_property
    def num_with_biographies(self) -> int:
        return len(self.with_category("biographies"))

    @cached_property
    def num_with_0_phone_numbers(self) -> int:
        return len(self.with_category_count("phoneNumbers", operator.eq, 0))

    @cached_property
    def num_with_1_phone_numbers(self) -> int:
        return len(self.with_category_count("phoneNumbers", operator.eq, 1))

    @cached_property
    def num_with_2_phone_numbers(self) -> int:
        return len(self.with_category_count("phoneNumbers", operator.eq, 2))

    @cached_property
    def num_with_3_or_more_phone_numbers(self) -> int:
        return len(self.with_category_count("phoneNumbers", operator.ge, 3))

    @cached_property
    def num_with_birthday_year(self) -> int:
        return len(self.with_birthday_year)

    @cached_property
    def num_with_biographies_few_words(self) -> int:
        return self.count_num_contacts_by_biography_length["few words"]

    @cached_property
    def num_with_biographies_few_sentences(self) -> int:
        return self.count_num_contacts_by_biography_length["few sentences"]

    @cached_property
    def num_with_biographies_few_paragraphs(self) -> int:
        return self.count_num_contacts_by_biography_length["few paragraphs"]

    # Supporting functions
    def classify_text(self, text: str, few_words_threshold: int = 5, few_sentences_threshold: int = 3) -> str:
        words, sentences, paragraphs = self.text_structure_analyzer.analyze_text(text)
        if sentences == 1 and words <= few_words_threshold:
            return 'few words'
        elif sentences <= few_sentences_threshold:
            return 'few sentences'
        else:
            return 'few paragraphs'
