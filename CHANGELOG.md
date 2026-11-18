# Dr. George Change History

Versions are dated (`YEAR.MONTH.PATCH`). Each quarterly update is a release, and a fix between updates bumps the patch. Each release is tagged `v<version>` on GitHub.

## 2026.11.1 (2026-11-18)

A patch release for the Fall 2026 close-out (epic [#21](https://github.com/klenwell/dr-george/issues/21)). The live chart is unchanged.

- The test suite runs with no warnings, and any new warning now fails it (`filterwarnings = error` in `setup.cfg`). The Cement deprecation warning is fixed at its cause: `framework_logging = False`. `--debug` works as before, without Cement's internal hook and handler messages. Set `CEMENT_FRAMEWORK_LOGGING=1` to see them ([#30](https://github.com/klenwell/dr-george/issues/30)).
- The runbook's troubleshooting no longer says errors only show with `--debug`. They always print a traceback on stderr and exit 1 ([#28](https://github.com/klenwell/dr-george/issues/28), closed as not reproducible).

## 2026.11.0 (2026-11-17): Fall 2026 update

The first quarterly update. The plan is in the [Fall 2026 charter](docs/roadmap/20261116-fall-2026-update-charter.md), and the work is tracked in the [Dr. George Project](https://github.com/users/klenwell/projects/2).

**Data** (epic [#19](https://github.com/klenwell/dr-george/issues/19))
- 2025 is complete. Its December was missing because the January import ran before NOAA had published it.
- 2026 is added, through Oct 14, the latest day NOAA had published on 2026-11-16 (Oct 1–11 are still missing).
- The averages are rebuilt over complete years only (1917–2025), and the legend names the period ([#24](https://github.com/klenwell/dr-george/issues/24)).
- `download --years 2025 2026` re-downloads given years without deleting files by hand ([#27](https://github.com/klenwell/dr-george/pull/27)).
- [`docs/data-update.md`](docs/data-update.md) is the runbook for the quarterly refresh.

**Chart** (epic [#20](https://github.com/klenwell/dr-george/issues/20)), measured on the live site with [`tools/perf/`](tools/perf/README.md#after-20-2026-11-17):

| | Before | After |
|---|---|---|
| Ready | 2.5 s | 0.36 s |
| Hover work per move | 647 ms | 52 ms |
| Redraws per hover move | 1.8 | 0.8 |

- The chart draws once on load, with straight lines, no points, and pre-shaped data ([#43](https://github.com/klenwell/dr-george/pull/43)).
- Hovering redraws only when the hovered year changes ([#42](https://github.com/klenwell/dr-george/pull/42)).
- **Click or tap a point** to pin a panel of every year with the same high or low on that day, and choose one to highlight it ([#44](https://github.com/klenwell/dr-george/pull/44)). It replaces the tooltip list, which couldn't be clicked.
- The averages show one decimal place, and the tooltip says "Click to pin" (or "Tap") ([#38](https://github.com/klenwell/dr-george/issues/38)).
- The page fits phone screens ([#46](https://github.com/klenwell/dr-george/pull/46), [#48](https://github.com/klenwell/dr-george/pull/48)).
- Bootstrap is pinned to 5.2.3 (CSS and JS) with integrity hashes, and the unused date adapter and annotation plugin are removed ([#41](https://github.com/klenwell/dr-george/pull/41)).

## 0.0.1

Initial release.
