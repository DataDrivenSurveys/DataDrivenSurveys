"""Created on 2023-05-10 13:47.

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
@author: Stefan Teofanovic (stefan.teofanovic@heig-vd.ch)
"""
from __future__ import annotations

from collections.abc import ItemsView, Iterator, KeysView, MutableMapping, ValuesView
from copy import deepcopy
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from _typeshed import SupportsKeysAndGetItem


class Flow(MutableMapping):
    def __init__(self, flow: dict | Flow | None = None) -> None:
        if isinstance(flow, dict):
            self._data = flow
        elif isinstance(flow, Flow):
            self._data = flow.to_dict()
        else:
            self._data = {
                "FlowID": "FL_1",
                "Properties": {},
                "Type": "Root",
                "Flow": [],
            }
        self._flow_id: str = self._data["FlowID"]
        self._type: str = self._data["Type"]
        self._subflows: list | None = None

    @property
    def flow_id(self):
        return self._flow_id

    @property
    def data(self):
        return deepcopy(self._data)

    def to_dict(self) -> dict:
        """Returns the dictionary format of the Flow.

        The resultant dictionary can be used as the payload for Qualtrics
        requests.
        """
        d = self.data
        if "Flow" in d:
            subflows = []
            for f in d["Flow"]:
                if isinstance(f, dict):
                    subflows.append(f)
                else:
                    subflows.append(f.to_dict())
            d["Flow"] = subflows
        return d

    def __setitem__(self, key: str, value: Any) -> None:
        if isinstance(value, dict):
            self._data[key] = EmbeddedData.from_dict(value)
        else:
            self._data[key] = value

    def __delitem__(self, key: str) -> None:
        del self._data[key]

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator[Any]:
        return iter(self._data)

    def __contains__(self, key: str) -> bool:
        return key in self._data

    def __eq__(self, other):
        return self.flow_id == other.flow_id

    def __ne__(self, other):
        return not self == other

    def keys(self) -> KeysView[str]:
        return self._data.keys()

    def items(self) -> ItemsView[str, Any]:
        return self._data.items()

    def values(self) -> ValuesView[Any]:
        return self._data.values()

    def get(self, key: str, default=None) -> Any | None:
        return self._data.get(key, default)

    def pop(self, key: str) -> Any:
        return self._data.pop(key)

    def popitem(self) -> tuple[str, Any]:
        return self._data.popitem()

    def clear(self) -> None:
        self._data.clear()

    def update(self, __m: SupportsKeysAndGetItem[str, Any], **kwargs: Any) -> None:
        self._data.update(__m, **kwargs)

    def setdefault(self, key: str) -> Any | None:
        return self._data.setdefault(key)
