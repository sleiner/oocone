"""Module containing the main API entry points for this module."""

from __future__ import annotations

import datetime as dt
import logging
from typing import TYPE_CHECKING, Any, Literal

from oocone import errors
from oocone._internal import scrape_consumption, scrape_meter_table
from oocone.types import (
    UNKNOWN,
    Consumption,
    ConsumptionType,
    MeterStatus,
    TrafficLightColor,
    TrafficLightStatus,
)

if TYPE_CHECKING:
    from oocone.auth import Auth

ROUTE_LOGIN = "/signinForm.php?mode=ok"
BEAUTIFULSOUP_PARSER = "html.parser"

logger = logging.getLogger(__name__)


class Enocoo:
    """Provides access to the data accessible via the enocoo Web interface."""

    def __init__(self, auth: Auth, timezone: dt.tzinfo) -> None:
        """
        Initialize the API and store the auth so we can make requests.

        Parameters
        ----------
        auth
            Indicates how to contact the enocoo dashboard, including URL and credentials.
        timezone
            The timezone in which the building of the energy management system is located.

        """
        self.auth = auth
        self.timezone = timezone

    @staticmethod
    def __extract_key_from_response(response_data: dict[str, Any], key: str) -> Any:
        try:
            result = response_data[key]
        except KeyError:
            msg = (
                f'API response does not contain key "{key}".\n'
                f"Response data:\n"
                f"{response_data}"
            )
            raise KeyError(msg) from None

        return result

    async def get_traffic_light_status(self) -> TrafficLightStatus:
        """Return the status of the energy traffic light."""
        response, _ = await self.auth.request("GET", "php/getTrafficLightStatus.php")

        try:
            # We parse the response as JSON, even though the Content-Type header might indicate
            # otherwise.
            response_data = await response.json(content_type=None)
        except Exception as e:
            raise errors.UnexpectedResponse from e

        def parse_color(response_data: dict) -> TrafficLightColor | Literal[UNKNOWN]:
            try:
                raw = self.__extract_key_from_response(response_data, "color")
            except KeyError as e:
                logger.warning(e)
                return UNKNOWN

            if raw == "rot":
                return TrafficLightColor.RED
            if raw == "gelb":
                return TrafficLightColor.YELLOW
            if raw == r"grün":
                return TrafficLightColor.GREEN

            logger.warning('Got unexpected color: "%s", raw')
            return UNKNOWN

        def parse_current_energy_price(response_data: dict) -> float | Literal[UNKNOWN]:
            try:
                raw = self.__extract_key_from_response(response_data, "currentEnergyprice")
            except KeyError as e:
                logger.warning(e)
                return UNKNOWN

            try:
                result = float(raw)
            except ValueError:
                logger.warning("Could not parse energy price %s as a number", raw)
                return UNKNOWN

            return result

        return TrafficLightStatus(
            color=parse_color(response_data),
            current_energy_price=parse_current_energy_price(response_data),
        )

    async def get_meter_table(self) -> list[MeterStatus]:
        """Return the status of all individual consumption meters available in the dashboard."""
        return await scrape_meter_table.get_meter_table(
            date=dt.datetime.now(tz=self.timezone).date(),
            timezone=self.timezone,
            auth=self.auth,
        )

    async def get_area_ids(self) -> list[str]:
        """Get all area IDs available via the dashboard."""
        return await scrape_consumption.get_area_ids(auth=self.auth)

    async def get_individual_consumption(
        self,
        consumption_type: ConsumptionType,
        during: dt.date,
        interval: Literal["day", "year"],
        area_id: str,
    ) -> list[Consumption]:
        """Return individual consumption statistics for a given meter type."""
        if interval == "day":
            return await scrape_consumption.get_daily_consumption(
                consumption_type=consumption_type,
                area_id=area_id,
                date=during,
                timezone=self.timezone,
                auth=self.auth,
            )
        if interval == "year":
            return await scrape_consumption.get_yearly_consumption(
                consumption_type=consumption_type,
                area_id=area_id,
                year_number=during.year,
                auth=self.auth,
            )

        msg = f'Illegal interval "{interval}"'
        raise errors.OoconeMisuse(msg)
