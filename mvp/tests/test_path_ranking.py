"""Complete-path ranking uses all costs and keeps graph/flow semantics explicit."""
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from api.main import create_app
from nordic_flow.io import load_dataset
from nordic_flow.optimiser import solve
from nordic_flow.path_ranking import rank_paths
from nordic_flow.report import cost_breakdown
from nordic_flow.schema import Dataset, Plan, Sku, Supplier, Warehouse, Zone

DATA = Path(__file__).parents[1] / "data"


def branching(mode="milp"):
    ds, _ = load_dataset(DATA / "branching")
    return ds, solve(ds, mode)


def by_path(result):
    return {tuple(row["warehouses"]): row for row in result["paths"]}


def test_all_nine_paths_ranked_by_whole_path_cost_and_accounted_plan():
    ds, plan = branching()
    result = rank_paths(ds, plan, "Z1", "SKU-01", 12)
    assert result["total_paths"] == 9 and result["truncated"] is False
    assert [row["cost_per_pallet"] for row in result["paths"]] == [7, 10, 12, 12, 14, 15, 15, 15, 16]
    paths = by_path(result)
    ad, be = paths["A", "D"], paths["B", "E"]
    assert (ad["freight_per_pallet"], ad["handling_per_pallet"], ad["quoted_total"]) == (3, 4, 84)
    assert (ad["max_pallets"], ad["can_carry_quantity"], ad["plan_pallets"], ad["plan_cost"]) == (6, False, 6, 42)
    assert ad["bottlenecks"] == ["Warehouse D capacity"]
    assert (be["cost_per_pallet"], be["quoted_total"], be["max_pallets"], be["can_carry_quantity"], be["plan_cost"]) == (10, 120, 12, True, 60)
    assert sum(row["plan_pallets"] for row in result["paths"]) == 12
    assert sum(row["plan_cost"] for row in result["paths"]) == 102
    assert result["plan_accounting"]["delivered_pallets"] == 12
    assert result["plan_accounting"]["total_cost"] == 102
    assert "not physical" in result["plan_accounting"]["note"]


def test_k_best_are_global_cheapest_not_first_discovered():
    ds, plan = branching()
    result = rank_paths(ds, plan, "Z1", "SKU-01", 6, limit=2)
    assert [row["warehouses"] for row in result["paths"]] == [["A", "D"], ["B", "E"]]
    assert result["truncated"] is True and result["total_paths"] == 9
    assert all(row["can_carry_quantity"] for row in result["paths"])


@pytest.mark.parametrize("mode,quantity,maximum", [("milp", 3, 2), ("lp", 2.5, 2.5)])
def test_standalone_limits_use_factor_and_whole_pallet_rounding(mode, quantity, maximum):
    ds, _ = branching()
    ds.skus["SKU-01"] = Sku("SKU-01", "Example product", 2)
    ds.transfer_capacity["A", "D"] = 2.5
    plan = solve(ds, mode)
    ad = by_path(rank_paths(ds, plan, "Z1", "SKU-01", quantity))["A", "D"]
    assert ad["max_pallets"] == maximum
    assert ad["can_carry_quantity"] is (mode == "lp")
    assert "Warehouse A → Warehouse D route limit" in ad["bottlenecks"]


def test_zero_limit_and_warehouse_eligibility_exclude_path_options():
    ds, _ = branching()
    ds.transfer_capacity["A", "D"] = 0
    ds.eligible = {warehouse: {"SKU-01"} for warehouse in ds.warehouses}
    ds.eligible["C"] = set()
    result = rank_paths(ds, solve(ds), "Z1", "SKU-01")
    assert result["total_paths"] == 5
    assert ("A", "D") not in by_path(result)
    assert not any("C" in row["warehouses"] for row in result["paths"])


def test_manual_paths_are_reserved_before_accounting_shared_aggregate_flows():
    ds = Dataset(
        suppliers={s: Supplier(s, s) for s in ("S1", "S2")},
        warehouses={"H": Warehouse("H", "Hub", 10, 1, 1)},
        zones={z: Zone(z, z, "H") for z in ("Z1", "Z2")},
        skus={"P": Sku("P", "Product")},
        inbound={("S1", "H"): 1, ("S2", "H"): 3},
        outbound={("H", "Z1"): 2, ("H", "Z2"): 4},
        supply={("S1", "P"): 5, ("S2", "P"): 5},
        demand={("Z1", "P"): 5, ("Z2", "P"): 5},
    )
    plan = Plan("OPTIMAL", "milp", inbound={("S1", "H", "P"): 5, ("S2", "H", "P"): 5},
                outbound={("H", "Z1", "P"): 5, ("H", "Z2", "P"): 5})
    manual = [{"supplier": "S2", "warehouses": ["H"], "zone": "Z1", "sku": "P", "pallets": 3, "reason": "Partner allocation"}]
    one = rank_paths(ds, plan, "Z1", "P", manual_routes=manual)
    two = rank_paths(ds, plan, "Z2", "P", manual_routes=manual)
    assert {row["supplier"]: row["plan_pallets"] for row in one["paths"]} == {"S1": 2, "S2": 3}
    assert one["plan_accounting"]["total_cost"] == 31
    assert two["plan_accounting"]["total_cost"] == 39
    assert one["plan_accounting"]["total_cost"] + two["plan_accounting"]["total_cost"] == cost_breakdown(ds, plan)["total"]


