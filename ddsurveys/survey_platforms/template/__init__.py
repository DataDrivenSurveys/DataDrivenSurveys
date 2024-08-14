#!/usr/bin/env python3
"""Created on 2023-04-27 13:48.

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
@author: Stefan Teofanovic (stefan.teofanovic@heig-vd.ch)
"""
from __future__ import annotations

from typing import Any, ClassVar

from ddsurveys.get_logger import get_logger
from ddsurveys.survey_platforms.bases import FormButton, FormField, SurveyPlatform

# API related classes
# from .api import ...

__all__: list[str] = ["TemplateSurveyPlatform"]


logger = get_logger(__name__)


class TemplateSurveyPlatform(SurveyPlatform):

    # Form fields declarations go here
    form_fields: ClassVar[list[FormField | FormButton]] = [
        #...
    ]

    def __init__(
        self, survey_id: str = "", survey_platform_api_key: str = "", **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self.survey_id: str = survey_id
        self.survey_platform_api_key: str = survey_platform_api_key


    def fetch_survey_platform_info(self) -> tuple[int, str | None, dict[str, Any]]:
        ...

    def handle_project_creation(
        self, project_name: str, *, use_existing_survey: bool = False
    ) -> tuple[int, str, str, str | None, dict[str, Any]]:
        ...

    def handle_variable_sync(self, enabled_variables) -> tuple[int, str, str]:
        ...

    def handle_prepare_survey(
        self, project_short_id: str, survey_platform_fields: dict, embedded_data: dict
    ) -> tuple[bool, str | None]:
        ...

    def handle_export_survey_responses(
        self, project_short_id: str = ""
    ) -> tuple[bool, str, None]:
        ...

    def get_preview_link(
        self, survey_platform_fields: dict, enabled_variables: dict
    ) -> tuple[int, str, str, str]:
        ...
