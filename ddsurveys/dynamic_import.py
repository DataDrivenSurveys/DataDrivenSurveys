#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This module provides utilities for dynamic and lazy importing of modules and their members within the Data-Driven Surveys application. It aims to streamline the import process, reduce initial load times, and manage namespace pollution by allowing for the selective import of modules and their components only when they are actually needed.

Features include:
- Dynamic import of all modules within a specified directory, with support for excluding specific modules and planned support for recursive directory traversal.
- Lazy loading of modules and their members, which defers the import until the module or member is accessed for the first time.
- A decorator to facilitate lazy importing directly within function or method definitions, further simplifying the management of dependencies.

The utilities provided by this module are particularly useful in large applications with many dependencies or modules, where import times can significantly impact startup times or where namespace management becomes cumbersome.

Usage examples include dynamically importing plugins or modules based on configuration files, lazily importing heavy dependencies in a script to improve command line tool responsiveness, or simply organizing imports more efficiently in a large codebase.

Created on 2023-09-04 13:51

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
@author: Stefan Teofanovic (stefan.teofanovic@heig-vd.ch)
"""

import importlib
import importlib.util
import sys
from functools import wraps
from os import PathLike
from pathlib import Path


def dynamic_import(parent_package: PathLike, exclude_names: tuple[str] = (), recursive: bool = False):
    """
    Dynamically imports modules from a specified directory.

    This function imports all Python modules found in the given directory, optionally excluding
    specified module names and supporting recursive search within subdirectories.

    Args:
        parent_package (PathLike): The directory from which to import modules. If a file is passed,
                                   its parent directory is used.
        exclude_names (tuple[str], optional): Names of modules to exclude from importing. Defaults to ().
        recursive (bool, optional): If True, imports modules from subdirectories recursively. Currently,
                                    this feature is not implemented and will raise NotImplementedError if set to True.

    Returns:
        list: A list of imported modules.

    Raises:
        NotImplementedError: If recursive import is requested, as this feature is not yet implemented.
    """
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
        except (ImportError, ModuleNotFoundError):
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
