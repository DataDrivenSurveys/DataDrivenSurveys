#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2023-06-06 15:10

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
"""
from ddsurveys.survey_platforms.qualtrics.api import DistributionsAPI

if __name__ == "__main__":
    # Create an unique distribution URL
    distributions_api = DistributionsAPI()

    # You need to provide the survey_id of the survey for which you want to create a unique URL
    survey_id = ""

    # Get the first contacts directory id
    # Make sure to store this ID for future use
    directory_id = distributions_api.get_first_directory_id()

    # TODO: move mailing list creation+directory id getting to project creation

    # Get the user id of the account making API calls
    # Make sure to store this ID for future use
    user_id = distributions_api.get_user_id()

    # Create a new mailing list
    # Make sure to store this ID for future use
    mailing_list_id = distributions_api.create_mailing_list(directory_id, "DataDrivenSurveys - UUID", user_id).json()["result"]["id"]

    #
    # Create a new contact for a participant
    #
    embedded_data = {
        'fitbit.account.created_date': '2015-05-23',
        'fitbit.act1.date': '2022-06-23',
        'fitbit.act1.distance': 11.3,
        'fitbit.act1.map': 'https://i.pinimg.com/originals/d0/93/25/d09325349cc7b502e0f64f612021c925.jpg',
        'fitbit.act1.type': 'Running',
        'fitbit.activities.by_frequency[0]': 'Running',
        'fitbit.activities.by_frequency[1]': 'Gym',
        'fitbit.activities.by_frequency[2]': 'Yoga',
        'fitbit.activities.most_frequent': 'Running',
        'fitbit.steps.average': 11526,
        'fitbit.steps.median': 7500,
    }
    new_contact_dict = distributions_api.create_contact(directory_id, mailing_list_id, embedded_data)
    contact_id = new_contact_dict["id"]
    contact_lookup_id = new_contact_dict["contactLookupId"]
    # The contact_lookup_id will be paired with the mailing_list_id in future API calls

    unique_url = distributions_api.create_unique_distribution_link(survey_id, mailing_list_id, contact_lookup_id)

    print("The unique URL for the new contact is:")
    print(unique_url)
