import os
import gzip
import json

from ..config.noaa import STATIONS
from ..config.secrets import NOAA_API_TOKEN
from ..config.app import DATA_ROOT
from ..adapters.noaa import NoaaAdapter

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

    def max_temps_by_year(self, year):
        max_temps = []
        for record in self.json_records_by_year(year):
            datatype = record.get('datatype')
            if datatype == 'TMAX':
                max_temps.append(record)
        return max_temps

    def json_path_by_year(self, year):
        return f'{DATA_ROOT}/noaa/json/{self.noaa_id}-{year}.json'

    def json_zpath_by_year(self, year):
        return f'{self.json_path_by_year(year)}.gz'
