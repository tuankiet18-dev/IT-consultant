"""Warehouse order comes from allowed directed links, not warehouse IDs."""
import io
import json
from pathlib import Path
import zipfile

import pytest
from fastapi.testclient import TestClient

from api.main import create_app
from nordic_flow.baseline import baseline
from nordic_flow.cli import main
from nordic_flow.io import load_dataset
from nordic_flow.optimiser import solve
from nordic_flow.report import cost_breakdown
from nordic_flow.validation import has_errors, validate
from nordic_flow.verify import verify_plan


DATA = Path(__file__).parents[1] / "data"
SAMPLE = DATA / "reordered"
ZIP = DATA / "testcases" / "09_reordered_warehouses.zip"


@pytest.mark.parametrize("mode", ["lp", "milp"])
def test_warehouse_e_can_precede_warehouse_a(mode):
    dataset, issues = load_dataset(SAMPLE)
    assert issues == [] and not has_errors(validate(dataset, mode))
    assert list(dataset.warehouses) == ["A", "E"]
    assert set(dataset.inbound) == {("SUP1", "E")}
    assert set(dataset.transfers) == {("E", "A")}
    assert set(dataset.outbound) == {("A", "Z1")}
    for plan in (baseline(dataset), solve(dataset, mode)):
        assert plan.usable and verify_plan(dataset, plan) == []
        assert plan.inbound == {("SUP1", "E", "SKU-01"): 12}
        assert plan.transfers == {("E", "A", "SKU-01"): 12}
        assert plan.outbound == {("A", "Z1", "SKU-01"): 12}
        assert cost_breakdown(dataset, plan) == {
            "inbound_freight": 24, "transfer_freight": 36, "direct_freight": 0,
            "outbound_freight": 48, "inbound_handling": 24,
            "outbound_handling": 24, "total": 156,
        }


def test_ready_to_upload_reordered_zip(tmp_path):
    client = TestClient(create_app(tmp_path / "reordered.db"))
    uploaded = client.post("/api/scenarios", files={
        "files": (ZIP.name, ZIP.read_bytes(), "application/zip"),
    })
    assert uploaded.status_code == 200, uploaded.text
    scenario = uploaded.json()
    assert scenario["valid"] and scenario["issues"] == []
    assert scenario["summary"]["warehouses"] == 2
    result = client.post(f"/api/scenarios/{scenario['id']}/runs", json={})
    assert result.status_code == 200, result.text
    run = result.json()
    assert run["status"] == "OPTIMAL"
    assert run["comparison"]["baseline"]["total"] == 156
    assert run["comparison"]["optimised"]["total"] == 156
    assert run["verify"] == {"baseline_violations": [], "optimised_violations": []}
    assert run["optimised"]["transfers"] == [{
        "from_warehouse": "E", "to_warehouse": "A", "sku": "SKU-01", "pallets": 12,
    }]
    assert run["network"]["inbound_lanes"][0]["warehouse"] == "E"
    assert run["network"]["outbound_lanes"][0]["warehouse"] == "A"


def test_adding_both_directions_creates_a_rejected_cycle(tmp_path):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in SAMPLE.glob("*.csv"):
            content = path.read_text(encoding="utf-8")
            if path.name == "transfer_rates.csv":
                content += "A,E,3,12\n"
            archive.writestr(path.name, content)
    client = TestClient(create_app(tmp_path / "cycle.db"))
    uploaded = client.post("/api/scenarios", files={
        "files": ("cycle.zip", buffer.getvalue(), "application/zip"),
    })
    assert uploaded.status_code == 200, uploaded.text
    scenario = uploaded.json()
    assert scenario["valid"] is False
    assert any("acyclic" in issue["message"] for issue in scenario["issues"])
    response = client.post(f"/api/scenarios/{scenario['id']}/runs", json={})
    assert response.status_code == 422 and response.json()["code"] == "invalid_data"


def test_cli_exports_reordered_warehouse_flow(tmp_path, capsys):
    assert main(["run", str(SAMPLE), "--out", str(tmp_path)]) == 0
    assert "E,A,SKU-01,12" in (tmp_path / "optimised_transfers.csv").read_text()
    report = json.loads((tmp_path / "comparison.json").read_text())
    assert report["baseline_valid"] is True
    assert report["baseline"]["total"] == report["optimised"]["total"] == 156
    assert "OPTIMAL" in capsys.readouterr().out
