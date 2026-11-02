"""Synthetic demo data: one Swedish region, 2 suppliers, 3 warehouses, 6 zones, 20 SKUs.

Everything here is invented for demonstration. Costs and capacities are chosen so that
the 'habit' baseline overloads the warehouse preferred by most zones, as the Round 1
hypothesis describes. The resulting saving is an artefact of this data, not a forecast.
"""
from __future__ import annotations
import csv
import random
from pathlib import Path

ZONES = [("Z1", "Zone 1", "WA"), ("Z2", "Zone 2", "WA"), ("Z3", "Zone 3", "WA"),
         ("Z4", "Zone 4", "WB"), ("Z5", "Zone 5", "WB"), ("Z6", "Zone 6", "WC")]
CATEGORIES = ["Cement", "Plasterboard", "Insulation", "Timber", "Roofing sheet",
              "Bricks", "Mortar", "Tile adhesive", "Drywall screws", "Paint pail"]


def generate(folder: str | Path, seed: int = 7) -> Path:
    rnd = random.Random(seed)
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)

    def write(name, header, rows):
        with (folder / name).open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f); w.writerow(header); w.writerows(rows)

    skus = [(f"SKU-{i:02d}", f"{CATEGORIES[(i - 1) % 10]} {'standard' if i <= 10 else 'large'}",
             1 if i <= 10 else 2) for i in range(1, 21)]
    demand = {(z[0], s[0]): rnd.choice([0, 0, 2, 4, 6, 8, 10, 12]) for z in ZONES for s in skus}
    total = {s[0]: sum(demand[z[0], s[0]] for z in ZONES) for s in skus}
    for s in skus:                                      # every SKU is wanted somewhere
        if total[s[0]] == 0:
            demand["Z1", s[0]] = 4; total[s[0]] = 4
    supply = [(sup, s[0], int(total[s[0]] * rnd.uniform(0.75, 0.95)) + 2) for sup in ("SUP1", "SUP2") for s in skus]

    need_cap = {w: sum(q * (2 if int(p[4:]) > 10 else 1) for (z, p), q in demand.items()
                       if dict((zz[0], zz[2]) for zz in ZONES)[z] == w) for w in ("WA", "WB", "WC")}
    grand = sum(need_cap.values())
    capacity = {"WA": int(grand * 0.30), "WB": int(grand * 0.38), "WC": int(grand * 0.38)}

    write("suppliers.csv", ["supplier_id", "name"], [("SUP1", "Supplier 1"), ("SUP2", "Supplier 2")])
    write("warehouses.csv", ["warehouse_id", "name", "capacity_pallets", "handling_in", "handling_out"],
          [("WA", "Warehouse A", capacity["WA"], 4, 4), ("WB", "Warehouse B", capacity["WB"], 5, 5),
           ("WC", "Warehouse C", capacity["WC"], 3, 3)])
    write("zones.csv", ["zone_id", "name", "preferred_warehouse"], ZONES)
    write("skus.csv", ["sku_id", "name", "pallet_factor"], skus)
    # Warehouses nearest to most zones (WA) are far from both suppliers, so the habit rule pays
    # high inbound freight; this is the Round 1 hypothesis, built into the demo data on purpose.
    inbound = {("SUP1", "WA"): 44, ("SUP1", "WB"): 26, ("SUP1", "WC"): 16,
               ("SUP2", "WA"): 48, ("SUP2", "WB"): 24, ("SUP2", "WC"): 18}
    write("inbound_rates.csv", ["supplier_id", "warehouse_id", "cost_per_pallet"],
          [(s, w, c) for (s, w), c in inbound.items()])
    dist = {"WA": [14, 18, 22, 30, 36, 40], "WB": [34, 28, 22, 16, 20, 28], "WC": [40, 36, 32, 26, 20, 14]}
    write("outbound_rates.csv", ["warehouse_id", "zone_id", "cost_per_pallet"],
          [(w, ZONES[i][0], dist[w][i]) for w in dist for i in range(6)])
    write("supply.csv", ["supplier_id", "sku_id", "max_pallets"], supply)
    write("demand.csv", ["zone_id", "sku_id", "pallets"],
          [(z, p, q) for (z, p), q in demand.items() if q > 0])
    return folder
