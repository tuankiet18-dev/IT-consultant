"""CSV examples shown to users must match the actual upload parser's headers."""
import csv
import io
import json
from pathlib import Path
import re

import pytest

from nordic_flow.io import REQUIRED, OPTIONAL

GUIDE = Path(__file__).parents[1] / "frontend" / "src" / "views" / "GuideView.jsx"
TEXT = GUIDE.read_text(encoding="utf-8")
EXAMPLES = dict(re.findall(r'\{ name: "([^"\n]+\.csv)".*?csv: ("(?:[^"\\]|\\.)*")', TEXT, re.S))


@pytest.mark.parametrize("filename,columns", list(REQUIRED.items()) + list(OPTIONAL.items()))
def test_guide_csv_example_has_real_required_headers_and_rectangular_rows(filename, columns):
    example = json.loads(EXAMPLES[filename])
    rows = list(csv.reader(io.StringIO(example)))
    assert set(columns) <= set(rows[0])
    assert len(rows[0]) == len(set(rows[0]))
    assert all(len(row) == len(rows[0]) for row in rows[1:])


def test_guide_covers_exactly_the_supported_csv_files():
    assert set(EXAMPLES) == set(REQUIRED) | set(OPTIONAL)


@pytest.mark.parametrize("row", ["S,SKU-01,10,extra", "S,SKU-01"])
def test_malformed_csv_row_is_reported_instead_of_crashing_upload(tmp_path, row):
    from fastapi.testclient import TestClient
    from api.main import create_app
    golden = Path(__file__).parents[1] / "data" / "golden"
    files = [("files", (path.name, path.read_text(encoding="utf-8"), "text/csv"))
             for path in golden.glob("*.csv") if path.name != "demand.csv"]
    files.append(("files", ("demand.csv", "zone_id,sku_id,pallets\n" + row + "\n", "text/csv")))
    response = TestClient(create_app(tmp_path / "bad-row.db")).post("/api/scenarios", files=files)
    assert response.status_code == 200, response.text
    assert not response.json()["valid"]
    assert any(issue["file"] == "demand.csv" and issue["row"] == 2
               and "same number" in issue["message"] for issue in response.json()["issues"])
