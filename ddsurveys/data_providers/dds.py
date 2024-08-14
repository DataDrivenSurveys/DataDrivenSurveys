#!/usr/bin/env python3
"""Created on 2023-08-31 16:59.

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
@author: Stefan Teofanovic (stefan.teofanovic@heig-vd.ch)
"""

__all__ = ["DDSDataProvider"]

from typing import Any, ClassVar

from ddsurveys.data_providers.bases import FormTextBlock, FrontendDataProvider
from ddsurveys.data_providers.data_categories import DataCategory
from ddsurveys.data_providers.variables import BuiltInVariable
from ddsurveys.get_logger import get_logger
from ddsurveys.variable_types import VariableDataType

logger = get_logger(__name__)


class FrontendActivity(DataCategory):
    """Represents a category of data related to frontend user activities."""

    builtin_variables: ClassVar[list[BuiltInVariable]] = [
        BuiltInVariable.create_instances(
            name="open_transparency_table",
            label="Open Transparency Table",
            description="Indicates whether the respondent has accessed the transparency table.",
            data_type=VariableDataType.TEXT,
            test_value_placeholder="True",
            info="This variable reflects access to the transparency table, set to 'True' if accessed and 'False' "
                 "otherwise.",
            extractor_func=lambda variable, data: (
                bool(variable["qualified_name"] in data and data[variable["qualified_name"]]["count"] > 0)
            ),
            data_origin=[{"method": "", "endpoint": "", "documentation": "Monitored by the frontend application."}],
        )
    ]


class DDSDataProvider(FrontendDataProvider):
    # Class attributes go here
    app_required: bool = False

    fields: ClassVar[list[dict[str, Any]]] = {}

    # Form fields declarations go here
    form_fields: ClassVar[list[FormTextBlock]] = [FormTextBlock(name="information", content="information")]

    # DataCategory declarations go here
    data_categories = [FrontendActivity]
