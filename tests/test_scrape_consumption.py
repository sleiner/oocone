"""Tests for oocone._internal.scrape_consumption."""

import pytest

from oocone import Auth
from oocone._internal.scrape_consumption import _get_area_ids


@pytest.mark.asyncio()
async def test_get_area_ids(mock_auth: Auth) -> None:
    """Check that _get_area_ids returns the area ID as indicated in ownConsumption.php."""
    ids = await _get_area_ids(mock_auth)
    assert ids == ["123"]
