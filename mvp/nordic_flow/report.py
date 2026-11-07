"""Cost breakdowns and baseline-vs-optimised comparison (all numbers computed here, never by AI)."""
from __future__ import annotations
from collections import defaultdict
from .schema import Dataset, Plan


def cost_breakdown(ds: Dataset, plan: Plan) -> dict[str, float]:
    b = {"inbound_freight": 0.0, "transfer_freight": 0.0, "direct_freight": 0.0, "inbound_handling": 0.0,
         "outbound_freight": 0.0, "outbound_handling": 0.0}
    for (s, w, p), q in plan.inbound.items():
        b["inbound_freight"] += ds.inbound[s, w] * q
        b["inbound_handling"] += ds.warehouses[w].handling_in * q
    for (w, z, p), q in plan.outbound.items():
        b["outbound_freight"] += ds.outbound[w, z] * q
        b["outbound_handling"] += ds.warehouses[w].handling_out * q
    for (origin, destination, p), q in plan.transfers.items():
        b["transfer_freight"] += ds.transfers[origin, destination] * q
        b["outbound_handling"] += ds.warehouses[origin].handling_out * q
        b["inbound_handling"] += ds.warehouses[destination].handling_in * q
    for (supplier, zone, p), q in plan.direct.items():
        b["direct_freight"] += ds.direct[supplier, zone] * q
    b["total"] = sum(b.values())
    return {k: round(v, 6) for k, v in b.items()}


def utilisation(ds: Dataset, plan: Plan) -> dict[str, float]:
    load = defaultdict(float)
    for (s, w, p), q in plan.inbound.items():
        load[w] += q * ds.skus[p].pallet_factor
    for (origin, destination, p), q in plan.transfers.items():
        load[destination] += q * ds.skus[p].pallet_factor
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
    transfer_changes = [
        {"from_warehouse": origin, "to_warehouse": destination, "sku": sku,
         "baseline": base.transfers.get((origin, destination, sku), 0),
         "optimised": opt.transfers.get((origin, destination, sku), 0)}
        for origin, destination, sku in sorted(set(base.transfers) | set(opt.transfers))
        if abs(base.transfers.get((origin, destination, sku), 0) - opt.transfers.get((origin, destination, sku), 0)) > 1e-6
    ]
    direct_changes = [
        {"supplier": supplier, "zone": zone, "sku": sku,
         "baseline": base.direct.get((supplier, zone, sku), 0),
         "optimised": opt.direct.get((supplier, zone, sku), 0)}
        for supplier, zone, sku in sorted(set(base.direct) | set(opt.direct))
        if abs(base.direct.get((supplier, zone, sku), 0) - opt.direct.get((supplier, zone, sku), 0)) > 1e-6
    ]
    loads = defaultdict(float)
    for (_, warehouse, sku), quantity in opt.inbound.items():
        loads[warehouse] += quantity * ds.skus[sku].pallet_factor
    for (_, warehouse, sku), quantity in opt.transfers.items():
        loads[warehouse] += quantity * ds.skus[sku].pallet_factor
    return {
        "baseline": cb, "optimised": co,
        "saving": round(saving, 6), "saving_pct": round(pct, 4),
        "utilisation_baseline": utilisation(ds, base), "utilisation_optimised": utilisation(ds, opt),
        "changes": changes,
        "transfer_changes": transfer_changes,
        "direct_changes": direct_changes,
        "binding_warehouses": [w.id for w in ds.warehouses.values()
                               if w.capacity > 0 and abs(loads[w.id] - w.capacity) <= 1e-6],
        "baseline_status": base.status, "optimised_status": opt.status,
    }
