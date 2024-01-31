#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2023-05-05 11:14

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
"""
import unittest

from ddsurveys.survey_platforms.qualtrics import SurveysAPI


class SurveyTest(unittest.TestCase):

    _temp_survey_id = ""

    def __init__(self, *args, **kwargs):
        self.survey_id = "SV_dd3PBVMgHt4UcTA"
        self.survey_api = SurveysAPI()
        super().__init__(*args, **kwargs)

    @property
    def temp_survey_id(self):
        return self.__class__._temp_survey_id

    def test_create_delete_survey(self):
        resp = self.survey_api.create_survey("Test Surveys API")
        self.created_survey_id = resp.json()["result"]["SurveyID"]
        self.assertEqual(resp.status_code, 200)

        resp2 = self.survey_api.delete_survey(self.created_survey_id)
        self.assertEqual(resp2.status_code, 200)

    def test_get_survey(self):
        resp = self.survey_api.get_survey(self.survey_id)
        self.assertEqual(resp.status_code, 200)

    def test_get_survey_metadata(self):
        resp = self.survey_api.get_survey_metadata(self.survey_id)
        self.assertEqual(resp.status_code, 200)

    def test_get_flow(self):
        resp = self.survey_api.get_flow(self.survey_id)
        self.assertEqual(resp.status_code, 200)


if __name__ == '__main__':
    unittest.main()
