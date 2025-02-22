/*
 * YearSelector Component
 *
 * Uses JS Class template:
 * https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Classes
**/
const YearSelectorConfig = {
  selector: 'select#yearSelector',
}

class YearSelector {
  constructor(chart) {
    this.chart = chart;
    this.selector = $(YearSelectorConfig.selector);
  }

  populate() {
    const component = this;
    const $selector = this.selector;
    const years = this.chart.years.toReversed();

    years.forEach((year) => {
      const $option = $('<option />').val(year).text(year);
      $selector.append($option);
    });

    $selector.on('change', (event) => component.onChange(event));
  }

  onChange(event) {
    const selectedYear = $(event.target).val();
    console.log('selected', selectedYear);
    this.chart.highlightYear(selectedYear);
  }
}
