"""Tests for oocone._internal.html_table."""

from pathlib import Path

import pytest
from bs4 import BeautifulSoup

from oocone._internal.html_table import Table, parse_table
from oocone.enocoo import BEAUTIFULSOUP_PARSER

from . import RESPONSES_DIR


def __testdata(data_id: str) -> (str, Table):
    if data_id == "synthetic":
        html = """\
            <table class="table table-striped">
                <tr>
                    <th>Header 1</th>
                    <th>Header 2</th>
                    <th>Header 3</th>
                </tr>
                <tr>
                    <td>Row 1, Data Point 1</td>
                    <td>Row 1, Data Point 2</td>
                    <td>Row 1, Data Point 3</td>
                </tr>
                <tr>
                    <td>Row 2, Data Point 1</td>
                    <td>Row 2, Data Point 2</td>
                    <td>Row 2, Data Point 3</td>
                </tr>
            </table>
            """
        expected_table = Table(
            columns=["Header 1", "Header 2", "Header 3"],
            rows=[
                {
                    "Header 1": "Row 1, Data Point 1",
                    "Header 2": "Row 1, Data Point 2",
                    "Header 3": "Row 1, Data Point 3",
                },
                {
                    "Header 1": "Row 2, Data Point 1",
                    "Header 2": "Row 2, Data Point 2",
                    "Header 3": "Row 2, Data Point 3",
                },
            ],
        )
    elif data_id == "newMeterTable.php":
        html = Path.open(RESPONSES_DIR / "newMeterTable.php", encoding="utf-8").read()
        expected_table = Table(
            columns=["Fläche", "Bezeichnung", "Zähler-Nr.", "Zeitpunkt", "Zählerstand", "Einheit"],
            rows=[
                {
                    "Fläche": "H12W34",
                    "Bezeichnung": "Verbrauch Kaltwasser H12W34 Bad",
                    "Zähler-Nr.": "00000001",
                    "Zeitpunkt": "01.01.2021 12:34:56",
                    "Zählerstand": "1.234,56",
                    "Einheit": "m3",
                },
                {
                    "Fläche": "H12W34",
                    "Bezeichnung": "Verbrauch Kaltwasser H12W34 WC",
                    "Zähler-Nr.": "00000002",
                    "Zeitpunkt": "01.01.2021 12:34:56",
                    "Zählerstand": "1.234,56",
                    "Einheit": "m3",
                },
                {
                    "Fläche": "H12W34",
                    "Bezeichnung": "Verbrauch Strom H12W34",
                    "Zähler-Nr.": "00000003",
                    "Zeitpunkt": "01.01.2021 12:34:56",
                    "Zählerstand": "1.234,56",
                    "Einheit": "kWh",
                },
                {
                    "Fläche": "H12W34",
                    "Bezeichnung": "Verbrauch Wärme H12W34",
                    "Zähler-Nr.": "00000004",
                    "Zeitpunkt": "01.01.2021 12:34:56",
                    "Zählerstand": "1.234,56",
                    "Einheit": "kWh",
                },
                {
                    "Fläche": "H12W34",
                    "Bezeichnung": "Verbrauch Warmwasser H12W34 Bad",
                    "Zähler-Nr.": "00000005",
                    "Zeitpunkt": "01.01.2021 12:34:56",
                    "Zählerstand": "1.234,56",
                    "Einheit": "m3",
                },
                {
                    "Fläche": "H12W34",
                    "Bezeichnung": "Verbrauch Warmwasser H12W34 WC",
                    "Zähler-Nr.": "00000006",
                    "Zeitpunkt": "01.01.2021 12:34:56",
                    "Zählerstand": "1.234,56",
                    "Einheit": "m3",
                },
            ],
        )
    else:
        msg = f'Unknown data ID "{data_id}"'
        raise ValueError(msg)

    return html, expected_table


@pytest.mark.parametrize(
    "data_id",
    [
        "synthetic",
        "newMeterTable.php",
    ],
)
def test_parse_table(data_id: str) -> None:
    """Check that a given HTML string is parsed as a specific expected Table instance."""
    html, expected_table = __testdata(data_id)
    html_table = BeautifulSoup(html, features=BEAUTIFULSOUP_PARSER).find("table")
    parsed_table = parse_table(html_table)

    assert parsed_table == expected_table
