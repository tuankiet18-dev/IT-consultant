"""The 'habit' baseline: each zone is served from its preferred warehouse.

Within a warehouse, suppliers are used cheapest-inbound-first. If the preferred
warehouse is full or cannot take a SKU, the planner falls back to the next
cheapest warehouse for that zone. The result is always feasible when a
feasible plan exists for the greedy order; otherwise the shortfall is reported.
"""
from __future__ import annotations
from .schema import Dataset, Plan


def baseline(ds: Dataset) -> Plan:
    supply_left = dict(ds.supply)
    cap_left = {w.id: w.capacity for w in ds.warehouses.values()}
    plan = Plan(status="BASELINE", mode="baseline")
    inb, outb = {}, {}
    for z in ds.zones.values():
        order = [z.preferred_warehouse] + sorted(
            (w for w in ds.warehouses if w != z.preferred_warehouse and (w, z.id) in ds.outbound),
            key=lambda w: ds.outbound[w, z.id])
        for p, sku in ds.skus.items():
            need = ds.demand.get((z.id, p), 0)
            for w in order:
                if need <= 0:
                    break
                if (w, z.id) not in ds.outbound or not ds.sku_allowed(w, p):
                    continue
                lanes = sorted((s for s in ds.suppliers if (s, w) in ds.inbound),
                               key=lambda s: ds.inbound[s, w])
                for s in lanes:
                    if need <= 0:
                        break
                    room = int(cap_left[w] // sku.pallet_factor)
                    qty = min(need, supply_left.get((s, p), 0), room)
                    qty = int(qty)
                    if qty <= 0:
                        continue
                    supply_left[s, p] -= qty
                    cap_left[w] -= qty * sku.pallet_factor
                    inb[s, w, p] = inb.get((s, w, p), 0) + qty
                    outb[w, z.id, p] = outb.get((w, z.id, p), 0) + qty
                    need -= qty
            if need > 0:
                plan.shortfall[z.id, p] = need
    plan.inbound, plan.outbound = inb, outb
    if plan.shortfall:
        plan.status = "BASELINE_INFEASIBLE"
    return plan
