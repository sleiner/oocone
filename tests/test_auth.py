import pytest
from aiohttp.test_utils import TestClient

from oocone import Auth, errors


@pytest.mark.asyncio
@pytest.mark.mocked_api
async def test_login_successful(mock_api: TestClient) -> None:
    auth = Auth(
        websession=mock_api.session,
        base_url=str(mock_api.server.make_url("/")),
        username="correct",
        password="correct",
    )
    await auth._login()


@pytest.mark.asyncio
@pytest.mark.mocked_api
async def test_login_raise_on_failure(mock_api: TestClient) -> None:
    auth = Auth(
        websession=mock_api.session,
        base_url=str(mock_api.server.make_url("/")),
        username="correct",
        password="incorrect",
    )
    with pytest.raises(errors.AuthenticationFailed):
        await auth._login()
