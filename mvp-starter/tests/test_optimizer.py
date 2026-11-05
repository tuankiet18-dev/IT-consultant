"""Behavior checks for the Nordic Flow allocation solver."""

import unittest
from dataclasses import replace
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np

from nordic_flow.csv_io import load_problem
from nordic_flow.models import Status
from nordic_flow.optimizer import optimize


FIXTURE = Path(__file__).resolve().parents[1] / "examples" / "warehouse_split" / "input"
FACTORY = "FACTORY_01"
CUSTOMER = "CUSTOMER_01"
SKU = "SKU_01"


class OptimizeTests(unittest.TestCase):
    def setUp(self):
        self.problem = load_problem(FIXTURE)

    def assert_infeasible(self, result):
        self.assertEqual(result.status, Status.INFEASIBLE)
        self.assertEqual(result.inbound, {})
        self.assertEqual(result.outbound, {})
        self.assertIsNone(result.total_cost)

    def test_fixture_splits_60_and_40_for_cost_920(self):
        result = optimize(self.problem)

        self.assertEqual(result.status, Status.OPTIMAL)
        self.assertEqual(result.inbound, {(FACTORY, "WH_A", SKU): 60, (FACTORY, "WH_B", SKU): 40})
        self.assertEqual(result.outbound, {("WH_A", CUSTOMER, SKU): 60, ("WH_B", CUSTOMER, SKU): 40})
        for pallets in [*result.inbound.values(), *result.outbound.values()]:
            self.assertIs(type(pallets), int)
        self.assertIsInstance(result.total_cost, Decimal)
        self.assertEqual(result.total_cost, Decimal("920"))

    def test_combined_warehouse_capacity_below_demand(self):
        warehouses = dict(self.problem.warehouses)
        warehouses["WH_B"] = replace(warehouses["WH_B"], capacity_pallets=30)

        self.assert_infeasible(optimize(replace(self.problem, warehouses=warehouses)))

    def test_capacity_is_shared_between_skus(self):
        # Each SKU alone fits in WH_A (50 <= 60); together, at least 40 must go via WH_B.
        problem = replace(
            self.problem,
            supply={(FACTORY, SKU): 50, (FACTORY, "SKU_02"): 50},
            demand={(CUSTOMER, SKU): 50, (CUSTOMER, "SKU_02"): 50},
        )
        result = optimize(problem)

        self.assertEqual(result.status, Status.OPTIMAL)
        self.assertEqual(result.total_cost, Decimal("920"))
        warehouse_load = {
            wh: sum(qty for (_, warehouse, _), qty in result.inbound.items() if warehouse == wh)
            for wh in problem.warehouses
        }
        self.assertEqual(warehouse_load, {"WH_A": 60, "WH_B": 40})
        for (_, sku), demand in problem.demand.items():
            delivered = sum(qty for (_, _, item), qty in result.outbound.items() if item == sku)
            self.assertEqual(delivered, demand)

    def test_zero_rate_is_available_but_an_absent_lane_is_not(self):
        rates = {("WH_A", CUSTOMER): Decimal("0")}
        problem = replace(self.problem, outbound_rates=rates)
        self.assert_infeasible(optimize(problem))

        # WH_B's reintroduced lane restores feasibility; the free WH_A lane is used first.
        restored = replace(problem, outbound_rates={**rates, ("WH_B", CUSTOMER): Decimal("4")})
        result = optimize(restored)
        self.assertEqual(result.status, Status.OPTIMAL)
        self.assertEqual(result.outbound, {("WH_A", CUSTOMER, SKU): 60, ("WH_B", CUSTOMER, SKU): 40})
        self.assertEqual(result.total_cost, Decimal("740"))

    def test_cannot_deliver_pallets_under_a_different_sku(self):
        problem = replace(self.problem, supply={(FACTORY, "SKU_02"): 100})

        self.assert_infeasible(optimize(problem))

    def test_zero_demand_does_not_ship_unused_supply(self):
        problem = replace(self.problem, demand={(CUSTOMER, SKU): 0})
        result = optimize(problem)

        self.assertEqual(result.status, Status.OPTIMAL)
        self.assertEqual(result.inbound, {})
        self.assertEqual(result.outbound, {})
        self.assertEqual(result.total_cost, Decimal("0"))

    def test_time_limit_without_candidate_is_not_infeasible(self):
        stopped = SimpleNamespace(status=1, x=None, message="Time limit reached")
        with patch("nordic_flow.optimizer.milp", return_value=stopped):
            result = optimize(self.problem, time_limit_seconds=1)

        self.assertEqual(result.status, Status.ERROR)
        self.assertIsNone(result.total_cost)
        self.assertIn("Time limit", result.message)

    def test_time_limit_with_valid_candidate_is_only_feasible(self):
        # This plan sends everything via the more expensive warehouse.
        stopped = SimpleNamespace(status=1, x=np.array([0, 100, 0, 100]), message="Time limit reached")
        with patch("nordic_flow.optimizer.milp", return_value=stopped):
            result = optimize(self.problem, time_limit_seconds=1)

        self.assertEqual(result.status, Status.FEASIBLE)
        self.assertEqual(result.total_cost, Decimal("1100"))
