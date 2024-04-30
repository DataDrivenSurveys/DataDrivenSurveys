#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2024-04-30 13:44

@author: Lev Velykoivanenko (lev.velykoivanenko@gmail.com)
@author: Stefan Teofanovic (stefan.teofanovic@heig-vd.ch)
"""
import os
from pathlib import Path
from typing import Optional

from dotenv import dotenv_values, load_dotenv


def get_and_load_env(path: Path) -> dict[str, Optional[str]]:
    path = Path(path).resolve()
    path_dot_local = path.parent.joinpath(f"{path.name}.local")
    load_dotenv(str(path))
    env = dotenv_values(str(path))
    if path_dot_local.is_file():
        load_dotenv(str(path_dot_local))
        env = {**env, **dotenv_values(str(path_dot_local))}
    return env


def handle_env_file(path: Optional[str] = None) -> dict[str, Optional[str]]:
    """
    Load environment variables from a custom path or from the environment files located inside the module root.
    This function follows loading conventions of Create React App (CRA), wherein it will load default files and then
    .local version if they exist.

    Args:
        path: Path to the environment file. If not provided, the environment files located inside the module root are loaded.

    Returns:
        dict[str, Optional[str]]: A dict containing the loaded environment variables.
    """

    module_dir = Path(__file__).resolve().parent
    if path is not None:
        # Load environment variables from a custom path
        env = get_and_load_env(path)
    elif os.environ.get("DDS_ENV", "development").casefold() == "development":
        # Development environment
        env = get_and_load_env(module_dir.joinpath(".env.development"))
    elif os.environ.get("DDS_ENV", "testing").casefold() == "testing":
        env = get_and_load_env(module_dir.joinpath(".env.testing"))
    else:
        # Default to production environment
        env = get_and_load_env(module_dir.joinpath(".env.production"))

    return env

