#!/usr/bin/env python3
"""Created on 2024-07-08 16:15.

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
"""

__all__ = [
    # TypedDicts for daily stats summaries API Responses
    "ActiveZoneMinutesValueDict",
    "ActiveZoneMinutesDay",
    "ActiveZoneMinutesSeriesResponseDict",
    "ActivityTimeSeriesDayDict",
    "ActivityTimeSeriesResponseDict",
    # TypedDicts for Activities List API Responses
    "MinutesInHeartRateZoneDict",
    "ActiveZoneMinutesDict",
    "ActivityLevelDict",
    "ManualValuesSpecifiedDict",
    "ActivityDict",
    "ActivitiesListPaginationDict",
    "ActivitiesListResponseDict",
    # TypedDicts for Sleep API Responses
    "DeviceDict",
    # User Profile API Responses
    "UserDict",
    "UserProfileResponseDict",
    # Frequent Activities API endpoints
    "FrequentActivityDict",
    # Favorite Activities API endpoints
    "FavoriteActivityDict",
]

from typing import Literal, NotRequired, TypedDict


# TypedDicts for daily stats summaries API Responses
class ActiveZoneMinutesValueDict(TypedDict):
    activeZoneMinutes: int
    fatBurnActiveZoneMinutes: NotRequired[int]
    cardioActiveZoneMinutes: NotRequired[int]
    peakActiveZoneMinutes: NotRequired[int]


class ActiveZoneMinutesDay(TypedDict):
    dateTime: str
    value: ActiveZoneMinutesValueDict


ActiveZoneMinutesSeriesResponseDict = TypedDict(
    "ActiveZoneMinutesSeriesResponseDict", {"activities-active-zone-minutes": list[ActiveZoneMinutesDay]}
)


class ActivityTimeSeriesDayDict(TypedDict):
    dateTime: str
    value: str


ActivityTimeSeriesResponseDict = TypedDict(
    "ActivityTimeSeriesResponseDict",
    {
        "activities-activityCalories": NotRequired[list[ActivityTimeSeriesDayDict]],
        "activities-calories": NotRequired[list[ActivityTimeSeriesDayDict]],
        "activities-caloriesBMR": NotRequired[list[ActivityTimeSeriesDayDict]],
        "activities-distance": NotRequired[list[ActivityTimeSeriesDayDict]],
        "activities-elevation": NotRequired[list[ActivityTimeSeriesDayDict]],
        "activities-floors": NotRequired[list[ActivityTimeSeriesDayDict]],
        "activities-minutesSedentary": NotRequired[list[ActivityTimeSeriesDayDict]],
        "activities-minutesLightlyActive": NotRequired[list[ActivityTimeSeriesDayDict]],
        "activities-minutesFairlyActive": NotRequired[list[ActivityTimeSeriesDayDict]],
        "activities-minutesVeryActive": NotRequired[list[ActivityTimeSeriesDayDict]],
        "activities-tracker-activityCalories": NotRequired[list[ActivityTimeSeriesDayDict]],
        "activities-tracker-calories": NotRequired[list[ActivityTimeSeriesDayDict]],
        "activities-tracker-distance": NotRequired[list[ActivityTimeSeriesDayDict]],
        "activities-tracker-elevation": NotRequired[list[ActivityTimeSeriesDayDict]],
        "activities-tracker-floors": NotRequired[list[ActivityTimeSeriesDayDict]],
        "activities-tracker-minutesSedentary": NotRequired[list[ActivityTimeSeriesDayDict]],
        "activities-tracker-minutesLightlyActive": NotRequired[list[ActivityTimeSeriesDayDict]],
        "activities-tracker-minutesFairlyActive": NotRequired[list[ActivityTimeSeriesDayDict]],
        "activities-tracker-minutesVeryActive": NotRequired[list[ActivityTimeSeriesDayDict]],
        "activities-tracker-steps": NotRequired[list[ActivityTimeSeriesDayDict]],
    },
)


# TypedDicts for Activities List API Responses
class MinutesInHeartRateZoneDict(TypedDict):
    minuteMultiplier: int
    minutes: int
    order: int
    type: Literal["OUT_OF_ZONE", "FAT_BURN", "CARDIO", "PEAK"]
    zoneName: Literal["Out of Range", "Fat Burn", "Cardio", "Peak"]


