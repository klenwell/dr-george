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


class HistoricalTempChart {
  constructor(config) {
    this.config = config;
    this.dateTime = luxon.DateTime;
    this.plotter = new Chart(this.canvas, this.chartConfig);
    this.datasetsByYear = {};
    this.highlightedDatasets = [];
    this.highlightIndex = 0;
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

  get legend() {
    const labelTextMap = {
      'Min mean': 'Average Mins',
      'Max mean': 'Average Maxes'
    }
    const displayedLabels = Object.values(labelTextMap);

    const generateLabels = (chart) => {
      return chart.data.datasets.map((dataset, index) => ({
        text: labelTextMap[dataset.label],
        strokeStyle: dataset.borderColor,
        fillStyle: dataset.borderColor,
        datasetIndex: index
      }));
    }

    return {
      display: true,
      labels: {
        usePointStyle: true,
        generateLabels: (chart) => generateLabels(chart),
        filter: (legendItem, chartData) => displayedLabels.includes(legendItem.text)
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

    await Promise.all(
      years.map(async (year) => {
        let model = new AnnualStationData(year);
        await model.fetchData();
        await this.pushDataset(model);
        if ( year % 10 == 1 ) {
          plotter.update();
        }
      })
    );

    this.highlightMeans();
    plotter.update();
  }

  async animate(yearDropdown) {

  }

  async pushDataset(model) {
    const minDataSet = this.toDataset(model, 'min');
    const maxDataSet = this.toDataset(model, 'max');

    this.plotter.data.datasets.push(minDataSet);
    this.plotter.data.datasets.push(maxDataSet);
    this.datasetsByYear[model.year] = [minDataSet, maxDataSet];
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

  onHover(event, elements) {
    if ( !elements.length ) return;

    const datasetIndex = elements[0].datasetIndex;
    const year = this.plotter.data.datasets[datasetIndex].year;
    this.highlightYear(year);
    this.plotter.update();

    // Custom event that can be used to make other updates (like with dropdown)
    $(document).trigger("yearHover", [year]);
  }

  highlightYear(year) {
    const datasets = this.datasetsByYear[year];
    this.unhighlightYear(year);
    this.highlightDataset(datasets[0]);
    this.highlightDataset(datasets[1]);
  }

  unhighlightYear(year) {
    this.highlightedDatasets.forEach((dataset) => {
      this.unhighlightDataset(dataset);
    });

    this.highlightedDatasets = [];
  }

  highlightDataset(dataset) {
    const colorMap = {
      'min': this.config.colors.minHighlight,
      'max': this.config.colors.maxHighlight
    }
    const color = colorMap[dataset.extremity];

    dataset.oldColor = dataset.borderColor;
    dataset.borderColor = color;
    dataset.order = this.highlightIndex;

    this.highlightIndex--;
    this.highlightedDatasets.push(dataset);
  }

  unhighlightDataset(dataset) {
    if ( !dataset ) return

    dataset.borderColor = dataset.oldColor;
    this.highlightedDataset = null;
  }

  highlightMeans() {
    const [minDataset, maxDataset] = this.datasetsByYear['mean']

    // Min
    minDataset.borderColor = this.config.colors.minMeanHighlight;
    minDataset.borderWidth = 2;
    minDataset.order = -1000;

    // Max
    maxDataset.borderColor = this.config.colors.maxMeanHighlight;
    maxDataset.borderWidth = 2;
    maxDataset.order = -1000;
  }

  toDataset(model, extremity) {
    const typeMap = {
      'min': [model.minTemps, `Min ${model.year}`, this.config.colors.min],
      'max': [model.maxTemps, `Max ${model.year}`, this.config.colors.max]
    }

    const data = typeMap[extremity][0];
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
      pointRadius: 1,
      pointHitRadius: 3,
      tension: 0.5
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
