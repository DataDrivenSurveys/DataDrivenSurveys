"""This module defines classes and methods for variables in the DDS system.

Classes:
    Attribute: An abstract base class representing a generic attribute.
    BuiltInVariable: A class representing built-in variables with additional properties.
    CVAttribute: A class representing custom variable attributes.
    SelectionOperator: An enumeration of selection operators.
    CVSelection: A class implementing the strategy pattern for custom variable
        selection.
    CVFilter: A class representing filters applied to custom variables.
    CustomVariableRow: A class representing a row of custom variable data.
    CustomVariable: A class representing a custom variable with associated data and
        methods.

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
@author: Stefan Teofanovic (stefan.teofanovic@heig-vd.ch).
"""

from __future__ import annotations

import random
from abc import ABC, abstractmethod
from enum import Enum
from typing import TYPE_CHECKING, Any, ClassVar, cast, override

from ddsurveys.data_providers.data_categories import DataCategory
from ddsurveys.get_logger import get_logger
from ddsurveys.typings.data_providers.variables import (
    BuiltinVariableDict,
    CVAttributeDict,
)
from ddsurveys.variable_types import Data, VariableDataType

if TYPE_CHECKING:
    from collections.abc import Callable

    from ddsurveys.data_providers.bases import DataProvider
    from ddsurveys.data_providers.data_categories import TDataCategoryClass
    from ddsurveys.typings.data_providers.variables import (
        AttributeDict,
        ComputedVariableDict,
        CustomVariableDict,
        CustomVariableUploadDict,
        CVFilterDict,
        CVSelectionDict,
        DataDict,
        DataOriginDict,
        SelectionDict,
        SelectionStrategyDict,
    )
    from ddsurveys.typings.models import CustomVariableDict as DBCustomVariableDict
    from ddsurveys.typings.variable_types import TVariableValue
    from ddsurveys.variable_types import OperatorDict, TDataClass


__all__ = [
    "Attribute",
    "CVFilter",
    "CustomVariableRow",
    "CustomVariable",
]

logger = get_logger(__name__)


class Attribute(ABC):
    @abstractmethod
    def __init__(
        self,
        name: str,
        label: str,
        data_type: VariableDataType,
        description: str,
        info: str = "",
        test_value: str = "",
        test_value_placeholder: str = "",
        unit: str = "",
        data_origin: list[DataOriginDict] | None = None,
    ) -> None:
        if data_origin is None:
            data_origin = []

        self.name: str = name
        self.label: str = label
        self.data_type: VariableDataType = data_type
        self.description: str = description
        self.info: str = info
        self.test_value = test_value
        self.test_value_placeholder: str = test_value_placeholder
        self.unit: str = unit
        self.data_origin: list[DataOriginDict] = data_origin

        if self.test_value != "":
            self.test_value: str = self.test_value_placeholder

    @override
    def __str__(self):
        return f"{self.__class__.__name__}: name={self.name}, label={self.label}, data_type={self.data_type}"

    @override
    def __repr__(self) -> str:
        attrs = ", ".join(f"{name}={value!r}" for name, value in self.to_dict().items())
        return f"{self.__class__.__name__}({attrs})"

    def to_dict(self) -> AttributeDict:
        """Converts the object to a dictionary.

        Converts the object to a dictionary for use in backend responses and database
        storage.

        Returns:
            AttributeDict: A dictionary containing the object's attributes.

        Example:
            # Converting and instance to a dictionary
            attr = Attribute("age", "Age", VariableDataType.INTEGER, "Age in years")
            attr.to_dict()
        """
        return {
            "name": self.name,
            "label": self.label,
            "data_type": self.data_type.value,
            "description": self.description,
            "info": self.info,
            "test_value": self.test_value,
            "test_value_placeholder": self.test_value_placeholder,
            "unit": self.unit,
            "data_origin": self.data_origin,
        }


