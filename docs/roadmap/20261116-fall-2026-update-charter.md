# Charter: Fall 2026 Update

Written: 2026-11-16 · **Status: active** (approved 2026-11-16). Epics are refined one at a time with `/epic` and tracked as issues in `dr-george`, in a new Dr. George GitHub Project (Epic 1, Step 00).

## Why

Dr. George charts daily highs and lows at the Santa Ana Fire Station (NOAA GHCND `USC00047888`) from 1917 on, at [klenwell.com/dr-george/santa-ana](https://klenwell.com/dr-george/santa-ana/). It was last updated on 2026-01-11, and it's been shared on Reddit, so people see stale data and a slow page.

This is the first of a series of **quarterly updates**. Each one refreshes the data and takes on a small set of fixes. This one sets up the process that later ones reuse: a GitHub Project to track the work, and a runbook for the data update.

## What's there now (findings, 2026-11-16)

**Data**
- The site has one JSON file per year, `docs/santa-ana/data/USC00047888-<year>.json` (1917–2025), plus `-mean.json`. The raw NOAA downloads are in `data/noaa/santa_ana/*.json.gz`.
- **2025 is missing all of December.** All 31 days have null highs and lows: the January import ran before NOAA had published them.
- **There's no 2026 file,** so the chart ends at 2025.
- The CLI (`download`, `export`) re-downloads a year only after its file is deleted by hand (README).
- It calls NOAA's CDO web services v2 (`cdo-web/api/v2/data`) with a token kept in the gitignored `dr_george/config/secrets.py`. Whether the token and the API still work hasn't been checked since January.
- `-mean.json` dates from 2025-02-24, so the averages probably cover 1917–2024. It's never been rebuilt. *Corrected 2026-11-16 ([#24](https://github.com/klenwell/dr-george/issues/24)):* the mean averaged every year through the current one, so it included January–February 2025. It wasn't rebuilt in January 2026 because `export` crashed silently on 2026, which had no download yet.

**Chart page** (`docs/santa-ana/`, Chart.js 3.8 with jQuery)
- **Every load fetches 110 files, about 6.1 MB.** Each yearly file has the date, station ID and precipitation for every day, and the chart uses none of them.
- **The chart draws about 220 line datasets × 366 points** (around 80,000 points) with curve smoothing (`tension: 0.5`) and a visible point at each value.
- **Each hover redraws the chart twice.** `onHover` calls `update()`, then fires `yearHover`, which sets the year dropdown. Its `change` handler highlights the year again and calls `draw()`. This runs on every mouse move over a point.
- **The rollover's "pick a matching year" feature doesn't work** (from the owner's screenshot, 2026-11-16).
  - **What it's for:** when you hover over a point, the tooltip lists every year with the same temperature on that date. Hovering Jun 27 at 84° lists 2012, 2001, 1970, 1956, 1930, 1928 and 1927. The idea is that you can then pick one of those years to highlight it.
  - **Why it can't work:** the tooltip is drawn on the canvas, so its rows aren't controls. It also disappears as soon as the pointer moves off the point, so the pointer can never reach it.
  - **The boxes only look like checkboxes.** They're Chart.js's color swatches. Chart.js fills them with the dataset's `backgroundColor`, which is never set, so it falls back to the default translucent grey. The border is the line's color at 20% opacity (`#…33`). Only the highlighted year's box gets a visible border.
  - **Getting this working is a feature for Epic 2,** not just a styling fix (see [Decisions](#decisions-2026-11-16)).
- **Smaller issues:**
  - `highlightIndex` counts down forever, so every hover sets a new draw `order`.
  - `unhighlightYear(year)` ignores its argument.
  - The Bootstrap CSS (5.2.0-beta1) and JS (5.0.2) versions don't match.
  - `chartjs-adapter-date-fns` loads with no pinned version, and it looks unused (the x-axis is category labels).
- There are no front-end tests. The Python tests are the Cement template's (`command1`).

## Goals

1. **Current data.** The chart shows 2025 complete and 2026 through the latest day NOAA has published.
2. **A fast page.** First load and hover are visibly faster, with a measured before and after (see [Done when](#done-when)).
3. **Rollover works.** From a point, you can pick any other year with the same temperature on that date, and it gets highlighted. Hovering or selecting a year highlights exactly that year.
4. **Tracked work.** A Dr. George GitHub Project with epics and tickets, following the Sweepers conventions.
5. **Repeatable updates.** A runbook that makes the next quarterly data update a short, routine task.

## Scope

**In:**
- Refreshing Santa Ana data (re-downloading 2025, adding 2026).
- Deciding on and rebuilding the mean.
- Making the CLI's re-download easier.
- Changing the exported data format for speed.
- Chart rendering and hover performance, and fixing the rollover bugs.
- Pinning and aligning CDN libraries.
- The GitHub Project and labels.
- A data-update runbook, and a changelog entry.

**Out:**
- New stations or a second page.
- Precipitation charts.
- A redesign.
- A build step or framework.
- Moving off GitHub Pages and klenwell.com.

## Principles

- **Static and thin.** Plain HTML/JS on Pages, with no bundler. A dependency is added only once it earns its place, and the reason is recorded.
- **The data is the source of truth.** The raw NOAA downloads stay committed. The site's JSON is always rebuilt from them by `export` and never edited by hand.
- **Measure before optimizing.** Record load time, transfer size and hover responsiveness before changes and after each one, in the issue or PR.
- **Secrets stay out.** The NOAA token lives only in the gitignored `secrets.py`, and docs use `<noaa-token>`.
- **Approval first** for anything outward-facing: creating the Project, pushing, and merging to `main` (which publishes the site).
- **Issues and PRs record what really happened,** including failures.

## Tracking: GitHub Project

This follows the setup from the Sweepers Editor retrospective (2026-11-11), as used in the Sweepers charters:

| Jira | GitHub |
|---|---|
| Project / board | **One long-lived Project, "Dr. George",** on `klenwell`, with board, table and roadmap views. It's reused by every quarterly update |
| Epic | **A parent issue** labeled `epic`, with each step as a sub-issue |
| Story / task / bug | **Sub-issues** or standalone issues, labeled `story`, `task` or `bug` |
| Status | The Project's Status field, with built-in automations that move items to Done when the issue closes or the PR merges |

- **One PR per step.** Its body says `Closes #<step issue>`.
- **The docs stay the record.** Each epic's README in `docs/epics/YYYYMMDD-<slug>/` keeps a status table, and its runbooks record results.
- **Bugs and ideas** found mid-epic become issues, not just follow-up bullets.
- **Setup needs the owner** to add the `project` scope to the `gh` token for `klenwell` (`gh auth refresh -s project`), because it opens a browser login.

## Proposed epics

| # | Epic | Scope |
|---|---|---|
| 1 | `oc-data-2026q4` | **Step 00:** create the Project and labels, and file this charter's epics as issues. Check the NOAA token and API. Re-download 2025 and download 2026 to date. Add a `--force` (or `refresh`) option so a year can be re-downloaded without deleting files by hand. Decide on and rebuild the mean. Re-export, check the chart locally, and publish. Write `docs/data-update.md` as the quarterly runbook |
| 2 | `chart-performance` | Measure a baseline. Make the matching-years tooltip work (see Decision 5). Fix the double redraw on hover, and throttle hover. Cut drawing cost: no smoothing, no points until hover, and `parsing: false` with pre-shaped data. Export one compact file (highs and lows only, all years) in place of 110 files, keeping the per-year files if anything else uses them. Pin and align the CDN libraries, and remove the unused date adapter. Measure again |
| 3 | `quarterly-close` | Add a CHANGELOG entry and README updates (the update workflow, the Project link). Write a short retrospective, and seed the Winter 2027 update with a data-refresh issue and any backlog |

Epic 1 comes first: it's quick, it fixes the most visible problem, and it tests the pipeline. If Epic 2 changes the export format, re-exporting is cheap.

## Decisions (2026-11-16)

Approved with the recommended options. Any of them can be revisited when its epic or ticket is planned.

1. **The mean is rebuilt over all complete years** (1917–2025 this time) on each update, and the legend names the period ("Average Highs 1917–2025", [#24](https://github.com/klenwell/dr-george/issues/24)). Alternatives considered: keep it as it is (1917 through part of 2025), or use NOAA's 1991–2020 normal. The 30-year normal could be a later story.
2. **One combined data file.** `export` writes one compact file with the highs and lows for every year, roughly 0.3–0.5 MB before Pages' gzip, in place of 110 requests. Epic 2 confirms this with measurements. Slimmed per-year files are the fallback.
3. **Chart.js stays on 3.8 for now.** Epic 2 revisits a move to 4.x only if the cheaper fixes don't reach the targets.
4. **The Project is a user Project on `klenwell`, named "Dr. George",** and is reused by every quarterly update.
5. **Picking a matching year is click to pin.**
   - Hovering shows the tooltip as it does now.
   - Clicking a point pins it as an HTML panel (using Chart.js's `external` tooltip hook), with each matching year as a clickable row.
   - Choosing a row highlights that year and sets the dropdown.
   - Clicking elsewhere or pressing Esc closes the panel.
   - It works with touch, where there's no hover.
   - Alternatives considered: keeping an HTML tooltip open while the pointer moves onto it (fiddly, because other points take over on the way), and clicking repeatedly to cycle through the matching years (you can't see or choose a year).

## Done when

- The live page shows 2025 complete and 2026 through NOAA's latest day.
- The Project tracks this update's epics, with every step closed by a merged PR.
- From any point, you can pick another year with the same temperature on that date, and it gets highlighted. This works with a mouse and on a phone.
- Measured on the same machine and browser:
  - First load transfers less than 1 MB of data, down from about 6.1 MB.
  - Hovering stays smooth, with one redraw per hover change.
- `docs/data-update.md` lets the next quarterly refresh be done in one sitting.
