"""This module provides various utility functions.

Created on 2024-04-30 13:44

@author: Lev Velykoivanenko (lev.velykoivanenko@gmail.com)
@author: Stefan Teofanovic (stefan.teofanovic@heig-vd.ch)
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import dotenv_values


def get_and_load_env(path: Path | str, *, in_module_root: bool = False) -> dict[str, str | None]:
    """Loads environment variables from a path.

    This function first resolves the given path to an absolute path.
    If `in_module_root` is True, the path is treated as relative to the module's root
    directory.
    It then loads environment variables from the specified `.env` file.
    If a `.env.local` file exists in the same directory, it loads this file as well,
    allowing local overrides of the environment variables.

    Args:
        path: A Path object or string specifying the path to the `.env` file.
            This can be an absolute path or, if
            `in_module_root` is True, a path relative to the module's root directory.
        in_module_root: A boolean indicating whether the path is relative to the
            module's root directory.
            Defaults to False.

    Returns:
        A dictionary with the loaded environment variables.
        The keys are the variable names, and the values are the variable values or None
        if the variable is not set.
        If `.env.local` exists, variables defined there will override those from the
        `.env` file.
    """
    # Prepare paths
    module_dir: Path = Path(__file__).resolve().parent
    path = module_dir.joinpath(path).resolve() if in_module_root else Path(path).resolve()
    path_dot_local: Path = path.parent.joinpath(f"{path.name}.local")

    env: dict[str, str | None] = dotenv_values(str(path))
    if path_dot_local.is_file():
        env = {**env, **dotenv_values(str(path_dot_local))}

    # Load .env file variables into the environment variables
    for k, v in env.items():
        if v is not None:
            os.environ[k] = v
    return env


def handle_env_file(path: str | None = None) -> dict[str, str | None]:
    """Load environment variables from a custom path or from the default .env files.

     The default .env files are located inside the module root.

    This function is designed to simplify the process of loading environment variables
    for different deployment stages (e.g., development, testing, production) by
    automatically selecting the appropriate `.env` file based on the `DDS_ENV`
    environment variable.
    If a `.env.local` file exists for the selected environment, it will also be loaded
    to allow for local overrides.
    This approach follows the loading conventions used by Create React App (CRA).

    Args:
        path: A string specifying a custom path to an environment file.
            If provided, this file will be loaded instead of the default files
            based on `DDS_ENV`.
            If not provided, the function will load the environment file based on the
            value of `DDS_ENV` or default to `.env.development` if `DDS_ENV` is not set.

    Returns:
        A dictionary containing the loaded environment variables.
        The keys are the variable names, and the values are the variable values
        or None if the variable is not set.
        If a `.env.local` file exists for the selected environment, variables defined
        there will override those from the main `.env` file.
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
