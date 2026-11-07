"""CSV loading with row-level error reporting (no silent fixes)."""
from __future__ import annotations
import csv
from pathlib import Path
from .schema import Dataset, Issue, Supplier, Warehouse, Zone, Sku

REQUIRED = {
    "suppliers.csv": ["supplier_id", "name"],
    "warehouses.csv": ["warehouse_id", "name", "capacity_pallets", "handling_in", "handling_out"],
    "zones.csv": ["zone_id", "name", "preferred_warehouse"],
    "skus.csv": ["sku_id", "name", "pallet_factor"],
    "inbound_rates.csv": ["supplier_id", "warehouse_id", "cost_per_pallet"],
    "outbound_rates.csv": ["warehouse_id", "zone_id", "cost_per_pallet"],
    "supply.csv": ["supplier_id", "sku_id", "max_pallets"],
    "demand.csv": ["zone_id", "sku_id", "pallets"],
}
OPTIONAL = {
    "warehouse_skus.csv": ["warehouse_id", "sku_id"],
    "transfer_rates.csv": ["from_warehouse_id", "to_warehouse_id", "cost_per_pallet"],
    "direct_rates.csv": ["supplier_id", "zone_id", "cost_per_pallet"],
}


def _num(v: str, file: str, row: int, col: str, issues: list[Issue], minimum: float = 0.0):
    try:
        x = float(v)
    except (TypeError, ValueError):
        issues.append(Issue("error", file, row, f"'{col}' must be a number, got {v!r}"))
        return None
    if x != x or x in (float("inf"), float("-inf")):
        issues.append(Issue("error", file, row, f"'{col}' must be finite"))
        return None
    if x < minimum:
        issues.append(Issue("error", file, row, f"'{col}' must be >= {minimum}, got {x}"))
        return None
    return x


def _rows(path: Path, columns: list[str], issues: list[Issue]):
    name = path.name
    if not path.exists():
        issues.append(Issue("error", name, None, "file is missing"))
        return
    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        missing = [c for c in columns if c not in (reader.fieldnames or [])]
        if missing:
            issues.append(Issue("error", name, None, f"missing column(s): {', '.join(missing)}"))
            return
        for i, row in enumerate(reader, start=2):  # header is row 1
            if None in row or any(value is None for value in row.values()):
                issues.append(Issue("error", name, i, "row must have the same number of fields as the header"))
                continue
            yield i, {k: (v or "").strip() for k, v in row.items()}


def load_dataset(folder: str | Path) -> tuple[Dataset, list[Issue]]:
    folder = Path(folder)
    ds, issues = Dataset(), []

    def dup(key, store, file, row):
        if key in store:
            issues.append(Issue("error", file, row, f"duplicate key {key}"))
            return True
        return False

    for i, r in _rows(folder / "suppliers.csv", REQUIRED["suppliers.csv"], issues) or []:
        if not r["supplier_id"]:
            issues.append(Issue("error", "suppliers.csv", i, "supplier_id is empty")); continue
        if not dup(r["supplier_id"], ds.suppliers, "suppliers.csv", i):
            ds.suppliers[r["supplier_id"]] = Supplier(r["supplier_id"], r["name"])
    for i, r in _rows(folder / "warehouses.csv", REQUIRED["warehouses.csv"], issues) or []:
        cap = _num(r["capacity_pallets"], "warehouses.csv", i, "capacity_pallets", issues)
        hi = _num(r["handling_in"], "warehouses.csv", i, "handling_in", issues)
        ho = _num(r["handling_out"], "warehouses.csv", i, "handling_out", issues)
        if None in (cap, hi, ho) or not r["warehouse_id"]:
            continue
        if not dup(r["warehouse_id"], ds.warehouses, "warehouses.csv", i):
            ds.warehouses[r["warehouse_id"]] = Warehouse(r["warehouse_id"], r["name"], cap, hi, ho)
    for i, r in _rows(folder / "zones.csv", REQUIRED["zones.csv"], issues) or []:
        if not r["zone_id"]:
            issues.append(Issue("error", "zones.csv", i, "zone_id is empty")); continue
        if not dup(r["zone_id"], ds.zones, "zones.csv", i):
            ds.zones[r["zone_id"]] = Zone(r["zone_id"], r["name"], r["preferred_warehouse"])
    for i, r in _rows(folder / "skus.csv", REQUIRED["skus.csv"], issues) or []:
        pf = _num(r["pallet_factor"], "skus.csv", i, "pallet_factor", issues)
        if pf is None or not r["sku_id"]:
            continue
        if pf <= 0:
            issues.append(Issue("error", "skus.csv", i, "pallet_factor must be > 0")); continue
        if not dup(r["sku_id"], ds.skus, "skus.csv", i):
            ds.skus[r["sku_id"]] = Sku(r["sku_id"], r["name"], pf)

    def pairs(file, a, b, val, store, minimum=0.0):
        for i, r in _rows(folder / file, REQUIRED[file], issues) or []:
            x = _num(r[val], file, i, val, issues, minimum)
            if x is None:
                continue
            key = (r[a], r[b])
            if not dup(key, store, file, i):
                store[key] = x

    pairs("inbound_rates.csv", "supplier_id", "warehouse_id", "cost_per_pallet", ds.inbound)
    pairs("outbound_rates.csv", "warehouse_id", "zone_id", "cost_per_pallet", ds.outbound)
    pairs("supply.csv", "supplier_id", "sku_id", "max_pallets", ds.supply)
    pairs("demand.csv", "zone_id", "sku_id", "pallets", ds.demand)

    transfers = folder / "transfer_rates.csv"
    if transfers.exists():
        for i, r in _rows(transfers, OPTIONAL[transfers.name], issues) or []:
            cost = _num(r["cost_per_pallet"], transfers.name, i, "cost_per_pallet", issues)
            key = (r["from_warehouse_id"], r["to_warehouse_id"])
            if cost is None or dup(key, ds.transfers, transfers.name, i):
                continue
            ds.transfers[key] = cost
            if r.get("max_pallets"):
                cap = _num(r["max_pallets"], transfers.name, i, "max_pallets", issues)
                if cap is not None:
                    ds.transfer_capacity[key] = cap

    direct = folder / "direct_rates.csv"
    if direct.exists():
        for i, r in _rows(direct, OPTIONAL[direct.name], issues) or []:
            cost = _num(r["cost_per_pallet"], direct.name, i, "cost_per_pallet", issues)
            key = (r["supplier_id"], r["zone_id"])
            if cost is None or dup(key, ds.direct, direct.name, i):
                continue
            ds.direct[key] = cost
            if r.get("max_pallets"):
                cap = _num(r["max_pallets"], direct.name, i, "max_pallets", issues)
                if cap is not None:
                    ds.direct_capacity[key] = cap

    elig = folder / "warehouse_skus.csv"
    if elig.exists():
        ds.eligible = {w: set() for w in ds.warehouses}
        for i, r in _rows(elig, OPTIONAL["warehouse_skus.csv"], issues) or []:
            ds.eligible.setdefault(r["warehouse_id"], set()).add(r["sku_id"])
    return ds, issues
