"""Tests for the oocone.Enocoo.get_traffic_light_status() method."""

import pytest

from oocone import Auth, Enocoo
from oocone.types import TrafficLightColor
from tests import TIMEZONE


@pytest.mark.asyncio
async def test_happy_path(mock_auth: Auth) -> None:
    """Check that Enocoo.get_traffic_light_status successfully returns for mock API data."""
    enocoo = Enocoo(mock_auth, TIMEZONE)
    result = await enocoo.get_traffic_light_status()
    assert isinstance(result.color, TrafficLightColor)
    assert isinstance(result.current_energy_price.value, float)
