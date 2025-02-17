import json
from decimal import Decimal


class DailyStationSummary:
    def __init__(self, station, date, max_temp, min_temp, precip):
        self.station = station
        self.date = date
        self.max_temp = max_temp
        self.min_temp = min_temp
        self.precipitation = precip

    @property
    def year(self):
        return self.date.year

    @property
    def date_str(self):
        if self.date is None:
            return None
        return self.date.strftime('%Y-%m-%d')

    def to_dict(self):
        return {
            'date': self.date_str,
            'max_temp':  self.dec_to_json(self.max_temp),
            'min_temp': self.dec_to_json(self.min_temp),
            'precipitation': self.dec_to_json(self.precipitation),
            'station_id': self.station.id_key
        }

    def dec_to_json(self, number):
        if type(number) is Decimal:
            return f"{number:.1f}"
        else:
            return number


    def to_json(self):
        return json.dumps(
            self.to_dict(),
            sort_keys=True,
            indent=2
        )

    def __repr__(self):
        id = self.station.id_key
        d = self.date_str
        maxt = self.max_temp
        mint = self.min_temp
        rain = self.precipitation
        return f"<{id} {d} max_temp={maxt} min_temp={mint} rain={rain:.2f}>"
