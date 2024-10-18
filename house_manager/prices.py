from datetime import date, datetime, timedelta
import zoneinfo

LONDON = zoneinfo.ZoneInfo("Europe/London")


def get_electricity_price(dt: datetime) -> float:
    localtime = dt.astimezone(LONDON)
    cheap_rate = (localtime.hour == 0 and localtime.minute >= 30) \
        or localtime.hour in (1, 2, 3) \
        or ((localtime.hour == 4 or (localtime.hour == 5 and localtime.minute < 30)) \
            if dt >= datetime(2024, 7, 1, tzinfo=LONDON) else
            (localtime.hour == 4 and localtime.minute < 30))

    if (dt.date() == date(2024, 8, 15) and localtime.hour == 13) \
       or (dt.date() == date(2024, 8, 31) and localtime.hour == 13) \
       or (dt.date() == date(2024, 9, 10) and localtime.hour == 13):
        return 0
    if dt >= datetime(2024, 10, 1):
        return 0.085 if cheap_rate else 0.26716
    if dt >= datetime(2024, 7, 1):
        return 0.085 if cheap_rate else 0.24393
    if localtime >= datetime(2024, 4, 1, tzinfo=LONDON):
        return 0.09 if cheap_rate else 0.27936
    return 0.09 if cheap_rate else 0.3103


def is_cheap_rate(dt: datetime) -> bool:
    return get_electricity_price(dt) <= 0.1


def get_cheap_rate_end(dt: datetime) -> datetime:
    while is_cheap_rate(dt):
        dt += timedelta(minutes=1)
    return dt


def get_export_price(dt: datetime) -> float:
    return 0.08


def get_electricity_standing_charge(dt: datetime) -> float:
    if dt >= datetime(2024, 10, 1, tzinfo=LONDON):
        return 0.48788
    if dt >= datetime(2024, 4, 1, tzinfo=LONDON):
        return 0.47849
    return 0.4201


def get_gas_price(dt: datetime) -> float:
    if dt >= datetime(2024, 10, 1, tzinfo=LONDON):
        return 0.06161
    if dt >= datetime(2024, 7, 1, tzinfo=LONDON):
        return 0.05402
    if dt >= datetime(2024, 4, 1, tzinfo=LONDON):
        return 0.05963
    return 0.0731


def get_gas_standing_charge(dt: datetime) -> float:
    if dt >= datetime(2024, 10, 1, tzinfo=LONDON):
        return 0.29379
    if dt >= datetime(2024, 4, 1, tzinfo=LONDON):
        return 0.28949
    return 0.2747


def get_water_price(dt: datetime) -> float:
    return (1.2668 + 1.1537) / 1000


def get_water_standing_charge(dt: datetime) -> float:
    return 0.3136
