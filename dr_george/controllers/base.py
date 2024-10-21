
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
        from ..config.secrets import NOAA_API_TOKEN
        import requests

        BASE_URL = 'https://www.ncei.noaa.gov/cdo-web/api/v2/'

        headers = {
            'token': NOAA_API_TOKEN
        }

        station_id = 'GHCND:USW00023119'  # NOAA station ID for Santa Ana, CA
        start_date = '2023-01-01'
        end_date = '2023-12-31'

        url = f"{BASE_URL}data"
        params = {
            'datasetid': 'GHCND',
            'stationid': station_id,
            'startdate': start_date,
            'enddate': end_date,
            'limit': 1000,
            'datatypeid': 'TMAX',  # Daily Maximum Temperature
            'units': 'standard'  # Fahrenheit
        }

        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()['results']

        breakpoint()
