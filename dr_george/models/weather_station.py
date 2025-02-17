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
    def end_year(self):
        return self.config.get('end_year', date.today().year)

    @property
    def api_id(self):
        return f'GHCND:{self.noaa_id}'

    @property
    def years(self):
        return range(self.start_year, self.end_year+1)

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

    def download_noaa_data_by_year(self, year):
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

    def daily_summaries_by_doy(self, day_of_year):
        daily_summaries = []
        for annual_summary in self.annual_summaries:
            daily_summary = annual_summary.daily_summary_by_doy(day_of_year)
            daily_summaries.append(daily_summary)
        return daily_summaries

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

    def max_rain_by_year(self, year):
        summary = self.annual_summaries_by_year[year]
        valid_reports = [dr for dr in summary.daily_reports if dr.precipitation != None]
        sorted_reports = sorted(valid_reports, key=lambda r: r.precipitation, reverse=True)
        return sorted_reports[0]

    def json_path_by_year(self, year):
        return f'{DATA_ROOT}/noaa/json/{self.noaa_id}-{year}.json'

    def json_zpath_by_year(self, year):
        return f'{self.json_path_by_year(year)}.gz'
