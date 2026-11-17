"""
Tests for the mean (average lines) and the export: complete years only, the
period in the mean file, and skipping years with no downloaded data.

Uses a fake three-year station with generated raw files in a temp directory,
so no real data is read or written.
"""
import gzip
import json
from datetime import date, timedelta

import pytest

import dr_george.models.weather_station as ws_module
from dr_george.models.weather_station import WeatherStation
from dr_george.main import DrGeorgeTest

THIS_YEAR = date.today().year
FIRST_YEAR = THIS_YEAR - 2

# Daily high for every day of each year. Lows are 20 degrees lower.
HIGHS = {FIRST_YEAR: 60, FIRST_YEAR + 1: 70, THIS_YEAR: 100}


def write_raw_year(data_root, year, high, through=None):
    """Write a raw NOAA-style file with TMAX/TMIN/PRCP for each day of year."""
    results = []
    day = date(year, 1, 1)
    last = through or date(year, 12, 31)
    while day <= last:
        stamp = day.strftime('%Y-%m-%dT00:00:00')
        results += [
            {'date': stamp, 'datatype': 'TMAX', 'value': high},
            {'date': stamp, 'datatype': 'TMIN', 'value': high - 20},
            {'date': stamp, 'datatype': 'PRCP', 'value': 0},
        ]
        day += timedelta(days=1)

    path = data_root / 'noaa' / 'fake' / f'FAKE-{year}.json.gz'
    with gzip.open(path, 'wt', encoding='utf-8') as f:
        json.dump({'metadata': {'resultset': {'count': len(results)}}, 'results': results}, f)


@pytest.fixture
def fake_station(tmp_path, monkeypatch):
    data_root = tmp_path / 'data'
    pages_root = tmp_path / 'docs'
    (data_root / 'noaa' / 'fake').mkdir(parents=True)
    (pages_root / 'fake' / 'data').mkdir(parents=True)

    monkeypatch.setattr(ws_module, 'DATA_ROOT', str(data_root))
    monkeypatch.setattr(ws_module, 'GH_PAGES_ROOT', str(pages_root))
    monkeypatch.setitem(ws_module.STATIONS, 'fake', {'noaa_id': 'FAKE', 'start_year': FIRST_YEAR})

    write_raw_year(data_root, FIRST_YEAR, HIGHS[FIRST_YEAR])
    write_raw_year(data_root, FIRST_YEAR + 1, HIGHS[FIRST_YEAR + 1])
    # The current year only has January so far.
    write_raw_year(data_root, THIS_YEAR, HIGHS[THIS_YEAR], through=date(THIS_YEAR, 1, 31))

    return {'pages_root': pages_root, 'data_root': data_root}


def test_mean_years_stop_before_the_current_year(fake_station):
    station = WeatherStation('fake')

    assert station.end_year == THIS_YEAR
    assert station.mean_end_year == THIS_YEAR - 1
    assert list(station.mean_years) == [FIRST_YEAR, FIRST_YEAR + 1]


def test_mean_excludes_the_current_year(fake_station):
    station = WeatherStation('fake')

    jan_1 = station.daily_mean_reports[0]
    jul_1 = station.daily_mean_reports[182]

    # (60 + 70) / 2. With the current year's 100 included, it would be 76.7.
    assert float(jan_1.max_temp) == 65.0
    assert float(jan_1.min_temp) == 45.0
    assert float(jul_1.max_temp) == 65.0


def test_mean_export_names_the_period(fake_station):
    station = WeatherStation('fake')

    path = station.export_means_to_json()
    with open(path) as f:
        data = json.load(f)

    assert data['year'] == 'mean'
    assert data['start_year'] == FIRST_YEAR
    assert data['end_year'] == THIS_YEAR - 1
    assert len(data['daily']) == 366


def test_export_skips_years_without_downloaded_data(fake_station, capsys):
    current = fake_station['data_root'] / 'noaa' / 'fake' / f'FAKE-{THIS_YEAR}.json.gz'
    current.unlink()

    with DrGeorgeTest(argv=['export', 'fake']) as app:
        app.run()

    out = capsys.readouterr().out
    exported = sorted(p.name for p in (fake_station['pages_root'] / 'fake' / 'data').iterdir())

    assert f'Skipped {THIS_YEAR}: no downloaded data' in out
    assert exported == [f'FAKE-{FIRST_YEAR}.json', f'FAKE-{FIRST_YEAR + 1}.json', 'FAKE-mean.json']
