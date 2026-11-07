"""Manual complete paths are reviewable child plans, with original costs retained."""
import io
import json
import sqlite3
import zipfile

import pytest
from fastapi.testclient import TestClient

from api.db import SCHEMA
from api.main import create_app


@pytest.fixture
def client(tmp_path):
    return TestClient(create_app(tmp_path / "manual-api.db"))


def original(client, mode="milp"):
    scenario = client.post("/api/scenarios/sample", json={"name": "branching"}).json()
    response = client.post(f"/api/scenarios/{scenario['id']}/runs", json={"mode": mode})
    assert response.status_code == 200, response.text
    return scenario, response.json()


def route(path=None, pallets=6, reason="Maintain a warehouse partner relationship"):
    return {"supplier": "SUP1", "warehouses": path or ["B", "D"], "zone": "Z1", "sku": "SKU-01",
            "pallets": pallets, "reason": reason}


def add(client, run, body=None):
    response = client.post(f"/api/runs/{run['id']}/routes", json=body or route())
    assert response.status_code == 200, response.text
    return response.json()


def transfer_map(run):
    return {(row["from_warehouse"], row["to_warehouse"]): row["pallets"] for row in run["optimised"]["transfers"]}


def test_manual_route_creates_child_keeps_original_and_exports_truthful_reason(client):
    _, base = original(client)
    manual = add(client, base)
    assert manual["parent_run_id"] == base["id"] and manual["state"] == "draft"
    assert manual["kind"] == "override"
    assert manual["comparison"]["optimised"]["total"] == 132
    assert manual["optimum_total"] == 102 and manual["cost_of_planner_decisions"] == 30
    assert transfer_map(manual) == {("B", "D"): 6, ("B", "E"): 6}
    assert manual["route_pins"] == [route()]
    assert manual["verify"]["optimised_violations"] == []
    assert client.get(f"/api/runs/{manual['id']}").json()["route_pins"] == [route()]
    stored_original = client.get(f"/api/runs/{base['id']}").json()
    assert stored_original["comparison"]["optimised"]["total"] == 102
    assert stored_original["route_pins"] == []
    explanation = client.post(f"/api/runs/{manual['id']}/explanation").json()
    assert explanation["facts"]["planner_routes"] == [{
        "supplier": "Factory", "warehouses": ["Warehouse B", "Warehouse D"], "zone": "Customer",
        "sku": "Example product", "pallets": 6,
    }]
    assert explanation["facts"]["cost_of_pins"] == 30
    assert "planner reserved 6 pallets" in explanation["text"]
    assert "Factory to Warehouse B to Warehouse D to Customer" in explanation["text"]
    assert "cost difference from the original plan is 30" in explanation["text"]
    assert client.get(f"/api/runs/{manual['id']}/export").status_code == 409
    approved = client.post(f"/api/runs/{manual['id']}/decision", json={"decision": "approve"})
    assert approved.status_code == 200
    archive = zipfile.ZipFile(io.BytesIO(client.get(f"/api/runs/{manual['id']}/export").content))
    assert json.loads(archive.read("manual_routes.json")) == [route()]
    events = client.get(f"/api/audit?scenario_id={base['scenario_id']}").json()
    assert any(event["type"] == "ROUTE_OVERRIDE_APPLIED" for event in events)
    assert client.get("/api/audit/verify").json()["ok"]


def test_route_replacement_append_and_remove_are_new_versions(client):
    _, base = original(client)
    first = add(client, base)
    replaced = add(client, first, route(pallets=4))
    assert len(replaced["route_pins"]) == 1 and replaced["route_pins"][0]["pallets"] == 4
    assert replaced["comparison"]["optimised"]["total"] == 122
    appended = add(client, first, route(["A", "E"]))
    assert len(appended["route_pins"]) == 2
    assert appended["comparison"]["optimised"]["total"] == 144
    removed = client.delete(f"/api/runs/{first['id']}/routes/0")
    assert removed.status_code == 200, removed.text
    restored = removed.json()
    assert restored["route_pins"] == []
    assert restored["comparison"]["optimised"]["total"] == 102
    assert restored["optimum_total"] == 102 and restored["cost_of_planner_decisions"] == 0
    assert client.get(f"/api/runs/{first['id']}").json()["route_pins"] == [route()]
    assert client.delete(f"/api/runs/{restored['id']}/routes/0").status_code == 404


@pytest.mark.parametrize("body", [
    route(["E", "A"]), route(["A", "D", "A"]), route(["UNKNOWN"]),
    {**route(), "supplier": "UNKNOWN"}, {**route(), "sku": "UNKNOWN"}, {**route(), "zone": "UNKNOWN"},
    route(pallets=0.5), route(pallets=13), route(reason=""),
])
def test_invalid_or_missing_paths_never_create_fake_lanes(client, body):
    scenario, base = original(client)
    response = client.post(f"/api/runs/{base['id']}/routes", json=body)
    assert response.status_code == 422, response.text
    assert len(client.get(f"/api/scenarios/{scenario['id']}/runs").json()) == 1
    assert client.get(f"/api/runs/{base['id']}").json()["route_pins"] == []


