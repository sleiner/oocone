"""Tests for oocone.Enocoo."""

import datetime as dt

import pytest

from oocone import Auth, Enocoo
from oocone.types import ConsumptionType, MeterStatus, TrafficLightColor

from . import TIMEZONE


@pytest.mark.asyncio()
@pytest.mark.filterwarnings("ignore::bs4.MarkupResemblesLocatorWarning")  # false-positive
async def test_get_traffic_light_status(mock_auth: Auth) -> None:
    """Check that Enocoo.get_traffic_light_status successfully returns for mock API data."""
    enocoo = Enocoo(mock_auth, TIMEZONE)
    result = await enocoo.get_traffic_light_status()
    assert isinstance(result.color, TrafficLightColor)
    assert isinstance(result.current_energy_price, float)


@pytest.mark.asyncio()
async def test_get_meter_table(mock_auth: Auth) -> None:
    """Check that Enocoo.get_traffic_light_status successfully returns for mock API data."""
    expected = [
        MeterStatus(
            name="Verbrauch Kaltwasser H12W34 Bad",
            area="H12W34",
            meter_id="00000001",
            timestamp=dt.datetime(2021, 1, 1, 12, 34, 56, tzinfo=TIMEZONE),
            reading=1234.56,
            unit="m³",
        ),
        MeterStatus(
            name="Verbrauch Kaltwasser H12W34 WC",
            area="H12W34",
            meter_id="00000002",
            timestamp=dt.datetime(2021, 1, 1, 12, 34, 56, tzinfo=TIMEZONE),
            reading=1234.56,
            unit="m³",
        ),
        MeterStatus(
            name="Verbrauch Strom H12W34",
            area="H12W34",
            meter_id="00000003",
            timestamp=dt.datetime(2021, 1, 1, 12, 34, 56, tzinfo=TIMEZONE),
            reading=1234.56,
            unit="kWh",
        ),
        MeterStatus(
            name="Verbrauch Wärme H12W34",
            area="H12W34",
            meter_id="00000004",
            timestamp=dt.datetime(2021, 1, 1, 12, 34, 56, tzinfo=TIMEZONE),
            reading=1234.56,
            unit="kWh",
        ),
        MeterStatus(
            name="Verbrauch Warmwasser H12W34 Bad",
            area="H12W34",
            meter_id="00000005",
            timestamp=dt.datetime(2021, 1, 1, 12, 34, 56, tzinfo=TIMEZONE),
            reading=1234.56,
            unit="m³",
        ),
        MeterStatus(
            name="Verbrauch Warmwasser H12W34 WC",
            area="H12W34",
            meter_id="00000006",
            timestamp=dt.datetime(2021, 1, 1, 12, 34, 56, tzinfo=TIMEZONE),
            reading=1234.56,
            unit="m³",
        ),
    ]

    enocoo = Enocoo(mock_auth, timezone=TIMEZONE)
    result = await enocoo.get_meter_table()
    assert result == expected


@pytest.mark.asyncio()
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
async def test_get_individual_consumption_day(
    date: dt.date, consumption_type: ConsumptionType, mock_auth: Auth
) -> None:
    """Check that enocoo.get_individual_consumption returns daily data in expected format."""
    enocoo = Enocoo(mock_auth, TIMEZONE)
    consumption = await enocoo.get_individual_consumption(
        consumption_type=consumption_type, area_id="123", during=date, interval="day"
    )

    for hour in {cons.start.hour for cons in consumption}:
        num_readings = len([cons for cons in consumption if cons.start.hour == hour])
        assert num_readings == 4, "consumption should contain 4 readings per hour"  # noqa: PLR2004


@pytest.mark.asyncio()
@pytest.mark.parametrize(
    "consumption_type",
    [
        ConsumptionType.ELECTRICITY,
        ConsumptionType.WATER_COLD,
        ConsumptionType.WATER_HOT,
        ConsumptionType.HEAT,
    ],
)
async def test_get_individual_consumption_year(
    consumption_type: ConsumptionType, mock_auth: Auth
) -> None:
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


@pytest.mark.asyncio()
async def test_get_area_ids(mock_auth: Auth) -> None:
    """Check that enocoo.get_area_ids returns the area ID as indicated in ownConsumption.php."""
    enocoo = Enocoo(mock_auth, TIMEZONE)
    ids = await enocoo.get_area_ids()
    assert ids == ["123"]
