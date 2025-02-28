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

    years.forEach((year) => component.addYearOption(year));

    $selector.on('change', (event) => component.onChange(event));

    $(document).on("yearHover", (e, year) => component.onYearHover(year));
  }

  addYearOption(year) {
    const $option = $('<option />').val(year).text(year);
    this.selector.append($option);
  }

  onChange(event) {
    const selectedYear = $(event.target).val();

    // User could select first label value
    if ( !selectedYear) {
      return;
    }

    this.chart.highlightYear(selectedYear);
    this.chart.draw();
  }

  onYearHover(year) {
    this.selector.val(year).trigger('change');
  }
}
