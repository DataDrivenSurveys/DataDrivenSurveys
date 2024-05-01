#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2023-09-05 17:52

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
@author: Stefan Teofanovic (stefan.teofanovic@heig-vd.ch)
"""

import logging
from typing import Union

import coloredlogs

coloredlogs.install()

# In the event that we decide to replace the default logger with a custom one, backup the old one.
old_logger = logging.getLogger


def get_logger(name: str) -> logging.Logger:
    """Get a logger and ensure its hierarchy matches the name."""
    name_: str
    if not name.startswith('ddsurveys'):
        name_ = f'ddsurveys.{name}'
    else:
        name_ = name

    parts: list[str] = name_.split('.')
    current_name: str = ''
    last_logger = None
    logger = None
    for part in parts:
        current_name = f'{current_name}.{part}' if current_name else part
        logger = old_logger(current_name)
        if last_logger:
            logger.parent = last_logger  # Set the parent logger
        last_logger = logger

    if logger is None:
        logger = old_logger(name)
    return logger


module_logger: logging.Logger = get_logger(__name__)


def only_log_ddsurveys() -> None:
    """Filter logger output to only show output from loggers that start with 'ddsurveys'.

    This silences the output from most loggers used in imported packages.
    """
    logging.getLogger('urllib3').setLevel(logging.CRITICAL)
    logging.getLogger('requests_oauthlib').setLevel(logging.CRITICAL)
    logging.getLogger().addFilter(lambda record: record.name.startswith('ddsurveys'))


def set_logger_level(
    logger: Union[str, logging.Logger],
    level: Union[int, str] = logging.INFO,
    recursive: bool = False,
    include_root: bool = False,
) -> None:
    """Set a logger's level.

    This function can also be used to change the log level of the entire logger's hierarchy.
    It can also be used to change the log level of the root logger.

    Args:
        logger:
        level:
        recursive:
        include_root:

    Returns:

    """
    if not isinstance(logger, logging.Logger):
        logger = get_logger(logger)

    if isinstance(level, str):
        level = getattr(logging, level.upper())

    if include_root:
        coloredlogs.set_level(level)

    if not recursive:
        logger.setLevel(level)
        return

    loggers = [l for l in logger.manager.loggerDict.values()
               if (hasattr(l, "parent") and l.parent == logger)  or (hasattr(l, "name") and logger.name in l.name)]

    for l in loggers:
        l.setLevel(level)


def match_app_logger_level(only_log_ddsurveys_: bool = False) -> None:
    from flask import current_app as app

    try:
        set_logger_level("ddsurveys", app.logger.level, recursive=True, include_root=True)
        coloredlogs.set_level(app.logger.level)
        if only_log_ddsurveys_:
            only_log_ddsurveys()
    except RuntimeError:
        module_logger.warning("Tried to call match_app_logger_level while not in a flask app context.")
