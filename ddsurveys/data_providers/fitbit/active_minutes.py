from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar, override

from ddsurveys.data_providers.data_categories import DataCategory
from ddsurveys.data_providers.variables import BuiltInVariable
from ddsurveys.variable_types import VariableDataType

if TYPE_CHECKING:
    from collections.abc import Sequence

    from ddsurveys.data_providers.fitbit import FB_DC_BuiltinVariables, FitbitDataProvider


class ActiveMinutes(DataCategory["FitbitDataProvider"]):
    """Variables related to active minutes."""

    @override
    def fetch_data(self) -> Sequence[dict[str, Any]]: ...

    builtin_variables: ClassVar[FB_DC_BuiltinVariables] = [
        BuiltInVariable["FitbitDataProvider"].create_instances(
            name="average_weekly_heart_zone_time_last_6_months",
            label="Average Weekly Heart Zone Minutes Last 6 Months",
            description="Average weekly heart zone minutes",
            data_type=VariableDataType.NUMBER,
            test_value_placeholder="120",
            unit="minutes",
            info="Average weekly heart zone minutes over the last 6 months.",
            extractor_func=lambda self: self.average_weekly_heart_zone_time_last_6_months,
            data_origin=[
                {
                    "method": "",
                    "endpoint": (
                        "https://api.fitbit.com/1/user/[user-id]/activities/active-zone-minutes/date/["
                        "start-date]/[end-date].json"
                    ),
                    "documentation": (
                        "https://dev.fitbit.com/build/reference/web-api/active-zone-minutes-timeseries"
                        "/get-azm-timeseries-by-interval/"
                    ),
                },
            ],
        ),
        BuiltInVariable["FitbitDataProvider"].create_instances(
            name="average_weekly_active_time_last_6_months",
            label="Average Weekly Active Minutes Only From A Tracker Last 6 Months",
            description="Average weekly active minutes only from a tracker",
            data_type=VariableDataType.NUMBER,
            test_value_placeholder="120",
            unit="minutes",
            info="Average weekly active minutes only from a tracker over the last 6 months.",
            extractor_func=lambda self: self.average_weekly_active_time_last_6_months,
            data_origin=[
                {
                    "method": "",
                    "endpoint": (
                        "https://api.fitbit.com/1/user/[user-id]/activities/[activityType]/date/["
                        "start-date]/[end-date].json"
                    ),
                    "documentation": (
                        "https://dev.fitbit.com/build/reference/web-api/activity-timeseries/get-activity"
                        "-timeseries-by-date-range/"
                    ),
                },
            ],
        ),
        BuiltInVariable["FitbitDataProvider"].create_instances(
            name="average_weekly_active_time_all_sources_last_6_months",
            label="Average Weekly Active Minutes From All sources Last 6 Months",
            description="Average weekly active minutes from all sources (tracker and manual entry)",
            data_type=VariableDataType.NUMBER,
            test_value_placeholder="120",
            unit="minutes",
            info=(
                "Average weekly active minutes from all sources (tracker and manual entry) "
                "over the last 6 months."
            ),
            extractor_func=lambda self: self.average_weekly_active_time_all_sources_last_6_months,
            data_origin=[
                {
                    "method": "",
                    "endpoint": (
                        "https://api.fitbit.com/1/user/[user-id]/activities/[activityType]/date/["
                        "start-date]/[end-date].json"
                    ),
                    "documentation": (
                        "https://dev.fitbit.com/build/reference/web-api/activity-timeseries/get-activity"
                        "-timeseries-by-date-range/"
                    ),
                },
            ],
        ),
        BuiltInVariable["FitbitDataProvider"].create_instances(
            name="average_weekly_activity_time_last_6_months",
            label="Average Weekly Activity Time Last 6 Months",
            description="Average weekly minutes spent doing activities",
            data_type=VariableDataType.NUMBER,
            test_value_placeholder="120",
            unit="minutes",
            info="Average weekly minutes spend doing activities over the last 6 months.",
            extractor_func=lambda self: self.average_weekly_activity_time_last_6_months,
            data_origin=[
                {
                    "method": "",
                    "endpoint": "https://api.fitbit.com /1/user/[user-id]/activities/list.json ",
                    "documentation": "https://dev.fitbit.com/build/reference/web-api/activity/get-activity-log-list/",
                },
            ],
        ),
    ]
