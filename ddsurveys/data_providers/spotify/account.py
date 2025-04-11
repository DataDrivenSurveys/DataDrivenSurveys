from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar, final, override

from ddsurveys.data_providers.data_categories import DataCategory
from ddsurveys.data_providers.variables import BuiltInVariable
from ddsurveys.variable_types import VariableDataType

if TYPE_CHECKING:
    from collections.abc import Sequence

    from ddsurveys.data_providers.spotify import SpotifyDataProvider


class Account(DataCategory["SpotifyDataProvider"]):

    data_origin = [
        {
            "method": "user_info",
            "endpoint": "https://api.spotify.com/v1/me/",
            "documentation": "https://developer.spotify.com/documentation/web-api/reference/get-current-users-profile",
        }
    ]

    def fetch_data(self) -> list[dict[str, Any]]:
        pass

    builtin_variables = [
        BuiltInVariable.create_instances(
            name="follower_count",
            label="Total Follower Count",
            description="Total follower count of the user.",
            test_value_placeholder="2",
            data_type=VariableDataType.NUMBER,
            info=(
                "This will be the number of users following this account."
            ),
            extractor_func=lambda self: self.total_follower_count,
            data_origin=[
                {
                    "method": "user_profile",
                    "endpoint": "https://api.spotify.com/v1/me/",
                    "documentation": "https://developer.spotify.com/documentation/web-api/reference/get-current-users-profile",
                },
            ],
        ),

        BuiltInVariable.create_instances(
            name="subscription_level",
            label="Subscription Level",
            description="The spotify subscription level of the user.",
            test_value_placeholder="Free",
            data_type=VariableDataType.TEXT,
            info=(
                "This will be the product subscription level of the user to Spotify."
            ),
            extractor_func=lambda self: self.subscription_level,
            data_origin=[
                {
                    "method": "user_profile",
                    "endpoint": "https://api.spotify.com/v1/me/",
                    "documentation": "https://developer.spotify.com/documentation/web-api/reference/get-current-users-profile",
                },
            ],
        ),
    ]