#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2023-04-27 13:47

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
"""

__name__ = "ddsurveys"
__author__ = "Lev Velykoivanenko"
__author_email__ = "lev.velykoivanenko@unil.com"
__version__ = "0.0.1"
__license___ = ""
__package__ = "ddsurveys"


# Set up custom loggers
import logging
from .get_logger import get_logger
import verboselogs
import coloredlogs

# We can override the builtin getLogger function with our own
# logging.getLogger = get_logger

coloredlogs.install()


# Import base data provider
# import data_providers
from .data_providers import DataProvider

# Import base survey platforms
# import survey_platforms
from .survey_platforms import SurveyPlatform

