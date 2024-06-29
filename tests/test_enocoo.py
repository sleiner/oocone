"""Tests for oocone.Enocoo."""

import pytest

from oocone import Auth, Enocoo
from oocone.types import TrafficLightColor


@pytest.mark.asyncio()
@pytest.mark.mocked_api()
@pytest.mark.filterwarnings("ignore::bs4.MarkupResemblesLocatorWarning")  # false-positive
async def test_get_traffic_light_status(mock_auth: Auth) -> None:
    """Check that Enocoo.get_traffic_light_status successfully returns for mock API data."""
    enocoo = Enocoo(mock_auth)
    result = await enocoo.get_traffic_light_status()
    assert isinstance(result.color, TrafficLightColor)
    assert isinstance(result.current_energy_price, float)
