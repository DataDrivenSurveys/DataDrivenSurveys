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
        load_dotenv(path)
        env = dotenv_values(path)
        if Path(f"{path}.local").is_file():
            load_dotenv(f"{path}.local")
            env = {**env, **dotenv_values(f"{path}.local")}
    elif os.environ.get("DDS_DEVELOPMENT", "False").casefold() == "true":
        # Development environment
        env_path = module_dir.joinpath(".env.development").resolve()
        env_local_path = module_dir.joinpath(".env.development.local").resolve()
        load_dotenv(str(env_path))
        env = dotenv_values(str(env_path))
        if env_local_path.is_file():
            load_dotenv(str(env_local_path))
            env = {**env, **dotenv_values(str(env_local_path))}
    else:
        # Default to production environment
        env_path = module_dir.joinpath(".env.production").resolve()
        env_local_path = module_dir.joinpath(".env.production.local").resolve()
        load_dotenv(str(env_path))
        env = dotenv_values(str(env_path))
        if env_local_path.is_file():
            load_dotenv(str(env_local_path))
            env = {**env, **dotenv_values(str(env_local_path))}

    return env

