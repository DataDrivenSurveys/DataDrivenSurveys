"""This module provides logging functionalities tailored for the Data-Driven Surveys app.

It includes custom logger creation, configuration, and filtering mechanisms to enhance
logging output and management.
The module facilitates the creation of loggers with a consistent naming convention,
allows for dynamic log level
adjustments, and provides utilities to restrict logging output to specific parts of the
app.
Additionally, it integrates colored logging for improved readability and supports
matching Flask app log levels with custom loggers.

Created on 2023-09-05 17:52

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
@author: Stefan Teofanovic (stefan.teofanovic@heig-vd.ch)
"""

import logging
from typing import Literal

import coloredlogs

# coloredlogs.install()

# In the event that we decide to replace the default logger with a custom one, backup the old one.
old_logger = logging.getLogger


# class ProjectLoggerLevelsInt(IntEnum):
#     NOTSET = 0
#     DEBUG = 10
#     INFO = 20
#     WARN = 30
#     WARNING = 30
#     ERROR = 40
#     CRITICAL = 50
#     FATAL = 50


# class ProjectLoggerLevelsStr(StrEnum):
#     NOTSET = "NOTSET"
#     DEBUG = "DEBUG"
#     INFO = "INFO"
#     WARN = "WARN"
#     WARNING = "WARNING"
#     ERROR = "ERROR"
#     CRITICAL = "CRITICAL"
#     FATAL = "FATAL"


type ProjectLoggerLevels = Literal[
    "NOTSET",
    "DEBUG",
    "INFO",
    "WARN",
    "WARNING",
    "ERROR",
    "CRITICAL",
    "FATAL",
]


def get_logger(name: str) -> logging.Logger:
    """Creates or retrieves a logger with a hierarchical name that starts with 'ddsurveys'.

    If the provided name does not start with 'ddsurveys', it is prefixed accordingly.
    This ensures that all loggers used within the app follow a consistent naming
    convention, facilitating easier management and filtering of log messages.

    The function constructs the logger hierarchy by splitting the name on dots and
    creating or retrieving loggers for each segment, setting each as the parent of the
    next.
    This hierarchical structure allows for fine-grained control over logging levels
    and propagation.

    Parameters:
        name: The name of the logger.
            This will be prefixed with 'ddsurveys' if not already.

    Returns:
        The logger object with the specified name, following the app's naming convention.

    Note:
        If the logger for the specified name already exists, it will be retrieved instead of created.
    """
    name_: str
    name_ = f"ddsurveys.{name}" if not name.startswith("ddsurveys") else name

    parts: list[str] = name_.split(".")
    current_name: str = ""
    last_logger = None
    logger = None
    for part in parts:
        current_name = f"{current_name}.{part}" if current_name else part
        logger = old_logger(current_name)
        if last_logger:
            logger.parent = last_logger  # Set the parent logger
        last_logger = logger

    if logger is None:
        logger = old_logger(name)
    return logger


module_logger: logging.Logger = get_logger(__name__)


def only_log_ddsurveys() -> None:
    """Filters the logging output to only include messages from loggers that start with 'ddsurveys'.

    This function specifically targets and silences the output from common imported
    packages such as 'urllib3' and 'requests_oauthlib' by setting their log level to
    CRITICAL.

    Additionally, it adds a filter to the root logger to ensure that only log messages
    originating from loggers with names starting with 'ddsurveys' are displayed.

    This is particularly useful for reducing noise in the app's log output,
    making it easier to focus on relevant app-specific messages.

    There are no parameters or return values for this function.
    """
    logging.getLogger("urllib3").setLevel(logging.CRITICAL)
    logging.getLogger("requests_oauthlib").setLevel(logging.CRITICAL)
    logging.getLogger().addFilter(lambda record: record.name.startswith("ddsurveys"))


def set_logger_level(
    logger: str | logging.Logger,
    level: int | str = logging.INFO,
    recursive: bool = False,
    include_root: bool = False,
) -> None:
    """Sets the logging level for a specified logger.

    This function allows for the adjustment of logging levels
    dynamically, facilitating more granular control over logging output.

    It can operate on both individual loggers and hierarchies
    of loggers, and optionally adjust the root logger's level to match.

    Args:
        logger: The logger to adjust.
            This can be specified either by its name (str) or directly by passing a
            logging.Logger instance.
            If a name is provided, the logger will be retrieved or created following
            the application's naming convention.
        level: The new logging level. This can be specified either as a logging level
            constant (e.g., logging.INFO) or as a string (e.g., 'INFO').
            Defaults to logging.INFO.
        recursive: If True, the function will recursively set the logging level for all
            child loggers of the specified logger.
            This is useful for adjusting logging levels across a section of the
            application.
            Defaults to False.
        include_root: If True, the root logger's level will also be set to the specified
            level.
            This affects all loggers in the application and can be used to globally
            adjust logging verbosity.
            Defaults to False.

    Returns:
        This function does not return a value but modifies the logging configuration
        directly.
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

    l: logging.Logger
    loggers = [
        l
        for l in logger.manager.loggerDict.values()
        if (hasattr(l, "parent") and l.parent == logger)
        or (hasattr(l, "name") and logger.name in l.name)
    ]

    for l in loggers:
        l.setLevel(level)


def match_app_logger_level(only_log_ddsurveys_: bool = False) -> None:
    """Matches the logging level of the application's custom loggers with the Flask application's current logging level.

    This function ensures that the logging output from the custom loggers ('ddsurveys' prefixed) is consistent with
    the Flask application's logging level, providing a unified logging verbosity across the application. Additionally,
    it can filter the logging output to only include messages from 'ddsurveys' prefixed loggers, reducing noise from
    external libraries.

    Args:
      only_log_ddsurveys_ (bool, optional):
        If True, filters the logging output to only include messages from loggers that start with 'ddsurveys'. This
        is useful for focusing on application-specific log messages and reducing noise from external libraries.
        Defaults to False.

    Returns:
      None:
        This function does not return a value but modifies the logging configuration directly.

    Raises:
      RuntimeError:
        If the function is called outside a Flask application context, a RuntimeError is raised. This ensures that
        the function is only used where it can properly access the Flask application's logger.
    """
    from flask import current_app as app

    try:
        set_logger_level("ddsurveys", app.logger.level, recursive=True, include_root=True)
        coloredlogs.set_level(app.logger.level)
        if only_log_ddsurveys_:
            only_log_ddsurveys()
    except RuntimeError:
        module_logger.warning(
            "Tried to call match_app_logger_level while not in a flask app context."
        )
