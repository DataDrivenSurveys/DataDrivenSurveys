from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar, final, override

from ddsurveys.data_providers.data_categories import DataCategory
from ddsurveys.data_providers.variables import BuiltInVariable
from ddsurveys.variable_types import VariableDataType

if TYPE_CHECKING:
    from collections.abc import Sequence

    from ddsurveys.data_providers.spotify import SpotifyDataProvider


class Devices(DataCategory["SpotifyDataProvider"]):

    data_origin = [
        {
            "method": "devices",
            "endpoint": "https://api.spotify.com/v1/me/player/devices",
            "documentation": "https://developer.spotify.com/documentation/web-api/reference/get-a-users-available-devices",
        }
    ]

    def fetch_data(self) -> list[dict[str, Any]]:
        pass

    builtin_variables = [
        BuiltInVariable.create_instances(
            name="devices",
            label="Available Devices",
            description="Devices associated with account.",
            test_value_placeholder="Computer (Chrome)",
            data_type=VariableDataType.TEXT,
            is_indexed_variable=True,
            index_start=1,
            index_end=2,
            info=(
                "Devices sorted by id."
            ),
            extractor_func=lambda self, idx: self.devices(idx),
            data_origin=[
                {
                    "method": "devices",
                    "endpoint": "https://api.spotify.com/v1/me/player/devices",
                    "documentation": "https://developer.spotify.com/documentation/web-api/reference/get-a-users-available-devices",
                },
            ],
        )
    ]