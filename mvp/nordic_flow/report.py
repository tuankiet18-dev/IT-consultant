"""Cost breakdowns and baseline-vs-optimised comparison (all numbers computed here, never by AI)."""
from __future__ import annotations
from collections import defaultdict
from .schema import Dataset, Plan


def cost_breakdown(ds: Dataset, plan: Plan) -> dict[str, float]:
    b = {"inbound_freight": 0.0, "inbound_handling": 0.0, "outbound_freight": 0.0, "outbound_handling": 0.0}
    for (s, w, p), q in plan.inbound.items():
        b["inbound_freight"] += ds.inbound[s, w] * q
        b["inbound_handling"] += ds.warehouses[w].handling_in * q
    for (w, z, p), q in plan.outbound.items():
        b["outbound_freight"] += ds.outbound[w, z] * q
        b["outbound_handling"] += ds.warehouses[w].handling_out * q
    b["total"] = sum(b.values())
    return {k: round(v, 6) for k, v in b.items()}


def utilisation(ds: Dataset, plan: Plan) -> dict[str, float]:
    load = defaultdict(float)
    for (s, w, p), q in plan.inbound.items():
        load[w] += q * ds.skus[p].pallet_factor
    return {w.id: round(load[w.id] / w.capacity, 4) if w.capacity else 0.0 for w in ds.warehouses.values()}


def warehouse_by_zone(plan: Plan) -> dict[tuple[str, str], dict[str, float]]:
    out: dict[tuple[str, str], dict[str, float]] = defaultdict(dict)
    for (w, z, p), q in plan.outbound.items():
        out[z, p][w] = out[z, p].get(w, 0) + q
    return out


def compare(ds: Dataset, base: Plan, opt: Plan) -> dict:
    cb, co = cost_breakdown(ds, base), cost_breakdown(ds, opt)
    saving = cb["total"] - co["total"]
    pct = (saving / cb["total"] * 100) if cb["total"] else 0.0
    bz, oz = warehouse_by_zone(base), warehouse_by_zone(opt)
    changes = []
    for key in sorted(set(bz) | set(oz)):
        if bz.get(key, {}) != oz.get(key, {}):
            changes.append({"zone": key[0], "sku": key[1], "baseline": bz.get(key, {}), "optimised": oz.get(key, {})})
    return {
        "baseline": cb, "optimised": co,
        "saving": round(saving, 6), "saving_pct": round(pct, 4),
        "utilisation_baseline": utilisation(ds, base), "utilisation_optimised": utilisation(ds, opt),
        "changes": changes,
        "binding_warehouses": [w for w, u in utilisation(ds, opt).items() if u >= 0.999],
        "baseline_status": base.status, "optimised_status": opt.status,
    }
