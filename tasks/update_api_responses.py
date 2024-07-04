"""
Updates the API response snapshots under tests/data/responses/.

Before executing it, be sure to set these env variables:
    - ENOCOO_BASE_URL
    - ENOCOO_USERNAME
    - ENOCOO_PASSWORD
"""

import asyncio
import os
import re
from collections import OrderedDict
from itertools import count
from pathlib import Path
from typing import TypeVar

import aiohttp

PROJECT_DIR = Path(__file__).parent.parent
RESPONSES_DIR = PROJECT_DIR / "tests" / "data" / "responses"
BASE_URL = os.environ["ENOCOO_BASE_URL"].rstrip("/")

limit_concurrent_requests = asyncio.Semaphore(3)
T = TypeVar("T")


async def post_login(
    username: str, password: str, *, session: aiohttp.ClientSession | None = None
) -> str:
    if not session:
        async with aiohttp.ClientSession() as temp_session:
            return await post_login(username, password, session=temp_session)

    async with (
        limit_concurrent_requests,
        session.post(
            f"{BASE_URL}/signinForm.php?mode=ok",
            data={"user": username, "passwort": password},
        ) as response,
    ):
        return await response.text()


async def get(path: str, *, session: aiohttp.ClientSession | None = None) -> str:
    if not session:
        async with aiohttp.ClientSession() as temp_session:
            return await get(path, session=temp_session)

    async with limit_concurrent_requests, session.get(f"{BASE_URL}/{path}") as response:
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

    requests = OrderedDict()

    async with aiohttp.ClientSession() as logged_in_session:
        requests["signinForm.success.php"] = async_id(
            await post_login(username, password, session=logged_in_session)
        )
        requests["newMeterTable.php"] = get("php/newMeterTable.php", session=logged_in_session)
        requests["newMeterTable.notLoggedIn.php"] = get("php/newMeterTable.php")

        requests["ownConsumption.php"] = get("php/ownConsumption.php", session=logged_in_session)

        requests["getTrafficLightStatus.php"] = get("php/getTrafficLightStatus.php")

        requests["signinForm.failure.php"] = post_login("incorrect", "incorrect")

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
