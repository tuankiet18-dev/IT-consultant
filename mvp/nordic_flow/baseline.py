"""The 'habit' baseline: each zone is served from its preferred warehouse.

Within a warehouse, suppliers are used cheapest-inbound-first. If the preferred
warehouse is full or cannot take a SKU, the planner falls back to the next
cheapest warehouse for that zone. The result is always feasible when a
feasible plan exists for the greedy order; otherwise the shortfall is reported.
With transfer lanes, a shortest available path supplies each selected final
warehouse. Every visited warehouse and transfer lane consumes its capacity.
"""
from __future__ import annotations
import heapq
import math
from .schema import Dataset, Plan


def baseline(ds: Dataset) -> Plan:
    if ds.transfers or ds.direct:
        return _transfer_baseline(ds)
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


def _transfer_baseline(ds: Dataset) -> Plan:
    """Greedy preferred final warehouse with the cheapest currently available path."""
    plan = Plan(status="BASELINE", mode="baseline")
    supply_left = dict(ds.supply)
    cap_left = {w.id: w.capacity for w in ds.warehouses.values()}
    lane_left = dict(ds.transfer_capacity)
    direct_left = dict(ds.direct_capacity)
    successors = {w: [] for w in ds.warehouses}
    for origin, destination in ds.transfers:
        successors[origin].append(destination)

    def cheapest_path(final, sku):
        factor = ds.skus[sku].pallet_factor
        available = {w for w in ds.warehouses if ds.sku_allowed(w, sku)
                     and cap_left[w] + 1e-9 >= factor}
        distances, heap = {}, []
        for (supplier, warehouse), rate in ds.inbound.items():
            if warehouse not in available or supply_left.get((supplier, sku), 0) < 1:
                continue
            cost = rate + ds.warehouses[warehouse].handling_in
            if cost < distances.get(warehouse, float("inf")):
                distances[warehouse] = cost
                heapq.heappush(heap, (cost, warehouse, supplier, (warehouse,)))
        while heap:
            cost, warehouse, supplier, path = heapq.heappop(heap)
            if cost > distances[warehouse]:
                continue
            if warehouse == final:
                return supplier, path
            for destination in successors[warehouse]:
                if destination not in available or lane_left.get((warehouse, destination), float("inf")) < 1:
                    continue
                next_cost = (cost + ds.transfers[warehouse, destination]
                             + ds.warehouses[warehouse].handling_out
                             + ds.warehouses[destination].handling_in)
                if next_cost < distances.get(destination, float("inf")):
                    distances[destination] = next_cost
                    heapq.heappush(heap, (next_cost, destination, supplier, (*path, destination)))
        return None

    for zone in ds.zones.values():
        order = [zone.preferred_warehouse] + sorted(
            (w for w in ds.warehouses if w != zone.preferred_warehouse and (w, zone.id) in ds.outbound),
            key=lambda w: ds.outbound[w, zone.id])
        for sku, item in ds.skus.items():
            need = ds.demand.get((zone.id, sku), 0)
            for final in order:
                if (final, zone.id) not in ds.outbound or not ds.sku_allowed(final, sku):
                    continue
                while need > 0:
                    route = cheapest_path(final, sku)
                    if route is None:
                        break
                    supplier, path = route
                    lanes = list(zip(path, path[1:]))
                    room = min(math.floor((cap_left[w] + 1e-9) / item.pallet_factor) for w in path)
                    lane_room = min((lane_left.get(lane, float("inf")) for lane in lanes), default=float("inf"))
                    qty = int(min(need, supply_left[supplier, sku], room, lane_room))
                    if qty <= 0:
                        break
                    supply_left[supplier, sku] -= qty
                    for warehouse in path:
                        cap_left[warehouse] -= qty * item.pallet_factor
                    first_key = (supplier, path[0], sku)
                    plan.inbound[first_key] = plan.inbound.get(first_key, 0) + qty
                    for origin, destination in lanes:
                        key = (origin, destination, sku)
                        plan.transfers[key] = plan.transfers.get(key, 0) + qty
                        if (origin, destination) in lane_left:
                            lane_left[origin, destination] -= qty
                    key = (final, zone.id, sku)
                    plan.outbound[key] = plan.outbound.get(key, 0) + qty
                    need -= qty
                if need <= 0:
                    break
            if need > 0:
                # Habit remains warehouse-first. Direct delivery is a fallback,
                # and its route capacity is shared across all products.
                direct_suppliers = sorted((s for s in ds.suppliers if (s, zone.id) in ds.direct),
                                          key=lambda s: (ds.direct[s, zone.id], s))
                for supplier in direct_suppliers:
                    quantity = int(min(need, supply_left.get((supplier, sku), 0),
                                       direct_left.get((supplier, zone.id), float("inf"))))
                    if quantity <= 0:
                        continue
                    plan.direct[supplier, zone.id, sku] = quantity
                    supply_left[supplier, sku] -= quantity
                    if (supplier, zone.id) in direct_left:
                        direct_left[supplier, zone.id] -= quantity
                    need -= quantity
                    if need <= 0:
                        break
            if need > 0:
                plan.shortfall[zone.id, sku] = need
    if plan.shortfall:
        plan.status = "BASELINE_INFEASIBLE"
    return plan
