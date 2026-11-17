// Measures load and hover performance of the Dr. George chart page.
//
// Usage (from tools/perf):
//   node measure.mjs [--url URL] [--runs N] [--throttle X] [--steps N] [--json]
//
// Uses the installed Chrome (CHROME_PATH, default /usr/bin/google-chrome) through
// puppeteer-core, so no browser is downloaded. See README.md for what each number means.
import puppeteer from 'puppeteer-core';

const DEFAULTS = {
  url: 'https://klenwell.com/dr-george/santa-ana/',
  runs: 3,
  throttle: 1,
  steps: 60,
  json: false,
};

function parseArgs(argv) {
  const opts = { ...DEFAULTS };
  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];
    if (arg === '--json') opts.json = true;
    else if (arg === '--url') opts.url = argv[++i];
    else if (arg === '--runs') opts.runs = Number(argv[++i]);
    else if (arg === '--throttle') opts.throttle = Number(argv[++i]);
    else if (arg === '--steps') opts.steps = Number(argv[++i]);
    else if (arg === '--help' || arg === '-h') {
      console.log('node measure.mjs [--url URL] [--runs N] [--throttle X] [--steps N] [--json]');
      process.exit(0);
    } else {
      console.error(`Unknown argument: ${arg}`);
      process.exit(2);
    }
  }
  return opts;
}

const sorted = (xs) => [...xs].sort((a, b) => a - b);
const median = (xs) => sorted(xs)[Math.floor(xs.length / 2)];
const percentile = (xs, p) => sorted(xs)[Math.min(xs.length - 1, Math.floor(xs.length * p))];
const twoFrames = () => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)));

// Count Chart.update() calls: wrap the Chart global as soon as the CDN script defines it.
// Chart.js 3 assigns window.Chart twice with the same class, so wrap only once
// (wrapping twice counted every update as two before 2026-11-17).
function countChartUpdates() {
  let ChartClass;
  window.__chartUpdates = 0;
  Object.defineProperty(window, 'Chart', {
    configurable: true,
    get() { return ChartClass; },
    set(value) {
      if (value === ChartClass || value.prototype.update.__counted) {
        ChartClass = value;
        return;
      }
      const update = value.prototype.update;
      value.prototype.update = function (...args) {
        window.__chartUpdates++;
        return update.apply(this, args);
      };
      value.prototype.update.__counted = true;
      ChartClass = value;
    },
  });
}

async function measureOnce(browser, opts) {
  const page = await browser.newPage();
  await page.setViewport({ width: 1200, height: 800 });
  await page.setCacheEnabled(false);

  const cdp = await page.createCDPSession();
  await cdp.send('Network.enable');
  if (opts.throttle > 1) {
    await cdp.send('Emulation.setCPUThrottlingRate', { rate: opts.throttle });
  }

  const net = { requests: 0, dataRequests: 0, bytes: 0, dataBytes: 0 };
  const urls = new Map();
  const isData = (url) => /\/data\/[^/]+\.json/.test(url || '');
  cdp.on('Network.requestWillBeSent', (e) => {
    urls.set(e.requestId, e.request.url);
    net.requests++;
    if (isData(e.request.url)) net.dataRequests++;
  });
  cdp.on('Network.loadingFinished', (e) => {
    net.bytes += e.encodedDataLength;
    if (isData(urls.get(e.requestId))) net.dataBytes += e.encodedDataLength;
  });

  await page.evaluateOnNewDocument(countChartUpdates);

  // Ready: the year dropdown is filled, which happens after every year has
  // loaded and the chart has rendered. Then wait for that frame to paint.
  const start = Date.now();
  await page.goto(opts.url, { waitUntil: 'domcontentloaded' });
  await page.waitForFunction(
    () => document.querySelectorAll('#yearSelector option').length > 1,
    { timeout: 180000, polling: 50 },
  );
  await page.evaluate(twoFrames);
  const readyMs = Date.now() - start;
  const loadUpdates = await page.evaluate(() => window.__chartUpdates);
  const years = await page.evaluate(() => document.querySelectorAll('#yearSelector option').length - 1);
  const metrics = await page.metrics();

  // Hover: sweep the pointer left to right across the band of daily highs.
  // Each move is timed until two animation frames have passed, because
  // Chart.js handles pointer events once per frame. That wait sets a floor of
  // about 50 ms on wall time, so main-thread work (Chrome's TaskDuration over
  // the sweep, divided by the moves) is the measure that shows real cost.
  const box = await (await page.$('canvas#chart')).boundingBox();
  await page.evaluate(() => { window.__chartUpdates = 0; });
  const before = await page.metrics();
  const hoverTimes = [];
  for (let i = 0; i < opts.steps; i++) {
    const x = box.x + 40 + (box.width - 60) * (i / opts.steps);
    const y = box.y + box.height * 0.33;
    const t = Date.now();
    await page.mouse.move(x, y);
    await page.evaluate(twoFrames);
    hoverTimes.push(Date.now() - t);
  }
  const hoverUpdates = await page.evaluate(() => window.__chartUpdates);
  const after = await page.metrics();
  const hoverWorkMs = ((after.TaskDuration - before.TaskDuration) * 1000) / opts.steps;

  await page.close();
  return {
    readyMs,
    loadUpdates,
    requests: net.requests,
    dataRequests: net.dataRequests,
    transferKb: net.bytes / 1024,
    dataTransferKb: net.dataBytes / 1024,
    heapMb: metrics.JSHeapUsedSize / 1048576,
    hoverWorkMs,
    hoverMedianMs: median(hoverTimes),
    hoverP90Ms: percentile(hoverTimes, 0.9),
    hoverUpdates,
    hoverUpdatesPerMove: hoverUpdates / opts.steps,
    years,
  };
}

const LABELS = {
  readyMs: 'Ready (ms)',
  loadUpdates: 'Redraws during load',
  requests: 'Requests (all)',
  dataRequests: 'Requests (data)',
  transferKb: 'Transfer, all (KB)',
  dataTransferKb: 'Transfer, data (KB)',
  heapMb: 'JS heap (MB)',
  hoverWorkMs: 'Hover work per move (ms)',
  hoverMedianMs: 'Hover wall time, median (ms)',
  hoverP90Ms: 'Hover wall time, p90 (ms)',
  hoverUpdates: 'Redraws during hover sweep',
  hoverUpdatesPerMove: 'Redraws per hover move',
  years: 'Years in dropdown',
};

const round = (n) => Math.round(n * 10) / 10;

const opts = parseArgs(process.argv.slice(2));
const browser = await puppeteer.launch({
  executablePath: process.env.CHROME_PATH || '/usr/bin/google-chrome',
  headless: true,
  args: ['--no-first-run'],
});

const runs = [];
try {
  for (let i = 0; i < opts.runs; i++) runs.push(await measureOnce(browser, opts));
} finally {
  await browser.close();
}

const summary = Object.fromEntries(Object.keys(LABELS).map((k) => [k, round(median(runs.map((r) => r[k])))]));

if (opts.json) {
  console.log(JSON.stringify({ ...opts, date: new Date().toISOString(), median: summary, runs }, null, 2));
} else {
  console.log(`${opts.url}  runs=${opts.runs}  cpu-throttle=${opts.throttle}x  hover-steps=${opts.steps}`);
  console.log('| Measure | Median | Runs |');
  console.log('|---|---|---|');
  for (const [k, label] of Object.entries(LABELS)) {
    console.log(`| ${label} | ${summary[k]} | ${runs.map((r) => round(r[k])).join(', ')} |`);
  }
}
