"""Independent plan checker. Does not use the solver, so it can catch model bugs."""
from __future__ import annotations
from collections import defaultdict
import math
from .network import has_transfer_cycle
from .schema import Dataset, Plan


def verify_plan(ds: Dataset, plan: Plan, tol: float = 1e-6, allow_shortfall: bool = False) -> list[str]:
    """Strict by default: a plan that leaves demand unmet is not a valid plan (shortfall is for diagnosis only)."""
    bad: list[str] = []
    if plan.shortfall and not allow_shortfall:
        bad.append(f"plan leaves demand unmet for {len(plan.shortfall)} zone-and-SKU pair(s)")
    sup, dem = defaultdict(float), defaultdict(float)
    cap = defaultdict(float)
    ins, outs = defaultdict(float), defaultdict(float)
    transfer_load = defaultdict(float)
    direct_load = defaultdict(float)
    used_transfer_lanes = set()

    def valid_quantity(q, description):
        if isinstance(q, bool) or not isinstance(q, (int, float)) or not math.isfinite(q) or q < -tol:
            bad.append(f"invalid quantity for {description}")
            return False
        if plan.mode == "milp" and abs(q - round(q)) > tol:
            bad.append(f"fractional quantity in whole-pallet plan for {description}")
            return False
        return True

    for (s, w, p), q in plan.inbound.items():
        if not valid_quantity(q, f"inbound {s}->{w} {p}"):
            continue
        if s not in ds.suppliers or w not in ds.warehouses or p not in ds.skus:
            bad.append(f"unknown inbound reference {s}->{w} {p}")
            continue
        if (s, w) not in ds.inbound: bad.append(f"lane {s}->{w} is not allowed")
        if not ds.sku_allowed(w, p): bad.append(f"SKU {p} not allowed at {w}")
        sup[s, p] += q; ins[w, p] += q; cap[w] += q * ds.skus[p].pallet_factor
    for (w, z, p), q in plan.outbound.items():
        if not valid_quantity(q, f"outbound {w}->{z} {p}"):
            continue
        if w not in ds.warehouses or z not in ds.zones or p not in ds.skus:
            bad.append(f"unknown outbound reference {w}->{z} {p}")
            continue
        if (w, z) not in ds.outbound: bad.append(f"lane {w}->{z} is not allowed")
        if not ds.sku_allowed(w, p): bad.append(f"SKU {p} not allowed at {w}")
        if (z, p) not in ds.demand and q > tol: bad.append(f"unexpected demand shipment {w}->{z} {p}")
        dem[z, p] += q; outs[w, p] += q
    for (supplier, zone, sku), quantity in plan.direct.items():
        if not valid_quantity(quantity, f"direct {supplier}->{zone} {sku}"):
            continue
        if supplier not in ds.suppliers or zone not in ds.zones or sku not in ds.skus:
            bad.append(f"unknown direct reference {supplier}->{zone} {sku}")
            continue
        if (supplier, zone) not in ds.direct:
            bad.append(f"direct lane {supplier}->{zone} is not allowed")
        if (zone, sku) not in ds.demand and quantity > tol:
            bad.append(f"unexpected demand shipment {supplier}->{zone} {sku}")
        sup[supplier, sku] += quantity
        dem[zone, sku] += quantity
        direct_load[supplier, zone] += quantity
    for (origin, destination, p), q in plan.transfers.items():
        if not valid_quantity(q, f"transfer {origin}->{destination} {p}"):
            continue
        if origin not in ds.warehouses or destination not in ds.warehouses or p not in ds.skus:
            bad.append(f"unknown transfer reference {origin}->{destination} {p}")
            continue
        if (origin, destination) not in ds.transfers:
            bad.append(f"transfer lane {origin}->{destination} is not allowed")
        if not ds.sku_allowed(origin, p) or not ds.sku_allowed(destination, p):
            bad.append(f"SKU {p} not allowed on transfer {origin}->{destination}")
        ins[destination, p] += q; outs[origin, p] += q
        cap[destination] += q * ds.skus[p].pallet_factor
        transfer_load[origin, destination] += q
        if q > tol:
            used_transfer_lanes.add((origin, destination))
    if has_transfer_cycle(used_transfer_lanes):
        bad.append("transfer flow contains a warehouse cycle")
    for lane, q in transfer_load.items():
        limit = ds.transfer_capacity.get(lane, float("inf"))
        if q > limit + tol:
            bad.append(f"transfer capacity exceeded for {lane}: {q:g} > {limit:g}")
    for lane, quantity in direct_load.items():
        limit = ds.direct_capacity.get(lane, float("inf"))
        if quantity > limit + tol:
            bad.append(f"direct capacity exceeded for {lane}: {quantity:g} > {limit:g}")
    for k, v in sup.items():
        if v > ds.supply.get(k, 0) + tol: bad.append(f"supply exceeded for {k}: {v:g} > {ds.supply.get(k, 0):g}")
    shortfall = {}
    for (z, p), q in plan.shortfall.items():
        if not valid_quantity(q, f"shortfall {z} {p}"):
            continue
        if (z, p) not in ds.demand:
            bad.append(f"unknown shortfall demand {z} {p}")
            continue
        shortfall[z, p] = q
    for k, q in ds.demand.items():
        got = dem.get(k, 0) + shortfall.get(k, 0)
        if abs(got - q) > tol: bad.append(f"demand not met for {k}: {got:g} vs {q:g}")
    for k in set(ins) | set(outs):
        if abs(ins.get(k, 0) - outs.get(k, 0)) > tol: bad.append(f"flow imbalance at {k}: in {ins.get(k,0):g}, out {outs.get(k,0):g}")
    for w, load in cap.items():
        if load > ds.warehouses[w].capacity + tol: bad.append(f"capacity exceeded at {w}: {load:g} > {ds.warehouses[w].capacity:g}")
    return bad
