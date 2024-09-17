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
        project, data_connection, status = get_project_data_connection(db, user, data_provider_name)
        if status is not None:
            data_connection: ResponseReturnValue
            # Case where something could not be found in the database
            return data_connection, status
        data_connection: DataConnection


Created on 2023-09-08 13:52

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
@author: Stefan Teofanovic (stefan.teofanovic@heig-vd.ch)
"""
from __future__ import annotations

from collections.abc import Callable
from copy import deepcopy
from typing import TYPE_CHECKING, Literal

from flask import g, jsonify

from ddsurveys.get_logger import get_logger
from ddsurveys.models import Collaboration, DataConnection, Project, Researcher

if TYPE_CHECKING:
    from flask.typing import ResponseReturnValue
    from sqlalchemy.orm.session import Session

__all__ = [
    "get_researcher",
    "get_project",
    "get_project_data_connection",
    "abbreviate_variable_name",
    "insert_exists_variables"
]

logger = get_logger(__name__)

REPLACEMENT_RULES: dict[str, list[tuple[str, str, int]]] = {
    "common": [
        (".builtin.", ".b.", -1),
        (".custom.", ".c.", -1),
        (".exists", ".e", -1),
        ("_with_", "_w_", -1),
        ("_biographies", "_bios", -1),
        ("_paragraphs", "_paras", -1),
        ("_addresses", "_addrs", -1),
        ("_address", "_addr", -1),
    ],
    "dds": [
        (".frontendactivity.", ".frntendact.", -1),
        ("open_", "opn_", -1),
        ("_table", "_tbl", -1),
    ],
    "fitbit": [
        (".fitbit.", ".fitb.", -1),
        (".steps.", ".st.", -1),
        (".calories.", ".cl.", -1),
        (".distance.", ".dr.", -1),
        (".floors.", ".fl.", -1),
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


def get_researcher(
    db: Session,
    user: dict[str, str]
) -> tuple[Researcher, None] | tuple[ResponseReturnValue, int]:
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
        logger.error("User %s not found", user['email'])
        return jsonify({"message": {"id": "api.unauthorised", "text": "Unauthorised"}}), 401

    return researcher, None


def get_project(db: Session, user: dict[str, str]) -> tuple[Project, None] | tuple[ResponseReturnValue, int]:
    researcher, satus = get_researcher(db, user)
    if satus is not None:
        # Case where the user or project could not be found
        return researcher, satus

    # get the project
    project_id = g.get('project_id')
    project = db.query(Project).join(Collaboration).filter(
        Collaboration.researcher_id == researcher.id,
        Project.id == project_id
    ).first()

    if not project:
        logger.error("Project %s not found", project_id)
        return jsonify({"message": {"id": "api.projects.not_found", "text": "Project not found"}}), 404

    return project, None


def get_project_data_connection(
    db: Session,
    user: dict[str, str],
    data_provider_name: str
) -> tuple[Project, DataConnection, None] | tuple[None, ResponseReturnValue, int]:
    project, satus = get_project(db, user)
    if satus is not None:
        # Case where the user or project could not be found
        return None, project, satus

    # get the data connection
    data_connection = db.query(DataConnection).filter_by(
        project_id=project.id,
        data_provider_name=data_provider_name
    )

    if not data_connection:
        logger.error("Data connection for %s not found in project %s", data_provider_name, project.id)
        return (None,
                jsonify({"message": {"id": "api.data_provider.connection_not_found",
                                     "text": "Data connection not found"}}),
                404)

    return project, data_connection.first(), None


def _apply_abbreviation_rules(name: str, ruleset: str, condition: Callable[[str, int], bool], max_length: int) -> str:
    for rule in REPLACEMENT_RULES[ruleset]:
        name = name.replace(*rule)
        if condition(name, max_length):
            return name
    return name


def abbreviate_variable_name(
    variable_name: str,
    first_apply: Literal['common', 'dp'] = "dp",
    strategy: Literal['full', 'minimal'] = "full",
    max_length: int = 45
) -> str:
    """Shorten variable names to conform to Qualtrics standards."""
    if max_length <= 0:
        msg = "max_length must be greater than 0"
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
        msg = f"Variable name '{variable_name}' could not be shortened to fit the maximum {max_length} characters. End result: '{name}'"
        raise ValueError(msg)

    return name


def insert_exists_variables(variables: list[dict]) -> list[dict]:
    start_id = len(variables)
    variables_ = deepcopy(variables)
    # exists_variables = []
    # for i, var_ in enumerate(variables_):
    #     exists_variables.append(create_exists_variable(var_, start_id + i))
    # variables_.extend(exists_variables)
    variables_.extend([create_exists_variable(var_, start_id + i) for i, var_ in enumerate(variables)])
    variables_.sort(key=lambda x: x["qualified_name"])
    return variables_


def create_exists_variable(variable: dict, id_: int) -> dict:
    """Create a .exists variable."""
    return {
        **variable,
        "id": id_,
        "data_type": "Text",
        "qualified_name": f"{variable['qualified_name']}.exists"
    }
