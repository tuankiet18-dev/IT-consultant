"""Warehouse transfer network checks shared by import and the independent verifier."""
from __future__ import annotations
from collections import defaultdict, deque
from .schema import Dataset


def has_transfer_cycle(lanes) -> bool:
    """Kahn's algorithm handles large networks without recursive traversal."""
    successors = defaultdict(list)
    degree = defaultdict(int)
    for origin, destination in lanes:
        successors[origin].append(destination)
        degree.setdefault(origin, 0)
        degree[destination] += 1
    queue = deque(node for node, incoming in degree.items() if incoming == 0)
    visited = 0
    while queue:
        node = queue.popleft()
        visited += 1
        for destination in successors[node]:
            degree[destination] -= 1
            if degree[destination] == 0:
                queue.append(destination)
    return visited != len(degree)


def reachable_warehouses(ds: Dataset, sku: str) -> set[str]:
    """Warehouses reachable from a supplied SKU through eligible, open locations."""
    available = {w for w, warehouse in ds.warehouses.items()
                 if warehouse.capacity > 0 and ds.sku_allowed(w, sku)}
    reached = {w for supplier, w in ds.inbound if w in available and ds.supply.get((supplier, sku), 0) > 0}
    successors = defaultdict(list)
    for (origin, destination) in ds.transfers:
        if origin in available and destination in available and ds.transfer_capacity.get((origin, destination), float("inf")) > 0:
            successors[origin].append(destination)
    queue = deque(reached)
    while queue:
        for destination in successors[queue.popleft()]:
            if destination not in reached:
                reached.add(destination)
                queue.append(destination)
    return reached


def direct_suppliers(ds: Dataset, zone: str, sku: str) -> set[str]:
    """Supplied origins with a positive declared direct lane to this customer."""
    return {supplier for supplier, destination in ds.direct
            if destination == zone and supplier in ds.suppliers
            and ds.supply.get((supplier, sku), 0) > 0
            and ds.direct_capacity.get((supplier, zone), float("inf")) > 0}
