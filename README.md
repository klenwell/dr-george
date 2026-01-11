# Dr. George

A simple Python command line app to analyze and visualize public weather data (with a focus on Southern California).

## Installation

```
$ pip install -r requirements.txt

$ python setup.py install
```

## Visualization Workflow

Configure NOAA station in `dr_george/config/noaa.py`:

```
STATIONS = {
    # https://www.ncei.noaa.gov/cdo-web/datasets/GHCND/stations/GHCND:USC00047888/detail
    'santa_ana': {
        'noaa_id': 'USC00047888',
        'start_year': 1917
    }
}
```

Download NOAA data:

```
python -m dr_george.main download santa_ana
```

Note: You'll have to delete existing data file for a given year to re-download it.

Export JSON data for chart:

```
python -m dr_george.main export santa_ana
```

Build web page. Example:

- https://github.com/klenwell/dr-george/blob/main/docs/santa-ana/index.html

## Local Web Server
To test web pages in `docs` directory:

```
cd docs
python -m http.server 3001
```

http://localhost:3001/
