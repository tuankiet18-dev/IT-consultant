"""Explain why a dataset has no feasible plan (shortage of supply, capacity or lanes)."""
from __future__ import annotations
from .optimiser import solve
from .network import direct_suppliers
from .schema import Dataset


def diagnose(ds: Dataset) -> dict:
    """Solve a relaxed LP where demand may go unmet at a heavy penalty and report where it does."""
    plan = solve(ds, mode="lp", allow_shortfall=True)
    if not plan.usable:
        return {"feasible": False, "unmet_by_zone_sku": {}, "unmet_by_sku": {},
                "likely_causes": [f"diagnostic solver returned {plan.status}; review the transfer graph and data"]}
    short = plan.shortfall
    by_sku: dict[str, float] = {}
    for (z, p), q in short.items():
        by_sku[p] = by_sku.get(p, 0) + q
    total_cap = sum(w.capacity for w in ds.warehouses.values())
    need_cap = sum(max(0.0, quantity - sum(
        min(ds.supply.get((supplier, sku), 0), ds.direct_capacity.get((supplier, zone), float("inf")))
        for supplier in direct_suppliers(ds, zone, sku))) * ds.skus[sku].pallet_factor
        for (zone, sku), quantity in ds.demand.items() if sku in ds.skus)
    supply_gap = {p: sum(q for (z, k), q in ds.demand.items() if k == p) - sum(q for (s, k), q in ds.supply.items() if k == p)
                  for p in ds.skus}
    causes = []
    if any(g > 1e-9 for g in supply_gap.values()):
        causes.append("supply: total supply is below demand for " + ", ".join(p for p, g in supply_gap.items() if g > 1e-9))
    if need_cap > total_cap + 1e-9:
        causes.append(f"capacity: total warehouse capacity {total_cap:g} is below demand requiring warehouse handling {need_cap:g}")
    if short and not causes:
        causes.append("warehouse, transfer or direct-route bottleneck: review capacity, lane limits and SKU eligibility along the route to demand")
    return {"feasible": not short, "unmet_by_zone_sku": short, "unmet_by_sku": by_sku, "likely_causes": causes}
