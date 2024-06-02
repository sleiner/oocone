import asyncio
import os
import re
from collections import OrderedDict
from itertools import count
from pathlib import Path

import aiohttp

PROJECT_DIR = Path(__file__).parent.parent
RESPONSES_DIR = PROJECT_DIR / "tests" / "data" / "responses"
BASE_URL = "https://example.com"

limit_concurrent_requests = asyncio.Semaphore(3)


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
        text = await response.text()
    return text


async def get(path: str, *, session: aiohttp.ClientSession | None = None) -> str:
    if not session:
        async with aiohttp.ClientSession() as temp_session:
            return await get(path, session=temp_session)

    async with limit_concurrent_requests, session.get(f"{BASE_URL}/{path}") as response:
        text = await response.text()
    return text


async def async_id(x):
    return x


def anonymize_new_meter_table(original_html: str) -> str:
    html = original_html

    # dwelling unit number
    html = re.sub(r"H\d{2}W\d{2}", "H12W34", html)

    # meter numbers
    meter_numbers = count(start=1)
    html = re.sub(r"\d{8}", lambda _: f"{next(meter_numbers):08}", html)

    # date and time
    html = re.sub(r"\d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2}", "01.01.2021 12:34:56", html)

    # meter values
    html = re.sub(r"[\d\.]+,\d{2}", "1.234,56", html)

    return html


async def main() -> None:
    global BASE_URL
    BASE_URL = os.environ["ENOCOO_BASE_URL"].rstrip("/")

    username = os.environ["ENOCOO_USERNAME"]
    password = os.environ["ENOCOO_PASSWORD"]

    requests = OrderedDict()

    async with aiohttp.ClientSession() as logged_in_session:
        requests["signinForm.success.php"] = async_id(
            await post_login(username, password, session=logged_in_session)
        )
        requests["newMeterTable.php"] = get("php/newMeterTable.php", session=logged_in_session)
        requests["newMeterTable.notLoggedIn.php"] = get("php/newMeterTable.php")

        requests["getTrafficLightStatus.php"] = get("php/getTrafficLightStatus.php")

        requests["signinForm.failure.php"] = post_login("incorrect", "incorrect")

        responses = zip(
            requests.keys(),
            await asyncio.gather(*[asyncio.create_task(t) for t in requests.values()]),
            strict=True,
        )

    responses = dict(responses)

    for doc in ("newMeterTable.php",):
        responses[doc] = anonymize_new_meter_table(responses[doc])

    RESPONSES_DIR.mkdir(parents=True, exist_ok=True)
    for name, response in responses.items():
        with open(RESPONSES_DIR / name, "w", encoding="utf-8") as f:
            f.write(response)


if __name__ == "__main__":
    asyncio.run(main())
