"""Explain why a dataset has no feasible plan (shortage of supply, capacity or lanes)."""
from __future__ import annotations
from .optimiser import solve
from .schema import Dataset


def diagnose(ds: Dataset) -> dict:
    """Solve a relaxed LP where demand may go unmet at a heavy penalty and report where it does."""
    plan = solve(ds, mode="lp", allow_shortfall=True)
    short = plan.shortfall
    by_sku: dict[str, float] = {}
    for (z, p), q in short.items():
        by_sku[p] = by_sku.get(p, 0) + q
    total_cap = sum(w.capacity for w in ds.warehouses.values())
    need_cap = sum(q * ds.skus[p].pallet_factor for (z, p), q in ds.demand.items() if p in ds.skus)
    supply_gap = {p: sum(q for (z, k), q in ds.demand.items() if k == p) - sum(q for (s, k), q in ds.supply.items() if k == p)
                  for p in ds.skus}
    causes = []
    if any(g > 1e-9 for g in supply_gap.values()):
        causes.append("supply: total supply is below demand for " + ", ".join(p for p, g in supply_gap.items() if g > 1e-9))
    if need_cap > total_cap + 1e-9:
        causes.append(f"capacity: total warehouse capacity {total_cap:g} is below demand {need_cap:g}")
    if short and not causes:
        causes.append("lanes or SKU eligibility: some demand cannot reach a warehouse that is allowed to serve it")
    return {"feasible": not short, "unmet_by_zone_sku": short, "unmet_by_sku": by_sku, "likely_causes": causes}
