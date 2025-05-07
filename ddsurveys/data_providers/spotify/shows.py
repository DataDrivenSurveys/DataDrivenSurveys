from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar, final, override

from ddsurveys.data_providers.data_categories import DataCategory
from ddsurveys.data_providers.variables import BuiltInVariable
from ddsurveys.variable_types import VariableDataType

if TYPE_CHECKING:
    from collections.abc import Sequence

    from ddsurveys.data_providers.spotify import SpotifyDataProvider

# shows is podcasts
class Shows(DataCategory["SpotifyDataProvider"]):

    data_origin = [
        {
            "method": "shows",
            "endpoint": r"https://api.spotify.com/v1/shows/{id}",
            "documentation": "https://developer.spotify.com/documentation/web-api/reference/get-a-show",
        }
    ]

    def fetch_data(self) -> list[dict[str, Any]]:
        pass

    builtin_variables = [
        BuiltInVariable.create_instances(
            name="shows_cnt",
            label="Number of shows",
            description="Number of shows (e.g. podcasts) user follows.",
            test_value_placeholder="3",
            data_type=VariableDataType.NUMBER,
            info=(
                "The number of shows the user follows."
            ),
            extractor_func=lambda self: self.shows_cnt,
            data_origin = [
                {
                    "method": "shows",
                    "endpoint": r"https://api.spotify.com/v1/shows/{id}",
                    "documentation": "https://developer.spotify.com/documentation/web-api/reference/get-a-show",
                }
            ]
        )
    ]