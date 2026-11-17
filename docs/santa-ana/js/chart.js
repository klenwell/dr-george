/*
 * Chart Component
 *
 * Uses JS Class template:
 * https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Classes
**/
const HistoricalTempChartConfig = {
  selector: 'canvas#chart',
  startYear: 1917,
  colors: {
    min: '#A3D5FF33',
    minHighlight: '#0077CCFF',
    minMeanHighlight: '#005A99CC',
    max: '#ff880033',
    maxHighlight: '#cc3300ff',
    maxMeanHighlight: '#b35f00cc'
  }
}

// Chart.js draws datasets with a lower order on top. Years use 0 (this year)
// and up, so the highlighted year goes above them, and the averages above it.
const HIGHLIGHT_ORDER = -500;
const MEAN_ORDER = -1000;


class HistoricalTempChart {
  constructor(config) {
    this.config = config;
    this.dateTime = luxon.DateTime;
    this.plotter = new Chart(this.canvas, this.chartConfig);
    this.datasetsByYear = {};
    this.highlightedDatasets = [];
    this.highlightedYear = null;
    this.meanPeriod = null;
  }

  /*
   * Getters
  **/
  get canvas() {
    return $(this.config.selector)
  }

  // Refer: https://stackoverflow.com/a/48143738/1093087
  get chartConfig() {
    return {
      type: 'line',
      data: {
        labels: this.labels,
        datasets: []
      },
      options: {
        animation: false,
        // Data arrives as {x: day index, y: temp}, already sorted, so
        // Chart.js can skip parsing it on every update.
        parsing: false,
        normalized: true,
        onHover: (e, els) => this.onHover(e, els),
        plugins: {
          legend: this.legend
        },
        scales: {
          x: {
            ticks: this.xTicks,
            grid: this.xGrid
          },
          y: {
            type: 'linear',
            min: 20,
            max: 120
          }
        }
      }
    }
  }

  // Only the mean datasets get a legend entry. The period comes from the
  // mean file (start_year, end_year), so each data update changes it.
  get legend() {
    const labelTextMap = {
      'Min mean': 'Average Lows',
      'Max mean': 'Average Highs'
    }

    const generateLabels = (chart) => {
      const period = this.meanPeriod ? ` ${this.meanPeriod}` : '';
      return chart.data.datasets
        .map((dataset, index) => ({ dataset, index }))
        .filter(({ dataset }) => labelTextMap[dataset.label])
        .map(({ dataset, index }) => ({
          text: `${labelTextMap[dataset.label]}${period}`,
          strokeStyle: dataset.borderColor,
          fillStyle: dataset.borderColor,
          datasetIndex: index
        }));
    }

    return {
      display: true,
      labels: {
        usePointStyle: true,
        generateLabels: (chart) => generateLabels(chart)
      }
    }
  }

  get xTicks() {
    const tickText = (value, index, values) => {
      const dayZero = luxon.DateTime.local(2020, 1, 1);
      let date = dayZero.plus({ days: index });
      return (date.day === 1) ? date.monthShort : '';
    };

    return {
      autoSkip: false,
      callback: (value, index, values) => tickText(value, index, values)
    }
  }

  get xGrid() {
    const gray = '#c8c8c8';
    const tickColor = (context) => {
      let color = context.tick.label === '' ? 'transparent' : gray;
      return color;
    };

    return {
      display: true,
      drawTicks: true,
      color: (context) => tickColor(context)
    }
  }

  get years() {
    const startYear = this.config.startYear;
    const endYear = this.thisYear;
    return Array.from(
      { length: (endYear - startYear) + 1 },
      (_, index) => startYear + index
    );
  }

  get thisYear() {
    return this.dateTime.now().year;
  }

  get dayNums() {
    return Array.from(Array(366).keys()).map((n) => { return n + 1 })
  }

  get labels() {
    // Make sure we're counting against a leap year
    const dayZero = this.dateTime.local(2019, 12, 31);
    return this.dayNums.map((dayNum) => {
      let date = dayZero.plus({ days: dayNum });
      let label = `${date.monthShort} ${date.day}`;
      return label;
    });
  }

  /*
   * Async Methods
  **/
  async render() {
    const years = this.years.concat(['mean']);
    const plotter = this.plotter;

    // Fetch every year, then draw once. Drawing as years arrived (every
    // tenth year) cost more than it showed.
    await Promise.all(
      years.map(async (year) => {
        let model = new AnnualStationData(year);
        await model.fetchData();

        if (model.data) {
          await this.pushDataset(model);
        }
        else {
          console.warn(`No data for year ${year}`)
        }
      })
    );
    performance.mark('dr-george:data-loaded');

    this.highlightMeans();
    plotter.update();
    performance.mark('dr-george:drawn');
    $('#chartLoading').remove();
  }

  async animate(yearDropdown) {

  }

  async pushDataset(model) {
    const minDataSet = this.toDataset(model, 'min');
    const maxDataSet = this.toDataset(model, 'max');

    this.plotter.data.datasets.push(minDataSet);
    this.plotter.data.datasets.push(maxDataSet);
    this.datasetsByYear[model.year] = [minDataSet, maxDataSet];

    if (model.year === 'mean' && model.data.start_year && model.data.end_year) {
      this.meanPeriod = `${model.data.start_year}\u2013${model.data.end_year}`;
    }
  }

