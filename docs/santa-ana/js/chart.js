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
      this.config = config
      this.dateTime = luxon.DateTime
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
          plugins: {
            legend: {
                display: false,
            }
          }
        }
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
        let label = (date.day === 1) ? date.monthShort : date.day;
        return label;
      });
    }

    /*
     * Methods
    **/
    render() {
      let chart = new Chart(this.canvas, this.chartConfig);
      let models = {};

      this.years.forEach(async (year) => {
        if ( year > 1930 ) { return; };
        let model = new AnnualStationData(year);
        await model.fetchData();
        await this.renderYear(model, chart);
        //models[year] = model;
      });
    }

    async renderYear(model, chart) {
      let minDataSet = this.toDataset(model.minTemps, `Min ${model.year}`, 'lightblue');
      let maxDataSet = this.toDataset(model.maxTemps, `Max ${model.year}`, 'orange');
      chart.data.datasets.push(minDataSet);
      chart.data.datasets.push(maxDataSet);
      chart.update();
    }

    toDataset(data, label, color) {
      return {
        label: label,
        fill: false,
        borderWidth: 2,
        borderColor: color,
        pointRadius: 2,
        data: data,
        tension: 0.2
      }
    }

    lazyRender() {
      const delay = 1000;
      const minDataset = this.toDataset(this.model.mins, 'Min Temp', 'blue');
      const maxDataset = this.toDataset(this.model.maxes, 'Max Temp', 'orange');
      const datasets = [minDataset, maxDataset];
      let chart = new Chart(this.canvas, this.config);

      datasets.forEach((dataset, index) => {
        setTimeout(() => {
          console.log('push', dataset);
          chart.data.datasets.push(dataset);
          chart.update();
        }, index * delay); // 1-second delay between each update
      });
    }
  }


  /*
   * Main block: these are the things that happen on designated event.
  **/
  $(document).ready(() => {
    const chart = new HistoricalTempChart(HistoricalTempChartConfig)
    chart.render()
  })
