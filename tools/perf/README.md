# Chart performance script

`measure.mjs` loads the Santa Ana chart in headless Chrome. It times the load and a sweep of hover moves, and counts how often Chart.js redraws. It was added in [#33](https://github.com/klenwell/dr-george/issues/33) for epic [#20](https://github.com/klenwell/dr-george/issues/20), where each change is measured against the baseline below.

This folder is outside `docs/`, so GitHub Pages doesn't publish it.

## Setup

You need Node 18 or later and Google Chrome. The script uses `puppeteer-core`, which drives your installed Chrome and doesn't download a browser.

```bash
cd tools/perf
npm install
```

Chrome is expected at `/usr/bin/google-chrome`. Set `CHROME_PATH` to use a different one.

## Usage

```bash
node measure.mjs                                   # live site, 3 runs
node measure.mjs --url http://localhost:3001/santa-ana/
node measure.mjs --throttle 4                      # 4x slower CPU, roughly a mid-range phone
node measure.mjs --runs 5 --steps 60 --json        # JSON output, every run included
```

Local URLs need a server first: `cd docs && python3 -m http.server 3001`.

It prints a Markdown table of medians, plus each run's value, ready to paste into a PR.

## What the numbers mean

| Measure | How it's taken |
|---|---|
| Ready (ms) | From navigation until the year dropdown is filled (which happens after every year has loaded and the chart has rendered), plus two animation frames for the paint |
| Data loaded / Draw after data loaded | Marks the page sets in `render()` (since #36): when every year's data has been fetched and added (on the page's clock, from navigation), and how long the one redraw after that took. They show "–" for pages without the marks |
| Redraws during load | Calls to `Chart.prototype.update` up to ready. The script counts them by wrapping the `Chart` global when the CDN script defines it |
| Requests / transfer | From the DevTools network log. "Data" means `…/data/*.json`. **Transfer only means something against the live site:** GitHub Pages gzips JSON, and `python3 -m http.server` doesn't |
| JS heap (MB) | `JSHeapUsedSize` when the chart is ready |
| **Hover work per move (ms)** | **The main hover measure.** The pointer moves 60 times, left to right across the band of daily highs. Chrome's main-thread busy time (`TaskDuration`) over the sweep is divided by 60. On an empty page it measures about 1.3 ms |
| Hover wall time | The same sweep, timing each move until two animation frames have passed (Chart.js handles pointer events once per frame), as the median and 90th percentile. **It has a floor of about 50 ms** (measured on an empty page), so it only shows big differences |
| Redraws during hover sweep / per move | `update` calls during the sweep |
| Years in dropdown | A sanity check that the page loaded every year |

**Caveats:**
- Headless Chrome may draw in software, without the GPU, so absolute times can be slower than in a desktop browser. Compare runs taken on the same machine.
- Ready time varies from run to run, by up to about ±0.5 s. Use the median of 3 or more runs.
- **Floors, measured on an empty page:** hover work is about 1.3 ms per move, and hover wall time is about 50 ms (the two-frame wait plus the round trip to Chrome).

## Baseline (2026-11-17, before #20)

Taken with this script on the owner's Linux desktop, with Chrome 157 in headless mode. Medians of 3 runs, except the throttled run, which is 1 run. The full tables are in [#33](https://github.com/klenwell/dr-george/issues/33).

| Measure | Live site | Local server | Live, 4x CPU throttle |
|---|---|---|---|
| Ready (ms) | 2,521 (runs: 2,019–2,619) | 2,107 | 9,207 |
| Redraws during load | 13 | 13 | 13 |
| Requests (data) | 111 | 111 | 111 |
| Transfer, data (KB) | 322 | 6,172 (uncompressed) | 322 |
| **Hover work per move (ms)** | **647** | 665 | 2,693 |
| Hover wall time, median (ms) | 700 | 717 | 2,800 |
| Redraws per hover move | 1.8 | 1.8 | 1.8 |

The local server sends about 19 times as much data as the live site, uncompressed, yet it's no slower to be ready. So download size isn't what slows the page. Redraws are: 13 during load, and 1.8 per hover move, each drawing 222 lines.

**Correction (2026-11-17, #35):** the first version of the script counted every redraw twice, because Chart.js 3 assigns `window.Chart` twice and the script wrapped `update` both times. The table above has the corrected counts (first published as 26 and 3.6). The timings were not affected.

## After #20 (2026-11-17)

Measured on the live site in [#39](https://github.com/klenwell/dr-george/issues/39), after the last step of [#20](https://github.com/klenwell/dr-george/issues/20) was published, on the same machine and Chrome as the baseline. Medians of 5 runs, or 3 at 4x throttle.

| Measure | Baseline (live) | **After (live)** | Baseline, 4x throttle | **After, 4x throttle** |
|---|---|---|---|---|
| Ready (ms) | 2,521 (2,354 in the corrected re-run) | **362** | 9,207 | **1,010** |
| Data loaded / draw after (ms) | – | 247 / 58 | – | 675 / 167 |
| Redraws during load | 13 | **2** | 13 | 2 |
| Transfer, data (KB) | 322 | 322 | 322 | 322 |
| **Hover work per move (ms)** | **647** | **52.2** (runs 51.1–53.1) | 2,693 | **207** |
| Hover wall time, median (ms) | 700 | 83 | 2,800 | 250 |
| Redraws per hover move | 1.8 | **0.8** (one per change of year) | 1.8 | 0.8 |
| JS heap (MB) | 44 | 24 | – | 23 |

What made the difference: the chart draws once after loading instead of 13 times (#36); lines have no point dots or curve smoothing, so a full redraw takes about 2 ms instead of about 200 ms (#36); and hover redraws only when the year changes (#35).

Hover missed its "under 50 ms" target by about 2 ms. The owner accepted that (2026-11-17, #39): Chart.js's own JavaScript is about 25 ms of each move, and most of the rest is the browser painting the canvas, which more tuning or Chart.js 4 wouldn't remove.
