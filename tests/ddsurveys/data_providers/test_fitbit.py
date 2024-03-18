#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2023-11-16 13:50

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
@author: Stefan Teofanovic (stefan.teofanovic@heig-vd.ch)
"""

import pytest
from ddsurveys.data_providers.fitbit import FitbitDataProvider, Activities, Account, Steps, Badges


# DATA CATEGORY TESTS
def test_data_category_get_by_value():
    """Check data category retrieval by value."""
    # Given the structure, `Account` should be discoverable by its value.
    assert FitbitDataProvider.get_data_category("account") == Account
    assert FitbitDataProvider.get_data_category("activities") == Activities
    assert FitbitDataProvider.get_data_category("steps") == Steps
    assert FitbitDataProvider.get_data_category("badges") == Badges


@pytest.mark.parametrize("data_category", [Account, Activities, Steps, Badges])
def test_datacategory_to_dict(data_category):
    """Validate data category dictionary conversion."""
    # Ensure to_dict provides the expected structure.
    account_dict = data_category.to_dict()
    assert 'label' in account_dict, "The label should be included in the DataCategory dict."
    assert 'value' in account_dict, "The value should be included in the DataCategory dict."
    assert 'builtin_variables' in account_dict, "The builtin variables should be included in the DataCategory dict."
    assert 'cv_attributes' in account_dict, "The custom variables should be included in the DataCategory dict."

