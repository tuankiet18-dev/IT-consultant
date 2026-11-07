"""What-if scenario changes applied to a copy of a dataset."""
from __future__ import annotations
import copy
import math
from .schema import Dataset, Warehouse


class ChangeError(ValueError):
    pass


def apply_changes(ds: Dataset, changes: list[dict]) -> Dataset:
    """Supported changes:
    {"type": "close_warehouse", "warehouse": "WA"}
    {"type": "set_capacity", "warehouse": "WA", "capacity": 200}
    {"type": "scale_demand", "zone": "Z1", "factor": 1.2}          # rounded up to whole pallets
    {"type": "set_rate", "kind": "inbound"|"outbound"|"transfer"|"direct", "from": "SUP1", "to": "WA", "cost": 50}
    """
    new = copy.deepcopy(ds)
    for c in changes:
        t = c.get("type")
        if t in ("close_warehouse", "set_capacity"):
            w = new.warehouses.get(c.get("warehouse"))
            if w is None:
                raise ChangeError(f"unknown warehouse {c.get('warehouse')!r}")
            cap = 0.0 if t == "close_warehouse" else float(c.get("capacity", -1))
            if not math.isfinite(cap) or cap < 0:
                raise ChangeError("capacity must be finite and >= 0")
            new.warehouses[w.id] = Warehouse(w.id, w.name, cap, w.handling_in, w.handling_out)
        elif t == "scale_demand":
            z, f = c.get("zone"), float(c.get("factor", -1))
            if z not in new.zones:
                raise ChangeError(f"unknown zone {z!r}")
            if not math.isfinite(f) or f < 0:
                raise ChangeError("factor must be finite and >= 0")
            for key in [k for k in new.demand if k[0] == z]:
                new.demand[key] = math.ceil(new.demand[key] * f - 1e-9)
        elif t == "set_rate":
            kind, a, b, cost = c.get("kind"), c.get("from"), c.get("to"), float(c.get("cost", -1))
            store = {"inbound": new.inbound, "outbound": new.outbound, "transfer": new.transfers, "direct": new.direct}.get(kind)
            if store is None or (a, b) not in store:
                raise ChangeError(f"no {kind} lane {a!r}->{b!r}")
            if not math.isfinite(cost) or cost < 0:
                raise ChangeError("cost must be finite and >= 0")
            store[(a, b)] = cost
        else:
            raise ChangeError(f"unknown change type {t!r}")
    return new


def describe(changes: list[dict], ds: Dataset) -> str:
    parts = []
    for c in changes:
        t = c["type"]
        if t == "close_warehouse":
            parts.append(f"close {ds.warehouses[c['warehouse']].name}")
        elif t == "set_capacity":
            parts.append(f"set {ds.warehouses[c['warehouse']].name} capacity to {c['capacity']:g}")
        elif t == "scale_demand":
            parts.append(f"scale demand of {ds.zones[c['zone']].name} by x{c['factor']:g}")
        elif t == "set_rate":
            parts.append(f"set {c['kind']} rate {c['from']}->{c['to']} to {c['cost']:g}")
    return "; ".join(parts) or "no change"
