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
      this.chart = new Chart(this.canvas, this.chartConfig)
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
          plugins: {
            legend: {
                display: false,
            }
          },
          scales: {
            x: {
              ticks: {
                autoSkip: false,
                callback: function(value, index, values) {
                  const dayZero = luxon.DateTime.local(2019, 12, 31);
                  let date = dayZero.plus({days: index});
                  return (date.day === 1) ? date.monthShort : '';
                }
              },
              grid: {
                display: true,
                drawTicks: true,
                color: function(context) {
                  const gray = 'rgba(200, 200, 200, 0.8)';
                  let tickColor = context.tick.label === '' ? 'transparent' : gray;
                  return tickColor;
                }
              }
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

    /*
     * Methods
    **/
    async render() {
      await Promise.all(
        this.years.map(async (year) => {
          let model = new AnnualStationData(year);
          await model.fetchData();
          await this.pushDataset(model, chart);
        })
      );

      chart.update();
      return this;
    }

    async pushDataset(model, chart) {
      const minHex = '0088ff';
      const maxHex = 'ff8800'
      const opHex = '22'

      let minColor = `#${minHex}${opHex}`;
      let maxColor = `#${maxHex}${opHex}`;
      let minDataSet = this.toDataset(model.minTemps, `Min ${model.year}`, minColor);
      let maxDataSet = this.toDataset(model.maxTemps, `Max ${model.year}`, maxColor);

      chart.data.datasets.push(minDataSet);
      chart.data.datasets.push(maxDataSet);
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

    toDataset(data, label, color) {
      return {
        label: label,
        fill: false,
        borderWidth: 1,
        borderColor: color,
        pointRadius: 1,
        data: data,
        tension: 0.5
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
