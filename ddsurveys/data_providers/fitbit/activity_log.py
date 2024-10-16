#!/usr/bin/env python3
"""Created on 2024-07-09 14:50.

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pprint import pformat
from typing import TYPE_CHECKING, Literal, overload

from ddsurveys.data_providers.date_ranges import DateRanges, ensure_date, range_date

if TYPE_CHECKING:
    from ddsurveys.data_providers.fitbit.api_response_dicts import (
        ActiveZoneMinutesDict,
        ActivityDict,
        ActivityLevelDict,
        HeartRateZoneDict,
        IntervalWorkoutData,
        ManualValuesSpecifiedDict,
        SourceDict,
    )


@dataclass(slots=True)
class Activity:
    """Class representing a Fitbit activity based on the Fitbit API response."""

    # Parameter 'activityName' unfilled
    # Parameter 'activityTypeId' unfilled
    # Parameter 'calories' unfilled
    # Parameter 'duration' unfilled
    # Parameter 'lastModified' unfilled
    # Parameter 'logId' unfilled
    # Parameter 'logType' unfilled
    # Parameter 'manualValuesSpecified' unfilled
    # Parameter 'originalDuration' unfilled
    # Parameter 'originalStartTime' unfilled
    # Parameter 'startTime' unfilled

    # __slots__ = (
    #     "activeDuration",
    #     "activeZoneMinutes",
    #     "activityLevel",
    #     "activityName",
    #     "activityTypeId",
    #     "averageHeartRate",
    #     "calories",
    #     "caloriesLink",
    #     "detailsLink",
    #     "distance",
    #     "distanceUnit",
    #     "duration",
    #     "elevationGain",
    #     "hasActiveZoneMinutes",
    #     "heartRateLink",
    #     "heartRateZones",
    #     "lastModified",
    #     "logId",
    #     "logType",
    #     "manualValuesSpecified",
    #     "originalDuration",
    #     "originalStartTime",
    #     "pace",
    #     "source",
    #     "speed",
    #     "startTime",
    #     "steps",
    #     "tcxLink",
    #     "start_datetime",
    #     "start_date",
    # )

    # Values occurring in basic manual activity
    logId: int | None = None
    activityTypeId: int | None = None
    startTime: str = None
    calories: int | None = None
    distance: float | None = None
    steps: int | None = None
    speed: float | None = None
    pace: float | None = None
    duration: int | None = None
    activeDuration: int | None = None
    distanceUnit: str | None = None
    logType: Literal["auto_detected", "manual", "mobile_run", "tracker"] | None = None
    manualValuesSpecified: ManualValuesSpecifiedDict | None = None
    intervalWorkoutData: IntervalWorkoutData | None = None
    heartRateZones: HeartRateZoneDict | None = None
    activeZoneMinutes: ActiveZoneMinutesDict | None = None
    inProgress: bool | None = None
    caloriesLink: str | None = None
    lastModified: str | None = None
    originalStartTime: str | None = None
    originalDuration: int | None = None
    elevationGain: float | None = None
    hasActiveZoneMinutes: bool | None = None

    # Other possible values
    activityLevel: list[ActivityLevelDict] | None = None
    activityName: str | None = None
    averageHeartRate: int | None = None
    detailsLink: str | None = None
    heartRateLink: str | None = None
    source: SourceDict | None = None
    tcxLink: str | None = None

    # Computed values
    start_datetime: datetime = field(init=False)
    start_date: date = field(init=False)

    # def __init__(
    #     self,
    #     activeDuration: int,
    #     activityLevel: list[ActivityLevelDict],
    #     activityName: str,
    #     activityTypeId: int,
    #     calories: int,
    #     duration: int,
    #     lastModified: str,
    #     logId: int,
    #     logType: Literal["auto_detected", "manual", "mobile_run", "tracker"],
    #     manualValuesSpecified: ManualValuesSpecifiedDict,
    #     originalDuration: int,
    #     originalStartTime: str,
    #     startTime: str,
    #     averageHeartRate: int | None = None,
    #     activeZoneMinutes: ActiveZoneMinutesDict | None = None,
    #     caloriesLink: str | None = None,
    #     detailsLink: str | None = None,
    #     distance: float | None = None,
    #     distanceUnit: str | None = None,
    #     elevationGain: float | None = None,
    #     hasActiveZoneMinutes: bool | None = None,
    #     heartRateLink: str | None = None,
    #     heartRateZones: HeartRateZoneDict | None = None,
    #     pace: float | None = None,
    #     source: SourceDict | None = None,
    #     speed: float | None = None,
    #     steps: int | None = None,
    #     tcxLink: str | None = None,
    # ) -> None:
    #     # Values read from the Fitbit API
    #     self.activeDuration = activeDuration
    #     self.activeZoneMinutes = activeZoneMinutes
    #     self.activityLevel = activityLevel
    #     self.activityName = activityName
    #     self.activityTypeId = activityTypeId
    #     self.averageHeartRate = averageHeartRate
    #     self.calories = calories
    #     self.caloriesLink = caloriesLink
    #     self.detailsLink = detailsLink
    #     self.distance = distance
    #     self.distanceUnit = distanceUnit
    #     self.duration = duration
    #     self.elevationGain = elevationGain
    #     self.hasActiveZoneMinutes = hasActiveZoneMinutes
    #     self.heartRateLink = heartRateLink
    #     self.heartRateZones = heartRateZones
    #     self.lastModified = lastModified
    #     self.logId = logId
    #     self.logType = logType
    #     self.manualValuesSpecified = manualValuesSpecified
    #     self.originalDuration = originalDuration
    #     self.originalStartTime = originalStartTime
    #     self.pace = pace
    #     self.source = source
    #     self.speed = speed
    #     self.startTime = startTime
    #     self.steps = steps
    #     self.tcxLink = tcxLink
    #
    #     # Computed values
    #     self.start_datetime = datetime.fromisoformat(self.startTime)
    #     self.start_date = self.start_datetime.date()

    def __post_init__(self):
        self.start_datetime = datetime.fromisoformat(self.startTime)
        self.start_date = self.start_datetime.date()

    def __hash__(self) -> int:
        return hash(self.logId)

    def __eq__(self, other: Activity) -> bool:
        return self.logId == other.logId

    def __lt__(self, other: Activity | date | datetime) -> bool:
        if isinstance(other, Activity):
            return self.start_datetime < other.start_datetime
        if isinstance(other, date):
            return self.start_date < other
        if isinstance(other, datetime):
            return self.start_datetime < other
        return NotImplemented


class ActivityLog:
    __slots__ = (
        "date_ranges",
        # "activities",
        "id_activities",
        "date_activities",
        "type_activities",
        "name_activities",
        "_integration_last_end_date",
        "_integration_last_start_date",
    )

    activity_types: tuple[Literal["auto_detected", "manual", "mobile_run", "tracker"]] = (
        "auto_detected",
        "manual",
        "mobile_run",
        "tracker",
    )

    def __init__(self) -> None:
        self.date_ranges = DateRanges()
        # self.activities = []
        self.id_activities = {}
        self.date_activities = {}
        self.type_activities = {}
        self.name_activities = {}
        self._integration_last_end_date: date = None
        self._integration_last_start_date: date = None

    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__} with {len(self.id_activities)} activities and {len(self.date_activities)} "
            f"dates"
        )

    def __repr__(self) -> str:
        num_activities = len(self.id_activities)
        num_dates = len(self.date_activities)
        num_types = len(self.type_activities)
        num_names = len(self.name_activities)
        return (
            f"{self.__class__.__name__}(num_activities={num_activities}, num_dates={num_dates}, num_types="
            f"{num_types}, num_names={num_names})"
        )

    @overload
    def __getitem__(self, item: date) -> list[Activity]: ...

    @overload
    def __getitem__(self, item: datetime) -> list[Activity]: ...

    @overload
    def __getitem__(self, item: slice) -> list[Activity]: ...

    @overload
    def __getitem__(self, item: str) -> list[Activity]: ...

    @overload
    def __getitem__(self, item: int) -> Activity: ...

    def __getitem__(self, item):
        # Case where getting a date, datetime, or slice of date or datetime.
        if isinstance(item, datetime):
            item = item.date()
        if isinstance(item, date):
            return self.date_activities[item]
        if isinstance(item, slice):
            if not isinstance(item.start, date | datetime) or not isinstance(item.stop, date | datetime):
                msg = "Slicing is only supported for date or datetime objects."
                raise TypeError(msg)
            start, end, step = ensure_date(item.start), ensure_date(item.stop), item.step
            activities = []
            for date_ in range_date(start, end, step):
                activities.extend(self.date_activities[date_])
            return activities

        # Case where getting an activity by ID.
        if isinstance(item, int):
            return self.id_activities[item]

        # Case where getting an activity by name or type.
        if isinstance(item, str):
            if item in self.__class__.activity_types:
                return self.type_activities[item]
            if item in self.name_activities:
                return self.name_activities[item]
            msg = f"Activity with name or type '{item}' not found."
            raise KeyError(msg)

        msg = f"Unsupported index type: {type(item)}"
        raise TypeError(msg)

    def describe(self) -> str:
        dates_details = pformat({date: len(activities) for date, activities in self.date_activities.items()})
        types_details = pformat({type_: len(activities) for type_, activities in self.type_activities.items()})
        names_details = pformat({name: len(activities) for name, activities in self.name_activities.items()})
        return (
            f"{self.__class__.__name__} with {len(self.id_activities)} activities.\nActivities by date:\n"
            f"{dates_details}\nActivities by types:\n{types_details}\nActivities by names:\n{names_details}"
        )

    def integrate_activity(self, activity_data: ActivityDict) -> None:
        if activity_data["logId"] in self.id_activities:
            return  # Activity with this ID already exists in the log

        activity = Activity(**activity_data)
        # self.activities.append(activity)
        self.id_activities[activity.logId] = activity
        self.date_activities.setdefault(activity.start_datetime.date(), []).append(activity)
        self.type_activities.setdefault(activity.logType, []).append(activity)
        self.name_activities.setdefault(activity.activityName, []).append(activity)

    def integrate_activities_list(self, data: list[ActivityDict], continuous: bool = True) -> None:
        if continuous:
            self.date_ranges.add_date_range(
                datetime.fromisoformat(data[0]["startTime"]),
                datetime.fromisoformat(data[-1]["startTime"]),
            )
            end_date = datetime.fromisoformat(data[-1]["startTime"]).date()
            if self._integration_last_end_date is None or end_date > self._integration_last_end_date:
                self._integration_last_end_date = end_date
            start_date = end_date
            for activity_data in data:
                self.integrate_activity(activity_data)
                act_start_date = self.id_activities[activity_data["logId"]].start_date
                if act_start_date < start_date:
                    start_date = act_start_date

            if self._integration_last_start_date is None or start_date < self._integration_last_start_date:
                self._integration_last_start_date = start_date

            if self._integration_last_start_date + timedelta(days=1) < self._integration_last_end_date:
                self.date_ranges.add_date_range(start_date, end_date)
                self._integration_last_start_date = None
                self._integration_last_end_date = None
        else:
            for activity_data in data:
                self.integrate_activity(activity_data)

    def get_by_date(self, date: datetime) -> list[Activity]:
        return self.date_activities.get(date.date(), [])

    def get_by_type(self, activity_type: Literal["auto_detected", "manual", "mobile_run", "tracker"]) -> list[Activity]:
        return self.type_activities.get(activity_type, [])

    def get_by_name(self, activity_name: str) -> list[Activity]:
        return self.name_activities.get(activity_name, [])
