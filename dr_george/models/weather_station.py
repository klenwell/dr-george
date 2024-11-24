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
    def api_id(self):
        return f'GHCND:{self.noaa_id}'

    def persist_tmax_by_year(self, year):
        zpath = self.tmax_json_zpath(year)

        if os.path.exists(zpath):
            print(f"{year}: {zpath} exists")
            return self.tmax_data_by_year(year)
        else:
            data = self.noaa.get_tmax_by_year(self.api_id, year)
            print(f"{year}: writing to {zpath}")
            with gzip.open(zpath, 'wt', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

        return data

    def tmax_data_by_year(self, year):
        zpath = self.tmax_json_zpath(year)
        with gzip.open(zpath, 'rt', encoding='utf-8') as f:
                return json.load(f)

    def tmax_json_path(self, year):
        return f'{DATA_ROOT}/noaa/tmax/{self.noaa_id}-{year}.json'

    def tmax_json_zpath(self, year):
        return f'{self.tmax_json_path(year)}.gz'
