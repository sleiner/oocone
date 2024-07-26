import datetime as dt
import json
import logging
import re
from functools import lru_cache

from oocone.auth import Auth
from oocone.errors import UnexpectedResponse
from oocone.types import Consumption, ConsumptionType

logger = logging.getLogger(__name__)

_CONSUMPTION_CLASSES = {
    ConsumptionType.ELECTRICITY: "Stromverbrauch",
    ConsumptionType.HEAT: "Waerme",
    ConsumptionType.WATER_COLD: "Kaltwasser",
    ConsumptionType.WATER_HOT: "Warmwasser",
}

_CONSUMPTION_UNITS = {
    ConsumptionType.ELECTRICITY: "kWh",
    ConsumptionType.HEAT: "kWh",
    ConsumptionType.WATER_COLD: "m³",
    ConsumptionType.WATER_HOT: "m³",
}

NUM_MONTHS = 12


@lru_cache
async def get_area_ids(auth: Auth) -> list[str]:
    response, _ = await auth.request("GET", "php/ownConsumption.php")
    html = await response.text()

    try:
        area_id = re.search(r'var chosenResidenceId = "(\d+)";', html)[1]
    except Exception as e:
        msg = "Could not scrape area ID from embedded JavaScript code"
        raise UnexpectedResponse(msg) from e

    return [area_id]


async def get_daily_consumption(
    consumption_type: ConsumptionType, area_id: str, date: dt.date, timezone: dt.tzinfo, auth: Auth
) -> list[Consumption]:
    response, _ = await auth.request(
        "GET",
        "php/getMeterDataWithParam.php",
        params={
            "AreaId": area_id,
            "from": date.isoformat(),
            "intVal": "Tag",
            "mClass": _CONSUMPTION_CLASSES[consumption_type],
        },
    )
    return parse_daily_consumption(
        daily_consumption_json=await response.text(),
        unit=_CONSUMPTION_UNITS[consumption_type],
        date=date,
        timezone=timezone,
        values_are_integrated=(consumption_type == ConsumptionType.HEAT),
    )


async def get_yearly_consumption(
    consumption_type: ConsumptionType, area_id: str, year_number: int, auth: Auth
) -> list[Consumption]:
    response, _ = await auth.request(
        "GET",
        "php/getMeterDataWithParam.php",
        params={
            "AreaId": area_id,
            "from": f"{year_number}-01-01",
            "intVal": "Jahr",
            "mClass": _CONSUMPTION_CLASSES[consumption_type],
        },
    )
    return parse_yearly_consumption(
        yearly_consumption_json=await response.text(),
        unit=_CONSUMPTION_UNITS[consumption_type],
        year_number=year_number,
    )


def parse_daily_consumption(
    *,
    daily_consumption_json: str,
    values_are_integrated: bool,
    unit: str,
    date: dt.date,
    timezone: dt.tzinfo,
) -> list[Consumption]:
    results = []

    json_data = json.loads(daily_consumption_json)
    hours = json_data[1]
    values = json_data[0]

    last_time = dt.datetime(
        date.year, date.month, date.day, hour=0, minute=0, second=0, tzinfo=timezone
    )
    last_hour = None
    last_value = 0
    period = dt.timedelta(minutes=15)

    for hour, value in zip(hours, values, strict=False):
        if last_hour is not None and hour < last_hour:
            logger.warning(
                "Hours are unordered in daily consumption reading for %s: hour %s follows hour %s."
                " Consumption metric is discarded.",
                date.isoformat(),
                hour,
                last_hour,
            )
            continue
        if hour == last_hour:
            time = last_time + period
        else:
            time = last_time.replace(hour=hour, minute=0)

        if values_are_integrated:
            consumption_value = float(value) - float(last_value)
        else:
            consumption_value = float(value)

        consumption = Consumption(start=time, period=period, value=consumption_value, unit=unit)
        results.append(consumption)

        last_time = time
        last_hour = hour
        last_value = value

    return results


def parse_yearly_consumption(
    *,
    yearly_consumption_json: str,
    unit: str,
    year_number: int,
) -> list[Consumption]:
    results = []

    month_names_to_number = {
        "Jan.": 1,
        "Feb.": 2,
        "Mär.": 3,
        "Apr.": 4,
        "Mai": 5,
        "Jun.": 6,
        "Jul.": 7,
        "Aug.": 8,
        "Sep.": 9,
        "Okt.": 10,
        "Nov.": 11,
        "Dez.": 12,
    }

    json_data = json.loads(yearly_consumption_json)
    month_names = json_data[1]
    values = json_data[0]

    for month_name, value in zip(month_names, values, strict=False):
        month = month_names_to_number[month_name]

        begin_of_month = dt.date(year_number, month, 1)
        begin_of_next_month = dt.date(
            year_number if month < NUM_MONTHS else year_number + 1,
            month + 1 if month < NUM_MONTHS else 1,
            1,
        )
        consumption = Consumption(
            start=begin_of_month,
            period=begin_of_next_month - begin_of_month,
            value=value,
            unit=unit,
        )
        results.append(consumption)

    return results
