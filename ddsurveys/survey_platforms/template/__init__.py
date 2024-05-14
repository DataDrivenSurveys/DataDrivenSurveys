#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2023-04-27 13:48

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
@author: Stefan Teofanovic (stefan.teofanovic@heig-vd.ch)
"""

__all__ = ["TemplateSurveyPlatform"]

from typing import Any, Optional
from urllib.parse import quote_plus

from ...get_logger import get_logger

from ..bases import FormButton, FormField, SurveyPlatform

# API related classes
# from .api import ...

logger = get_logger(__name__)


class TemplateSurveyPlatform(SurveyPlatform):

    # Form fields declarations go here
    form_fields: list[FormField | FormButton] = [
        #...
    ]

    def __init__(
        self, survey_id: str = None, survey_platform_api_key: str = None, **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self.survey_id = survey_id
        self.survey_platform_api_key = survey_platform_api_key

        ...

    def fetch_survey_platform_info(self) -> tuple[int, Optional[str], dict[str, Any]]:
        ...

    def handle_project_creation(
        self, project_name: str, use_existing_survey: bool = False
    ) -> tuple[int, str, str, str | None, dict[str, Any]]:
        ...

    def handle_variable_sync(self, enabled_variables) -> tuple[int, str, str]:
        ...

    def handle_prepare_survey(
        self, project_short_id: str, survey_platform_fields: dict, embedded_data: dict
    ) -> tuple[bool, Optional[str]]:
        ...

    def handle_export_survey_responses(
        self, project_short_id: str = None
    ) -> tuple[bool, str, None]:
        ...

    def get_preview_link(
        self, survey_platform_fields: dict, enabled_variables: dict
    ) -> tuple[int, str, str, str]:
        ...
