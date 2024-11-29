import os
import gzip
import json
import statistics
from datetime import date
from functools import cached_property

from ..config.noaa import STATIONS
from ..config.secrets import NOAA_API_TOKEN
from ..config.app import DATA_ROOT
from ..adapters.noaa import NoaaAdapter
from ..models.annual_station_summary import AnnualStationSummary


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
    def api_id(self):
        return f'GHCND:{self.noaa_id}'

    @cached_property
    def annual_summaries(self):
        summaries = []
        this_year = date.today().year
        for year in range(self.start_year, this_year+1):
            summary = AnnualStationSummary(self, year)
            summaries.append(summary)
        return summaries

    def daily_summaries_by_doy(self, day_of_year):
        daily_summaries = []
        for annual_summary in self.annual_summaries:
            daily_summary = annual_summary.daily_summary_by_doy(day_of_year)
            daily_summaries.append(daily_summary)
        return daily_summaries

    def persist_json_records_by_year(self, year):
        zpath = self.json_zpath_by_year(year)

        if os.path.exists(zpath):
            print(f"{year}: {zpath} exists")
            return self.json_records_by_year(year)
        else:
            data = self.noaa.get_json_records_by_year(self.api_id, year)
            print(f"{year}: writing to {zpath}")
            with gzip.open(zpath, 'wt', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

        return data

    def json_records_by_year(self, year):
        zpath = self.json_zpath_by_year(year)
        with gzip.open(zpath, 'rt', encoding='utf-8') as f:
                return json.load(f)

    def avg_max_temp_by_doy(self, day_of_year):
        daily_reports = self.daily_summaries_by_doy(day_of_year)
        max_temps = [report.max_temp for report in daily_reports if report.max_temp != None]
        return statistics.mean(max_temps)

    def max_temp_by_doy(self, day_of_year):
        daily_reports = self.daily_summaries_by_doy(day_of_year)
        valid_reports = [report for report in daily_reports if report.max_temp != None]
        sorted_reports = sorted(valid_reports, key=lambda r: (r.max_temp, r.year), reverse=True)
        return sorted_reports[0]

    def json_path_by_year(self, year):
        return f'{DATA_ROOT}/noaa/json/{self.noaa_id}-{year}.json'

    def json_zpath_by_year(self, year):
        return f'{self.json_path_by_year(year)}.gz'
