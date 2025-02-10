"""Types for library users."""

import datetime as dt
import enum
from dataclasses import dataclass
from functools import cached_property
from typing import Literal


class TrafficLightColor(enum.StrEnum):
    """Color of a traffic light."""

    RED = enum.auto()
    YELLOW = enum.auto()
    GREEN = enum.auto()


UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class Quantity:
    """A representation of a physical quantity, by value and unit."""

    value: float
    unit: str


@dataclass(frozen=True)
class TrafficLightStatus:
    """Data returned via the traffic light page."""

    color: TrafficLightColor | Literal[UNKNOWN]
    current_energy_price: Quantity | Literal[UNKNOWN]


@dataclass(frozen=True)
class MeterStatus:
    """Information about a meter and its current state."""

    name: str
    area: str
    meter_id: str
    timestamp: dt.datetime
    reading: Quantity


class ConsumptionType(enum.StrEnum):
    """Type of thing to consume (i.e. something that would be measured by a utility meter)."""

    ELECTRICITY = enum.auto()
    WATER_HOT = enum.auto()
    WATER_COLD = enum.auto()
    HEAT = enum.auto()


@dataclass(frozen=True)
class Consumption:
    """Indicates the amount of consumption at a specific time."""

    start: dt.datetime
    period: dt.timedelta

    value: float
    unit: str


@dataclass(frozen=True)
class PhotovoltaicSummary:
    """Information about the quarter's solar generation and power consumption in a given period."""

    start: dt.datetime
    period: dt.timedelta

    consumption: Quantity
    generation: Quantity

    @cached_property
    def calculated_feed_into_grid(self) -> Quantity:
        """The (calculated) amount of energy being fed into the electrical grid."""
        if self.own_consumption is None:
            # We know: own_consumption = consumption_from_pv / pv_generation
            # own_consumption can not be calculated if pv_generation is 0.
            # But if pv_generation is 0, the feed into grid is also 0.
            return Quantity(value=0.0, unit=self.generation.unit)

        feed_factor = 1.0 - (self.own_consumption / 100.0)
        return Quantity(value=self.generation * feed_factor, unit=self.generation.unit)

    @cached_property
    def calculated_supply_from_grid(self) -> Quantity:
        """The (calculated) amount of energy being pulled from the electrical grid."""
        # We know: self_sufficiency = pv_usage / (pv_usage + supply_from_grid)
        #     and:      consumption = pv_usage + supply_from_grid
        # =>       supply_from_grid = consumption * (1 - self_sufficiency)
        if self.self_sufficiency is None:
            # self_sufficiency is only None when the PV production is 0.
            # In that case, we pull all power from the grid.
            return self.consumption

        supply_factor = 1.0 - (self.self_sufficiency / 100.0)
        return Quantity(self.consumption * supply_factor, unit=self.consumption.unit)

    self_sufficiency: float | None
    own_consumption: float | None