class ActiveZoneMinutesDict(TypedDict):
    minutesInHeartRateZones: list[MinutesInHeartRateZoneDict]
    totalMinutes: int


class ActivityLevelDict(TypedDict):
    """A dictionary containing information about a given activity level."""

    minutes: int
    name: Literal["sedentary", "lightly", "fairly", "very"]


class HeartRateZoneDict(TypedDict):
    """A dictionary containing information about an activity's heart rate zones.
    The Heart Rate scope is required to retrieve this dictionary.
    """

    caloriesOut: int
    max: int
    min: int
    minutes: int
    name: Literal["Cardio", "Fat Burn", "Out of Range", "Peak"]


class ManualValuesSpecifiedDict(TypedDict):
    calories: bool
    distance: bool
    steps: bool


class IntervalWorkoutData(TypedDict):
    intervalSummaries: list
    numRepeats: int


class SourceDict(TypedDict):
    """A dictionary containing information about an activity's source.

    Attributes:
        id (str): The unique identifier of the source.
        name (str): The name of the source.
        trackerFeatures (list[Literal]): A list of the features supported by the source.
        type (str): The type of the source.
        url (str): The URL of the source.
    """

    id: str
    name: str
    trackerFeatures: list[Literal["CALORIES", "DISTANCE", "ELEVATION", "GPS", "HEARTRATE", "PACE", "STEPS", "VO2_MAX"]]
    type: str
    url: str


class ActivityDict(TypedDict):
    """A dictionary representing a single activity's data from the Fitbit API.

    Parts of this documentation is based on the Fitbit API documentation.

    Fitbit devices calculate the metrics using the following formulas:
        distance = steps * stride length
        pace = time(sec) / distance
        speed = distance / time(hour)

    Attributes:
        activeDuration (int): The amount of time (milliseconds) within each activityLevel.
        activeZoneMinutes (NotRequired[ActiveZoneMinutesDict]): The minutes spent in each heart rate zone.
        activityLevel (list[ActivityLevelDict]): Total number of minutes the user spent at each activity level during that activity.
        activityName (str): Name of the recorded exercise.
        activityTypeId (int): The activityName's identifier number.
        averageHeartRate (int): The average heart rate during the exercise. The Heart Rate scope is required to see this value.
        calories (int): The calories burned during the activity.
        caloriesLink (NotRequired[str]): Web API endpoint to call to get the specific calories burned for the named exercise.
        detailsLink (NotRequired[str]): An endpoint that provides additional details about the user's activity either
            manually logged on the mobile application or API, or auto-recognized by the Fitbit device.
            Activities recorded using the device's exercise app are not supported.
        distance (NotRequired[float]): The distance covered during the activity. distance = steps * stride length
        distanceUnit (NotRequired[str]): Distance units defined by the Accept-Language header.
        duration (int): The length in time (milliseconds) after the exercise was edited.
            If the exercise was not edited, the duration = originalDuration.
            This value will contain pauses during the exercise.
        elevationGain (NotRequired[float]): The elevation gain during the activity.
        hasActiveZoneMinutes (NotRequired[bool]): Indicates whether the activity has active zone minutes.
        heartRateLink (NotRequired[str]): The link to the heart rate data for the activity.
            The Heart Rate scope is required to see this value.
        lastModified (str): The timestamp (in ISO date format) when the activity was last modified.
        logId (int): The unique identifier for the activity log.
        logType (str): The type of activity log created.
        manualValuesSpecified (ManualValuesSpecifiedDict): Indicates whether manual values were specified for calories,
            distance, and steps.
        originalDuration (int): The initial length in time (milliseconds) that the exercise was recorded.
            This value will contain pauses during the exercise.
        originalStartTime (str): The initial start datetime (in ISO date format) that the exercise was recorded.
        pace (NotRequired[float]): Calculated average pace during the exercise. pace = time(sec) / distance
        source (SourceDict): The source of the activity data.
        speed (NotRequired[float]): Calculated average speed during the exercise. speed = distance / time
        startTime (str): The start time of the activity.
        steps (int): The number of steps taken during the activity.
        tcxLink (NotRequired[str]): The link to the TCX file for the activity.
    """

    activeDuration: int
    activeZoneMinutes: NotRequired[ActiveZoneMinutesDict]
    activityLevel: list[ActivityLevelDict]
    activityName: str
    activityTypeId: int
    averageHeartRate: NotRequired[int]
    calories: int
    caloriesLink: NotRequired[str]
    detailsLink: NotRequired[str]
    distance: NotRequired[float]
    distanceUnit: NotRequired[str]
    duration: int
    elevationGain: NotRequired[float]
    hasActiveZoneMinutes: NotRequired[bool]
    heartRateLink: NotRequired[str]
    heartRateZones: NotRequired[HeartRateZoneDict]
    inProgress: bool
    intervalWorkoutData: NotRequired[IntervalWorkoutData]
    lastModified: str
    logId: int
    logType: Literal["auto_detected", "manual", "mobile_run", "tracker"]
    manualValuesSpecified: ManualValuesSpecifiedDict
    originalDuration: int
    originalStartTime: str
    pace: NotRequired[float]
    source: NotRequired[SourceDict]
    speed: NotRequired[float]
    startTime: str
    steps: NotRequired[int]
    tcxLink: NotRequired[str]


