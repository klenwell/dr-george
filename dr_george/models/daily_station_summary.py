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

    def __repr__(self):
        id = self.station.id_key
        d = self.date.strftime('%Y-%m-%d')
        maxt = self.max_temp
        mint = self.min_temp
        rain = self.precipitation
        return f"<{id} {d} max_temp={maxt} min_temp={mint} rain={rain:.2f}>"
