from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar, final, override

from ddsurveys.data_providers.data_categories import DataCategory
from ddsurveys.data_providers.variables import BuiltInVariable
from ddsurveys.variable_types import VariableDataType

if TYPE_CHECKING:
    from collections.abc import Sequence

    from ddsurveys.data_providers.spotify import SpotifyDataProvider


class Tracks(DataCategory["SpotifyDataProvider"]):

    data_origin = [
        {
            "method": "tracks",
            "endpoint": "https://api.spotify.com/v1/me/tracks",
            "documentation": "https://developer.spotify.com/documentation/web-api/reference/get-users-saved-tracks",
        }
    ]

    def fetch_data(self) -> list[dict[str, Any]]:
        pass

    builtin_variables = [
        BuiltInVariable.create_instances(
            name="tracks",
            label="Saved Tacks",
            description="The user's saved tracks.",
            test_value_placeholder="Runaway (Cri)",
            data_type=VariableDataType.TEXT,
            is_indexed_variable=True,
            index_start=1,
            index_end=5, # to keep things simple only access 5 tracks
            info=(
                "Tracks sorted by name and artist."
            ),
            extractor_func=lambda self, idx: self.tracks(idx),
            data_origin=[
                {
                    "method": "tracks",
                    "endpoint": "https://api.spotify.com/v1/me/tracks",
                    "documentation": "https://developer.spotify.com/documentation/web-api/reference/get-users-saved-tracks",
                },
            ],
        )
    ]