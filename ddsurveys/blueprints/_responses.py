"""This module provides the ResponseReturnValues and dicts for various methods.

Created on 2024-09-23 15:55

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
"""
from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

from ddsurveys.typings.models import ProjectPublicDict

if TYPE_CHECKING:
    from ddsurveys.typings.data_providers.variables import ProjectVariableDict

class MessageDict(TypedDict):
    id: str
    text: str


MessageResponse = tuple[MessageDict, int]


class Projects:
    class GetPublicProjectDict(ProjectPublicDict):
        project_ready: bool
        used_variables: list[ProjectVariableDict]

    class GetPublicProjectResponse:
        ...
