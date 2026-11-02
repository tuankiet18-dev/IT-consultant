"""Independent plan checker. Does not use the solver, so it can catch model bugs."""
from __future__ import annotations
from collections import defaultdict
from .schema import Dataset, Plan


def verify_plan(ds: Dataset, plan: Plan, tol: float = 1e-6) -> list[str]:
    bad: list[str] = []
    sup, dem = defaultdict(float), defaultdict(float)
    cap = defaultdict(float)
    ins, outs = defaultdict(float), defaultdict(float)
    for (s, w, p), q in plan.inbound.items():
        if q < -tol: bad.append(f"negative flow {s}->{w} {p}")
        if (s, w) not in ds.inbound: bad.append(f"lane {s}->{w} is not allowed")
        if not ds.sku_allowed(w, p): bad.append(f"SKU {p} not allowed at {w}")
        sup[s, p] += q; ins[w, p] += q; cap[w] += q * ds.skus[p].pallet_factor
    for (w, z, p), q in plan.outbound.items():
        if q < -tol: bad.append(f"negative flow {w}->{z} {p}")
        if (w, z) not in ds.outbound: bad.append(f"lane {w}->{z} is not allowed")
        dem[z, p] += q; outs[w, p] += q
    for k, v in sup.items():
        if v > ds.supply.get(k, 0) + tol: bad.append(f"supply exceeded for {k}: {v:g} > {ds.supply.get(k, 0):g}")
    for k, q in ds.demand.items():
        got = dem.get(k, 0) + plan.shortfall.get(k, 0)
        if abs(got - q) > tol: bad.append(f"demand not met for {k}: {got:g} vs {q:g}")
    for k in set(ins) | set(outs):
        if abs(ins.get(k, 0) - outs.get(k, 0)) > tol: bad.append(f"flow imbalance at {k}: in {ins.get(k,0):g}, out {outs.get(k,0):g}")
    for w, load in cap.items():
        if load > ds.warehouses[w].capacity + tol: bad.append(f"capacity exceeded at {w}: {load:g} > {ds.warehouses[w].capacity:g}")
    return bad
