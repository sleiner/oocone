"""Tests for the oocone.Enocoo.get_individual_consumption() method."""

import datetime as dt

import pytest

from oocone import Auth, Enocoo
from oocone.types import ConsumptionType
from tests import TIMEZONE


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "date",
    [
        pytest.param(dt.date(2024, 1, 1), id="regular day"),
        pytest.param(dt.date(2023, 10, 29), id="summer time to winter time"),
        pytest.param(dt.date(2024, 3, 31), id="winter time to summer time"),
    ],
)
@pytest.mark.parametrize(
    "consumption_type",
    [
        ConsumptionType.ELECTRICITY,
        ConsumptionType.WATER_COLD,
        ConsumptionType.WATER_HOT,
        ConsumptionType.HEAT,
    ],
)
async def test_daily(date: dt.date, consumption_type: ConsumptionType, mock_auth: Auth) -> None:
    """Check that enocoo.get_individual_consumption returns daily data in expected format."""
    enocoo = Enocoo(mock_auth, TIMEZONE)
    consumption = await enocoo.get_individual_consumption(
        consumption_type=consumption_type, area_id="123", during=date, interval="day"
    )

    for hour in {cons.start.hour for cons in consumption}:
        period_sum = sum(
            [cons.period for cons in consumption if cons.start.hour == hour], start=dt.timedelta()
        )
        assert period_sum == dt.timedelta(
            hours=1
        ), f"periods for hour {hour} should add up to one hour"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "consumption_type",
    [
        ConsumptionType.ELECTRICITY,
        ConsumptionType.WATER_COLD,
        ConsumptionType.WATER_HOT,
        ConsumptionType.HEAT,
    ],
)
async def test_yearly(consumption_type: ConsumptionType, mock_auth: Auth) -> None:
    """Check that enocoo.get_individual_consumption returns yearly data in expected format."""
    enocoo = Enocoo(mock_auth, TIMEZONE)
    consumption = await enocoo.get_individual_consumption(
        consumption_type=consumption_type,
        area_id="123",
        during=dt.date(2024, 1, 1),
        interval="year",
    )

    for reading in consumption:
        match reading.start.month:
            case 1 | 3 | 5 | 7 | 8 | 10 | 12:
                assert reading.period == dt.timedelta(days=31)
            case 2:
                assert reading.period == dt.timedelta(days=29)
            case 4 | 6 | 9 | 11:
                assert reading.period == dt.timedelta(days=30)
