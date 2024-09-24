"""Tests for the oocone.Enocoo.get_individual_consumption() method."""

import datetime as dt
import json

import pytest

from oocone import Auth, Enocoo
from oocone._internal.scrape_consumption import _CONSUMPTION_CLASSES as CONSUMPTION_CLASSES
from oocone.types import ConsumptionType
from tests import RESPONSES_DIR, TIMEZONE


def _get_consumption_sum(
    consumption_type: ConsumptionType, *, date: dt.date, interval: str, compensate_off_by_one: bool
) -> float:
    def enocoo_response(request_date: dt.date) -> list:
        response_path = (
            RESPONSES_DIR
            / "getMeterDataWithParam.{consumption}.{date}.{interval}.php".format(  # noqa: UP032
                consumption=CONSUMPTION_CLASSES[consumption_type],
                date=request_date.isoformat(),
                interval=interval,
            )
        )

        with response_path.open("rb") as response_file:
            response = response_file.read()

        return json.loads(response)

    if consumption_type == ConsumptionType.HEAT:
        # Heat readings are integrated, so we need to calculate differences
        raw_readings = enocoo_response(date)[0]
        readings_current_day = [raw_readings[0], raw_readings[-1] - raw_readings[0]]
    else:
        readings_current_day = enocoo_response(date)[0]
    if compensate_off_by_one:
        readings_next_day = enocoo_response(date + dt.timedelta(days=1))[0]
        relevant_readings = readings_current_day[1:] + readings_next_day[:1]
    else:
        relevant_readings = readings_current_day

    return sum(relevant_readings)


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
@pytest.mark.parametrize(
    "compensate_quirks",
    [
        pytest.param(False, id="uncompensated"),
        pytest.param(True, id="compensated"),
    ],
)
async def test_daily(
    *, date: dt.date, consumption_type: ConsumptionType, compensate_quirks: bool, mock_auth: Auth
) -> None:
    """Check that enocoo.get_individual_consumption returns daily data in expected format."""
    enocoo = Enocoo(mock_auth, TIMEZONE)

    consumption = await enocoo.get_individual_consumption(
        consumption_type=consumption_type,
        area_id="123",
        during=date,
        interval="day",
        compensate_off_by_one=compensate_quirks,
    )

    for hour in {cons.start.hour for cons in consumption}:
        period_sum = sum(
            [cons.period for cons in consumption if cons.start.hour == hour], start=dt.timedelta()
        )
        assert period_sum == dt.timedelta(
            hours=1
        ), f"periods for hour {hour} should add up to one hour"

    expected_sum = _get_consumption_sum(
        consumption_type, date=date, interval="Tag", compensate_off_by_one=compensate_quirks
    )
    actual_sum = sum(cons.value for cons in consumption)
    assert actual_sum == expected_sum


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

    with (
        pytest.warns(UserWarning, match="off by one"),
        pytest.warns(
            match="input looks more like a filename than markup"  # this is supposed to be filtered
        ),
    ):
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
