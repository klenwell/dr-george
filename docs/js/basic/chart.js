/*
 * Basic Chart Component
 *
 * Uses JS Class template:
 * https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Classes
**/
class BasicChart {
    constructor(model) {
      this.model = model
      this.dateTime = luxon.DateTime
    }

    /*
     * Getters
    **/
    get canvas() {
      const selector = 'canvas#basic-chart'
      return $(selector)
    }

    // Refer: https://stackoverflow.com/a/48143738/1093087
    get config() {
      return {
        type: 'line',
        data: {
          labels: Array.from(Array(366).keys()),
          datasets: []
        }
      }
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

    /*
     * Methods
    **/
    lazyRender() {
      const minDataset = this.toDataset(this.model.mins, 'Min Temp', 'blue');
      const maxDataset = this.toDataset(this.model.maxes, 'Max Temp', 'orange');
      let chart = new Chart(this.canvas, this.config);

      [minDataset, maxDataset].forEach((dataset) => {
        console.log('push', dataset)
        chart.data.datasets.push(dataset)
        chart.update()
      });
    }
  }


  /*
   * Main block: these are the things that happen on designated event.
  **/
  $(document).on(BasicModel.dataReady, (event, model) => {
    const chart = new BasicChart(model)
    chart.lazyRender()
  })
