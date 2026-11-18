# Quarterly Data Update

How to refresh the Santa Ana chart (https://klenwell.com/dr-george/santa-ana/) with the latest NOAA data. It takes one sitting, about 30 minutes plus review. It was written from the Fall 2026 update ([#19](https://github.com/klenwell/dr-george/issues/19)), and the [Fall 2026 charter](roadmap/20261116-fall-2026-update-charter.md) is the plan behind it.

## When

Once a quarter, around mid-February, May, August and November.

**Expect NOAA to lag by about 1–1½ months.** Santa Ana Fire Station (`USC00047888`) is a co-op station that reports in batches. On 2026-11-16, its data ran through Oct 14, but Oct 1–11 were still missing. The last weeks before an update are often blank or patchy, and the next update fills them in.

**Which years to refresh:**

| Update | Years | Why |
|---|---|---|
| Winter (February) | Last year **and** this year | Last year's last month or two weren't published at the previous update |
| Spring, Summer, Fall | This year only | Last year is already complete. Re-downloading it rewrites its `.gz` file (gzip stores a timestamp), which adds noise to the diff |

If last year still has gaps after the winter update, add it again to the next update.

## Prerequisites (one-time)

- **Python virtualenv `dr-george`** (pyenv, Python 3.12):

  ```bash
  pyenv virtualenv 3.12.6 dr-george
  ~/.pyenv/versions/dr-george/bin/pip install -r requirements-dev.txt
  ```

  The commands below use the virtualenv's full path, `~/.pyenv/versions/dr-george/bin/python`, so they work even when pyenv isn't set up in the shell.
- **NOAA token** in `dr_george/config/secrets.py`. This file is gitignored, so never commit it:

  ```python
  NOAA_API_TOKEN = '<noaa-token>'
  ```

  Request a token (free, emailed) at https://www.ncdc.noaa.gov/cdo-web/token. The app uses NOAA's [CDO web services v2](https://www.ncdc.noaa.gov/cdo-web/webservices/v2).
- **`gh`**, logged in as `klenwell`, for the issue and PR.

## Steps

Below, `2027` stands for the current year and `2026` for the previous one. Change them to fit.

### 1. Open an issue and a branch

Add a `task` issue, such as "Refresh Santa Ana data (Winter 2027)", to the [Dr. George Project](https://github.com/users/klenwell/projects/2), and paste in the [checklist](#checklist) below. Then:

```bash
git checkout main && git pull
git checkout -b data-refresh-2027q1
```

### 2. Download

```bash
~/.pyenv/versions/dr-george/bin/python -m dr_george.main download santa_ana --years 2026 2027
```

`--years` re-downloads just those years and replaces their files. A failed request leaves the existing file as it was. Expected output, one pair of lines per year:

```
2026: writing to …/data/noaa/santa_ana/USC00047888-2026.json.gz
2026: 1095 of 1095 records
```

A complete year has about 1,095 records (high, low and precipitation × 365 days), or 1,098 in a leap year. Fewer than that means NOAA is still missing days.

### 3. Export

```bash
~/.pyenv/versions/dr-george/bin/python -m dr_george.main export santa_ana
```

This writes `docs/santa-ana/data/USC00047888-<year>.json` for every downloaded year, then `USC00047888-mean.json`. The mean averages complete years only, from 1917 through last year, and the chart's legend shows that period. Check the output:

- **The last line should be `Export means: …`.** If it stops early, a Python traceback follows the last line, and the command exits 1 (check with `echo $?`). The traceback goes to stderr, so it doesn't show if only stdout is captured.
- `Skipped <year>: no downloaded data` means that year was never downloaded. Go back to step 2.

### 4. Check what changed

```bash
git status --short data docs
```

Expect only the years you downloaded, their site JSON, and the mean. The other years should re-export byte-for-byte the same. If another year shows up, find out why before going on.

Find out how far each refreshed year now reaches, and where its gaps are:

```bash
for y in 2026 2027; do python3 -c "
import json, sys
y = sys.argv[1]
d = [x for x in json.load(open(f'docs/santa-ana/data/USC00047888-{y}.json'))['daily'] if x['date']]
have = [x['date'] for x in d if x['max_temp'] is not None and x['min_temp'] is not None]
last = have[-1] if have else None
gaps = [x['date'] for x in d if last and x['date'] <= last and x['date'] not in have]
print(f'{y}: {len(have)} days, latest {last}, gaps before it: {len(gaps)}', gaps[:5])
" $y; done
```

Put these numbers in the PR. For example, on 2026-11-16 it showed `2026: 276 days, latest 2026-10-14, gaps before it: 11 ['2026-10-01', …]`.

### 5. Check locally

```bash
cd docs && python3 -m http.server 3001
```

Open http://localhost:3001/santa-ana/ and hard-refresh. Check that:

- **Select a Year** lists the current year first.
- Picking the current year and last year highlights lines through the latest dates from step 4.
- The legend reads **Average Lows 1917–<last year>** and **Average Highs 1917–<last year>**.
- **Animate** plays through to the current year and ends on the average lines.

### 6. Publish

Merging to `main` publishes the site, because GitHub Pages serves `docs/` from `main`.

```bash
git add data/noaa/santa_ana docs/santa-ana/data
git commit -m "Refresh Santa Ana data through <latest date>"
git push -u origin data-refresh-2027q1
gh pr create --title "Refresh Santa Ana data through <latest date>" --body "Closes #<issue>. …"
```

After merging, wait for Pages to finish building, then check the live page with a hard refresh:

```bash
gh api repos/klenwell/dr-george/pages/builds/latest --jq '"\(.status) \(.commit[0:7])"'   # "built <merge commit>"
```

## Troubleshooting

| Symptom | Cause and fix |
|---|---|
| `Command 'python' not found` | pyenv isn't set up in this shell. Use the full path, `~/.pyenv/versions/dr-george/bin/python` |
| `download` prints `failed <HTTP error>` three times, then stops | NOAA rejected the request three times in a row. A 400 or 401 usually means a bad token: check `secrets.py`, and request a new token if it's no longer valid. A 5xx means NOAA is having trouble, so retry later. It then stops with a traceback ending in `Exception: Server is hosed: Try again later.` |
| `export` stops early | An unexpected error. Its traceback is on stderr, and the command exits 1. Make sure you're seeing stderr (for example, don't redirect it with `2>/dev/null`). In January 2026, this happened because the current year had no download yet. `export` now skips such years |
| A year's lines are blank for recent weeks | NOAA hasn't published those days yet (see [When](#when)). It fills in at the next update |
| The legend shows `1917â€“2025` | The page is being read with the wrong character encoding. `index.html` must keep `<meta charset="utf-8">` |
| The page still shows old data after merging | Pages is still building, or the browser has cached it. Check the build command above, then hard-refresh |

## Checklist

Paste this into the quarter's issue:

```markdown
- [ ] Branch from up-to-date `main`
- [ ] `download santa_ana --years <years>`: record counts noted
- [ ] `export santa_ana`: ends with `Export means`, nothing skipped
- [ ] `git status`: only the refreshed years, their JSON and the mean changed
- [ ] Gap check: latest date and gaps noted in the PR
- [ ] Local check at http://localhost:3001/santa-ana/: dropdown, highlight, legend period, Animate
- [ ] PR opened with `Closes #<issue>`, then merged
- [ ] Pages built, and the live page checked with a hard refresh
```
