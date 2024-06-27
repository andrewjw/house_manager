from datetime import datetime
import json
from typing import Any, Optional

from .prices import get_electricity_price, get_electricity_standing_charge, \
                    get_gas_price, get_gas_standing_charge, get_export_price

# {'electricitymeter': {'timestamp': '2022-11-07T09:20:08Z',
#   'energy': {'export': {'cumulative': 0.0, 'units': 'kWh'},
#              'import': {'cumulative': 15254.827, 'day': 3.717,
#                         'week': 3.717, 'month': 60.439, 'units': 'kWh',
#                         'mpan': 'abcd', 'supplier': 'Octopus Energy',
#                         'price': {'unitrate': 0.16401,
#                                   'standingcharge': 0.19383}}},
#   'power': {'value': 0.425, 'units': 'kW'}}}

# {'gasmeter': {'timestamp': '2022-11-07T09:35:38Z',
#   'energy': {'import': {'cumulative': 66589.57, 'day': 17.326,
#                         'week': 17.326, 'month': 383.157, 'units': 'kWh',
#                         'cumulativevol': 5995.276,
#                         'cumulativevolunits': 'm3',
#                         'dayvol': 17.326, 'weekvol': 17.326,
#                         'monthvol': 383.157,
#                         'dayweekmonthvolunits': 'kWh',
#                         'mprn': 'wxyz',
#                         'supplier': '---',
#                         'price': {'unitrate': 0.03623,
#                                   'standingcharge': 0.168}}}}}
METRIC = "glowprom_{metric}"
METRIC_KEYS = "{{type=\"{type}\", {idname}=\"{idvalue}\"}}"

METRIC_METADATA = {
    "octopus_cost": ("The cost of energy used", "counter"),
}

METRIC_HELP = "# HELP {metric} {help}"
METRIC_TYPE = "# TYPE {metric} {type}"

ELECTRIC_LAST_MSG: Optional[datetime] = None
GAS_LAST_MSG: Optional[datetime] = None

ELECTRIC_CUM: Optional[float] = None
GAS_CUM: Optional[float] = None

ELECTRIC_LAST_POWER: Optional[float] = None
ELECTRIC_EXPORT: float = 0.0

ELECTRIC_COST: Optional[float] = None
ELECTRIC_FEED_IN: Optional[float] = None
GAS_COST: Optional[float] = None


def glow_msg(client, userdata, msg: Any) -> None:
    global ELECTRIC_LAST_MSG, GAS_LAST_MSG, \
           ELECTRIC_COST, GAS_COST, \
           ELECTRIC_CUM, GAS_CUM, ELECTRIC_FEED_IN, \
           ELECTRIC_LAST_POWER, ELECTRIC_EXPORT
    # # Code adapted from
    # # https://gist.github.com/ndfred/b373eeafc4f5b0870c1b8857041289a9
    payload = json.loads(msg.payload)

    key = list(payload.keys())[0]
    energy = payload[key]["energy"]

    now = datetime.utcnow()
    if key == "electricitymeter":
        power = get_power(payload[key]["power"])
        mpan = energy["import"]["mpan"]
        if mpan.lower() == "read pending":
            return

        #    convert_units(energy["export"]["cumulative"],
        #                  energy["export"]["units"])

        import_cum = convert_units(energy["import"]["cumulative"],
                                   energy["import"]["units"])

        if ELECTRIC_LAST_MSG is None or ELECTRIC_COST is None \
           or ELECTRIC_CUM is None:
            ELECTRIC_LAST_MSG = now
            ELECTRIC_COST = 0.0
            ELECTRIC_FEED_IN = 0.0
            ELECTRIC_CUM = import_cum
            ELECTRIC_LAST_POWER = power
            ELECTRIC_EXPORT = 0
        else:
            if now.date() != ELECTRIC_LAST_MSG.date():
                ELECTRIC_COST += get_electricity_standing_charge(now)

            gap_since = (now - ELECTRIC_LAST_MSG).total_seconds()
            if gap_since < 300:
                assert ELECTRIC_LAST_POWER is not None
                if ELECTRIC_LAST_POWER <= 0 and power <= 0:
                    avg_power = abs((power + ELECTRIC_LAST_POWER) / 2)
                    sys.stderr.write(f"power both: {power} + {ELECTRIC_LAST_POWER}\n")
                elif ELECTRIC_LAST_POWER <= 0 and power > 0:
                    avg_power = abs(ELECTRIC_LAST_POWER / 2)
                    sys.stderr.write(f"power last {ELECTRIC_LAST_POWER}\n")
                elif ELECTRIC_LAST_POWER > 0 and power <= 0:
                    avg_power = abs(power / 2)
                    sys.stderr.write(f"power this {power}\n")
                else:
                    avg_power = 0
                exported = ELECTRIC_EXPORT \
                    + avg_power * (gap_since / (60 * 60))
            else:
                exported = ELECTRIC_EXPORT

            ELECTRIC_LAST_POWER = power

            ELECTRIC_LAST_MSG = now
            ELECTRIC_COST += \
                (import_cum - ELECTRIC_CUM) * get_electricity_price(now)
            ELECTRIC_FEED_IN += \
                (exported - ELECTRIC_EXPORT) * get_export_price(now)
            ELECTRIC_CUM = import_cum
            ELECTRIC_EXPORT = exported

    elif key == "gasmeter":
        mprn = energy["import"]["mprn"]
        if mprn.lower() == "read pending":
            return

        gas_cum = convert_units(energy["import"]["cumulative"],
                                energy["import"]["units"])
        if GAS_LAST_MSG is None or GAS_COST is None or GAS_CUM is None:
            GAS_LAST_MSG = now
            GAS_COST = 0.0
            GAS_CUM = gas_cum
        else:
            if now.date() != GAS_LAST_MSG.date():
                GAS_COST += get_gas_standing_charge(now)

            GAS_LAST_MSG = now

            GAS_COST += (gas_cum - GAS_CUM) * get_gas_price(now)

            GAS_CUM = gas_cum
    else:
        print(f"Unknown payload type {key}")


def get_glow_metrics() -> str:
    if ELECTRIC_COST is None:
        return ""
    return f"""
# HELP octopus_cost The total cost of energy.
# TYPE octopus_cost counter
octopus_cost{{type="electric"}} {ELECTRIC_COST}
octopus_cost{{type="gas"}} {GAS_COST}

# HELP octopus_feed_in The amount earn from feed in
# TYPE octopus_feed_in counter
octopus_feed_in{{type="electric"}} {ELECTRIC_FEED_IN}

# HELP octopus_export The total kwh exported
# TYPE octopus_export counter
octopus_export {ELECTRIC_EXPORT}
"""


def convert_units(value: float, units: str) -> float:
    if units == "kW" or units == "kWh":
        return value
    return value / 1000.0


def get_power(msg) -> float:
    return convert_units(msg["value"], msg["units"])
