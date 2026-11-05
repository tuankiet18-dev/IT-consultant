"""Data shared by the CSV reader, validator and future optimizer."""

from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from typing import Mapping


class InputDataError(ValueError):
    """An input error with the CSV location when available."""

    def __init__(self, filename: str, message: str, row: int | None = None):
        self.filename = filename
        self.row = row
        self.message = message
        location = filename if row is None else f"{filename}:{row}"
        super().__init__(f"{location}: {message}")


@dataclass(frozen=True)
class CsvRow:
    filename: str
    line: int
    values: Mapping[str, str]


@dataclass(frozen=True)
class Warehouse:
    capacity_pallets: int
    handling_cost_per_pallet: Decimal


@dataclass(frozen=True)
class Problem:
    """Validated inputs for one planning period.

    Supply and demand are keyed by (source or destination, SKU).
    Rates are keyed by the ordered pair of endpoints. An absent key is a
    forbidden lane; a present Decimal(0) is a free lane.
    """

    supply: Mapping[tuple[str, str], int]
    warehouses: Mapping[str, Warehouse]
    demand: Mapping[tuple[str, str], int]
    inbound_rates: Mapping[tuple[str, str], Decimal]
    outbound_rates: Mapping[tuple[str, str], Decimal]


class Status(str, Enum):
    OPTIMAL = "OPTIMAL"
    FEASIBLE = "FEASIBLE"
    INFEASIBLE = "INFEASIBLE"
    ERROR = "ERROR"


@dataclass(frozen=True)
class AllocationResult:
    """Sparse pallet flows from the solver; independent verification is separate."""

    status: Status
    inbound: Mapping[tuple[str, str, str], int] = field(default_factory=dict)
    outbound: Mapping[tuple[str, str, str], int] = field(default_factory=dict)
    total_cost: Decimal | None = None
    message: str | None = None
