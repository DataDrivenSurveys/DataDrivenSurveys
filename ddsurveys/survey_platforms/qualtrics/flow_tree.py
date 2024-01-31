#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2023-05-10 13:47

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
"""
from _typeshed import SupportsKeysAndGetItem
from copy import deepcopy
from typing import Any, ItemsView, Iterator, KeysView, MutableMapping, NoReturn, TypeVar, Union, ValuesView, overload

# Taken from typing module:
T = TypeVar('T')  # Any type.
KT = TypeVar('KT')  # Key type.
VT = TypeVar('VT')  # Value type.
T_co = TypeVar('T_co', covariant=True)  # Any type covariant containers.
V_co = TypeVar('V_co', covariant=True)  # Any type covariant containers.
VT_co = TypeVar('VT_co', covariant=True)  # Value type covariant containers.


class Flow(MutableMapping):
    def __init__(self, flow: Union[dict, "Flow"] = None):
        if isinstance(flow, dict):
            self._data = flow
        elif isinstance(flow, Flow):
            self._data = flow.to_dict()
        else:
            self._data = {"FlowID": "FL_1", "Properties": {}, "Type": "Root", "Flow": []}
        self._flow_id: str = self._data["FlowID"]
        self._type: str = self._data["Type"]
        self._subflows: list = None

    @property
    def flow_id(self):
        return self._flow_id

    @property
    def data(self):
        return deepcopy(self._data)

    def to_dict(self) -> dict:
        """
        Returns the dictionary format of the Flow. The resultant dictionary can be used as the payload for Qualtrics
        requests.

        Returns
        -------

        """
        d = self.data
        if "Flow" in d:
            subflows = list()
            for f in d["Flow"]:
                if isinstance(f, dict):
                    subflows.append(f)
                else:
                    subflows.append(f.to_dict())
            d["Flow"] = subflows
        return d

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
        return self.flow_id == other.flow_id

    def __ne__(self, other):
        return not self == other

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

    def popitem(self) -> tuple[KT, VT]:
        return self._data.popitem()

    def clear(self) -> None:
        self._data.clear()

    def update(self, __m: SupportsKeysAndGetItem[KT, VT], **kwargs: VT) -> None:
        self._data.update(__m, **kwargs)

    def setdefault(self, key: KT) -> T | None:
        return self._data.setdefault(key)
