/*
 * BasicModel
 *
 * This is really as much a decorator or view helper as a data model.
 *
 * Uses JS Class template:
 * https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Classes
**/
const BasicModelConfig = {
  readyEvent: 'BasicModel:data:ready',
  extractUrl: 'data/USC00047888-2024.json'
}


class BasicModel {
  constructor(config) {
    this.config = config
    this.data = {}
    this.dateTime = luxon.DateTime
  }

  /*
    * Getters
  **/
  // For use by component as on event string to confirm data loaded:
  // $(document).on(BasicModel.dataReady, (event, model) => {})
  static get dataReady() {
    return BasicModelConfig.readyEvent
  }

  get dailies() {
    return this.data.daily;
  }

  get maxes() {
    return this.dailies.map((daily) => daily.max_temp ? parseInt(daily.max_temp) : null);
  }

  get mins() {
    return this.dailies.map((daily) => daily.min_temp ? parseInt(daily.min_temp) : null);
  }

  /*
    * Public Methods
  **/
  fetchData() {
    fetch(this.config.extractUrl)
      .then(response => response.json())
      .then(data => this.onFetchComplete(data))
  }

  byDayNum(num) {
    const i = num - 1;
    const daily = this.dailies[i];
    const record = {
      date: this.dateTime.fromISO(daily.date),
      max: parseInt(daily.max_temp),
      min: parseInt(daily.min_temp),
      rain: parseFloat(daily.precipitation)
    };
    return record;
  }

  /*
    * Private Methods
  **/
  onFetchComplete(jsonData) {
    this.data = jsonData
    this.triggerReadyEvent()
  }

  triggerReadyEvent() {
    console.log(this.config.readyEvent, this)
    $(document).trigger(this.config.readyEvent, [this])
  }
}


/*
  * Main block: these are the things that happen on page load.
**/
$(document).ready(function() {
  const model = new BasicModel(BasicModelConfig);
  model.fetchData();
})
