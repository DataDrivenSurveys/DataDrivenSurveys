from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar, final, override

from ddsurveys.data_providers.data_categories import DataCategory
from ddsurveys.data_providers.variables import BuiltInVariable
from ddsurveys.variable_types import VariableDataType

if TYPE_CHECKING:
    from collections.abc import Sequence

    from ddsurveys.data_providers.spotify import SpotifyDataProvider


class Artist(DataCategory["SpotifyDataProvider"]):

    data_origin = [
        {
            "method": "artists",
            "endpoint": r"https://api.spotify.com/v1/artists/{id}",
            "documentation": "https://developer.spotify.com/documentation/web-api/reference/get-an-artist",
        }
    ]

    def fetch_data(self) -> list[dict[str, Any]]:
        pass

    builtin_variables = [
        BuiltInVariable.create_instances(
            name="top_artist",
            label="Most frequent artist",
            description="Most frequent artist in user's playlists.",
            test_value_placeholder="CRi",
            data_type=VariableDataType.TEXT,
            info=(
                "The name of the artist with most tracks in user's playlists."
            ),
            extractor_func=lambda self: self.top_artist,
            data_origin = [
                {
                    "method": "artists",
                    "endpoint": "https://api.spotify.com/v1/artists",
                    "documentation": "https://developer.spotify.com/documentation/web-api/reference/get-an-artist",
                }
            ]
        )
    ]