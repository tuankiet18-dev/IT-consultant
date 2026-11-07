"""Direct factory-to-customer freight shares supply, demand and lane limits."""
from pathlib import Path

import pytest

from nordic_flow.baseline import baseline
from nordic_flow.cli import main
from nordic_flow.diagnosis import diagnose
from nordic_flow.io import load_dataset
from nordic_flow.manual_routes import reserved_flows, validate_manual_routes, verify_manual_routes
from nordic_flow.optimiser import solve
from nordic_flow.report import compare, cost_breakdown, utilisation
from nordic_flow.schema import Dataset, Plan, Sku, Supplier, Warehouse, Zone
from nordic_flow.validation import has_errors, validate
from nordic_flow.verify import verify_plan
from nordic_flow.whatif import apply_changes


def direct_dataset(with_warehouse=False, direct_rate=4, cap=None):
    dataset = Dataset(
        suppliers={"S1": Supplier("S1", "Factory")},
        zones={"Z1": Zone("Z1", "Customer", "W" if with_warehouse else "")},
        skus={"P1": Sku("P1", "Product", 1)},
        supply={("S1", "P1"): 10}, demand={("Z1", "P1"): 10},
        direct={("S1", "Z1"): direct_rate},
    )
    if cap is not None:
        dataset.direct_capacity["S1", "Z1"] = cap
    if with_warehouse:
        dataset.warehouses["W"] = Warehouse("W", "Warehouse", 10, 1, 1)
        dataset.inbound["S1", "W"] = 1
        dataset.outbound["W", "Z1"] = 3
    return dataset


@pytest.mark.parametrize("mode", ["milp", "lp"])
def test_direct_only_needs_no_warehouse_and_pays_no_handling(mode):
    ds = direct_dataset()
    assert validate(ds, mode) == []
    plan = solve(ds, mode)
    assert plan.status == "OPTIMAL"
    assert plan.direct == {("S1", "Z1", "P1"): 10}
    assert plan.inbound == plan.outbound == plan.transfers == {}
    assert verify_plan(ds, plan) == []
    assert cost_breakdown(ds, plan) == {
        "inbound_freight": 0, "transfer_freight": 0, "direct_freight": 40,
        "inbound_handling": 0, "outbound_freight": 0, "outbound_handling": 0, "total": 40,
    }
    base = baseline(ds)
    assert base.status == "BASELINE"
    assert base.direct == plan.direct and verify_plan(ds, base) == []
    assert compare(ds, base, plan)["saving"] == 0
    assert utilisation(ds, plan) == {}


@pytest.mark.parametrize("direct_rate,expected_direct,expected_cost", [(4, 10, 40), (9, 0, 60)])
def test_solver_compares_direct_with_full_warehouse_cost(direct_rate, expected_direct, expected_cost):
    ds = direct_dataset(True, direct_rate)
    base, plan = baseline(ds), solve(ds)
    assert cost_breakdown(ds, base)["total"] == 60
    assert sum(plan.direct.values()) == expected_direct
    assert cost_breakdown(ds, plan)["total"] == expected_cost
    assert verify_plan(ds, plan) == []
    comparison = compare(ds, base, plan)
    if expected_direct:
        assert comparison["direct_changes"] == [{"supplier": "S1", "zone": "Z1", "sku": "P1", "baseline": 0, "optimised": 10}]
    else:
        assert comparison["direct_changes"] == []


def test_direct_limit_splits_goods_and_does_not_consume_warehouse_capacity():
    ds = direct_dataset(True, cap=6)
    ds.warehouses["W"] = Warehouse("W", "Warehouse", 4, 1, 1)
    assert not has_errors(validate(ds))
    for plan in (baseline(ds), solve(ds)):
        assert plan.direct == {("S1", "Z1", "P1"): 6}
        assert plan.outbound == {("W", "Z1", "P1"): 4}
        assert cost_breakdown(ds, plan)["total"] == 48
        assert utilisation(ds, plan) == {"W": 1}
        assert verify_plan(ds, plan) == []


