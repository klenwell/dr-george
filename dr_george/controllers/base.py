
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
    @ex(help="Run the Application interactively. Useful for testing and development.")
    def download(self):
        from ..adapters.noaa import NoaaAdapter
        from ..config.secrets import NOAA_API_TOKEN
        import json
        import os
        import gzip

        year = 1952
        santa_ana_station = 'GHCND:USC00047888'
        noaa = NoaaAdapter(NOAA_API_TOKEN)

        fpath = f'/tmp/santa-ana-{year}.json'
        zpath = f'{fpath}.gz'

        if os.path.exists(zpath):
            print(f"reading from {zpath}")
            with gzip.open(zpath, 'rt', encoding='utf-8') as f:  # 'rt' for reading text from gzip
                data = json.load(f)

        else:
            data = noaa.get_tmax_by_year(santa_ana_station, year)
            print(f"writing to {zpath}")
            with gzip.open(zpath, 'wt', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

        breakpoint()


    # To run: python -m dr_george.main interactive
    @ex(help="Run the Application interactively. Useful for testing and development.")
    def interactive(self):
        from ..adapters.noaa import NoaaAdapter
        from ..config.secrets import NOAA_API_TOKEN
        from ..models.weather_station import WeatherStation

        cache = False
        station = WeatherStation('santa_ana')
        print(station.noaa_id)
        data = station.get_tmax_by_year(1920, cache)
        breakpoint()

        santa_ana_station = 'GHCND:USC00047888'
        noaa = NoaaAdapter(NOAA_API_TOKEN)

        annual_data = {}
        for year in range(1920, 1921, 1):
            data = noaa.get_tmax_by_year(santa_ana_station, year)
            annual_data[year] = data
            temps = [d['value'] for d in data]
            print(year, min(temps), max(temps), sum(temps)/len(temps))

        breakpoint()
