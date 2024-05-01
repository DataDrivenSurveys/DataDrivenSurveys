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


def get_and_load_env(path: Path | str, in_module_root: bool = False) -> dict[str, Optional[str]]:
    # Prepare paths
    module_dir = Path(__file__).resolve().parent
    if in_module_root:
        path = module_dir.joinpath(path).resolve()
    else:
        path = Path(path).resolve()
    path_dot_local = path.parent.joinpath(f"{path.name}.local")

    # Load environment variables
    load_dotenv(str(path))
    env = dotenv_values(str(path))
    if path_dot_local.is_file():
        # Load .local override files to override the default ones
        load_dotenv(str(path_dot_local))
        env = {**env, **dotenv_values(str(path_dot_local))}
    return env


def handle_env_file(path: Optional[str] = None) -> dict[str, Optional[str]]:
    """
    Load environment variables from a custom path or from the environment files located inside the module root.
    This function follows loading conventions of Create React App (CRA), wherein it will load default files and then
    .local version if they exist.
    The type of environment file that is is loaded is determined by the environment variable DDS_ENV.
    If DDS_ENV is not set, it will default to "development".

    Args:
        path: Path to the environment file. If not provided, the environment files located inside the module root are loaded.

    Returns:
        dict[str, Optional[str]]: A dict containing the loaded environment variables.
    """
    env: dict[str, str | None]
    if path is not None:
        # Load environment variables from a custom path
        env = get_and_load_env(path=path)
    elif os.environ.get("DDS_ENV", "").casefold() == "production":
        env = get_and_load_env(".env.production", in_module_root=True)
    elif os.environ.get("DDS_ENV", "").casefold() == "testing":
        env = get_and_load_env(".env.testing", in_module_root=True)
    else:
        # Default to development environment
       env = get_and_load_env(".env.development", in_module_root=True)

    return env
