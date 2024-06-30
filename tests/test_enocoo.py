"""Tests for oocone.Enocoo."""

from datetime import datetime

import pytest

from oocone import Auth, Enocoo
from oocone.types import MeterStatus, TrafficLightColor

from . import TIMEZONE


@pytest.mark.asyncio()
@pytest.mark.mocked_api()
@pytest.mark.filterwarnings("ignore::bs4.MarkupResemblesLocatorWarning")  # false-positive
async def test_get_traffic_light_status(mock_auth: Auth) -> None:
    """Check that Enocoo.get_traffic_light_status successfully returns for mock API data."""
    enocoo = Enocoo(mock_auth, TIMEZONE)
    result = await enocoo.get_traffic_light_status()
    assert isinstance(result.color, TrafficLightColor)
    assert isinstance(result.current_energy_price, float)


@pytest.mark.asyncio()
@pytest.mark.mocked_api()
async def test_get_meter_table(mock_auth: Auth) -> None:
    """Check that Enocoo.get_traffic_light_status successfully returns for mock API data."""
    expected = [
        MeterStatus(
            name="Verbrauch Kaltwasser H12W34 Bad",
            area="H12W34",
            meter_id="00000001",
            timestamp=datetime(2021, 1, 1, 12, 34, 56, tzinfo=TIMEZONE),
            reading=1234.56,
            unit="m³",
        ),
        MeterStatus(
            name="Verbrauch Kaltwasser H12W34 WC",
            area="H12W34",
            meter_id="00000002",
            timestamp=datetime(2021, 1, 1, 12, 34, 56, tzinfo=TIMEZONE),
            reading=1234.56,
            unit="m³",
        ),
        MeterStatus(
            name="Verbrauch Strom H12W34",
            area="H12W34",
            meter_id="00000003",
            timestamp=datetime(2021, 1, 1, 12, 34, 56, tzinfo=TIMEZONE),
            reading=1234.56,
            unit="kWh",
        ),
        MeterStatus(
            name="Verbrauch Wärme H12W34",
            area="H12W34",
            meter_id="00000004",
            timestamp=datetime(2021, 1, 1, 12, 34, 56, tzinfo=TIMEZONE),
            reading=1234.56,
            unit="kWh",
        ),
        MeterStatus(
            name="Verbrauch Warmwasser H12W34 Bad",
            area="H12W34",
            meter_id="00000005",
            timestamp=datetime(2021, 1, 1, 12, 34, 56, tzinfo=TIMEZONE),
            reading=1234.56,
            unit="m³",
        ),
        MeterStatus(
            name="Verbrauch Warmwasser H12W34 WC",
            area="H12W34",
            meter_id="00000006",
            timestamp=datetime(2021, 1, 1, 12, 34, 56, tzinfo=TIMEZONE),
            reading=1234.56,
            unit="m³",
        ),
    ]

    enocoo = Enocoo(mock_auth, timezone=TIMEZONE)
    result = await enocoo.get_meter_table()
    assert result == expected