def test_exponential_path_count_keeps_only_global_k_suffixes():
    ds = Dataset(suppliers={"S": Supplier("S", "S")}, zones={"Z": Zone("Z", "Z", "L59a")},
                 skus={"P": Sku("P", "P")}, supply={("S", "P"): 1}, demand={("Z", "P"): 1})
    for level in range(60):
        for name in "ab":
            current = f"L{level}{name}"
            ds.warehouses[current] = Warehouse(current, current, 1, 0, 0)
            if level == 0:
                ds.inbound["S", current] = 0
            if level == 59:
                ds.outbound[current, "Z"] = 0
            else:
                for following in "ab":
                    ds.transfers[current, f"L{level + 1}{following}"] = 0
    # An empty accounting plan is enough to exercise path enumeration, not solving.
    result = rank_paths(ds, Plan("OPTIMAL", "milp"), "Z", "P", limit=3)
    assert len(result["paths"]) == 3
    assert result["total_paths"] is None and result["truncated"] is True
    assert all(row["cost_per_pallet"] == 0 for row in result["paths"])


@pytest.mark.parametrize("zone,sku,quantity,limit", [
    ("missing", "SKU-01", 1, 50), ("Z1", "missing", 1, 50),
    ("Z1", "SKU-01", 0, 50), ("Z1", "SKU-01", float("nan"), 50),
    ("Z1", "SKU-01", float("inf"), 50), ("Z1", "SKU-01", 1.5, 50),
    ("Z1", "SKU-01", 1, 0), ("Z1", "SKU-01", 1, 101),
])
def test_invalid_comparison_inputs_are_rejected(zone, sku, quantity, limit):
    ds, plan = branching()
    with pytest.raises(ValueError):
        rank_paths(ds, plan, zone, sku, quantity, limit)


def test_broken_aggregate_flows_are_not_misrepresented_as_used_complete_paths():
    ds, plan = branching()
    plan.inbound["SUP1", "A", "SKU-01"] = 2
    with pytest.raises(ValueError, match="unmatched"):
        rank_paths(ds, plan, "Z1", "SKU-01")


def test_api_uses_effective_run_rates_closures_and_manual_routes(tmp_path):
    client = TestClient(create_app(tmp_path / "ranking.db"))
    scenario = client.post("/api/scenarios/sample", json={"name": "branching"}).json()
    original = client.post(f"/api/scenarios/{scenario['id']}/runs", json={}).json()
    query = "?zone=Z1&sku=SKU-01&quantity=12"
    original_paths = client.get(f"/api/runs/{original['id']}/paths{query}").json()
    assert original_paths["run_id"] == original["id"] and original_paths["total_paths"] == 9
    assert original_paths["paths"][0]["cost_per_pallet"] == 7
    changed = client.post(f"/api/scenarios/{scenario['id']}/whatif", json={"changes": [
        {"type": "set_rate", "kind": "inbound", "from": "SUP1", "to": "A", "cost": 9},
        {"type": "close_warehouse", "warehouse": "D"},
    ]}).json()
    ranked = client.get(f"/api/runs/{changed['id']}/paths{query}").json()
    assert ranked["total_paths"] == 6 and ranked["paths"][0]["warehouses"] == ["B", "E"]
    assert not any("D" in row["warehouses"] for row in ranked["paths"])
    assert client.get(f"/api/runs/{original['id']}/paths{query}").json() == original_paths
    child = client.post(f"/api/runs/{original['id']}/routes", json={
        "supplier": "SUP1", "warehouses": ["B", "D"], "zone": "Z1", "sku": "SKU-01", "pallets": 6, "reason": "Partner allocation",
    }).json()
    child_paths = client.get(f"/api/runs/{child['id']}/paths{query}").json()
    assert by_path(child_paths)["B", "D"]["plan_pallets"] == 6
    assert by_path(child_paths)["A", "D"]["plan_pallets"] == 0
    assert child_paths["plan_accounting"]["total_cost"] == 132
    assert client.get(f"/api/runs/{child['id']}/paths?zone=Z1&sku=SKU-01&quantity=1.5").status_code == 422
    assert client.get(f"/api/runs/{child['id']}/paths?zone=Z1&sku=SKU-01&limit=101").status_code == 422


def test_reordered_warehouse_path_retains_its_real_order():
    ds, _ = load_dataset(DATA / "reordered")
    result = rank_paths(ds, solve(ds), "Z1", "SKU-01", 12)
    assert result["total_paths"] == 1
    assert result["paths"][0]["warehouses"] == ["E", "A"]
    assert result["paths"][0]["cost_per_pallet"] == 13
    assert result["paths"][0]["quoted_total"] == 156
