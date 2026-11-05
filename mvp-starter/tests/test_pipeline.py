"""Exercise the CSV-to-verified-plan pipeline and its export boundary."""

import csv
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

from nordic_flow import csv_io
from nordic_flow.csv_io import load_problem, write_result
from nordic_flow.models import AllocationResult, Status
from nordic_flow.service import run_allocation


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "warehouse_split"
OUTPUT_NAMES = {"inbound_plan.csv", "outbound_plan.csv", "summary.csv"}


def _read_csv(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.reader(handle))


class PipelineTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.input_dir = self.root / "input"
        self.output_dir = self.root / "output"
        shutil.copytree(EXAMPLE / "input", self.input_dir)

    def _make_infeasible(self):
        (self.input_dir / "warehouses.csv").write_text(
            "warehouse_id,capacity_pallets,handling_cost_per_pallet\nWH_A,60,2\nWH_B,30,2\n",
            encoding="utf-8",
        )

    def test_writes_only_the_three_expected_csvs(self):
        result = run_allocation(self.input_dir, output_dir=self.output_dir)

        self.assertEqual(result.status, Status.OPTIMAL)
        self.assertEqual(result.total_cost, Decimal("920"))
        self.assertEqual({path.name for path in self.output_dir.iterdir()}, OUTPUT_NAMES)
        for name in OUTPUT_NAMES:
            with self.subTest(name=name):
                self.assertEqual(
                    _read_csv(self.output_dir / name), _read_csv(EXAMPLE / "expected" / name)
                )

    def test_can_return_a_verified_plan_without_exporting(self):
        result = run_allocation(self.input_dir)

        self.assertEqual(result.status, Status.OPTIMAL)
        self.assertEqual(result.total_cost, Decimal("920"))
        self.assertEqual(set(self.root.iterdir()), {self.input_dir})

    def test_infeasible_problem_does_not_create_output(self):
        self._make_infeasible()

        result = run_allocation(self.input_dir, output_dir=self.output_dir)

        self.assertEqual(result.status, Status.INFEASIBLE)
        self.assertFalse(self.output_dir.exists())

    def test_invalid_input_reports_error_without_creating_output(self):
        (self.input_dir / "demand.csv").unlink()

        result = run_allocation(self.input_dir, output_dir=self.output_dir)

        self.assertEqual(result.status, Status.ERROR)
        self.assertIn("demand.csv", result.message)
        self.assertFalse(self.output_dir.exists())

    def test_existing_output_is_not_changed(self):
        self.output_dir.mkdir()
        previous = self.output_dir / "summary.csv"
        previous.write_bytes(b"previous run\n")

        result = run_allocation(self.input_dir, output_dir=self.output_dir)

        self.assertEqual(result.status, Status.ERROR)
        self.assertEqual(previous.read_bytes(), b"previous run\n")
        self.assertEqual(list(self.output_dir.iterdir()), [previous])

    def test_falsely_optimal_solver_plan_is_rejected_before_export(self):
        false_plan = AllocationResult(status=Status.OPTIMAL, total_cost=Decimal("0"))
        with patch("nordic_flow.service.optimize", return_value=false_plan):
            result = run_allocation(self.input_dir, output_dir=self.output_dir)

        self.assertEqual(result.status, Status.ERROR)
        self.assertFalse(result.inbound)
        self.assertFalse(result.outbound)
        self.assertFalse(self.output_dir.exists())

    def test_direct_export_also_rejects_an_unverified_plan(self):
        problem = load_problem(self.input_dir)
        false_plan = AllocationResult(status=Status.OPTIMAL, total_cost=Decimal("0"))

        with self.assertRaises(ValueError):
            write_result(problem, false_plan, self.output_dir)

        self.assertFalse(self.output_dir.exists())

    def test_export_failure_cleans_up_files_already_written(self):
        write_table = csv_io._write_table

        def fail_on_second_table(path, header, rows, created):
            if path.name == "outbound_plan.csv":
                raise PermissionError("simulated write failure")
            write_table(path, header, rows, created)

        with patch("nordic_flow.csv_io._write_table", side_effect=fail_on_second_table):
            result = run_allocation(self.input_dir, output_dir=self.output_dir)

        self.assertEqual(result.status, Status.ERROR)
        self.assertIn("simulated write failure", result.message)
        self.assertFalse(self.output_dir.exists())

    def _run_cli(self):
        return subprocess.run(
            [
                sys.executable,
                "-m",
                "nordic_flow.cli",
                str(self.input_dir),
                str(self.output_dir),
                "--time-limit",
                "10",
            ],
            cwd=ROOT,
            env={**os.environ, "PYTHONPATH": str(ROOT / "src")},
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
        )

    def test_cli_exits_zero_for_an_exported_plan(self):
        completed = self._run_cli()

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertTrue((self.output_dir / "summary.csv").is_file())

    def test_cli_exits_two_for_an_infeasible_problem(self):
        self._make_infeasible()

        completed = self._run_cli()

        self.assertEqual(completed.returncode, 2, completed.stderr)
        self.assertFalse(self.output_dir.exists())
