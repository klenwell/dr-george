/*
 * AnnualStationData
 *
 * This is really as much a decorator or view helper as a data model.
 *
 * Uses JS Class template:
 * https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Classes
**/
const AnnualStationDataConfig = {
  noaaID: 'USC00047888',
}


class AnnualStationData {
  constructor(year) {
    this.config = AnnualStationDataConfig
    this.year = year
    this.dateTime = luxon.DateTime
  }

  /*
   * Getters
  **/
  get extractUrl() {
    return `data/${this.config.noaaID}-${this.year}.json`
  }

  get dailies() {
    return this.data.daily;
  }

  get maxTemps() {
    return this.dailies.map((daily) => daily.max_temp ? parseInt(daily.max_temp) : null);
  }

  get minTemps() {
    return this.dailies.map((daily) => daily.min_temp ? parseInt(daily.min_temp) : null);
  }

  /*
   * Async Methods
  **/
  async fetchData() {
    try {
      const response = await fetch(this.extractUrl);
      if (!response.ok) {
        throw new Error(`Response status: ${response.status}`);
      }

      const jsonData = await response.json();
      this.data = jsonData;
      console.log('fetched', this.year)
    } catch (error) {
      console.error(error.message);
    }
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
}
