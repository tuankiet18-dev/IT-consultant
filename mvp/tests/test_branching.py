"""A 3-by-3 network must choose complete paths and respect shared capacity."""
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from api.main import create_app
from nordic_flow.io import load_dataset


def test_branching_path_costs_can_be_checked_by_hand():
    ds, issues = load_dataset(Path(__file__).parents[1] / "data" / "branching")
    assert issues == []
    assert set(ds.inbound) == {("SUP1", w) for w in "ABC"}
    assert set(ds.outbound) == {(w, "Z1") for w in "DEF"}
    # Factory freight + transfer freight + final freight + two receipts and dispatches.
    costs = {
        (a, b): ds.inbound["SUP1", a] + rate + ds.outbound[b, "Z1"]
        + ds.warehouses[a].handling_in + ds.warehouses[a].handling_out
        + ds.warehouses[b].handling_in + ds.warehouses[b].handling_out
        for (a, b), rate in ds.transfers.items()
    }
    assert costs == {
        ("A", "D"): 7, ("A", "E"): 12, ("A", "F"): 16,
        ("B", "D"): 12, ("B", "E"): 10, ("B", "F"): 15,
        ("C", "D"): 15, ("C", "E"): 15, ("C", "F"): 14,
    }
    # The cheapest path is limited to six pallets at D. The next cheapest serves the rest.
    assert 6 * costs["A", "D"] + 6 * costs["B", "E"] == 102
    assert 12 * min(costs[a, "F"] for a in "ABC") == 168


@pytest.mark.parametrize("mode", ["milp", "lp"])
def test_branching_sample_splits_then_reroutes_when_capacity_changes(tmp_path, mode):
    client = TestClient(create_app(tmp_path / "branching.db"))
    assert "branching" in client.get("/api/config").json()["samples"]
    scenario = client.post("/api/scenarios/sample", json={"name": "branching"}).json()
    assert scenario["valid"] and scenario["issues"] == []
    assert scenario["summary"]["warehouses"] == 6
    assert scenario["summary"]["transfer_lanes"] == 9
    assert {(r["from_warehouse"], r["to_warehouse"]) for r in scenario["entities"]["transfer_lanes"]} == {
        (a, b) for a in "ABC" for b in "DEF"
    }
    response = client.post(f"/api/scenarios/{scenario['id']}/runs", json={"mode": mode})
    assert response.status_code == 200, response.text
    run = response.json()
    assert run["status"] == "OPTIMAL"
    assert run["comparison"]["baseline"]["total"] == 168
    assert run["comparison"]["optimised"] == {
        "inbound_freight": 24, "transfer_freight": 12, "direct_freight": 0, "outbound_freight": 18,
        "inbound_handling": 24, "outbound_handling": 24, "total": 102,
    }
    assert run["verify"]["optimised_violations"] == []
    assert {(r["from_warehouse"], r["to_warehouse"]): r["pallets"]
            for r in run["optimised"]["transfers"]} == {("A", "D"): 6, ("B", "E"): 6}

    explanation = client.post(f"/api/runs/{run['id']}/explanation").json()
    assert "Warehouse A to Warehouse D" in explanation["text"]
    assert "Warehouse B to Warehouse E" in explanation["text"]
    assert explanation["facts"]["transfer_pallet_legs"] == 12

    for change, expected, lane in [
        ({"type": "close_warehouse", "warehouse": "D"}, 120, ("B", "E")),
        ({"type": "set_capacity", "warehouse": "D", "capacity": 12}, 84, ("A", "D")),
    ]:
        changed = client.post(f"/api/scenarios/{scenario['id']}/whatif", json={
            "changes": [change], "mode": mode, "reference_run_id": run["id"],
        })
        assert changed.status_code == 200, changed.text
        result = changed.json()
        assert result["comparison"]["optimised"]["total"] == expected
        assert result["verify"]["optimised_violations"] == []
        assert {(r["from_warehouse"], r["to_warehouse"]): r["pallets"]
                for r in result["optimised"]["transfers"]} == {lane: 12}
    # What-if copies must leave the original available network and result intact.
    assert client.get(f"/api/scenarios/{scenario['id']}").json()["entities"]["warehouses"]["D"]["capacity"] == 6
    assert client.get(f"/api/runs/{run['id']}").json()["comparison"]["optimised"]["total"] == 102
