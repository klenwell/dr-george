from functools import cached_property
from datetime import datetime, date, timedelta

from ..config.noaa import DATE_FORMAT


class AnnualStationSummary:
    def __init__(self, station, year):
        self.station = station
        self.year = year

    @cached_property
    def tmax_data(self):
        return self.station.tmax_data_by_year(self.year)

    @cached_property
    def tmax_data(self):
        return self.station.tmax_data_by_year(self.year)

    @cached_property
    def tmax_metadata(self):
        return self.tmax_data['metadata']['resultset']

    @cached_property
    def tmax_results(self):
        return self.tmax_data['results']

    @cached_property
    def tmax_dated_results(self):
        dated_results = {}
        for result in self.tmax_results:
            result_date = self.date_str_to_date(result['date'])
            dated_results[result_date] = result
        return dated_results

    @cached_property
    def dates(self):
        return sorted(self.tmax_dated_results.keys())

    @cached_property
    def doy_values(self):
        day_values = {}
        for day_num in self.days_of_leap_year:
            dated = self.day_of_leap_year_to_date(day_num)
            value = self.tmax_dated_results.get(dated)
            day_values[day_num] = value
        return day_values

    @property
    def days_of_leap_year(self):
        return range(1, 367)

    @property
    def days_in_year(self):
        return 366 if self.has_leap_day() else 365

    @property
    def dates_missing(self):
        missing_dates = []
        for day_num in self.days_of_leap_year:
            value = self.doy_values[day_num]
            if not value:
                missing_date = self.day_of_leap_year_to_date(day_num)
                if missing_date:
                    missing_dates.append(missing_date)
        return missing_dates

    def has_leap_day(self):
        leap_day_num = 60
        dated = self.day_of_year_to_date(leap_day_num)
        return dated.month == 2

    def day_of_year_to_date(self, doy):
        return date(self.year, 1, 1) + timedelta(days=doy - 1)

    def day_of_leap_year_to_date(self, day_of_leap_year):
        leap_day_num = 60

        if self.has_leap_day():
            day_num = day_of_leap_year
        elif day_of_leap_year < leap_day_num:
            day_num = day_of_leap_year
        elif day_of_leap_year == leap_day_num:
            return None
        else:
            day_num = day_of_leap_year - 1

        return self.day_of_year_to_date(day_num)

    def date_str_to_date(self, date_str):
        return datetime.strptime(date_str, DATE_FORMAT).date()
