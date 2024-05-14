#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2023-05-08 16:20

If you need to implement a custom API for a new survey platform, you can use this submodule to do so.
Otherwise, you can just delete it or ignore it.

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
@author: Stefan Teofanovic (stefan.teofanovic@heig-vd.ch)
"""

from .qualtrics_requests import QualtricsRequests

from .distributions import DistributionsAPI
from .exceptions import (
    AuthorizationError,
    BadRequestError,
    FailedQualtricsRequest,
    MissingAPIToken,
    MissingMailingListID,
    MissingSurveyID,
    NotFoundError,
    ServerError,
    UnhandledStatusCodeError,
)
from .surveys import SurveysAPI
