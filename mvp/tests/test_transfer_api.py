import io
import json
import zipfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from api.main import create_app
from nordic_flow.baseline import baseline
from nordic_flow.explain import build_facts, check_numbers, template_text
from nordic_flow.io import load_dataset
from nordic_flow.report import compare
from nordic_flow.optimiser import solve
from nordic_flow.schema import Warehouse

DATA = Path(__file__).parents[1] / "data"


@pytest.fixture
def client(tmp_path):
    return TestClient(create_app(tmp_path / "transfers.db"))


def sample_run(client):
    scenario = client.post("/api/scenarios/sample", json={"name": "transshipment"}).json()
    assert scenario["valid"]
    response = client.post(f"/api/scenarios/{scenario['id']}/runs", json={})
    assert response.status_code == 200, response.text
    return scenario, response.json()


def test_transfer_sample_cost_facts_override_and_export(client):
    scenario, run = sample_run(client)
    assert scenario["summary"]["transfer_lanes"] == 2
    assert run["comparison"]["baseline"]["total"] == 210
    assert run["comparison"]["optimised"] == {
        "inbound_freight": 20, "transfer_freight": 50, "direct_freight": 0, "inbound_handling": 30,
        "outbound_freight": 40, "outbound_handling": 30, "total": 170,
    }
    assert [(x["from_warehouse"], x["to_warehouse"], x["pallets"]) for x in run["optimised"]["transfers"]] == [
        ("HUB", "REG", 10), ("REG", "LOCAL", 10),
    ]
    assert run["verify"]["optimised_violations"] == []
    explanation = client.post(f"/api/runs/{run['id']}/explanation").json()
    assert len(explanation["facts"]["transfer_movements"]) == 2
    assert explanation["facts"]["transfer_pallet_legs"] == 20
    assert "Central hub" in explanation["text"] and "Local warehouse" in explanation["text"]
    assert check_numbers(explanation["text"], explanation["facts"]) == []

    child = client.post(f"/api/runs/{run['id']}/overrides", json={
        "zone": "Z1", "sku": "SKU-01", "warehouse": "REG", "pallets": 10, "reason": "Regional handover required",
    })
    assert child.status_code == 200, child.text
    assert child.json()["comparison"]["optimised"]["total"] == 210
    assert child.json()["cost_of_planner_decisions"] == 40
    assert client.get(f"/api/runs/{run['id']}").json()["comparison"]["optimised"]["total"] == 170
    assert client.get(f"/api/runs/{run['id']}/export").status_code == 409
    client.post(f"/api/runs/{run['id']}/decision", json={"decision": "approve"})
    exported = client.get(f"/api/runs/{run['id']}/export")
    archive = zipfile.ZipFile(io.BytesIO(exported.content))
    csv = archive.read("optimised_transfers.csv").decode()
    assert "HUB,REG,SKU-01,10" in csv and "REG,LOCAL,SKU-01,10" in csv
    assert "baseline_transfers.csv" in archive.namelist()


def test_upload_zip_with_optional_transfer_file(client):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        for path in (DATA / "transshipment").glob("*.csv"):
            archive.writestr(path.name, path.read_text())
    response = client.post("/api/scenarios", files={"files": ("network.zip", buffer.getvalue(), "application/zip")})
    assert response.status_code == 200, response.text
    scenario = response.json()
    assert scenario["valid"] and scenario["summary"]["transfer_lanes"] == 2
    result = client.post(f"/api/scenarios/{scenario['id']}/runs", json={})
    assert result.status_code == 200 and result.json()["comparison"]["optimised"]["total"] == 170


def test_transfer_bottleneck_returns_whatif_diagnosis(client):
    files = []
    for path in (DATA / "transshipment").glob("*.csv"):
        text = path.read_text()
        if path.name == "inbound_rates.csv":
            text = "supplier_id,warehouse_id,cost_per_pallet\nSUP1,HUB,2\n"
        files.append(("files", (path.name, text, "text/csv")))
    scenario = client.post("/api/scenarios", files=files).json()
    assert scenario["valid"]
    response = client.post(f"/api/scenarios/{scenario['id']}/whatif", json={
        "changes": [{"type": "set_capacity", "warehouse": "REG", "capacity": 5}],
    })
    assert response.status_code == 200, response.text
    assert response.json()["feasible"] is False
    assert response.json()["diagnosis"]["unmet_by_zone_sku"]


