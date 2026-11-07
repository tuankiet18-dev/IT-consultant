"""Hand-checkable regressions for optional, multi-warehouse transfer flows."""
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
import shutil

import pytest

from nordic_flow.baseline import baseline
from nordic_flow.io import load_dataset
from nordic_flow.optimiser import solve
from nordic_flow.report import compare, cost_breakdown, utilisation
from nordic_flow.schema import Sku, Zone
from nordic_flow.validation import has_errors, validate
from nordic_flow.verify import verify_plan
from nordic_flow.whatif import apply_changes


DATA = Path(__file__).parent.parent / "data"


@pytest.fixture
def chain():
    dataset, issues = load_dataset(DATA / "transshipment")
    assert not issues and not has_errors(validate(dataset))
    return dataset


@pytest.fixture
def folder(tmp_path):
    target = tmp_path / "dataset"
    shutil.copytree(DATA / "transshipment", target)
    return target


def test_three_warehouses_conserve_goods_and_charge_each_handling_step(chain):
    plan = solve(chain)
    assert plan.status == "OPTIMAL"
    assert plan.inbound == {("SUP1", "HUB", "SKU-01"): 10}
    assert plan.transfers == {("HUB", "REG", "SKU-01"): 10, ("REG", "LOCAL", "SKU-01"): 10}
    assert plan.outbound == {("LOCAL", "Z1", "SKU-01"): 10}
    assert verify_plan(chain, plan) == []
    # Ten pallets pay 2 + 3 + 2 + 4 freight and six handling charges of 1.
    assert cost_breakdown(chain, plan) == {
        "inbound_freight": 20, "transfer_freight": 50, "direct_freight": 0, "inbound_handling": 30,
        "outbound_freight": 40, "outbound_handling": 30, "total": 170,
    }
    assert plan.objective == pytest.approx(170)
    assert utilisation(chain, plan) == {"HUB": 0.5, "REG": 0.5, "LOCAL": 0.5}


def test_baseline_keeps_preferred_final_warehouse_and_can_receive_via_transfers(chain):
    plan = baseline(chain)
    assert plan.status == "BASELINE" and verify_plan(chain, plan) == []
    assert plan.transfers == {("HUB", "REG", "SKU-01"): 10}
    assert plan.outbound == {("REG", "Z1", "SKU-01"): 10}
    comparison = compare(chain, plan, solve(chain))
    assert comparison["baseline"]["total"] == 210
    assert comparison["optimised"]["total"] == 170
    assert comparison["saving"] == 40


def test_reachability_accepts_a_final_warehouse_without_direct_supplier_lane(chain):
    chain.inbound = {("SUP1", "HUB"): 2}
    chain.outbound = {("LOCAL", "Z1"): 4}
    assert not has_errors(validate(chain))
    for plan in (baseline(chain), solve(chain)):
        assert plan.usable and verify_plan(chain, plan) == []
        assert plan.transfers["REG", "LOCAL", "SKU-01"] == 10


def test_transfer_capacity_is_shared_across_skus(chain):
    chain.skus["SKU-02"] = Sku("SKU-02", "Second product", 1)
    chain.demand = {("Z1", "SKU-01"): 6, ("Z1", "SKU-02"): 6}
    chain.supply["SUP1", "SKU-02"] = 20
    chain.transfer_capacity["REG", "LOCAL"] = 5
    plan = solve(chain)
    assert verify_plan(chain, plan) == []
    total = sum(q for (origin, destination, _), q in plan.transfers.items()
                if (origin, destination) == ("REG", "LOCAL"))
    assert total == pytest.approx(5)
    assert cost_breakdown(chain, plan)["total"] == pytest.approx(5 * 17 + 7 * 21)
    assert verify_plan(chain, baseline(chain)) == []


def test_intermediate_capacity_counts_incoming_transfer_pallets(chain):
    chain.warehouses["REG"] = replace(chain.warehouses["REG"], capacity=5)
    plan = solve(chain)
    assert verify_plan(chain, plan) == []
    assert plan.transfers["HUB", "REG", "SKU-01"] == 5
    assert plan.inbound["SUP1", "LOCAL", "SKU-01"] == 5
    assert plan.objective == pytest.approx(215)
    assert utilisation(chain, plan)["REG"] == 1


