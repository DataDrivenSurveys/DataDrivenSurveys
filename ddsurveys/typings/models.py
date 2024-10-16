#!/usr/bin/env python3
"""Created on 2024-07-24 13:07.

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal, NotRequired, TypedDict

if TYPE_CHECKING:
    from datetime import datetime

    from ddsurveys.typings.data_providers.variables import DataOriginDict, SelectionDict


class ResearcherDict(TypedDict):
    id: int
    firstname: str
    lastname: str
    email: str


class FieldsDict(TypedDict):
    client_id: str
    client_secret: str


class DataProviderDict(TypedDict):
    name: str
    data_provider_name: str
    data_provider_type: str


class FiltersDict(TypedDict):
    attr: str
    operator: str
    value: str


class CVAttributeDict(TypedDict):
    attribute: str
    category: str
    data_origin: list[DataOriginDict]
    data_type: str
    description: str
    enabled: bool
    info: str
    label: str
    name: str
    test_value: str
    test_value_placeholder: str
    unit: str


class DataOriginDict(TypedDict):
    documentation: str


class CollaborationDict(TypedDict):
    project_id: str
    researcher: ResearcherDict


class DataConnectionDict(TypedDict):
    project_id: str
    data_provider_name: str
    data_provider: DataProviderDict
    fields: FieldsDict


class DataConnectionPublicDict(TypedDict):
    data_provider: DataProviderDict | None


class CustomVariableDict(TypedDict):
    id: int
    cv_attributes: list[CVAttributeDict]
    data_category: str
    data_provider: str
    filters: list[FiltersDict]
    selection: SelectionDict
    type: str
    variable_name: str
    enabled: bool


class BuiltinVariableDict(TypedDict):
    id: int
    category: str
    data_origin: list[DataOriginDict]
    data_provider: str
    data_type: str
    description: str
    enabled: bool
    index: NotRequired[int]
    info: str
    is_indexed_variable: bool
    label: str
    name: str
    provider_type: str
    qualified_name: str
    test_value: str
    test_value_placeholder: str
    type: str
    unit: NotRequired[str]


class BuiltinVariableDict_(BuiltinVariableDict): ...


class IndexedVariableDict(TypedDict):
    id: int
    category: str
    data_origin: list[DataOriginDict]
    data_provider: str
    data_type: str
    description: str
    enabled: bool
    index: int
    info: str
    is_indexed_variable: Literal[True]
    label: str
    name: str
    provider_type: str
    qualified_name: str
    test_value: str
    test_value_placeholder: str
    type: str
    unit: NotRequired[str]


class SurveyPlatformFieldsDict(TypedDict):
    survey_id: str
    survey_platform_api_key: str
    survey_name: str
    base_url: str
    survey_status: str
    mailing_list_id: str
    directory_id: str


class DistributionDict(TypedDict):
    id: str
    url: str


class RespondentDict(TypedDict):
    id: str
    project_id: str
    distribution: DistributionDict


class ProjectDict(TypedDict):
    id: str
    short_id: str
    name: str
    survey_status: str
    survey_platform_name: str
    survey_platform_fields: SurveyPlatformFieldsDict
    last_modified: datetime
    creation_date: datetime
    last_synced: datetime
    variables: list[BuiltinVariableDict]
    custom_variables: list[CustomVariableDict]
    data_connections: list[DataConnectionDict]
    collaborations: list[CollaborationDict]
    respondents: list[RespondentDict]


class ProjectPublicDict(TypedDict):
    id: str
    short_id: str
    name: str
    survey_name: str
    data_connections: list[DataConnectionPublicDict]


class DataProviderAccessDict(TypedDict):
    respondent_id: str
    data_provider_name: str
    access_token: str
    refresh_token: str
