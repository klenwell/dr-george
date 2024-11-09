import requests


BASE_URL = 'https://www.ncei.noaa.gov/cdo-web/api/v2'


class NoaaAdapter:
    @property
    def url(self):
        return  f"{BASE_URL}/data"

    def __init__(self, api_token):
        self.token = api_token

    def get_tmax_by_year(self, station_id, year):
        start_date = f'{year}-01-01'
        end_date = f'{year}-12-31'

        headers = {
            'token': self.token
        }

        params = {
            'datasetid': 'GHCND',
            'stationid': station_id,
            'startdate': start_date,
            'enddate': end_date,
            'limit': 1000,
            'datatypeid': 'TMAX',  # Daily Maximum Temperature
            'units': 'standard'  # Fahrenheit
        }

        response = requests.get(self.url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()['results']
        return data
