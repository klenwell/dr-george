import os
import gzip
import json
import statistics
from datetime import date
from functools import cached_property

from ..config.noaa import STATIONS
from ..config.secrets import NOAA_API_TOKEN
from ..config.app import DATA_ROOT, GH_PAGES_ROOT, path_join
from ..adapters.noaa import NoaaAdapter
from ..models.annual_station_summary import AnnualStationSummary, DailyStationSummary
from ..libs.calendar import abs_day_nums_in_year, abs_day_num_to_date


class WeatherStation:
    def __init__(self, id_key):
        self.id_key = id_key
        self.noaa = NoaaAdapter(NOAA_API_TOKEN)

    @property
    def config(self):
        return STATIONS[self.id_key]

    @property
    def noaa_id(self):
        return self.config['noaa_id']

    @property
    def start_year(self):
        return int(self.config['start_year'])

    @property
    def end_year(self):
        return self.config.get('end_year', date.today().year)

    @property
    def api_id(self):
        return f'GHCND:{self.noaa_id}'

    @property
    def years(self):
        return range(self.start_year, self.end_year+1)

    @property
    def mean_end_year(self):
        """Last year in the mean: the year before the current one.

        The current calendar year is still filling in, so it's left out of
        the mean. Earlier years with gaps are still averaged day by day.
        """
        return min(self.end_year, date.today().year - 1)

    @property
    def mean_years(self):
        return range(self.start_year, self.mean_end_year+1)

    @cached_property
    def dates(self):
        dates = []
        for day_num in abs_day_nums_in_year():
            dated = abs_day_num_to_date(self.year, day_num)
            dates.append(dated)
        return dates

    @cached_property
    def annual_summaries_by_year(self):
        summaries_map = {}
        for year in self.years:
            summary = AnnualStationSummary(self, year)
            summaries_map[year] = summary
        return summaries_map

    @cached_property
    def annual_summaries(self):
        return sorted(self.annual_summaries_by_year.values(), key=lambda s: s.year)

    @cached_property
    def daily_mean_reports(self):
        reports = []
        years = self.mean_years
        for day_num in abs_day_nums_in_year():
            max_temp = self.avg_max_temp_by_doy(day_num, years)
            min_temp = self.avg_min_temp_by_doy(day_num, years)
            precip = self.avg_rain_by_doy(day_num, years)
            dated = abs_day_num_to_date(self.mean_end_year, day_num)
            report = DailyStationSummary(self, dated, max_temp, min_temp, precip)
            reports.append(report)
        return reports

    def download_noaa_data_by_year(self, year, force=False):
        """Download a year's NOAA records and save them as gzipped JSON.

        An existing file is reused, except for the current year (which is
        still filling in) or when force is True. The new file is written to
        a temp path and renamed into place, so a failed fetch or write never
        damages an existing file.
        """
        zpath = self.json_zpath_by_year(year)

        if os.path.exists(zpath) and year != self.end_year and not force:
            print(f"{year}: {zpath} exists")
            return self.json_records_by_year(year)

        data = self.noaa.get_json_records_by_year(self.api_id, year)
        print(f"{year}: writing to {zpath}")

        tmp_path = f"{zpath}.tmp"
        try:
            with gzip.open(tmp_path, 'wt', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            os.replace(tmp_path, zpath)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

        return data

    def export_summary_to_json(self, year):
        summary = self.annual_summaries_by_year[year]
        json_file = f"{self.noaa_id}-{year}.json"
        pages_sub_dir = self.id_key.replace("_", "-")
        json_path = path_join(GH_PAGES_ROOT, pages_sub_dir, 'data', json_file)

        json_data = {
            'noaa_id': self.noaa_id,
            'year': year,
            'daily': [dr.to_dict() for dr in summary.daily_reports]
        }

        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)

        return json_path

    def export_means_to_json(self):
        json_file = f"{self.noaa_id}-mean.json"
        pages_sub_dir = self.id_key.replace("_", "-")
        json_path = path_join(GH_PAGES_ROOT, pages_sub_dir, 'data', json_file)

        json_data = {
            'noaa_id': self.noaa_id,
            'year': 'mean',
            'start_year': self.start_year,
            'end_year': self.mean_end_year,
            'daily': [dr.to_dict() for dr in self.daily_mean_reports]
        }

        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)

        return json_path


    def daily_summaries_by_doy(self, day_of_year, years=None):
        """Each year's summary for one day of the year. years limits which
        years are included (default: all of them)."""
        daily_summaries = []
        for annual_summary in self.annual_summaries:
            if years is not None and annual_summary.year not in years:
                continue
            daily_summary = annual_summary.daily_summary_by_doy(day_of_year)
            daily_summaries.append(daily_summary)
        return daily_summaries

    def has_raw_data(self, year):
        return os.path.exists(self.json_zpath_by_year(year))

    def json_records_by_year(self, year):
        zpath = self.json_zpath_by_year(year)
        with gzip.open(zpath, 'rt', encoding='utf-8') as f:
                return json.load(f)

    def avg_max_temp_by_doy(self, day_of_year, years=None):
        daily_reports = self.daily_summaries_by_doy(day_of_year, years)
        max_temps = [report.max_temp for report in daily_reports if report.max_temp != None]
        return statistics.mean(max_temps)

    def max_temp_by_doy(self, day_of_year):
        daily_reports = self.daily_summaries_by_doy(day_of_year)
        valid_reports = [report for report in daily_reports if report.max_temp != None]
        sorted_reports = sorted(valid_reports, key=lambda r: (r.max_temp, r.year), reverse=True)
        return sorted_reports[0]

    def avg_min_temp_by_doy(self, day_of_year, years=None):
        daily_reports = self.daily_summaries_by_doy(day_of_year, years)
        max_temps = [report.min_temp for report in daily_reports if report.min_temp != None]
        return statistics.mean(max_temps)

    def avg_rain_by_doy(self, day_of_year, years=None):
        daily_reports = self.daily_summaries_by_doy(day_of_year, years)
        rain_amts = [dr.precipitation for dr in daily_reports if dr.precipitation != None]
        return statistics.mean(rain_amts)

    def max_rain_by_year(self, year):
        summary = self.annual_summaries_by_year[year]
        valid_reports = [dr for dr in summary.daily_reports if dr.precipitation != None]
        sorted_reports = sorted(valid_reports, key=lambda r: r.precipitation, reverse=True)
        return sorted_reports[0]

    def json_path_by_year(self, year):
        return f'{DATA_ROOT}/noaa/{self.id_key}/{self.noaa_id}-{year}.json'

    def json_zpath_by_year(self, year):
        return f'{self.json_path_by_year(year)}.gz'
