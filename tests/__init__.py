"""Tests suite for `oocone`."""

from pathlib import Path
from zoneinfo import ZoneInfo

TESTS_DIR = Path(__file__).parent
RESPONSES_DIR = TESTS_DIR / "data" / "responses"
TIMEZONE = ZoneInfo("Europe/Berlin")
