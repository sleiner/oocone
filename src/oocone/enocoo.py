"""Module containing the main API entry points for this module."""

from __future__ import annotations

import logging
from datetime import datetime, tzinfo
from typing import Any, Literal

import aiohttp
from bs4 import BeautifulSoup

from oocone import errors
from oocone._internal.html_table import parse_table
from oocone.types import UNKNOWN, MeterStatus, TrafficLightColor, TrafficLightStatus

ROUTE_LOGIN = "/signinForm.php?mode=ok"
BEAUTIFULSOUP_PARSER = "html.parser"

logger = logging.getLogger(__name__)


class Auth:
    """Acquires authentication for the dashboard and makes authenticated requests."""

    def __init__(
        self,
        *,
        websession: aiohttp.ClientSession | None = None,
        base_url: str,
        username: str,
        password: str,
    ) -> None:
        """Initialize."""
        self._base_url = base_url.rstrip("/")
        self.__username = username
        self.__password = password
        self._session = websession or aiohttp.ClientSession()
        self._logged_in = False

    @staticmethod
    def _response_indicates_not_logged_in(response: BeautifulSoup) -> bool:
        if response.title is not None and "abgemeldet" in response.title.text.lower():
            return True
        if response.find("input", {"type": "password"}) is not None:  # noqa: SIM103
            return True

        return False

    async def _login(self) -> None:
        async with self._session.post(
            self._base_url + ROUTE_LOGIN,
            data={"user": self.__username, "passwort": self.__password},
        ) as response:
            response_text = await response.text()

            soup = BeautifulSoup(response_text, features=BEAUTIFULSOUP_PARSER)
            if self._response_indicates_not_logged_in(soup):
                raise errors.AuthenticationFailed

    async def request(
        self, method: str, path: str, *, retry_with_login: bool = True, **kwargs: dict
    ) -> (aiohttp.ClientResponse, BeautifulSoup):
        """Make a request."""
        try:
            response = await self._session.request(
                method,
                f"{self._base_url}/{path}",
                **kwargs,
            )
        except aiohttp.client_exceptions.ClientError as e:
            raise errors.ConnectionIssue from e

        soup = BeautifulSoup(await response.text(), BEAUTIFULSOUP_PARSER)

        if self._response_indicates_not_logged_in(soup):
            if retry_with_login:
                await self._login()
                return await self.request(method, path, retry_with_login=False, **kwargs)

            raise errors.AuthenticationFailed

        return (response, soup)


class Enocoo:
    """Provides access to the data accessible via the enocoo Web interface."""

    def __init__(self, auth: Auth, timezone: tzinfo) -> None:
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
        response, soup = await self.auth.request(
            "POST",
            "php/newMeterTable.php",
            data={"dateParam": datetime.now(tz=self.timezone).date().isoformat()},
        )
        html_table = soup.find("table")
        meter_table = parse_table(html_table)

        def parse_timestamp(timestamp: str) -> datetime:
            dateformat = r"%d.%m.%Y %H:%M:%S"
            return datetime.strptime(timestamp, dateformat).replace(tzinfo=self.timezone)

        def parse_reading(reading: str) -> float:
            # The reading uses german number formatting with a comma as the decimal separator and a
            # dot as the thousands separator. The convention used by float is a dot as the decimal
            # separator and comma as the thousands separator.abs

            reading = reading.replace(".", "")  # we don't need a thousands separator here
            reading = reading.replace(",", ".")

            return float(reading)

        def parse_unit(text: str) -> str:
            if text == "m3":  # noqa: SIM108
                result = "m³"
            else:
                result = text

            return result

        result = []
        for row in meter_table.rows:
            try:
                meter_status = MeterStatus(
                    name=row["Bezeichnung"],
                    area=row["Fläche"],
                    meter_id=row["Zähler-Nr."],
                    timestamp=parse_timestamp(row["Zeitpunkt"]),
                    reading=parse_reading(row["Zählerstand"]),
                    unit=parse_unit(row["Einheit"]),
                )
            except Exception as e:
                raise errors.UnexpectedResponse from e

            result.append(meter_status)

        return result
