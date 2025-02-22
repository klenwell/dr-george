/*
 * Chart Component
 *
 * Uses JS Class template:
 * https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Classes
**/
const HistoricalTempChartConfig = {
  selector: 'canvas#chart',
  startYear: 1917
}


class HistoricalTempChart {
    constructor(config) {
      this.config = config;
      this.dateTime = luxon.DateTime;
      this.chart = new Chart(this.canvas, this.chartConfig);
      this.highlightedDataset = null;
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
            legend: {
                display: false,
            }
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

    onHover(event, elements) {
      if (!elements.length) {
        return;
      }

      const datasetIndex = elements[0].datasetIndex;
      const dataset = this.chart.data.datasets[datasetIndex];
      this.highlightDataset(dataset);
    }

    highlightDataset(dataset) {
      const colorMap = {
        'min': this.colors.minHighlight,
        'max': this.colors.maxHighlight
      }

      const color = colorMap[dataset.extremity]
      this.highlightIndex--;
      console.log('un/highlight', this.highlightedDataset, dataset);

      this.unhighlightDataset(this.highlightedDataset);
      dataset.oldColor = dataset.borderColor;
      dataset.borderColor = color;
      dataset.order = this.highlightIndex;
      this.highlightedDataset = dataset;
      this.chart.update();
    }

    unhighlightDataset(dataset) {
      if ( ! dataset ) {
        return;
      }

      dataset.borderColor = dataset.oldColor;
      this.highlightedDataset = null;
    }

    get xTicks() {
      const tickText = (value, index, values) => {
        const dayZero = luxon.DateTime.local(2019, 12, 31);
          let date = dayZero.plus({days: index});
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
      return Array.from(Array(366).keys()).map((n) => { return n+1 })
    }

    get labels() {
      // Make sure we're counting against a leap year
      const dayZero = this.dateTime.local(2019, 12, 31);
      return this.dayNums.map((dayNum) => {
        let date = dayZero.plus({days: dayNum});
        //let label = (date.day === 1) ? date.monthShort : `${date.month}/${date.day}`;
        let label = `${date.month}/${date.day}`;
        return label;
      });
    }

    get colors() {
      return {
        min: '#99ccff33',
        minHighlight: '#0066ffff',
        max: '#ff880033',
        maxHighlight: '#bb6600ff'
      }
    }

    /*
     * Methods
    **/
    async render() {
      await Promise.all(
        this.years.map(async (year) => {
          let model = new AnnualStationData(year);
          await model.fetchData();
          await this.pushDataset(model);
        })
      );

      this.chart.update();
      return this;
    }

    async pushDataset(model) {
      const minDataSet = this.toDataset(model, 'min');
      const maxDataSet = this.toDataset(model, 'max');

      this.chart.data.datasets.push(minDataSet);
      this.chart.data.datasets.push(maxDataSet);
    }

    toDataset(model, extremity) {
      const typeMap = {
        'min': [model.minTemps, `Min ${model.year}`, this.colors.min],
        'max': [model.maxTemps, `Max ${model.year}`, this.colors.max]
      }

      const data = typeMap[extremity][0];
      const label = typeMap[extremity][1];
      const color = typeMap[extremity][2];

      return {
        data: data,
        label: label,
        borderColor: color,
        extremity: extremity,
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
   * Main block: these are the things that happen on designated event.
  **/
  $(document).ready(() => {
    const chart = new HistoricalTempChart(HistoricalTempChartConfig)
    chart.render()
  })
