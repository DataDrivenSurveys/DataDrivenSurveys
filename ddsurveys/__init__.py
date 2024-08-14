#!/usr/bin/env python3
"""Created on 2023-04-27 13:47.

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
@author: Stefan Teofanovic (stefan.teofanovic@heig-vd.ch)
"""

__name__ = "ddsurveys"
__author__ = "Lev Velykoivanenko"
__author_email__ = "lev.velykoivanenko@unil.com"
__version__ = "1.0.0"
__license___ = "MIT License"
__package__ = "ddsurveys"

# Set up custom loggers
import coloredlogs

from ddsurveys.data_providers import DataProvider
from ddsurveys.get_logger import get_logger
from ddsurveys.survey_platforms import SurveyPlatform

# We can override the builtin getLogger function with our own
# logging.getLogger = get_logger

coloredlogs.install()
