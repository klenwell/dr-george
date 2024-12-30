from functools import cached_property
from decimal import Decimal
import statistics

from ..config.noaa import DATE_FORMAT
from ..models.daily_station_summary import DailyStationSummary
from ..libs.calendar import date_str_to_date, abs_day_nums_in_year, abs_day_num_to_date


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
    def min_temp_records(self):
        return self.extract_records_by_datatype('TMIN')

    @cached_property
    def precipitation_records(self):
        return self.extract_records_by_datatype('PRCP')

    @cached_property
    def dated_max_temps(self):
        dated_values = {}
        for record in self.max_temp_records:
            result_date = date_str_to_date(record['date'], DATE_FORMAT)
            dated_values[result_date] = Decimal(record['value'])
        return dated_values

    @cached_property
    def dated_min_temps(self):
        dated_values = {}
        for record in self.min_temp_records:
            result_date = date_str_to_date(record['date'], DATE_FORMAT)
            dated_values[result_date] = Decimal(record['value'])
        return dated_values

    @cached_property
    def dated_precipitation(self):
        dated_values = {}
        for record in self.precipitation_records:
            result_date = date_str_to_date(record['date'], DATE_FORMAT)
            dated_values[result_date] = Decimal(record['value'])
        return dated_values

    @cached_property
    def daily_reports(self):
        reports = []
        for day_num in abs_day_nums_in_year():
            dated = abs_day_num_to_date(self.year, day_num)
            max_temp = self.dated_max_temps.get(dated)
            min_temp = self.dated_min_temps.get(dated)
            precip = self.dated_precipitation.get(dated)
            report = DailyStationSummary(self.station, dated, max_temp, min_temp, precip)
            reports.append(report)
        return reports

    @property
    def daily_precipitation_reports(self):
        return [dr for dr in self.daily_reports if dr.precipitation != None]

    @property
    def daily_tmax_reports(self):
        return [dr for dr in self.daily_reports if dr.max_temp != None]

    @property
    def daily_tmin_reports(self):
        return [dr for dr in self.daily_reports if dr.min_temp != None]

    @property
    def total_precipitation(self):
        return sum([dr.precipitation for dr in self.daily_precipitation_reports])

    @property
    def avg_max_temp(self):
        return statistics.mean([dr.max_temp for dr in self.daily_tmax_reports])

    @property
    def avg_min_temp(self):
        return statistics.mean([dr.min_temp for dr in self.daily_tmin_reports])

    def daily_summary_by_doy(self, day_of_year):
        i = day_of_year - 1
        return self.daily_reports[i]

    def extract_records_by_datatype(self, datatype):
        records = []
        for record in self.json_results:
            record_type = record.get('datatype')
            if record_type == datatype:
                records.append(record)
        return records

    def __repr__(self):
        id = self.station.id_key
        y = self.year
        hi = self.avg_max_temp
        lo = self.avg_min_temp
        rain = self.total_precipitation
        return f"<Annual {id} {y} avg_hi={hi:.1f} avg_lo={lo:.1f} rain={rain:.1f}>"
