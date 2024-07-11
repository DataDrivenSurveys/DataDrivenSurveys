#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime
"""
activities_frequent
[{'activityId': 17151, 'calories': 600, 'description': 'Walking less than 2 mph, strolling very slowly', 'distance': 1.86, 'duration': 1800000, 'name': 'Walk'}, {'activityId': 1010, 'calories': 700, 'description': 'Very Leisurely - Less than 10 mph', 'distance': 9.94, 'duration': 2700000, 'name': 'Bike'}, {'activityId': 12030, 'calories': 1000, 'description': 'Running - 5 mph (12 min/mile)', 'distance': 3.11, 'duration': 3600000, 'name': 'Run'}]  
"""
fitbit_mock_data = {
    "user_profile": {
        "aboutMe": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        "age": 30,
        "ambassador": False,
        "autoStrideEnabled": True,
        "avatar": "https://example.com/avatar.jpg",
        "avatar150": "https://example.com/avatar150.jpg",
        "avatar640": "https://example.com/avatar640.jpg",
        "averageDailySteps": 8000,
        "challengesBeta": False,
        "clockTimeDisplayFormat": "24hour",
        "country": "US",
        "corporate": False,
        "corporateAdmin": False,
        "dateOfBirth": "1993-01-01",
        "displayName": "JohnDoe123",
        "displayNameSetting": "displayName",
        "distanceUnit": "km",
        "encodedId": "ABCD1234",
        "features": {
            "exerciseGoal": True
        },
        "firstName": "John",
        "foodsLocale": "en_US",
        "fullName": "John Doe",
        "gender": "MALE",
        "glucoseUnit": "mg/dL",
        "height": 175,  # in centimeters
        "heightUnit": "cm",
        "isBugReportEnabled": False,
        "isChild": False,
        "isCoach": False,
        "languageLocale": "en_US",
        "lastName": "Doe",
        "legalTermsAcceptRequired": True,
        "locale": "en_US",
        "memberSince": "2018-05-05",
        "mfaEnabled": False,
        "offsetFromUTCMillis": -18000000,  # equivalent to UTC-5 hours
        "sdkDeveloper": False,
        "sleepTracking": True,
        "startDayOfWeek": "Monday",
        "state": "NY",
        "strideLengthRunning": 1.2,  # in meters
        "strideLengthRunningType": "default",
        "strideLengthWalking": 0.8,  # in meters
        "strideLengthWalkingType": "default",
        "swimUnit": "m",
        "temperatureUnit": "Celsius",
        "timezone": "America/New_York",
        "topBadges": [
            {"id": 1, "name": "10k steps", "date": "2020-01-01"},
            {"id": 2, "name": "Marathon", "date": "2019-01-01"}
        ],
        "waterUnit": "ml",
        "waterUnitName": "milliliter",
        "weight": 70,  # in kilograms
        "weightUnit": "kg"
    },
    "activities_favorite": [
        {
            "activityId": 15680,
            "description": "",
            "mets": 6,
            "name": "Tennis, doubles"
        }
    ],
    "activities_frequent": [
        {
            "activityId": 90013,
            "calories": -1,
            "description": "Walking less than 2 mph, strolling very slowly",
            "distance": 1.61,
            "duration": 1178000,
            "originalStartTime": "2023-01-01T12:00:00.000",
            "name": "Walk"
        },
        {
            "activityId": 15000,
            "calories": 234,
            "description": "",
            "distance": 0,
            "duration": 1228000,
            "originalStartTime": "2023-01-10T12:00:00.000",
            "name": "Sport"
        },
        {
            "activityId": 1071,
            "calories": 790,
            "description": "",
            "distance": 0,
            "duration": 973000,
            "originalStartTime": "2023-01-15T12:00:00.000",
            "name": "Outdoor Bike"
        }
    ],
    "activity_logs": {
        "activities": [
            {
                "activityId": 90013,
                "calories": -1,
                "description": "Walking less than 2 mph, strolling very slowly",
                "distance": 1.61,
                "duration": 1178000,
                "originalStartTime": "2023-01-01T12:00:00.000",
                "activityName": "Walk"
            },
            {
                "activityId": 15000,
                "calories": 234,
                "description": "",
                "distance": 0,
                "duration": 1228000,
                "originalStartTime": "2023-01-10T12:00:00.000",
                "activityName": "Sport"
            },
            {
                "activityId": 1071,
                "calories": 790,
                "description": "",
                "distance": 0,
                "duration": 973000,
                "originalStartTime": "2023-01-15T12:00:00.000",
                "activityName": "Outdoor Bike"
            }
        ]
    },
    "activities_recent": [
       {
            "activityId": 90013,
            "calories": -1,
            "description": "Walking less than 2 mph, strolling very slowly",
            "distance": 1.61,
            "duration": 1178000,
            "name": "Walk"
        },
        {
            "activityId": 1071,
            "calories": 0,
            "description": "",
            "distance": 0,
            "duration": 973000,
            "name": "Outdoor Bike"
        }
    ],
    "lifetime_stats": {
        "best": {
        "total": {
            "distance": {
                "date": "2021-01-01",
                "value": 15.33423820935418
            },
            "floors": {
                "date": "2016-01-01",
                "value": 140.00000029608
            },
            "steps": {
                "date": "2021-01-01",
                "value": 30123
            }
        },
        "tracker": {
            "distance": {
                "date": "2021-01-01",
                "value": 15.33423820935418
            },
            "floors": {
                "date": "2016-01-01",
                "value": 140.00000029608
            },
            "steps": {
                "date": "2021-01-01",
                "value": 30123
            }
        }
        },
        "lifetime": {
            "total": {
                "activeScore": -1,
                "caloriesOut": -1,
                "distance": 1234,
                "floors": 9876,
                "steps": 7654321
            },
            "tracker": {
                "activeScore": -1,
                "caloriesOut": -1,
                "distance": 1234,
                "floors": 9876,
                "steps": 1234567
            }
        }
    },
    "daily_stats": {},
    "highest_daily_steps_last_6_months_date_steps": (datetime(2024, 1, 1), 10000),
    "average_weekly_heart_zone_time_last_6_months": 180,
    "average_weekly_active_time_last_6_months": 180,
    "average_weekly_activity_time_last_6_months": 180,
}

instagram_mock_data = {
    "media_count": 1234
}
