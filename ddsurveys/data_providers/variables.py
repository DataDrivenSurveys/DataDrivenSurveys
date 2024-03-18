#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

__all__ = [
    "Attribute",
    "CVFilter",
    "CustomVariableRow",
    "CustomVariable"
]

import random

from abc import ABC
from enum import Enum

from typing import Any, Mapping

from .data_categories import DataCategory

from ..variable_types import VariableDataType, Data

from ..get_logger import get_logger

logger = get_logger(__name__)


class Attribute(ABC):
    def __init__(self,
                 name: str,
                 label: str,
                 data_type: VariableDataType,
                 description: str,
                 info: str = None,
                 test_value: str = None,
                 test_value_placeholder: str = None,
                 unit: str = None,
                 data_origin: str = []):
        self.name = name
        self.label = label
        self.data_type = data_type
        self.description = description
        self.info = info
        self.test_value = test_value
        self.test_value_placeholder = test_value_placeholder
        self.unit = unit
        self.data_origin = data_origin

        if self.test_value is None:
            self.test_value = self.test_value_placeholder

    def to_dict(self) -> dict[str, Any]:
        return {
            "label": self.label,
            "description": self.description,
            "name": self.name,
            "data_type": self.data_type.value,
            "info": self.info,
            "test_value": self.test_value,
            "test_value_placeholder": self.test_value_placeholder,
            "unit": self.unit,
            "data_origin": self.data_origin
        }


class BuiltInVariable(Attribute):
    def __init__(self, name, label, description, data_type, unit=None, info="", test_value_placeholder=None,
                 is_indexed_variable=False, index=None, extractor_func=None, data_origin=None):
        super().__init__(
            name=name,
            label=label,
            data_type=data_type,
            description=description,
            info=info,
            test_value_placeholder=test_value_placeholder,
            unit=unit
        )
        # self.name = name
        # self.label = label
        # self.description = description
        # self.data_type = data_type
        # self.unit = unit
        # self.info = info
        # self.test_value_placeholder = test_value_placeholder
        self.is_indexed_variable = is_indexed_variable
        self.index = index
        self.extractor_func = extractor_func
        self.data_origin = data_origin

    @classmethod
    def create_instances(cls, name, label, description, data_type, unit=None, info="", test_value_placeholder=None,
                         is_indexed_variable=False, index_start=None, index_end=None, extractor_func=None, data_origin=None):
        instances = []

        if is_indexed_variable:
            if index_end is None or index_start is None:
                raise ValueError("Both index_start and index_end must be provided for indexed variables.")

            # Ensure index_end is greater than index_start
            if index_end < index_start:
                raise ValueError("index_end should be greater than index_start")

            for idx in range(index_start, index_end + 1):
                instance = cls(
                    name=name,
                    label=label,
                    description=description,
                    data_type=data_type,
                    unit=unit,
                    info=info,
                    test_value_placeholder=test_value_placeholder,
                    is_indexed_variable=is_indexed_variable,
                    index=idx,
                    extractor_func=extractor_func,
                    data_origin=data_origin
                )
                instances.append(instance)

            return instances
        else:
            single_instance = cls(
                name=name,
                label=label,
                description=description,
                data_type=data_type,
                unit=unit,
                info=info,
                test_value_placeholder=test_value_placeholder,
                is_indexed_variable=is_indexed_variable,
                extractor_func=extractor_func,
                data_origin=data_origin
            )
            instances.append(single_instance)

        # If not an indexed variable, just create a single instance
        return instances

    def to_dict(self) -> dict[str, Any]:

        #parent_class_name = self.extractor_func.__qualname__[:self.extractor_func.__qualname__.rfind(".")]
        #data_provider = parent_class_name[:-12].lower()


        dct = super().to_dict()
        dct.update({
            "is_indexed_variable": self.is_indexed_variable,
            "index": self.index,
        })
        return dct


class CVAttribute(Attribute):
    def __init__(self,
                 name: str,
                 label: str,
                 data_type: VariableDataType,
                 description: str,
                 info: str = None,
                 test_value: str = None,
                 test_value_placeholder: str = None,
                 unit: str = None,
                 attribute: str = None,
                 enabled: bool = None
                 ):
        super().__init__(name, label, data_type, description, info, test_value, test_value_placeholder, unit)
        self.attribute = attribute
        self.enabled = enabled

    def to_dict(self) -> dict[str, Any]:
        dct = super().to_dict()
        dct.update({
            "attribute": self.attribute,
            "enabled": self.enabled
        })
        return dct


