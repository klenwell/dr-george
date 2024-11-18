from ..config.stations import STATIONS
from ..config.secrets import NOAA_API_TOKEN
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

    def get_tmax_by_year(self, year, cache=True):
        cache_key = 'TBA'

        if cache:
            cached_data = self.get_cache(cache_key)
            if cached_data:
                return cached_data

        data = self.noaa.get_tmax_by_year(self.api_id, year)

        if cache:
            self.cache_data(cache_key, data)

        return data
