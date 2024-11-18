import requests


BASE_URL = 'https://www.ncei.noaa.gov/cdo-web/api/v2'


class NoaaAdapter:
    @property
    def url(self):
        return  f"{BASE_URL}/data"

    def __init__(self, api_token):
        self.token = api_token

    def get_dataset(self, station_id, data_type_id, start_date, end_date):
        headers = {
            'token': self.token
        }

        params = {
            'datasetid': 'GHCND',
            'stationid': station_id,
            'startdate': start_date,
            'enddate': end_date,
            'limit': 1000,
            'datatypeid': data_type_id,
            'units': 'standard'  # Fahrenheit
        }

        response = requests.get(self.url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()

    def get_tmax_by_year(self, station_id, year):
        data_type_id = 'TMAX'
        start_date = f'{year}-01-01'
        end_date = f'{year}-12-31'

        return self.get_dataset(station_id, data_type_id, start_date, end_date)
