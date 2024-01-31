#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2023-04-27 13:51

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
"""

import json
from pathlib import Path

from ddsurveys.qualtrics_api.survey_api import *
from ddsurveys.qualtrics_api.qualtrics_requests import QualtricsRequests


if __name__ == "__main__":
    conf_file = Path("conf.json")
    if conf_file.is_file():
        with open(conf_file, "r") as f:
            conf = json.load(f)
    else:
        conf = {

        }

    q_requests = QualtricsRequests(conf["Qualtrics_API_token"], "EU")
    surveys_api = Surveys(conf["Qualtrics_API_token"], "EU")

    data = {"SurveyName": "api-test-survey",
            "Language": "EN",
            "ProjectCategory": "CORE"}

    # resp = q_requests.post("survey-definitions", json=data)

    notice = {
        'meta': {
            'httpStatus': '200 - OK',
            'requestId': '3e81237f-fcf0-41dc-8684-0775368e5f7c',
            'notice': 'Request proxied. For faster response times, use this host instead: fra1.qualtrics.com'
        },
        'result': {'SurveyID': 'SV_7ZBfmQv4GsOxzng',
                   'DefaultBlockID': 'BL_4ZuxNCEfXnRyphA'}}

    info = {'meta': {'httpStatus': '200 - OK',
                     'requestId': '25641ae0-b766-47c1-8679-cea3e5021be2'},
            'result': {'SurveyID': 'SV_e3OyJozlSuFHdzw',
                       'DefaultBlockID': 'BL_56mcNMyfwfkF6Ye'}}

    # r = resp
    print(surveys_api.base_url)
    # r = q_requests.get("survey-definitions/SV_e3OyJozlSuFHdzw")
    r = surveys_api.get_survey("SV_e3OyJozlSuFHdzw")
    print(surveys_api.base_url)
