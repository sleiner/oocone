"""
Updates the API response snapshots under tests/data/responses/.

Before executing it, be sure to set these env variables:
    - ENOCOO_BASE_URL
    - ENOCOO_USERNAME
    - ENOCOO_PASSWORD
    - ENOCOO_AREA_ID
"""

import asyncio
import os
import re
from collections import OrderedDict
from collections.abc import Callable, Mapping
from itertools import count
from pathlib import Path
from typing import Any, TypeVar

import aiohttp

PROJECT_DIR = Path(__file__).parent.parent
RESPONSES_DIR = PROJECT_DIR / "tests" / "data" / "responses"
BASE_URL = os.environ["ENOCOO_BASE_URL"].rstrip("/")

limit_concurrent_requests = asyncio.Semaphore(3)
T = TypeVar("T")


async def get(
    path: str,
    *,
    params: Mapping[str, str] | None = None,
    session: aiohttp.ClientSession | None = None,
) -> str:
    return await request(lambda s: s.get(f"{BASE_URL}/{path}", params=params), session)


async def post(path: str, data: Any = None, *, session: aiohttp.ClientSession | None = None) -> str:
    return await request(
        lambda s: s.post(f"{BASE_URL}/{path}", data=data),
        session,
    )


async def post_login(
    username: str, password: str, *, session: aiohttp.ClientSession | None = None
) -> str:
    return await post(
        path="signinForm.php?mode=ok",
        data={"user": username, "passwort": password},
        session=session,
    )


async def request(make_request: Callable, session: aiohttp.ClientSession | None = None) -> str:
    if not session:
        async with aiohttp.ClientSession() as temp_session:
            return await request(make_request, session=temp_session)

    async with limit_concurrent_requests, make_request(session) as response:
        return await response.text()


async def async_id(x: T) -> T:
    return x


def anonymize(original_html: str) -> str:
    html = original_html

    # dwelling unit number
    html = re.sub(r"H\d{2}W\d{2}", "H12W34", html)

    # account ID
    html = re.sub(r"H\d{2}W\d{2}_\d{2}", "H12W34_01", html)

    # area ID
    html = re.sub(
        r'var chosenResidenceId = "(\d+)";',
        r'var chosenResidenceId = "123";',
        html,
    )

    # meter numbers
    meter_numbers = count(start=1)
    html = re.sub(
        r"(?!<td>)\d{8}(?=</td>)",
        lambda _: f"{next(meter_numbers):08}",
        html,
    )

    # date and time
    html = re.sub(r"\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2}", "01.01.2021 12:34:56", html)
    html = re.sub(r"\d{2}\.\d{2}\.\d{4} - \d{2}\.\d{2}\.\d{4}", "01.01.2021 - 02.02.2022", html)

    # meter values
    html = re.sub(
        r"(?!<td>)[\d\.]+,\d{2}(?=<\/td>)",
        "1.234,56",
        html,
    )

    return html  # noqa: RET504


async def main() -> None:
    username = os.environ["ENOCOO_USERNAME"]
    password = os.environ["ENOCOO_PASSWORD"]
    area_id = os.environ["ENOCOO_AREA_ID"]

    requests = OrderedDict()

    async with aiohttp.ClientSession() as logged_in_session:
        requests["signinForm.failure.php"] = post_login("incorrect", "incorrect")
        requests["signinForm.success.php"] = async_id(
            await post_login(username, password, session=logged_in_session)
        )

        for meter_class in ("Stromverbrauch", "Warmwasser", "Kaltwasser", "Waerme"):
            for interval in ("Tag", "Woche", "Monat", "Jahr"):
                for date in ("2023-10-29", "2024-01-01", "2024-03-31"):
                    requests[f"getMeterDataWithParam.{meter_class}.{date}.{interval}.php"] = get(
                        "php/getMeterDataWithParam.php",
                        params={
                            "AreaId": area_id,
                            "from": date,
                            "intVal": interval,
                            "mClass": meter_class,
                        },
                        session=logged_in_session,
                    )

        requests["getTrafficLightStatus.php"] = get("php/getTrafficLightStatus.php")

        requests["newMeterTable.php"] = get("php/newMeterTable.php", session=logged_in_session)
        requests["newMeterTable.notLoggedIn.php"] = get("php/newMeterTable.php")

        requests["ownConsumption.php"] = get("php/ownConsumption.php", session=logged_in_session)

        responses = zip(
            requests.keys(),
            await asyncio.gather(*[asyncio.create_task(t) for t in requests.values()]),
            strict=True,
        )

    responses = dict(responses)

    for doc in ("newMeterTable.php", "ownConsumption.php"):
        responses[doc] = anonymize(responses[doc])

    RESPONSES_DIR.mkdir(parents=True, exist_ok=True)
    for name, response in responses.items():
        with Path.open(RESPONSES_DIR / name, "w", encoding="utf-8") as f:
            f.write(response)


if __name__ == "__main__":
    asyncio.run(main())
