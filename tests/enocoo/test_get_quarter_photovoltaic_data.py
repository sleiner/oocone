"""Tests for the oocone.Enocoo.get_individual_consumption() method."""

import datetime as dt

import pytest

from oocone import Auth, Enocoo
from oocone.model import ConsumptionType, PhotovoltaicSummary, Quantity
from tests import TIMEZONE

FIFTEEN_MINUTES = dt.timedelta(seconds=720)


def _make_summaries(
    *datapoints: list[
        tuple[int, int, int, int, int, int, float, float, float | None, float | None]
    ],
) -> list[PhotovoltaicSummary]:
    result = []
    for datapoint in datapoints:
        (
            year,
            month,
            day,
            hour,
            minute,
            duration_minutes,
            consumption_kwh,
            generation_kwh,
            self_sufficiency,
            own_consumption,
        ) = datapoint
        summary = PhotovoltaicSummary(
            dt.datetime(year, month, day, hour, minute, tzinfo=TIMEZONE),
            dt.timedelta(minutes=duration_minutes),
            consumption=Quantity(consumption_kwh, "kWh"),
            generation=Quantity(generation_kwh, "kWh"),
            self_sufficiency=self_sufficiency,
            own_consumption=own_consumption,
        )
        result.append(summary)
    return result


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("date", "expected"),
    [
        pytest.param(
            dt.date(2024, 1, 1),
            _make_summaries(
                (2024, 1, 1, 0, 00, 15, 12.66, 0.0, None, None),
                (2024, 1, 1, 0, 15, 15, 14.71, 0.01, 0.07, 100.0),
                (2024, 1, 1, 0, 30, 15, 21.49, 0.02, 0.09, 100.0),
                (2024, 1, 1, 0, 45, 15, 14.71, 0.02, 0.14, 100.0),
                (2024, 1, 1, 1, 00, 15, 17.61, 0.01, 0.06, 100.0),
                (2024, 1, 1, 1, 15, 15, 24.53, 0.02, 0.08, 100.0),
                (2024, 1, 1, 1, 30, 15, 24.3, 0.01, 0.04, 100.0),
                (2024, 1, 1, 1, 45, 15, 24.46, 0.01, 0.04, 100.0),
                (2024, 1, 1, 2, 00, 15, 25.09, 0.01, 0.04, 100.0),
                (2024, 1, 1, 2, 15, 15, 25.82, 0.01, 0.04, 100.0),
                (2024, 1, 1, 2, 30, 15, 28.97, 0.02, 0.07, 100.0),
                (2024, 1, 1, 2, 45, 15, 25.36, 0.01, 0.04, 100.0),
                (2024, 1, 1, 3, 00, 15, 13.93, 0.01, 0.07, 100.0),
                (2024, 1, 1, 3, 15, 15, 10.51, 0.02, 0.19, 100.0),
                (2024, 1, 1, 3, 30, 15, 10.26, 0.0, None, None),
                (2024, 1, 1, 3, 45, 15, 10.99, 0.01, 0.09, 100.0),
                (2024, 1, 1, 4, 00, 15, 11.9, 0.02, 0.17, 100.0),
                (2024, 1, 1, 4, 15, 15, 10.28, 0.03, 0.29, 100.0),
                (2024, 1, 1, 4, 30, 15, 12.12, 0.0, None, None),
                (2024, 1, 1, 4, 45, 15, 12.79, 0.01, 0.08, 100.0),
                (2024, 1, 1, 5, 00, 15, 10.2, 0.01, 0.1, 100.0),
                (2024, 1, 1, 5, 15, 15, 10.9, 0.01, 0.09, 100.0),
                (2024, 1, 1, 5, 30, 15, 14.63, 0.01, 0.07, 100.0),
                (2024, 1, 1, 5, 45, 15, 14.98, 0.02, 0.13, 100.0),
                (2024, 1, 1, 6, 00, 15, 10.38, 0.02, 0.19, 100.0),
                (2024, 1, 1, 6, 15, 15, 9.19, 0.01, 0.11, 100.0),
                (2024, 1, 1, 6, 30, 15, 19.01, 0.01, 0.05, 100.0),
                (2024, 1, 1, 6, 45, 15, 26.15, 0.01, 0.04, 100.0),
                (2024, 1, 1, 7, 00, 15, 23.79, 0.0, None, None),
                (2024, 1, 1, 7, 15, 15, 23.6, 0.03, 0.13, 100.0),
                (2024, 1, 1, 7, 30, 15, 24.43, 0.02, 0.08, 100.0),
                (2024, 1, 1, 7, 45, 15, 26.59, 0.01, 0.04, 100.0),
                (2024, 1, 1, 8, 00, 15, 29.06, 0.0, None, None),
                (2024, 1, 1, 8, 15, 15, 15.74, 0.02, 0.13, 100.0),
                (2024, 1, 1, 8, 30, 15, 10.36, 0.04, 0.39, 100.0),
                (2024, 1, 1, 8, 45, 15, 12.46, 0.31, 2.49, 100.0),
                (2024, 1, 1, 9, 00, 15, 13.29, 0.93, 7.0, 100.0),
                (2024, 1, 1, 9, 15, 15, 11.01, 1.52, 13.81, 100.0),
                (2024, 1, 1, 9, 30, 15, 10.66, 2.08, 19.51, 100.0),
                (2024, 1, 1, 9, 45, 15, 9.96, 2.85, 28.61, 100.0),
                (2024, 1, 1, 10, 00, 15, 10.49, 2.86, 27.26, 100.0),
                (2024, 1, 1, 10, 15, 15, 10.54, 3.18, 30.17, 100.0),
                (2024, 1, 1, 10, 30, 15, 11.96, 3.1, 25.92, 100.0),
                (2024, 1, 1, 10, 45, 15, 16.22, 4.4, 27.13, 100.0),
                (2024, 1, 1, 11, 00, 15, 19.77, 4.98, 25.19, 100.0),
                (2024, 1, 1, 11, 15, 15, 17.79, 8.54, 48.0, 100.0),
                (2024, 1, 1, 11, 30, 15, 11.05, 9.29, 83.98, 99.89),
                (2024, 1, 1, 11, 45, 15, 25.27, 9.22, 36.49, 100.0),
                (2024, 1, 1, 12, 00, 15, 22.36, 8.33, 37.25, 100.0),
                (2024, 1, 1, 12, 15, 15, 24.43, 7.61, 31.15, 100.0),
                (2024, 1, 1, 12, 30, 15, 24.7, 8.91, 36.07, 100.0),
                (2024, 1, 1, 12, 45, 15, 27.36, 8.19, 29.93, 100.0),
                (2024, 1, 1, 13, 00, 15, 29.75, 7.61, 25.58, 100.0),
                (2024, 1, 1, 13, 15, 15, 35.8, 5.82, 16.26, 100.0),
                (2024, 1, 1, 13, 30, 15, 15.62, 5.78, 37.0, 100.0),
                (2024, 1, 1, 13, 45, 15, 15.93, 5.33, 33.46, 100.0),
                (2024, 1, 1, 14, 00, 15, 12.28, 4.83, 39.33, 100.0),
                (2024, 1, 1, 14, 15, 15, 11.79, 3.99, 33.84, 100.0),
                (2024, 1, 1, 14, 30, 15, 11.49, 4.85, 42.21, 100.0),
                (2024, 1, 1, 14, 45, 15, 12.11, 3.18, 26.26, 100.0),
                (2024, 1, 1, 15, 00, 15, 14.49, 2.92, 20.15, 100.0),
                (2024, 1, 1, 15, 15, 15, 15.74, 2.6, 16.52, 100.0),
                (2024, 1, 1, 15, 30, 15, 16.83, 1.92, 11.41, 100.0),
                (2024, 1, 1, 15, 45, 15, 18.14, 1.22, 6.73, 100.0),
                (2024, 1, 1, 16, 00, 15, 19.09, 0.9, 4.71, 100.0),
                (2024, 1, 1, 16, 15, 15, 16.47, 0.43, 2.61, 100.0),
                (2024, 1, 1, 16, 30, 15, 15.9, 0.09, 0.57, 100.0),
                (2024, 1, 1, 16, 45, 15, 15.39, 0.04, 0.26, 100.0),
                (2024, 1, 1, 17, 00, 15, 27.89, 0.01, 0.04, 100.0),
                (2024, 1, 1, 17, 15, 15, 30.46, 0.01, 0.03, 100.0),
                (2024, 1, 1, 17, 30, 15, 31.45, 0.01, 0.03, 100.0),
                (2024, 1, 1, 17, 45, 15, 32.04, 0.0, None, None),
                (2024, 1, 1, 18, 00, 15, 31.21, 0.01, 0.03, 100.0),
                (2024, 1, 1, 18, 15, 15, 34.22, 0.02, 0.06, 100.0),
                (2024, 1, 1, 18, 30, 15, 31.93, 0.02, 0.06, 100.0),
                (2024, 1, 1, 18, 45, 15, 17.94, 0.01, 0.06, 100.0),
                (2024, 1, 1, 19, 00, 15, 13.58, 0.01, 0.07, 100.0),
                (2024, 1, 1, 19, 15, 15, 13.4, 0.01, 0.07, 100.0),
                (2024, 1, 1, 19, 30, 15, 15.68, 0.02, 0.13, 100.0),
                (2024, 1, 1, 19, 45, 15, 13.34, 0.01, 0.07, 100.0),
                (2024, 1, 1, 20, 00, 15, 12.08, 0.01, 0.08, 100.0),
                (2024, 1, 1, 20, 15, 15, 14.97, 0.01, 0.07, 100.0),
                (2024, 1, 1, 20, 30, 15, 18.6, 0.01, 0.05, 100.0),
                (2024, 1, 1, 20, 45, 15, 14.11, 0.02, 0.14, 100.0),
                (2024, 1, 1, 21, 00, 15, 14.25, 0.01, 0.07, 100.0),
                (2024, 1, 1, 21, 15, 15, 15.07, 0.01, 0.07, 100.0),
                (2024, 1, 1, 21, 30, 15, 14.42, 0.0, None, None),
                (2024, 1, 1, 21, 45, 15, 13.73, 0.01, 0.07, 100.0),
                (2024, 1, 1, 22, 00, 15, 10.79, 0.02, 0.19, 100.0),
                (2024, 1, 1, 22, 15, 15, 15.59, 0.02, 0.13, 100.0),
                (2024, 1, 1, 22, 30, 15, 26.85, 0.02, 0.07, 100.0),
                (2024, 1, 1, 22, 45, 15, 27.52, 0.0, None, None),
                (2024, 1, 1, 23, 00, 15, 23.81, 0.01, 0.04, 100.0),
                (2024, 1, 1, 23, 15, 15, 24.99, 0.02, 0.08, 100.0),
                (2024, 1, 1, 23, 30, 15, 27.23, 0.01, 0.04, 100.0),
                (2024, 1, 1, 23, 45, 15, 28.04, 0.01, 0.04, 100.0),
            ),
            id="regular day",
        ),
        pytest.param(
            dt.date(2023, 10, 29),
            _make_summaries(
                (2023, 10, 29, 0, 00, 15, 17.43, 0.01, 0.06, 100.0),
                (2023, 10, 29, 0, 15, 15, 14.37, 0.01, 0.07, 100.0),
                (2023, 10, 29, 0, 30, 15, 11.5, 0.01, 0.09, 100.0),
                (2023, 10, 29, 0, 45, 15, 11.46, 0.01, 0.09, 100.0),
                (2023, 10, 29, 1, 00, 15, 11.94, 0.03, 0.25, 100.0),
                (2023, 10, 29, 1, 15, 15, 9.84, 0.0, None, None),
                (2023, 10, 29, 1, 30, 15, 23.48, 0.01, 0.04, 100.0),
                (2023, 10, 29, 1, 45, 15, 23.77, 0.01, 0.04, 100.0),
                (2023, 10, 29, 2, 00, 15, 31.75, 0.03, 0.09, 100.0),
                (2023, 10, 29, 2, 15, 15, 34.35, 0.02, 0.06, 100.0),
                (2023, 10, 29, 2, 30, 15, 34.22, 0.02, 0.06, 100.0),
                (2023, 10, 29, 2, 45, 15, 17.54, 0.03, 0.17, 100.0),
                (2023, 10, 29, 3, 00, 15, 7.8, 0.02, 0.26, 100.0),
                (2023, 10, 29, 3, 15, 15, 7.94, 0.02, 0.25, 100.0),
                (2023, 10, 29, 3, 30, 15, 7.96, 0.01, 0.13, 100.0),
                (2023, 10, 29, 3, 45, 15, 7.92, 0.0, None, None),
                (2023, 10, 29, 4, 00, 15, 10.58, 0.01, 0.09, 100.0),
                (2023, 10, 29, 4, 15, 15, 12.59, 0.01, 0.08, 100.0),
                (2023, 10, 29, 4, 30, 15, 16.66, 0.01, 0.06, 100.0),
                (2023, 10, 29, 4, 45, 15, 13.86, 0.02, 0.14, 100.0),
                (2023, 10, 29, 5, 00, 15, 11.76, 0.03, 0.26, 100.0),
                (2023, 10, 29, 5, 15, 15, 8.77, 0.01, 0.11, 100.0),
                (2023, 10, 29, 5, 30, 15, 8.46, 0.01, 0.12, 100.0),
                (2023, 10, 29, 5, 45, 15, 8.83, 0.01, 0.11, 100.0),
                (2023, 10, 29, 6, 00, 15, 10.45, 0.0, None, None),
                (2023, 10, 29, 6, 15, 15, 9.48, 0.01, 0.11, 100.0),
                (2023, 10, 29, 6, 30, 15, 14.48, 0.03, 0.21, 100.0),
                (2023, 10, 29, 6, 45, 15, 24.07, 0.01, 0.04, 100.0),
                (2023, 10, 29, 7, 00, 15, 24.43, 0.01, 0.04, 100.0),
                (2023, 10, 29, 7, 15, 15, 27.35, 0.0, None, None),
                (2023, 10, 29, 7, 30, 15, 34.28, 0.02, 0.06, 100.0),
                (2023, 10, 29, 7, 45, 15, 25.76, 0.02, 0.08, 100.0),
                (2023, 10, 29, 8, 00, 15, 10.98, 0.03, 0.27, 100.0),
                (2023, 10, 29, 8, 15, 15, 10.36, 0.12, 1.16, 100.0),
                (2023, 10, 29, 8, 30, 15, 11.66, 0.38, 3.26, 100.0),
                (2023, 10, 29, 8, 45, 15, 12.5, 0.65, 5.2, 100.0),
                (2023, 10, 29, 9, 00, 15, 13.11, 0.87, 6.64, 100.0),
                (2023, 10, 29, 9, 15, 15, 15.82, 2.0, 12.64, 100.0),
                (2023, 10, 29, 9, 30, 15, 21.0, 2.46, 11.71, 100.0),
                (2023, 10, 29, 9, 45, 15, 20.44, 3.47, 16.98, 100.0),
                (2023, 10, 29, 10, 00, 15, 17.96, 2.97, 16.54, 100.0),
                (2023, 10, 29, 10, 15, 15, 16.92, 3.62, 21.39, 100.0),
                (2023, 10, 29, 10, 30, 15, 15.93, 2.69, 16.89, 100.0),
                (2023, 10, 29, 10, 45, 15, 18.1, 4.14, 22.87, 100.0),
                (2023, 10, 29, 11, 00, 15, 14.98, 2.49, 16.62, 100.0),
                (2023, 10, 29, 11, 15, 15, 19.27, 2.84, 14.74, 100.0),
                (2023, 10, 29, 11, 30, 15, 16.9, 3.38, 20.0, 100.0),
                (2023, 10, 29, 11, 45, 15, 14.65, 5.96, 40.68, 100.0),
                (2023, 10, 29, 12, 00, 15, 15.24, 8.7, 57.09, 100.0),
                (2023, 10, 29, 12, 15, 15, 18.58, 4.97, 26.75, 100.0),
                (2023, 10, 29, 12, 30, 15, 29.69, 7.45, 25.09, 100.0),
                (2023, 10, 29, 12, 45, 15, 29.49, 8.27, 28.04, 100.0),
                (2023, 10, 29, 13, 00, 15, 33.58, 11.06, 32.94, 100.0),
                (2023, 10, 29, 13, 15, 15, 28.82, 5.16, 17.9, 100.0),
                (2023, 10, 29, 13, 30, 15, 31.64, 5.91, 18.68, 100.0),
                (2023, 10, 29, 13, 45, 15, 16.93, 7.11, 42.0, 100.0),
                (2023, 10, 29, 14, 00, 15, 12.35, 5.21, 42.19, 100.0),
                (2023, 10, 29, 14, 15, 15, 13.86, 4.81, 34.7, 100.0),
                (2023, 10, 29, 14, 30, 15, 19.89, 4.39, 22.07, 100.0),
                (2023, 10, 29, 14, 45, 15, 25.31, 3.99, 15.76, 100.0),
                (2023, 10, 29, 15, 00, 15, 17.03, 4.83, 28.36, 100.0),
                (2023, 10, 29, 15, 15, 15, 16.03, 3.87, 24.14, 100.0),
                (2023, 10, 29, 15, 30, 15, 14.94, 3.49, 23.36, 100.0),
                (2023, 10, 29, 15, 45, 15, 14.65, 3.04, 20.75, 100.0),
                (2023, 10, 29, 16, 00, 15, 15.24, 2.07, 13.58, 100.0),
                (2023, 10, 29, 16, 15, 15, 19.24, 0.96, 4.99, 100.0),
                (2023, 10, 29, 16, 30, 15, 21.0, 0.52, 2.48, 100.0),
                (2023, 10, 29, 16, 45, 15, 17.69, 0.06, 0.34, 100.0),
                (2023, 10, 29, 17, 00, 15, 20.74, 0.02, 0.1, 100.0),
                (2023, 10, 29, 17, 15, 15, 16.7, 0.02, 0.12, 100.0),
                (2023, 10, 29, 17, 30, 15, 15.58, 0.02, 0.13, 100.0),
                (2023, 10, 29, 17, 45, 15, 16.1, 0.0, None, None),
                (2023, 10, 29, 18, 00, 15, 18.76, 0.02, 0.11, 100.0),
                (2023, 10, 29, 18, 15, 15, 30.85, 0.01, 0.03, 100.0),
                (2023, 10, 29, 18, 30, 15, 29.42, 0.01, 0.03, 100.0),
                (2023, 10, 29, 18, 45, 15, 32.11, 0.01, 0.03, 100.0),
                (2023, 10, 29, 19, 00, 15, 30.36, 0.0, None, None),
                (2023, 10, 29, 19, 15, 15, 31.18, 0.02, 0.06, 100.0),
                (2023, 10, 29, 19, 30, 15, 18.8, 0.01, 0.05, 100.0),
                (2023, 10, 29, 19, 45, 15, 13.79, 0.01, 0.07, 100.0),
                (2023, 10, 29, 20, 00, 15, 13.1, 0.01, 0.08, 100.0),
                (2023, 10, 29, 20, 15, 15, 13.86, 0.0, None, None),
                (2023, 10, 29, 20, 30, 15, 13.03, 0.02, 0.15, 100.0),
                (2023, 10, 29, 20, 45, 15, 13.98, 0.02, 0.14, 100.0),
                (2023, 10, 29, 21, 00, 15, 17.0, 0.02, 0.12, 100.0),
                (2023, 10, 29, 21, 15, 15, 11.62, 0.01, 0.09, 100.0),
                (2023, 10, 29, 21, 30, 15, 12.88, 0.01, 0.08, 100.0),
                (2023, 10, 29, 21, 45, 15, 14.85, 0.01, 0.07, 100.0),
                (2023, 10, 29, 22, 00, 15, 12.94, 0.01, 0.08, 100.0),
                (2023, 10, 29, 22, 15, 15, 13.84, 0.01, 0.07, 100.0),
                (2023, 10, 29, 22, 30, 15, 14.71, 0.02, 0.14, 100.0),
                (2023, 10, 29, 22, 45, 15, 19.0, 0.0, None, None),
                (2023, 10, 29, 23, 00, 15, 15.34, 0.02, 0.13, 100.0),
                (2023, 10, 29, 23, 15, 15, 13.01, 0.01, 0.08, 100.0),
                (2023, 10, 29, 23, 30, 15, 12.64, 0.01, 0.08, 100.0),
                (2023, 10, 29, 23, 45, 15, 12.64, 0.01, 0.08, 100.0),
            ),
            id="summer time to winter time",
        ),
        pytest.param(
            dt.date(2024, 3, 31),
            _make_summaries(
                (2024, 3, 31, 0, 00, 15, 11.91, 0.01, 0.08, 100.0),
                (2024, 3, 31, 0, 15, 15, 17.37, 0.01, 0.06, 100.0),
                (2024, 3, 31, 0, 30, 15, 25.4, 0.02, 0.08, 100.0),
                (2024, 3, 31, 0, 45, 15, 26.04, 0.01, 0.04, 100.0),
                (2024, 3, 31, 1, 00, 15, 24.42, 0.0, None, None),
                (2024, 3, 31, 1, 15, 15, 29.16, 0.01, 0.03, 100.0),
                (2024, 3, 31, 1, 30, 15, 26.11, 0.01, 0.04, 100.0),
                (2024, 3, 31, 1, 45, 15, 24.41, 0.02, 0.08, 100.0),
                (2024, 3, 31, 3, 00, 15, 9.0, 0.02, 0.22, 100.0),
                (2024, 3, 31, 3, 15, 15, 9.55, 0.0, None, None),
                (2024, 3, 31, 3, 30, 15, 9.71, 0.01, 0.1, 100.0),
                (2024, 3, 31, 3, 45, 15, 12.2, 0.01, 0.08, 100.0),
                (2024, 3, 31, 4, 00, 15, 10.95, 0.03, 0.27, 100.0),
                (2024, 3, 31, 4, 15, 15, 10.48, 0.0, None, None),
                (2024, 3, 31, 4, 30, 15, 9.66, 0.01, 0.1, 100.0),
                (2024, 3, 31, 4, 45, 15, 9.63, 0.02, 0.21, 100.0),
                (2024, 3, 31, 5, 00, 15, 9.79, 0.02, 0.2, 100.0),
                (2024, 3, 31, 5, 15, 15, 12.59, 0.0, None, None),
                (2024, 3, 31, 5, 30, 15, 12.56, 0.01, 0.08, 100.0),
                (2024, 3, 31, 5, 45, 15, 11.57, 0.01, 0.09, 100.0),
                (2024, 3, 31, 6, 00, 15, 13.93, 0.01, 0.07, 100.0),
                (2024, 3, 31, 6, 15, 15, 12.66, 0.01, 0.08, 100.0),
                (2024, 3, 31, 6, 30, 15, 11.28, 0.02, 0.18, 100.0),
                (2024, 3, 31, 6, 45, 15, 11.81, 0.02, 0.17, 100.0),
                (2024, 3, 31, 7, 00, 15, 11.55, 0.02, 0.17, 100.0),
                (2024, 3, 31, 7, 15, 15, 10.9, 0.05, 0.46, 100.0),
                (2024, 3, 31, 7, 30, 15, 14.35, 0.62, 4.32, 100.0),
                (2024, 3, 31, 7, 45, 15, 14.01, 0.9, 6.42, 100.0),
                (2024, 3, 31, 8, 00, 15, 21.42, 1.25, 5.84, 100.0),
                (2024, 3, 31, 8, 15, 15, 30.26, 2.5, 8.26, 100.0),
                (2024, 3, 31, 8, 30, 15, 25.72, 3.96, 15.4, 100.0),
                (2024, 3, 31, 8, 45, 15, 25.3, 4.78, 18.89, 100.0),
                (2024, 3, 31, 9, 00, 15, 26.27, 6.38, 24.29, 100.0),
                (2024, 3, 31, 9, 15, 15, 28.02, 5.66, 20.2, 100.0),
                (2024, 3, 31, 9, 30, 15, 28.05, 7.47, 26.63, 100.0),
                (2024, 3, 31, 9, 45, 15, 14.6, 8.88, 60.82, 100.0),
                (2024, 3, 31, 10, 00, 15, 21.54, 7.67, 35.61, 100.0),
                (2024, 3, 31, 10, 15, 15, 19.6, 13.75, 70.1, 99.93),
                (2024, 3, 31, 10, 30, 15, 16.15, 14.68, 90.65, 99.73),
                (2024, 3, 31, 10, 45, 15, 12.41, 11.42, 91.78, 99.74),
                (2024, 3, 31, 11, 00, 15, 17.55, 12.51, 71.23, 99.92),
                (2024, 3, 31, 11, 15, 15, 14.54, 12.98, 89.06, 99.77),
                (2024, 3, 31, 11, 30, 15, 19.74, 20.17, 99.44, 97.32),
                (2024, 3, 31, 11, 45, 15, 13.06, 13.04, 99.31, 99.46),
                (2024, 3, 31, 12, 00, 15, 18.38, 18.44, 99.95, 99.62),
                (2024, 3, 31, 12, 15, 15, 22.38, 22.42, 99.78, 99.6),
                (2024, 3, 31, 12, 30, 15, 23.86, 23.87, 99.79, 99.75),
                (2024, 3, 31, 12, 45, 15, 16.64, 16.64, 99.52, 99.52),
                (2024, 3, 31, 13, 00, 15, 14.1, 14.09, 99.43, 99.5),
                (2024, 3, 31, 13, 15, 15, 16.66, 16.92, 99.52, 97.99),
                (2024, 3, 31, 13, 30, 15, 21.81, 21.8, 98.76, 98.81),
                (2024, 3, 31, 13, 45, 15, 17.32, 17.36, 99.36, 99.14),
                (2024, 3, 31, 14, 00, 15, 16.04, 16.12, 99.94, 99.44),
                (2024, 3, 31, 14, 15, 15, 18.68, 10.55, 56.42, 99.91),
                (2024, 3, 31, 14, 30, 15, 32.0, 26.16, 81.69, 99.92),
                (2024, 3, 31, 14, 45, 15, 28.67, 24.15, 84.09, 99.83),
                (2024, 3, 31, 15, 00, 15, 11.36, 11.38, 99.74, 99.56),
                (2024, 3, 31, 15, 15, 15, 17.07, 10.59, 62.04, 100.0),
                (2024, 3, 31, 15, 30, 15, 11.57, 7.05, 60.93, 100.0),
                (2024, 3, 31, 15, 45, 15, 13.78, 7.22, 52.39, 100.0),
                (2024, 3, 31, 16, 00, 15, 15.57, 10.03, 64.42, 100.0),
                (2024, 3, 31, 16, 15, 15, 12.67, 11.38, 89.82, 100.0),
                (2024, 3, 31, 16, 30, 15, 12.25, 6.65, 54.29, 100.0),
                (2024, 3, 31, 16, 45, 15, 14.19, 7.97, 56.17, 100.0),
                (2024, 3, 31, 17, 00, 15, 15.74, 10.66, 67.66, 99.91),
                (2024, 3, 31, 17, 15, 15, 15.97, 6.96, 43.58, 100.0),
                (2024, 3, 31, 17, 30, 15, 15.96, 10.9, 68.3, 100.0),
                (2024, 3, 31, 17, 45, 15, 16.66, 5.57, 33.43, 100.0),
                (2024, 3, 31, 18, 00, 15, 13.64, 5.72, 41.94, 100.0),
                (2024, 3, 31, 18, 15, 15, 14.05, 4.86, 34.59, 100.0),
                (2024, 3, 31, 18, 30, 15, 14.23, 5.24, 36.82, 100.0),
                (2024, 3, 31, 18, 45, 15, 13.33, 4.85, 36.38, 100.0),
                (2024, 3, 31, 19, 00, 15, 15.0, 2.89, 19.27, 100.0),
                (2024, 3, 31, 19, 15, 15, 16.33, 1.53, 9.37, 100.0),
                (2024, 3, 31, 19, 30, 15, 16.77, 0.81, 4.83, 100.0),
                (2024, 3, 31, 19, 45, 15, 15.73, 0.71, 4.51, 100.0),
                (2024, 3, 31, 20, 00, 15, 19.36, 0.09, 0.46, 100.0),
                (2024, 3, 31, 20, 15, 15, 28.4, 0.0, None, None),
                (2024, 3, 31, 20, 30, 15, 28.92, 0.01, 0.03, 100.0),
                (2024, 3, 31, 20, 45, 15, 28.74, 0.01, 0.03, 100.0),
                (2024, 3, 31, 21, 00, 15, 28.77, 0.01, 0.03, 100.0),
                (2024, 3, 31, 21, 15, 15, 31.38, 0.01, 0.03, 100.0),
                (2024, 3, 31, 21, 30, 15, 31.74, 0.01, 0.03, 100.0),
                (2024, 3, 31, 21, 45, 15, 29.06, 0.01, 0.03, 100.0),
                (2024, 3, 31, 22, 00, 15, 14.49, 0.01, 0.07, 100.0),
                (2024, 3, 31, 22, 15, 15, 13.9, 0.02, 0.14, 100.0),
                (2024, 3, 31, 22, 30, 15, 16.91, 0.01, 0.06, 100.0),
                (2024, 3, 31, 22, 45, 15, 16.38, 0.02, 0.12, 100.0),
                (2024, 3, 31, 23, 00, 15, 17.38, 0.01, 0.06, 100.0),
                (2024, 3, 31, 23, 15, 15, 14.64, 0.01, 0.07, 100.0),
                (2024, 3, 31, 23, 30, 15, 16.43, 0.01, 0.06, 100.0),
                (2024, 3, 31, 23, 45, 15, 12.63, 0.0, None, None),
            ),
            id="winter time to summer time",
        ),
    ],
)
async def test_daily(
    *, date: dt.date, expected: list[PhotovoltaicSummary], mock_auth: Auth
) -> None:
    """Check that enocoo.get_individual_consumption returns daily data in expected format."""
    enocoo = Enocoo(mock_auth, TIMEZONE)

    actual = await enocoo.get_quarter_photovoltaic_data(during=date, interval="day")
    assert actual == expected


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

    with pytest.warns(UserWarning, match="off by one"):
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
