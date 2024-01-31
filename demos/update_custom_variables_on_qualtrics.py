#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2023-05-08 12:09

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
"""

import sys
import os
from pprint import pprint

# Insert project root into the path to allow imports
sys.path.insert(0, os.path.join(os.getcwd(), ".."))

from survey_platforms.qualtrics import EmbeddedData, EmbeddedDataBlock, Flow, SurveysAPI


if __name__ == "__main__":
    #
    # Creating the variables with a completely new survey
    #

    surveys_api = SurveysAPI(datacenter_location="EU")

    # This represents an EmbeddedData block in the survey flow.
    initial_custom_variables = {
        'Type': 'EmbeddedData',
        'FlowID': 'FL_2',
        'EmbeddedData': [
            {'Description': 'dds.fitbit.account.created_date', 'Type': 'Recipient',
             'Field': 'dds.fitbit.account.created_date', 'VariableType': 'Date', 'DataVisibility': []},
            {'Description': 'dds.fitbit.steps.average', 'Type': 'Recipient', 'Field': 'dds.fitbit.steps.average',
             'VariableType': 'Scale', 'DataVisibility': []}
        ]
    }

    # Provide the survey ID of an existing survey:
    survey_id = ''

    #
    # Get initial flow
    # Qualtrics creates by default the first block.
    #
    flow = Flow(surveys_api.get_flow(survey_id).json()["result"])

    # Add the new variables to the flow
    flow.custom_variables.update(EmbeddedDataBlock(initial_custom_variables))

    # An extra custom variable can be added like so:
    new_variable_name = "dds.fitbit.steps.median"
    new_variable = EmbeddedData(new_variable_name, "Recipient", "Scale")

    flow.custom_variables.append(new_variable)

    # Update the variables on Qualtrics
    resp = surveys_api.update_flow(survey_id, flow.to_dict())

    print(f"The survey can now be viewed on Qualtrics at the following URL:\n{surveys_api.get_survey_url(survey_id)}")

    # Check if the new flow is valid and has a root block:
    qualtrics_flow = Flow(surveys_api.get_flow(survey_id).json()["result"])
    print(qualtrics_flow)
    pprint(qualtrics_flow.to_dict())

    # The result should be this (assuming a newly created survey was used):
    # Flow(2 blocks, custom variables block id: FL_3)
    # {'Flow': [{'EmbeddedData': [{'AnalyzeText': False,
    #                              'DataVisibility': [],
    #                              'Description': 'dds.fitbit.account.created_date',
    #                              'Field': 'dds.fitbit.account.created_date',
    #                              'Type': 'Recipient',
    #                              'Value': '',
    #                              'VariableType': 'Date'},
    #                             {'AnalyzeText': False,
    #                              'DataVisibility': [],
    #                              'Description': 'dds.fitbit.steps.average',
    #                              'Field': 'dds.fitbit.steps.average',
    #                              'Type': 'Recipient',
    #                              'Value': '',
    #                              'VariableType': 'Scale'},
    #                             {'AnalyzeText': False,
    #                              'DataVisibility': {'Hidden': False,
    #                                                 'Private': False},
    #                              'Description': 'dds.fitbit.steps.median',
    #                              'Field': 'dds.fitbit.steps.median',
    #                              'Type': 'Recipient',
    #                              'Value': '',
    #                              'VariableType': 'Scale'}],
    #            'FlowID': 'FL_3',
    #            'Type': 'EmbeddedData'},
    #           {'FlowID': 'FL_2', 'ID': 'BL_8p4qO28FpNhZm8S', 'Type': 'Block'}],
    #  'FlowID': 'FL_1',
    #  'Properties': {'Count': 3},
    #  'Type': 'Root'}

    # Delete the demo survey
    # Uncomment the following lines if you want to check how the survey looks like on Qualtrics
    # delete_resp = surveys_api.delete_survey(survey_id)
    # if delete_resp.status_code == 200:
    #     print("Deleted successfully.")
    # else:
    #     print("Failed to delete with the following error:")
    #     pprint(delete_resp.json())
