#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2023-09-05 18:07

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
"""
from __future__ import annotations
import os
import re
import inspect
from flask import current_app
from copy import deepcopy
from abc import abstractmethod
from functools import cached_property
from typing import Any, Optional, Type, List, Dict, Tuple
from pprint import pprint

from .get_logger import get_logger

logger = get_logger(__name__)

TRegistryClass = Type["Registry"]
TUIRegistryClass = Type["UIRegistry"]

class FormElement:
    shared_prefix_text: str = "ddsurveys"

    def __init__(self, name: str, label: Optional[str] = None, helper_text: Optional[str] = None, data: Optional[Dict[str, Any]] = None, visibility_conditions: Optional[Dict[str, Any]] = None, interaction_effects: Optional[Dict[str, Any]] = None):
        self.name = name
        self.label = label
        if label is None:
            self.label = f"{name}.label"

        self.visibility_conditions = visibility_conditions
        self.interaction_effects = interaction_effects

        self.helper_text = helper_text
        if helper_text is None:
            self.helper_text = f"{name}.helper_text"

        self.data = data

    @classmethod
    def prefix_text(cls, text: str, class_: type) -> str:
        label = text
        if not text.startswith(cls.shared_prefix_text):
            label = f"{cls.shared_prefix_text}.{class_.__module__}.{text}"
        return label
    
    def get_qualified_name(self, class_: type) -> str:
        """
        Returns the fully qualified name key for the field.

        Args:
            class_ (type): Class in which the FormField instance is contained.

        Returns:
            str: Fully qualified name key.
        """
        return self.prefix_text(self.name, class_)
    
    @cached_property
    def registry_class(self) -> TUIRegistryClass:
        return self.__class__._registry_class

    @property
    def package(self) -> str:
        return self.__class__._package

    @package.setter
    def package(self, value: str):
        self.__class__._package = value


class FormButton(FormElement):
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
        data (dict):
            Additional data that will be sent to the frontend.
            This data will be available in the frontend when the button is clicked.
        onClick (dict):
            The onClick event of the button.
            The dictionary should contain the following keys:
                "action" (str): The action that should be performed when the button is clicked. This should be implemented in the reducer passed to the frontend FormFields component.
                "args" (dict): The arguments that should be passed to the action hanlder.
    """


    def __init__(self, onClick: Optional[Dict[str, Any]] = None, **kwargs):
        super().__init__(**kwargs)
        self.onClick = onClick
        self.type = "button"


    def register_field(self, cls):
        class_name = cls.__name__

        if self.package == "" and hasattr(cls, "_package"):
            self.package = getattr(cls, "_package", "")

        if not self.package.startswith("."):
            self.package = f".{self.package}"

        self.label = self.prefix_text(self.label, cls)
        if self.helper_text is not None and self.helper_text != "":
            self.helper_text = self.prefix_text(self.helper_text, cls)

        if class_name not in self.registry_class.cls_form_fields:
            self.registry_class.cls_form_fields[class_name] = []

        self.registry_class.cls_form_fields[class_name].append({
            "name": self.name,
            "label": self.label,
            "helper_text": self.helper_text,
            "type": self.type,
            "visibility_conditions": self.visibility_conditions,
            "onClick": self.onClick,
            "data": self.data
        })
        return cls
    
    


class FormField(FormElement):
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

    _package: str = ""
    _registry_class: TRegistryClass = None
    _registry_class_name: str = ""  # No need to set this manually.