class CVSelection:
    class SelectionOperator(Enum):
        RANDOM = "random"
        MAX = "max"
        MIN = "min"

    # Using the strategy pattern for cleaner code and scalability
    _strategies = {
        SelectionOperator.RANDOM: {
            "strategy": "_random_strategy",
            "operator": "random",
        },
        SelectionOperator.MAX: {
            "strategy": "_max_strategy",
            "operator": "max",
        },
        SelectionOperator.MIN: {
            "strategy": "_min_strategy",
            "operator": "min",
        }
    }

    def __init__(self, selection: dict[str, Any], attributes: list[CVAttribute]):
        operator = selection.get("operator", None)
        if operator is None:
            raise ValueError("Selection operator must be provided.")

        self.operator = self.SelectionOperator(selection.get("operator"))

        # The attribute is optional when the operator is random
        if self.operator != self.SelectionOperator.RANDOM and selection.get("attr", None) is None:
            raise ValueError("Selection attribute must be provided.")

        if selection.get("attr", None) is not None:
            self.attribute = next((attr for attr in attributes if attr.attribute == selection.get("attr")), None)

    def to_dict(self) -> dict[str, Any]:
        return {
            "operator": self._strategies.get(self.operator),
            # "attribute": self.attribute.to_dict() if self.attribute else None,
            "attribute": self.attribute.to_dict() if hasattr(self, "attribute") else None,
        }

    def __call__(self, rows: list['CustomVariableRow']) -> dict[str, Any]:
        if len(rows) == 0:
            return {}

        strategy = self._strategies.get(self.operator).get("strategy")

        if not strategy:
            logger.warning(f"Unknown selection operator: {self.operator}")
            return {}

        strategy_method = getattr(self, strategy, None)

        if not strategy_method:
            logger.warning(f"Strategy method {strategy} not found for operator: {self.operator}")
            return {}

        return strategy_method(rows)

    def _random_strategy(self, rows: list['CustomVariableRow']) -> dict[str, Any]:
        return random.choice(rows).data

    def _max_strategy(self, rows: list['CustomVariableRow']) -> dict[str, Any]:
        try:
            return max(rows, key=lambda x: x.data[self.attribute.attribute]).data
        except KeyError:
            logger.warning(f"Failed to perform max selection with attribute: {self.attribute.attribute}")
            return {}

    def _min_strategy(self, rows: list['CustomVariableRow']) -> dict[str, Any]:
        try:
            return min(rows, key=lambda x: x.data[self.attribute.attribute]).data
        except KeyError:
            logger.warning(f"Failed to perform min selection with attribute: {self.attribute.attribute}")
            return {}



class CVFilter:
    def __init__(self, attribute: CVAttribute, operator: str, value: str):
        if attribute is None or operator is None or value is None:
            raise ValueError("Attribute, operator, and value must be provided.")

        self.attribute = attribute

        data_type_class: Data = Data.determine_type(value)

        if not issubclass(data_type_class, Data):
            raise TypeError(f"Unsupported data type: {data_type_class}")

        self.operator = data_type_class.operators[operator]
        self.value = value

    def to_dict(self) -> dict[str, Any]:
        if self.attribute is None:
            return {
                "operator": self.operator.get("label"),
                "value": self.value
            }
        return {
            "attribute": self.attribute.to_dict(),
            "operator": self.operator.get("label"),
            "value": self.value
        }

    def __call__(self, custom_variable: CustomVariableRow):
        if self.attribute.attribute not in custom_variable.data:
            return False
        
        other_value = custom_variable.data[self.attribute.attribute]
        return self.operator.get('lambda')(other_value, self.value)

    def __repr__(self):
        return f"CVFilter(attr={self.attribute.attribute if hasattr(getattr(self, 'attribute', None), 'attribute') else None}, operator={self.operator.get('label')}, value={self.value})"

    def __str__(self):
        return f"{self.attribute.attribute} {self.operator.get('label')} {self.value}"


class CustomVariableRow:
    def __init__(self, variable_name: str, data_category: str, data: Mapping[str, Data], filters: list[CVFilter]):
        self.variable_name = variable_name
        self.data_category = data_category

        self.filters = filters

        self.data: Mapping[str, Data] = data

    def apply_filters(self) -> bool:
        return all(filter_(self) for filter_ in self.filters)
    
    def __repr__(self):
        return f"CustomVariableRow(variable_name={self.variable_name}, data_category={self.data_category}, data={self.data})"


