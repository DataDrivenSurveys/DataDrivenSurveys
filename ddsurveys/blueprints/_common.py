"""This module provides common functions for interacting with the database.

Examples:
    get_researcher(db, user):
        researcher, status = get_researcher(db, user)
        if status is not None:
            researcher: ResponseReturnValue
            # Case where the user could not be found
            return researcher, status
        researcher: Researcher

    get_project(db, user):
        project, status = get_project(db, user)
        if status is not None:
            project: ResponseReturnValue
            # Case where the user or project could not be found
            return project, status
        project: Project

    get_project_data_connection(db, user, data_provider_name):
        project_response, data_connection_int = get_project_data_connection(
            db=db,
            user=user,
            data_provider_name=data_provider_name,
        )
        if isinstance(data_connection_int, int):
            project_response: cast(Response, project_response)
            # Case where something could not be found in the database
            return project_response, data_connection_int
        project: Project = project_response
        data_connection: DataConnection = data_connection_int

Created on 2023-09-08 13:52

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
@author: Stefan Teofanovic (stefan.teofanovic@heig-vd.ch)
"""

from __future__ import annotations

from copy import deepcopy
from typing import TYPE_CHECKING, Literal, TypedDict, cast

from flask import Response as FlaskResponse
from flask import g

from ddsurveys.api_responses import APIResponses
from ddsurveys.get_logger import get_logger
from ddsurveys.models import Collaboration, DataConnection, Project, Researcher

if TYPE_CHECKING:
    import logging
    from collections.abc import Callable
    from http import HTTPStatus

    from sqlalchemy.orm import Query
    from sqlalchemy.orm.session import Session

    from ddsurveys.api_responses import APIResponseValue

__all__ = [
    "get_researcher",
    "get_project",
    "get_project_data_connection",
    "abbreviate_variable_name",
    "insert_exists_variables",
]

logger: logging.Logger = get_logger(__name__)


class JWTUserDict(TypedDict):
    id: int
    firstname: str
    lastname: str
    email: str


# TODO: move the replacement rules to the DP classes
type StrReplaceRule = tuple[str, str, int]


class TReplacementRules(TypedDict):
    common: list[StrReplaceRule]
    dds: list[StrReplaceRule]
    fitbit: list[StrReplaceRule]
    github: list[StrReplaceRule]
    googlecontacts: list[StrReplaceRule]
    instagram: list[StrReplaceRule]


REPLACEMENT_RULES: TReplacementRules = {
    "common": [
        (".builtin.", ".b.", -1),
        (".custom.", ".c.", -1),
        (".exists", ".e", -1),
        ("_with_", "_w_", -1),
        ("_biographies", "_bios", -1),
        ("_paragraphs", "_paras", -1),
        ("_addresses", "_addrs", -1),
        ("_address", "_addr", -1),
        ("average", "avg", -1),
    ],
    "dds": [
        (".frontendactivity.", ".frntendact.", -1),
        ("open_", "opn_", -1),
        ("_table", "_tbl", -1),
    ],
    "fitbit": [
        # DP name
        (".fitbit.", ".fitb.", -1),
        # DataCategories
        (".steps.", ".st.", -1),
        (".calories.", ".cl.", -1),
        (".distance.", ".dr.", -1),
        (".floors.", ".fl.", -1),
        (".account.", ".acc.", -1),
        (".activities.", ".act.", -1),
        (".activeminutes.", ".actvmin.", -1),
        (".daily.", ".dly.", -1),
        # Variable names
        (".last_whole_month_", ".lst_whl_mnth_", -1),
        ("workout", "wrkout", -1),
        (".account_created_at_least_6_months_ago", ".created_min_6_months_ago", -1),
        ("_weekly_heart_zone_time_last_6_months", "_wkl_hrt_zn_6_mnths", -1),
        ("_weekly_active_time_last_6_months", "_wkl_actv_6_mnths", -1),
        ("_weekly_active_time_all_sources_last_6_months", "_wkl_actv_all_6_mnths", -1),
        ("_weekly_activity_time_last_6_months", "_wkl_actvty_6_mnths", -1),
        (".highest_steps_last_6_months_steps", ".hghst_stps_lst_6_mnths_stps", -1),
        (".highest_steps_last_6_months_date", ".hghst_stps_lst_6_mnths_date", -1),
        (".has_activities_last_whole_month", ".has_actvs_last_whole_month", -1),
        (".has_activities_last_whole_month", ".has_actvs_last_whole_month", -1),
        ("_aerobic_", "_aerbc_", -1),
        ("_interval_workout", "_intrvl_wrkout", -1),
        # ("", "", -1),
    ],
    "github": [
        (".github.", ".gh.", -1),
    ],
    "googlecontacts": [
        (".googlecontacts.", ".gc.", -1),
        (".people.", ".p.", -1),
    ],
    "instagram": [
        (".instagram.", ".ig.", -1),
        (".likes.", ".lk.", -1),
        (".comments.", ".cm.", -1),
        (".follower_count.", ".fc.", -1),
        (".media_count.", ".mc.", -1),
    ],
}


