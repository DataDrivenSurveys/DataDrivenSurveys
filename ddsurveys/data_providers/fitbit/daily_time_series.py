#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2024-07-08 16:18

@author: Lev Velykoivanenko (lev.velykoivanenko@unil.ch)
"""
from datetime import datetime
from typing import Any, Hashable, Callable

from .api_response_dicts import ActivityTimeSeriesDayDict, ActivityTimeSeriesResponseDict


class GroupingFunctions:
    @staticmethod
    def by_calendar_week(date_str: str) -> Hashable:
        calendar = datetime.strptime(date_str, "%Y-%m-%d").isocalendar()
        return calendar.year, calendar.week


GroupedTimeSeriesData = dict[Hashable, list[Any]]
ConvertedTimeSeriesData = dict[Hashable, int | float]


def group_time_series(
    data: ActivityTimeSeriesResponseDict,
    grouping_function: Callable[[str], Hashable]
) -> GroupedTimeSeriesData:
    grouped_stats = {}
    for time_series in data.values():
        for activity_stats in time_series:
            grouping_key = grouping_function(activity_stats["dateTime"])
            if grouping_key not in grouped_stats:
                grouped_stats[grouping_key] = []
            grouped_stats[grouping_key].append(activity_stats["value"])
    return grouped_stats


def merge_time_series(data: GroupedTimeSeriesData | list[GroupedTimeSeriesData]) -> GroupedTimeSeriesData:
    if isinstance(data, dict):
        return data

    merged_data = {}
    for data_ in data:
        for key, values in data_.items():
            if key not in merged_data:
                merged_data[key] = []
            merged_data[key].extend(values)
    return merged_data


def merge_group_time_series(
    data: ActivityTimeSeriesResponseDict,
    grouping_function: Callable[[datetime], Hashable],
) -> GroupedTimeSeriesData:
    return merge_time_series(group_time_series(data, grouping_function))


class AggregationFunctions:

    @staticmethod
    def sum(data: GroupedTimeSeriesData, convert: bool = True, to_type: Callable = int) -> ConvertedTimeSeriesData:
        if convert:
            return {
                key: sum(values)
                for key, values in {
                    key: [to_type(value) for value in values]
                    for key, values in data.items()
                }.items()
            }
        else:
            return {
                key: sum(values)
                for key, values in {
                    key: [value for value in values]
                    for key, values in data.items()
                }.items()
            }


