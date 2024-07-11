#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This module defines a flexible framework for creating and managing form elements within a UI, specifically tailored for
data providers. It includes classes for form elements such as buttons, fields, and text blocks, each with customizable
attributes for labels, helper texts, visibility conditions, and interaction effects. The module also introduces a
registry system to dynamically manage these form elements and ensure their proper integration and functionality within
the UI.

The core classes include:
- `FormElement`: The base class for all form elements, providing common properties and methods.
- `FormButton`: A class for creating buttons with customizable actions and data.
- `FormField`: A class for creating input fields with various types and validation requirements.
- `FormTextBlock`: A class for creating text blocks to display information or instructions.

Additionally, the module provides a `RegistryBase` metaclass for creating registries that manage the instantiation and
registration of form elements, facilitating their reuse and customization across different parts of the UI.

Created on 2023-09-05 18:07

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
@author: Stefan Teofanovic (stefan.teofanovic@heig-vd.ch)
"""
from __future__ import annotations

from abc import abstractmethod, ABC
from copy import deepcopy
from functools import cached_property
from logging import Logger
from pprint import pprint
from typing import Any, Optional, Type, Union
from typing_extensions import override

from .get_logger import get_logger

logger: Logger = get_logger(__name__)

TRegistryClass = Type["Registry"]
TUIRegistryClass = Type["UIRegistry"]


class FormElement(ABC):
    """
    The base class for all form elements within the UI framework, providing a foundation for creating interactive and
    dynamic form components. This class encapsulates common properties and functionalities shared across different types
    of form elements, such as buttons, fields, and text blocks. It includes mechanisms for setting labels, helper texts,
    visibility conditions, and interaction effects, allowing for a highly customizable user interface experience.

    Attributes:
        name (str): The unique identifier for the form element.
        label (Optional[str]): The display label for the form element, used for UI presentation.
        helper_text (Optional[str]): Additional information or guidance provided to the user regarding the form element.
        data (Optional[dict[str, Any]]): Arbitrary data associated with the form element, for use in custom behaviors or callbacks.
        visibility_conditions (Optional[dict[str, Any]]): Conditions that determine when the form element is visible to the user.
        interaction_effects (Optional[dict[str, Any]]): Effects or actions triggered by user interaction with the form element.

    The class also provides utility methods for prefixing text with a shared prefix and generating qualified names for form elements,
    facilitating consistency and namespace management within the UI framework.
    """

    _package: str
    _registry_class: TUIRegistryClass
    _registry_class_name: str

    shared_prefix_text: str = "ddsurveys"

    def __init__(
        self,
        name: str,
        label: Optional[str] = None,
        helper_text: Optional[str] = None,
        data: Optional[dict[str, Any]] = None,
        visibility_conditions: Optional[dict[str, Any]] = None,
        interaction_effects: Optional[dict[str, Any]] = None,
    ) -> None:
        """
        Initialize a new instance of FormElement.

        Args:
            name (str): The name of the form element.
            label (Optional[str]): The label of the form element. Defaults to None.
            helper_text (Optional[str]): The helper text for the form element. Defaults to None.
            data (Optional[dict[str, Any]]): Additional data associated with the form element. Defaults to None.
            visibility_conditions (Optional[dict[str, Any]]): Conditions under which the form element is visible. Defaults to None.
            interaction_effects (Optional[dict[str, Any]]): Effects triggered by interaction with the form element. Defaults to None.
        """
        self.name: str = name
        self.label: str = label or f"{name}.label"

        self.visibility_conditions: dict[str, Any] | None = visibility_conditions
        self.interaction_effects: dict[str, Any] | None = interaction_effects

        self.helper_text: str = helper_text or f"{name}.helper_text"

        self.data: dict[str, Any] | None = data

    @classmethod
    def prefix_text(cls, text: str, class_: type) -> str:
        """
        Prefixes the given text with a shared prefix and the module of the provided class.

        Args:
            text (str): The text to be prefixed.
            class_ (type): The class whose module will be used in the prefix.

        Returns:
            str: The prefixed text.
        """
        label: str = text
        if not text.startswith(cls.shared_prefix_text):
            label = f"{cls.shared_prefix_text}.{class_.__module__}.{text}"
        return label

    def get_qualified_name(self, class_: type) -> str:
        """
        Generates a fully qualified name for the form element based on its name and the class it is associated with.

        Args:
            class_ (type): The class associated with the form element.

        Returns:
            str: The fully qualified name key for the form element.
        """
        return self.prefix_text(self.name, class_)

    @cached_property
    def registry_class(self) -> TUIRegistryClass:
        """
        Returns the registry class associated with this form element.

        Returns:
            TUIRegistryClass: The registry class.
        """
        return self.__class__._registry_class

    @property
    def package(self) -> str:
        """
        Returns the package name associated with this form element.

        Returns:
            str: The package name.
        """
        return self.__class__._package

    @package.setter
    def package(self, value: str) -> None:
        """
        Sets the package name for this form element.

        Args:
            value (str): The new package name.
        """
        self.__class__._package = value

    @abstractmethod
    def register_field(self, cls: type) -> type:
        ...


class FormButton(FormElement):
    """
    A class for creating button elements within a UI framework, designed to be filled by data providers upon addition to the UI.

    This class extends `FormElement` to include functionality specific to buttons, such as handling click events and passing additional data to the frontend. It allows for the customization of button labels, helper texts, and the actions performed on click events, facilitating interactive and dynamic UI components.

    Attributes:
        name (str): The unique identifier for the button.
        label (str): The display label for the button, used for UI presentation. If not provided, it is generated based on the button's name.
        helper_text (str): Additional information or guidance provided to the user regarding the button. If not provided, it is generated based on the button's name.
        data (dict): Arbitrary data associated with the button, sent to the frontend when the button is clicked.
        on_click (dict): A dictionary specifying the action to be performed when the button is clicked, including the action type and arguments for the action handler.

    The `on_click` dictionary should contain:
        - "action" (str): The action to be performed on click.
        - "args" (dict): Arguments to be passed to the action handler.
    """

    def __init__(self, on_click: Optional[dict[str, Any]] = None, **kwargs) -> None:
        """
        Initializes a new instance of the FormButton class.

        Args:
            on_click (Optional[dict[str, Any]]): A dictionary specifying the onClick event for the button. Defaults to None.
                                                 It should specify the action to be performed when the button is
                                                 clicked and any arguments that should be passed to the action handler.
            **kwargs: Arbitrary keyword arguments passed to the base class initializer.


        """
        super().__init__(**kwargs)
        self.on_click: dict[str, Any] | None = on_click
        self.type = "button"
        self.__class__._registry_class_name = self.__class__._registry_class.__name__

    @override
    def register_field(self, cls: type) -> type:
        """
        Registers the button as a field within a given class, allowing it to be dynamically managed and reused across different parts of the UI.

        This method prefixes the button's label and helper text with a shared prefix and the module of the provided class to ensure uniqueness and consistency. It then adds the button to the registry of form fields associated with the class, making it available for instantiation and rendering in the UI.

        Args:
            cls (type): The class with which this button is to be registered.

        Returns:
            Type: The class passed as an argument, allowing for method chaining or further modifications.
        """
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

        self.registry_class.cls_form_fields[class_name].append(
            {
                "name": self.name,
                "label": self.label,
                "helper_text": self.helper_text,
                "type": self.type,
                "visibility_conditions": self.visibility_conditions,
                "onClick": self.on_click,
                "data": self.data,
            }
        )
        return cls


class FormField(FormElement):
    """
    A class representing a form field within a UI framework, designed for data providers to specify the fields that need to be filled out when added to the UI.

    Attributes:
        name (str): The name of the field, serving as a unique identifier.
        type (str): The type of input expected for the field, e.g., "text".
        required (bool): Indicates whether the field must be filled out. Defaults to True.
        label (str): The display label for the field. If not provided, a label is generated based on the field's name.
        helper_text (str): Additional guidance provided for the field. If not provided, helper text is generated based on the field's name.
        value (str): The default value of the field. Defaults to an empty string.
        disabled (bool): Indicates whether the field is disabled (i.e., not editable). Defaults to False.
    """

    def __init__(
        self,
        type: str = "text",
        value: str = "",
        required: bool = True,
        disabled: bool = False,
        **kwargs,
    ) -> None:
        """
        Initializes a new instance of FormField.

        Args:
            type (str): The type of input for the field. Defaults to "text".
            value (str): The default value of the field. Defaults to an empty string.
            required (bool): Whether the field is required. Defaults to True.
            disabled (bool): Whether the field is disabled. Defaults to False.
            **kwargs: Arbitrary keyword arguments passed to the base class initializer.
        """
        super().__init__(**kwargs)
        self.type = type
        self.required = required

        self.value = value
        self.disabled = disabled

        self.__class__._registry_class_name = self.__class__._registry_class.__name__

    @override
    def register_field(self, cls: type) -> type:
        """
        Registers the field within a given class, allowing it to be dynamically managed and reused across different parts of the UI.

        This method prefixes the field's label and helper text with a shared prefix and the module of the provided class to ensure uniqueness and consistency. It then adds the field to the registry of form fields associated with the class, making it available for instantiation and rendering in the UI.

        Args:
            cls (type): The class with which this field is to be registered.

        Returns:
            type: The class passed as an argument, allowing for method chaining or further modifications.
        """
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

        self.registry_class.cls_form_fields[class_name].append(
            {
                "name": self.name,
                "label": self.label,
                "value": self.value,
                "type": self.type,
                "disabled": self.disabled,
                "required": self.required,
                "helper_text": self.helper_text,
                "visibility_conditions": self.visibility_conditions,
                "interaction_effects": self.interaction_effects,
                "data": self.data,
            }
        )
        return cls

    @classmethod
    def check_input_fields(
        cls,
        fields: list[dict],
        form_fields: list[FormField | FormButton],
        override_required_fields: list[str] = None,
        class_: type = None,
    ) -> tuple[bool, Optional[str]]:
        """
        Checks if all required fields are present and not empty in the input fields.

        Args:
            fields (list[dict]): A list of dictionaries representing input fields with their values.
            form_fields (list[FormField | FormButton]): A list of FormField or FormButton instances to check against.
            override_required_fields (list[str], optional): A list of field names that are not required, even if marked as such.
            class_ (type, optional): The class in which the FormField instance is contained. Defaults to None.

        Returns:
            tuple[bool, Optional[str]]: A tuple containing a boolean indicating success (True if all required fields are present) and an optional string representing the full name key of a missing field if any.
        """
        if override_required_fields is None:
            override_required_fields = []

        if class_ is None:
            class_ = cls

        # transform the list into dict
        if isinstance(fields, list):
            fields = {field["name"]: field.get("value", None) for field in fields}

        # Check if the required fields are present
        for field in form_fields:
            if field.type in ["text", "hidden"]:
                required = field.required

                if field.name in override_required_fields:
                    required = True

                if required and not fields.get(field.name, None):
                    # Return (False, full name key of the missing field)
                    return False, field.get_qualified_name(class_)

        return True, None

    def __repr__(self) -> str:
        """
        Returns a string representation of the FormField instance.

        Returns:
            str: A string representation of the FormField instance, including its name, type, required status, label, helper text, and data.
        """
        return (
            f"{self.__class__.__name__}(name={self.name!r}, type={self.type!r}, required={self.required!r}, "
            f"label={self.label!r}, helper_text={self.helper_text!r}, data={self.data!r})"
        )


class FormTextBlock(FormElement):
    """
    This class is used to declare text blocks that provide information, instructions, or any kind of descriptive text
    in the UI.

    Attributes:
        content (str):
            The content of the text block. This is the actual text that will be displayed in the UI.
        position (int):
            The position where the text block should be displayed relative to other elements in the UI. This could be
            interpreted by the frontend to place the text block in the correct order among other form elements.
    """

    def __init__(self, content: str, **kwargs) -> None:
        """
        Initializes a new instance of the FormTextBlock class.

        This constructor sets up a text block element with the specified content. It is designed to provide descriptive
        text within the UI, such as instructions or information. The `type` attribute is set to "textblock" to distinguish
        it from other form elements.

        Args:
            content (str): The text content of the text block. This is the actual text that will be displayed.
            **kwargs: Arbitrary keyword arguments that are passed to the base class initializer. This allows for the
                    inclusion of additional parameters that are common to all form elements, such as name, visibility
                    conditions, and interaction effects.

        Returns:
            None
        """
        super().__init__(**kwargs)
        self.content: str = content
        self.type = "textblock"  # This type is used to render the element appropriately in the frontend.

    @override
    def register_field(self, cls: type) -> type:
        """
        Registers the text block as a field within a given class, allowing it to be dynamically managed and reused across different parts of the UI.

        This method prefixes the text block's content with a shared prefix and the module of the provided class to ensure uniqueness and consistency. It then adds the text block to the registry of form fields associated with the class, making it available for instantiation and rendering in the UI.

        Args:
            cls (type): The class with which this text block is to be registered.

        Returns:
            type: The class passed as an argument, allowing for method chaining or further modifications.
        """
        class_name = cls.__name__

        if self.package == "" and hasattr(cls, "_package"):
            self.package = getattr(cls, "_package", "")

        if not self.package.startswith("."):
            self.package = f".{self.package}"

        # Use prefix_text to ensure that content is prefixed if necessary, similar to how labels and helper texts are handled.
        self.content = self.prefix_text(self.content, cls)

        if class_name not in self.registry_class.cls_form_fields:
            self.registry_class.cls_form_fields[class_name] = []

        # Adding the text block to the registry with its content.
        self.registry_class.cls_form_fields[class_name].append(
            {
                "name": self.name,
                "content": self.content,
                "type": self.type,
                "visibility_conditions": self.visibility_conditions,
            }
        )
        return cls


# `reg_dicts` is a global list used to store information about registries during the metaclass creation process.
# Each item in the list is a tuple containing the name of the class, the registry dictionary associated with that class,
# and the unique identifier (ID) of the registry dictionary. This list is primarily used for debugging and introspection
# purposes, allowing developers to track the creation and registration of classes within the dynamic registry system.
reg_dicts: list[tuple[str, dict, int]] = []


class RegistryBase(type):
    """
    A metaclass for creating registries. This class is responsible for managing the creation and registration of classes
    that inherit from it, facilitating a dynamic registry system where subclasses can be automatically registered and
    retrieved. It supports inheritance, attribute binding from parent classes, and attribute unwrangling for private or
    protected attributes.

    Attributes:
        registries (dict[str, Registry]): A class-level dictionary that keeps track of all registries created.
        __calls_counter (dict): A dictionary to keep track of the number of times each class is instantiated.
    """

    registries: dict[str, Registry] = {}

    __calls_counter: dict[Any, Any] = {}

    @classmethod
    def getattr_from_all_parents(
        mcs, class_: Registry, attribute: str, values: list = None
    ) -> list:
        """
        Recursively collects values of a specified attribute from a class and all its parent classes in the hierarchy.

        Args:
            mcs (RegistryBase): The metaclass instance calling this method, typically a subclass of `RegistryBase`.
            class_ (Registry): The class from which to start collecting attribute values, moving up its parent classes.
            attribute (str): The name of the attribute for which values are being collected.
            values (list, optional): A list to which the collected values will be appended. If None, a new list is created.
                                     Defaults to None.

        Returns:
            list: A list of values collected for the specified attribute from the given class and its parents.
        """
        if values is None:
            values = []
        if hasattr(class_._parent, attribute):
            values.append(getattr(class_._parent, attribute))
        else:
            values.append(mcs.getattr_from_all_parents(attribute, values))
        return values

    @classmethod
    def get_first_defined_from_parents(
        mcs, class_: Registry, attribute: str, default=None
    ) -> Any:
        """
        Recursively searches for the first defined value of a given attribute in the class hierarchy, starting from the specified class and moving up its parent classes.

        Args:
            mcs (RegistryBase): The metaclass instance calling this method.
            class_ (Registry): The class from which to start the search for the attribute.
            attribute (str): The name of the attribute to search for.
            default (Any, optional): The default value to return if the attribute is not found in the class hierarchy. Defaults to None.

        Returns:
            Any: The first non-None value of the specified attribute found in the class hierarchy; if not found, returns the specified default value.
        """
        if class_ is None:
            return default

        val = getattr(class_._parent, attribute, None)
        if val:
            return val
        else:
            return mcs.get_first_defined_from_parents(
                class_._parent, attribute, default
            )

    # @staticmethod
    # def bind_to_base(base_class: Registry, child_class: Registry, attr_name: str) -> None:
    #     if base_class is not None and child_class is not None:
    #         setattr(child_class, attr_name, getattr(base_class, attr_name))

    @staticmethod
    def bind_to_base(
        base_class: Registry, child_class: Registry, attributes: list[str]
    ) -> None:
        """
        Binds specified attributes from a base class to a child class.

        This method is used to inherit attributes from a base class to its subclasses dynamically. It is particularly
        useful for attributes that are meant to be shared or overridden by subclasses.

        Args:
            base_class (Registry): The base class from which attributes are to be inherited.
            child_class (Registry): The child class to which attributes are to be bound.
            attributes (list[str]): A list of attribute names to be bound from the base class to the child class.
        """
        if base_class is not None and child_class is not None:
            for attr_name in attributes:
                setattr(child_class, attr_name, getattr(base_class, attr_name))

    @classmethod
    def rebind_wrangled_attributes(mcs, class_, attributes: list[str]) -> None:
        """
        Rebinds attributes that have been "wrangled" (i.e., name-mangled) to their original names.

        This method is useful for dealing with private or protected attributes that have been renamed by Python's
        name-mangling mechanism to prevent name clashes in subclasses.

        Args:
            class_ (Registry): The class whose attributes are to be rebound.
            attributes (list[str]): A list of attribute names to be rebound to their original names.
        """
        for attr_name in attributes:
            wrangled_name, unwrangled_name = mcs.unwrangle_name(class_, attr_name)
            setattr(class_, unwrangled_name, getattr(class_, wrangled_name))

    @staticmethod
    def unwrangle_name(class_, name: str) -> tuple[str, str]:
        """
        Converts a wrangled (name-mangled) attribute name back to its original form.

        Args:
            class_ (Registry): The class containing the wrangled attribute.
            name (str): The wrangled attribute name.

        Returns:
            tuple[str, str]: A tuple containing the wrangled name and the original (unwrangled) name.
        """
        wrangled_name = name
        unwrangled_name = ""
        if name.startswith("__"):
            wrangled_name = f"_{class_.__name__}{wrangled_name}"
            unwrangled_name = name[2:]

        elif wrangled_name.startswith("_"):
            unwrangled_name = wrangled_name[1:]

        return wrangled_name, unwrangled_name

    @classmethod
    def print_num_calls(cls) -> None:
        """
        Prints the number of times each class has been instantiated.

        This method is primarily used for debugging purposes, to track how many instances of each class have been created.
        """
        pprint(cls.__calls_counter)

    def __new__(mcs, name, bases, attrs, **kwargs) -> type:
        """
        Creates a new class instance. This method is automatically called when a new class is defined that inherits from
        RegistryBase or one of its subclasses.

        Args:
            name (str): The name of the class being created.
            bases (tuple): A tuple containing the base classes of the class being created.
            attrs (dict): A dictionary of attributes and methods defined in the class.
            **kwargs: Additional keyword arguments.

        Returns:
            type: The newly created class.
        """
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
            mcs.rebind_wrangled_attributes(
                new_class, attrs.get("attrs_to_unwrangle", [])
            )
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

        attrs_to_bind_to_base.extend(
            mcs.get_first_defined_from_parents(new_class, "attrs_to_bind_to_base")
        )
        attrs_to_unwrangle.extend(
            mcs.get_first_defined_from_parents(new_class, "attrs_to_unwrangle")
        )
        to_dict_attrs.extend(
            mcs.get_first_defined_from_parents(new_class, "to_dict_attrs", [])
        )

        new_class.attrs_to_bind_to_base = attrs_to_bind_to_base
        new_class.attrs_to_unwrangle = attrs_to_unwrangle
        new_class.to_dict_attrs = to_dict_attrs

        registration_base = None
        direct_base_name = ""

        p: Registry
        base_name_list = [
            p.base_name
            for p in parents
            if hasattr(p, "base_name") and p.base_name != ""
        ]
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
            if (
                name not in registration_base.registry_exclude
                and name not in mcs.registries
            ):
                new_class.register()

        reg_dict = getattr(new_class, f"_{name}__registry", None)
        reg_dicts.append([name, reg_dict, id(reg_dict)])

        if attrs.get("base_name", "") != "" and name not in mcs.registries:
            mcs.registries[name] = new_class

        return new_class


class Registry(metaclass=RegistryBase):
    """
    A base class for creating registries. This class, along with its metaclass `RegistryBase`, facilitates the creation
    of a dynamic registry system where subclasses can be automatically registered and retrieved. This is useful for
    scenarios where you need to maintain a list of subclasses that can be dynamically referenced by name or some other
    identifier.

    Attributes:
        base_name (str): The base name of the registry, used to differentiate between different types of registries.
        attrs_to_bind_to_base (list[str]): Attributes that should be inherited from the base class.
        attrs_to_unwrangle (list[str]): Attributes that have been name-mangled and need to be accessible in a more
                                        straightforward manner.
        _package (str): The package or module name where the base class is defined. This is used for namespacing purposes.
        _parent (Registry): A reference to the parent class in the registry hierarchy.
        to_dict_attrs (list[str]): Attributes that should be included when converting the class information to a dictionary.
        __registry (dict[str, TRegistryClass]): A private dictionary holding the registry of classes.
        __registry_exclude (list[str]): A list of class names to exclude from the registry.
        registry (dict[str, dict[str, TRegistryClass]]): A public-facing dictionary that provides convenient access to the
                                                         registered classes.
        registry_exclude (list[str]): A public-facing list of class names that are excluded from the registry.
        name (str): The name of the class, typically set dynamically upon registration.
        name_lower (str): A lowercase version of the class name, useful for case-insensitive comparisons.
        label (str): A human-readable label for the class, often used for UI display purposes.
        package (str): The package or module name that contains the class. This is used for namespacing and organization.
    """
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

    @classmethod
    def register(cls) -> None:
        """
        Registers the current class in the registry. This method sets various class attributes based on the class name
        and its position in the inheritance hierarchy, and then adds the class to the registry for later retrieval.

        This method is typically called automatically when a subclass is defined, thanks to the metaclass configuration.
        """
        # Set class attributes
        # cls.name = cls.__name__[:-len(base.__name__.split(".")[-1])]
        if cls.base_name in cls.__name__:
            cls.name = cls.__name__[: -len(cls.base_name)]
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
    def register_subclasses(cls, class_: type = None) -> None:
        """
        Recursively registers all subclasses of the current class. This method is useful for ensuring that all relevant
        subclasses are registered in the registry, especially when dealing with dynamic imports or modules that may not
        be imported upfront.

        Args:
            class_ (type, optional): The class to start the registration process from. If None, starts with the current class.
        """
        if class_ is None:
            class_ = cls
        for subclass in class_.__subclasses__():
            if subclass.__name__ in cls.__registry_exclude:
                cls.register_subclasses(subclass)
            elif cls.base_name in subclass.__name__:
                subclass.register()

    @classmethod
    def get_registry(cls) -> dict[str, TRegistryClass]:
        """
        Retrieves the registry dictionary for the current class. This dictionary contains all registered subclasses,
        allowing for dynamic lookup and instantiation.

        Returns:
            dict[str, TRegistryClass]: A dictionary mapping class names to class objects.

        Raises:
            ValueError: If no subclasses have been registered under the current base name.
        """
        registry = cls.__registry.get(cls.base_name)
        if registry is None:
            raise ValueError(f"No subclasses of {cls.base_name} have been registered.")
        return registry

    @classmethod
    def get_class_by_name(cls, name) -> TRegistryClass:
        """
        Retrieves a class from the registry by its name.

        Args:
            name (str): The name of the class to retrieve.

        Returns:
            TRegistryClass: The class object associated with the given name.
        """
        return cls.registry.get(cls.base_name, {}).get(name)

    @classmethod
    def get_class_by_value(cls, value) -> TRegistryClass | None:
        """
        Retrieves a class from the registry by its value attribute. This method is useful for cases where classes are
        referenced by a value other than their name, such as a lowercase version of the name.

        Args:
            value (str): The value associated with the class to retrieve.

        Returns:
            TRegistryClass | None: The class object associated with the given value, or None if no matching class is found.
        """
        for subclass in cls.registry.get(cls.base_name, {}).values():
            if subclass.name_lower == value:
                return subclass
        return None

    @classmethod
    def to_dict(cls) -> dict:
        """
        Converts the class attributes specified in `to_dict_attrs` to a dictionary. This is useful for serializing class
        information to a format that can be easily transmitted or stored.

        Returns:
            dict: A dictionary containing the class attributes specified in `to_dict_attrs`.
        """
        d = {attr: getattr(cls, attr) for attr in cls.to_dict_attrs}
        return d


class UIRegistry(Registry):
    """
    A subclass of Registry tailored for UI components, managing the registration and retrieval of UI-related classes.
    This class extends the base Registry functionality to include UI-specific attributes and methods, such as handling
    form fields and providing instructions for UI components.

    Attributes:
        base_name (str): The base name of the UI registry, used to differentiate it from other types of registries.
        attrs_to_bind_to_base (list[str]): Attributes that should be inherited from the base class.
        _parent (Registry): A reference to the parent class in the registry hierarchy.
        cls_form_fields (dict[str, list[dict[str, Any]]]): A dictionary mapping class names to lists of form field
            dictionaries. These form fields are used to dynamically generate UI forms.
        instructions (str): A string template for generating instruction text for the UI component.
        instructions_helper_url (str): A URL to a help page or document providing additional instructions.
        callback_url (str): The URL to which a user should be redirected after a certain action is completed in the UI.
        app_creation_url (str): The URL for creating new instances of the application or service.
        dds_app_creation_instructions (str): Specific instructions for creating an application or service within a
            particular domain or system.
        to_dict_attrs (list[str]): Attributes that will be included when converting the class information to a dictionary.
        fields (list[dict[str, Any]]): A list of dictionaries representing the fields of the UI component.
        form_fields (list[FormField | FormButton]): A list of FormField or FormButton instances representing the form
            fields to be used in the UI.

    Methods:
        register: Registers the current class in the UI registry and initializes class-specific attributes.
        get_form_fields_storage: Returns the storage dictionary for form fields associated with the class.
        get_fields: Retrieves the list of form fields associated with the class.
        get_all_form_fields: Collects and returns form fields from all registered UI classes.
    """
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

    to_dict_attrs: list[str] = [
        "label",
        "value",
        "instructions",
        "instructions_helper_url",
        "callback_url",
        "app_creation_url",
        "dds_app_creation_instructions",
        "fields",
    ]

    # Class attributes that need be redeclared or redefined in child classes
    # The following attributes need to be redeclared in child classes.
    # You can just copy and paste them into the child class body.
    fields: list[dict[str, Any]] = []

    # Form fields declarations go here
    # Child classes should redeclare the form_fields attribute and populate the list with instances of FormField.
    # These instances are used to create the form when adding a data provider in the UI.
    form_fields: list[FormField | FormButton] = []

    @classmethod
    def register(cls) -> None:
        """
        Registers the current class in the UI registry, initializes class-specific attributes based on the class name
        and package, and adds form fields to the class form fields storage. This method overrides the base class
        register method to include UI-specific registration logic.
        """
        super().register()

        package = f".{cls._package}" if cls._package != "" else ""
        cls.instructions = f"api{package}.{cls.name_lower}.instructions.text"
        cls.instructions_helper_url = (
            f"api{package}.{cls.name_lower}.instructions.helper_url"
        )

        cls.callback_url = f"dist/redirect/{cls.name_lower}"

        # Add class to the shared dictionaries to avoid errors in future methods
        if cls.__qualname__ not in cls.cls_form_fields:
            cls.cls_form_fields[cls.__qualname__] = []

        for field in cls.form_fields:
            field.register_field(cls)

        cls.fields = cls.get_fields()

    @classmethod
    def get_form_fields_storage(cls) -> dict[str, list[dict[str, Any]]]:
        """
        Returns the storage dictionary for form fields associated with the class. This dictionary maps class names to
        lists of form field dictionaries.

        Returns:
            dict[str, list[dict[str, Any]]]: The dictionary containing form fields for the class.
        """
        return cls._cls_form_fields

    @classmethod
    def get_fields(cls) -> list[FormField]:
        """
        Retrieves the list of form fields associated with the current class. This method allows for dynamic access to
        form fields defined in subclasses of the UIRegistry, facilitating the generation of UI forms based on the
        registered form fields.

        Returns:
            list[FormField]: A list of FormField instances associated with the class. If no form fields are registered
            for the class, an empty list is returned.
        """
        return cls.cls_form_fields.get(cls.__qualname__, [])

    @classmethod
    def get_all_form_fields(cls) -> list[dict[str, Any]]:
        """
        Retrieves a list of dictionaries representing all form fields from registered UIRegistry subclasses. Each dictionary
        contains information about the UI component, such as its label, value, instructions, helper URL, and fields. If a
        subclass has an authorization URL (indicative of OAuth2 integration), it is included under the 'oauth2' key.

        This method is useful for dynamically generating UI forms based on the registered UI components, allowing for
        a flexible and extensible UI architecture.

        Returns:
            list[dict[str, Any]]: A list of dictionaries, each representing a UI component with its associated form fields
            and other metadata. The structure of each dictionary is as follows:
            - 'label': The human-readable label of the UI component.
            - 'value': A value identifier for the UI component, typically a lowercase version of the class name.
            - 'instructions': Instruction text associated with the UI component.
            - 'instructions_helper_url': A URL pointing to additional help or documentation.
            - 'fields': A list of form fields associated with the UI component.
            - 'oauth2': (Optional) A dictionary containing 'authorize_url' if the UI component supports OAuth2 authorization.
        """
        registry = cls.get_registry()

        result = []

        subclass: UIRegistry
        for subclass in registry.values():
            item = {
                "label": subclass.label,
                "value": subclass.name_lower,
                "instructions": subclass.instructions,
                "instructions_helper_url": subclass.instructions_helper_url,
                "fields": subclass.get_fields(),
            }

            if hasattr(subclass, "get_authorize_url"):
                item["oauth2"] = {"authorize_url": subclass.get_authorize_url()}

            result.append(item)

        return result


class OAuthBase:
    """
    Base class for handling OAuth authentication flows.

    This class provides a framework for implementing OAuth authentication, including methods for initializing API and OAuth clients,
    generating authorization URLs, requesting access tokens, and revoking tokens. It is designed to be subclassed by specific
    implementations that provide the details for different OAuth providers.

    Attributes:
        token_url (str): URL to request the access token from the OAuth provider.
        revoke_url (str): URL to revoke the access token.
        base_authorize_url (str): Base URL for the authorization request.
        redirect_uri (str): URI to redirect to after authorization.
        _scopes (list[str]): List of scopes for the OAuth authorization.
        _categories_scopes (dict[str, str]): Mapping of scope categories to specific scopes.
        client_id (str): Client ID issued to the client by the OAuth provider.
        client_secret (str): Client secret issued to the client by the OAuth provider.
        access_token (str): Access token for accessing the OAuth provider's resources.
        refresh_token (str): Token used to refresh the access token.
        _authorize_url (str): Full URL used for the authorization request.
        _required_scopes (list[str]): List of scopes required for the application.
        api_client: Placeholder for an API client instance.
        oauth_client: Placeholder for an OAuth client instance.

    Methods to be implemented by subclasses:
        init_api_client(self, *args, **kwargs) -> None: Initializes the API client.
        init_oauth_client(self, *args, **kwargs) -> None: Initializes the OAuth client.
        get_authorize_url(self, builtin_variables: list[dict], custom_variables: list[dict] = None) -> str: Generates the authorization URL.
        get_client_id(self) -> str: Returns the client ID.
        request_token(self, code: str) -> dict[str, Any]: Requests an access token using the provided code.
        revoke_token(self, token: str) -> bool: Revokes the provided token.
    """
    # General class attributes
    # These attributes need to be overridden

    token_url: str = ""
    revoke_url: str = ""
    base_authorize_url: str = ""
    redirect_uri: str = ""

    _scopes: list[str] = []
    _categories_scopes: dict[str, str] = {}

    def __init__(
        self,
        client_id: str = None,
        client_secret: str = None,
        access_token: str = None,
        refresh_token: str = None,
        **kwargs,
    ) -> None:
        """
        Initializes an OAuthBase instance with the necessary credentials and tokens for OAuth authentication flow.

        This constructor sets up the initial state of the OAuthBase object, including client credentials, access tokens,
        and placeholders for API and OAuth clients. It is designed to be extended by subclasses that implement specific
        OAuth providers' authentication flows.

        Args:
            client_id (str, optional): The client ID issued to the client by the OAuth provider. Defaults to None.
            client_secret (str, optional): The client secret issued to the client by the OAuth provider. Defaults to None.
            access_token (str, optional): The access token for accessing the OAuth provider's resources. Defaults to None.
            refresh_token (str, optional): The token used to refresh the access token. Defaults to None.
            **kwargs: Arbitrary keyword arguments that can be used by subclasses to pass additional parameters.

        Attributes:
            client_id (str): Client ID for OAuth authentication.
            client_secret (str): Client secret for OAuth authentication.
            access_token (str): Access token for accessing protected resources.
            refresh_token (str): Refresh token for obtaining new access tokens.
            _authorize_url (str): The full URL used for the authorization request. Initially empty.
            _required_scopes (list[str]): List of scopes required for the application. Initially empty.
            api_client: Placeholder for an API client instance. Initially None.
            oauth_client: Placeholder for an OAuth client instance. Initially None.
        """
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
        """
        Initializes the API client used for making requests to the OAuth provider's resources.

        This method should be implemented by subclasses to set up the API client with the necessary configuration,
        such as base URLs, authentication headers, and any other required initialization parameters.

        Args:
            *args: Variable length argument list that can be used to pass non-keyworded, variable-length argument list.
            **kwargs: Arbitrary keyword arguments that can be used to pass additional parameters required for initializing the API client.

        Returns:
            None
        """
        ...

    @abstractmethod
    def init_oauth_client(self, *args, **kwargs) -> None:
        """
        Initializes the OAuth client used for handling OAuth authentication flows.

        This method should be implemented by subclasses to set up the OAuth client with the necessary configuration,
        such as client ID, client secret, authorization URLs, and any other required initialization parameters. The
        OAuth client is responsible for managing the OAuth flow, including generating authorization URLs, exchanging
        authorization codes for access tokens, and refreshing tokens as needed.

        Args:
            *args: Variable length argument list that can be used to pass non-keyworded, variable-length argument list.
            **kwargs: Arbitrary keyword arguments that can be used to pass additional parameters required for initializing the OAuth client.

        Returns:
            None: This method does not return a value but should set up the OAuth client as a side effect.
        """
        ...

    @abstractmethod
    def get_authorize_url(
        self, builtin_variables: list[dict], custom_variables: list[dict] = None
    ) -> str:
        """
        Generates the authorization URL that clients will use to initiate the OAuth authorization flow.

        This method constructs the URL required for the user to grant authorization to the application. It may include
        various parameters such as client ID, redirect URI, scope, state, and any other necessary OAuth parameters. The
        method should be implemented by subclasses to accommodate the specific requirements of different OAuth providers.

        Args:
            builtin_variables (list[dict]): A list of dictionaries containing built-in variables required for generating
                the authorization URL. These could include items like client ID, redirect URI, etc.
            custom_variables (list[dict], optional): A list of dictionaries containing custom variables that may be needed
                for generating the authorization URL. These are additional parameters specific to the OAuth provider or
                the authorization flow being implemented. Defaults to None.

        Returns:
            str: The fully constructed authorization URL to which the user should be redirected to begin the OAuth
            authorization process.

        Note:
            This is an abstract method and must be implemented by subclasses.
        """
        ...

    @abstractmethod
    def get_client_id(self) -> str:
        """
        Retrieves the client ID used for OAuth authentication.

        This method must be implemented by subclasses to return the client ID provided by the OAuth provider. The client ID
        is a public identifier for apps. Even though it’s public, it’s best that it isn’t shared widely, as it can sometimes
        be used to construct authorization URLs that may lead to phishing attacks.

        Returns:
            str: The client ID for the OAuth application.
        """
        ...

    @abstractmethod
    def request_token(self, code: str) -> dict[str, Any]:
        """
        Requests an access token from the OAuth provider using the provided authorization code.

        This method should be implemented by subclasses to handle the exchange of the authorization code for an access token.
        The exchange typically involves sending a request to the OAuth provider's token endpoint with the authorization code,
        client ID, client secret, and redirect URI. The response from the OAuth provider will include the access token and,
        optionally, a refresh token and other metadata.

        Args:
            code (str): The authorization code received from the OAuth provider as part of the authorization flow.

        Returns:
            dict[str, Any]: A dictionary containing the access token and optionally other tokens and metadata provided by the
            OAuth provider. The exact contents of this dictionary will depend on the specific OAuth provider and the scopes
            requested.

        Note:
            This is an abstract method and must be implemented by subclasses.
        """
        ...

    @abstractmethod
    def revoke_token(self, token: str) -> bool:
        """
        Revokes the given access or refresh token using the OAuth provider's revocation endpoint.

        This method should be implemented by subclasses to ensure that tokens can be properly revoked, enhancing security
        by preventing the use of old or compromised tokens. The implementation should make a request to the OAuth provider's
        token revocation endpoint, passing the token to be revoked along with any necessary authentication details (such as
        client ID and client secret).

        Args:
            token (str): The token (access or refresh) that needs to be revoked.

        Returns:
            bool: True if the token was successfully revoked, False otherwise. Implementations should return False in cases
            where the revocation process fails due to network issues, invalid responses, or if the OAuth provider indicates
            that the token could not be revoked.

        Note:
            This is an abstract method and must be implemented by subclasses.
        """
        ...


class JSONCompatible(ABC):
    @abstractmethod
    def to_json(self) -> dict[str, Union[int, float, str, bool, list, dict]]:
        ...

