#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2023-04-27 13:47

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
@author: Stefan Teofanovic (stefan.teofanovic@heig-vd.ch)
"""

__name__ = "ddsurveys"
__author__ = "Lev Velykoivanenko"
__author_email__ = "lev.velykoivanenko@unil.com"
__version__ = "1.0.0"
__license___ = ""
__package__ = "ddsurveys"


# Set up custom loggers
import coloredlogs

from .get_logger import get_logger

# We can override the builtin getLogger function with our own
# logging.getLogger = get_logger

coloredlogs.install()


# Import base data provider
# import data_providers
from .data_providers import DataProvider

# Import base survey platforms
# import survey_platforms
from .survey_platforms import SurveyPlatform