class BuiltInVariable[DP: DataProvider](Attribute):
    def __init__(
        self,
        name: str,
        label: str,
        data_type: VariableDataType,
        description: str,
        info: str = "",
        test_value: str = "",
        test_value_placeholder: str = "",
        unit: str = "",
        data_origin: list[DataOriginDict] | None = None,
        *,
        is_indexed_variable: bool = False,
        index: int | None = None,
        extractor_func: Callable[[DP], TVariableValue]
        | Callable[[DP, int], TVariableValue]
        | None = None,
    ) -> None:
        if data_origin is None:
            data_origin = []

        super().__init__(
            name=name,
            label=label,
            data_type=data_type,
            description=description,
            info=info,
            test_value=test_value,
            test_value_placeholder=test_value_placeholder,
            unit=unit,
            data_origin=data_origin,
        )

        self.is_indexed_variable: bool = is_indexed_variable
        self.index: int | None = index
        self.extractor_func: (
            Callable[[DP], TVariableValue] | Callable[[DP, int], TVariableValue] | None
        ) = extractor_func

    @classmethod
    def create_instances(
        cls,
        *,
        name: str,
        label: str,
        description: str,
        data_type: VariableDataType,
        info: str = "",
        # test_value: str = "",
        test_value_placeholder: str = "",
        unit: str = "",
        data_origin: list[DataOriginDict] | None = None,
        is_indexed_variable: bool = False,
        index_start: int | None = None,
        index_end: int | None = None,
        extractor_func: Callable[[DP], TVariableValue]
        | Callable[[DP, int], TVariableValue]
        | None = None,
    ) -> list[BuiltInVariable[DP]]:
        if data_origin is None:
            data_origin = []

        instances: list[BuiltInVariable[DP]] = []

        if is_indexed_variable:
            if index_end is None or index_start is None:
                msg = "Both index_start and index_end must be provided for indexed variables."
                raise ValueError(msg)

            # Ensure index_end is greater than index_start
            if index_end < index_start:
                msg = "index_end should be greater than index_start"
                raise ValueError(msg)

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
                    data_origin=data_origin,
                )
                instances.append(instance)

            return instances

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
            data_origin=data_origin,
        )
        instances.append(single_instance)

        # If not an indexed variable, just create a single instance
        return instances

    @override
    def to_dict(self) -> BuiltinVariableDict:
        dct = super().to_dict()
        dct = cast(BuiltinVariableDict, dct)
        dct["is_indexed_variable"] = self.is_indexed_variable
        dct["index"] = self.index
        return dct


class CVAttribute(Attribute):
    def __init__(
        self,
        name: str,
        label: str,
        data_type: VariableDataType,
        description: str,
        info: str = "",
        test_value: str = "",
        test_value_placeholder: str = "",
        unit: str = "",
        *,
        attribute: str = "",
        enabled: bool = False,
    ) -> None:
        super().__init__(
            name=name,
            label=label,
            data_type=data_type,
            description=description,
            info=info,
            test_value=test_value,
            test_value_placeholder=test_value_placeholder,
            unit=unit,
        )
        self.attribute: str = attribute
        self.enabled: bool = enabled

    @override
    def to_dict(self) -> CVAttributeDict:
        dct = super().to_dict()
        dct = cast(CVAttributeDict, dct)
        dct.update({"attribute": self.attribute, "enabled": self.enabled})
        return dct


class SelectionOperator(Enum):
    RANDOM = "random"
    MAX = "max"
    MIN = "min"


class CVSelection:
    # Using the strategy pattern for cleaner code and scalability
    _strategies: ClassVar[dict[SelectionOperator, SelectionStrategyDict]] = {
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
        },
    }

    def __init__(self, selection: SelectionDict, attributes: list[CVAttribute]) -> None:
        operator: str = selection.get("operator", "")
        if operator == "":
            msg = "Selection operator must be provided."
            raise ValueError(msg)

        self.operator: SelectionOperator = SelectionOperator(selection.get("operator"))
        self.attribute: CVAttribute

        # The attribute is optional when the operator is random
        if self.operator == SelectionOperator.RANDOM:
            # Set empty CVAttribute as it won't be used for actual selection
            self.attribute = CVAttribute(
                name="",
                label="",
                data_type=VariableDataType.TEXT,
                description="",
                info="",
                test_value="",
                test_value_placeholder="",
            )
        else:
            selected_attribute: str = selection.get("attr", "")
            if selected_attribute != "":
                for attr in attributes:
                    if attr.attribute == selected_attribute:
                        self.attribute = attr
                        break

    def to_dict(self) -> CVSelectionDict:
        return {
            "operator": self._strategies[self.operator],
            "attribute": self.attribute.to_dict() if self.attribute.name != "" else None,
        }

    def __call__(self, rows: list[CustomVariableRow]) -> dict[str, Any]:
        if len(rows) == 0:
            return {}

        strategy: str = self._strategies[self.operator]["strategy"]

        if not strategy:
            logger.warning("Unknown selection operator: %s", self.operator)
            return {}

        strategy_method: Callable[[list[CustomVariableRow]], DataDict] | None = getattr(
            self, strategy, None
        )

        if strategy_method is None:
            logger.error("Strategy method %s not found for operator: %s", strategy, self.operator)
            return {}

        return strategy_method(rows)

    def _random_strategy(self, rows: list[CustomVariableRow]) -> DataDict:
        return random.choice(rows).data  # noqa: S311

    def _max_strategy(self, rows: list[CustomVariableRow]) -> DataDict:
        try:
            return max(rows, key=lambda row: row.data[self.attribute.attribute]).data  # type: ignore
        except (KeyError, TypeError) as e:
            logger.exception(
                "Failed to perform max selection with attribute: %s", self.attribute.attribute
            )
            if isinstance(e, KeyError):
                logger.exception("Key was not found in data: %s")
            else:
                logger.exception("Type error occurred when attempting to compare values: %s")
            return {}

    def _min_strategy(self, rows: list[CustomVariableRow]) -> DataDict:
        try:
            return min(rows, key=lambda row: row.data[self.attribute.attribute]).data  # type: ignore
        except (KeyError, TypeError) as e:
            logger.exception(
                "Failed to perform min selection with attribute: %s", self.attribute.attribute
            )
            if isinstance(e, KeyError):
                logger.exception("Key was not found in data: %s")
            else:
                logger.exception("Type error occurred when attempting to compare values: %s")
            return {}


