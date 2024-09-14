"""Tests for the oocone.Enocoo.get_meter_table() method."""

import datetime as dt

import pytest

from oocone import Auth, Enocoo
from oocone.types import MeterStatus
from tests import TIMEZONE


def _expected_meter_table(date: dt.date) -> list[MeterStatus]:
    expected_timestamp = dt.datetime(date.year, date.month, date.day, 12, 34, 56, tzinfo=TIMEZONE)
    return [
        MeterStatus(
            name="Verbrauch Kaltwasser H12W34 Bad",
            area="H12W34",
            meter_id="00000001",
            timestamp=expected_timestamp,
            reading=1234.56,
            unit="m³",
        ),
        MeterStatus(
            name="Verbrauch Kaltwasser H12W34 WC",
            area="H12W34",
            meter_id="00000002",
            timestamp=expected_timestamp,
            reading=1234.56,
            unit="m³",
        ),
        MeterStatus(
            name="Verbrauch Strom H12W34",
            area="H12W34",
            meter_id="00000003",
            timestamp=expected_timestamp,
            reading=1234.56,
            unit="kWh",
        ),
        MeterStatus(
            name="Verbrauch Wärme H12W34",
            area="H12W34",
            meter_id="00000004",
            timestamp=expected_timestamp,
            reading=1234.56,
            unit="kWh",
        ),
        MeterStatus(
            name="Verbrauch Warmwasser H12W34 Bad",
            area="H12W34",
            meter_id="00000005",
            timestamp=expected_timestamp,
            reading=1234.56,
            unit="m³",
        ),
        MeterStatus(
            name="Verbrauch Warmwasser H12W34 WC",
            area="H12W34",
            meter_id="00000006",
            timestamp=expected_timestamp,
            reading=1234.56,
            unit="m³",
        ),
    ]


@pytest.mark.asyncio
async def test_without_params(mock_auth: Auth) -> None:
    """Check that the function returns data for the current day when called without parameters."""
    expected = _expected_meter_table(dt.datetime.now(tz=TIMEZONE).date())

    enocoo = Enocoo(mock_auth, timezone=TIMEZONE)
    result = await enocoo.get_meter_table()

    assert result == expected


@pytest.mark.asyncio
async def test_with_date_param(mock_auth: Auth) -> None:
    """Check that when called with a date param, the function returns data for that day."""
    date = dt.date(2012, 12, 12)
    expected = _expected_meter_table(date)

    enocoo = Enocoo(mock_auth, timezone=TIMEZONE)
    result = await enocoo.get_meter_table(date=date)

    assert result == expected
