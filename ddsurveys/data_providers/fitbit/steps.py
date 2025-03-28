from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar, override

from ddsurveys.data_providers.data_categories import DataCategory
from ddsurveys.data_providers.variables import BuiltInVariable
from ddsurveys.variable_types import VariableDataType

if TYPE_CHECKING:
    from collections.abc import Sequence

    from ddsurveys.data_providers.fitbit import FB_DC_BuiltinVariables, FitbitDataProvider


class Steps(DataCategory["FitbitDataProvider"]):
    """Variables related to steps."""

    @override
    def fetch_data(self) -> Sequence[dict[str, Any]]: ...

    builtin_variables: ClassVar[FB_DC_BuiltinVariables] = [
        BuiltInVariable["FitbitDataProvider"].create_instances(
            name="average",
            label="Average Lifetime Steps",
            description=(
                "Average lifetime steps. "
                "If steps on only active days is not available, this will calculate "
                "the average step count using the account creation date and total lifetime steps."
            ),
            data_type=VariableDataType.NUMBER,
            test_value_placeholder="10000",
            unit="steps",
            info="Average lifetime steps. ",
            extractor_func=lambda self: self.average_lifetime_steps,
            data_origin=[
                {
                    "method": "activities_frequent",
                    "endpoint": "https://api.fitbit.com/1/user/[user-id]/profile.json",
                    "documentation": "https://dev.fitbit.com/build/reference/web-api/user/get-profile/",
                },
                {
                    "method": "lifetime_stats",
                    "endpoint": "https://api.fitbit.com/1/user/[user-id]/activities.json",
                    "documentation": "https://dev.fitbit.com/build/reference/web-api/activity/create-activity-log/",
                },
            ],
        ),
        BuiltInVariable["FitbitDataProvider"].create_instances(
            name="highest",
            label="Highest Lifetime Steps",
            description=(
                "Highest step count achieved on a single day. "
                "This includes wearable activity tracker data only."
            ),
            data_type=VariableDataType.NUMBER,
            test_value_placeholder="20000",
            unit="steps",
            info="Highest step count achieved on a single day. ",
            extractor_func=lambda self: self.highest_lifetime_steps,
            data_origin=[
                {
                    "method": "lifetime_stats",
                    "endpoint": "https://api.fitbit.com/1/user/[user-id]/activities.json",
                    "documentation": "https://dev.fitbit.com/build/reference/web-api/activity/create-activity-log/",
                },
            ],
        ),
    ]
