import re
import shutil
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from nordic_flow.csv_io import load_problem
from nordic_flow.models import InputDataError


FIXTURE = (
    Path(__file__).resolve().parents[1] / "examples" / "warehouse_split" / "input"
)


class LoadProblemTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.input_dir = Path(self.temp.name) / "input"
        shutil.copytree(FIXTURE, self.input_dir)

    def change(self, filename, old, new):
        path = self.input_dir / filename
        original = (FIXTURE / filename).read_text(encoding="utf-8")
        self.assertIn(old, original)
        path.write_text(original.replace(old, new, 1), encoding="utf-8")

    def assert_invalid(self, filename, row=None):
        location = re.escape(filename)
        if row is not None:
            location += f":{row}:"
        with self.assertRaisesRegex(InputDataError, location):
            load_problem(self.input_dir)

    def test_loads_golden_as_typed_problem(self):
        problem = load_problem(self.input_dir)

        available = problem.supply["FACTORY_01", "SKU_01"]
        required = problem.demand["CUSTOMER_01", "SKU_01"]
        self.assertIs(type(available), int)
        self.assertIs(type(required), int)
        self.assertEqual((available, required), (100, 100))

        warehouse = problem.warehouses["WH_A"]
        self.assertIs(type(warehouse.capacity_pallets), int)
        self.assertEqual(warehouse.capacity_pallets, 60)
        self.assertIsInstance(warehouse.handling_cost_per_pallet, Decimal)
        self.assertEqual(warehouse.handling_cost_per_pallet, Decimal("2"))
        self.assertIsInstance(problem.inbound_rates["FACTORY_01", "WH_B"], Decimal)
        self.assertEqual(problem.inbound_rates["FACTORY_01", "WH_B"], Decimal("5"))
        self.assertEqual(problem.outbound_rates["WH_B", "CUSTOMER_01"], Decimal("4"))

    def test_free_route_is_present_but_omitted_route_is_absent(self):
        self.change(
            "inbound_rates.csv",
            "FACTORY_01,WH_A,3\nFACTORY_01,WH_B,5",
            "FACTORY_01,WH_A,0",
        )

        rates = load_problem(self.input_dir).inbound_rates

        self.assertEqual(rates["FACTORY_01", "WH_A"], Decimal("0"))
        self.assertNotIn(("FACTORY_01", "WH_B"), rates)

    def test_unknown_warehouse_reports_route_location(self):
        self.change("inbound_rates.csv", "FACTORY_01,WH_B,5", "FACTORY_01,UNKNOWN,5")
        self.assert_invalid("inbound_rates.csv", row=3)

    def test_unknown_destination_reports_route_location(self):
        self.change("outbound_rates.csv", "WH_A,CUSTOMER_01,3", "WH_A,UNKNOWN,3")
        self.assert_invalid("outbound_rates.csv", row=2)

    def test_duplicate_key_reports_duplicate_row(self):
        self.change(
            "supply.csv",
            "FACTORY_01,SKU_01,100",
            "FACTORY_01,SKU_01,100\nFACTORY_01,SKU_01,1",
        )
        self.assert_invalid("supply.csv", row=3)

    def test_invalid_pallet_counts_are_rejected(self):
        for count in ("-1", "1.5", "abc", ""):
            with self.subTest(count=count):
                self.change("supply.csv", "SKU_01,100", f"SKU_01,{count}")
                self.assert_invalid("supply.csv", row=2)

    def test_nonfinite_negative_and_malformed_rates_are_rejected(self):
        for rate in ("NaN", "Infinity", "-1", "x"):
            with self.subTest(rate=rate):
                self.change("inbound_rates.csv", "WH_A,3", f"WH_A,{rate}")
                self.assert_invalid("inbound_rates.csv", row=2)

    def test_wrong_header_is_rejected(self):
        self.change("demand.csv", "required_pallets", "required_cartons")
        self.assert_invalid("demand.csv")

    def test_missing_required_file_is_reported(self):
        (self.input_dir / "outbound_rates.csv").unlink()
        self.assert_invalid("outbound_rates.csv")
