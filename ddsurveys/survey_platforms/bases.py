#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2023-05-23 14:08

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
@author: Stefan Teofanovic (stefan.teofanovic@heig-vd.ch)
"""

from __future__ import annotations
import os
from abc import abstractmethod
from typing import Tuple, Optional, List, Dict, Any, Type

from ..get_logger import get_logger
from ..shared_bases import UIRegistry, FormField as BaseFormField, FormButton as BaseFormButton

logger = get_logger(__name__)

__all__ = [
    "SurveyPlatform",
    "FormField",
]

TSurveyPlatformClass = Type["SurveyPlatform"]


class SurveyPlatform(UIRegistry):
    """
    Interface class defining methods and attributes that survey platforms should support.
    """

    # General class attributes
    # base_name will decide the key in the class registry where each child class of SurveyPlatform will be stored.
    base_name: str = "SurveyPlatform"
    registry_exclude: list[str] = ["SurveyPlatform", "OAuthSurveyPlatform"]

    # mainly used to generate the full qualified name for message ids
    _package = __package__


    # The following attributes (normally) do not need to be redeclared in child classes
    name: str = ""
    name_lower: str = ""
    label: str = ""
    value: str = ""  # TODO: remove cls.value once Enum nomenclature is removed
    instructions: str = ""

    # Class attributes that need be redeclared or redefined in child classes
    # The following attributes need to be redeclared in child classes.
    # You can just copy and paste them into the child class body.
    fields: list[dict[str, Any]] = {}

    # Unique class attributes go here

    # Form fields declarations go here
    # Child classes should redeclare the form_fields attribute and populate the list with instances of FormField.
    # These instances are used to create the form when adding a data provider in the UI.
    form_fields: list[FormField] = []

    def __init__(self, *args, **kwargs):
        super().__init__()

    @classmethod
    def check_input_fields(cls, fields: List[dict],
                           override_required_fields: List[str] = None,
                           class_: type = None) -> Tuple[bool, Optional[str]]:
        """
        Check if all the required fields are present and not empty.
        """
        if override_required_fields is None:
            override_required_fields = []
        if class_ is None:
            class_ = cls
        return FormField.check_input_fields(fields, cls.form_fields, override_required_fields, class_)

    @abstractmethod
    def fetch_survey_platform_info(self) -> Tuple[int, Optional[str], Dict[str, Any]]:
        """
        Fetch information about the survey platform. And translate it into the DDS format.
        Returns:
        {
            "connected": False,        - Whether the survey platform is connected or not.
            "active": False,           - Whether the survey is active or not.
            "exists": False,           - Whether the survey exists or not.
            "survey_name": None,       - The name of the survey.
            "survey_status": "unknown" - The status of the survey. Allowed values are: "active", "inactive", "unknown"
        }

        Each survey platform should implement this method and decide what any of these keys mean in its own platform context.
        """
        raise NotImplementedError("fetch_survey_platform_info method not implemented.")

    @abstractmethod
    def handle_project_creation(self, project_name: str, use_existing_survey: bool = False) -> Tuple[int, str, str, str, Dict[str, Any]]:
        """
        Create a project in the survey platform and return the Tuple with:
        - Status code (200 or 40x)
        - Message ID (str)
        - Message English Text (str)
        - Project Name (str) - The project name can be conditional (user input or survey name) and should be returned here.
        - Fields for the survey platform (dict) - The fields required for a particular survey platform. Stored in JSON field project.survey_platform_fields.
        """
        raise NotImplementedError("handle_project_creation method not implemented.")

    @abstractmethod
    def handle_variable_sync(self, enabled_variables: dict) -> Tuple[int, str, str]:
        """
        Sync the variables in the survey platform and return the Tuple with:
        - Status code (200 or 40x)
        - Message ID (str)
        - Message English Text (str)
        The status 200 means that the variables were successfully synced.
        The status 40x means that the variables were not synced.
        """
        raise NotImplementedError("handle_variable_sync method not implemented.")

    @abstractmethod
    def handle_prepare_survey(self, project_short_id: str, survey_platform_fields: str, embedded_data: dict) -> Tuple[bool, Optional[str]]:
        """
        Prepare the survey in the survey platform and return the Tuple with:
        - Boolean representing whether the survey was successfully prepared or not.
        - Unique Distribution URL (str) - The URL that will be used to distribute the survey.
        """
        raise NotImplementedError("handle_prepare_survey method not implemented.")
    
    @abstractmethod
    def handle_export_survey_responses(self, project_short_id: str) -> Tuple[bool, Optional[str]]:
        """
        Download the responses from the survey platform and return the Tuple with:
        - Status code (200 or 40x)
        - Message ID (str)
        - Message English Text (str)
        - File Content (str) - The content of the file that was downloaded.
        """
        raise NotImplementedError("handle_export_survey_responses method not implemented.")
    
    @staticmethod
    def get_preview_link(survey_platform_fields, enabled_variables) -> Tuple[int, str, str, str]:
        """
        Get the preview link for the survey.
        - Status code (200 or 40x)
        - Message ID (str)
        - Message English Text (str)
        - Preview Link (str) - The preview link for the survey.

        """
        raise NotImplementedError("get_preview_link method not implemented.")


class OAuthSurveyPlatform(SurveyPlatform):
    # General class attributes
    # These attributes need to be overridden
    token_url: str = ""
    revoke_url: str = ""
    base_authorize_url: str = ""

    _scopes: list[str] = []

    def __init__(self, client_id: str = None, client_secret: str = None,
                 access_token: str = None, refresh_token: str = None, **kwargs):
        super().__init__()
        self.client_id: str = client_id
        self.client_secret: str = client_secret
        self.access_token: str = access_token
        self.refresh_token: str = refresh_token
        self._authorize_url: str = ""
        self._required_scopes: list[str] = []

        self.api_client = None
        self.oauth_client = None

    @classmethod
    def get_redirect_uri(cls) -> str:
        # TODO: avoid using environment variables.
        frontend_url = os.getenv("FRONTEND_URL")
        return f"{frontend_url}/survey_platform/redirect/{cls.name_lower}"
    
    @classmethod
    def get_authorize_url(cls) -> str:
        pass
    
    @classmethod
    def get_app_credentials(cls) -> dict[str, str]:
        pass

    # Instance properties
    @property
    def required_scopes(self) -> list[str]:
        return self._required_scopes

    @required_scopes.setter
    def required_scopes(self, scopes: list[str]):
        self._required_scopes = scopes

    # Methods that child classes must implement
    @abstractmethod
    def init_api_client(self, *args, **kwargs) -> None:
        pass

    @abstractmethod
    def init_oauth_client(self, *args, **kwargs) -> None:
        pass

    

    @abstractmethod
    def get_client_id(self) -> str:
        pass

    @abstractmethod
    def request_token(self, code: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def revoke_token(self, token: str) -> bool:
        pass


class FormField(BaseFormField):
    """This class is used to declare fields that a data provider needs to be filled when it is added in the UI.


    Attributes:
        name (str):
            The name of the field.
        type (str):
            The type of input that is expected.
            Allowed values are: "text"
        required (bool): Whether the field is required to be filled or not.
        label (str):
            The label of the field.
            It is used to look up the string that should be displayed in the UI in the frontend/src/i18n/resources.json
            file.
            If no label is passed, the value of name will be used to generate the label like so:
            f"api.data_provider.{DP.__name__.lower()}.{name}.label"
        helper_text (str):
            The helper text of the field.
            It is used to look up the string that should be displayed in the UI in the frontend/src/i18n/resources.json
            file.
            If no helper text is passed, the value of name will be used to generate the helper text like so:
            f"api.data_provider.{DP.__name__.lower()}.{name}.helper_text"
    """

    shared_prefix_text: str = "api"
    _package: str = ""
    _registry_class = SurveyPlatform
    _registry_class_name: str = ""  # No need to set this manually.


class FormButton(BaseFormButton):
    """This class is used to declare buttons that a data provider needs to be filled when it is added in the UI.

    Attributes:
        name (str):
            The name of the button.
        label (str):
            The label of the button.
            It is used to look up the string that should be displayed in the UI in the frontend/src/i18n/resources.json
            file.
            If no label is passed, the value of name will be used to generate the label like so:
            f"api.data_provider.{DP.__name__.lower()}.{name}.label"
        helper_text (str):
            The helper text of the button.
            It is used to look up the string that should be displayed in the UI in the frontend/src/i18n/resources.json
            file.
            If no helper text is passed, the value of name will be used to generate the helper text like so:
            f"api.data_provider.{DP.__name__.lower()}.{name}.helper_text"
        href (str):
            The href of the button.
        data (dict):
            Additional data for the frontend.
    """

    shared_prefix_text: str = "api"
    _package: str = ""
    _registry_class = SurveyPlatform
    _registry_class_name: str = ""  # No need to set this manually.