import datetime as dt
import json
import logging
import re
from collections.abc import Mapping
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


@lru_cache
async def _get_area_ids(auth: Auth) -> list[str]:
    response, _ = await auth.request("GET", "php/ownConsumption.php")
    html = await response.text()

    try:
        area_id = re.search(r'var chosenResidenceId = "(\d+)";', html)[1]
    except Exception as e:
        msg = "Could not scrape area ID from embedded JavaScript code"
        raise UnexpectedResponse(msg) from e

    return [area_id]


async def get_daily_consumption(
    consumption_type: ConsumptionType, date: dt.date, timezone: dt.tzinfo, auth: Auth
) -> Mapping[str, list[Consumption]]:
    results = {}
    for area_id in await _get_area_ids(auth):
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
        results[area_id] = parse_daily_consumption(
            daily_consumption_json=await response.text(),
            unit=_CONSUMPTION_UNITS[consumption_type],
            date=date,
            timezone=timezone,
            values_are_integrated=(consumption_type == ConsumptionType.HEAT),
        )
    return results


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
