#!/usr/bin/env python3
"""Created on 2023-05-23 14:01

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
@author: Stefan Teofanovic (stefan.teofanovic@heig-vd.ch)
"""
from __future__ import annotations

import os
import traceback
from abc import abstractmethod
from typing import Any, TypeVar

from ..get_logger import get_logger
from ..shared_bases import FormField as BaseFormField
from ..shared_bases import FormTextBlock as BaseFormTextBlock
from ..shared_bases import UIRegistry
from ..variable_types import TVariableValue
from .data_categories import DataCategory
from .variables import CustomVariable

__all__ = [
    "TDataProviderClass",
    "TOAuthDataProviderClass",
    "TDataProvider",
    "TOAuthDataProvider",
    "FormField",
    "DataProvider",
    "OAuthDataProvider",
]


logger = get_logger(__name__)

TDataProviderClass = type["DataProvider"]
TDataProvider = TypeVar("TDataProvider", bound="DataProvider")
TOAuthDataProviderClass = type["OAuthDataProvider"]

TOAuthDataProvider = TypeVar("TOAuthDataProvider", bound="OAuthDataProvider")

# Base classes used for defining data providers
DATA_PROVIDER_BASE_CLASSES = ["DataProvider", "OAuthBase"]


# TODO: stop using Enum attribute nomenclature and use attribute names that make sense
class DataProvider(UIRegistry):
    """Base class for data providers that provides common functionality for all data providers.

    Child classes should follow the same class layout to standardize the code base and to facilitate development.
    Comments declare what type of methods are meant to go where.
    Simply copy the class, delete the non-abstract methods, and implement the abstract methods.
    Then you can add any class/instance attributes, form fields, variables, etc.

    Attributes:
    """

    # General class attributes
    base_name: str = "DataProvider"
    # attrs_to_unwrangle: list[str] = [""]
    registry_exclude: list[str] = [
        "DataProvider",
        "OAuthDataProvider",
        "FrontendDataProvider",
    ]
    _package = __package__

    # Do not override the following attributes
    # __registry: dict[str, TDataProviderClass] = {}
    # _cls_form_fields: dict[str, list[dict[str, Any]]] = {}
    _all_data_categories: dict[str, dict[str, DataCategory]] = {}

    # The following are placeholder properties for convenient access to the name wrangled dicts
    # registry: dict[str, TDataProviderClass] = None
    # cls_form_fields: dict[str, list[FormField]] = None

    # The following attributes (normally) do not need to be redeclared in child classes
    app_required: bool = True
    name: str = ""
    name_lower: str = ""
    provider_type: str = "generic"
    label: str = ""
    instructions: str = ""
    instructions_helper_url: str = ""

    # Class attributes that need be redeclared or redefined in child classes
    # The following attributes need to be redeclared in child classes.
    # You can just copy and paste them into the child class body.
    fields: list[dict[str, Any]] = {}
    # Unique class attributes go here

    # Form fields declarations go here
    # Child classes should redeclare the form_fields attribute and populate the list with instances of FormField.
    # These instances are used to create the form when adding a data provider in the UI.
    form_fields: list[FormField] = []

    # Custom Variable Data Categories
    data_categories: list[DataCategory] = []

    # Variable declarations go here
    # Use the @variable decorator

    # Standard/builtin class methods go here
    def __init__(self, *args, **kwargs):
        self._variable_values: dict[str, Any] = {}

    def __str__(self):
        return f"{self.__class__.__name__}"

    def __repr__(self):
        return f"{self.__class__.__name__}()"

    @classmethod
    def register(cls):
        super().register()
        if cls.name not in cls._all_data_categories:
            cls._all_data_categories[cls.name] = {}
        for data_category in cls.data_categories:
            cls._all_data_categories[cls.name][data_category.value] = data_category

    # @classmethod
    # def get_variable_storage(cls) -> dict[str, list[dict[str, Any]]]:
    #     return DataProvider.cls_variables

    # fields are used to generate the form for the user to fill out
    # the dict object "fields" can be used to create an instance of the class using the ** operator: provider_class(**data_connection.fields)

    @classmethod
    def get_builtin_variables(cls) -> list[dict[str, str]]:
        data_cats = cls.get_data_categories()
        # Include the provider_type in each builtin variable dictionary
        return [
            {**item, "provider_type": cls.provider_type}
            for cat in data_cats
            for item in cat["builtin_variables"]
        ]

    # Instance properties

    # Methods used for extracting data
    def select_relevant_variables(
        self, variables: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Selects only the variables that are enabled and relevant to this data provider.

        Args:
            variables:
                List of dicts where each dict contains key/value pairs conforming to the Variable class.

        Returns:
            A list of dicts where each dict contains key/value pairs conforming to the Variable class.
        """
        return [
            variable
            for variable in variables
            if variable.get("enabled", False)
            and (variable["data_provider"] == self.name_lower)
        ]

    def calculate_variables(
        self,
        project_builtin_variables: list[dict] = None,
        project_custom_variables: list[dict] = None,
        **kwargs
    ) -> dict[str, TVariableValue]:
        """Calculates the values of passed variables.

        Args:
            project_builtin_variables:
                List of dicts where each dict contains key/value pairs conforming to the Variable class.
            project_custom_variables:
                List of dicts where each dict contains key/value pairs conforming to the CustomVariable class.

        Returns:
            A dict of key value pairs where the key is the name of the variable and the value is the value of the variable.
            This dict can be passed to SurveyPlatform.upload_variable_values()
        """
        if project_builtin_variables is None:
            project_builtin_variables = []
        if project_custom_variables is None:
            project_custom_variables = []

        calculated_variables = {}

        for variable in self.select_relevant_variables(project_builtin_variables):
            value = None
            try:
                value = self.get_variable_value(**variable)
                exists = value is not None
            except ValueError:
                logger.warning(
                    f"Variable {variable['name']} could not be calculated with the following "
                    f"error:\n{traceback.format_exc()}"
                )
                exists = False

            calculated_variables[variable["qualified_name"]] = value
            calculated_variables[f"{variable['qualified_name']}.exists"] = exists

        for variable in self.select_relevant_variables(project_custom_variables):
            # if variable.get('enabled', False) and variable['data_provider'] == self.name_lower:
            custom_var_manager = CustomVariable(
                data_provider=self, custom_variable=variable
            )

            custom_vars = custom_var_manager.calculate_custom_variables()

            calculated_variables.update(custom_vars)

        return calculated_variables

    def get_variable_value(
        self,
        category: str = "",
        name: str = "",
        qualified_name: str = "",
        is_indexed_variable: bool = False,
        index: int = 0,
        **kwargs,
    ) -> TVariableValue:

        if qualified_name in self._variable_values:
            return self._variable_values[qualified_name]

        data_category_class = self.get_data_category(category.lower())

        logger.debug(f"Calculating variable '{name}' for data category '{category}'")

        if data_category_class is None:
            raise ValueError(f"Data category '{category}' not found")

        variable_func = data_category_class.get_builtin_variable_by_name(
            name
        ).extractor_func

        if variable_func:
            if is_indexed_variable:
                value = variable_func(self, index)
            else:
                value = variable_func(self)
            self._variable_values[name] = value
            return value
        else:
            raise ValueError(
                f"'{self.__class__.__name__}' object does not have a defined function or a factory "
                f"function to build a function for '{name}'"
            )

    @staticmethod
    def get_used_variables(
        project_builtin_variables=None, project_custom_variables=None
    ):
        """Returns a list of dicts containing the name and description of the project enabled variables
        Used by the respondent page to display the variables used in the project
        """
        used_variables = []

        for variable in project_builtin_variables or []:
            if variable.get("enabled", False):
                used_variables.append(
                    {
                        "data_provider": variable.get("data_provider", ""),
                        "variable_name": variable.get("qualified_name", ""),
                        "description": variable["description"],
                        "data_origin": variable.get("data_origin", []),
                        "type": "Builtin",
                    }
                )

        for variable in project_custom_variables or []:
            if variable.get("enabled", False):
                custom_variable = CustomVariable(
                    data_provider=None, custom_variable=variable
                )
                cv_dict = custom_variable.to_dict()
                used_variables.append(
                    {
                        "data_provider": variable.get("data_provider", ""),
                        "variable_name": cv_dict.get("qualified_name", ""),
                        "data": cv_dict,
                        "data_origin": cv_dict.get("data_category", {}).get(
                            "data_origin", []
                        ),
                        "type": "Custom",
                    }
                )

        # order by data provider type
        used_variables = sorted(used_variables, key=lambda v: v["data_provider"])

        return used_variables

    @classmethod
    def get_data_category(cls, data_category_name: str) -> DataCategory:
        """Get a specific data category by its name.

        Args:
            data_category_name (str): The name of the data category to retrieve.

        Returns:
            DataCategory: The requested data category object.

        Raises:
            KeyError: If the specified data category name does not exist.
        """
        return cls._all_data_categories[cls.name][data_category_name]

    @classmethod
    def get_data_categories(cls) -> list[dict[str, Any]]:
        """Get a list of data categories along with their associated data provider and built-in variables.

        Returns:
            list[dict[str, Any]]: A list of dictionaries, where each dictionary represents a data category and its associated data provider, along with a list of built-in variables.
        """
        data_categories_dicts = [cat.to_dict() for cat in cls.data_categories]
        for dct in data_categories_dicts:
            dct["data_provider_name"] = cls.name

            # Updating the builtin variables' names
            for variable in dct["builtin_variables"]:
                category_name = variable["category"].lower()
                variable_name = variable["name"]
                # Check if variable is indexed
                if variable.get("is_indexed_variable", False) and "index" in variable:
                    index = variable["index"]
                    qualified_name = f"dds.{cls.name.lower()}.builtin.{category_name}.{variable_name}{index}"
                else:
                    qualified_name = f"dds.{cls.name.lower()}.builtin.{category_name}.{variable_name}"

                variable["qualified_name"] = qualified_name
                variable["data_provider"] = cls.name.lower()
                variable["type"] = "Builtin"

            # sort the builtin variables by updated name
            dct["builtin_variables"] = sorted(
                dct["builtin_variables"], key=lambda v: v["name"]
            )

        return data_categories_dicts

    @classmethod
    def get_all_data_categories(cls) -> list[dict[str, str]]:
        subclass: TDataProviderClass
        categories = [
            item
            for subclass in cls.registry.get("DataProvider").values()
            for item in subclass.get_data_categories()
        ]
        return sorted(
            categories, key=lambda dp: (dp["data_provider_name"], dp["label"])
        )

    @classmethod
    def get_all_form_fields(cls) -> list[dict[str, Any]]:
        """Get a list of all form fields along with their associated metadata.

        Returns:
            list[dict[str, Any]]: A list of dictionaries, where each dictionary represents a form field and its associated metadata.
        """
        registry = cls.get_registry()

        result = []

        subclass: UIRegistry
        for subclass in registry.values():
            # item = {
            #     "label": subclass.label,
            #     "value": subclass.name_lower,
            #     "instructions": subclass.instructions,
            #     "instructions_helper_url": subclass.instructions_helper_url,
            #     "fields": subclass.get_fields()
            # }

            item = subclass.to_dict()
            item["app_required"] = subclass.app_required

            if hasattr(subclass, "get_redirect_uri"):
                item["oauth2"] = {"redirect_uri": subclass.get_redirect_uri()}

            result.append(item)

        return result

    # Methods that child classes must implement
    @abstractmethod
    def test_connection_before_extraction(self) -> bool:
        ...

    @abstractmethod
    def test_connection(self) -> bool:
        ...

    def to_public_dict(self) -> dict[str, Any]:
        return {
            "data_provider_name": self.name_lower,
            "type": self.provider_type,
        }

    # Properties to access class attributes

    # Class methods

    # Instance properties

    # Instance methods

    # Cached API responses
    # API calls should be wrapped in properties using @cached_property decorators

    # Extractor functions
    # These are functions that extract user data from the API


class FrontendDataProvider(DataProvider):

    # Class attributes that need be redeclared or redefined in child classes
    provider_type: str = "frontend"

    # Standard class methods go here
    def __init__(self, **kwargs):

        super().__init__(**kwargs)

    def test_connection(self) -> bool:
        return True

    def get_variable_value(
        self, data: dict[str, Any], variable: dict[str, Any], **kwargs
    ) -> TVariableValue:

        name = variable["name"]
        category = variable["category"]
        qualified_name = variable["qualified_name"]

        if qualified_name in self._variable_values:
            return self._variable_values[qualified_name]

        data_category_class = self.get_data_category(category.lower())

        logger.debug(f"Calculating variable '{name}' for data category '{category}'")

        if data_category_class is None:
            raise ValueError(f"Data category '{category}' not found")

        variable_func = data_category_class.get_builtin_variable_by_name(
            name
        ).extractor_func

        if variable_func:
            return variable_func(variable=variable, data=data)
        else:
            raise ValueError(
                f"'{self.__class__.__name__}' object does not have a defined function or a factory "
                f"function to build a function for '{name}'"
            )

    def calculate_variables(
        self, project_builtin_variables: dict[str, Any], data: dict[str, Any]
    ) -> dict[str, Any]:
        select_relevant_variables = self.select_relevant_variables(
            project_builtin_variables
        )
        calculated_variables = {}
        for variable in select_relevant_variables:
            value = self.get_variable_value(data, variable)
            exists = value is not None
            if exists:
                calculated_variables[variable["qualified_name"]] = value
            else:
                calculated_variables[variable["qualified_name"]] = ""
            calculated_variables[f"{variable['qualified_name']}.exists"] = exists

        return calculated_variables


class OAuthDataProvider(DataProvider):
    # General class attributes
    # These attributes need to be overridden
    token_url: str = ""
    revoke_url: str = ""
    base_authorize_url: str = ""

    # Class attributes that need be redeclared or redefined in child classes
    provider_type: str = "oauth"

    _scopes: list[str] = []
    _categories_scopes: dict[str, str] = {}

    def __init__(
        self,
        client_id: str = None,
        client_secret: str = None,
        access_token: str = None,
        refresh_token: str = None,
        builtin_variables: list[dict] = None,
        custom_variables: list[dict] = None,
        **kwargs,
    ):
        super().__init__()
        self.client_id: str = client_id
        self.client_secret: str = client_secret
        self.access_token: str = access_token
        self.refresh_token: str = refresh_token
        self._authorize_url: str = ""
        self._required_scopes: list[str] = []

        self.api_client = None
        self.oauth_client = None

        self.builtin_variables = builtin_variables
        self.custom_variables = custom_variables

    def __repr__(self):
        return (f"{self.__class__.__name__}(client_id={self.client_id!r}, client_secret={self.client_secret!r}, "
                f"access_token={self.access_token!r}, refresh_token={self.refresh_token!r}, "
                f"self.api_client={self.api_client!r}, self.oauth_client={self.oauth_client!r}, "
                f"self.builtin_variables={self.builtin_variables!r}, self.custom_variables={self.custom_variables!r})")
    @classmethod
    def get_redirect_uri(cls) -> str:
        # TODO: avoid using environment variables.
        frontend_url = os.getenv("FRONTEND_URL")
        if frontend_url is None or frontend_url == "":
            logger.critical("FRONTEND_URL environment variable not set, empty, or failed to load.")
        return f"{frontend_url}/dist/redirect/{cls.name_lower}"

    def to_public_dict(self) -> dict:
        # Now requires context data to generate the authorize_url
        authorize_url = self.get_authorize_url(
            builtin_variables=self.builtin_variables,
            custom_variables=self.custom_variables,
        )
        return {
            **super().to_public_dict(),
            "client_id": self.client_id,
            "authorize_url": authorize_url,
        }

    # Instance properties
    @property
    def scopes(self):
        return self.__class__._scopes

    @property
    def required_scopes(self) -> list[str]:
        return self._required_scopes

    @required_scopes.setter
    def required_scopes(self, scopes: list[str]):
        self._required_scopes = scopes

    # Instance methods
    def get_required_scopes(
        self, builtin_variables: list[dict] = None, custom_variables: list[dict] = None
    ) -> list[str]:
        if len(self.required_scopes) > 0:
            return self.required_scopes

        if builtin_variables is None:
            builtin_variables = []
        if custom_variables is None:
            custom_variables = []

        builtin_variables = self.select_relevant_variables(builtin_variables)
        custom_variables = self.select_relevant_variables(custom_variables)

        required_scopes = {
            self._categories_scopes[v["category"]] for v in builtin_variables
        }

        required_scopes.union(
            {self._categories_scopes[v["data_category"]] for v in custom_variables}
        )

        required_scopes = list(required_scopes)

        self.required_scopes = required_scopes
        return required_scopes

    # Methods that child classes must implement
    @abstractmethod
    def init_api_client(self, *args, **kwargs) -> None:
        ...

    @abstractmethod
    def init_oauth_client(self, *args, **kwargs) -> None:
        ...

    @abstractmethod
    def get_authorize_url(
        self, builtin_variables: list[dict], custom_variables: list[dict] = None
    ) -> str:
        ...

    @abstractmethod
    def get_client_id(self) -> str:
        ...

    @abstractmethod
    def request_token(self, data: dict[str, Any]) -> dict[str, Any]:
        ...

    @abstractmethod
    def revoke_token(self, token: str) -> bool:
        ...


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
    _registry_class = DataProvider
    _registry_class_name: str = ""  # No need to set this manually.


class FormTextBlock(BaseFormTextBlock):
    """This class is used to declare text blocks that a data provider needs to be filled when it is added in the UI.

    Attributes:
        content (str):
            The content of the text block.
        type (str):
            The type of the text block.
            Allowed values are: "text"
    """

    shared_prefix_text: str = "api"
    _package: str = ""
    _registry_class = DataProvider
    _registry_class_name: str = ""  # No need to set this manually.
