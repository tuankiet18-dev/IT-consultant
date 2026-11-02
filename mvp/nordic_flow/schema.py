"""Plain data model for one planning period.

Units: quantities are pallets; costs are currency units per pallet; warehouse
capacity is in pallet-equivalents per planning period (pallet x pallet_factor).
"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Supplier:
    id: str
    name: str


@dataclass(frozen=True)
class Warehouse:
    id: str
    name: str
    capacity: float          # pallet-equivalents handled per period
    handling_in: float       # cost per pallet received
    handling_out: float      # cost per pallet shipped


@dataclass(frozen=True)
class Zone:
    id: str
    name: str
    preferred_warehouse: str  # used only by the baseline ("habit") rule


@dataclass(frozen=True)
class Sku:
    id: str
    name: str
    pallet_factor: float = 1.0  # capacity units used by one pallet


@dataclass
class Dataset:
    suppliers: dict[str, Supplier] = field(default_factory=dict)
    warehouses: dict[str, Warehouse] = field(default_factory=dict)
    zones: dict[str, Zone] = field(default_factory=dict)
    skus: dict[str, Sku] = field(default_factory=dict)
    inbound: dict[tuple[str, str], float] = field(default_factory=dict)    # (supplier, warehouse) -> cost
    outbound: dict[tuple[str, str], float] = field(default_factory=dict)   # (warehouse, zone) -> cost
    supply: dict[tuple[str, str], float] = field(default_factory=dict)     # (supplier, sku) -> max pallets
    demand: dict[tuple[str, str], float] = field(default_factory=dict)     # (zone, sku) -> pallets
    eligible: dict[str, set[str]] | None = None                            # warehouse -> allowed SKUs (None = all)

    def sku_allowed(self, warehouse: str, sku: str) -> bool:
        return self.eligible is None or sku in self.eligible.get(warehouse, set())


@dataclass
class Plan:
    status: str                       # OPTIMAL | FEASIBLE | INFEASIBLE | ERROR | BASELINE | BASELINE_INFEASIBLE
    mode: str                         # lp | milp | baseline
    objective: float | None = None
    inbound: dict[tuple[str, str, str], float] = field(default_factory=dict)   # (supplier, warehouse, sku) -> pallets
    outbound: dict[tuple[str, str, str], float] = field(default_factory=dict)  # (warehouse, zone, sku) -> pallets
    shortfall: dict[tuple[str, str], float] = field(default_factory=dict)      # (zone, sku) -> unmet pallets
    solve_seconds: float = 0.0

    @property
    def usable(self) -> bool:
        return self.status in ("OPTIMAL", "FEASIBLE", "BASELINE")


@dataclass(frozen=True)
class Issue:
    severity: str   # error | warning
    file: str
    row: int | None
    message: str

    def __str__(self) -> str:
        where = self.file + (f" row {self.row}" if self.row else "")
        return f"[{self.severity.upper()}] {where}: {self.message}"
