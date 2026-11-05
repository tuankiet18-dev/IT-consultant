"""Show how an integrator calls the installed core for two planning scenarios."""

import csv
import json
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory

from nordic_flow.models import AllocationResult, Status
from nordic_flow.service import run_allocation


FIXTURE = Path(__file__).resolve().parent / "warehouse_split" / "input"


def to_payload(result: AllocationResult) -> dict:
    """Example UI adapter: tuple-keyed maps become rows; decimals become strings."""
    return {
        "status": result.status.value,
        "message": result.message,
        "total_cost": format(result.total_cost, "f") if result.total_cost is not None else None,
        "inbound": [
            {"source_id": source, "warehouse_id": warehouse, "sku_id": sku, "pallets": pallets}
            for (source, warehouse, sku), pallets in sorted(result.inbound.items())
        ],
        "outbound": [
            {"warehouse_id": warehouse, "destination_id": destination, "sku_id": sku, "pallets": pallets}
            for (warehouse, destination, sku), pallets in sorted(result.outbound.items())
        ],
    }


def main() -> None:
    """Verify one successful run and one infeasible run without modifying the fixture."""
    with TemporaryDirectory(prefix="nordic-flow-") as temp:
        root = Path(temp)
        output = root / "verified"
        result = run_allocation(FIXTURE, output_dir=output, time_limit_seconds=10)
        if result.status != Status.OPTIMAL or result.total_cost != 920:
            raise RuntimeError(f"expected OPTIMAL at cost 920, got {result!r}")
        if {path.name for path in output.iterdir()} != {
            "inbound_plan.csv", "outbound_plan.csv", "summary.csv"
        }:
            raise RuntimeError("expected the three verified CSVs")

        reduced_input = root / "reduced_capacity"
        shutil.copytree(FIXTURE, reduced_input)
        warehouse_csv = reduced_input / "warehouses.csv"
        with warehouse_csv.open(encoding="utf-8", newline="") as stream:
            rows = list(csv.reader(stream))
        for row in rows[1:]:
            if row[0] == "WH_B":
                row[1] = "30"
        with warehouse_csv.open("w", encoding="utf-8", newline="") as stream:
            csv.writer(stream).writerows(rows)

        rejected_output = root / "rejected"
        rejected = run_allocation(reduced_input, output_dir=rejected_output, time_limit_seconds=10)
        if rejected.status != Status.INFEASIBLE or rejected_output.exists():
            raise RuntimeError(f"expected INFEASIBLE without CSV export, got {rejected!r}")

        print(json.dumps(
            {"warehouse_split": to_payload(result), "reduced_capacity": to_payload(rejected)},
            indent=2,
        ))


if __name__ == "__main__":
    main()