class CVFilter:
    __slots__: tuple[str, ...] = ("attribute", "operator", "value")

    def __init__(
        self,
        attribute: CVAttribute | None,
        operator: str | None,
        value: str | None,
    ) -> None:
        if attribute is None or operator is None or value is None:
            msg = "Attribute, operator, and value must be provided."
            raise ValueError(msg)

        data_type_class: TDataClass | None = None
        data_type_class = Data.determine_type(value)

        if not issubclass(data_type_class, Data):
            msg = f"Unsupported data type: {data_type_class}"
            raise TypeError(msg)

        self.attribute: CVAttribute = attribute
        self.operator: OperatorDict = data_type_class.operators[operator]
        self.value: str = value

    def to_dict(self) -> CVFilterDict:
        # if self.attribute is None:
        #     return {"operator": self.operator.get("label"), "value": self.value}
        return {
            "attribute": self.attribute.to_dict(),
            "operator": self.operator.get("label"),
            "value": self.value,
        }

    def __call__(self, custom_variable_row: CustomVariableRow) -> bool:
        if self.attribute.attribute not in custom_variable_row.data:
            return False

        other_value: TVariableValue = custom_variable_row.data[self.attribute.attribute]
        return self.operator["func"](other_value, self.value)

    @override
    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__}: attribute={self.attribute.attribute}, "
            f"operator={self.operator.get('label')}, value={self.value}"
        )

    @override
    def __repr__(self) -> str:
        attrs = ", ".join(f"{key}={value!r}" for key, value in self.to_dict().items())
        return f"{self.__class__.__name__}({attrs})"


class CustomVariableRow:
    __slots__: tuple[str, ...] = (
        "variable_name",
        "data_category",
        "filters",
        "data",
    )

    def __init__(
        self,
        variable_name: str,
        data_category: TDataCategoryClass,
        data: DataDict,
        filters: list[CVFilter],
    ) -> None:
        self.variable_name: str = variable_name
        self.data_category: TDataCategoryClass = data_category

        self.filters: list[CVFilter] = filters

        self.data: DataDict = data

    def apply_filters(self) -> bool:
        return all(filter_(self) for filter_ in self.filters)

    @override
    def __repr__(self) -> str:
        return (
            f"CustomVariableRow(variable_name={self.variable_name!r}, data_category={self.data_category.__name__!r}, "
            f"data={self.data!r})"
        )


