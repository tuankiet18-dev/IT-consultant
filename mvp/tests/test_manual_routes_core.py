"""Manual complete paths reserve flow while the remaining demand is optimised."""
from copy import deepcopy
from pathlib import Path

import pytest

from nordic_flow.io import load_dataset
from nordic_flow.manual_routes import reserved_flows, validate_manual_routes, verify_manual_routes
from nordic_flow.optimiser import solve
from nordic_flow.report import cost_breakdown
from nordic_flow.schema import Zone
from nordic_flow.verify import verify_plan


@pytest.fixture
def branching():
    ds, issues = load_dataset(Path(__file__).parents[1] / "data" / "branching")
    assert issues == []
    return ds


def route(path, pallets=6, **changes):
    return {"supplier": "SUP1", "warehouses": path, "zone": "Z1", "sku": "SKU-01",
            "pallets": pallets, "reason": "Maintain preferred partner relationship", **changes}


@pytest.mark.parametrize("mode", ["milp", "lp"])
def test_manual_path_can_cost_more_than_unrestricted_optimum(branching, mode):
    assert solve(branching, mode).objective == pytest.approx(102)
    manual = [route(["B", "D"])]
    plan = solve(branching, mode, route_pins=manual)
    assert plan.status == "OPTIMAL"
    assert plan.transfers == {("B", "D", "SKU-01"): 6, ("B", "E", "SKU-01"): 6}
    assert cost_breakdown(branching, plan)["total"] == 6 * 12 + 6 * 10 == 132
    assert verify_plan(branching, plan) == []
    assert verify_manual_routes(branching, plan, manual) == []


def test_shared_supplier_quantity_can_exceed_reserved_quantity(branching):
    manual = [route(["A", "E"])]
    plan = solve(branching, route_pins=manual)
    assert plan.status == "OPTIMAL"
    assert plan.inbound == {("SUP1", "A", "SKU-01"): 12}
    assert plan.transfers == {("A", "D", "SKU-01"): 6, ("A", "E", "SKU-01"): 6}
    assert plan.objective == pytest.approx(114)
    assert verify_manual_routes(branching, plan, manual) == []


def test_manual_path_can_reserve_all_demand(branching):
    manual = [route(["C", "F"], 12)]
    plan = solve(branching, route_pins=manual)
    assert plan.objective == 168
    assert plan.inbound == {("SUP1", "C", "SKU-01"): 12}
    assert plan.transfers == {("C", "F", "SKU-01"): 12}
    assert verify_plan(branching, plan) == []


def test_shared_manual_legs_add_across_customer_paths(branching):
    branching.zones["Z2"] = Zone("Z2", "Second customer", "F")
    branching.demand = {("Z1", "SKU-01"): 6, ("Z2", "SKU-01"): 6}
    branching.outbound["E", "Z2"] = 2
    manual = [route(["B", "E"], 6), route(["B", "E"], 6, zone="Z2")]
    inbound, transfers, outbound, direct = reserved_flows(manual)
    assert direct == {}
    assert inbound == {("SUP1", "B", "SKU-01"): 12}
    assert transfers == {("B", "E", "SKU-01"): 12}
    assert outbound == {("E", "Z1", "SKU-01"): 6, ("E", "Z2", "SKU-01"): 6}
    plan = solve(branching, route_pins=manual)
    assert plan.objective == 120
    assert plan.transfers == transfers
    assert verify_plan(branching, plan) == []
    assert verify_manual_routes(branching, plan, manual) == []


def test_manual_paths_do_not_double_count_same_customer_demand(branching):
    manual = [route(["A", "D"], 6), route(["B", "E"], 7)]
    assert any("exceeding demand" in error for error in validate_manual_routes(branching, manual))
    assert solve(branching, route_pins=manual).status == "INFEASIBLE"


@pytest.mark.parametrize("manual", [
    route(["A", "D"], 7),  # D handles only six pallets.
    route(["C", "F"], 12),  # Aggregate supply is reduced below reservation in the test.
])
def test_physical_limits_can_reject_an_otherwise_declared_path(branching, manual):
    if manual["warehouses"] == ["C", "F"]:
        branching.supply["SUP1", "SKU-01"] = 11
    assert validate_manual_routes(branching, [manual]) == []
    assert solve(branching, route_pins=[manual]).status == "INFEASIBLE"


def test_zero_route_limit_prevents_reserved_flow(branching):
    branching.transfer_capacity["B", "D"] = 0
    assert solve(branching, route_pins=[route(["B", "D"], 1)]).status == "INFEASIBLE"


