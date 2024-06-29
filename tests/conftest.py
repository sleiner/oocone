"""Common fixtures and settings for all tests."""

from asyncio import AbstractEventLoop
from pathlib import Path

import pytest
from aiohttp import web
from aiohttp.test_utils import TestClient
from aiohttp.typedefs import Handler
from pytest_aiohttp.plugin import AiohttpClient

from . import RESPONSES_DIR

pytest_plugins = ("pytest_asyncio",)

signed_in = web.AppKey("signed_in", bool)


async def _signin_form(request: web.Request) -> web.Response:
    response_path = RESPONSES_DIR / "signinForm.failure.php"
    response = web.Response()

    if request.method == "POST":
        data = await request.post()
        username = data.get("user")
        password = data.get("passwort")
        credentials_correct = username == "correct" and password == "correct"  # noqa: S105

        if credentials_correct and request.query.get("mode") == "ok":
            response_path = RESPONSES_DIR / "signinForm.success.php"
            response.set_cookie("logged_in", "true")

    with Path.open(response_path, "rb") as f:
        response.body = f.read()

    return response


def _response_from_file(response_path: Path, *, needs_login: bool = True) -> Handler:
    original_response_path = response_path

    async def handler(request: web.Request) -> web.Response:
        response = web.Response()

        if needs_login and request.cookies.get("logged_in") != "true":
            response_path = RESPONSES_DIR / "newMeterTable.notLoggedIn.php"
        else:
            response_path = RESPONSES_DIR / original_response_path

        with Path.open(response_path, "rb") as f:
            response.body = f.read()

        return response

    return handler


@pytest.fixture()
def mock_api(event_loop: AbstractEventLoop, aiohttp_client: AiohttpClient) -> TestClient:
    """Return a mock API instance."""
    app = web.Application()
    app[signed_in] = False

    app.router.add_post("/signinForm.php", _signin_form)
    app.router.add_get(
        "/php/getTrafficLightStatus.php",
        _response_from_file("getTrafficLightStatus.php", needs_login=False),
    )
    app.router.add_get(
        "/php/newMeterTable.php",
        _response_from_file("newMeterTable.php", needs_login=True),
    )
    return event_loop.run_until_complete(aiohttp_client(app))


@pytest.fixture()
def mock_auth(mock_api: TestClient):  # noqa: ANN201
    """Return an Auth instance accessing a mock API."""
    # Importing oocone directly inside conftest.py breaks the typeguard plugin for pytest,
    # so we import it lazily. Because of this, we cannot give a return type hint :(
    from oocone import Auth

    return Auth(
        websession=mock_api.session,
        base_url=str(mock_api.server.make_url("/")),
        username="correct",
        password="correct",  # noqa: S106
    )
