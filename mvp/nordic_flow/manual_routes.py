"""Planner reservations for complete supplier-to-zone paths.

A reservation fixes a quantity on one ordered path. Multiple reservations add
on shared legs. The optimiser may send additional goods on those legs. Because
each reservation is a complete balanced path, subtracting all reserved flows
from a plan leaves a valid residual flow for the remaining demand.
"""
from __future__ import annotations

from collections import defaultdict
import math

from .schema import Dataset, Plan


def validate_manual_routes(ds: Dataset, route_pins: list[dict] | None, mode: str = "milp") -> list[str]:
    """Check path declarations; shared capacity and supply remain solver limits."""
    errors: list[str] = []
    if mode not in ("lp", "milp"):
        return ["manual route mode must be 'lp' or 'milp'"]
    if route_pins is None:
        return errors
    if not isinstance(route_pins, list):
        return ["manual routes must be a list"]
    reserved_demand = defaultdict(float)
    for index, route in enumerate(route_pins, 1):
        prefix = f"manual route {index}"
        if not isinstance(route, dict):
            errors.append(f"{prefix} must be an object")
            continue
        supplier, zone, sku = (route.get(field) for field in ("supplier", "zone", "sku"))
        references_valid = True
        for name, value, store in (("supplier", supplier, ds.suppliers), ("zone", zone, ds.zones), ("sku", sku, ds.skus)):
            if not isinstance(value, str) or value not in store:
                errors.append(f"{prefix} has an unknown {name}")
                references_valid = False
        quantity = route.get("pallets")
        quantity_valid = (isinstance(quantity, (int, float)) and not isinstance(quantity, bool)
                          and math.isfinite(quantity) and quantity > 0)
        if not quantity_valid:
            errors.append(f"{prefix} pallets must be finite and positive")
        elif mode == "milp" and quantity != int(quantity):
            errors.append(f"{prefix} requires whole pallets in MILP mode")
        reason = route.get("reason")
        if not isinstance(reason, str) or len(reason.strip()) < 3:
            errors.append(f"{prefix} requires a reason of at least three characters")
        path = route.get("warehouses")
        path_valid = isinstance(path, list)
        if not path_valid:
            errors.append(f"{prefix} warehouses must be an ordered list (empty for direct delivery)")
        else:
            for warehouse in path:
                if not isinstance(warehouse, str) or warehouse not in ds.warehouses:
                    errors.append(f"{prefix} has an unknown warehouse")
                    path_valid = False
            if path_valid and len(set(path)) != len(path):
                errors.append(f"{prefix} must not visit a warehouse more than once")
                path_valid = False
        if not references_valid:
            continue
        if quantity_valid:
            reserved_demand[zone, sku] += quantity
        if not path_valid:
            continue
        if ds.supply.get((supplier, sku), 0) <= 0:
            errors.append(f"{prefix} supplier has no supply of the selected SKU")
        if ds.demand.get((zone, sku), 0) <= 0:
            errors.append(f"{prefix} zone has no demand for the selected SKU")
        if not path:
            if (supplier, zone) not in ds.direct:
                errors.append(f"{prefix} must include at least one warehouse or a declared direct lane; direct lane {supplier}->{zone} is not declared")
            continue
        if (supplier, path[0]) not in ds.inbound:
            errors.append(f"{prefix} inbound lane {supplier}->{path[0]} is not declared")
        for origin, destination in zip(path, path[1:]):
            if (origin, destination) not in ds.transfers:
                errors.append(f"{prefix} transfer lane {origin}->{destination} is not declared")
        if (path[-1], zone) not in ds.outbound:
            errors.append(f"{prefix} outbound lane {path[-1]}->{zone} is not declared")
        for warehouse in path:
            if not ds.sku_allowed(warehouse, sku):
                errors.append(f"{prefix} SKU {sku} is not eligible at {warehouse}")
    for (zone, sku), quantity in reserved_demand.items():
        demand = ds.demand.get((zone, sku), 0)
        if quantity > demand + 1e-6:
            errors.append(f"manual routes reserve {quantity:g} pallets for {zone}/{sku}, exceeding demand {demand:g}")
    return errors


def reserved_flows(route_pins: list[dict] | None) -> tuple[dict, dict, dict, dict]:
    """Sum validated paths into inbound, transfer, outbound and direct maps."""
    inbound, transfers, outbound = defaultdict(float), defaultdict(float), defaultdict(float)
    direct = defaultdict(float)
    for route in route_pins or []:
        supplier, zone, sku = (route[field] for field in ("supplier", "zone", "sku"))
        path, quantity = route["warehouses"], route["pallets"]
        if not path:
            direct[supplier, zone, sku] += quantity
            continue
        inbound[supplier, path[0], sku] += quantity
        for origin, destination in zip(path, path[1:]):
            transfers[origin, destination, sku] += quantity
        outbound[path[-1], zone, sku] += quantity
    return dict(inbound), dict(transfers), dict(outbound), dict(direct)


def verify_manual_routes(ds: Dataset, plan: Plan, route_pins: list[dict] | None, tol: float = 1e-6) -> list[str]:
    """Independently ensure a computed plan contains every reserved path quantity."""
    errors = validate_manual_routes(ds, route_pins, plan.mode)
    if errors:
        return errors
    for name, actual, reserved in zip(
        ("inbound", "transfer", "outbound", "direct"),
        (plan.inbound, plan.transfers, plan.outbound, plan.direct),
        reserved_flows(route_pins),
    ):
        for key, quantity in reserved.items():
            actual_quantity = actual.get(key, 0)
            if not isinstance(actual_quantity, (int, float)) or not math.isfinite(actual_quantity) or actual_quantity < quantity - tol:
                errors.append(f"manual route {name} requirement not met for {key}: {actual_quantity} < {quantity:g}")
    return errors
