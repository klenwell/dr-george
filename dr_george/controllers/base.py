
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

    @ex(help="Run the Application interactively. Useful for testing and development.")
    def interactive(self):
        from ..adapters.noaa import NoaaAdapter
        from ..config.secrets import NOAA_API_TOKEN

        santa_ana_station = 'GHCND:USC00047888'
        noaa = NoaaAdapter(NOAA_API_TOKEN)

        annual_data = {}
        for year in range(1960, 2025, 1):
            data = noaa.get_tmax_by_year(santa_ana_station, year)
            annual_data[year] = data
            temps = [d['value'] for d in data]
            print(year, min(temps), max(temps), sum(temps)/len(temps))

        breakpoint()
