"""Direct supplier-to-customer delivery stays explicit in every API output."""
import io
import json
import zipfile

import pytest
from fastapi.testclient import TestClient

from api.main import create_app
from nordic_flow.explain import check_numbers


@pytest.fixture
def client(tmp_path):
    return TestClient(create_app(tmp_path / "direct.db"))


def input_files(*, warehouse=False, direct_cost=4, direct_limit=10):
    files = {
        "suppliers.csv": "supplier_id,name\nSUP1,Factory\n",
        "warehouses.csv": "warehouse_id,name,capacity_pallets,handling_in,handling_out\n",
        "zones.csv": "zone_id,name,preferred_warehouse\nZ1,Customer," + ("A" if warehouse else "") + "\n",
        "skus.csv": "sku_id,name,pallet_factor\nSKU-01,Product,1\n",
        "inbound_rates.csv": "supplier_id,warehouse_id,cost_per_pallet\n",
        "outbound_rates.csv": "warehouse_id,zone_id,cost_per_pallet\n",
        "supply.csv": "supplier_id,sku_id,max_pallets\nSUP1,SKU-01,10\n",
        "demand.csv": "zone_id,sku_id,pallets\nZ1,SKU-01,10\n",
        "direct_rates.csv": f"supplier_id,zone_id,cost_per_pallet,max_pallets\nSUP1,Z1,{direct_cost},{direct_limit}\n",
    }
    if warehouse:
        files["warehouses.csv"] += "A,Warehouse A,10,1,1\n"
        files["inbound_rates.csv"] += "SUP1,A,3\n"
        files["outbound_rates.csv"] += "A,Z1,4\n"
    return files


def upload(client, **kwargs):
    response = client.post("/api/scenarios", files=[
        ("files", (name, value, "text/csv")) for name, value in input_files(**kwargs).items()
    ])
    assert response.status_code == 200, response.text
    scenario = response.json()
    assert scenario["valid"], scenario["issues"]
    return scenario


def run(client, scenario, mode="milp"):
    response = client.post(f"/api/scenarios/{scenario['id']}/runs", json={"mode": mode})
    assert response.status_code == 200, response.text
    return response.json()


@pytest.mark.parametrize("mode", ["milp", "lp"])
def test_zero_warehouse_direct_plan_explanation_ranking_and_export(client, mode):
    scenario = upload(client)
    assert scenario["summary"]["warehouses"] == 0
    assert scenario["summary"]["direct_lanes"] == 1
    result = run(client, scenario, mode)
    assert result["comparison"]["baseline_valid"]
    assert result["comparison"]["baseline"]["total"] == 40
    assert result["comparison"]["optimised"]["total"] == 40
    assert result["optimised"]["direct"] == [{"supplier": "SUP1", "zone": "Z1", "sku": "SKU-01", "pallets": 10}]
    assert result["optimised"]["inbound"] == result["optimised"]["outbound"] == result["optimised"]["transfers"] == []
    assert result["comparison"]["optimised"]["direct_freight"] == 40
    assert result["comparison"]["optimised"]["inbound_handling"] == 0
    assert result["comparison"]["optimised"]["outbound_handling"] == 0
    assert result["verify"]["optimised_violations"] == []
    assert result["network"]["direct_lanes"] == [{
        "supplier": "SUP1", "zone": "Z1", "cost_per_pallet": 4, "max_pallets": 10,
        "available": True, "unavailable_reason": None,
    }]
    response = client.post(f"/api/runs/{result['id']}/explanation")
    assert response.status_code == 200, response.text
    explanation = response.json()
    assert "direct-delivery baseline" in explanation["text"]
    assert "directly from Factory to Customer, without warehouse handling" in explanation["text"]
    assert explanation["facts"]["direct_pallets"] == explanation["facts"]["delivered_pallets"] == 10
    assert check_numbers(explanation["text"], explanation["facts"]) == []
    response = client.get(f"/api/runs/{result['id']}/paths", params={"zone": "Z1", "sku": "SKU-01", "quantity": 10})
    assert response.status_code == 200, response.text
    ranking = response.json()
    path = ranking["paths"][0]
    assert ranking["total_paths"] == 1
    assert path["warehouses"] == []
    assert path["cost_per_pallet"] == path["freight_per_pallet"] == 4
    assert path["handling_per_pallet"] == 0
    assert path["quoted_total"] == path["plan_cost"] == 40
    assert path["plan_pallets"] == path["max_pallets"] == 10
    assert path["can_carry_quantity"]
    assert ranking["plan_accounting"]["total_cost"] == 40
    client.post(f"/api/runs/{result['id']}/decision", json={"decision": "approve"})
    exported = client.get(f"/api/runs/{result['id']}/export")
    assert exported.status_code == 200
    with zipfile.ZipFile(io.BytesIO(exported.content)) as archive:
        assert "SUP1,Z1,SKU-01,10" in archive.read("optimised_direct.csv").decode()
        assert "baseline_direct.csv" in archive.namelist()
        assert archive.read("optimised_inbound.csv").decode().count("\n") == 1


