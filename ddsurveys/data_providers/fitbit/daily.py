from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar, final, override

from ddsurveys.data_providers.data_categories import DataCategory
from ddsurveys.data_providers.variables import BuiltInVariable
from ddsurveys.variable_types import VariableDataType

if TYPE_CHECKING:
    from collections.abc import Sequence

    from ddsurveys.data_providers.fitbit import FB_DC_BuiltinVariables, FitbitDataProvider


def _get_highest_steps_last_6_months_date(self: "FitbitDataProvider") -> str | None:
    dt, _ = self.highest_daily_steps_last_6_months_date_steps
    if dt is None:
        return None
    return dt.strftime("%Y-%m-%d")


@final
class Daily(DataCategory["FitbitDataProvider"]):
    """Variables related to daily statistics."""

    @override
    def fetch_data(self) -> Sequence[dict[str, Any]]: ...

    builtin_variables: ClassVar[FB_DC_BuiltinVariables] = [
        BuiltInVariable["FitbitDataProvider"].create_instances(
            name="highest_steps_last_6_months_steps",
            label="Highest Daily Step Count in Last 6 Months",
            description=(
                "Highest step count achieved on a single day within the last 6 months. "
                "This includes wearable activity tracker data only."
            ),
            data_type=VariableDataType.NUMBER,
            test_value_placeholder="20000",
            unit="steps",
            info="Highest daily step count in last 6 months.",
            extractor_func=lambda self: self.highest_daily_steps_last_6_months_date_steps[1],
            data_origin=[
                {
                    "method": "",
                    "endpoint": (
                        "https://api.fitbit.com/1/user/[user-id]/activities/tracker/steps/date/[start-date]/["
                        "end-date].json"
                    ),
                    "documentation": (
                        "https://dev.fitbit.com/build/reference/web-api/activity-timeseries/get-activity"
                        "-timeseries-by-date-range/"
                    ),
                },
            ],
        ),
        BuiltInVariable["FitbitDataProvider"].create_instances(
            name="highest_steps_last_6_months_date",
            label="Date of Highest Daily Step Count in Last 6 Months",
            description=(
                "Date of step count achieved on a single day within the last 6 months. "
                "This includes wearable activity tracker data only."
            ),
            data_type=VariableDataType.DATE,
            test_value_placeholder="2020-01-01",
            unit="date",
            info="Date of highest daily step count in last 6 months.",
            extractor_func=_get_highest_steps_last_6_months_date,
            data_origin=[
                {
                    "method": "",
                    "endpoint": (
                        "https://api.fitbit.com/1/user/[user-id]/activities/tracker/steps/date/[start-date]/["
                        "end-date].json"
                    ),
                    "documentation": (
                        "https://dev.fitbit.com/build/reference/web-api/activity-timeseries/get-activity"
                        "-timeseries-by-date-range/"
                    ),
                },
            ],
        ),
    ]
