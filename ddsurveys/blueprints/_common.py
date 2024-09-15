#!/usr/bin/env python3
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

from typing import TYPE_CHECKING

from flask import g, jsonify

from ddsurveys.get_logger import get_logger
from ddsurveys.models import Collaboration, DataConnection, Project, Researcher

if TYPE_CHECKING:
    from flask.typing import ResponseReturnValue
    from sqlalchemy.orm.session import Session

__all__ = ["get_researcher", "get_project", "get_project_data_connection"]


logger = get_logger(__name__)


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
