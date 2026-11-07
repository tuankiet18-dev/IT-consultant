"""Acceptance checks for the ready-to-upload manual input ZIPs."""
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from api.main import create_app

CASES = Path(__file__).parents[1] / "data" / "testcases"


@pytest.mark.parametrize("filename,valid,status,baseline,cost,legs", [
    ("01_three_warehouses.zip", True, 200, 210, 170, 2),
    ("02_required_intermediate_warehouses.zip", True, 200, 170, 170, 2),
    ("03_transfer_limit_5_pallets.zip", True, 200, 210, 190, 2),
    ("04_intermediate_bottleneck.zip", True, 409, None, None, None),
    ("05_invalid_warehouse_cycle.zip", False, 422, None, None, None),
    ("06_cheaper_direct_delivery.zip", True, 200, 210, 70, 0),
    ("07_branching_warehouse_choices.zip", True, 200, 168, 102, 2),
    ("08_branching_more_capacity.zip", True, 200, 168, 84, 1),
])
def test_ready_to_upload_case(tmp_path, filename, valid, status, baseline, cost, legs):
    client = TestClient(create_app(tmp_path / "manual.db"))
    uploaded = client.post("/api/scenarios", files={
        "files": (filename, (CASES / filename).read_bytes(), "application/zip"),
    })
    assert uploaded.status_code == 200, uploaded.text
    scenario = uploaded.json()
    assert scenario["valid"] is valid
    response = client.post(f"/api/scenarios/{scenario['id']}/runs", json={"mode": "milp"})
    assert response.status_code == status, response.text
    if status == 200:
        result = response.json()
        assert result["status"] == "OPTIMAL"
        assert result["comparison"]["baseline"]["total"] == baseline
        assert result["comparison"]["optimised"]["total"] == cost
        assert len(result["optimised"]["transfers"]) == legs
        assert result["verify"]["optimised_violations"] == []
        if filename.startswith("03"):
            deliveries = {row["warehouse"]: row["pallets"] for row in result["optimised"]["outbound"]}
            assert deliveries == {"REG": 5, "LOCAL": 5}
        if filename.startswith("07"):
            assert {(r["from_warehouse"], r["to_warehouse"]): r["pallets"]
                    for r in result["optimised"]["transfers"]} == {("A", "D"): 6, ("B", "E"): 6}
        if filename.startswith("08"):
            assert {(r["from_warehouse"], r["to_warehouse"]): r["pallets"]
                    for r in result["optimised"]["transfers"]} == {("A", "D"): 12}
    elif status == 409:
        assert response.json()["code"] == "no_feasible_plan"
        assert response.json()["details"]["unmet_by_zone_sku"]
    else:
        assert any("acyclic" in issue["message"] for issue in scenario["issues"])
