#!/usr/bin/env python3
"""Created on 2023-05-08 12:16.

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
@author: Stefan Teofanovic (stefan.teofanovic@heig-vd.ch)
"""

import os
import sys

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

    test2 = {
        'FlowID': 'FL_2',
        'Type': 'EmbeddedData',
        'EmbeddedData': [
            {
                'Description': 'dds.fitbit.account.creation_date',
                'Field': 'dds.fitbit.account.creation_date',
                'Type': 'Recipient',
                'VariableType': 'Date',
                'DataVisibility': {'Private': False, 'Hidden': False},
                'AnalyzeText': False,
                'Value': ''
            }, {
                'Description': 'dds.fitbit.activities_by_frequency[0]',
                'Field': 'dds.fitbit.activities_by_frequency[0]',
                'Type': 'Recipient',
                'VariableType': 'String',
                'DataVisibility': {'Private': False, 'Hidden': False},
                'AnalyzeText': False,
                'Value': ''
            }, {
                'Description': 'dds.fitbit.activities_by_frequency[1]',
                'Field': 'dds.fitbit.activities_by_frequency[1]',
                'Type': 'Recipient',
                'VariableType': 'String',
                'DataVisibility': {'Private': False, 'Hidden': False},
                'AnalyzeText': False,
                'Value': ''
            }, {
                    'Description': 'dds.fitbit.steps.average',
                    'Field': 'dds.fitbit.steps.average',
                    'Type': 'Recipient',
                    'VariableType': 'Scale',
                    'DataVisibility': {'Private': False, 'Hidden': False},
                    'AnalyzeText': False,
                    'Value': ''
            }
        ]
    }

    resp = surveys_api.create_survey("DDSurveys Temp Demo Survey")
    survey_id = resp.json()["result"]["SurveyID"]

    # survey_id = ''

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


    # Check if the new flow is valid and has a root block:
    qualtrics_flow = Flow(surveys_api.get_flow(survey_id).json()["result"])

    # The result should be this:
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
    # Comment the following line if you want to check how the survey looks like on Qualtrics
    delete_resp = surveys_api.delete_survey(survey_id)
    if delete_resp.status_code == 200:
        pass
    else:
        pass