class FormField(FormElement):
    def __init__(self, type: str = "text", value: str = "", required: bool = True, disabled: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.type = type
        self.required = required

        self.value = value
        self.disabled = disabled

        self.__class__._registry_class_name = self.__class__._registry_class.__name__


    def register_field(self, cls):
        class_name = cls.__name__

        if self.package == "" and hasattr(cls, "_package"):
            self.package = getattr(cls, "_package", "")

        if not self.package.startswith("."):
            self.package = f".{self.package}"

        self.label = self.prefix_text(self.label, cls)
        if self.helper_text is not None and self.helper_text != "":
            self.helper_text = self.prefix_text(self.helper_text, cls)

        if class_name not in self.registry_class.cls_form_fields:
            self.registry_class.cls_form_fields[class_name] = []

        self.registry_class.cls_form_fields[class_name].append({
            "name": self.name,
            "label": self.label,
            "value": self.value,
            "type": self.type,
            "disabled": self.disabled,
            "required": self.required,
            "helper_text": self.helper_text,
            "visibility_conditions": self.visibility_conditions,
            "interaction_effects": self.interaction_effects,
            "data": self.data
        })
        return cls

    @classmethod
    def check_input_fields(cls, fields: List[dict], form_fields: List[FormField],
                           override_required_fields: List[str] = None,
                           class_: type = None) -> Tuple[bool, Optional[str]]:
        """
        Check if all the required fields are present and not empty in the input fields.

        Args:
            fields (list): List of input fields with their values.
            form_fields (list): List of FormField instances.
            override_required_fields (optional) List[str]: List of fields that are not required.
            class_ (type): Class in which the FormField instance is contained.

        Returns:
            tuple: (True, None) if all required fields are present.
                (False, <full name key>) if any required field is missing.
        """
        if override_required_fields is None:
            override_required_fields = []

        if class_ is None:
            class_ = cls

        # transform the list into dict
        if isinstance(fields, list):
            fields = {field['name']: field.get('value', None) for field in fields}

        # Check if the required fields are present
        for field in form_fields:
            if field.type in ['text', 'hidden']:
                required = field.required

                if field.name in override_required_fields:
                    required = True

                if required and not fields.get(field.name, None):
                    # Return (False, full name key of the missing field)
                    return False, field.get_qualified_name(class_)

        return True, None

    def __repr__(self):
        return (f"{self.__class__.__name__}(name={self.name!r}, type={self.type!r}, required={self.required!r}, "
                f"label={self.label!r}, helper_text={self.helper_text!r}, data={self.data!r})")

reg_dicts = []

class RegistryBase(type):
    registries: dict[str, Registry] = {}

    __calls_counter = {}

    @classmethod
    def getattr_from_all_parents(mcs, class_: Registry, attribute: str, values: list = None) -> list:
        if values is None:
            values = []
        if hasattr(class_._parent, attribute):
            values.append(getattr(class_._parent, attribute))
        else:
            values.append(mcs.getattr_from_all_parents(attribute, values))
        return values

    @classmethod
    def get_first_defined_from_parents(mcs, class_: Registry, attribute: str, default=None) -> Any:
        if class_ is None:
            return default

        val = getattr(class_._parent, attribute, None)
        if val:
            return val
        else:
            return mcs.get_first_defined_from_parents(class_._parent, attribute, default)

    # @staticmethod
    # def bind_to_base(base_class: Registry, child_class: Registry, attr_name: str):
    #     if base_class is not None and child_class is not None:
    #         setattr(child_class, attr_name, getattr(base_class, attr_name))

    @staticmethod
    def bind_to_base(base_class: Registry, child_class: Registry, attributes: list[str]):
        if base_class is not None and child_class is not None:
            for attr_name in attributes:
                setattr(child_class, attr_name, getattr(base_class, attr_name))

    @classmethod
    def rebind_wrangled_attributes(mcs, class_, attributes: list[str]):
        for attr_name in attributes:
            wrangled_name, unwrangled_name = mcs.unwrangle_name(class_, attr_name)
            setattr(class_, unwrangled_name, getattr(class_, wrangled_name))

    @staticmethod
    def unwrangle_name(class_, name: str) -> tuple[str, str]:
        wrangled_name = name
        unwrangled_name = ""
        if name.startswith("__"):
            wrangled_name = f"_{class_.__name__}{wrangled_name}"
            unwrangled_name = name[2:]

        elif wrangled_name.startswith("_"):
            unwrangled_name = wrangled_name[1:]

        return wrangled_name, unwrangled_name

    @classmethod
    def print_num_calls(cls):
        pprint(cls.__calls_counter)

    def __new__(mcs, name, bases, attrs, **kwargs):
        if name not in mcs.__calls_counter:
            mcs.__calls_counter[name] = 0
        mcs.__calls_counter[name] += 1

        # Code partially based on django.db.models.base.ModelBase
        super_new = super().__new__

        # Also ensure initialization is only performed for subclasses of Model
        # (excluding Model class itself).
        parents = [b for b in bases if isinstance(b, RegistryBase)]
        if len(parents) == 0:
            new_class = super_new(mcs, name, bases, attrs)
            mcs.rebind_wrangled_attributes(new_class, attrs.get("attrs_to_unwrangle", []))
            return new_class

        # Create the class.
        module = attrs.pop("__module__")
        new_attrs = {"__module__": module}
        classcell = attrs.pop("__classcell__", None)
        if classcell is not None:
            new_attrs["__classcell__"] = classcell
        attr_meta = attrs.pop("Meta", None)
        for attr_name, attr_value in attrs.items():
            new_attrs[attr_name] = attr_value
        new_class = super_new(mcs, name, bases, new_attrs, **kwargs)

        new_class._parent = parents[0]

        # Preparing to bind class attributes

        # Extend class attributes that are lists using parent's values
        attrs_to_bind_to_base = deepcopy(attrs.get("attrs_to_bind_to_base", []))
        attrs_to_unwrangle = deepcopy(attrs.get("attrs_to_unwrangle", []))
        to_dict_attrs = deepcopy(attrs.get("to_dict_attrs", []))

        attrs_to_bind_to_base.extend(mcs.get_first_defined_from_parents(new_class, "attrs_to_bind_to_base"))
        attrs_to_unwrangle.extend(mcs.get_first_defined_from_parents(new_class, "attrs_to_unwrangle"))
        to_dict_attrs.extend(mcs.get_first_defined_from_parents(new_class, "to_dict_attrs", []))

        new_class.attrs_to_bind_to_base = attrs_to_bind_to_base
        new_class.attrs_to_unwrangle = attrs_to_unwrangle
        new_class.to_dict_attrs = to_dict_attrs

        registration_base = None
        direct_base_name = ""

        p: Registry
        base_name_list = [p.base_name for p in parents
                          if hasattr(p, "base_name") and p.base_name != ""]
        if len(base_name_list) > 0 and "base_name" not in attrs:
            direct_base_name = base_name_list[-1]

        # all_dicts_to_bind = mcs.getattr_from_all_parents(new_class, "attrs_to_unwrangle")
        # for l in all_dicts_to_bind:
        #     attrs_to_unwrangle.extend(l)
        #     attrs_to_unwrangle = set(attrs_to_unwrangle)  # Remove duplicates
        #     attrs_to_unwrangle = sorted(list(attrs_to_unwrangle))
        #
        # new_class.attrs_to_unwrangle = attrs_to_unwrangle

        if direct_base_name in mcs.registries:
            registration_base = mcs.registries[direct_base_name]
        elif name in mcs.registries:
            # Handle case where class code is executed multiple times.
            # TODO: fix importing to avoid circular imports and needing this.
            registration_base = mcs.registries[name]
        else:
            pass

        mcs.bind_to_base(registration_base, new_class, attrs_to_bind_to_base)

        if registration_base is not None:
            # Register the child class
            if name not in registration_base.registry_exclude and name not in mcs.registries:
                new_class.register()

        reg_dict = getattr(new_class, f"_{name}__registry", None)
        reg_dicts.append([name, reg_dict, id(reg_dict)])

        if attrs.get("base_name", "") != "" and name not in mcs.registries:
            mcs.registries[name] = new_class

        return new_class


class Registry(metaclass=RegistryBase):
    # General class attributes
    base_name: str = "Registry"
    attrs_to_bind_to_base: list[str] = ["registry", "registry_exclude"]
    attrs_to_unwrangle: list[str] = ["__registry", "__registry_exclude"]
    _package = __package__
    _parent: Registry = None

    to_dict_attrs: list[str] = []

    __registry: dict[str, TRegistryClass] = {}
    __registry_exclude: list[str] = []

    # The following are placeholder properties for convenient access to the name wrangled dicts
    registry: dict[str, dict[str, TRegistryClass]] = None
    registry_exclude: list[str] = None

    # The following attributes (normally) do not need to be redeclared in child classes
    name: str = ""
    name_lower: str = ""
    label: str = ""
    package: str = ""
    """This is the name of the package/module that contains the base class."""

    @classmethod
    def register(cls):
        # Set class attributes
        # cls.name = cls.__name__[:-len(base.__name__.split(".")[-1])]
        if cls.base_name in cls.__name__:
            cls.name = cls.__name__[:-len(cls.base_name)]
        else:
            cls.name = cls.__name__
        cls.name_lower = cls.name.lower()
        cls.value = cls.name_lower  # For compatibility with old naming approach
        cls.label = cls.name
        cls.package = cls._package

        # Register the class in the registry dict for text-based lookups
        base_name = cls.base_name
        if base_name not in cls.registry:
            cls.registry[base_name] = {}

        if cls.name not in cls.registry[base_name]:
            cls.registry[base_name][cls.name] = cls


    @classmethod
    def register_subclasses(cls, class_=None):
        if class_ is None:
            class_ = cls
        for subclass in class_.__subclasses__():
            if subclass.__name__ in cls.__registry_exclude:
                cls.register_subclasses(subclass)
            elif cls.base_name in subclass.__name__:
                subclass.register()

    @classmethod
    def get_registry(cls) -> dict[str, TRegistryClass]:
        registry = cls.__registry.get(cls.base_name)
        if registry is None:
            raise ValueError(f"No subclasses of {cls.base_name} have been registered.")
        return registry

    @classmethod
    def get_class_by_name(cls, name) -> TRegistryClass:
        return cls.registry.get(name)

    @classmethod
    def get_class_by_value(cls, value) -> TRegistryClass:
        for subclass in cls.registry.get(cls.base_name, {}).values():
            if subclass.name_lower == value:
                return subclass
        return None

    @classmethod
    def to_dict(cls) -> dict:
        d = {attr: getattr(cls, attr) for attr in cls.to_dict_attrs}
        return d


class UIRegistry(Registry):
    base_name = "UIRegistry"

    attrs_to_bind_to_base: list[str] = ["cls_form_fields"]
    # attrs_to_unwrangle: list[str] = ["__cls_form_fields"]

    _parent = Registry

    cls_form_fields: dict[str, list[dict[str, Any]]] = {}

    instructions: str = ""
    instructions_helper_url: str = ""

    callback_url: str = ""
    app_creation_url: str = ""
    dds_app_creation_instructions: str = ""

    to_dict_attrs: list[str] = ["label", "value", "instructions", "instructions_helper_url",
                                "callback_url", "app_creation_url", "dds_app_creation_instructions",
                                "fields"]
    """Attributes that will be packaged into a dictionary to be sent as responses through the API."""

    # Class attributes that need be redeclared or redefined in child classes
    # The following attributes need to be redeclared in child classes.
    # You can just copy and paste them into the child class body.
    fields: list[dict[str, Any]] = {}

    # Form fields declarations go here
    # Child classes should redeclare the form_fields attribute and populate the list with instances of FormField.
    # These instances are used to create the form when adding a data provider in the UI.
    form_fields: list[FormField] = []

    @classmethod
    def register(cls):
        super().register()

        package = f".{cls._package}" if cls._package != "" else ""
        cls.instructions = f"api{package}.{cls.name_lower}.instructions.text"
        cls.instructions_helper_url = f"api{package}.{cls.name_lower}.instructions.helper_url"

        cls.callback_url = f"dist/redirect/{cls.name_lower}"

        # Add class to the shared dictionaries to avoid errors in future methods
        if cls.__qualname__ not in cls.cls_form_fields:
            cls.cls_form_fields[cls.__qualname__] = []

        for field in cls.form_fields:
            field.register_field(cls)

        cls.fields = cls.get_fields()

    @classmethod
    def get_form_fields_storage(cls) -> dict[str, list[dict[str, Any]]]:
        return cls._cls_form_fields

    @classmethod
    def get_fields(cls) -> list[FormField]:
        return cls.cls_form_fields.get(cls.__qualname__, [])

    @classmethod
    def get_all_form_fields(cls) -> list[dict[str, Any]]:
        registry = cls.get_registry()

        result = []

        subclass: UIRegistry
        for subclass in registry.values():
            item = {
                "label": subclass.label,
                "value": subclass.name_lower,
                "instructions": subclass.instructions,
                "instructions_helper_url": subclass.instructions_helper_url,
                "fields": subclass.get_fields()
            }

            if hasattr(subclass, "get_authorize_url"):
                item["oauth2"] = {
                    "authorize_url": subclass.get_authorize_url()
                }

            result.append(item)

        return result
    


class OAuthBase:
    # General class attributes
    # These attributes need to be overridden

    token_url: str = ""
    revoke_url: str = ""
    base_authorize_url: str = ""
    redirect_uri: str = ""

    _scopes: list[str] = []
    _categories_scopes: dict[str, str] = {}

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

    # Methods that child classes must implement
    @abstractmethod
    def init_api_client(self, *args, **kwargs) -> None:
        pass

    @abstractmethod
    def init_oauth_client(self, *args, **kwargs) -> None:
        pass

    @abstractmethod
    def get_authorize_url(self, builtin_variables: list[dict], custom_variables: list[dict] = None) -> str:
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