def test_legacy_saved_plan_has_empty_transfers_and_explanation(client):
    scenario = client.post("/api/scenarios/sample", json={"name": "golden"}).json()
    run = client.post(f"/api/scenarios/{scenario['id']}/runs", json={}).json()
    baseline_json = run["baseline"]
    optimised_json = run["optimised"]
    comparison = run["comparison"]
    baseline_json.pop("transfers")
    optimised_json.pop("transfers")
    comparison.pop("transfer_changes")
    for name in ("baseline", "optimised"):
        comparison[name].pop("transfer_freight")
    db = client.app.state.db
    db.execute("UPDATE runs SET baseline_json=?,optimised_json=?,comparison_json=? WHERE id=?",
               (json.dumps(baseline_json), json.dumps(optimised_json), json.dumps(comparison), run["id"]))
    historical = client.get(f"/api/runs/{run['id']}").json()
    assert historical["optimised"]["transfers"] == []
    assert historical["comparison"]["optimised"]["transfer_freight"] == 0
    assert historical["comparison"]["optimised"]["total"] == 500
    explanation = client.post(f"/api/runs/{run['id']}/explanation")
    assert explanation.status_code == 200 and "500" in explanation.json()["text"]


def test_fractional_costs_are_consistent_in_standard_summary():
    ds, _ = load_dataset(DATA / "golden")
    ds.inbound = {lane: value * 0.015 for lane, value in ds.inbound.items()}
    ds.outbound = {lane: value * 0.015 for lane, value in ds.outbound.items()}
    base, opt = baseline(ds), solve(ds)
    facts = build_facts(ds, base, opt, compare(ds, base, opt))
    assert (facts["baseline_total"], facts["optimised_total"], facts["saving"]) == (10.5, 7.5, 3)
    text = template_text(facts)
    assert "7.5 cost units against 10.5" in text and "saving of 3" in text
    assert check_numbers(text, facts) == []


def test_actual_reassignment_quantity_and_full_warehouse_labels():
    ds, _ = load_dataset(DATA / "demo")
    base, opt = baseline(ds), solve(ds)
    facts = build_facts(ds, base, opt, compare(ds, base, opt))
    timber = [x for x in facts["largest_changes"] if x["zone"] == "Zone 3" and x["sku"] == "Timber large"]
    assert not timber or timber[0]["pallets"] == 4
    ds, _ = load_dataset(DATA / "golden")
    ds.warehouses["A"] = Warehouse("A", "Warehouse A", 100.5, 0, 0)
    base, opt = baseline(ds), solve(ds)
    facts = build_facts(ds, base, opt, compare(ds, base, opt))
    assert "Warehouse A" not in facts["warehouses_full_in_baseline"]


def test_invalid_baseline_does_not_feed_partial_cost_comparisons_to_ai():
    ds, _ = load_dataset(DATA / "golden")
    base, opt = baseline(ds), solve(ds)
    base.status = "BASELINE_INFEASIBLE"
    comparison = compare(ds, base, opt)
    comparison["baseline_valid"] = False
    comparison["saving"] = comparison["saving_pct"] = None
    facts = build_facts(ds, base, opt, comparison)
    assert facts["cost_change_by_type"] == {}
    assert facts["largest_changes"] == []
    assert facts["saving"] is None
    assert "largest reduction" not in template_text(facts)


def test_transfer_network_keeps_cheaper_direct_delivery_available():
    ds, _ = load_dataset(DATA / "transshipment")
    ds.inbound["SUP1", "LOCAL"] = 1
    plan = solve(ds)
    assert plan.transfers == {}
    assert plan.objective == 70


def test_cli_exports_transfer_legs(tmp_path):
    from nordic_flow.cli import main
    assert main(["run", str(DATA / "transshipment"), "--out", str(tmp_path)]) == 0
    assert "HUB,REG,SKU-01,10" in (tmp_path / "optimised_transfers.csv").read_text()
    assert json.loads((tmp_path / "comparison.json").read_text())["optimised"]["total"] == 170
