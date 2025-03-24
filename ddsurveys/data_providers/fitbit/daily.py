from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar

from ddsurveys.data_providers.data_categories import DataCategory
from ddsurveys.data_providers.variables import BuiltInVariable, CVAttribute
from ddsurveys.variable_types import VariableDataType

if TYPE_CHECKING:
    from ddsurveys.data_providers.fitbit import FitbitDataProvider
    from ddsurveys.data_providers.fitbit.api_response_dicts import ActivitiesListResponseDict


class Daily(DataCategory["FitbitDataProvider"]):
    def fetch_data(self) -> list[dict[str, Any]]:
        pass

    builtin_variables: ClassVar = [
        BuiltInVariable.create_instances(
            name="highest_steps_last_6_months_steps",
            label="Highest Daily Step Count in Last 6 Months",
            description="Highest step count achieved on a single day within the last 6 months. This includes wearable "
            "activity tracker data only.",
            data_type=VariableDataType.NUMBER,
            test_value_placeholder="20000",
            unit="steps",
            info="Highest daily step count in last 6 months.",
            extractor_func=lambda self: self.highest_daily_steps_last_6_months_date_steps[1],
            data_origin=[
                {
                    "method": "",
                    "endpoint": "https://api.fitbit.com/1/user/[user-id]/activities/tracker/steps/date/[start-date]/["
                    "end-date].json",
                    "documentation": "https://dev.fitbit.com/build/reference/web-api/activity-timeseries/get-activity"
                    "-timeseries-by-date-range/",
                }
            ],
        ),
        BuiltInVariable.create_instances(
            name="highest_steps_last_6_months_date",
            label="Date of Highest Daily Step Count in Last 6 Months",
            description="Date of step count achieved on a single day within the last 6 months. This includes wearable "
            "activity tracker data only.",
            data_type=VariableDataType.DATE,
            test_value_placeholder="2020-01-01",
            unit="date",
            info="Date of highest daily step count in last 6 months.",
            extractor_func=lambda self: self.highest_daily_steps_last_6_months_date_steps[
                0
            ].strftime("%Y-%m-%d"),
            data_origin=[
                {
                    "method": "",
                    "endpoint": "https://api.fitbit.com/1/user/[user-id]/activities/tracker/steps/date/[start-date]/["
                    "end-date].json",
                    "documentation": "https://dev.fitbit.com/build/reference/web-api/activity-timeseries/get-activity"
                    "-timeseries-by-date-range/",
                }
            ],
        ),
    ]
