import datetime as dt
import json
import logging
from typing import Any

from oocone._internal.scrape_timeseries import discard_unordered_hours, get_periods_per_hour
from oocone.auth import Auth
from oocone.model import PhotovoltaicSummary, Quantity

logger = logging.getLogger(__name__)


async def get_daily_photovoltaic_data(
    date: dt.date, timezone: dt.tzinfo, auth: Auth
) -> list[PhotovoltaicSummary]:
    logger.debug("Scraping daily photovoltaic data on %s...", date)
    response, _ = await auth.request(
        "GET",
        "php/getPVDataDetails.php",
        params={
            "from": date.isoformat(),
            "intVal": "Tag",
            "diagType": "GesamtverbrauchUndErzeugung",
        },
    )
    return _parse_daily_photovoltaic_data(
        data=await response.text(),
        unit="kWh",
        date=date,
        timezone=timezone,
    )


def _parse_daily_photovoltaic_data(
    *,
    data: str,
    unit: str,
    date: dt.date,
    timezone: dt.tzinfo,
) -> list[PhotovoltaicSummary]:
    results = []

    json_data = json.loads(data)
    values = zip(*(json_data[0:4]), strict=True)
    hours = json_data[4]

    last_time = dt.datetime(
        date.year, date.month, date.day, hour=0, minute=0, second=0, tzinfo=timezone
    )
    last_hour = None

    hours, values = discard_unordered_hours(hours, values, date, description="photovoltaic data")
    periods_per_hour = get_periods_per_hour(hours)

    def float_or_none(value: Any) -> float | None:
        if value is None:
            return None
        return float(value)

    for hour, value in zip(hours, values, strict=False):
        period = periods_per_hour[hour]

        if hour == last_hour:
            time = last_time + period
        else:
            time = last_time.replace(hour=hour, minute=0)

        summary = PhotovoltaicSummary(
            start=time,
            period=period,
            consumption=Quantity(value=float(value[0]), unit=unit),
            generation=Quantity(value=float(value[1]), unit=unit),
            self_sufficiency=float_or_none(value[2]),
            own_consumption=float_or_none(value[3]),
        )
        results.append(summary)

        last_time = time
        last_hour = hour

    return results
