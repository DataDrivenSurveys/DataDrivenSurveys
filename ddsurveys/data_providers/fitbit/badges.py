from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar

from ddsurveys.data_providers.data_categories import DataCategory
from ddsurveys.data_providers.variables import BuiltInVariable, CVAttribute
from ddsurveys.variable_types import VariableDataType

if TYPE_CHECKING:
    from ddsurveys.data_providers.fitbit import FitbitDataProvider
    from ddsurveys.data_providers.fitbit.api_response_dicts import ActivitiesListResponseDict


class Badges(DataCategory["FitbitDataProvider"]):
    data_origin: ClassVar = [
        {
            "method": "user_badges",
            "endpoint": "https://api.fitbit.com/1/user/[user-id]/badges.json",
            "documentation": "https://dev.fitbit.com/build/reference/web-api/user/get-badges/",
        }
    ]

    cv_attributes: ClassVar = [
        CVAttribute(
            label="Date",
            description="The date the badge was earned.",
            attribute="dateTime",
            name="date",
            data_type=VariableDataType.DATE,
            test_value_placeholder="2023-01-10T12:00:00.000",
            info="The date the badge was earned",
        ),
        CVAttribute(
            label="Badge Name",
            description="The name of the badge.",
            attribute="badgeName",
            name="name",
            data_type=VariableDataType.TEXT,
            test_value_placeholder="Walk",
            info="The name of the badge",
        ),
    ]

    builtin_variables: ClassVar = []

    def fetch_data(self) -> list[dict[str, Any]]:
        data = self.data_provider.user_badges
        return data or []