class ActivitiesListPaginationDict(TypedDict):
    beforeDate: str
    limit: int
    next: str
    offset: int
    previous: str
    sort: str


class ActivitiesListResponseDict(TypedDict):
    activities: list[ActivityDict]
    pagination: ActivitiesListPaginationDict


# Device API endpoints
class DeviceDict(TypedDict):
    batteryLevel: int
    deviceVersion: str
    features: list[str]
    id: str
    lastSyncTime: str
    mac: str


# User Profile API endpoints
class TopBadge(TypedDict):
    badgeGradientEndColor: str
    badgeGradientStartColor: str
    badgeType: str
    category: str
    cheers: list
    dateTime: str
    description: str
    earnedMessage: str
    encodedId: str
    image100px: str
    image125px: str
    image300px: str
    image50px: str
    image75px: str
    marketingDescription: str
    mobileDescription: str
    name: str
    shareImage640px: str
    shareText: str
    shortDescription: str
    shortName: str
    timesAchieved: int
    value: int


class FeaturesDict(TypedDict):
    exerciseGoal: bool


class UserDict(TypedDict):
    age: int
    ambassador: bool
    autoStrideEnabled: bool
    avatar: str
    avatar150: str
    avatar640: str
    averageDailySteps: int
    challengesBeta: bool
    clockTimeDisplayFormat: str
    corporate: bool
    corporateAdmin: bool
    country: str
    dateOfBirth: str
    displayName: str
    displayNameSetting: str
    distanceUnit: str
    encodedId: str
    features: FeaturesDict
    firstName: str
    foodsLocale: str
    fullName: str
    gender: str
    glucoseUnit: str
    height: float
    heightUnit: str
    isBugReportEnabled: bool
    isChild: bool
    isCoach: bool
    languageLocale: str
    lastName: str
    legalTermsAcceptRequired: bool
    locale: str
    memberSince: str
    mfaEnabled: bool
    offsetFromUTCMillis: int
    sdkDeveloper: bool
    sleepTracking: str
    startDayOfWeek: str
    strideLengthRunning: float
    strideLengthRunningType: str
    strideLengthWalking: float
    strideLengthWalkingType: str
    swimUnit: str
    temperatureUnit: str
    timezone: str
    topBadges: list[TopBadge]
    visibleUser: bool
    waterUnit: str
    waterUnitName: str
    weight: float
    weightUnit: str


class UserProfileResponseDict(TypedDict):
    user: UserDict


# Frequent Activities API endpoints
class FrequentActivityDict(TypedDict):
    activityId: int
    calories: int
    description: str
    distance: float
    duration: int
    name: str


# Favorite Activities API endpoints
class FavoriteActivityDict(TypedDict):
    activityId: int
    description: str
    mets: int
    name: str
