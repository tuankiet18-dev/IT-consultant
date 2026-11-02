"""Hand-checkable example from the Round 1 deck (slide 7): baseline 700, optimum 500."""
from pathlib import Path
import pytest
from nordic_flow.baseline import baseline
from nordic_flow.io import load_dataset
from nordic_flow.optimiser import solve
from nordic_flow.report import compare, cost_breakdown
from nordic_flow.validation import has_errors, validate
from nordic_flow.verify import verify_plan

GOLDEN = Path(__file__).parent.parent / "data" / "golden"


@pytest.fixture(scope="module")
def ds():
    d, issues = load_dataset(GOLDEN)
    assert not issues and not has_errors(validate(d))
    return d


def test_baseline_is_700(ds):
    b = baseline(ds)
    assert b.status == "BASELINE"
    assert cost_breakdown(ds, b)["total"] == 700
    assert not verify_plan(ds, b)


@pytest.mark.parametrize("mode", ["lp", "milp"])
def test_optimum_is_500_and_valid(ds, mode):
    o = solve(ds, mode)
    assert o.status == "OPTIMAL"
    assert o.objective == pytest.approx(500)
    assert cost_breakdown(ds, o)["total"] == pytest.approx(500)
    assert not verify_plan(ds, o)
    assert o.outbound == {("A", "N", "SKU-01"): 60, ("B", "S", "SKU-01"): 40}


def test_comparison_saving_is_28_57_percent(ds):
    c = compare(ds, baseline(ds), solve(ds, "milp"))
    assert c["saving"] == pytest.approx(200)
    assert c["saving_pct"] == pytest.approx(28.5714, abs=1e-3)
    assert c["binding_warehouses"] == []          # neither warehouse is full in the optimum
    assert c["utilisation_baseline"]["A"] == 1.0   # the habit plan fills warehouse A completely
