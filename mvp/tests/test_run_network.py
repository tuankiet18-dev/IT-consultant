"""The route diagram must describe the dataset used by this exact run."""
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from api.main import create_app
from api.service import _network_metadata
from nordic_flow.io import load_dataset


@pytest.fixture
def client(tmp_path):
    return TestClient(create_app(tmp_path / "network.db"))


def create_run(client, sample="branching"):
    scenario = client.post("/api/scenarios/sample", json={"name": sample}).json()
    response = client.post(f"/api/scenarios/{scenario['id']}/runs", json={})
    assert response.status_code == 200, response.text
    return scenario, response.json()


def test_run_network_includes_used_and_unused_declared_routes(client):
    _, run = create_run(client)
    network = run["network"]
    assert len(network["inbound_lanes"]) == 3
    assert len(network["transfer_lanes"]) == 9
    assert len(network["outbound_lanes"]) == 3
    assert set(network["warehouses"]) == set("ABCDEF")
    assert network["warehouses"]["D"] == {
        "name": "Warehouse D", "capacity": 6, "handling_in": 1, "handling_out": 1,
    }
    assert {(lane["from_warehouse"], lane["to_warehouse"]) for lane in network["transfer_lanes"]} == {
        (a, b) for a in "ABC" for b in "DEF"
    }
    for kind in ("inbound_lanes", "transfer_lanes", "outbound_lanes"):
        assert all(lane["available"] and lane["unavailable_reason"] is None for lane in network[kind])
    assert network["suppliers"] == {"SUP1": "Factory"}
    assert network["zones"] == {"Z1": "Customer"}
    assert len(run["optimised"]["transfers"]) == 2


@pytest.mark.parametrize("change,kind,keys,value", [
    ({"type": "set_rate", "kind": "inbound", "from": "SUP1", "to": "A", "cost": 9},
     "inbound_lanes", {"supplier": "SUP1", "warehouse": "A"}, 9),
    ({"type": "set_rate", "kind": "transfer", "from": "B", "to": "D", "cost": 2},
     "transfer_lanes", {"from_warehouse": "B", "to_warehouse": "D"}, 2),
    ({"type": "set_rate", "kind": "outbound", "from": "E", "to": "Z1", "cost": 8},
     "outbound_lanes", {"warehouse": "E", "zone": "Z1"}, 8),
])
def test_whatif_network_rates_match_effective_data(client, change, kind, keys, value):
    scenario, original = create_run(client)
    response = client.post(f"/api/scenarios/{scenario['id']}/whatif", json={"changes": [change]})
    assert response.status_code == 200, response.text
    changed = response.json()
    find = lambda network: next(lane for lane in network[kind] if all(lane[key] == val for key, val in keys.items()))
    assert find(changed["network"])["cost_per_pallet"] == value
    assert find(original["network"])["cost_per_pallet"] != value
    assert client.get(f"/api/runs/{changed['id']}").json()["network"] == changed["network"]
    assert client.get(f"/api/runs/{original['id']}").json()["network"] == original["network"]


def test_closed_warehouse_network_and_override_retain_changed_capacity(client):
    scenario, original = create_run(client)
    changed = client.post(f"/api/scenarios/{scenario['id']}/whatif", json={
        "changes": [{"type": "close_warehouse", "warehouse": "D"}],
    }).json()
    network = changed["network"]
    assert network["warehouses"]["D"]["capacity"] == 0
    for lane in network["transfer_lanes"]:
        assert lane["available"] is (lane["to_warehouse"] != "D")
        if not lane["available"]:
            assert "zero handling capacity" in lane["unavailable_reason"]
    assert not next(lane for lane in network["outbound_lanes"] if lane["warehouse"] == "D")["available"]
    child = client.post(f"/api/runs/{changed['id']}/overrides", json={
        "zone": "Z1", "sku": "SKU-01", "warehouse": "E", "pallets": 6, "reason": "Review alternate delivery split",
    })
    assert child.status_code == 200, child.text
    assert child.json()["network"] == network
    assert client.get(f"/api/runs/{original['id']}").json()["network"]["warehouses"]["D"]["capacity"] == 6


def test_expanded_capacity_appears_in_run_network(client):
    scenario, _ = create_run(client)
    changed = client.post(f"/api/scenarios/{scenario['id']}/whatif", json={
        "changes": [{"type": "set_capacity", "warehouse": "D", "capacity": 12}],
    }).json()
    assert changed["network"]["warehouses"]["D"]["capacity"] == 12
    assert all(lane["available"] for lane in changed["network"]["transfer_lanes"])


def test_legacy_saved_plans_get_network_without_storage_migration(client):
    _, run = create_run(client, "golden")
    base, opt, comparison = run["baseline"], run["optimised"], run["comparison"]
    for plan in (base, opt):
        plan.pop("transfers")
    for name in ("baseline", "optimised"):
        comparison[name].pop("transfer_freight")
    client.app.state.db.execute(
        "UPDATE runs SET baseline_json=?,optimised_json=?,comparison_json=? WHERE id=?",
        (json.dumps(base), json.dumps(opt), json.dumps(comparison), run["id"]),
    )
    restored = client.get(f"/api/runs/{run['id']}")
    assert restored.status_code == 200, restored.text
    network = restored.json()["network"]
    assert network["transfer_lanes"] == []
    assert len(network["inbound_lanes"]) == 4
    assert restored.json()["optimised"]["transfers"] == []


def test_local_lane_availability_respects_limits_and_sku_eligibility():
    ds, _ = load_dataset(Path(__file__).parents[1] / "data" / "branching")
    ds.transfer_capacity["B", "D"] = 0
    ds.eligible = {warehouse: {"SKU-01"} for warehouse in ds.warehouses}
    ds.eligible["C"] = set()
    network = _network_metadata(ds)
    transfers = {(lane["from_warehouse"], lane["to_warehouse"]): lane for lane in network["transfer_lanes"]}
    assert not transfers["B", "D"]["available"]
    assert "zero pallet limit" in transfers["B", "D"]["unavailable_reason"]
    assert all(not transfers["C", destination]["available"] for destination in "DEF")
    assert not next(lane for lane in network["inbound_lanes"] if lane["warehouse"] == "C")["available"]
    assert transfers["A", "D"]["available"]
