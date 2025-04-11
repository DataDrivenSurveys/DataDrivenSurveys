from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar, final, override

from ddsurveys.data_providers.data_categories import DataCategory
from ddsurveys.data_providers.variables import BuiltInVariable
from ddsurveys.variable_types import VariableDataType

if TYPE_CHECKING:
    from collections.abc import Sequence

    from ddsurveys.data_providers.spotify import SpotifyDataProvider


class Genres(DataCategory["SpotifyDataProvider"]):

    data_origin = [
                {
                    "method": "genres",
                    "endpoint": "https://api.spotify.com/v1/artists",
                    "documentation": "https://developer.spotify.com/documentation/web-api/reference/get-an-artist",
                }
    ]

    def fetch_data(self) -> list[dict[str, Any]]:
        pass

    builtin_variables = [
        BuiltInVariable.create_instances(
            name="genres",
            label="Available Genres",
            description="Most frequent genres.",
            test_value_placeholder="Progressive House",
            data_type=VariableDataType.TEXT,
            is_indexed_variable=True,
            index_start=1,
            index_end=2,
            info=(
                "Genres sorted by frequency."
            ),
            extractor_func=lambda self, idx: self.genres(idx),
            data_origin=[
                {
                    "method": "genres",
                    "endpoint": "https://api.spotify.com/v1/artists",
                    "documentation": "https://developer.spotify.com/documentation/web-api/reference/get-an-artist",
                },
            ],
        )
    ]