"""Read inputs and export verified plans in the Nordic Flow v0.1 contract."""

import csv
from collections.abc import Iterable
from pathlib import Path

from .models import AllocationResult, CsvRow, InputDataError, Problem
from .validation import validate_problem
from .verify import require_verified_costs

_HEADERS = {
    "supply.csv": ("source_id", "sku_id", "available_pallets"),
    "warehouses.csv": ("warehouse_id", "capacity_pallets", "handling_cost_per_pallet"),
    "demand.csv": ("destination_id", "sku_id", "required_pallets"),
    "inbound_rates.csv": ("source_id", "warehouse_id", "transport_cost_per_pallet"),
    "outbound_rates.csv": ("warehouse_id", "destination_id", "transport_cost_per_pallet"),
}


def _read_rows(path: Path, header: tuple[str, ...]) -> list[CsvRow]:
    """Check CSV structure, preserving the physical start line of each record."""
    rows = []
    line = 1
    try:
        with path.open(encoding="utf-8-sig", newline="") as stream:
            reader = csv.reader(stream, strict=True)
            if tuple(next(reader, ())) != header:
                raise InputDataError(path.name, f"expected header {','.join(header)}", line)
            while True:
                line = reader.line_num + 1
                values = next(reader, None)
                if values is None:
                    break
                if len(values) != len(header):
                    raise InputDataError(
                        path.name,
                        f"expected {len(header)} columns, found {len(values)}",
                        line,
                    )
                rows.append(CsvRow(path.name, line, dict(zip(header, values))))
    except UnicodeDecodeError as exc:
        raise InputDataError(path.name, "expected a UTF-8 CSV") from exc
    except csv.Error as exc:
        raise InputDataError(path.name, f"invalid CSV: {exc}", line) from exc
    except FileNotFoundError as exc:
        raise InputDataError(path.name, "required file is missing") from exc
    except OSError as exc:
        raise InputDataError(path.name, f"could not read CSV: {exc.strerror}") from exc
    return rows


def load_problem(input_dir: str | Path) -> Problem:
    """Load the five required files and return a validated planning problem."""
    folder = Path(input_dir)
    tables = {name: _read_rows(folder / name, header) for name, header in _HEADERS.items()}
    return validate_problem(
        supply_rows=tables["supply.csv"],
        warehouse_rows=tables["warehouses.csv"],
        demand_rows=tables["demand.csv"],
        inbound_rows=tables["inbound_rates.csv"],
        outbound_rows=tables["outbound_rates.csv"],
    )


def write_result(problem: Problem, result: AllocationResult, output_dir: str | Path) -> Path:
    """Verify and write three CSVs to a new directory; never overwrite a prior run."""
    costs = require_verified_costs(problem, result)
    folder = Path(output_dir)
    inbound = (
        (
            source, wh, sku, quantity,
            format(problem.inbound_rates[source, wh] * quantity, "f"),
            format(problem.warehouses[wh].handling_cost_per_pallet * quantity, "f"),
        )
        for (source, wh, sku), quantity in sorted(result.inbound.items())
        if quantity > 0
    )
    outbound = (
        (wh, destination, sku, quantity, format(problem.outbound_rates[wh, destination] * quantity, "f"))
        for (wh, destination, sku), quantity in sorted(result.outbound.items())
        if quantity > 0
    )
    summary = (
        result.status.value,
        sum(problem.demand.values()),
        sum(result.outbound.values()),
        format(costs.inbound_cost, "f"),
        format(costs.handling_cost, "f"),
        format(costs.outbound_cost, "f"),
        format(costs.total_cost, "f"),
    )
    tables = (
        ("inbound_plan.csv", "source_id,warehouse_id,sku_id,pallets,transport_cost,handling_cost", inbound),
        ("outbound_plan.csv", "warehouse_id,destination_id,sku_id,pallets,transport_cost", outbound),
        (
            "summary.csv",
            "status,total_demand_pallets,total_allocated_pallets,"
            "inbound_cost,handling_cost,outbound_cost,total_cost",
            (summary,),
        ),
    )
    folder.mkdir(parents=True, exist_ok=False)
    created: list[Path] = []
    try:
        for name, header, rows in tables:
            _write_table(folder / name, header, rows, created)
    except Exception:
        # Only clean up paths this call created; preserve prior runs.
        for path in created:
            try:
                path.unlink(missing_ok=True)
            except OSError:
                pass
        try:
            folder.rmdir()
        except OSError:
            pass
        raise
    return folder


def _write_table(
    path: Path,
    header: str,
    rows: Iterable[tuple[str | int, ...]],
    created: list[Path],
) -> None:
    with path.open("x", encoding="utf-8", newline="") as stream:
        created.append(path)
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(header.split(","))
        writer.writerows(rows)