def test_shared_capacity_conflict_is_rejected_and_audited(client):
    scenario, base = original(client)
    response = client.post(f"/api/runs/{base['id']}/routes", json=route(pallets=7))
    assert response.status_code == 409, response.text
    assert response.json()["code"] == "pins_infeasible"
    assert len(client.get(f"/api/scenarios/{scenario['id']}/runs").json()) == 1
    assert any(event["type"] == "ROUTE_OVERRIDE_REJECTED" for event in client.get(f"/api/audit?run_id={base['id']}").json())


def test_fractional_mode_can_reserve_fractional_complete_paths(client):
    _, base = original(client, "lp")
    manual = add(client, base, route(["A", "E"], 0.5))
    assert manual["route_pins"][0]["pallets"] == 0.5
    assert manual["verify"]["optimised_violations"] == []


def test_final_delivery_pins_and_manual_paths_inherit_each_other(client):
    _, base = original(client)
    manual = add(client, base)
    exact = client.post(f"/api/runs/{manual['id']}/overrides", json={
        "zone": "Z1", "sku": "SKU-01", "warehouse": "E", "pallets": 6, "reason": "Customer delivery requirement",
    })
    assert exact.status_code == 200, exact.text
    assert exact.json()["route_pins"] == [route()]
    assert len(exact.json()["pins"]) == 1
    second = add(client, exact.json(), route(["A", "E"], 6))
    assert second["pins"] == exact.json()["pins"]
    assert second["comparison"]["optimised"]["total"] == 144
    conflict = client.post(f"/api/runs/{manual['id']}/overrides", json={
        "zone": "Z1", "sku": "SKU-01", "warehouse": "E", "pallets": 12, "reason": "Conflicting full delivery",
    })
    assert conflict.status_code == 409


def test_manual_paths_use_effective_whatif_network(client):
    scenario, base = original(client)
    changed = client.post(f"/api/scenarios/{scenario['id']}/whatif", json={
        "changes": [{"type": "set_capacity", "warehouse": "D", "capacity": 12}],
    }).json()
    manual = add(client, changed)
    assert manual["changes"] == changed["changes"]
    assert manual["network"]["warehouses"]["D"]["capacity"] == 12
    assert manual["optimum_total"] == 84
    assert manual["comparison"]["optimised"]["total"] == 114
    assert manual["cost_of_planner_decisions"] == 30
    assert client.get(f"/api/runs/{base['id']}").json()["network"]["warehouses"]["D"]["capacity"] == 6


@pytest.mark.parametrize("decision", ["approve", "reject"])
def test_decided_plans_lock_both_manual_path_operations(client, decision):
    _, base = original(client)
    manual = add(client, base)
    client.post(f"/api/runs/{manual['id']}/decision", json={"decision": decision, "comment": "Reviewed choice"})
    assert client.post(f"/api/runs/{manual['id']}/routes", json=route(["A", "E"])).status_code == 409
    assert client.delete(f"/api/runs/{manual['id']}/routes/0").status_code == 409


def test_original_database_migrates_without_losing_existing_plans_or_approvals(client, tmp_path):
    _, run = original(client)
    client.post(f"/api/runs/{run['id']}/decision", json={"decision": "approve"})
    path = tmp_path / "old-format.db"
    legacy = sqlite3.connect(path)
    legacy.executescript(SCHEMA.replace(",\n  route_pins_json TEXT NOT NULL DEFAULT '[]'", ""))
    for table in ("scenarios", "runs", "audit_events"):
        for row in client.app.state.db.all(f"SELECT * FROM {table}"):
            values = {key: value for key, value in dict(row).items() if key != "route_pins_json"}
            legacy.execute(f"INSERT INTO {table}({','.join(values)}) VALUES({','.join('?' for _ in values)})", tuple(values.values()))
    legacy.commit()
    legacy.close()
    migrated = TestClient(create_app(path))
    restored = migrated.get(f"/api/runs/{run['id']}").json()
    assert restored["route_pins"] == [] and restored["state"] == "approved"
    assert restored["comparison"]["optimised"]["total"] == 102
    assert migrated.get("/api/audit/verify").json()["ok"]
    reopened = TestClient(create_app(path))
    assert reopened.get(f"/api/runs/{run['id']}").json()["route_pins"] == []


def test_human_relationship_reason_does_not_become_an_invented_discount(client):
    _, base = original(client)
    manual = add(client, base, route(reason="A relationship may provide an unconfirmed 50 percent internal discount"))
    explanation = client.post(f"/api/runs/{manual['id']}/explanation").json()
    assert manual["comparison"]["optimised"]["total"] == 132
    assert "discount" not in json.dumps(explanation["facts"]).lower()
    assert "50" not in explanation["text"]
