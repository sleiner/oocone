import datetime as dt
import logging
from collections import Counter
from collections.abc import Iterable

logger = logging.getLogger(__name__)


def get_periods_per_hour(hours: list[int]) -> dict[int, dt.timedelta]:
    one_hour = dt.timedelta(hours=1)
    max_period = dt.timedelta(minutes=15)

    return {
        hour: min(one_hour / measurements_per_hour, max_period)
        for hour, measurements_per_hour in Counter(hours).items()
    }


def discard_unordered_hours[ValueT](
    hours: Iterable[int],
    values: Iterable[ValueT],
    date: dt.date,
    *,
    description: str,
    stop_after_midnight: bool = True,
) -> (list[int], list[ValueT]):
    filtered_hours = []
    filtered_values = []

    last_hour = None

    for hour, value in zip(hours, values, strict=False):
        if stop_after_midnight and last_hour == 23 and hour != last_hour:  # noqa: PLR2004
            # hour after midnight -> discard
            break
        if last_hour is not None and hour < last_hour:
            logger.warning(
                "Hours are unordered in daily %s reading for %s: hour %s follows hour %s."
                " %s metric is discarded.",
                description,
                date.isoformat(),
                hour,
                last_hour,
                description.capitalize(),
            )
            continue

        filtered_hours.append(hour)
        filtered_values.append(value)
        last_hour = hour

    return filtered_hours, filtered_values