def get_researcher(db: Session, user: JWTUserDict) -> tuple[Researcher, None] | APIResponseValue:
    """Get the researcher from the database.

    Args:
        db:
        user:

    Returns:
        The researcher from the database and None if the user could be found.
        If the user could not be found, returns a ResponseReturnValue and the status
        code.
    """
    researcher = db.query(Researcher).filter_by(email=user["email"]).first()
    if not researcher:
        logger.error("User %s not found", user["email"])
        return APIResponses.AUTHORIZATION.UNAUTHORIZED.response

    return researcher, None


def get_project(db: Session, user: JWTUserDict) -> tuple[Project, None] | APIResponseValue:
    researcher: Researcher | FlaskResponse | None
    status: HTTPStatus | None
    researcher, status = get_researcher(db, user)
    if status is not None:
        researcher = cast(FlaskResponse, researcher)
        # Case where the user or project could not be found
        return researcher, status

    researcher = cast(Researcher, researcher)

    # get the project
    project_id = g.get("project_id")
    project: Project | None = (
        db.query(Project)
        .join(Collaboration)
        .filter(Collaboration.researcher_id == researcher.id, Project.id == project_id)
        .first()
    )

    if not project:
        logger.error("Project %s not found", project_id)
        return APIResponses.PROJECTS.NOT_FOUND.response

    return project, None


def get_project_data_connection(
    db: Session,
    user: JWTUserDict,
    data_provider_name: str,
    # ) -> tuple[Project, DataConnection, None] | tuple[None, ResponseReturnValue, int]:
) -> tuple[Project, DataConnection] | APIResponseValue:
    project: Project | FlaskResponse | None
    status: HTTPStatus | None
    project, status = get_project(db, user)
    if status is not None:
        project = cast(FlaskResponse, project)
        # Case where the user or project could not be found
        return project, status

    project = cast(Project, project)

    # get the data connection
    data_connection: Query[DataConnection] | None = db.query(DataConnection).filter_by(
        project_id=project.id,
        data_provider_name=data_provider_name,
    )

    if not data_connection:
        logger.error(
            "Data connection for %s not found in project %s",
            data_provider_name,
            project.id,
        )
        return APIResponses.DATA_PROVIDER.CONNECTION_NOT_FOUND.response

    return project, cast(DataConnection, data_connection.first())


def _apply_abbreviation_rules(
    name: str,
    ruleset: str,
    condition: Callable[[str, int], bool],
    max_length: int,
) -> str:
    for rule in REPLACEMENT_RULES[ruleset]:
        rule: StrReplaceRule
        name = name.replace(*rule)
        if condition(name, max_length):
            return name
    return name


def abbreviate_variable_name(
    variable_name: str,
    first_apply: Literal["common", "dp"] = "dp",
    strategy: Literal["full", "minimal"] = "full",
    max_length: int = 45,
) -> str:
    """Shorten variable names to conform to SurveyPlatform requirements standards."""
    if max_length == -1:
        return variable_name

    if max_length <= 0:
        msg = f"max_length must be greater than 0 or -1. Received: {max_length}"
        raise ValueError(msg)

    if strategy != "full" and len(variable_name) < max_length:
        return variable_name

    if strategy == "full":

        def condition(name: str, max_length: int) -> bool:
            return False

    else:

        def condition(name: str, max_length: int) -> bool:
            return len(name) <= max_length

    dp_name: str = variable_name.split(".")[1]
    name: str = variable_name

    first = "common" if first_apply == "common" else dp_name
    second = "common" if first_apply == "dp" else dp_name

    name = _apply_abbreviation_rules(name, first, condition, max_length)
    if strategy == "full" or condition(name, max_length):
        name = _apply_abbreviation_rules(name, second, condition, max_length)

    if len(name) > max_length:
        msg = (
            f"Variable name '{variable_name}' could not be shortened to fit the maximum {max_length} characters. "
            f"End result: '{name}'. "
            f"Shortened from: {len(variable_name)} -> {len(name)}"
        )
        raise ValueError(msg)

    return name


def insert_exists_variables(variables: list[dict]) -> list[dict]:
    start_id = len(variables)
    variables_ = deepcopy(variables)
    # exists_variables = []
    # for i, var_ in enumerate(variables_):
    #     exists_variables.append(create_exists_variable(var_, start_id + i))
    # variables_.extend(exists_variables)
    variables_.extend([
        create_exists_variable(var_, start_id + i) for i, var_ in enumerate(variables)
    ])
    variables_.sort(key=lambda x: x["qualified_name"])
    return variables_


def create_exists_variable(variable: dict, id_: int) -> dict:
    """Create a .exists variable."""
    return {
        **variable,
        "id": id_,
        "data_type": "Text",
        "qualified_name": f"{variable['qualified_name']}.exists",
    }
