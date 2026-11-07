"""Upload-ready direct and long-chain cases with independently worked costs."""
import csv
import io
import json
from pathlib import Path
import zipfile

import pytest
from fastapi.testclient import TestClient

from api.main import create_app
from nordic_flow.baseline import baseline
from nordic_flow.cli import main
from nordic_flow.io import REQUIRED, load_dataset
from nordic_flow.optimiser import solve
from nordic_flow.report import cost_breakdown
from nordic_flow.validation import has_errors, validate
from nordic_flow.verify import verify_plan


MVP = Path(__file__).parents[1]
CASES = [
    ("10_direct_factory_customer", 0, 70, 70, 10),
    ("11_chain_3_warehouses", 3, 130, 130, 0),
    ("12_chain_4_warehouses", 4, 160, 160, 0),
    ("13_chain_5_warehouses", 5, 190, 190, 0),
    ("14_chain_8_warehouses", 8, 280, 280, 0),
    ("15_chain_12_warehouses", 12, 400, 400, 0),
    ("16_mixed_direct_chain_5", 5, 190, 145, 3),
]


@pytest.mark.parametrize("stem,count,baseline_cost,optimum,direct_qty", CASES)
def test_shipping_download_matches_flat_source_zip(stem, count, baseline_cost, optimum, direct_qty):
    original = MVP / "data/testcases" / f"{stem}.zip"
    downloadable = MVP / "frontend/public/examples" / f"{stem}.zip"
    assert downloadable.read_bytes() == original.read_bytes()
    source = MVP / "data/shipping_cases" / stem
    with zipfile.ZipFile(original) as archive:
        assert set(REQUIRED) <= set(archive.namelist())
        assert set(archive.namelist()) == {path.name for path in source.glob("*.csv")}
        assert all("/" not in name and "\\" not in name for name in archive.namelist())
        for name in archive.namelist():
            assert archive.read(name) == (source / name).read_bytes()
    if count == 0:
        # Empty header-only warehouse files are genuine direct shipment, not a fake hub.
        for name in ("warehouses.csv", "inbound_rates.csv", "outbound_rates.csv"):
            assert list(csv.DictReader(io.StringIO((source / name).read_text()))) == []


@pytest.mark.parametrize("mode", ["milp", "lp"])
@pytest.mark.parametrize("stem,count,baseline_cost,optimum,direct_qty", CASES)
def test_shipping_sources_have_worked_cost_and_verified_flow(mode, stem, count, baseline_cost, optimum, direct_qty):
    ds, issues = load_dataset(MVP / "data/shipping_cases" / stem)
    assert issues == []
    assert not has_errors(validate(ds, mode))
    assert len(ds.warehouses) == count
    assert len(ds.transfers) == max(0, count - 1)
    base, opt = baseline(ds), solve(ds, mode)
    for plan in (base, opt):
        assert plan.usable
        assert verify_plan(ds, plan) == []
    assert cost_breakdown(ds, base)["total"] == baseline_cost
    assert cost_breakdown(ds, opt)["total"] == optimum
    assert sum(opt.direct.values()) == direct_qty
    warehouse_qty = 10 - direct_qty
    assert sum(opt.inbound.values()) == (warehouse_qty if count else 0)
    assert sum(opt.outbound.values()) == (warehouse_qty if count else 0)
    assert sum(opt.transfers.values()) == max(0, count - 1) * warehouse_qty
    if count:
        unit_cost = 2 + (count - 1) * 1 + 3 + count * 2
        assert unit_cost == 3 * count + 4
        assert cost_breakdown(ds, opt)["total"] == warehouse_qty * unit_cost + direct_qty * 4
    else:
        assert opt.inbound == opt.transfers == opt.outbound == {}
        assert cost_breakdown(ds, opt)["total"] == 10 * 7


@pytest.mark.parametrize("stem,count,baseline_cost,optimum,direct_qty", CASES)
def test_ready_to_upload_shipping_zip_and_ranking(tmp_path, stem, count, baseline_cost, optimum, direct_qty):
    client = TestClient(create_app(tmp_path / f"{stem}.db"))
    archive = MVP / "data/testcases" / f"{stem}.zip"
    uploaded = client.post("/api/scenarios", files={
        "files": (archive.name, archive.read_bytes(), "application/zip"),
    })
    assert uploaded.status_code == 200, uploaded.text
    scenario = uploaded.json()
    assert scenario["valid"] and scenario["issues"] == []
    assert scenario["summary"]["warehouses"] == count
    response = client.post(f"/api/scenarios/{scenario['id']}/runs", json={"mode": "milp"})
    assert response.status_code == 200, response.text
    run = response.json()
    assert run["status"] == "OPTIMAL"
    assert run["comparison"]["baseline"]["total"] == baseline_cost
    assert run["comparison"]["optimised"]["total"] == optimum
    assert run["verify"] == {"baseline_violations": [], "optimised_violations": []}
    assert len(run["optimised"]["transfers"]) == max(0, count - 1)
    assert sum(row["pallets"] for row in run["optimised"]["direct"]) == direct_qty
    assert len(run["network"].get("direct_lanes", [])) == (1 if direct_qty else 0)
    ranking = client.get(f"/api/runs/{run['id']}/paths", params={"zone": "Z1", "sku": "SKU-01", "quantity": 10})
    assert ranking.status_code == 200, ranking.text
    data = ranking.json()
    assert data["plan_accounting"]["delivered_pallets"] == 10
    assert data["plan_accounting"]["total_cost"] == optimum
    assert data["total_paths"] == (2 if stem.startswith("16") else 1)
    if count == 0:
        row = data["paths"][0]
        assert row["warehouses"] == []
        assert row["cost_per_pallet"] == 7 and row["handling_per_pallet"] == 0
        assert row["quoted_total"] == 70 and row["plan_pallets"] == 10
    else:
        row = next(row for row in data["paths"] if len(row["warehouses"]) == count)
        assert row["warehouses"] == [f"W{i:02d}" for i in range(1, count + 1)]
        assert row["cost_per_pallet"] == 3 * count + 4
        if stem.startswith("16"):
            direct = next(row for row in data["paths"] if row["warehouses"] == [])
            assert direct["max_pallets"] == 3 and direct["can_carry_quantity"] is False
            assert direct["plan_pallets"] == 3 and row["plan_pallets"] == 7


@pytest.mark.parametrize("stem,cost", [
    ("10_direct_factory_customer", 70),
    ("13_chain_5_warehouses", 190),
    ("15_chain_12_warehouses", 400),
    ("16_mixed_direct_chain_5", 145),
])
def test_shipping_cli_export_preserves_actual_legs(tmp_path, capsys, stem, cost):
    assert main(["run", str(MVP / "data/shipping_cases" / stem), "--out", str(tmp_path)]) == 0
    comparison = json.loads((tmp_path / "comparison.json").read_text())
    assert comparison["optimised"]["total"] == cost
    assert comparison["baseline_valid"] is True
    assert (tmp_path / "optimised_direct.csv").exists()
    assert "OPTIMAL" in capsys.readouterr().out
