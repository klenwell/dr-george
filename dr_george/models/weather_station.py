import os
import gzip
import json

from ..config.stations import STATIONS
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
        fpath = f'{DATA_ROOT}/noaa/tmax/{self.noaa_id}-{year}.json'
        zpath = f'{fpath}.gz'

        if os.path.exists(zpath):
            print(f"{year}: {zpath} exists")
            with gzip.open(zpath, 'rt', encoding='utf-8') as f:
                data = json.load(f)

        else:
            data = self.noaa.get_tmax_by_year(self.api_id, year)
            print(f"{year}: writing to {zpath}")
            with gzip.open(zpath, 'wt', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

        return data
