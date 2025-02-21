
from cement import Controller, ex
from cement.utils.version import get_version_banner
from ..core.version import get_version

from requests.exceptions import HTTPError
import time

from ..models.weather_station import WeatherStation

VERSION_BANNER = """
Dr. George analyzes public weather data. %s
%s
""" % (get_version(), get_version_banner())


class Base(Controller):
    class Meta:
        label = 'base'

        # text displayed at the top of --help output
        description = 'Dr. George analyzes public weather data.'

        # text displayed at the bottom of --help output
        epilog = 'Usage: dr_george command1 --foo bar'

        # controller level arguments. ex: 'dr_george --version'
        arguments = [
            ### add a version banner
            ( [ '-v', '--version' ],
              { 'action'  : 'version',
                'version' : VERSION_BANNER } ),
        ]

    # To run: python -m dr_george.main download <station_id>
    # NOTE: station_id must be defined in config/noaa.py
    @ex(
        help="Download NOAA weather station data and store locally.",
        arguments=[
            (['station_id'], dict(action='store', nargs=1)),
        ],
    )
    def download(self):
        station_id = self.app.pargs.station_id[0]
        station = WeatherStation(station_id)
        max_retries = 3

        for year in range(station.start_year, station.end_year+1, 1):
            success = False
            retries = 0
            while not success:
                try:
                    data = station.download_noaa_data_by_year(year)
                    success = True
                    print(f"{year}: {len(data['results'])} of {data['metadata']['resultset']['count']} records")
                except HTTPError as e:
                    retries += 1
                    print('failed', e)
                    if retries >= max_retries:
                        raise Exception('Server is hosed: Try again later.')
                    time.sleep(1)


    # To run: python -m dr_george.main test-download
    @ex(help="Download a single year to sanity check download action.")
    def test_download(self):
        station_id = 'santa_ana'
        year = 1984

        station = WeatherStation(station_id)
        data = station.download_noaa_data_by_year(year)
        print(year, data['metadata']['resultset']['count'], len(data['results']))

    # To run: python -m dr_george.main export <station_id>
    @ex(
        help="Export weather station data to json files for frontend use.",
        arguments=[
            (['station_id'], dict(action='store', nargs=1)),
        ],
    )
    def export(self):
        station_id = self.app.pargs.station_id[0]
        station = WeatherStation(station_id)

        for year in range(station.start_year, station.end_year+1, 1):
            fpath = station.export_summary_to_json(year)
            print(f"Exported {year}: {fpath}")

    # To run: python -m dr_george.main analyze
    @ex(help="Run analysis.")
    def analyze(self):
        from ..libs.calendar import abs_day_nums_in_year, day_of_year_to_date
        import gzip, json

        station_id = 'santa_ana'
        station = WeatherStation(station_id)
        min_temps = {}
        year_null_count = {}

        data = station.json_records_by_year(1984)
        breakpoint()

        zpath = station.json_zpath_by_year(1984)
        with gzip.open(zpath, 'rt', encoding='utf-8') as f:
            breakpoint()

        for day_num in abs_day_nums_in_year():
            sds_list = station.daily_summaries_by_doy(day_num)
            years_missing = [sds.year for sds in sds_list if sds.min_temp is None]
            years_present = [sds.year for sds in sds_list if sds.min_temp is not None]
            min_temps[day_num] = years_present
            print(day_num, day_of_year_to_date(2020, day_num), len(years_missing))

        for year in station.years:
            ass = station.annual_summaries_by_year[year]
            days_missing = []
            for doy in abs_day_nums_in_year():
                ds = ass.daily_summary_by_doy(doy)
                if ds.min_temp is None:
                    days_missing.append(doy)
            year_null_count[year] = len(days_missing)
            print(year, len(days_missing), days_missing)

    def _default(self):
        """Default action if no sub-command is passed."""
        self.app.args.print_help()

    @ex(
        help='example sub command1',

        # sub-command level arguments. ex: 'dr_george command1 --foo bar'
        arguments=[
            ### add a sample foo option under subcommand namespace
            ( [ '-f', '--foo' ],
              { 'help' : 'notorious foo option',
                'action'  : 'store',
                'dest' : 'foo' } ),
        ],
    )
    def command1(self):
        """Example sub-command."""

        data = {
            'foo' : 'bar',
        }

        ### do something with arguments
        if self.app.pargs.foo is not None:
            data['foo'] = self.app.pargs.foo

        self.app.render(data, 'command1.jinja2')

    # To run: python -m dr_george.main interactive
    @ex(help="Run the Application interactively. Useful for testing and development.")
    def interactive(self):
        from ..models.weather_station import WeatherStation
        from ..models.annual_station_summary import AnnualStationSummary
        from ..libs.calendar import date, date_to_abs_day_num
        from ..config.app import GH_PAGES_ROOT, path_join
        import json

        station = WeatherStation('santa_ana')
        print(len(station.annual_summaries))

        today = date.today()
        abs_day_num = date_to_abs_day_num(today)
        print(station.avg_max_temp_by_doy(abs_day_num))
        report = station.max_temp_by_doy(abs_day_num)
        print(report)

        breakpoint()

        max_rains = []
        for year in station.years:
            report = station.max_rain_by_year(year)
            max_rains.append(report)
            print(station.annual_summaries_by_year[year])
        print(sorted(max_rains, key=lambda r:r.precipitation, reverse=True)[:10])
