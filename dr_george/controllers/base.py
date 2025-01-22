
from cement import Controller, ex
from cement.utils.version import get_version_banner
from ..core.version import get_version

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

    # To run: python -m dr_george.main download
    @ex(help="Download data and store locally.")
    def download(self):
        from ..models.weather_station import WeatherStation

        station = WeatherStation('santa_ana')

        for year in range(station.start_year, station.end_year, 1):
            data = station.persist_json_records_by_year(year)
            print(f"{year}: {data['metadata']['resultset']['count']} records")

    # To run: python -m dr_george.main export
    @ex(help="Download data and store locally.")
    def export(self):
        from ..models.weather_station import WeatherStation
        from ..config.app import GH_PAGES_ROOT, path_join
        import json

        station = WeatherStation('santa_ana')
        year = 2024
        summary = station.annual_summaries_by_year[year]
        json_file = f"{station.noaa_id}-{year}.json"
        json_path = path_join(GH_PAGES_ROOT, 'data', 'basic', json_file)

        json_data = {
            'noaa_id': station.noaa_id,
            'year': year,
            'daily': [dr.to_dict() for dr in summary.daily_reports]
        }

        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)

        print(json_path)


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
