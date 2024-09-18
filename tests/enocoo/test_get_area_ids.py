"""Tests for the oocone.Enocoo.get_area_ids() method."""

import pytest

from oocone import Auth, Enocoo
from tests import TIMEZONE


@pytest.mark.asyncio
async def test_happy_path(mock_auth: Auth) -> None:
    """Check that enocoo.get_area_ids returns the area ID as indicated in ownConsumption.php."""
    enocoo = Enocoo(mock_auth, TIMEZONE)
    ids = await enocoo.get_area_ids()
    assert ids == ["123"]
