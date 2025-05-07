from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar, final, override

from ddsurveys.data_providers.data_categories import DataCategory
from ddsurveys.data_providers.variables import BuiltInVariable
from ddsurveys.variable_types import VariableDataType

if TYPE_CHECKING:
    from collections.abc import Sequence

    from ddsurveys.data_providers.spotify import SpotifyDataProvider


class Playlist(DataCategory["SpotifyDataProvider"]):

    data_origin = [
        {
            "method": "playlist_count",
            "endpoint": "https://api.spotify.com/v1/playlists",
            "documentation": "https://developer.spotify.com/documentation/web-api/reference/get-playlist",
        }
    ]

    def fetch_data(self) -> list[dict[str, Any]]:
        pass

    builtin_variables = [
        BuiltInVariable.create_instances(
            name="spotify_playlist_count",
            label="User's playlist count",
            description="The number of playlists the user has.",
            test_value_placeholder="2",
            data_type=VariableDataType.NUMBER,
            info="This shows the number of playlists the user has.",
            extractor_func=lambda self: self.playlist_count,
            data_origin=[
                {
                    "method": "playlists",
                    "endpoint": "https://api.fitbit.com/1/user/[user-id]/profile.json",
                    "documentation": "https://dev.fitbit.com/build/reference/web-api/user/get-profile/",
                },
            ],
        )
    ]