#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2024-07-10 12:06

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
"""
from bisect import bisect_left, bisect_right
from datetime import date, datetime, timedelta
from typing import Generator, overload


class DateRanges:
    __slots__ = ("_start_dates", "_end_dates")

    def __init__(self):
        self._start_dates: list[date] = []
        self._end_dates: list[date] = []

    def __str__(self):
        num_ranges = len(self._start_dates)
        total_days = sum(
            (end_date - start_date).days + 1 for start_date, end_date in zip(self._start_dates, self._end_dates))
        return f"{self.__class__.__name__} with {num_ranges} ranges covering a total of {total_days} days"

    def __repr__(self):
        ranges = ", ".join(
            f"({start_date}, {end_date})" for start_date, end_date in zip(self._start_dates, self._end_dates))
        return f"{self.__class__.__name__}([{ranges}])"

    def add_date_range(self, start_date: date, end_date: date) -> None:
        start_date = ensure_date(start_date)
        end_date = ensure_date(end_date)

        # Find the index where the new range should be inserted
        index = bisect_left(self._start_dates, start_date)

        # Check if the new range overlaps with the previous range
        if index > 0 and start_date <= self._end_dates[index - 1]:
            # Merge the ranges
            self._end_dates[index - 1] = max(end_date, self._end_dates[index - 1])
        else:
            # Insert the new range into the lists
            self._start_dates.insert(index, start_date)
            self._end_dates.insert(index, end_date)

        # Check if the new range overlaps with the next range
        if index < len(self._start_dates) - 1 and end_date >= self._start_dates[index + 1]:
            # Merge the ranges
            self._end_dates[index] = max(end_date, self._end_dates[index + 1])
            del self._start_dates[index + 1]
            del self._end_dates[index + 1]

    def date_in_range(self, date_: date) -> bool:
        date = ensure_date(date_)

        # Find the index of the range that contains the date
        index = bisect_right(self._start_dates, date_)

        # Check if the date is within the range
        if index > 0 and self._end_dates[index - 1] >= date_:
            return True
        else:
            return False

    def range_in_ranges(self, start_date: date, end_date: date) -> bool:
        start_date = ensure_date(start_date)
        end_date = ensure_date(end_date)

        # Find the index of the range that contains the start date
        start_index = bisect_right(self._start_dates, start_date)

        # Check if the end date is within the same range
        if start_index > 0 and self._end_dates[start_index - 1] >= end_date:
            return True
        else:
            return False


def ensure_date(date_: datetime | date) -> date:
    if isinstance(date_, date):
        return date_
    return date_.date()


def range_date(start: date, stop: date, step: int = 1) -> Generator[date, None, None]:
    start = ensure_date(start)
    stop = ensure_date(stop)
    if step is None:
        step = 1
    delta = timedelta(days=step)

    while start < stop:
        yield start
        start += delta


def get_isoweek(date_: date | datetime) -> tuple[int, int]:
    cal = date_.isocalendar()
    return cal[0], cal[1]


def get_weeks_difference(start_date: date | datetime, end_date: date | datetime) -> int:
    start_date = ensure_date(start_date)
    end_date = ensure_date(end_date)
    return (end_date - start_date).days // 7
