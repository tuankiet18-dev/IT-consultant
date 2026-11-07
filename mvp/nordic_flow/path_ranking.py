"""Cheapest complete paths and an explicitly labelled accounting of plan flows.

The model stores aggregate SKU flows, not individual pallet journeys. A
deterministic path decomposition can explain costs, but is not physical tracing.
"""
from __future__ import annotations

from collections import defaultdict, deque
import hashlib
import json
import math

from .schema import Dataset, Plan

TOL = 1e-6
MAX_SAFE_COUNT = 2**53 - 1


def _identity(supplier: str, warehouses: tuple[str, ...], zone: str, sku: str) -> str:
    raw = json.dumps([supplier, warehouses, zone, sku], separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()[:20]


def _path_cost(ds: Dataset, supplier: str, warehouses: tuple[str, ...], zone: str) -> tuple[float, float]:
    if not warehouses:
        return ds.direct[supplier, zone], 0.0
    freight = ds.inbound[supplier, warehouses[0]] + ds.outbound[warehouses[-1], zone]
    freight += sum(ds.transfers[a, b] for a, b in zip(warehouses, warehouses[1:]))
    handling = sum(ds.warehouses[w].handling_in + ds.warehouses[w].handling_out for w in warehouses)
    return freight, handling


def _plan_paths(ds: Dataset, plan: Plan, sku: str, manual_routes: list[dict]) -> dict[tuple, float]:
    """Subtract complete manual reservations, then decompose balanced residuals.

    Only the selected SKU is considered, across all zones, so a path's final
    customer is derived from an actual outbound flow rather than guessed.
    """
    inbound = {(s, w): q for (s, w, p), q in plan.inbound.items() if p == sku}
    transfers = {(a, b): q for (a, b, p), q in plan.transfers.items() if p == sku}
    outbound = {(w, z): q for (w, z, p), q in plan.outbound.items() if p == sku}
    direct = {(s, z): q for (s, z, p), q in plan.direct.items() if p == sku}
    paths = defaultdict(float)

    def subtract(store, key, quantity):
        value = store.get(key, 0) - quantity
        if value < -TOL:
            raise ValueError("The plan cannot be decomposed into its declared manual paths.")
        store[key] = max(0.0, value)

    for route in manual_routes:
        if route["sku"] != sku:
            continue
        supplier, warehouses, zone, quantity = route["supplier"], tuple(route["warehouses"]), route["zone"], route["pallets"]
        if not warehouses:
            subtract(direct, (supplier, zone), quantity)
            paths[supplier, warehouses, zone] += quantity
            continue
        subtract(inbound, (supplier, warehouses[0]), quantity)
        for a, b in zip(warehouses, warehouses[1:]):
            subtract(transfers, (a, b), quantity)
        subtract(outbound, (warehouses[-1], zone), quantity)
        paths[supplier, warehouses, zone] += quantity

    for (supplier, zone), quantity in sorted(direct.items()):
        if quantity > TOL:
            paths[supplier, (), zone] += quantity

    for supplier, first in sorted(inbound):
        while inbound[supplier, first] > TOL:
            warehouses = [first]
            current = first
            while True:
                delivery = next(((w, z) for (w, z) in sorted(outbound) if w == current and outbound[w, z] > TOL), None)
                if delivery:
                    break
                transfer = next(((a, b) for (a, b) in sorted(transfers) if a == current and transfers[a, b] > TOL), None)
                if not transfer or transfer[1] in warehouses:
                    raise ValueError("The saved aggregate flows do not form complete balanced paths.")
                current = transfer[1]
                warehouses.append(current)
            legs = list(zip(warehouses, warehouses[1:]))
            quantity = min([inbound[supplier, first], outbound[delivery]] + [transfers[leg] for leg in legs])
            subtract(inbound, (supplier, first), quantity)
            for leg in legs:
                subtract(transfers, leg, quantity)
            subtract(outbound, delivery, quantity)
            paths[supplier, tuple(warehouses), delivery[1]] += quantity
    if any(q > TOL for q in (*transfers.values(), *outbound.values())):
        raise ValueError("The saved aggregate flows leave unmatched deliveries or transfers.")
    return dict(paths)


def rank_paths(ds: Dataset, plan: Plan, zone: str, sku: str, quantity: float = 1,
               limit: int = 50, manual_routes: list[dict] | None = None) -> dict:
    """Return the global cheapest K eligible paths, not the first K discovered.

    A reverse topological dynamic program retains K+1 suffixes at every
    warehouse. Any omitted suffix has at least K+1 cheaper suffixes for the same
    prefix, so it cannot enter the global first K. Path counts need no traversal
    of every complete combination and are capped only for JSON-safe reporting.
    """
    if zone not in ds.zones or sku not in ds.skus or ds.demand.get((zone, sku), 0) <= 0:
        raise ValueError("Choose a known zone and product with positive demand.")
    if isinstance(quantity, bool) or not isinstance(quantity, (int, float)) or not math.isfinite(quantity) or quantity <= 0:
        raise ValueError("Comparison quantity must be finite and positive.")
    if plan.mode == "milp" and quantity != int(quantity):
        raise ValueError("Comparison quantity must use whole pallets in MILP mode.")
    if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 100:
        raise ValueError("Path limit must be between 1 and 100.")
    factor = ds.skus[sku].pallet_factor
    integer = plan.mode == "milp"

    def capacity(value):
        return math.floor(value + 1e-9) if integer else value

    allowed = {w for w, data in ds.warehouses.items()
               if ds.sku_allowed(w, sku) and capacity(data.capacity / factor) > 0}
    successors = defaultdict(list)
    indegree = {w: 0 for w in allowed}
    for a, b in sorted(ds.transfers):
        cap = ds.transfer_capacity.get((a, b), math.inf)
        if a in allowed and b in allowed and (math.isinf(cap) or capacity(cap) > 0):
            successors[a].append(b)
            indegree[b] += 1
    queue = deque(sorted(w for w, degree in indegree.items() if degree == 0))
    order = []
    while queue:
        current = queue.popleft()
        order.append(current)
        for next_warehouse in successors[current]:
            indegree[next_warehouse] -= 1
            if indegree[next_warehouse] == 0:
                queue.append(next_warehouse)
    if len(order) != len(allowed):
        raise ValueError("Complete path ranking requires an acyclic warehouse network.")
    keep = limit + 1
    suffixes, counts = {}, {}
    for current in reversed(order):
        handling = ds.warehouses[current].handling_in + ds.warehouses[current].handling_out
        candidates = []
        count = 0
        if (current, zone) in ds.outbound:
            candidates.append((ds.outbound[current, zone] + handling, (current,)))
            count += 1
        for next_warehouse in successors[current]:
            candidates.extend((ds.transfers[current, next_warehouse] + handling + cost, (current,) + path)
                              for cost, path in suffixes[next_warehouse])
            count += counts[next_warehouse]
        suffixes[current] = sorted(candidates)[:keep]
        counts[current] = min(count, MAX_SAFE_COUNT + 1)
    candidates = []
    total = 0
    for supplier, first in sorted(ds.inbound):
        if first not in allowed or capacity(ds.supply.get((supplier, sku), 0)) <= 0:
            continue
        candidates.extend((ds.inbound[supplier, first] + cost, supplier, path) for cost, path in suffixes[first])
        total += counts[first]
    for (supplier, destination), cost in sorted(ds.direct.items()):
        if destination != zone or capacity(ds.supply.get((supplier, sku), 0)) <= 0:
            continue
        cap = ds.direct_capacity.get((supplier, destination), math.inf)
        if not math.isinf(cap) and capacity(cap) <= 0:
            continue
        candidates.append((cost, supplier, ()))
        total += 1
    candidates.sort()
    accounted = _plan_paths(ds, plan, sku, manual_routes or [])
    rows = []
    for rank, (_, supplier, warehouses) in enumerate(candidates[:limit], 1):
        freight, handling = _path_cost(ds, supplier, warehouses, zone)
        limits = [("Supplier supply", capacity(ds.supply[supplier, sku])),
                  ("Customer demand", capacity(ds.demand[zone, sku]))]
        limits.extend((ds.warehouses[w].name + " capacity", capacity(ds.warehouses[w].capacity / factor)) for w in warehouses)
        limits.extend((ds.warehouses[a].name + " → " + ds.warehouses[b].name + " route limit", capacity(ds.transfer_capacity[a, b]))
                      for a, b in zip(warehouses, warehouses[1:]) if (a, b) in ds.transfer_capacity)
        if not warehouses and (supplier, zone) in ds.direct_capacity:
            limits.append(("Direct delivery route limit", capacity(ds.direct_capacity[supplier, zone])))
        maximum = min(value for _, value in limits)
        planned = accounted.get((supplier, warehouses, zone), 0)
        rows.append({
            "id": _identity(supplier, warehouses, zone, sku), "rank": rank,
            "supplier": supplier, "warehouses": list(warehouses), "zone": zone, "sku": sku,
            "cost_per_pallet": round(freight + handling, 6),
            "freight_per_pallet": round(freight, 6), "handling_per_pallet": round(handling, 6),
            "quoted_total": round((freight + handling) * quantity, 6),
            "max_pallets": round(maximum, 6), "can_carry_quantity": quantity <= maximum + TOL,
            "bottlenecks": [name for name, value in limits if abs(value - maximum) <= TOL],
            "plan_pallets": round(planned, 6), "plan_cost": round(planned * (freight + handling), 6),
        })
    relevant = [(supplier, warehouses, delivered_zone, q) for (supplier, warehouses, delivered_zone), q in accounted.items() if delivered_zone == zone]
    return {
        "zone": zone, "sku": sku, "quantity": quantity, "mode": plan.mode, "limit": limit,
        "total_paths": total if total <= MAX_SAFE_COUNT else None,
        "truncated": total > limit,
        "paths": rows,
        "plan_accounting": {
            "method": "deterministic_flow_decomposition",
            "note": "Plan path quantities are one deterministic accounting of aggregate product flows, with manual paths reserved first; they are not physical pallet tracking.",
            "delivered_pallets": round(sum(q for _, _, _, q in relevant), 6),
            "total_cost": round(sum(q * sum(_path_cost(ds, supplier, warehouses, zone)) for supplier, warehouses, _, q in relevant), 6),
        },
    }