def test_direct_lane_limit_is_shared_across_products():
    ds = direct_dataset(True, cap=8)
    ds.skus["P2"] = Sku("P2", "Second product", 1)
    ds.supply = {("S1", "P1"): 6, ("S1", "P2"): 6}
    ds.demand = {("Z1", "P1"): 6, ("Z1", "P2"): 6}
    ds.warehouses["W"] = Warehouse("W", "Warehouse", 12, 1, 1)
    plan = solve(ds)
    assert sum(plan.direct.values()) == 8
    assert sum(plan.outbound.values()) == 4
    assert cost_breakdown(ds, plan)["total"] == 56
    assert verify_plan(ds, plan) == []
    # The greedy reference still uses warehouses first.
    assert cost_breakdown(ds, baseline(ds))["total"] == 72


def test_closed_direct_route_uses_warehouse_or_reports_no_path():
    ds = direct_dataset(True, cap=0)
    plan = solve(ds)
    assert plan.direct == {}
    assert cost_breakdown(ds, plan)["total"] == 60
    ds = direct_dataset(cap=0)
    assert has_errors(validate(ds))
    assert solve(ds).status == "INFEASIBLE"
    diagnostic = diagnose(ds)
    assert not diagnostic["feasible"]
    assert diagnostic["unmet_by_zone_sku"] == {("Z1", "P1"): 10}


@pytest.mark.parametrize("quantity", [-1, float("nan"), float("inf"), True, 1.5])
def test_independent_verifier_rejects_invalid_direct_quantity(quantity):
    ds = direct_dataset()
    plan = Plan("OPTIMAL", "milp", direct={("S1", "Z1", "P1"): quantity})
    assert any("quantity" in issue for issue in verify_plan(ds, plan))


def test_independent_verifier_checks_supply_demand_lane_and_capacity():
    ds = direct_dataset(cap=6)
    plan = Plan("OPTIMAL", "milp", direct={("S1", "Z1", "P1"): 11})
    issues = verify_plan(ds, plan)
    assert any("direct capacity exceeded" in issue for issue in issues)
    assert any("supply exceeded" in issue for issue in issues)
    assert any("demand not met" in issue for issue in issues)
    ds.direct = {}
    assert any("not allowed" in issue for issue in verify_plan(ds, plan))
    plan.direct = {("unknown", "Z1", "P1"): 10}
    assert any("unknown direct reference" in issue for issue in verify_plan(ds, plan))


def test_direct_and_warehouse_flows_share_supplier_supply():
    ds = direct_dataset(True)
    plan = Plan("OPTIMAL", "milp", inbound={("S1", "W", "P1"): 5},
                outbound={("W", "Z1", "P1"): 5}, direct={("S1", "Z1", "P1"): 10})
    assert any("supply exceeded" in issue for issue in verify_plan(ds, plan))
    assert any("demand not met" in issue for issue in verify_plan(ds, plan))


def test_direct_manual_route_reserves_empty_warehouse_path():
    ds = direct_dataset(True, direct_rate=9)
    route = {"supplier": "S1", "warehouses": [], "zone": "Z1", "sku": "P1", "pallets": 6,
             "reason": "Agreed direct delivery"}
    assert validate_manual_routes(ds, [route]) == []
    assert reserved_flows([route]) == ({}, {}, {}, {("S1", "Z1", "P1"): 6})
    plan = solve(ds, route_pins=[route])
    assert cost_breakdown(ds, plan)["total"] == 78
    assert plan.direct == {("S1", "Z1", "P1"): 6}
    assert verify_plan(ds, plan) == verify_manual_routes(ds, plan, [route]) == []
    assert solve(ds, pins={("W", "Z1", "P1"): 10}, route_pins=[route]).status == "INFEASIBLE"
    plan.direct.clear()
    assert any("direct requirement not met" in issue for issue in verify_manual_routes(ds, plan, [route]))
    ds.direct.clear()
    assert any("not declared" in issue for issue in validate_manual_routes(ds, [route]))


