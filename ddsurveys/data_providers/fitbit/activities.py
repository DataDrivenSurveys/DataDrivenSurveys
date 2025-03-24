from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar

from ddsurveys.data_providers.data_categories import DataCategory
from ddsurveys.data_providers.variables import BuiltInVariable, CVAttribute
from ddsurveys.variable_types import VariableDataType

if TYPE_CHECKING:
    from ddsurveys.data_providers.fitbit import FitbitDataProvider
    from ddsurveys.data_providers.fitbit.api_response_dicts import ActivitiesListResponseDict


class Activities(DataCategory["FitbitDataProvider"]):
    data_origin: ClassVar = [
        {
            "method": "activities_frequent",
            "endpoint": "https://api.fitbit.com/1/user/[user-id]/activities/frequent.json",
            "documentation": "https://dev.fitbit.com/build/reference/web-api/activity/get-frequent-activities/",
        }
    ]

    def fetch_data(self) -> list[dict[str, Any]]:
        data: ActivitiesListResponseDict = self.data_provider.activity_logs
        if "activities" in data:
            return data["activities"]
        return []

    cv_attributes: ClassVar = [
        CVAttribute(
            name="duration",
            label="Activity Duration",
            description="The duration of the activity in seconds.",
            attribute="duration",
            data_type=VariableDataType.NUMBER,
            test_value_placeholder="100",
            info="The duration of the activity in seconds",
            unit="seconds",
        ),
        CVAttribute(
            name="calories",
            label="Calories Burned",
            description="The number of calories burned during the activity in kcal.",
            attribute="calories",
            data_type=VariableDataType.NUMBER,
            test_value_placeholder="100",
            info="The number of calories burned during the activity",
            unit="kcal",
        ),
        CVAttribute(
            label="Date",
            description="The date of the activity.",
            attribute="originalStartTime",
            name="date",
            data_type=VariableDataType.DATE,
            test_value_placeholder="2023-01-10T12:00:00.000+02:00",
            info="The date of the activity",
        ),
        CVAttribute(
            label="Distance",
            name="distance",
            description="The distance traveled during the activity in meters.",
            attribute="distance",
            data_type=VariableDataType.NUMBER,
            test_value_placeholder="100",
            info="The distance traveled during the activity",
            unit="meters",
        ),
        CVAttribute(
            label="Activity Type",
            description="The type of the activity.",
            attribute="activityName",
            name="type",
            data_type=VariableDataType.TEXT,
            test_value_placeholder="Walk",
            info="The type of activity",
        ),
    ]

    builtin_variables: ClassVar = [
        BuiltInVariable.create_instances(
            name="by_frequency",
            label="Activities by Frequency",
            description="Activities sorted from most frequent to least frequent. Index 1 "
            "is  the most frequent activity, index 2 is the second most frequent activity, "
            "and so on.",
            test_value_placeholder="Walk",
            data_type=VariableDataType.TEXT,
            info="Activities sorted from most frequent to least frequent. Index 1 is  the most frequent activity, ",
            is_indexed_variable=True,
            index_start=1,
            index_end=5,
            extractor_func=lambda self, idx: self.activities_by_frequency(idx),
            data_origin=[
                {
                    "method": "activities_frequent",
                    "endpoint": "https://api.fitbit.com/1/user/[user-id]/activities/frequent.json",
                    "documentation": "https://dev.fitbit.com/build/reference/web-api/activity/get-frequent-activities/",
                }
            ],
        )
    ]
