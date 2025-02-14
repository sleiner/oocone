"""Tests for the oocone.Enocoo.get_area_ids() method."""

import pytest

from oocone import Auth, Enocoo
from tests import TIMEZONE
from tests.conftest import MOCK_API_DATASET_NAMES, MockApiParams


@pytest.mark.asyncio
@pytest.mark.parametrize("dataset", MOCK_API_DATASET_NAMES)
async def test_happy_path(dataset: str, mock_auth: Auth, mock_api_params: MockApiParams) -> None:
    """Check that enocoo.get_area_ids returns the area ID as indicated in ownConsumption.php."""
    mock_api_params.dataset_name = dataset
    enocoo = Enocoo(mock_auth, TIMEZONE)

    ids = await enocoo.get_area_ids()
    assert ids == ["123"]
