from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar, final, override

from ddsurveys.data_providers.data_categories import DataCategory
from ddsurveys.data_providers.variables import BuiltInVariable
from ddsurveys.variable_types import VariableDataType

if TYPE_CHECKING:
    from collections.abc import Sequence

    from ddsurveys.data_providers.spotify import SpotifyDataProvider

# audiobooks are saved in episodes
class Episode(DataCategory["SpotifyDataProvider"]):

    data_origin = [
        {
            "method": "episode",
            "endpoint": r"https://api.spotify.com/v1/audiobooks/{id}",
            "documentation": "https://developer.spotify.com/documentation/web-api/reference/get-an-audiobook",
        }
    ]

    def fetch_data(self) -> list[dict[str, Any]]:
        pass

    builtin_variables = [
        BuiltInVariable.create_instances(
            name="episode_cnt",
            label="Number of episodes",
            description="Number of epsiodes.",
            test_value_placeholder="2",
            data_type=VariableDataType.NUMBER,
            info=(
                "The number of episodes saved in user's account."
            ),
            extractor_func=lambda self: self.episode_cnt,
            data_origin = [
                {
                    "method": "episode",
                    "endpoint": r"https://api.spotify.com/v1/episodes/{id}",
                    "documentation": "https://developer.spotify.com/documentation/web-api/reference/get-an-episode",
                }
            ]
        )
    ]