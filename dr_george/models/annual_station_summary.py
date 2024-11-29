from functools import cached_property
from datetime import datetime, date, timedelta
from decimal import Decimal

from ..config.noaa import DATE_FORMAT


class AnnualStationSummary:
    def __init__(self, station, year):
        self.station = station
        self.year = year

    @cached_property
    def json_data(self):
        return self.station.json_records_by_year(self.year)

    @cached_property
    def json_metadata(self):
        return self.json_data['metadata']['resultset']

    @cached_property
    def json_results(self):
        return self.json_data['results']

    @cached_property
    def max_temp_records(self):
        return self.extract_records_by_datatype('TMAX')

    @cached_property
    def precipitation_records(self):
        return self.extract_records_by_datatype('PRCP')

    @cached_property
    def dated_max_temps(self):
        dated_values = {}
        for record in self.max_temp_records:
            result_date = self.date_str_to_date(record['date'])
            dated_values[result_date] = Decimal(record['value'])
        return dated_values

    @cached_property
    def dated_precipitation(self):
        dated_values = {}
        for record in self.precipitation_records:
            result_date = self.date_str_to_date(record['date'])
            dated_values[result_date] = Decimal(record['value'])
        return dated_values

    @cached_property
    def doy_max_temps(self):
        day_of_year_temps = {}
        for day_num in self.days_of_leap_year:
            dated = self.day_of_leap_year_to_date(day_num)
            day_of_year_temps[day_num] = self.dated_max_temps.get(dated)
        return day_of_year_temps

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
            value = self.doy_tmax_values[day_num]
            if not value:
                missing_date = self.day_of_leap_year_to_date(day_num)
                if missing_date:
                    missing_dates.append(missing_date)
        return missing_dates

    def extract_records_by_datatype(self, datatype):
        records = []
        for record in self.json_results:
            record_type = record.get('datatype')
            if record_type == datatype:
                records.append(record)
        return records

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
