from datetime import datetime, timedelta, UTC
import os
from typing import List, Optional

import openmeteo_requests  # type:ignore
from retry_requests import retry  # type:ignore

RETRY_SESSION = retry(retries = 5, backoff_factor = 0.2)
OPENMETEO = openmeteo_requests.Client(session = RETRY_SESSION)

URL = "https://api.open-meteo.com/v1/forecast"
PARAMS = {
	"latitude": os.environ["HOUSE_LAT"],
	"longitude": os.environ["HOUSE_LONG"],
	"timezone": "GMT",
	"hourly": ["cloud_cover", "cloud_cover_low", "cloud_cover_mid", "cloud_cover_high"],
}

class ForecastEntry:
    def __init__(self, time: datetime, total: float, low: float, mid: float, high: float):
        self.time = time
        self.total = total
        self.low = low
        self.mid = mid
        self.high = high

    def __str__(self) -> str:
        return f"{self.time} Total:{self.total} Low:{self.low} Mid: {self.mid} High:{self.high}"

class CloudForecast:
    def __init__(self) -> None:
        self.last_update: Optional[datetime] = None
        self.forecast: List[ForecastEntry] = []

    def update(self) -> None:
        if self.last_update is not None and (datetime.now(UTC) - self.last_update).total_seconds() > 6 * 60 * 60:
            return
        response = OPENMETEO.weather_api(URL, params=PARAMS)[0]
        hourly = response.Hourly()
        hourly_cloud_cover = hourly.Variables(0)
        hourly_cloud_cover_low = hourly.Variables(1)
        hourly_cloud_cover_mid = hourly.Variables(2)
        hourly_cloud_cover_high = hourly.Variables(3)

        start_time = datetime.fromtimestamp(hourly.Time() - response.UtcOffsetSeconds(), tz=UTC)
        forecast = []
        for v in range(hourly_cloud_cover.ValuesLength()):
            forecast.append(
                ForecastEntry(
                    start_time + timedelta(seconds=hourly.Interval() * v),
                    hourly_cloud_cover.Values(v),
                    hourly_cloud_cover_low.Values(v),
                    hourly_cloud_cover_mid.Values(v),
                    hourly_cloud_cover_high.Values(v)
                )
            )
        self.last_update = datetime.now(UTC)
        self.forecast = forecast

    def get_clouds(self, time: datetime) -> Optional[ForecastEntry]:
        self.update()
        before: Optional[int] = None
        for i in range(len(self.forecast)):
            if self.forecast[i].time == time:
                return self.forecast[i]
            if self.forecast[i].time < time:
                before = i

        if before is None or before == len(self.forecast) - 1:
            # We're after the last forecast value
            return None

        perc = (time - self.forecast[before].time).total_seconds() / 3600.0
        return ForecastEntry(
            time,
            self.forecast[before].total * perc + self.forecast[before + 1].total * (1 - perc),
            self.forecast[before].low * perc + self.forecast[before + 1].low * (1 - perc),
            self.forecast[before].mid * perc + self.forecast[before + 1].mid * (1 - perc),
            self.forecast[before].high * perc + self.forecast[before + 1].high * (1 - perc),
        )
