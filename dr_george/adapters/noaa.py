import requests


BASE_URL = 'https://www.ncei.noaa.gov/cdo-web/api/v2'
DATA_TYPES_ID = 'TMAX, TMIN, PRCP'


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
            'offset': 1,
            'datatypeid': data_type_id,
            'units': 'standard'  # Fahrenheit
        }

        # Make paginated requests
        stitched_data = None

        # Source: https://chatgpt.com/share/67b3d0ab-db38-800e-ac5e-b6990e15eb3d
        while True:
            response = requests.get(self.url, headers=headers, params=params)
            response.raise_for_status()

            data = response.json()

            if not stitched_data:
                stitched_data = data
            else:
                stitched_data['results'].extend(data.get('results', []))

            # Check if more data exists
            resultset = data.get("metadata", {}).get("resultset", {})
            total_records = resultset.get("count", 0)
            offset = resultset.get("offset", 1)
            limit = resultset.get("limit", 1000)

            # Break if we've fetched all records
            if offset + limit > total_records:
                break

            # Update the offset for the next request
            params['offset'] = offset + limit

        return stitched_data

    def get_json_records_by_year(self, station_id, year):
        data_type_id = DATA_TYPES_ID
        start_date = f'{year}-01-01'
        end_date = f'{year}-12-31'

        return self.get_dataset(station_id, data_type_id, start_date, end_date)
