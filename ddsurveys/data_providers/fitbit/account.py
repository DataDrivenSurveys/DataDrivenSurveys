from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar, final, override

from ddsurveys.data_providers.data_categories import DataCategory
from ddsurveys.data_providers.variables import BuiltInVariable
from ddsurveys.variable_types import VariableDataType

if TYPE_CHECKING:
    from collections.abc import Sequence

    from ddsurveys.data_providers.fitbit import FitbitDataProvider


@final
class Account(DataCategory["FitbitDataProvider"]):
    """Variables related to a user's account."""

    @override
    def fetch_data(self) -> Sequence[dict[str, Any]]: ...

    builtin_variables: ClassVar[list[list[BuiltInVariable["FitbitDataProvider"]]]] = [
        BuiltInVariable["FitbitDataProvider"].create_instances(
            name="creation_date",
            label="Account Creation Date",
            description="Date of account creation.",
            data_type=VariableDataType.DATE,
            test_value_placeholder="2020-01-01",
            info=(
                "This will be the date that the respondent's Fitbit account was created. "
                "It will be in YYYY-MM-DD format."
            ),
            extractor_func=lambda self: self.user_profile["memberSince"],
            data_origin=[
                {
                    "method": "user_profile",
                    "endpoint": "https://api.fitbit.com/1/user/[user-id]/profile.json",
                    "documentation": "https://dev.fitbit.com/build/reference/web-api/user/get-profile/",
                },
            ],
        ),
        BuiltInVariable["FitbitDataProvider"].create_instances(
            name="account_created_at_least_6_months_ago",
            label="Account Created at Least 6 Months Ago",
            description="Account created at least 6 months ago.",
            data_type=VariableDataType.TEXT,
            test_value_placeholder="True",
            info=(
                "This will be 'True' if the account was created at least 6 months ago, "
                "otherwise 'False'."
            ),
            extractor_func=lambda self: self.account_created_at_least_6_months_ago,
            data_origin=[
                {
                    "method": "user_profile",
                    "endpoint": "https://api.fitbit.com/1/user/[user-id]/profile.json",
                    "documentation": "https://dev.fitbit.com/build/reference/web-api/user/get-profile/",
                },
            ],
        ),
    ]
