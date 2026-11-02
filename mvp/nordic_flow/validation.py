"""Semantic checks run before any optimisation. Errors block the run."""
from __future__ import annotations
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
    for (s, p), q in ds.supply.items():
        if s not in ds.suppliers: err("supply.csv", f"unknown supplier {s!r}")
        if p not in ds.skus: err("supply.csv", f"unknown SKU {p!r}")
        if mode == "milp" and q != int(q): warn("supply.csv", f"non-integer supply {q} for ({s}, {p}); it will be rounded down in MILP mode")
    for (z, p), q in ds.demand.items():
        if z not in ds.zones: err("demand.csv", f"unknown zone {z!r}")
        if p not in ds.skus: err("demand.csv", f"unknown SKU {p!r}")
        if mode == "milp" and q != int(q): err("demand.csv", f"demand for ({z}, {p}) is {q}; MILP needs whole pallets")
    for z in ds.zones.values():
        if z.preferred_warehouse not in ds.warehouses:
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
        ok = any((w, z) in ds.outbound and ds.sku_allowed(w, p)
                 and any((s, w) in ds.inbound and ds.supply.get((s, p), 0) > 0 for s in ds.suppliers)
                 for w in ds.warehouses)
        if not ok:
            err("outbound_rates.csv", f"no allowed lane can serve zone {z} with SKU {p}")
    total_cap = sum(w.capacity for w in ds.warehouses.values())
    total_need = sum(q * ds.skus[p].pallet_factor for (z, p), q in ds.demand.items() if p in ds.skus)
    if total_need > total_cap + 1e-9:
        err("warehouses.csv", f"total warehouse capacity {total_cap:g} is below total demand {total_need:g}")
    return out


def has_errors(issues: list[Issue]) -> bool:
    return any(i.severity == "error" for i in issues)
