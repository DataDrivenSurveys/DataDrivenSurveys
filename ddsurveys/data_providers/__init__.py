#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This module dynamically loads all the data_provider submodules.

The dynamic loading makes it function as plug and play for adding new data providers.

The module loading code is based on:
https://stackoverflow.com/questions/3365740/how-to-import-all-submodules

Created on 2023-05-23 14:00

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
@author: Stefan Teofanovic (stefan.teofanovic@heig-vd.ch)
"""
__all__ = ["DataProvider"]

from .bases import (DataProvider, OAuthDataProvider, TOAuthDataProvider, TDataProviderClass, TOAuthDataProviderClass,
                    TDataProvider)
from ..dynamic_import import dynamic_import


excluded_dynamic_load_modules = ("bases", "custom_variables", "variables", "__init__", "_registration",)

# All data providers need to be imported before calling DataProvider.register_subclasses()
# Any data providers that are not imported will not be registered.
# Only top-level modules in data_providers will be imported.
# This import executes all the class code in the modules.
modules = dynamic_import(__file__, exclude_names=excluded_dynamic_load_modules, recursive=False)
