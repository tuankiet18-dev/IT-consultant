from pathlib import Path
import pytest
from nordic_flow.baseline import baseline
from nordic_flow.diagnosis import diagnose
from nordic_flow.io import load_dataset
from nordic_flow.optimiser import solve
from nordic_flow.report import cost_breakdown
from nordic_flow.verify import verify_plan
from nordic_flow.whatif import ChangeError, apply_changes

GOLDEN = Path(__file__).parent.parent / "data" / "golden"


@pytest.fixture
def ds():
    return load_dataset(GOLDEN)[0]


def test_pin_forces_decision_and_costs_more(ds):
    free = solve(ds, "milp")
    pinned = solve(ds, "milp", pins={("A", "S", "SKU-01"): 40})   # keep South on warehouse A (the habit)
    assert pinned.status == "OPTIMAL" and not verify_plan(ds, pinned)
    assert pinned.outbound[("A", "S", "SKU-01")] == 40
    assert pinned.objective > free.objective
    assert cost_breakdown(ds, pinned)["total"] == pytest.approx(700)


def test_pin_on_disallowed_lane_is_infeasible(ds):
    assert solve(ds, "milp", pins={("A", "ZZ", "SKU-01"): 5}).status == "INFEASIBLE"


def test_pin_beyond_capacity_is_infeasible(ds):
    # warehouse B has capacity 60; pinning 70 pallets there cannot work
    assert solve(ds, "milp", pins={("B", "N", "SKU-01"): 70}).status == "INFEASIBLE"


def test_close_warehouse_makes_plan_dearer_or_infeasible(ds):
    closed_b = apply_changes(ds, [{"type": "close_warehouse", "warehouse": "B"}])
    p = solve(closed_b, "milp")
    assert p.status == "OPTIMAL" and p.objective == pytest.approx(700)  # only warehouse A remains: the habit plan
    closed_a = apply_changes(ds, [{"type": "close_warehouse", "warehouse": "A"}])
    assert solve(closed_a, "milp").status == "INFEASIBLE"               # B alone (60) cannot serve 100 pallets
    assert any(c.startswith("capacity") for c in diagnose(closed_a)["likely_causes"])


def test_scale_demand_and_rate_change(ds):
    up = apply_changes(ds, [{"type": "scale_demand", "zone": "N", "factor": 1.5}])
    assert up.demand[("N", "SKU-01")] == 90 and ds.demand[("N", "SKU-01")] == 60   # original untouched
    cheap = apply_changes(ds, [{"type": "set_rate", "kind": "inbound", "from": "S2", "to": "B", "cost": 0}])
    assert solve(cheap, "milp").objective == pytest.approx(460)     # 40 pallets x 1 saved on the used lane


@pytest.mark.parametrize("bad", [{"type": "nope"}, {"type": "close_warehouse", "warehouse": "X"},
                                 {"type": "scale_demand", "zone": "N", "factor": -1},
                                 {"type": "set_rate", "kind": "inbound", "from": "S1", "to": "Q", "cost": 1}])
def test_bad_changes_are_rejected(ds, bad):
    with pytest.raises(ChangeError):
        apply_changes(ds, [bad])
