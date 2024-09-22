"""Types for library users."""

import datetime as dt
import enum
from dataclasses import dataclass
from typing import Literal


class TrafficLightColor(enum.StrEnum):
    """Color of a traffic light."""

    RED = enum.auto()
    YELLOW = enum.auto()
    GREEN = enum.auto()


UNKNOWN = "UNKNOWN"


@dataclass
class Quantity:
    """A representation of a physical quantity, by value and unit."""

    value: float
    unit: str


@dataclass
class TrafficLightStatus:
    """Data returned via the traffic light page."""

    color: TrafficLightColor | Literal[UNKNOWN]
    current_energy_price: Quantity | Literal[UNKNOWN]


@dataclass
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


@dataclass
class Consumption:
    """Indicates the amount of consumption at a specific time."""

    start: dt.datetime
    period: dt.timedelta

    value: float
    unit: str