  /*
   * Methods
  **/
  draw() {
    this.plotter.update();
  }

  hideDatasets() {
    const plotter = this.plotter;
    plotter.data.datasets.forEach((dataset, index) => {
      plotter.setDatasetVisibility(index, false);
    });
    plotter.update();
  }

  unhideDatasetsByYear(year) {
    const datasets = this.datasetsByYear[year];
    const minDatasetIndex = this.plotter.data.datasets.indexOf(datasets[0]);
    const maxDatasetIndex = this.plotter.data.datasets.indexOf(datasets[1]);
    this.plotter.setDatasetVisibility(minDatasetIndex, true);
    this.plotter.setDatasetVisibility(maxDatasetIndex, true);
  }

  // Redraw only when the pointer reaches a different year. Chart.js calls
  // onHover again after every update (it replays the last event), and most
  // pointer moves land on a new year, so this guard is what keeps a hover to
  // one redraw.
  onHover(event, elements) {
    if (!elements.length) return;

    const datasetIndex = elements[0].datasetIndex;
    const year = this.plotter.data.datasets[datasetIndex].year;
    if (this.isHighlighted(year)) return;

    this.highlightYear(year);
    this.draw();

    // Custom event that can be used to make other updates (like with dropdown)
    $(document).trigger("yearHover", [year]);
  }

  isHighlighted(year) {
    return this.highlightedYear !== null && String(year) === this.highlightedYear;
  }

  highlightYear(year) {
    const datasets = this.datasetsByYear[year];
    if (!datasets) return;

    this.clearHighlight();
    this.highlightDataset(datasets[0]);
    this.highlightDataset(datasets[1]);
    this.highlightedYear = String(year);
  }

  // Unhighlights the year if it's the one highlighted.
  unhighlightYear(year) {
    if (this.isHighlighted(year)) this.clearHighlight();
  }

  clearHighlight() {
    this.highlightedDatasets.forEach((dataset) => {
      this.unhighlightDataset(dataset);
    });

    this.highlightedDatasets = [];
    this.highlightedYear = null;
  }

  highlightDataset(dataset) {
    const colorMap = {
      'min': this.config.colors.minHighlight,
      'max': this.config.colors.maxHighlight
    }
    const color = colorMap[dataset.extremity];

    dataset.oldColor = dataset.borderColor;
    dataset.oldOrder = dataset.order;
    dataset.borderColor = color;
    dataset.order = HIGHLIGHT_ORDER;

    this.highlightedDatasets.push(dataset);
  }

  unhighlightDataset(dataset) {
    if (!dataset) return

    dataset.borderColor = dataset.oldColor;
    dataset.order = dataset.oldOrder;
  }

  // Width 3: without point dots, the old width of 2 read thinner than before.
  highlightMeans() {
    const [minDataset, maxDataset] = this.datasetsByYear['mean']

    // Min
    minDataset.borderColor = this.config.colors.minMeanHighlight;
    minDataset.borderWidth = 3;
    minDataset.order = MEAN_ORDER;

    // Max
    maxDataset.borderColor = this.config.colors.maxMeanHighlight;
    maxDataset.borderWidth = 3;
    maxDataset.order = MEAN_ORDER;
  }

  toDataset(model, extremity) {
    const typeMap = {
      'min': [model.minTemps, `Min ${model.year}`, this.config.colors.min],
      'max': [model.maxTemps, `Max ${model.year}`, this.config.colors.max]
    }

    const data = typeMap[extremity][0].map((y, x) => ({ x, y }));
    const label = typeMap[extremity][1];
    const color = typeMap[extremity][2];
    const order = this.thisYear - model.year;

    return {
      data: data,
      label: label,
      borderColor: color,
      year: model.year,
      extremity: extremity,
      order: order,
      fill: false,
      borderWidth: 1,
      // No dots or curve smoothing: with 222 lines of 366 days, they made
      // every redraw cost hundreds of ms. A point still shows on hover.
      pointRadius: 0,
      pointHitRadius: 3,
      tension: 0
    }
  }

  opHexByYear(year) {
    const opMin = 20;
    const opMax = 80;
    const opRange = opMax - opMin;
    const yearRange = this.thisYear - this.config.startYear;
    const yearIdx = year - this.config.startYear;
    const yearQuot = yearIdx / yearRange;
    const opIdx = (yearQuot * opRange) + opMin;
    const decimal = opIdx / 100;
    const hexValue = Math.round(decimal * 255).toString(16);
    return hexValue.length === 1 ? "0" + hexValue : hexValue;
  }
}


/*
 * Main block
**/
$(document).ready(async () => {
  const chart = new HistoricalTempChart(HistoricalTempChartConfig);
  const yearSelector = new YearSelector(chart);
  const chartAnimator = new ChartAnimator(chart, yearSelector);

  await chart.render();
  yearSelector.populate();
  chartAnimator.activate();
});
