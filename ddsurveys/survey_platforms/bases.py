"""This module provides base classes for creating survey platform integration classes.

Created on 2023-05-23 14:08.

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
@author: Stefan Teofanovic (stefan.teofanovic@heig-vd.ch)
"""

from __future__ import annotations

import os
from abc import abstractmethod
from typing import Any, ClassVar, TypeVar

from ddsurveys.get_logger import get_logger
from ddsurveys.shared_bases import FormButton as BaseFormButton
from ddsurveys.shared_bases import FormField as BaseFormField
from ddsurveys.shared_bases import UIRegistry

__all__ = [
    "SurveyPlatform",
    "OAuthSurveyPlatform",
    "FormField",
    "FormButton",
    #
    "TSurveyPlatformClass",
    "TSurveyPlatform",
    "TOAuthSurveyPlatformClass",
    "TOAuthSurveyPlatform",
    "TSurveyPlatformFormFieldClass",
    "TSurveyPlatformFormField",
    "TSurveyPlatformFormButtonClass",
    "TSurveyPlatformFormButton",
]

logger = get_logger(__name__)


TSurveyPlatformClass = type["SurveyPlatform"]
TSurveyPlatform = TypeVar("TSurveyPlatform", bound="SurveyPlatform")

TOAuthSurveyPlatformClass = type["OAuthSurveyPlatform"]
TOAuthSurveyPlatform = TypeVar("TOAuthSurveyPlatform", bound="OAuthSurveyPlatform")

TSurveyPlatformFormFieldClass = type["FormField"]
TSurveyPlatformFormField = TypeVar("TSurveyPlatformFormField", bound="FormField")

TSurveyPlatformFormButtonClass = type["FormButton"]
TSurveyPlatformFormButton = TypeVar("TSurveyPlatformFormButton", bound="FormButton")


