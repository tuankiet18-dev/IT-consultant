import shutil
from pathlib import Path
import pytest
from nordic_flow.diagnosis import diagnose
from nordic_flow.io import load_dataset
from nordic_flow.optimiser import solve
from nordic_flow.validation import has_errors, validate

GOLDEN = Path(__file__).parent.parent / "data" / "golden"


@pytest.fixture
def folder(tmp_path):
    dst = tmp_path / "d"
    shutil.copytree(GOLDEN, dst)
    return dst


def _edit(path, old, new):
    path.write_text(path.read_text().replace(old, new))


def test_negative_cost_is_reported_with_file_and_row(folder):
    _edit(folder / "inbound_rates.csv", "S1,A,2", "S1,A,-2")
    _, issues = load_dataset(folder)
    assert any(i.severity == "error" and i.file == "inbound_rates.csv" and i.row == 2 for i in issues)


def test_missing_column_blocks(folder):
    _edit(folder / "demand.csv", "zone_id,sku_id,pallets", "zone_id,sku_id,qty")
    _, issues = load_dataset(folder)
    assert any("missing column" in i.message for i in issues)


def test_unknown_reference_and_fractional_demand(folder):
    _edit(folder / "demand.csv", "S,SKU-01,40", "S9,SKU-01,40.5")
    ds, issues = load_dataset(folder)
    msgs = [i.message for i in validate(ds, "milp")]
    assert any("unknown zone" in m for m in msgs)
    assert any("whole pallets" in m for m in msgs)


def test_supply_shortage_is_blocked_and_diagnosed(folder):
    _edit(folder / "supply.csv", "S2,SKU-01,40", "S2,SKU-01,10")
    ds, issues = load_dataset(folder)
    assert has_errors(validate(ds))
    assert solve(ds, "milp").status == "INFEASIBLE"
    d = diagnose(ds)
    assert not d["feasible"]
    assert d["unmet_by_sku"]["SKU-01"] == pytest.approx(30)
    assert any(c.startswith("supply") for c in d["likely_causes"])


def test_capacity_shortage_is_diagnosed(folder):
    _edit(folder / "warehouses.csv", "A,Warehouse A,100,0,0", "A,Warehouse A,20,0,0")
    ds, _ = load_dataset(folder)
    d = diagnose(ds)
    assert not d["feasible"]
    assert any(c.startswith("capacity") for c in d["likely_causes"])


def test_lane_gap_is_diagnosed(folder):
    _edit(folder / "outbound_rates.csv", "A,S,7\n", "")
    _edit(folder / "outbound_rates.csv", "B,S,4\n", "")
    ds, _ = load_dataset(folder)
    assert any("no allowed lane" in i.message for i in validate(ds))
    d = diagnose(ds)
    assert not d["feasible"] and d["unmet_by_zone_sku"][("S", "SKU-01")] == pytest.approx(40)
