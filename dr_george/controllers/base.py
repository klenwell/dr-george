
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

        for year in range(station.start_year, 2025, 1):
            data = station.persist_json_records_by_year(year)
            print(f"{year}: {data['metadata']['resultset']['count']} records")


    # To run: python -m dr_george.main interactive
    @ex(help="Run the Application interactively. Useful for testing and development.")
    def interactive(self):
        from ..models.weather_station import WeatherStation
        from ..models.annual_station_summary import AnnualStationSummary

        station = WeatherStation('santa_ana')
        summary = AnnualStationSummary(station, 1972)
        print(len(summary.doy_max_temps))

        breakpoint()

        annual_data = {}
        for year in range(1920, 2025):
            data = station.persist_tmax_by_year(year)
            annual_data[year] = data['results']
            temps = [d['value'] for d in data['results']]
            print(year, len(temps), min(temps), max(temps), sum(temps)/len(temps))

        breakpoint()
