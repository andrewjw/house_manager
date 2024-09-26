from datetime import datetime, UTC

from .glow_msg import get_glow_metrics
from .prices import get_electricity_price, get_gas_price
from .suncalc import getPosition, getMoonPosition, getMoonIllumination
from .water_cost import WaterCost
from .weather_forecast import CloudForecast

METRIC = "glowprom_{metric}"
METRIC_KEYS = "{{type=\"{type}\", {idname}=\"{idvalue}\"}}"

METRIC_METADATA = {
    "octopus_rate": ("The price from Octopus.", "gauge"),
}

METRIC_HELP = "# HELP {metric} {help}"
METRIC_TYPE = "# TYPE {metric} {_type}"

CLOUDFORECAST = CloudForecast()
WATERCOST = WaterCost()
WATERCOST.start()

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

    lines.append(METRIC_HELP.format(metric="watercost_total", help="Total cost of water"))
    lines.append(METRIC_TYPE.format(metric="watercost_total", _type="counter"))
    lines.append(f'watercost_total {WATERCOST.cost}')

    lines.append(get_glow_metrics())

    lines.append(METRIC_HELP.format(metric="forecast_cloud", help="Cloud Cover"))
    lines.append(METRIC_TYPE.format(metric="forecast_cloud", _type="gauge"))
    forecast = CLOUDFORECAST.get_clouds(now)
    if forecast is not None:
        lines.append(f'forecast_cloud{{level="total"}} {forecast.total}')
        lines.append(f'forecast_cloud{{level="high"}} {forecast.high}')
        lines.append(f'forecast_cloud{{level="mid"}} {forecast.mid}')
        lines.append(f'forecast_cloud{{level="low"}} {forecast.low}')

    return "\n".join(lines)
