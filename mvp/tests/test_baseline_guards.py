"""Guards from the team review: no saving against an unusable baseline, strict verifier, safe ZIP import (T05, T12, G0-01/02)."""
import io
import zipfile
import pytest
from fastapi.testclient import TestClient
from api.main import create_app
from nordic_flow.baseline import baseline
from nordic_flow.io import load_dataset
from nordic_flow.optimiser import solve
from nordic_flow.schema import Plan
from nordic_flow.verify import verify_plan

# Greedy trap: Z1 is served first from warehouse A using the cheapest supplier (S1) and uses up all of S1's supply.
# Z2 can only be served through B, and B can only be supplied by S1, so the greedy baseline strands Z2.
TRAP = {
    "suppliers.csv": "supplier_id,name\nS1,Supplier 1\nS2,Supplier 2\n",
    "warehouses.csv": "warehouse_id,name,capacity_pallets,handling_in,handling_out\nA,Warehouse A,100,0,0\nB,Warehouse B,100,0,0\n",
    "zones.csv": "zone_id,name,preferred_warehouse\nZ1,Zone 1,A\nZ2,Zone 2,B\n",
    "skus.csv": "sku_id,name,pallet_factor\nSKU-01,Item,1\n",
    "inbound_rates.csv": "supplier_id,warehouse_id,cost_per_pallet\nS1,A,1\nS2,A,5\nS1,B,1\n",
    "outbound_rates.csv": "warehouse_id,zone_id,cost_per_pallet\nA,Z1,1\nB,Z1,9\nB,Z2,1\n",
    "supply.csv": "supplier_id,sku_id,max_pallets\nS1,SKU-01,10\nS2,SKU-01,10\n",
    "demand.csv": "zone_id,sku_id,pallets\nZ1,SKU-01,10\nZ2,SKU-01,10\n",
}


@pytest.fixture
def trap_dir(tmp_path):
    for k, v in TRAP.items():
        (tmp_path / k).write_text(v)
    return tmp_path


def test_greedy_baseline_fails_but_solver_succeeds(trap_dir):
    ds, issues = load_dataset(trap_dir)
    assert not issues
    b, o = baseline(ds), solve(ds, "milp")
    assert b.status == "BASELINE_INFEASIBLE" and b.shortfall == {("Z2", "SKU-01"): 10}
    assert o.status == "OPTIMAL" and not verify_plan(ds, o)


def test_verifier_is_strict_about_shortfall(trap_dir):
    ds = load_dataset(trap_dir)[0]
    b = baseline(ds)
    assert any("unmet" in v for v in verify_plan(ds, b))
    assert verify_plan(ds, b, allow_shortfall=True) == []        # only diagnosis may relax this


def test_api_reports_no_saving_for_unusable_baseline(trap_dir, tmp_path):
    c = TestClient(create_app(tmp_path / "t.db", llm_factory=lambda: type("L", (), {"enabled": False, "model": ""})()))
    files = [("files", (k, v, "text/csv")) for k, v in TRAP.items()]
    s = c.post("/api/scenarios", files=files).json()
    assert s["valid"]
    r = c.post(f"/api/scenarios/{s['id']}/runs", json={}).json()
    cmp = r["comparison"]
    assert cmp["baseline_valid"] is False and cmp["saving"] is None and cmp["saving_pct"] is None
    assert r["status"] == "OPTIMAL"
    e = c.post(f"/api/runs/{r['id']}/explanation").json()
    assert "no saving is reported" in e["text"] and "%" not in e["text"]


def _zip(entries: dict[str, bytes | str]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        for name, data in entries.items():
            z.writestr(name, data)
    return buf.getvalue()


@pytest.fixture
def client(tmp_path):
    return TestClient(create_app(tmp_path / "t.db", llm_factory=lambda: type("L", (), {"enabled": False, "model": ""})()))


def test_zip_import_works_for_a_flat_allowlisted_archive(client):
    r = client.post("/api/scenarios", files=[("files", ("data.zip", _zip(TRAP), "application/zip"))])
    assert r.status_code == 200 and r.json()["source"] == "upload:zip" and r.json()["valid"]


@pytest.mark.parametrize("entries,code", [
    ({"../evil.csv": "x"}, "unsafe_zip"),
    ({"sub/demand.csv": "x"}, "unsafe_zip"),
    ({"notes.txt": "x"}, "unexpected_file"),
    ({"demand.csv": "x" * 2_100_000}, "zip_too_large"),
])
def test_zip_import_rejects_unsafe_or_unexpected_content(client, entries, code):
    r = client.post("/api/scenarios", files=[("files", ("data.zip", _zip(entries), "application/zip"))])
    assert r.status_code == 422 and r.json()["code"] == code


def test_not_a_zip_is_rejected_cleanly(client):
    r = client.post("/api/scenarios", files=[("files", ("data.zip", b"not a zip", "application/zip"))])
    assert r.status_code == 422 and r.json()["code"] == "bad_zip"


def test_pin_must_be_whole_pallets_in_milp(client):
    s = client.post("/api/scenarios/sample", json={"name": "golden"}).json()
    run = client.post(f"/api/scenarios/{s['id']}/runs", json={}).json()
    r = client.post(f"/api/runs/{run['id']}/overrides",
                    json={"zone": "S", "sku": "SKU-01", "warehouse": "A", "pallets": 12.5, "reason": "test"})
    assert r.status_code == 422 and r.json()["code"] == "whole_pallets"