class SurveyPlatform(UIRegistry[TSurveyPlatformClass]):
    """Interface class for survey platforms."""

    # General class attributes
    # base_name will decide the key in the class registry where each child class of SurveyPlatform will be stored.
    base_name: str = "SurveyPlatform"
    registry_exclude: ClassVar[list[str]] = ["SurveyPlatform", "OAuthSurveyPlatform"]

    # mainly used to generate the full qualified name for message ids
    _package = __package__

    # The following attributes (normally) do not need to be re-declared in child classes
    name: str = ""
    name_lower: str = ""
    label: str = ""
    value: str = ""  # TODO: remove cls.value once Enum nomenclature is removed
    instructions: str = ""

    # Class attributes that need be re-declared or redefined in child classes
    # The following attributes need to be re-declared in child classes.
    # You can just copy and paste them into the child class body.
    fields: ClassVar[list[dict[str, Any]]] = []

    # Unique class attributes go here

    # TODO: update variable name generation to take this into account
    max_variable_name_length: int = -1
    """Maximum length for variable names that can be uploaded to the survey platform.

    Default value is -1, meaning no maximum length is set.
    """

    # TODO: update variable name generation to take this into account
    variable_replacement_rules: list[tuple[str, str, int]] = ()
    """Rules for replacing values in variable names.

    The rules coming from SurveyPlatforms should be used for replacing illegal
    characters.
    """

    # Form fields declarations go here
    # Child classes should redeclare the form_fields attribute and populate the list
    # with instances of FormField.
    # These instances are used to create the form when adding a data provider in the UI.
    form_fields: ClassVar[list[FormField | FormButton]] = []

    def __init__(self, *args, **kwargs) -> None:
        super().__init__()

    @classmethod
    def check_input_fields(
        cls,
        fields: list[dict],
        override_required_fields: list[str] | None = None,
        class_: type | None = None,
    ) -> tuple[bool, str | None]:
        """Check if all the required fields are present and not empty.

        Args:
            fields (list[dict]): A list of dictionaries representing the fields to be
                checked.
            override_required_fields (list[str] | None, optional): A list of field names
                that should be considered required, overriding the default required fields.
                Defaults to None.
            class_ (type | None, optional): The class type to be used for checking the
                fields.
                Defaults to None.

        Returns:
            tuple[bool, str | None]: A tuple where the first element is a boolean
                indicating whether all required fields are present and not empty,
                and the second element is a string containing an error message
                if any required field is missing or empty, otherwise None.
        """
        if override_required_fields is None:
            override_required_fields = []
        if class_ is None:
            class_ = cls
        return FormField.check_input_fields(
            fields=fields,
            form_fields=cls.form_fields,
            override_required_fields=override_required_fields,
            class_=class_,
        )

    @abstractmethod
    def fetch_survey_platform_info(self) -> tuple[int, str | None, dict[str, Any]]:
        """Fetch information about the survey platform and translate it into the DDS format.

        Each survey platform should implement this method and decide what any of these keys mean in its own platform
        context.

        Returns:
            dict with the following keys: {
                "connected": False,        # Whether the survey platform is connected or not.
                "active": False,           # Whether the survey is active or not.
                "exists": False,           # Whether the survey exists or not.
                "survey_name": None,       # The name of the survey.
                "survey_status": "unknown" # The status of the survey. Allowed values are: "active", "inactive",
                "unknown"
            }
        """
        ...

    @abstractmethod
    def handle_project_creation(
        self, project_name: str, *, use_existing_survey: bool = False
    ) -> tuple[int, str, str, str | None, dict[str, Any]]:
        """Create a project in the survey platform.

        Args:
            project_name: The name of the project.
            use_existing_survey: Whether to use an existing survey or create a new one.

        Returns:
            A tuple with the following structure:
            - Status code (HTTPStatus.OK or 40x)
            - Message ID (str)
            - Message English Text (str)
            - Project Name (str) - The project name can be conditional (user input or survey name) and should be
            returned here.
            - Fields for the survey platform (dict)
            - The fields required for a particular survey platform. Stored in JSON field project.survey_platform_fields.

        """
        ...

    @abstractmethod
    def handle_variable_sync(self, enabled_variables: dict) -> tuple[int, str, str]:
        """Sync the variables from DDS to the survey platform.

        Args:
            enabled_variables:

        Returns:
            A tuple:
            - Status code (HTTPStatus.OK or 40x)
            - Message ID (str)
            - Message English Text (str)
            The status HTTPStatus.OK means that the variables were successfully synced.
            The status 40x means that the variables were not synced.

        """
        ...

    @abstractmethod
    def handle_prepare_survey(
        self, project_short_id: str, survey_platform_fields: str, embedded_data: dict
    ) -> tuple[bool, str | None]:
        """Prepare the survey on the survey platform.

        Args:
            project_short_id:
            survey_platform_fields:
            embedded_data:

        Returns:
            tuple:
            - bool representing whether the survey was successfully prepared or not
            - the unique distribution URL
        """
        ...

    @abstractmethod
    def handle_export_survey_responses(self, project_short_id: str | None = None) -> tuple[int, str, str, str]:
        """Downloads the responses from the survey platform.

        Args:
            project_short_id:

        Returns:
            tuple made of the:
            - Status code (HTTPStatus.OK or 40x)
            - Message ID (str)
            - Message English Text (str)
            - File Content (str) - The content of the file that was downloaded.
        """
        ...

    @staticmethod
    @abstractmethod
    def get_preview_link(survey_platform_fields: dict, enabled_variables: dict) -> tuple[int, str, str, str]:
        """Get the preview link for the survey.
        - Status code (HTTPStatus.OK or 40x)
        - Message ID (str)
        - Message English Text (str)
        - Preview Link (str) - The preview link for the survey.

        Args:
            survey_platform_fields:
            enabled_variables:

        Returns:
            tuple made of the: status code, message id, message english text, and the preview link.
        """
        ...


class OAuthSurveyPlatform(SurveyPlatform):
    # General class attributes
    # These attributes need to be overridden
    token_url: str = ""
    revoke_url: str = ""
    base_authorize_url: str = ""

    _scopes: ClassVar[list[str]] = []

    def __init__(
        self,
        client_id: str | None = None,
        client_secret: str | None = None,
        access_token: str | None = None,
        refresh_token: str | None = None,
        **kwargs,
    ) -> None:
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
    @abstractmethod
    def get_authorize_url(cls) -> str: ...

    @classmethod
    @abstractmethod
    def get_app_credentials(cls) -> dict[str, str]: ...

    # Instance properties
    @property
    def required_scopes(self) -> list[str]:
        return self._required_scopes

    @required_scopes.setter
    def required_scopes(self, scopes: list[str]) -> None:
        self._required_scopes = scopes

    # Methods that child classes must implement
    @abstractmethod
    def init_api_client(self, *args, **kwargs) -> None: ...

    @abstractmethod
    def init_oauth_client(self, *args, **kwargs) -> None: ...

    @abstractmethod
    def get_client_id(self) -> str: ...

    @abstractmethod
    def request_token(self, code: str) -> dict[str, Any]: ...

    @abstractmethod
    def revoke_token(self, token: str) -> bool: ...


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