def test_direct_whatif_rate_changes_copy_and_warehouse_closure_leaves_direct_open():
    ds = direct_dataset(True)
    changed = apply_changes(ds, [{"type": "set_rate", "kind": "direct", "from": "S1", "to": "Z1", "cost": 2},
                                 {"type": "close_warehouse", "warehouse": "W"}])
    assert ds.direct["S1", "Z1"] == 4
    assert cost_breakdown(changed, solve(changed))["total"] == 20
    assert solve(changed).direct == {("S1", "Z1", "P1"): 10}


def write_direct_csvs(folder, direct_rows="S1,Z1,4,\n"):
    content = {
        "suppliers.csv": "supplier_id,name\nS1,Factory\n",
        "warehouses.csv": "warehouse_id,name,capacity_pallets,handling_in,handling_out\n",
        "zones.csv": "zone_id,name,preferred_warehouse\nZ1,Customer,\n",
        "skus.csv": "sku_id,name,pallet_factor\nP1,Product,1\n",
        "inbound_rates.csv": "supplier_id,warehouse_id,cost_per_pallet\n",
        "outbound_rates.csv": "warehouse_id,zone_id,cost_per_pallet\n",
        "supply.csv": "supplier_id,sku_id,max_pallets\nS1,P1,10\n",
        "demand.csv": "zone_id,sku_id,pallets\nZ1,P1,10\n",
        "direct_rates.csv": "supplier_id,zone_id,cost_per_pallet,max_pallets\n" + direct_rows,
    }
    for name, text in content.items():
        (folder / name).write_text(text, encoding="utf-8")


def test_optional_direct_csv_and_cli_exports(tmp_path):
    write_direct_csvs(tmp_path)
    ds, issues = load_dataset(tmp_path)
    assert issues == validate(ds) == []
    assert ds.direct == {("S1", "Z1"): 4} and ds.direct_capacity == {}
    destination = tmp_path / "output"
    assert main(["run", str(tmp_path), "--out", str(destination)]) == 0
    assert "S1,Z1,P1,10" in (destination / "optimised_direct.csv").read_text()
    assert "S1,Z1,P1,10" in (destination / "baseline_direct.csv").read_text()


@pytest.mark.parametrize("rows", ["S1,Z1,-1,\n", "S1,Z1,nan,\n", "S1,Z1,4,-1\n", "S1,Z1,4,inf\n", "S1,Z1,4,\nS1,Z1,5,\n"])
def test_malformed_direct_csv_is_not_silently_fixed(tmp_path, rows):
    write_direct_csvs(tmp_path, rows)
    _, issues = load_dataset(tmp_path)
    assert has_errors(issues)
    assert any(issue.file == "direct_rates.csv" and issue.row is not None for issue in issues)


@pytest.mark.parametrize("change", ["supplier", "zone", "negative", "nan", "orphan_capacity"])
def test_direct_semantic_checks_reject_bad_references_and_limits(change):
    ds = direct_dataset()
    if change == "supplier": ds.direct = {("missing", "Z1"): 4}
    if change == "zone": ds.direct = {("S1", "missing"): 4}
    if change == "negative": ds.direct_capacity["S1", "Z1"] = -1
    if change == "nan": ds.direct["S1", "Z1"] = float("nan")
    if change == "orphan_capacity": ds.direct_capacity["S1", "missing"] = 1
    assert any(issue.file == "direct_rates.csv" and issue.severity == "error" for issue in validate(ds))


def test_old_data_without_direct_file_preserves_original_costs():
    ds, issues = load_dataset(Path(__file__).parents[1] / "data" / "golden")
    assert issues == [] and ds.direct == ds.direct_capacity == {}
    base, plan = baseline(ds), solve(ds)
    assert cost_breakdown(ds, base)["total"] == 700
    assert cost_breakdown(ds, plan)["total"] == 500
    assert cost_breakdown(ds, plan)["direct_freight"] == 0
    assert plan.direct == {} and verify_plan(ds, plan) == []