# TODO: make this class inherit from Attribute
class CustomVariable:
    def __init__(
        self,
        *,
        data_provider: DataProvider | None,
        custom_variable: CustomVariableDict,
    ) -> None:
        self.data_list: list[dict[str, Any]] = []

        self.data_provider = data_provider
        self.data_provider_name = custom_variable.get("data_provider", "")

        self.data_category: TDataCategoryClass = DataCategory.get_by_value(
            custom_variable["data_category"]
        )

        if self.data_provider is not None:
            data_category_instance: DataCategory = self.data_category(data_provider=data_provider)
            data: list[dict[str, Any]] | None = data_category_instance.fetch_data()
            if data is not None and len(data) > 0:
                self.data_list = data

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
                enabled=attr["enabled"],
            )
            for attr in custom_variable["cv_attributes"]
        ]

        attr_attribute: dict[str, CVAttribute] = {attr.attribute: attr for attr in self.attributes}

        self.filters: list[CVFilter] = [
            CVFilter(
                attribute=attr_attribute[filter_["attr"]],
                operator=filter_["operator"],
                value=filter_["value"],
            )
            for filter_ in custom_variable["filters"]
        ]

        self.selection: CVSelection = CVSelection(
            selection=custom_variable["selection"], attributes=self.attributes
        )

        self.selected_row = None

    @override
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(data_provider={self.data_provider!r},"

    def to_dict(self) -> CustomVariableDict:
        return {
            "variable_name": self.variable_name,
            "qualified_name": self.get_qualified_name(),
            "data_category": self.data_category.to_dict(),
            "attributes": [attr.to_dict() for attr in self.attributes],
            "filters": [filter_.to_dict() for filter_ in self.filters],
            "selection": self.selection.to_dict(),
        }

    def get_qualified_name(self) -> str:
        return (
            f"dds.{self.data_provider_name}.custom.{self.data_category.value}.{self.variable_name}"
        )

    # def get_qualified_attributes(self) -> list[dict[str, Any]]:
    #     return [
    #         f"dds.{self.data_provider_name}.custom.{self.data_category.value}.{self.variable_name}.{attr.name}"
    #         for attr in self.attributes
    #         if attr.enabled
    #     ]

    @staticmethod
    def custom_variables_as_list(
        data: list[DBCustomVariableDict], result: dict[str, Any] | None = None
    ) -> list[CustomVariableUploadDict]:
        # TODO : used for syncing the custom variables into the survey platform, check if all these attributes are
        #  necessary
        # used to transform the custom variable data into the embedded data block format
        if result is None:
            result = {}
        output_data: list[CustomVariableUploadDict] = []

        for entry in data:
            for attribute in entry.get("cv_attributes", []):
                if not attribute.get("enabled", False):
                    continue

                # Build the transformed dictionary
                transformed_entry: CustomVariableUploadDict = {
                    "category": entry.get("data_category"),
                    "data_provider": entry.get("data_provider"),
                    "data_type": attribute.get("data_type"),
                    "description": attribute.get("description"),
                    "info": attribute.get("info"),
                    "variable_name": attribute.get("variable_name"),
                    "qualified_name": f"dds.{entry['data_provider']}.custom.{entry['data_category']}."
                    f"{entry['variable_name']}.{attribute['name']}",
                    "test_value_placeholder": attribute.get("test_value", ""),
                    "type": entry["type"],
                }

                if len(result) > 0 and result.get(attribute["attribute"]) is not None:
                    transformed_entry["value"] = result.get(attribute["attribute"])

                # Append the transformed dictionary to the output list
                output_data.append(transformed_entry)

        return output_data

    def to_data(self) -> ComputedVariableDict:
        """Used to transform the custom variable data into the embedded data block format.

        Each attribute of the custom variable is transformed into a separate variable for the survey platform.
        """
        data_provider_name = self.data_provider.name_lower

        if not self.attributes or len(self.attributes) == 0:
            return {}

        custom_var_name = (
            f"dds.{data_provider_name}.custom.{self.data_category.value}.{self.variable_name}"
        )

        output_data: ComputedVariableDict = {
            f"{custom_var_name}.exists": bool(self.selected_row) and self.selected_row != {}
        }

        for attribute in self.attributes:
            if not attribute.enabled:
                continue

            # Append the transformed dictionary to the output
            attr_name = attribute.name
            attr_value = self.selected_row.get(attribute.attribute)

            if isinstance(attr_value, int | float):
                attr_exists = True
            elif isinstance(attr_value, str):
                attr_exists = len(attr_value) > 0
            else:
                attr_exists = False

            output_data[f"{custom_var_name}.{attr_name}"] = attr_value
            output_data[f"{custom_var_name}.{attr_name}.exists"] = attr_exists

        return output_data

    def construct_custom_variables(self) -> list[CustomVariableRow]:
        return [
            CustomVariableRow(
                variable_name=self.variable_name,
                data_category=self.data_category,
                data=item,
                filters=self.filters,
            )
            for item in self.data_list
        ]

    @staticmethod
    def filter_custom_variables(
        custom_vars: list[CustomVariableRow],
    ) -> list[CustomVariableRow]:
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
        return self.to_data()
        # logger.debug("Selected Row: %s", data)
