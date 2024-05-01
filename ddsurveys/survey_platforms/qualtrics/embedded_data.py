#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2023-05-02 16:33

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
@author: Stefan Teofanovic (stefan.teofanovic@heig-vd.ch)
"""
from collections import OrderedDict
from collections.abc import MutableMapping
from copy import deepcopy
from typing import ItemsView, Iterator, KeysView, Mapping, TypeVar, Union, ValuesView, overload

# Taken from typing module:
T = TypeVar("T")  # Any type.
KT = TypeVar("KT")  # Key type.
VT = TypeVar("VT")  # Value type.
T_co = TypeVar("T_co", covariant=True)  # Any type covariant containers.
V_co = TypeVar("V_co", covariant=True)  # Any type covariant containers.
VT_co = TypeVar("VT_co", covariant=True)  # Value type covariant containers.

TEmbeddedData = TypeVar("TEmbeddedData", bound="EmbeddedData")
TEmbeddedDataLike = Union[Mapping[KT, VT], TEmbeddedData]

TEmbeddedDataBlock = TypeVar("TEmbeddedDataBlock", bound="EmbeddedDataBlock")
TEmbeddedDataBlockLike = Union[
    dict[str, TEmbeddedDataLike], dict[str, dict], TEmbeddedDataBlock
]


class EmbeddedData:
    """
    Class used to easily create and manipulate single EmbeddedData variables.
    """

    __slots__ = [
        "variable_name",
        "data_source_type",
        "variable_type",
        "analyze_text",
        "value",
        "data_visibility",
    ]

    field_type = {
        "Description": "str",  # Description to be shown to users in Qualtrics
        "Type": "str",
        "Field": "str",  # The name of the variable goes here, e.g., fitbit.steps.average
        "VariableType": "str",
        "DataVisibility": {"Private": "bool", "Hidden": "bool"},
        "AnalyzeText": "bool",
        "Value": "string",
    }

    allowed_values = {
        "Type": ["Recipient", "Custom", "EmbeddedData"],
        "VariableType": [
            "Nominal",
            "MultiValueNominal",
            "Ordinal",
            "Scale",
            "String",
            "Date",
            "FilterOnly",
            "Filter Only",
        ],
    }

    _qualtrics_to_attributes_map = {
        "Description": "variable_name",
        "Field": "variable_name",
        "Type": "data_source_type",
        "VariableType": "variable_type",
        "DataVisibility": "data_visibility",
        "AnalyzeText": "analyze_text",
        "Value": "value",
    }

    _attributes_to_qualtrics_map = {
        "analyze_text": "AnalyzeText",
        "data_source_type": "Type",
        "data_visibility": "DataVisibility",
        "variable_name": ["Description", "Field"],
        "value": "Value",
        "variable_type": "VariableType",
    }

    _values_to_qualtrics_types = {
        "Nominal": "Text Set",
        "MultiValueNominal": "Multi-Value Text Set",
        "Ordinal": "Number Set",
        "Scale": "Number",
        "String": "Text",
        "Date": "Date",
        "FilterOnly": "Filter Only",
    }

    """
    {
            "data_provider": self.data_provider,
            "category": self.category,
            "type": self.type,
            "name": self.name,
            "description": self.description,
            "data_type": self.data_type,
            "test_value_placeholder": self.test_value_placeholder,
            "info": self.info,
            "is_indexed_variable": self.is_indexed_variable,
            "index_start": self.index_start,
            "index_end": self.index_end,
            "value": self.value
        }
    """
    # TODO: finish implementing the translation of TVariable conforming dicts to EmbeddedData objects.
    _variable_to_attributes_map = {
        "name": "variable_name",
        "data_type": "variable_type",
    }

    _variable_types_to_qualtrics_types = {
        "Number": "Nominal",
        "Text": "String",
        "Date": "Date",
    }

    _qualtrics_types_to_values = {v: k for k, v in _values_to_qualtrics_types.items()}

    _to_custom_variable_map = {
        "Field": "name",
    }

    def __init__(
        self,
        variable_name: str,
        data_source_type: str,
        variable_type: str,
        data_visibility: dict = None,
        analyze_text: bool = False,
        value: str = "",
    ):
        """
        An object that wraps EmbeddedData flow blocks.

        Args:
            data_source_type:
                The type of embedded data.
                Allowed values are: 'Recipient', 'Custom', 'EmbeddedData'.
                'Recipient' corresponds to data taken from the participant distribution list.
                Corresponds to 'Type'.
            variable_type:
                Variable type.
                Allowed values are: 'Nominal', 'MultiValueNominal', 'Ordinal', 'Scale', 'String', 'Date', and 'FilterOnly'.
                Corresponds to 'VariableType'.
            data_visibility:
                Visibility of data.
                Corresponds to 'DataVisibility'.
            analyze_text:
                If true, analyze embedded data text.
                Corresponds to 'AnalyzeText'.
            value:
                An attribute associated with key.
                Corresponds to 'Value'.
        """
        self.variable_name: str = variable_name
        self.data_source_type: str = data_source_type
        self.variable_type: str = variable_type
        self.data_visibility: dict[str, bool]
        self.analyze_text: bool = analyze_text
        self.value: str = value

        if data_visibility is None:
            self.data_visibility = {"Private": False, "Hidden": False}
        elif isinstance(data_visibility, dict):
            if len(data_visibility) < 2:
                self.data_visibility = {"Private": False, "Hidden": False}
                self.data_visibility.update(data_visibility)
            else:
                self.data_visibility = data_visibility
        else:
            self.data_visibility = data_visibility

    @classmethod
    def from_variable(cls, variable) -> "EmbeddedData":
        """
        Factory method that create an EmbeddedData instance from a variable.
        """
        variable_name = variable["qualified_name"]
        data_source_type = "Recipient"
        variable_type = cls.translate_data_type(variable["data_type"])
        data_visibility = {"Private": False, "Hidden": False}
        analyze_text = False
        value = ""
        # value = variable.get("test_value", "")  # Assumes "test_value" is the correct mapping for value.

        return cls(
            variable_name,
            data_source_type,
            variable_type,
            data_visibility,
            analyze_text,
            value,
        )

    @classmethod
    def translate_data_type(cls, data_type):
        return cls._qualtrics_types_to_values.get(data_type, "String")

    @classmethod
    def embedded_data_to_custom_variable(cls, embedded_data_dict: dict) -> dict:
        out_dict = {"name": None, "__other__": {}}
        for k, v in embedded_data_dict.items():
            if k in cls._to_custom_variable_map:
                out_dict[cls._to_custom_variable_map[k]] = v
            else:
                out_dict["__other__"][k] = v
        return out_dict

    @property
    def qualtrics_to_attributes_map(self):
        return self.__class__._qualtrics_to_attributes_map

    def __getitem__(self, item):
        if item in self.__slots__:
            return self.__getattribute__(item)
        elif item in self.qualtrics_to_attributes_map:
            return self.__getattribute__(self.qualtrics_to_attributes_map[item])
        else:
            raise ValueError(
                f"Passed item '{item}' does not correspond to an {self.__class__.__name__} attribute or "
                f"Qualtrics defined EmbeddedData attribute."
            )

    def __eq__(self, other: Union[dict, "EmbeddedData"]) -> bool:
        if isinstance(other, EmbeddedData):
            return repr(self) == repr(other)
        elif isinstance(other, dict):
            return self.to_dict() == other
        else:
            return False

    @classmethod
    def from_dict(cls, dict_: dict) -> "EmbeddedData":
        new_dict = {cls._qualtrics_to_attributes_map[k]: v for k, v in dict_.items()}
        return cls(**new_dict)

    def to_dict(self, dict_type: str = "Qualtrics") -> dict:
        """

        Args:
            dict_type: A string describing the type of dictionary that should be returned. Allowed values are:
            'Qualtrics' and 'variable'.

        Returns:

        """
        if dict_type == "Qualtrics":
            out_dict = {k: self[k] for k in self.qualtrics_to_attributes_map}
            out_dict["Value"] = str(
                out_dict["Value"]
            )  # Convert value to string to avoid API errors.
            return out_dict
        elif dict_type == "variable":
            out_dict = {k: self[k] for k in self.qualtrics_to_attributes_map}
            return self.embedded_data_to_custom_variable(out_dict)
        else:
            raise ValueError(
                f"Passed dict_type '{dict_type}' is not allowed. Allowed values are: "
                f"'Qualtrics' and 'variable'."
            )

    @classmethod
    def get_dict_type(cls, dict_: dict) -> str:
        if all([k in cls._qualtrics_to_attributes_map for k in dict_]):
            return "Qualtrics"
        elif all([k in cls.__slots__ for k in dict_]):
            return "variable"
        else:
            raise ValueError(f"Passed dict_ is not a valid {cls.__name__} dictionary.")

    def __repr__(self):
        return (
            f"{self.__class__.__name__}('{self.variable_name}', '{self.data_source_type}', "
            f"'{self.variable_type}', {self.data_visibility}, {self.analyze_text}, '{self.value}')"
        )

    def __str__(self):
        return repr(self)


VariablesList = Union[list[dict[str, Union[str, dict]]], list[EmbeddedData]]


class EmbeddedDataBlock(MutableMapping):
    """
    Class used to easily create and manage EmbeddedData survey flow blocks.
    """

    @overload
    def __init__(self, ed_block: dict): ...

    @overload
    def __init__(self, flow_id: str = "FL_2", variables_list: VariablesList = None): ...

    def __init__(self, *args, **kwargs):
        # TODO: Use better variable names

        self._data: OrderedDict[str, EmbeddedData]
        self.flow_id: str

        if len(args) == 1 or kwargs.get("ed_block") is not None:
            block = kwargs.get("ed_block") or args[0]
            self.flow_id = block["FlowID"]
            self._data = OrderedDict(
                [(d["Field"], EmbeddedData.from_dict(d)) for d in block["EmbeddedData"]]
            )
        elif len(args) + len(kwargs) == 2:
            if len(args) == 2:
                self.flow_id = args[0]
                variables_list = args[1]
            elif len(kwargs) == 2:
                self.flow_id = kwargs["flow_id"]
                variables_list = kwargs["variables_list"]
            else:
                self.flow_id = args[0]
                variables_list = kwargs["variables_list"]

            if len(variables_list) == 0:
                self._data = OrderedDict()
            else:
                if isinstance(variables_list[0], EmbeddedData):
                    variables_list: list[EmbeddedData]
                    self._data = OrderedDict(
                        [(ed.variable_name, ed) for ed in variables_list]
                    )
                else:
                    self._data = OrderedDict(
                        [
                            (d["Field"], EmbeddedData.from_dict(d))
                            for d in variables_list
                        ]
                    )
        else:
            self.flow_id = "FL_2"
            self._data = OrderedDict()

    @classmethod
    def from_variables(cls, flow_id, variables):
        # Create a list of EmbeddedData objects from the variables
        embedded_data_list = [EmbeddedData.from_variable(var) for var in variables]

        # Use the list of EmbeddedData objects to create an EmbeddedDataBlock
        ed_block = cls(flow_id=flow_id, variables_list=embedded_data_list)

        return ed_block

    @property
    def data(self):
        return deepcopy(self._data)

    def to_dict(self, default_exists_value: bool = True) -> dict:
        """
        Returns the dictionary format of the block. This object can be inserted into a flow for uploading to Qualtrics.

        Returns
        -------

        """

        exists_variables = {
            f"{k}.exists": self.create_exists_variable(v, default_exists_value)
            for k, v in self._data.items()
            if not k.endswith(".exists") and f"{k}.exists" not in self._data
        }

        self._data.update(exists_variables)

        d = {
            "FlowID": self.flow_id,
            "Type": "EmbeddedData",
            "EmbeddedData": sorted(
                [ed.to_dict() for ed in self._data.values()],
                key=lambda x: x["Description"],
            ),
        }
        return d

    def __str__(self):
        return f"{self.__class__.__name__}({len(self._data)} variables)"

    def __repr__(self):
        return f"{self.__class__.__name__}({self.to_dict()!r})"

    def __setitem__(self, key: KT, value: VT) -> None:
        if isinstance(value, dict):
            self._data[key] = EmbeddedData.from_dict(value)
        else:
            self._data[key] = value

    def __delitem__(self, key: KT) -> None:
        del self._data[key]

    def __getitem__(self, key: KT) -> VT_co:
        return self._data[key]

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator[T_co]:
        return iter(self._data)

    def __contains__(self, key: KT) -> bool:
        return key in self._data

    def __eq__(self, other):
        if isinstance(other, EmbeddedDataBlock):
            return self._data == other.data
        else:
            return self._data == EmbeddedDataBlock(other).data

    def __ne__(self, other):
        return not self == other

    def append(self, item: Union[EmbeddedData, dict]):
        if isinstance(item, dict):
            item = EmbeddedData.from_dict(item)
        self[item.variable_name] = item

    def keys(self) -> KeysView[KT]:
        return self._data.keys()

    def items(self) -> ItemsView[KT, VT_co]:
        return self._data.items()

    def values(self) -> ValuesView[VT_co]:
        return self._data.values()

    def get(self, key: KT, default=None) -> VT_co | None:
        return self._data.get(key, default)

    def pop(self, key: KT) -> VT:
        return self._data.pop(key)

    def popitem(self, last=True) -> tuple[KT, VT]:
        return self._data.popitem(last)

    def clear(self) -> None:
        self._data.clear()

    def update(
        self,
        __m: Union[Mapping[KT, VT], EmbeddedData, "EmbeddedDataBlock"],
        **kwargs: VT,
    ) -> None:
        if isinstance(__m, dict):
            self._data.update(__m, **kwargs)
        elif isinstance(__m, EmbeddedData):
            self._data[__m.variable_name] = __m
        # elif isinstance(__m, EmbeddedDataBlock):
        elif __m.__class__.__name__ == "EmbeddedDataBlock":
            self._data.update(__m.data)

    def setdefault(self, key: KT) -> T | None:
        return self._data.setdefault(key)

    @staticmethod
    def create_exists_variable(
        ref_variable: TEmbeddedDataLike, value: bool
    ) -> EmbeddedData:
        ref_variable = deepcopy(ref_variable)

        if isinstance(ref_variable, EmbeddedData):
            ref_variable.variable_name = f"{ref_variable.variable_name}.exists"
            ref_variable.variable_type = "String"
            ref_variable.value = str(value)
            return ref_variable
        elif isinstance(ref_variable, dict):
            ref_variable.update(
                {
                    ref_variable["name"]: f"{ref_variable['name']}.exists",
                    "VariableType": "String",
                    "Value": str(value),
                }
            )
        return EmbeddedData.from_dict(ref_variable)

    def overwrite_custom_variables(self, new_variables: TEmbeddedDataBlockLike) -> None:
        """
        Overwrites the custom variables in the EmbeddedDataBlock with the new variables.
        Variables that are not namespaced with 'dds.' will not be overwritten.

        Args:
            new_variables: A dictionary or EmbeddedDataBlock containing the new variables that should be added to the EmbeddedDataBlock after removing the already existing variables.
            default_exists_value (bool): Default value for the implicit '.exists' variables if they have not been
            declared already.

        Returns:

        """
        current_variables: dict[str, EmbeddedData] = {
            k: v for k, v in self._data.items() if not k.startswith("dds.")
        }

        if isinstance(new_variables, dict):
            if isinstance(next(iter(new_variables.values())), EmbeddedDataBlock):
                current_variables.update(new_variables)
            else:
                current_variables.update(
                    {k: EmbeddedData.from_variable(v) for k, v in new_variables.items()}
                )
        elif isinstance(new_variables, EmbeddedDataBlock):
            current_variables.update(new_variables._data)
        else:
            raise ValueError(
                f"Passed item 'new_variables' does not correspond to a dict or EmbeddedDataBlock."
            )
        self._data = current_variables


if __name__ == "__main__":
    # ed = EmbeddedData()
    d = {
        "DataVisibility": {},
        "Description": "fitbit.act1.date",
        "Field": "fitbit.act1.date",
        "Type": "Recipient",
        "VariableType": "Date",
    }
    ed = EmbeddedData.from_dict(d)
    ed2 = ed.to_dict()

    variables = [
        {
            "id": 0,
            "category": "Account",
            "data_provider": "fitbit",
            "data_type": "Date",
            "description": "Date of account creation",
            "enabled": True,
            "info": "This will be the date that the respondent's Fitbit account was created. It will be in YYYY-MM-DD format.",
            "name": "dds.fitbit.account.creation_date",
            "test_value_placeholder": "2020-01-01",
            "type": "Builtin",
            "test_value": "dfghdfghdfh",
        },
        {
            "id": 1,
            "category": "Activities",
            "data_provider": "fitbit",
            "data_type": "Text",
            "description": "Most frequent activity name",
            "enabled": False,
            "info": "This will be the name of the most frequent activity that a user does. Otherwise it will be empty text. Tip: use display logic and question logic to decide if it's shown as an option.",
            "name": "dds.fitbit.activities_by_frequency[0]",
            "test_value_placeholder": "Walking",
            "type": "Builtin",
        },
        {
            "id": 2,
            "category": "Activities",
            "data_provider": "fitbit",
            "data_type": "Text",
            "description": "Second most frequent activity name",
            "enabled": False,
            "name": "dds.fitbit.activities_by_frequency[1]",
            "test_value_placeholder": "Running",
            "type": "Builtin",
        },
        {
            "id": 3,
            "category": "Steps",
            "data_provider": "fitbit",
            "data_type": "Number",
            "description": "Average lifetime steps",
            "enabled": True,
            "name": "dds.fitbit.steps.average",
            "test_value_placeholder": "10000",
            "type": "Builtin",
        },
    ]

    ed_block = EmbeddedDataBlock.from_variables("FL1", variables)

    from pprint import pprint

    pprint(ed_block.to_dict())
