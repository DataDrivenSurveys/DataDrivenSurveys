from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar, final

from ddsurveys.data_providers.data_categories import DataCategory, DC_CVAttributes
from ddsurveys.data_providers.variables import BuiltInVariable, CVAttribute
from ddsurveys.variable_types import VariableDataType

if TYPE_CHECKING:
    from ddsurveys.data_providers.fitbit import FB_DC_BuiltinVariables, FitbitDataProvider
    from ddsurveys.data_providers.fitbit.api_response_dicts import ActivitiesListResponseDict


_most_frequent_activities: list[str] = [
    "Walk",
    "Sport",
    "Run",
    "Bike",
    "Aerobic Workout",
    "Weights",
    "Swim",
    "Mountain Biking",
    "Workout",
    "Interval Workout",
    "Elliptical",
]


def _factory_activity_last_whole_month(act: str) -> list[BuiltInVariable["FitbitDataProvider"]]:
    return BuiltInVariable["FitbitDataProvider"].create_instances(
        name=f"last_whole_month_{act.lower().replace(' ', '_')}",
        label=f"Number of {act} activities done over the last month.",
        description=f"Number of {act} activities done over the last month.",
        test_value_placeholder="1",
        data_type=VariableDataType.NUMBER,
        info=f"Number of {act} activities done over the last month.",
        is_indexed_variable=False,
        extractor_func=lambda self: self.activities_last_whole_month_counts.get(act, None),
        # extractor_func=lambda self: get_last_whole_month_counts(self, act),
        data_origin=[
            {
                "method": "",
                "endpoint": "https://api.fitbit.com /1/user/[user-id]/activities/list.json ",
                "documentation": "https://dev.fitbit.com/build/reference/web-api/activity/get-activity-log-list/",
            },
        ],
    )


@final
class Activities(DataCategory["FitbitDataProvider"]):
    """Variables related to activities."""

    data_origin: ClassVar = [
        {
            "method": "activities_frequent",
            "endpoint": "https://api.fitbit.com/1/user/[user-id]/activities/frequent.json",
            "documentation": "https://dev.fitbit.com/build/reference/web-api/activity/get-frequent-activities/",
        },
    ]

    def fetch_data(self) -> list[dict[str, Any]]:
        data: ActivitiesListResponseDict = self.data_provider.activity_logs
        if "activities" in data:
            return data["activities"]
        return []

    cv_attributes: ClassVar[DC_CVAttributes] = [
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

    builtin_variables: ClassVar[FB_DC_BuiltinVariables] = [
        BuiltInVariable["FitbitDataProvider"].create_instances(
            name="by_frequency",
            label="Activities by Frequency",
            description=(
                "Activities sorted from most frequent to least frequent. "
                "Index 1 is  the most frequent activity, index 2 is the second "
                "most frequent activity, and so on."
            ),
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
                },
            ],
        ),
        BuiltInVariable["FitbitDataProvider"].create_instances(
            name="has_activities_last_whole_month",
            label="Has activities during over the last month",
            description="Has activities during last month",
            data_type=VariableDataType.TEXT,
            test_value_placeholder="True",
            info=(
                "This will be 'True' if the the account has activities over the last month, "
                "otherwise 'False'."
            ),
            extractor_func=lambda self: self.has_activities_last_whole_month,
            data_origin=[
                {
                    "method": "",
                    "endpoint": "https://api.fitbit.com /1/user/[user-id]/activities/list.json ",
                    "documentation": "https://dev.fitbit.com/build/reference/web-api/activity/get-activity-log-list/",
                },
            ],
        ),
        BuiltInVariable["FitbitDataProvider"].create_instances(
            name="last_whole_month_total",
            label="Total number of activities done over the last month.",
            description="Total number of activities done over the last month.",
            data_type=VariableDataType.NUMBER,
            test_value_placeholder="10",
            info="Total number of activities done over the last month.",
            extractor_func=lambda self: sum(self.activities_last_whole_month_counts.values()),
            data_origin=[
                {
                    "method": "",
                    "endpoint": "https://api.fitbit.com /1/user/[user-id]/activities/list.json ",
                    "documentation": "https://dev.fitbit.com/build/reference/web-api/activity/get-activity-log-list/",
                },
            ],
        ),
        *[_factory_activity_last_whole_month(act) for act in _most_frequent_activities],
        BuiltInVariable["FitbitDataProvider"].create_instances(
            name="last_whole_month_walk_distance",
            label="Average distance walked during Walk activities over the last month.",
            description="Average distance walked during Walk activities over the last month.",
            test_value_placeholder="3",
            data_type=VariableDataType.NUMBER,
            info="Average distance walked during Walk activities done over the last month.",
            is_indexed_variable=False,
            extractor_func=lambda self: self.activities_last_whole_month_walk_distance,
            data_origin=data_origin,
        ),
        BuiltInVariable["FitbitDataProvider"].create_instances(
            name="last_whole_month_run_gps",
            label="Number of Run activities with a GPS trace done over the last whole month.",
            description="Number of Run activities with a GPS trace done over the last whole month.",
            test_value_placeholder="100",
            data_type=VariableDataType.NUMBER,
            info="Number of Run activities with a GPS trace done over the last whole month.",
            is_indexed_variable=False,
            extractor_func=lambda self: self.activities_last_whole_month_run_gps,
            data_origin=data_origin,
        ),
        BuiltInVariable["FitbitDataProvider"].create_instances(
            name="last_whole_month_workout_duration",
            label="Average duration of Workout activities done over the last whole month.",
            description="Average duration of Workout activities done over the last whole month.",
            test_value_placeholder="100",
            data_type=VariableDataType.NUMBER,
            info="Average duration of Workout activities done over the last whole month.",
            is_indexed_variable=False,
            extractor_func=lambda self: self.activities_last_whole_month_workout_duration,
            data_origin=data_origin,
        ),
    ]