def test_exact_final_warehouse_pins_combine_with_path_reservations(branching):
    manual = [route(["B", "D"], 6)]
    pins = {("D", "Z1", "SKU-01"): 6}
    assert solve(branching, pins=pins, route_pins=manual).objective == pytest.approx(132)
    pins["D", "Z1", "SKU-01"] = 5
    assert solve(branching, pins=pins, route_pins=manual).status == "INFEASIBLE"


def test_fractional_reservation_only_allowed_in_lp(branching):
    manual = [route(["B", "D"], 1.5)]
    assert any("whole pallets" in error for error in validate_manual_routes(branching, manual, "milp"))
    assert solve(branching, route_pins=manual).status == "INFEASIBLE"
    plan = solve(branching, "lp", route_pins=manual)
    assert plan.status == "OPTIMAL"
    assert plan.objective == pytest.approx(109.5)
    assert plan.transfers["B", "D", "SKU-01"] == pytest.approx(1.5)
    assert verify_plan(branching, plan) == []


@pytest.mark.parametrize("manual,fragment", [
    (route([], 1), "direct lane"),
    (route(["A", "A"], 1), "more than once"),
    (route(["E", "A"], 1), "not declared"),
    (route(["A", "D"], 1, supplier="unknown"), "unknown supplier"),
    (route(["A", "D"], 1, sku="unknown"), "unknown sku"),
    (route(["A", "D"], 1, zone="unknown"), "unknown zone"),
    (route(["unknown"], 1), "unknown warehouse"),
    (route(["A", "D"], 0), "positive"),
    (route(["A", "D"], float("nan")), "finite"),
    (route(["A", "D"], float("inf")), "finite"),
    (route(["A", "D"], True), "positive"),
    (route(["A", "D"], 1, reason=" "), "reason"),
])
def test_bad_manual_paths_are_rejected_without_adding_routes(branching, manual, fragment):
    before = deepcopy(branching)
    assert any(fragment in error for error in validate_manual_routes(branching, [manual]))
    assert solve(branching, route_pins=[manual]).status == "INFEASIBLE"
    assert branching == before


def test_warehouse_product_eligibility_applies_along_manual_path(branching):
    branching.eligible = {warehouse: {"SKU-01"} for warehouse in branching.warehouses}
    branching.eligible["D"] = set()
    manual = [route(["B", "D"], 1)]
    assert any("not eligible" in error for error in validate_manual_routes(branching, manual))
    assert solve(branching, route_pins=manual).status == "INFEASIBLE"


def test_nonstandard_warehouse_order_works_when_declared_without_cycle(branching):
    # Warehouse letters have no built-in stage. Reorient the graph to E -> A.
    branching.inbound = {("SUP1", "E"): 2}
    branching.transfers = {("E", "A"): 3}
    branching.transfer_capacity = {("E", "A"): 12}
    branching.outbound = {("A", "Z1"): 4}
    manual = [route(["E", "A"], 12)]
    assert validate_manual_routes(branching, manual) == []
    plan = solve(branching, route_pins=manual)
    assert plan.status == "OPTIMAL"
    assert plan.objective == 12 * (2 + 3 + 4 + 4) == 156
    assert plan.transfers == {("E", "A", "SKU-01"): 12}
    assert verify_plan(branching, plan) == []


def test_one_warehouse_manual_path_does_not_need_transfer_lane(branching):
    branching.inbound["SUP1", "E"] = 20
    manual = [route(["E"], 12)]
    plan = solve(branching, route_pins=manual)
    assert plan.transfers == {}
    assert plan.objective == 12 * (20 + 2 + 2)


def test_manual_path_can_include_three_sequential_warehouses():
    ds, issues = load_dataset(Path(__file__).parents[1] / "data" / "transshipment")
    assert issues == []
    manual = [route(["HUB", "REG", "LOCAL"], 10)]
    plan = solve(ds, route_pins=manual)
    assert plan.status == "OPTIMAL" and plan.objective == 170
    assert plan.transfers == {("HUB", "REG", "SKU-01"): 10, ("REG", "LOCAL", "SKU-01"): 10}
    assert verify_plan(ds, plan) == []
    assert verify_manual_routes(ds, plan, manual) == []


def test_independent_manual_check_detects_omitted_reservation(branching):
    plan = solve(branching)
    assert verify_plan(branching, plan) == []
    assert any("requirement not met" in error for error in verify_manual_routes(branching, plan, [route(["B", "D"], 6)]))
