import argparse
from datetime import datetime, UTC
from time import sleep
from threading import Thread
from typing import Optional
import sys

from prometheus_api_client import PrometheusConnect  # type: ignore
import requests

from .prices import get_water_price, get_water_standing_charge
from .utils import report_exception


class WaterCost:
    def __init__(self) -> None:
        self.last_update: Optional[datetime] = None
        self.prev_usage: Optional[float] = None
        self.cost = 0.0
        self.thread: Optional[Thread] = None

    def start(self, args: argparse.Namespace) -> None:
        self._prom = PrometheusConnect(url=args.prometheus)

        self.thread = Thread(target=self._update)
        self.thread.daemon = False
        self.thread.start()

    @report_exception
    def _update(self) -> None:
        while True:
            dt = datetime.now(UTC)
            try:
                data = self._prom.get_current_metric_value(
                    metric_name="watermeter_count"
                )
            except (requests.ConnectionError, requests.exceptions.RetryError) as e:
                sys.stderr.write(f"Error querying water usage - {e}\n")
                sys.stderr.flush()
                data = []

            if len(data) == 0:
                sleep(30)
                continue

            usage = float(data[0]["value"][1])

            if self.last_update is not None and self.last_update.date() != dt.date():
                self.cost += get_water_standing_charge(dt)

            self.last_update = dt

            if self.prev_usage is None or self.prev_usage > usage:
                self.prev_usage = usage
            elif usage != self.prev_usage:
                self.cost += get_water_price(dt) * (usage - self.prev_usage)
                self.prev_usage = usage

            sleep(30)
