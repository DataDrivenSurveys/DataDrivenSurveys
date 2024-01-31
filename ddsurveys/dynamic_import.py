#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2023-09-04 13:51

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
"""

import sys
import importlib
import importlib.util
from functools import wraps
from os import PathLike
from pathlib import Path
from typing import Callable, Union
from types import ModuleType


def dynamic_import(parent_package: PathLike, exclude_names: tuple[str] = (), recursive: bool = False):
    modules = list()

    parent_package = Path(parent_package)

    if parent_package.suffix == ".py":
        parent_package = parent_package.parent

    if not recursive:
        path_iterator = Path(parent_package).glob("*")
    else:
        # TODO: Add support for recursive imports
        # path_iterator = Path(parent_package).rglob("*")
        raise NotImplementedError

    for path in path_iterator:
        if not path.is_dir() and path.suffix != ".py":
            continue
        module_name = path.stem
        if module_name.startswith(exclude_names):  # Skip importing certain modules
            continue
        try:
            modules.append(importlib.import_module(f".{module_name}", package=parent_package.stem))
        except ModuleNotFoundError:
            modules.append(importlib.import_module(f".{module_name}", package=f"ddsurveys.{parent_package.stem}"))
    return modules


class LazyModule:
    """
    Descriptor class to handle lazy module importing.
    """
    def __init__(self, module_name):
        self.module_name = module_name
        self.module = None

    def __get__(self, instance, owner):
        if not self.module:
            self.module = importlib.import_module(self.module_name)
        return self.module

    def __getattr__(self, attr):
        # Delegate attribute access to the underlying module
        return getattr(self.__get__(None, None), attr)

class LazyMember:
    """
    Descriptor class to handle lazy member importing.
    """
    def __init__(self, module_name, member_name):
        self.module_name = module_name
        self.member_name = member_name
        self.member = None

    def __get__(self, instance, owner):
        if not self.member:
            module = importlib.import_module(self.module_name)
            self.member = getattr(module, self.member_name)
        return self.member

    def __getattr__(self, attr):
        # Delegate attribute access to the underlying member
        return getattr(self.__get__(None, None), attr)

def lazy_import(name, member=None) -> None:
    """Lazily imports a module or a member of a module and binds it to the caller's namespace.

    Args:
        name (str): The name of the module to import.
        member (str or list of str, optional): The member(s) of the module to import.
            If None, the whole module is imported. Defaults to None.

    Returns: None
    """

    if member:
        if isinstance(member, list):
            for m in member:
                sys._getframe(1).f_globals[m] = LazyMember(name, m)
        else:
            sys._getframe(1).f_globals[member] = LazyMember(name, member)
    else:
        sys._getframe(1).f_globals[name] = LazyModule(name)


def require(module_name, members=None):
    """
    Decorator that lazily imports a module or its members and binds them to the caller's namespace.

    Args:
        module_name (str): The name of the module to import.
        members (str or list of str, optional): The member(s) of the module to import.
            If None, the whole module is imported. Defaults to None.

    Returns:
        function: The wrapped function with the required imports.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            lazy_import(module_name, members)
            return func(*args, **kwargs)

        return wrapper

    return decorator
