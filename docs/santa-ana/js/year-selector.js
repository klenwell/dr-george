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

    // Default
    const $defaultOption = $('<option />').val(null).text('Click Here');
    $selector.append($defaultOption);

    years.forEach((year) => {
      const $option = $('<option />').val(year).text(year);
      $selector.append($option);
    });

    $selector.on('change', (event) => component.onChange(event));

    $(document).on("yearHover", (e, year) => component.onYearHover(year));
  }

  onChange(event) {
    const selectedYear = $(event.target).val();
    console.log('selected', selectedYear);

    // Null Value
    if ( !selectedYear) {
      return;
    }

    this.chart.highlightYear(selectedYear);
  }

  onYearHover(year) {
    console.log('onYearHover', year);
    this.selector.val(year).trigger('change');
  }
}
