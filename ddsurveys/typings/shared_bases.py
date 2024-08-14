#!/usr/bin/env python3
"""
Created on 2024-07-25 18:33

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
"""
from typing import Any, NotRequired, TypedDict


class DataDict(TypedDict):
    helper_url: str


class FormFieldDict(TypedDict):
    name: str
    label: str
    value: str
    type: str
    disabled: bool
    required: bool
    helper_text: str
    visibility_conditions: NotRequired[Any]
    interaction_effects: NotRequired[Any]
    data: DataDict
