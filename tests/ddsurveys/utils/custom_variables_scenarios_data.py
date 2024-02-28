#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# not used yet
custom_variables_processing_scenarios = [
    (
        "Scenario 1: Filter by calories > 230, select the earliest activity",
        [
            {"attr": "calories", "operator": "__gt__", "value": "230"}
        ],
        {
            "attr": "originalStartTime", "operator": "min"
        },
        {
            'dds.fitbit.custom.activities.act1.exists': True,
            'dds.fitbit.custom.activities.act1.duration': 1228000,
            'dds.fitbit.custom.activities.act1.duration.exists': True,
            'dds.fitbit.custom.activities.act1.calories': 234,
            'dds.fitbit.custom.activities.act1.calories.exists': True,
            'dds.fitbit.custom.activities.act1.date': '2023-01-10T12:00:00.000',
            'dds.fitbit.custom.activities.act1.date.exists': True,
            'dds.fitbit.custom.activities.act1.distance': 0,
            'dds.fitbit.custom.activities.act1.distance.exists': True,
            'dds.fitbit.custom.activities.act1.type': 'Sport',
            'dds.fitbit.custom.activities.act1.type.exists': True
        }

    )
]

example_values = {
    "Date": {
        "attr": "originalStartTime",
        "value": "2023-01-10T12:00:00.000",
        "expected": {
            "__eq__": {
                "min": "2023-01-10T12:00:00.000",
                "max": "2023-01-10T12:00:00.000",
                "random": "2023-01-10T12:00:00.000"
            },
            "__ne__": {
                "min": "2023-01-01T12:00:00.000",
                "max": "2023-01-15T12:00:00.000",
                "random": None  # we have 2 resulting rows, can be either
            },
            "__gt__": {
                "min": "2023-01-15T12:00:00.000",
                "max": "2023-01-15T12:00:00.000",
                "random": None  # we have 2 resulting rows, can be either
            },
            "__ge__": {
                "min": "2023-01-10T12:00:00.000",
                "max": "2023-01-15T12:00:00.000",
                "random": None  # we have 2 resulting rows, can be either
            },
            "__lt__": {
                "min": "2023-01-01T12:00:00.000",
                "max": "2023-01-01T12:00:00.000",
                "random": "2023-01-01T12:00:00.000"
            },
            "__le__": {
                "min": "2023-01-01T12:00:00.000",
                "max": "2023-01-10T12:00:00.000",
                "random": None  # we have 2 resulting rows, can be either
            },
        }
    },
    "Number": {
        "attr": "calories",
        "value": "234",
        "expected": {
            "__eq__": {
                "min": "234",
                "max": "234",
                "random": "234"
            },
            "__ne__": {
                "min": "-1",
                "max": "790",
                "random": None  # we have 2 resulting rows, can be either
            },
            "__gt__": {
                "min": "790",
                "max": "790",
                "random": None  # we have 2 resulting rows, can be either
            },
            "__ge__": {
                "min": "234",
                "max": "790",
                "random": None  # we have 2 resulting rows, can be either
            },
            "__lt__": {
                "min": "-1",
                "max": "-1",
                "random": "-1"
            },
            "__le__": {
                "min": "-1",
                "max": "234",
                "random": None  # we have 2 resulting rows, can be either
            },
        }
    },
    "Text": {
        "attr": "activityName",
        "value": "Sport",
        "expected": {
            "__eq__": {
                "min": "Sport",
                "max": "Sport",
                "random": "Sport"
            },
            "__ne__": {
                "min": "Walk",
                "max": "Outdoor Bike",
                "random": None  # we have 2 resulting rows, can be either
            },
            "__contains__": {
                "min": "Sport",
                "max": "Sport",
                "random": "Sport"  # we have 2 resulting rows, can be either
            },
            "__not_contains__": {
                "min": "Walk",
                "max": "Outdoor Bike",
                "random": None  # we have 2 resulting rows, can be either
            },
            "startswith": {
                "min": "Sport",
                "max": "Sport",
                "random": "Sport"  # we have 2 resulting rows, can be either
            },
            "endswith": {
                "min": "Sport",
                "max": "Sport",
                "random": "Sport"  # we have 2 resulting rows, can be either
            },
            "regexp": {
                "min": "Sport",
                "max": "Sport",
                "random": "Sport"  # we have 2 resulting rows, can be either
            },
        }
    }
}

operator_mappings = {
    "Date": [
        {
            "label": "api.custom_variables.filters.operators.date.is",
            "value": "__eq__"
        },
        {
            "label": "api.custom_variables.filters.operators.date.is_not",
            "value": "__ne__"
        },
        {
            "label": "api.custom_variables.filters.operators.date.is_after",
            "value": "__gt__"
        },
        {
            "label": "api.custom_variables.filters.operators.date.is_on_or_after",
            "value": "__ge__"
        },
        {
            "label": "api.custom_variables.filters.operators.date.is_before",
            "value": "__lt__"
        },
        {
            "label": "api.custom_variables.filters.operators.date.is_on_or_before",
            "value": "__le__"
        }
    ],
    "Number": [
        {
            "label": "api.custom_variables.filters.operators.number.is",
            "value": "__eq__"
        },
        {
            "label": "api.custom_variables.filters.operators.number.is_not",
            "value": "__ne__"
        },
        {
            "label": "api.custom_variables.filters.operators.number.is_greater_than",
            "value": "__gt__"
        },
        {
            "label": "api.custom_variables.filters.operators.number.is_greater_than_or_equal_to",
            "value": "__ge__"
        },
        {
            "label": "api.custom_variables.filters.operators.number.is_less_than",
            "value": "__lt__"
        },
        {
            "label": "api.custom_variables.filters.operators.number.is_less_than_or_equal_to",
            "value": "__le__"
        }
    ],
    "Text": [
        {
            "label": "api.custom_variables.filters.operators.text.is",
            "value": "__eq__"
        },
        {
            "label": "api.custom_variables.filters.operators.text.is_not",
            "value": "__ne__"
        },
        {
            "label": "api.custom_variables.filters.operators.text.contains",
            "value": "__contains__"
        },
        {
            "label": "api.custom_variables.filters.operators.text.does_not_contain",
            "value": "__not_contains__"
        },
        {
            "label": "api.custom_variables.filters.operators.text.begins_with",
            "value": "startswith"
        },
        {
            "label": "api.custom_variables.filters.operators.text.ends_with",
            "value": "endswith"
        },
        {
            "label": "api.custom_variables.filters.operators.text.regexp",
            "value": "regexp"
        }
    ]
}

selection_operators = ["min", "max", "random"]


def get_scenarios():
    scenarios = []
    # For each DataType
    for data_type, ops in operator_mappings.items():
        example_attr = example_values[data_type].get("attr")
        example_value = example_values[data_type].get("value")

        # For each operator for the DataType
        for op in ops:
            op_value = op["value"]

            # For each selection operator
            for sel in selection_operators:
                label = (f"Scenario: Filter {data_type} using {op_value} with value {example_value}, select the {sel} "
                         f"activity")
                expected = example_values[data_type]["expected"][op_value][sel]
                scenarios.append(
                    (
                        label,
                        [{"attr": example_attr, "operator": op_value, "value": example_value}],
                        {"attr": "originalStartTime", "operator": sel},
                        {
                            "attr": example_attr,
                            "value": expected,
                        }  # The expected_data_to_upload will need to be manually added or computed
                    )
                )
    return scenarios
