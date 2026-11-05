"""Convert CSV fields to planning data and validate business keys."""

import re
from collections.abc import Callable, Iterable
from decimal import Decimal
from typing import TypeVar

from .models import CsvRow, InputDataError, Problem, Warehouse

K = TypeVar("K")
V = TypeVar("V")


def _error(row: CsvRow, message: str) -> InputDataError:
    return InputDataError(row.filename, message, row.line)


def _required(row: CsvRow, column: str) -> str:
    value = row.values[column].strip()
    if not value:
        raise _error(row, f"{column} must not be empty")
    return value


def _pallets(row: CsvRow, column: str) -> int:
    value = _required(row, column)
    if not re.fullmatch(r"[0-9]+", value):
        raise _error(row, f"{column} must be a non-negative integer")
    try:
        return int(value)
    except ValueError as exc:
        raise _error(row, f"{column} contains too many digits") from exc


def _cost(row: CsvRow, column: str) -> Decimal:
    value = _required(row, column)
    if not re.fullmatch(r"(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)", value):
        raise _error(row, f"{column} must be a finite non-negative decimal")
    return Decimal(value)


def _index(
    rows: Iterable[CsvRow],
    key_of: Callable[[CsvRow], K],
    value_of: Callable[[CsvRow], V],
) -> dict[K, V]:
    entries: dict[K, V] = {}
    first_lines: dict[K, int] = {}
    for row in rows:
        key = key_of(row)
        if key in entries:
            raise _error(row, f"duplicate key {key!r} (first seen on line {first_lines[key]})")
        entries[key] = value_of(row)
        first_lines[key] = row.line
    return entries


def _lane_key(
    row: CsvRow, first: str, second: str, first_ids: set[str], second_ids: set[str]
) -> tuple[str, str]:
    origin, destination = _required(row, first), _required(row, second)
    for column, value, known_ids in (
        (first, origin, first_ids),
        (second, destination, second_ids),
    ):
        if value not in known_ids:
            raise _error(row, f"unknown {column}: {value!r}")
    return origin, destination


def validate_problem(
    *,
    supply_rows: Iterable[CsvRow],
    warehouse_rows: Iterable[CsvRow],
    demand_rows: Iterable[CsvRow],
    inbound_rows: Iterable[CsvRow],
    outbound_rows: Iterable[CsvRow],
) -> Problem:
    """Validate and index input rows; leave feasibility checks to the solver."""
    supply = _index(
        supply_rows,
        lambda row: (_required(row, "source_id"), _required(row, "sku_id")),
        lambda row: _pallets(row, "available_pallets"),
    )
    warehouses = _index(
        warehouse_rows,
        lambda row: _required(row, "warehouse_id"),
        lambda row: Warehouse(
            _pallets(row, "capacity_pallets"), _cost(row, "handling_cost_per_pallet")
        ),
    )
    demand = _index(
        demand_rows,
        lambda row: (_required(row, "destination_id"), _required(row, "sku_id")),
        lambda row: _pallets(row, "required_pallets"),
    )
    source_ids = {source for source, _ in supply}
    warehouse_ids = set(warehouses)
    destination_ids = {destination for destination, _ in demand}
    inbound_rates = _index(
        inbound_rows,
        lambda row: _lane_key(row, "source_id", "warehouse_id", source_ids, warehouse_ids),
        lambda row: _cost(row, "transport_cost_per_pallet"),
    )
    outbound_rates = _index(
        outbound_rows,
        lambda row: _lane_key(
            row, "warehouse_id", "destination_id", warehouse_ids, destination_ids
        ),
        lambda row: _cost(row, "transport_cost_per_pallet"),
    )
    return Problem(supply, warehouses, demand, inbound_rates, outbound_rates)
