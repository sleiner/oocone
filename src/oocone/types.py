"""Types for library users."""

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
class TrafficLightStatus:
    """Data returned via the traffic light page."""

    color: TrafficLightColor | Literal[UNKNOWN]
    current_energy_price: float | Literal[UNKNOWN]
