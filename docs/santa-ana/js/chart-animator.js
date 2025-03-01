/*
 * ChartAnimator Component
 *
 * Uses JS Class template:
 * https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Classes
**/
const ChartAnimatorConfig = {
  selector: 'button#replay',
  replayDelay: 200
}

class ChartAnimator {
  constructor(chart, dropdown) {
    this.chart = chart;
    this.dropdown = dropdown;
    this.config = ChartAnimatorConfig;
    this.selector = $(ChartAnimatorConfig.selector);
  }

  activate() {
    const component = this;
    this.selector.prop('disabled', false);
    this.selector.on('click', (event) => component.onClick(event));
  }

  async onClick() {
    this.selector.prop('disabled', true);
    this.dropdown.selector.prop('disabled', true);

    this.chart.hideDatasets();
    await this.replay();

    this.selector.prop('disabled', false);
    this.dropdown.selector.prop('disabled', false);
  }

  async replay() {
    const chart = this.chart;
    const years = this.chart.years;
    const delay = this.config.replayDelay;
    const dropdown = this.dropdown;

    async function replayYears() {
      let lastYear = null;

      for (const year of years) {
        if (lastYear) chart.unhighlightYear(lastYear);

        chart.unhideDatasetsByYear(year);
        chart.highlightYear(year);
        chart.draw();
        dropdown.selector.val(year);

        lastYear = year;
        await new Promise((resolve) => setTimeout(resolve, delay));
      }
    }

    await replayYears();

    chart.unhideDatasetsByYear('mean');
    chart.highlightMeans();
    chart.draw();
  }
}