class CustomVariable:

    def __init__(self, data_provider: "DataProvider" = None, custom_variable: dict[str, Any] = None, **kwargs):

        self.data_list = []

        self.data_provider = data_provider
        self.data_provider_name = custom_variable.get("data_provider", '')

        data_category_class = DataCategory.get_by_value(custom_variable["data_category"])
        self.data_category = data_category_class

        if self.data_provider:
            data_category_instance = data_category_class(data_provider=data_provider)
            data = data_category_instance.fetch_data()
            self.data_list = data or []

        self.variable_name = custom_variable["variable_name"]

        self.attributes = [
            CVAttribute(
                name=attr["name"],
                label=attr["label"],
                data_type=VariableDataType(attr["data_type"]),
                description=attr["description"],
                info=attr["info"],
                test_value_placeholder=attr["test_value_placeholder"],
                unit=attr["unit"],
                attribute=attr["attribute"],
                enabled=attr["enabled"]
            )
            for attr in custom_variable["cv_attributes"]
        ]

        self.filters = [
            CVFilter(
                attribute=next((attr for attr in self.attributes if attr.attribute == f["attr"]), None),
                operator=f["operator"],
                value=f["value"]
            )
            for f in custom_variable["filters"]
        ]

        self.selection = CVSelection(
            selection=custom_variable["selection"],
            attributes=self.attributes
        )

        self.selected_row = None

    def __repr__(self):
        return (f"{self.__class__.__name__}(data_provider={self.data_provider!r},")

    def to_dict(self) -> dict[str, Any]:
        return {
            "variable_name": self.variable_name,
            "qualified_name": self.get_qualified_name(),
            "data_category": {
                "label": self.data_category.label,
                "value": self.data_category.value,
                "data_origin": self.data_category.data_origin,
            },
            "attributes": [attr.to_dict() for attr in self.attributes],
            "filters": [filter_.to_dict() for filter_ in self.filters],
            "selection": self.selection.to_dict(),
        }

    def get_qualified_name(self) -> str:
        return f"dds.{self.data_provider_name}.custom.{self.data_category.value}.{self.variable_name}"

    def get_qualified_attributes(self) -> list[dict[str, Any]]:
        return [
            f"dds.{self.data_provider_name}.custom.{self.data_category.value}.{self.variable_name}.{attr.name}"
            for attr in self.attributes if attr.enabled
        ]

    @staticmethod
    def custom_variables_as_list(data: list[dict[str, Any]], result: dict[str, Any] = None) -> list[dict[str, Any]]:
        # TODO : used for syncing the custom variables into the survey platform, check if all these attributes are necessary
        # used to transform the custom variable data into the embedded data block format
        output_data = []

        for entry in data:
            for attribute in entry.get('cv_attributes', []):
                if not attribute.get('enabled'):
                    continue
                # Build the transformed dictionary
                transformed_entry = {
                    'category': entry.get('data_category'),
                    'data_provider': entry.get('data_provider'),
                    'data_type': attribute.get('data_type'),
                    'description': attribute.get('description'),
                    'info': attribute.get('info'),
                    'variable_name': attribute.get('variable_name'),
                    'qualified_name': f"dds.{entry.get('data_provider')}.custom.{entry.get('data_category')}.{entry.get('variable_name')}.{attribute.get('name')}",
                    'test_value_placeholder': attribute.get('test_value', ""),
                    'type': entry.get('type'),
                }

                if result:
                    transformed_entry['value'] = result.get(attribute.get('attribute'))

                # Append the transformed dictionary to the output list
                output_data.append(transformed_entry)

        return output_data

    def to_data(self) -> list[dict[str, Any]]:
        """
        Used to transform the custom variable data into the embedded data block format
        Each attribute of the custom variable is transformed into a separate variable for the survey platform
        """

        data_provider_name = self.data_provider.name_lower

        if not self.attributes or len(self.attributes) == 0:
            return {}

        custom_var_name = f"dds.{data_provider_name}.custom.{self.data_category.value}.{self.variable_name}"

        output_data = {
            f"{custom_var_name}.exists": bool(self.selected_row) and self.selected_row != {}
        }

        for attribute in self.attributes:
            if not attribute.enabled:
                continue

            # Append the transformed dictionary to the output
            attr_name = attribute.name
            attr_value = self.selected_row.get(attribute.attribute)

            if isinstance(attr_value, (int, float)):
                attr_exists = True
            elif isinstance(attr_value, str):
                attr_exists = len(attr_value) > 0
            else:
                attr_exists = False

            output_data.update({
                f"{custom_var_name}.{attr_name}": attr_value,
                f"{custom_var_name}.{attr_name}.exists": attr_exists
            })

        return output_data

    def construct_custom_variables(self) -> list[CustomVariableRow]:
        return [
            CustomVariableRow(
                variable_name=self.variable_name,
                data_category=self.data_category,
                data=item,
                filters=self.filters
            )
            for item in self.data_list
        ]

    @staticmethod
    def filter_custom_variables(custom_vars: list[CustomVariableRow]) -> list[CustomVariableRow]:
        return [custom_var for custom_var in custom_vars if custom_var.apply_filters()]

    def apply_selection(self, filtered_vars: list[CustomVariableRow]) -> dict[str, Any]:
        # Create a CVSelection instance based on the current selection.
        if len(filtered_vars) == 0:
            return {}
        # Use the CVSelection instance to select the desired row(s).
        return self.selection(filtered_vars)

    def calculate_custom_variables(self) -> dict[str, Any]:
        # this method implies that the selection always returns a single value
        custom_vars_rows = self.construct_custom_variables()
        filtered_vars = self.filter_custom_variables(custom_vars_rows)
        self.selected_row = self.apply_selection(filtered_vars)
        logger.debug(f"Selected Row", self.to_data())
        return self.to_data()
