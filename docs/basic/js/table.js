/*
 * BasicTable
 *
 * Display model data as table.
 *
 * Uses JS Class template:
 * https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Classes
**/
const BasicTableConfig = {
  selector: 'section#basic-data table'
}


class BasicTable {
  static syncUrlToTab() {
    console.log('syncUrlToTab')
  }

  constructor(config, model) {
    this.config = config
    this.model = model
    this.dateTime = luxon.DateTime
  }

  /*
    * Getters
  **/


  /*
    * Public Methods
  **/
  render() {
    const $tbody = $(`${this.config.selector} tbody`);
    console.log(this.config.selector, $tbody);

    this.model.dailies.forEach((daily, n) => {
      var $tr = $("<tr>");
      $tr.append($("<td>").text(n + 1));
      $tr.append($("<td>").text(daily.date));
      $tr.append($("<td>").text(daily.max_temp));
      $tr.append($("<td>").text(daily.min_temp));
      $tr.append($("<td>").text(daily.precipitation));
      $tbody.append($tr);
    });
  }

  /*
    * Private Methods
  **/
}


/*
  * Main block: these are the things that happen on page load.
**/
$(document).ready(() => {
  BasicTable.syncUrlToTab()
})

$(document).on(BasicModel.dataReady, (event, model) => {
  const table = new BasicTable(BasicTableConfig, model)
  table.render()
})
