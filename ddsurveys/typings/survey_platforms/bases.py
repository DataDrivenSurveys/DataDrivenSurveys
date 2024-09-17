"""Type annotations for the Survey Platforms.

Created on 2024-09-16 15:37

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
"""
from typing import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    from ddsurveys.survey_platforms.bases import FormButton, FormField, OAuthSurveyPlatform, SurveyPlatform

    TSurveyPlatformClass = type["SurveyPlatform"]
    TSurveyPlatform = TypeVar("TSurveyPlatform", bound=SurveyPlatform)

    TOAuthSurveyPlatformClass = type["OAuthSurveyPlatform"]
    TOAuthSurveyPlatform = TypeVar("TOAuthSurveyPlatform", bound=OAuthSurveyPlatform)

    TSurveyPlatformFormFieldClass = type["FormField"]
    TSurveyPlatformFormField = TypeVar("TSurveyPlatformFormField", bound=FormField)

    TSurveyPlatformFormButtonClass = type["FormButton"]
    TSurveyPlatformFormButton = TypeVar("TSurveyPlatformFormButton", bound=FormButton)

    __all__ = [
        "TSurveyPlatformClass",
        "TSurveyPlatform",
        "TOAuthSurveyPlatformClass",
        "TOAuthSurveyPlatform",
        "TSurveyPlatformFormFieldClass",
        "TSurveyPlatformFormField",
        "TSurveyPlatformFormButtonClass",
        "TSurveyPlatformFormButton",
    ]
