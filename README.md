# Dr. George

A simple Python command line app to analyze and visualize public weather data (with a focus on Southern California).

**Live chart:** https://klenwell.com/dr-george/santa-ana/

It plots the daily high and low at the Santa Ana Fire Station (NOAA GHCND `USC00047888`) for every year since 1917, with the averages over all complete years. Hover over a line to highlight its year. Click or tap a point to list every year with the same high or low on that day, and choose one to highlight it.

## Quarterly updates

The chart is refreshed and improved once a quarter:

- **Runbook:** [docs/data-update.md](docs/data-update.md) refreshes the data in one sitting.
- **Plans:** each update starts with a charter in [docs/roadmap/](docs/roadmap/) and is run as epics.
- **Tracking:** the [Dr. George Project](https://github.com/users/klenwell/projects/2) on GitHub.
- **History:** [CHANGELOG.md](CHANGELOG.md). Each update is released and tagged with a dated version, such as `v2026.11.0`.

## Installation

Python 3.12, in a virtualenv (the runbook uses a pyenv virtualenv named `dr-george`):

```
pip install -r requirements-dev.txt
```

Downloading needs a NOAA token in `dr_george/config/secrets.py`, which is gitignored. See the [runbook](docs/data-update.md#prerequisites-one-time).

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

Existing years are kept, except the current one, which is always re-downloaded. To refresh specific years (for example, when NOAA has filled in late data):

```
python -m dr_george.main download santa_ana --years 2025 2026
```

Export JSON data for chart:

```
python -m dr_george.main export santa_ana
```

The chart page is [docs/santa-ana/](docs/santa-ana/). GitHub Pages publishes `docs/` from `main`, so merging to `main` updates the live site.

## Local Web Server

To test web pages in `docs` directory:

```
cd docs
python3 -m http.server 3001
```

http://localhost:3001/santa-ana/

## Tests

```
python -m pytest tests/
```

## Chart performance

[tools/perf/](tools/perf/README.md) measures the chart's load time and hover cost in headless Chrome, with the before and after numbers from the Fall 2026 update:

```
cd tools/perf
npm install
node measure.mjs
```
