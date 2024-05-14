#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2023-10-31 13:53

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
@author: Stefan Teofanovic (stefan.teofanovic@heig-vd.ch)
"""

__all__ = ["TemplateOAuthSurveyPlatform"]

import json
import os
import uuid
from typing import Any, Optional

import requests
from surveymonkey.client import Client as SMClient

from ...get_logger import get_logger
from ..bases import FormButton, FormField, OAuthSurveyPlatform

# API related classes
# from .api import ...

logger = get_logger(__name__)


class TemplateOAuthSurveyPlatform(OAuthSurveyPlatform):
    # Form fields declarations go here
    form_fields: list[FormField | FormButton] = [
        ...
    ]

    def __init__(
        self,
        survey_id: str = "",
        client_id: str = "",
        client_secret: str = "",
        access_token: str = "",
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)

        self.survey_id: str = survey_id
        self.client_id: str = client_id
        self.client_secret: str = client_secret
        self.access_token: str = access_token

        self.redirect_uri = self.get_redirect_uri()

        self.api_client: ...  # e.g., SurveyPlatformClient
        self.init_api_client(self.client_id, self.client_secret)

    # OAuthSurveyPlatform methods
    def init_api_client(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str = None,
        access_token: str = None,
        *args,
        **kwargs,
    ) -> None:
        self.client_id: str = client_id
        self.client_secret: str = client_secret

        self.api_client = ...  # e.g.,  self.api_client = SurveyPlatformClient(...)

    def init_oauth_client(self, *args, **kwargs) -> None:
        ...
        self.api_client = ...

    @classmethod
    def get_app_credentials(cls) -> dict[str, str]:
        ...

    @classmethod
    def get_authorize_url(cls) -> str:
        ...

    def get_client_id(self) -> str:
        ...

    def request_token(self, code: str) -> dict[str, Any]:
        ...

    def revoke_token(self, token: str) -> bool:
        ...

    # SurveyPlatform methods
    def fetch_survey_platform_info(self) -> tuple[int, Optional[str], dict[str, Any]]:
        ...

    def handle_project_creation(
        self, project_name: str, use_existing_survey: bool = False
    ) -> tuple[int, str, str, str, dict[str, Any]]:
        ...
    def handle_variable_sync(self, enabled_variables: dict) -> tuple[int, str, str]:
        ...

    def handle_prepare_survey(
        self, project_short_id: str, survey_platform_fields: dict, embedded_data: dict
    ) -> tuple[bool, Optional[str]]:
        ...

    def handle_export_survey_responses(
        self, project_short_id: str
    ) -> tuple[bool, str, None]:
        ...

    @staticmethod
    def get_preview_link(
        survey_platform_fields, enabled_variables
    ) -> tuple[int, str, str, str]:
        ...
