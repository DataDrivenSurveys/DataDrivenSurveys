#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2023-06-06 14:54

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
"""
from requests import Response


class FailedRequest(Exception):
    def __init__(self, resp: Response):
        message = f"Request failed with status code: {resp.status_code}."
        super().__init__(message)
