"""
Tests for downloading NOAA data: skip-or-refresh logic and the --years option.

NOAA is never called: the station's adapter is replaced with a stub, and
DATA_ROOT points at a temp directory.
"""
import gzip
import json
import os

import pytest
from requests.exceptions import HTTPError

import dr_george.models.weather_station as ws_module
from dr_george.models.weather_station import WeatherStation
from dr_george.controllers.base import Base
from dr_george.core.exc import DrGeorgeError
from dr_george.main import DrGeorgeTest


class StubNoaa:
    """Stands in for NoaaAdapter. Records requested years."""
    def __init__(self, fail=False):
        self.fail = fail
        self.calls = []

    def get_json_records_by_year(self, station_id, year):
        self.calls.append(year)
        if self.fail:
            raise HTTPError('503 Service Unavailable')
        return {'metadata': {'resultset': {'count': 1}},
                'results': [{'date': f'{year}-01-01T00:00:00', 'source': 'stub'}]}


@pytest.fixture
def station(tmp_path, monkeypatch):
    monkeypatch.setattr(ws_module, 'DATA_ROOT', str(tmp_path))
    (tmp_path / 'noaa' / 'santa_ana').mkdir(parents=True)
    st = WeatherStation('santa_ana')
    st.noaa = StubNoaa()
    return st


def write_existing(station, year, source='existing'):
    zpath = station.json_zpath_by_year(year)
    with gzip.open(zpath, 'wt', encoding='utf-8') as f:
        json.dump({'results': [{'source': source}]}, f)
    return zpath


def read_source(zpath):
    with gzip.open(zpath, 'rt', encoding='utf-8') as f:
        return json.load(f)['results'][0]['source']


# WeatherStation.download_noaa_data_by_year
def test_existing_past_year_is_kept_without_force(station):
    zpath = write_existing(station, 2025)

    station.download_noaa_data_by_year(2025)

    assert station.noaa.calls == []
    assert read_source(zpath) == 'existing'


def test_existing_past_year_is_replaced_with_force(station):
    zpath = write_existing(station, 2025)

    station.download_noaa_data_by_year(2025, force=True)

    assert station.noaa.calls == [2025]
    assert read_source(zpath) == 'stub'


def test_current_year_is_always_fetched(station):
    zpath = write_existing(station, station.end_year)

    station.download_noaa_data_by_year(station.end_year)

    assert station.noaa.calls == [station.end_year]
    assert read_source(zpath) == 'stub'


def test_missing_year_is_fetched(station):
    station.download_noaa_data_by_year(1984)

    assert station.noaa.calls == [1984]
    assert read_source(station.json_zpath_by_year(1984)) == 'stub'


def test_failed_fetch_leaves_existing_file_unchanged(station):
    zpath = write_existing(station, 2025)
    station.noaa = StubNoaa(fail=True)

    with pytest.raises(HTTPError):
        station.download_noaa_data_by_year(2025, force=True)

    assert read_source(zpath) == 'existing'
    assert not os.path.exists(f'{zpath}.tmp')


# Base._download_years (option handling)
def test_no_years_option_downloads_all_years_without_force(station):
    years, force = Base._download_years(station, None)

    assert years == list(station.years)
    assert years[0] == 1917
    assert force is False


def test_years_option_forces_only_those_years(station):
    years, force = Base._download_years(station, [2026, 2025, 2025])

    assert years == [2025, 2026]
    assert force is True


def test_years_option_rejects_out_of_range_years(station):
    with pytest.raises(DrGeorgeError, match='1900'):
        Base._download_years(station, [1900, 2025])


# CLI: download --years
def test_cli_years_option_passes_years_and_force(monkeypatch):
    calls = []

    def fake_download(self, year, force=False):
        calls.append((year, force))
        return {'metadata': {'resultset': {'count': 0}}, 'results': []}

    monkeypatch.setattr(WeatherStation, 'download_noaa_data_by_year', fake_download)

    argv = ['download', 'santa_ana', '--years', '2025', '2026']
    with DrGeorgeTest(argv=argv) as app:
        app.run()

    assert calls == [(2025, True), (2026, True)]
