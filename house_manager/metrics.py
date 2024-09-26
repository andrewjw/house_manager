from datetime import datetime, UTC
import os

from .glow_msg import get_glow_metrics
from .prices import get_electricity_price, get_gas_price
from .suncalc import getPosition, getMoonPosition, getMoonIllumination
from .weather_forecast import CloudForecast

METRIC = "glowprom_{metric}"
METRIC_KEYS = "{{type=\"{type}\", {idname}=\"{idvalue}\"}}"

METRIC_METADATA = {
    "octopus_rate": ("The price from Octopus.", "gauge"),
}

METRIC_HELP = "# HELP {metric} {help}"
METRIC_TYPE = "# TYPE {metric} {_type}"

CLOUDFORECAST = CloudForecast()

def get_metrics() -> str:
    now = datetime.now(UTC)

    lines = []

    metric = "octopus_rate"
    lines.append(
        METRIC_HELP.format(metric=metric, help=METRIC_METADATA[metric][0]))
    lines.append(
        METRIC_TYPE.format(metric=metric, _type=METRIC_METADATA[metric][1]))

    lines.append(
        f'octopus_rate{{type="electric"}} {get_electricity_price(now)}')
    lines.append(
        f'octopus_rate{{type="gas"}} {get_gas_price(now)}')

    lines.append(get_glow_metrics())

    lines.append(METRIC_HELP.format(metric="forecast_cloud", help="Cloud Cover"))
    lines.append(METRIC_TYPE.format(metric="forecast_cloud", _type="gauge"))
    forecast = CLOUDFORECAST.get_clouds(now)
    if forecast is not None:
        lines.append(f'forecast_cloud{{level="total"}} {forecast.total}')
        lines.append(f'forecast_cloud{{level="high"}} {forecast.high}')
        lines.append(f'forecast_cloud{{level="mid"}} {forecast.mid}')
        lines.append(f'forecast_cloud{{level="low"}} {forecast.low}')

    sun_position = getPosition(now, os.environ["HOUSE_LAT"], os.environ["HOUSE_LONG"])
    moon_position = getMoonPosition(now, os.environ["HOUSE_LAT"], os.environ["HOUSE_LONG"])
    moon_illumination = getMoonIllumination(now)

    lines.append(METRIC_HELP.format(metric="sun_position", help="Position of the sun in sky"))
    lines.append(METRIC_TYPE.format(metric="sun_position", _type="gauge"))
    lines.append(f'sun_position{{dimension="azimuth"}} {sun_position["azimuth"]}')
    sun_altitude = max(0, sun_position["altitude"])
    lines.append(f'sun_position{{dimension="altitude"}} {sun_altitude}')

    lines.append(METRIC_HELP.format(metric="moon_position", help="Position of the moon in sky"))
    lines.append(METRIC_TYPE.format(metric="moon_position", _type="gauge"))
    lines.append(f'moon_position{{dimension="azimuth"}} {moon_position["azimuth"]}')
    moon_altitude = max(0, moon_position["altitude"])
    lines.append(f'moon_position{{dimension="altitude"}} {moon_altitude}')
    lines.append(f'moon_position{{dimension="distance"}} {moon_position["distance"]}')

    lines.append(METRIC_HELP.format(metric="moon_illumination", help="Phase of the moon"))
    lines.append(METRIC_TYPE.format(metric="moon_illumination", _type="gauge"))
    lines.append(f'moon_illumination{{dimension="fraction"}} {moon_illumination["fraction"]}')
    lines.append(f'moon_illumination{{dimension="phase"}} {moon_illumination["phase"]}')
    lines.append(f'moon_illumination{{dimension="angle"}} {moon_illumination["angle"]}')

    return "\n".join(lines)
