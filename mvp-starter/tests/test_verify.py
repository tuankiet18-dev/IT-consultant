"""Verify plans independently from optimizer output and implementation."""

import unittest
from dataclasses import replace
from decimal import Decimal
from pathlib import Path

from nordic_flow.csv_io import load_problem
from nordic_flow.models import AllocationResult, Status
from nordic_flow.verify import verify_plan


INPUT = Path(__file__).resolve().parents[1] / "examples" / "warehouse_split" / "input"
SOURCE = "FACTORY_01"
DESTINATION = "CUSTOMER_01"
SKU = "SKU_01"


class VerifyPlanTests(unittest.TestCase):
    def setUp(self):
        self.problem = load_problem(INPUT)
        self.plan = AllocationResult(
            status=Status.OPTIMAL,
            inbound={(SOURCE, "WH_A", SKU): 60, (SOURCE, "WH_B", SKU): 40},
            outbound={("WH_A", DESTINATION, SKU): 60, ("WH_B", DESTINATION, SKU): 40},
            total_cost=Decimal("920"),
        )

    def assert_rejects(self, code, plan, problem=None):
        report = verify_plan(self.problem if problem is None else problem, plan)
        self.assertFalse(report.ok)
        self.assertIn(code, {issue.code for issue in report.issues})

    def test_fixture_plan_has_correct_independent_cost_breakdown(self):
        report = verify_plan(self.problem, self.plan)

        self.assertTrue(report.ok, report.issues)
        self.assertEqual(report.issues, ())
        self.assertIsNotNone(report.costs)
        self.assertEqual(report.costs.inbound_cost, Decimal("380"))
        self.assertEqual(report.costs.handling_cost, Decimal("200"))
        self.assertEqual(report.costs.outbound_cost, Decimal("340"))
        self.assertEqual(report.costs.total_cost, Decimal("920"))

    def test_one_warehouse_limit_is_shared_by_multiple_skus(self):
        sku2 = "SKU_02"
        problem = replace(
            self.problem,
            supply={(SOURCE, SKU): 40, (SOURCE, sku2): 40},
            demand={(DESTINATION, SKU): 40, (DESTINATION, sku2): 40},
        )
        plan = replace(
            self.plan,
            inbound={(SOURCE, "WH_A", SKU): 40, (SOURCE, "WH_A", sku2): 40},
            outbound={("WH_A", DESTINATION, SKU): 40, ("WH_A", DESTINATION, sku2): 40},
            total_cost=Decimal("640"),
        )

        self.assert_rejects("capacity", plan, problem)

    def test_supply_ceiling_applies_across_both_warehouses(self):
        problem = replace(self.problem, supply={(SOURCE, SKU): 80})

        self.assert_rejects("supply", self.plan, problem)

    def test_demand_must_be_exact_even_when_flows_balance(self):
        for required in (99, 101):
            with self.subTest(required=required):
                problem = replace(self.problem, demand={(DESTINATION, SKU): required})
                self.assert_rejects("demand", self.plan, problem)

    def test_warehouse_cannot_swap_skus_even_if_total_pallets_balance(self):
        sku2 = "SKU_02"
        problem = replace(
            self.problem,
            supply={(SOURCE, SKU): 50, (SOURCE, sku2): 50},
            demand={(DESTINATION, SKU): 50, (DESTINATION, sku2): 50},
        )
        plan = replace(
            self.plan,
            inbound={(SOURCE, "WH_A", SKU): 50, (SOURCE, "WH_B", sku2): 50},
            outbound={("WH_A", DESTINATION, sku2): 50, ("WH_B", DESTINATION, SKU): 50},
            total_cost=Decimal("950"),
        )

        self.assert_rejects("balance", plan, problem)

    def test_absent_lane_is_rejected_but_free_lane_is_valid(self):
        problem = replace(self.problem, outbound_rates={("WH_B", DESTINATION): Decimal("4")})
        self.assert_rejects("lane", self.plan, problem)

        rates = {**problem.outbound_rates, ("WH_A", DESTINATION): Decimal("0")}
        report = verify_plan(
            replace(problem, outbound_rates=rates),
            replace(self.plan, status=Status.FEASIBLE, total_cost=Decimal("740")),
        )
        self.assertTrue(report.ok, report.issues)
        self.assertEqual(report.costs.outbound_cost, Decimal("160"))
        self.assertEqual(report.costs.total_cost, Decimal("740"))

    def test_malformed_flow_key_is_rejected_without_crashing(self):
        self.assert_rejects("flow_key", replace(self.plan, inbound={(SOURCE, "WH_A"): 60}))

    def test_non_integer_or_negative_quantities_are_rejected(self):
        for invalid in (True, 60.0, Decimal("60.5"), -60):
            with self.subTest(invalid=invalid):
                plan = replace(self.plan, inbound={**self.plan.inbound, (SOURCE, "WH_A", SKU): invalid})
                self.assert_rejects("quantity", plan)

    def test_reported_cost_must_match_recomputed_cost(self):
        for invalid in (None, Decimal("919"), Decimal("NaN"), Decimal("sNaN")):
            with self.subTest(invalid=invalid):
                self.assert_rejects("cost", replace(self.plan, total_cost=invalid))

    def test_non_plan_statuses_are_not_certified(self):
        for status in (Status.INFEASIBLE, Status.ERROR):
            with self.subTest(status=status):
                self.assert_rejects("status", AllocationResult(status=status))
