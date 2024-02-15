from datetime import datetime, timezone

from .glow_msg import get_glow_metrics
from .prices import get_electricity_price, get_gas_price

METRIC = "glowprom_{metric}"
METRIC_KEYS = "{{type=\"{type}\", {idname}=\"{idvalue}\"}}"

METRIC_METADATA = {
    "octopus_rate": ("The price from Octopus.", "gauge"),
}

METRIC_HELP = "# HELP {metric} {help}"
METRIC_TYPE = "# TYPE {metric} {_type}"


def get_metrics() -> str:
    now = datetime.utcnow()

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

    return "\n".join(lines)