def test_pallet_factor_applies_at_each_visited_warehouse(chain):
    chain.skus["SKU-01"] = replace(chain.skus["SKU-01"], pallet_factor=2)
    chain.warehouses["REG"] = replace(chain.warehouses["REG"], capacity=12)
    plan = solve(chain)
    assert verify_plan(chain, plan) == []
    assert plan.transfers["HUB", "REG", "SKU-01"] == 6
    assert plan.objective == pytest.approx(206)
    assert utilisation(chain, plan)["REG"] == 1


@pytest.mark.parametrize("warehouse,total", [("HUB", 220), ("REG", 260)])
def test_closure_blocks_transit_through_the_closed_warehouse(chain, warehouse, total):
    changed = apply_changes(chain, [{"type": "close_warehouse", "warehouse": warehouse}])
    plan = solve(changed)
    assert verify_plan(changed, plan) == []
    assert all(warehouse not in (origin, destination) for origin, destination, _ in plan.transfers)
    assert plan.objective == pytest.approx(total)
    assert chain.warehouses[warehouse].capacity == 20


def test_lp_allows_fractional_transfers_and_milp_requires_whole_demand(chain):
    chain.demand["Z1", "SKU-01"] = 1.5
    assert has_errors(validate(chain, "milp"))
    assert not has_errors(validate(chain, "lp"))
    plan = solve(chain, "lp")
    assert plan.objective == pytest.approx(25.5)
    assert plan.transfers["HUB", "REG", "SKU-01"] == pytest.approx(1.5)
    assert verify_plan(chain, plan) == []
    plan.mode = "milp"
    assert any("fractional" in issue for issue in verify_plan(chain, plan))


def test_sku_restriction_at_intermediate_warehouse_blocks_that_path(chain):
    chain.inbound = {("SUP1", "HUB"): 2}
    chain.outbound = {("LOCAL", "Z1"): 4}
    chain.eligible = {"HUB": {"SKU-01"}, "REG": set(), "LOCAL": {"SKU-01"}}
    assert any("no allowed lane" in issue.message for issue in validate(chain))
    assert solve(chain).status == "INFEASIBLE"


def test_transfer_file_and_capacity_column_are_optional(folder):
    (folder / "transfer_rates.csv").unlink()
    dataset, issues = load_dataset(folder)
    assert not issues and dataset.transfers == {} and dataset.transfer_capacity == {}
    (folder / "transfer_rates.csv").write_text(
        "from_warehouse_id,to_warehouse_id,cost_per_pallet,max_pallets\nHUB,REG,3,\nREG,LOCAL,2,\n")
    dataset, issues = load_dataset(folder)
    assert not issues and dataset.transfer_capacity == {}
    assert solve(dataset).objective == 170
    (folder / "transfer_rates.csv").write_text(
        "from_warehouse_id,to_warehouse_id,cost_per_pallet\nHUB,REG,3\nREG,LOCAL,2\n")
    dataset, issues = load_dataset(folder)
    assert not issues and solve(dataset).objective == 170


@pytest.mark.parametrize("text,expected", [
    ("from_warehouse_id,to_warehouse_id\nHUB,REG\n", "missing column"),
    ("from_warehouse_id,to_warehouse_id,cost_per_pallet\nHUB,REG,-1\n", "must be >= 0"),
    ("from_warehouse_id,to_warehouse_id,cost_per_pallet\nHUB,REG,nan\n", "finite"),
    ("from_warehouse_id,to_warehouse_id,cost_per_pallet,max_pallets\nHUB,REG,1,-1\n", "must be >= 0"),
    ("from_warehouse_id,to_warehouse_id,cost_per_pallet,max_pallets\nHUB,REG,1,inf\n", "finite"),
    ("from_warehouse_id,to_warehouse_id,cost_per_pallet\nHUB,REG,1\nHUB,REG,2\n", "duplicate key"),
    ("from_warehouse_id,to_warehouse_id,cost_per_pallet\nUNKNOWN,REG,1\n", "unknown origin"),
    ("from_warehouse_id,to_warehouse_id,cost_per_pallet\nHUB,UNKNOWN,1\n", "unknown destination"),
    ("from_warehouse_id,to_warehouse_id,cost_per_pallet\nHUB,HUB,1\n", "itself"),
    ("from_warehouse_id,to_warehouse_id,cost_per_pallet\nHUB,REG,0\nREG,HUB,0\n", "acyclic"),
])
def test_malformed_transfer_csv_is_reported_before_solving(folder, text, expected):
    (folder / "transfer_rates.csv").write_text(text)
    dataset, issues = load_dataset(folder)
    issues += validate(dataset)
    assert any(issue.file == "transfer_rates.csv" and expected in issue.message for issue in issues)