def test_direct_manual_reservation_has_no_phantom_warehouse_and_is_removable(client):
    scenario = upload(client, warehouse=True, direct_cost=12)
    original = run(client, scenario)
    assert original["comparison"]["optimised"]["total"] == 90
    response = client.post(f"/api/runs/{original['id']}/routes", json={
        "supplier": "SUP1", "warehouses": [], "zone": "Z1", "sku": "SKU-01", "pallets": 4,
        "reason": "Customer requires direct delivery",
    })
    assert response.status_code == 200, response.text
    child = response.json()
    assert child["comparison"]["optimised"]["total"] == 102
    assert child["cost_of_planner_decisions"] == 12
    assert child["optimised"]["direct"][0]["pallets"] == 4
    assert child["optimised"]["outbound"][0]["pallets"] == 6
    assert child["route_pins"][0]["warehouses"] == []
    ranked = client.get(f"/api/runs/{child['id']}/paths", params={"zone": "Z1", "sku": "SKU-01"}).json()
    direct = next(path for path in ranked["paths"] if not path["warehouses"])
    assert direct["plan_pallets"] == 4 and direct["plan_cost"] == 48
    assert ranked["plan_accounting"]["total_cost"] == 102
    explanation = client.post(f"/api/runs/{child['id']}/explanation").json()
    assert "along Factory to Customer" in explanation["text"]
    assert check_numbers(explanation["text"], explanation["facts"]) == []
    restored = client.delete(f"/api/runs/{child['id']}/routes/0")
    assert restored.status_code == 200, restored.text
    assert restored.json()["comparison"]["optimised"]["total"] == 90
    assert client.get(f"/api/runs/{original['id']}").json()["optimised"]["direct"] == []


def test_direct_changes_and_partial_capacity_explanation_are_factual(client):
    scenario = upload(client, warehouse=True, direct_cost=4, direct_limit=4)
    result = run(client, scenario)
    assert result["comparison"]["baseline"]["total"] == 90
    assert result["comparison"]["optimised"]["total"] == 70
    assert result["optimised"]["direct"][0]["pallets"] == 4
    explanation = client.post(f"/api/runs/{result['id']}/explanation").json()
    facts = explanation["facts"]
    assert facts["decisions_changed"] == 1
    assert facts["largest_changes"][0]["pallets"] == 4
    assert facts["largest_changes"][0]["optimised_direct_from"] == [{"supplier": "Factory", "pallets": 4}]
    assert "4 pallets directly from Factory" in explanation["text"]
    assert facts["delivered_pallets"] == 10
    assert check_numbers(explanation["text"], facts) == []
    ranking = client.get(f"/api/runs/{result['id']}/paths", params={"zone": "Z1", "sku": "SKU-01", "quantity": 10}).json()
    assert [path["cost_per_pallet"] for path in ranking["paths"]] == [4, 9]
    assert ranking["paths"][0]["max_pallets"] == 4
    assert not ranking["paths"][0]["can_carry_quantity"]


def test_whatif_direct_price_and_closure_metadata_follow_effective_data(client):
    scenario = upload(client, warehouse=True, direct_cost=4)
    original = run(client, scenario)
    changed = client.post(f"/api/scenarios/{scenario['id']}/whatif", json={"changes": [
        {"type": "close_warehouse", "warehouse": "A"},
        {"type": "set_rate", "kind": "direct", "from": "SUP1", "to": "Z1", "cost": 6},
    ]})
    assert changed.status_code == 200, changed.text
    result = changed.json()
    assert result["feasible"] and result["comparison"]["optimised"]["total"] == 60
    assert result["network"]["direct_lanes"][0]["cost_per_pallet"] == 6
    assert not result["network"]["inbound_lanes"][0]["available"]
    ranking = client.get(f"/api/runs/{result['id']}/paths", params={"zone": "Z1", "sku": "SKU-01"}).json()
    assert ranking["total_paths"] == 1 and ranking["paths"][0]["cost_per_pallet"] == 6
    assert client.get(f"/api/runs/{original['id']}").json()["comparison"]["optimised"]["total"] == 40


def test_zero_direct_capacity_is_not_ranked_or_advertised_available(client):
    scenario = upload(client, warehouse=True, direct_limit=0)
    result = run(client, scenario)
    assert not result["network"]["direct_lanes"][0]["available"]
    ranked = client.get(f"/api/runs/{result['id']}/paths", params={"zone": "Z1", "sku": "SKU-01"}).json()
    assert len(ranked["paths"]) == 1 and ranked["paths"][0]["warehouses"] == ["A"]


def test_legacy_saved_run_defaults_direct_without_inventing_deliveries(client):
    scenario = client.post("/api/scenarios/sample", json={"name": "golden"}).json()
    result = run(client, scenario)
    base, optimum, comparison = result["baseline"], result["optimised"], result["comparison"]
    for plan in (base, optimum):
        plan.pop("direct")
    for kind in ("baseline", "optimised"):
        comparison[kind].pop("direct_freight")
    comparison.pop("direct_changes")
    client.app.state.db.execute("UPDATE runs SET baseline_json=?,optimised_json=?,comparison_json=? WHERE id=?", (
        json.dumps(base), json.dumps(optimum), json.dumps(comparison), result["id"],
    ))
    restored = client.get(f"/api/runs/{result['id']}").json()
    assert restored["optimised"]["direct"] == restored["baseline"]["direct"] == []
    assert restored["comparison"]["optimised"]["direct_freight"] == 0
    assert restored["comparison"]["direct_changes"] == []
    explanation = client.post(f"/api/runs/{result['id']}/explanation")
    assert explanation.status_code == 200 and explanation.json()["facts"]["direct_pallets"] == 0
