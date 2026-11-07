"""Semantic checks run before any optimisation. Errors block the run."""
from __future__ import annotations
import math
from .network import direct_suppliers, has_transfer_cycle, reachable_warehouses
from .schema import Dataset, Issue


def validate(ds: Dataset, mode: str = "milp") -> list[Issue]:
    out: list[Issue] = []
    err = lambda f, m: out.append(Issue("error", f, None, m))
    warn = lambda f, m: out.append(Issue("warning", f, None, m))

    if not ds.demand:
        err("demand.csv", "no demand rows")
    for (s, w) in ds.inbound:
        if s not in ds.suppliers: err("inbound_rates.csv", f"unknown supplier {s!r}")
        if w not in ds.warehouses: err("inbound_rates.csv", f"unknown warehouse {w!r}")
    for (w, z) in ds.outbound:
        if w not in ds.warehouses: err("outbound_rates.csv", f"unknown warehouse {w!r}")
        if z not in ds.zones: err("outbound_rates.csv", f"unknown zone {z!r}")
    for (supplier, zone), cost in ds.direct.items():
        if supplier not in ds.suppliers: err("direct_rates.csv", f"unknown supplier {supplier!r}")
        if zone not in ds.zones: err("direct_rates.csv", f"unknown zone {zone!r}")
        if not math.isfinite(cost) or cost < 0: err("direct_rates.csv", "cost_per_pallet must be finite and >= 0")
    for lane, cap in ds.direct_capacity.items():
        if lane not in ds.direct: err("direct_rates.csv", f"capacity has no direct lane {lane}")
        if not math.isfinite(cap) or cap < 0: err("direct_rates.csv", "max_pallets must be finite and >= 0")
    for (origin, destination), cost in ds.transfers.items():
        if origin not in ds.warehouses: err("transfer_rates.csv", f"unknown origin warehouse {origin!r}")
        if destination not in ds.warehouses: err("transfer_rates.csv", f"unknown destination warehouse {destination!r}")
        if origin == destination: err("transfer_rates.csv", "a warehouse cannot transfer to itself")
        if not math.isfinite(cost) or cost < 0: err("transfer_rates.csv", "cost_per_pallet must be finite and >= 0")
    for lane, cap in ds.transfer_capacity.items():
        if lane not in ds.transfers: err("transfer_rates.csv", f"capacity has no transfer lane {lane}")
        if not math.isfinite(cap) or cap < 0: err("transfer_rates.csv", "max_pallets must be finite and >= 0")
    if has_transfer_cycle(ds.transfers):
        err("transfer_rates.csv", "warehouse transfer lanes must form a directed acyclic graph")
    for (s, p), q in ds.supply.items():
        if s not in ds.suppliers: err("supply.csv", f"unknown supplier {s!r}")
        if p not in ds.skus: err("supply.csv", f"unknown SKU {p!r}")
        if mode == "milp" and q != int(q): warn("supply.csv", f"non-integer supply {q} for ({s}, {p}); it will be rounded down in MILP mode")
    reachable = {p: reachable_warehouses(ds, p) for p in ds.skus}
    for (z, p), q in ds.demand.items():
        if z not in ds.zones: err("demand.csv", f"unknown zone {z!r}")
        if p not in ds.skus: err("demand.csv", f"unknown SKU {p!r}")
        if mode == "milp" and q != int(q): err("demand.csv", f"demand for ({z}, {p}) is {q}; MILP needs whole pallets")
    for z in ds.zones.values():
        direct_zone = any(zone == z.id and ds.direct_capacity.get((supplier, zone), float("inf")) > 0
                          for supplier, zone in ds.direct)
        if z.preferred_warehouse not in ds.warehouses and not (not z.preferred_warehouse and direct_zone):
            err("zones.csv", f"zone {z.id} prefers unknown warehouse {z.preferred_warehouse!r}")
    if ds.eligible is not None:
        for w, skus in ds.eligible.items():
            if w not in ds.warehouses: err("warehouse_skus.csv", f"unknown warehouse {w!r}")
            for p in skus:
                if p not in ds.skus: err("warehouse_skus.csv", f"unknown SKU {p!r}")

    # feasibility pre-checks (cheap, explain the most common reasons for 'no solution')
    for p in ds.skus:
        need = sum(q for (z, k), q in ds.demand.items() if k == p)
        have = sum(q for (s, k), q in ds.supply.items() if k == p)
        if need > have + 1e-9:
            err("supply.csv", f"SKU {p}: demand {need:g} exceeds total supply {have:g}")
    for (z, p), q in ds.demand.items():
        if q <= 0: continue
        ok = any((w, z) in ds.outbound for w in reachable.get(p, set())) or bool(direct_suppliers(ds, z, p))
        if not ok:
            err("outbound_rates.csv", f"no allowed lane can serve zone {z} with SKU {p}")
    total_cap = sum(w.capacity for w in ds.warehouses.values())
    # An optimistic upper bound on direct delivery leaves a safe lower bound
    # on pallets that must visit at least one warehouse. Direct lane/supplier
    # competition is resolved by the solver, not by this cheap pre-check.
    total_need = 0.0
    for (zone, sku), quantity in ds.demand.items():
        if sku not in ds.skus:
            continue
        direct_possible = sum(min(ds.supply.get((supplier, sku), 0),
                                  ds.direct_capacity.get((supplier, zone), float("inf")))
                              for supplier in direct_suppliers(ds, zone, sku))
        total_need += max(0.0, quantity - direct_possible) * ds.skus[sku].pallet_factor
    if total_need > total_cap + 1e-9:
        err("warehouses.csv", f"total warehouse capacity {total_cap:g} is below demand requiring warehouse handling {total_need:g}")
    return out


def has_errors(issues: list[Issue]) -> bool:
    return any(i.severity == "error" for i in issues)
