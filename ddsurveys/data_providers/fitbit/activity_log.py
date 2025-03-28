"""Created on 2024-07-09 14:50.

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pprint import pformat
from typing import TYPE_CHECKING, Literal, overload, override

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

    # Values occurring in basic manual activity
    logId: int | None = None  # noqa: N815
    activityTypeId: int | None = None  # noqa: N815
    startTime: str | None = None  # noqa: N815
    calories: int | None = None
    distance: float | None = None
    steps: int | None = None
    speed: float | None = None
    pace: float | None = None
    duration: int | None = None
    activeDuration: int | None = None  # noqa: N815
    distanceUnit: str | None = None  # noqa: N815
    logType: Literal["auto_detected", "manual", "mobile_run", "tracker"] | None = None  # noqa: N815
    manualValuesSpecified: ManualValuesSpecifiedDict | None = None  # noqa: N815
    intervalWorkoutData: IntervalWorkoutData | None = None  # noqa: N815
    heartRateZones: HeartRateZoneDict | None = None  # noqa: N815
    activeZoneMinutes: ActiveZoneMinutesDict | None = None  # noqa: N815
    inProgress: bool | None = None  # noqa: N815
    caloriesLink: str | None = None  # noqa: N815
    lastModified: str | None = None  # noqa: N815
    originalStartTime: str | None = None  # noqa: N815
    originalDuration: int | None = None  # noqa: N815
    elevationGain: float | None = None  # noqa: N815
    hasActiveZoneMinutes: bool | None = None  # noqa: N815

    # Other possible values
    activityLevel: list[ActivityLevelDict] | None = None  # noqa: N815
    activityName: str | None = None  # noqa: N815
    averageHeartRate: int | None = None  # noqa: N815
    detailsLink: str | None = None  # noqa: N815
    heartRateLink: str | None = None  # noqa: N815
    source: SourceDict | None = None
    tcxLink: str | None = None  # noqa: N815
    hasGps: bool | None = None  # noqa: N815

    # Computed values
    start_datetime: datetime = field(init=False)
    start_date: date = field(init=False)

    def __post_init__(self) -> None:
        self.start_datetime = datetime.fromisoformat(self.startTime)
        self.start_date = self.start_datetime.date()

    @override
    def __hash__(self) -> int:
        return hash(self.logId)

    @override
    def __eq__(self, other: Activity) -> bool:
        return self.logId == other.logId

    def __lt__(self, other: Activity | date | datetime) -> bool:
        if isinstance(other, Activity):
            return self.start_datetime < other.start_datetime
        if isinstance(other, datetime):
            return self.start_datetime < other
        if type(other) is date:
            return self.start_date < other
        return NotImplemented


class ActivityLog:
    __slots__: tuple[str, ...] = (
        "_integration_last_end_date",
        "_integration_last_start_date",
        "date_activities",
        "date_ranges",
        # "activities",
        "id_activities",
        "name_activities",
        "type_activities",
    )

    activity_types: tuple[Literal["auto_detected", "manual", "mobile_run", "tracker"], ...] = (
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
            if not isinstance(item.start, date | datetime) or not isinstance(
                item.stop,
                date | datetime,
            ):
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
        dates_details = pformat({
            date: len(activities) for date, activities in self.date_activities.items()
        })
        types_details = pformat({
            type_: len(activities) for type_, activities in self.type_activities.items()
        })
        names_details = pformat({
            name: len(activities) for name, activities in self.name_activities.items()
        })
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
            if (
                self._integration_last_end_date is None
                or end_date > self._integration_last_end_date
            ):
                self._integration_last_end_date = end_date
            start_date = end_date
            for activity_data in data:
                self.integrate_activity(activity_data)
                act_start_date = self.id_activities[activity_data["logId"]].start_date
                if act_start_date < start_date:
                    start_date = act_start_date

            if (
                self._integration_last_start_date is None
                or start_date < self._integration_last_start_date
            ):
                self._integration_last_start_date = start_date

            if (
                self._integration_last_start_date + timedelta(days=1)
                < self._integration_last_end_date
            ):
                self.date_ranges.add_date_range(start_date, end_date)
                self._integration_last_start_date = None
                self._integration_last_end_date = None
        else:
            for activity_data in data:
                self.integrate_activity(activity_data)

    def get_by_date(self, date: datetime) -> list[Activity]:
        return self.date_activities.get(date.date(), [])

    def get_by_type(
        self,
        activity_type: Literal["auto_detected", "manual", "mobile_run", "tracker"],
    ) -> list[Activity]:
        return self.type_activities.get(activity_type, [])

    def get_by_name(self, activity_name: str) -> list[Activity]:
        return self.name_activities.get(activity_name, [])
