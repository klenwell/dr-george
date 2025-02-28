/*
 * ChartAnimator Component
 *
 * Uses JS Class template:
 * https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Classes
**/
const ChartAnimatorConfig = {
  selector: 'button#replay',
  replayDelay: 250
}

class ChartAnimator {
  constructor(chart, dropdown) {
    this.chart = chart;
    this.dropdown = dropdown;
    this.config = ChartAnimatorConfig;
    this.selector = $(ChartAnimatorConfig.selector);
  }

  activate() {
    console.log('activate', this);
    const component = this;
    this.selector.prop('disabled', false);
    this.selector.on('click', (event) => component.onClick(event));
  }

  async onClick() {
    console.log('clicked');
    this.selector.prop('disabled', true);
    this.dropdown.selector.prop('disabled', true);

    await this.replay();

    this.selector.prop('disabled', false);
    this.dropdown.selector.prop('disabled', false);
  }

  async replay() {
    return await new Promise((resolve) => setTimeout(resolve, 3000));

    const self = this;
    const chartYears = this.years;
    const chart = this.chart;
    const chartPlotter = this.chart.chart;
    const delay_ = this.config.replayDelay;
    const yearDelay = 5;

    async function replayYears(years, delay) {
      let lastYear = null;

      for (const year of years) {
        if ( ! self.datasetsByYear[year] ) {
          let model = new AnnualStationData(year);
          await model.fetchData();
          await self.pushDataset(model);
        }

        if (lastYear) self.unhighlightYear(lastYear);
        self.highlightYear(year);
        lastYear = year;

        jsChart.update();

        yearDropdown.addYearOption(year);
        yearDropdown.selector.val(year);

        await new Promise((resolve) => setTimeout(resolve, delay));
      }
    }

    await processYears(chartYears, yearDelay);

    console.log('years mapped');

    let model = new AnnualStationData('mean');
    await model.fetchData();
    await this.pushDataset(model);

    this.highlightMeans();
    this.chart.update();
  }
}
