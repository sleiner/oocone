from __future__ import annotations

import logging
from typing import Any, Literal

import aiohttp
from bs4 import BeautifulSoup

from oocone import errors
from oocone.types import UNKNOWN, TrafficLightColor, TrafficLightStatus

ROUTE_LOGIN = "/signinForm.php?mode=ok"
BEAUTIFULSOUP_PARSER = "html.parser"

logger = logging.getLogger(__name__)


class Auth:
    def __init__(
        self,
        *,
        websession: aiohttp.ClientSession | None = None,
        base_url: str,
        username: str,
        password: str,
    ):
        self._base_url = base_url.rstrip("/")
        self.__username = username
        self.__password = password
        self._session = websession or aiohttp.ClientSession()
        self._logged_in = False

    @staticmethod
    def response_indicates_not_logged_in(response: BeautifulSoup) -> bool:
        return response.find("input", {"type": "password"}) is not None

    async def _login(self) -> None:
        async with self._session.post(
            self._base_url + ROUTE_LOGIN,
            data={"user": self.__username, "passwort": self.__password},
        ) as response:
            response_text = await response.text()

            soup = BeautifulSoup(response_text, features=BEAUTIFULSOUP_PARSER)
            if self.response_indicates_not_logged_in(soup):
                raise errors.AuthenticationFailed

    async def request(
        self, method: str, path: str, retry_with_login: bool = True, **kwargs
    ) -> (aiohttp.ClientResponse, BeautifulSoup):
        """Make a request."""

        response = await self._session.request(
            method,
            f"{self._base_url}/{path}",
            **kwargs,
        )
        soup = BeautifulSoup(await response.text(), BEAUTIFULSOUP_PARSER)

        if self.response_indicates_not_logged_in(soup):
            if retry_with_login:
                self._login()
                return await self.request(method=method, retry_with_login=False, **kwargs)
            else:
                raise errors.AuthenticationFailed()
        else:
            return (response, soup)


class Enocoo:
    """Provides access to the data accessible via the enocoo Web interface"""

    def __init__(self, auth: Auth):
        """Initialize the API and store the auth so we can make requests."""
        self.auth = auth

    @staticmethod
    def __extract_key_from_response(response_data: dict[str, Any], key: str) -> Any:
        try:
            result = response_data[key]
        except KeyError:
            raise KeyError(
                f'API response does not contain key "{key}".\n'
                f"Response data:\n"
                f"{response_data}"
            ) from None

        return result

    async def get_traffic_light_status(self):
        try:
            response, _ = await self.auth.request("GET", "php/getTrafficLightStatus.php")
        except aiohttp.client_exceptions.ClientError as e:
            raise errors.ConnectionError() from e

        try:
            # We parse the response as JSON, even though the Content-Type header might indicate
            # otherwise.
            response_data = await response.json(content_type=None)
        except Exception as e:
            raise errors.UnexpectedResponse() from e

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

            logger.warning(f'Got unexpected color: "{raw}"')
            return UNKNOWN

        def parse_current_energy_price(response_data: dict) -> float | Literal[UNKNOWN]:
            try:
                raw = self.__extract_key_from_response(response_data, "currentEnergyprice")
            except KeyError as e:
                logger.warning(e)
                return UNKNOWN

            try:
                result = float(raw)
            except Exception:
                logger.warning("Could not parse energy price %s as a number")
                return UNKNOWN

            return result

        result = TrafficLightStatus(
            color=parse_color(response_data),
            current_energy_price=parse_current_energy_price(response_data),
        )
        return result
