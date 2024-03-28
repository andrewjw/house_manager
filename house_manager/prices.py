from datetime import datetime
import zoneinfo

london = zoneinfo.ZoneInfo("Europe/London")


def get_electricity_price(dt: datetime) -> float:
    localtime = dt.astimezone(london)
    cheap_rate = (localtime.hour == 0 and localtime.hour >= 30) \
        or localtime.hour in (1, 2, 3) \
        or (localtime.hour == 4 and localtime.hour < 30)

    if dt >= datetime(2024, 4, 1):
        return 0.09 if cheap_rate else 0.27936
    return 0.09 if cheap_rate else 0.3103


def get_electricity_standing_charge(dt: datetime) -> float:
    if dt >= datetime(2024, 4, 1):
        return 0.47849
    return 0.4201


def get_gas_price(dt: datetime) -> float:
    if dt >= datetime(2024, 4, 1):
        return 0.05963
    return 0.0731


def get_gas_standing_charge(dt: datetime) -> float:
    if dt >= datetime(2024, 4, 1):
        return 0.28949
    return 0.2747