def test_verifier_rejects_unlisted_transfer_lane(chain):
    plan = solve(chain)
    plan.transfers["HUB", "LOCAL", "SKU-01"] = 1
    assert any("not allowed" in issue for issue in verify_plan(chain, plan))


def test_verifier_rejects_transfer_limit_and_intermediate_capacity_violations(chain):
    plan = solve(chain)
    chain.transfer_capacity["REG", "LOCAL"] = 5
    chain.warehouses["REG"] = replace(chain.warehouses["REG"], capacity=5)
    issues = verify_plan(chain, plan)
    assert any("transfer capacity exceeded" in issue for issue in issues)
    assert any("capacity exceeded at REG" in issue for issue in issues)


def test_verifier_rejects_broken_transfer_balance(chain):
    plan = solve(chain)
    del plan.transfers["HUB", "REG", "SKU-01"]
    assert any("flow imbalance" in issue for issue in verify_plan(chain, plan))


def test_verifier_rejects_a_circulation_even_when_balances_match(chain):
    plan = solve(chain)
    chain.transfers["LOCAL", "HUB"] = 0
    plan.transfers["LOCAL", "HUB", "SKU-01"] = 1
    plan.transfers["HUB", "REG", "SKU-01"] += 1
    plan.transfers["REG", "LOCAL", "SKU-01"] += 1
    assert any("cycle" in issue for issue in verify_plan(chain, plan))


@pytest.mark.parametrize("kind", ["inbound", "outbound", "transfers"])
@pytest.mark.parametrize("quantity", [float("nan"), float("inf"), -1, 0.5])
def test_verifier_rejects_invalid_quantities_on_every_flow_type(chain, kind, quantity):
    plan = solve(chain)
    flows = getattr(plan, kind)
    flows[next(iter(flows))] = quantity
    assert any("quantity" in issue for issue in verify_plan(chain, plan))


@pytest.mark.parametrize("kind,key", [
    ("inbound", ("SUP1", "HUB", "UNKNOWN")),
    ("outbound", ("LOCAL", "UNKNOWN", "SKU-01")),
    ("transfers", ("HUB", "UNKNOWN", "SKU-01")),
])
def test_verifier_reports_unknown_flow_references_without_crashing(chain, kind, key):
    plan = solve(chain)
    getattr(plan, kind)[key] = 1
    assert any("unknown" in issue for issue in verify_plan(chain, plan))


def test_verifier_checks_outbound_eligibility_and_unexpected_demand(chain):
    plan = solve(chain)
    chain.eligible = {"HUB": {"SKU-01"}, "REG": {"SKU-01"}, "LOCAL": set()}
    assert any("not allowed at LOCAL" in issue for issue in verify_plan(chain, plan))
    chain.eligible = None
    chain.zones["Z2"] = Zone("Z2", "Other zone", "LOCAL")
    chain.outbound["LOCAL", "Z2"] = 1
    plan.outbound["LOCAL", "Z2", "SKU-01"] = 1
    assert any("unexpected demand" in issue for issue in verify_plan(chain, plan))


def test_existing_golden_dataset_keeps_700_to_500_without_transfers():
    dataset, issues = load_dataset(DATA / "golden")
    assert not issues and dataset.transfers == {}
    base, optimum = baseline(dataset), solve(dataset)
    assert base.transfers == {} and optimum.transfers == {}
    assert cost_breakdown(dataset, base)["total"] == 700
    assert optimum.objective == 500
