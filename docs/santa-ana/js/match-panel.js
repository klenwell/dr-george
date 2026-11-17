/*
 * MatchPanel Component
 *
 * A panel pinned next to a clicked (or tapped) point. It lists every year
 * with the same high (or low) on that day, and choosing one highlights it.
 *
 * Uses JS Class template:
 * https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Classes
**/
const MatchPanelConfig = {
  container: '.chart-block',
  gap: 14
}

class MatchPanel {
  constructor(chart) {
    this.chart = chart;
    this.config = MatchPanelConfig;
    this.container = $(this.config.container);
    this.panel = null;
    this.bindCloseHandlers();
  }

  get isOpen() {
    return this.panel !== null;
  }

  /*
   * Methods
  **/
  // point: { x, y, dayIndex, extremity, year, value }, with x and y in canvas pixels.
  open(point) {
    this.close();

    const isMean = point.year === 'mean';
    const kind = point.extremity === 'max' ? 'high' : 'low';
    const date = this.chart.labels[point.dayIndex];
    const value = this.chart.formatTemp(point.value, isMean);

    const $panel = $('<div class="match-panel card shadow" role="dialog" />')
      .attr('aria-label', `Years with the same ${kind} on ${date}`);
    const $body = $('<div class="card-body p-2" />').appendTo($panel);

    const $header = $('<div class="d-flex justify-content-between align-items-start gap-2" />').appendTo($body);
    $('<strong />').text(isMean ? `${date} \u00b7 Average ${kind}: ${value}` : `${date} \u00b7 ${kind[0].toUpperCase()}${kind.slice(1)}: ${value}`).appendTo($header);
    $('<button type="button" class="btn-close btn-sm" aria-label="Close" />')
      .on('click', () => this.close())
      .appendTo($header);

    if (isMean) {
      $('<div class="small text-muted mt-1" />').text('Averages have no matching years.').appendTo($body);
    }
    else {
      const years = this.chart.matchingYears(point.dayIndex, point.extremity, point.value);
      const yearWord = years.length === 1 ? 'year' : 'years';
      $('<div class="small text-muted mt-1 mb-1" />')
        .text(`${years.length} ${yearWord} with a ${kind} of ${value}:`)
        .appendTo($body);

      const $list = $('<div class="match-list list-group list-group-flush" />').appendTo($body);
      years.forEach((year) => {
        const isThis = String(year) === String(point.year);
        $('<button type="button" class="list-group-item list-group-item-action py-1 px-2" />')
          .text(isThis ? `${year} (this point)` : year)
          .toggleClass('fw-bold', isThis)
          .attr('aria-current', isThis ? 'true' : null)
          .on('click', () => this.choose(year))
          .appendTo($list);
      });
      $list.on('keydown', (e) => this.onListKeydown(e));
    }

    this.panel = $panel.appendTo(this.container);
    this.position(point);
    this.chart.setTooltipEnabled(false);

    const $first = $panel.find('.match-list button').first();
    ($first.length ? $first : $panel.find('.btn-close')).trigger('focus');
  }

  close() {
    if (!this.panel) return;
    this.panel.remove();
    this.panel = null;
    this.chart.setTooltipEnabled(true);
  }

  choose(year) {
    this.close();
    this.chart.pickYear(year);
  }

  // Next to the point, never over it: right of it if there's room, else
  // left, else above or below (narrow screens).
  position(point) {
    const gap = this.config.gap;
    const canvas = this.chart.canvas[0];
    const x = canvas.offsetLeft + point.x;
    const y = canvas.offsetTop + point.y;
    const boxWidth = this.container.innerWidth();
    const boxHeight = this.container.innerHeight();
    const width = this.panel.outerWidth();
    const height = this.panel.outerHeight();
    const clamp = (n, min, max) => Math.max(min, Math.min(n, max));

    let left, top;
    if (x + gap + width <= boxWidth) {
      left = x + gap;
      top = clamp(y - height / 2, 0, boxHeight - height);
    }
    else if (x - gap - width >= 0) {
      left = x - gap - width;
      top = clamp(y - height / 2, 0, boxHeight - height);
    }
    else {
      left = clamp(x - width / 2, 0, boxWidth - width);
      top = (y - gap - height >= 0) ? y - gap - height : y + gap;
    }

    this.panel.css({ left: `${left}px`, top: `${top}px` });
  }

  onListKeydown(event) {
    const $buttons = this.panel.find('.match-list button');
    const index = $buttons.index(document.activeElement);
    const moves = { ArrowDown: 1, ArrowUp: -1 };
    if (!(event.key in moves) || index < 0) return;

    event.preventDefault();
    const next = Math.max(0, Math.min(index + moves[event.key], $buttons.length - 1));
    $buttons.eq(next).trigger('focus');
  }

  bindCloseHandlers() {
    $(document).on('keydown', (e) => {
      if (e.key === 'Escape') this.close();
    });

    // Outside the panel closes it. Clicks on the chart are left to its
    // onClick, which pins another point or closes the panel.
    $(document).on('mousedown touchstart', (e) => {
      if (!this.panel) return;
      const target = e.target;
      if (this.panel[0].contains(target) || target === this.chart.canvas[0]) return;
      this.close();
    });
  }
}
