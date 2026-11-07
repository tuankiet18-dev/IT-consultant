"""Plan explanations: code computes the facts, the LLM only phrases them, code checks the numbers.

Guardrails (see MVP-SPEC section 9):
1. Facts are computed here from the solver output; the LLM never calculates.
2. Every number in the LLM text must match a number in the facts (rounding allowed), otherwise the text is
   rejected and a deterministic template is used instead.
3. By default, and with no API key or on any LLM error, the deterministic summary is used, so the demo never depends on the network.
4. The text is a draft until a planner approves it (handled by the API layer).
"""
from __future__ import annotations
import json
import re
from .llm import GroqClient, LLMError
from .report import cost_breakdown, utilisation
from .schema import Dataset, Plan

CATEGORY_LABEL = {"inbound_freight": "inbound freight", "transfer_freight": "warehouse transfer freight", "direct_freight": "direct delivery freight", "inbound_handling": "inbound handling",
                  "outbound_freight": "outbound freight", "outbound_handling": "outbound handling"}


def _route_cost(ds: Dataset, w: str, z: str, p: str):
    """Best-case delivered cost of one pallet of SKU p through warehouse w to zone z (cheapest supplier)."""
    if ds.transfers or ds.direct or (w, z) not in ds.outbound:
        return None
    inb = [ds.inbound[s, w] + ds.warehouses[w].handling_in for s in ds.suppliers
           if (s, w) in ds.inbound and ds.supply.get((s, p), 0) > 0]
    if not inb:
        return None
    return round(min(inb) + ds.outbound[w, z] + ds.warehouses[w].handling_out, 6)


def _main(d: dict):
    return max(d, key=lambda k: d[k]) if d else None


def _fmt(value: float) -> str:
    return f"{value:,.6f}".rstrip("0").rstrip(".")


def build_facts(ds: Dataset, base: Plan, opt: Plan, cmp: dict, pins: list[dict] | None = None,
                unpinned_total: float | None = None, route_pins: list[dict] | None = None) -> dict:
    valid = cmp.get("baseline_valid", base.status == "BASELINE")
    changes = []
    pairs = set((z, p) for _, z, p in (*base.outbound, *opt.outbound, *base.direct, *opt.direct))
    for zone, sku in sorted(pairs) if valid else []:
        bw_sources = {w: q for (w, z, p), q in base.outbound.items() if z == zone and p == sku}
        ow_sources = {w: q for (w, z, p), q in opt.outbound.items() if z == zone and p == sku}
        bd_sources = {s: q for (s, z, p), q in base.direct.items() if z == zone and p == sku}
        od_sources = {s: q for (s, z, p), q in opt.direct.items() if z == zone and p == sku}
        if bw_sources == ow_sources and bd_sources == od_sources:
            continue
        moved = round(sum(max(q - bw_sources.get(w, 0), 0) for w, q in ow_sources.items())
                      + sum(max(q - bd_sources.get(s, 0), 0) for s, q in od_sources.items()), 6)
        preferred = ds.warehouses.get(ds.zones[zone].preferred_warehouse)
        changes.append({
            "zone": ds.zones[zone].name, "sku": ds.skus[sku].name, "pallets": moved,
            "baseline_from": [{"warehouse": ds.warehouses[w].name, "pallets": q} for w, q in sorted(bw_sources.items())],
            "optimised_from": [{"warehouse": ds.warehouses[w].name, "pallets": q} for w, q in sorted(ow_sources.items())],
            "baseline_direct_from": [{"supplier": ds.suppliers[s].name, "pallets": q} for s, q in sorted(bd_sources.items())],
            "optimised_direct_from": [{"supplier": ds.suppliers[s].name, "pallets": q} for s, q in sorted(od_sources.items())],
            "zone_preferred_warehouse": preferred.name if preferred else None,
        })
        bw, ow = _main(bw_sources), _main(ow_sources)
        bc = _route_cost(ds, bw, zone, sku) if bw else None
        oc = _route_cost(ds, ow, zone, sku) if ow else None
        if bc is not None and oc is not None:
            changes[-1].update({"baseline_route_cost_per_pallet": bc, "optimised_route_cost_per_pallet": oc,
                                "route_cost_difference_per_pallet": round(bc - oc, 6)})
    changes.sort(key=lambda c: -c["pallets"])
    cb, co = cmp["baseline"], cmp["optimised"]
    baseline_load = {warehouse: 0.0 for warehouse in ds.warehouses}
    for (_, warehouse, sku), quantity in list(base.inbound.items()) + list(base.transfers.items()):
        baseline_load[warehouse] += quantity * ds.skus[sku].pallet_factor
    facts = {
        "currency": "cost units",
        "how_to_read": "warehouse route figures are cheapest-supplier estimates where present; transfer movements are individual legs; direct movements go supplier-to-customer without warehouse handling",
        "baseline_rule": "prefer each zone's assigned final warehouse, then others by outbound rate, using available supplier paths; use declared direct supplier-to-zone routes for remaining demand, within all supply and capacity limits",
        "total_demand_pallets": round(sum(ds.demand.values()), 6),
        "total_weekly_capacity": round(sum(w.capacity for w in ds.warehouses.values()), 6),
        "mode": opt.mode, "solver_status": opt.status,
        "network": {"suppliers": len(ds.suppliers), "warehouses": len(ds.warehouses),
                    "zones": len(ds.zones), "skus": len(ds.skus)},
        "baseline_valid": valid,
        "baseline_total": cb["total"] if valid else None, "optimised_total": co["total"],
        "saving": cmp["saving"] if valid else None, "saving_percent": round(cmp["saving_pct"], 1) if valid else None,
        "cost_change_by_type": {label: round(co.get(key, 0) - cb.get(key, 0), 6) for key, label in CATEGORY_LABEL.items()} if valid else {},
        "decisions_changed": len(changes) if valid else None,
        "largest_changes": changes[:6],
        "transfer_movements": [
            {"from_warehouse": ds.warehouses[a].name, "to_warehouse": ds.warehouses[b].name,
             "sku": ds.skus[sku].name, "pallets": quantity}
            for (a, b, sku), quantity in sorted(opt.transfers.items())
        ],
        "transfer_pallet_legs": round(sum(opt.transfers.values()), 6),
        "direct_movements": [{"supplier": ds.suppliers[s].name, "zone": ds.zones[z].name,
                              "sku": ds.skus[p].name, "pallets": q}
                             for (s, z, p), q in sorted(opt.direct.items())],
        "direct_pallets": round(sum(opt.direct.values()), 6),
        "delivered_pallets": round(sum(opt.direct.values()) + sum(opt.outbound.values()), 6),
        "warehouse_load_percent": {
            ds.warehouses[w].name: {"baseline": round(cmp["utilisation_baseline"][w] * 100, 4) if valid else None,
                                    "optimised": round(cmp["utilisation_optimised"][w] * 100, 4)}
            for w in ds.warehouses},
        "warehouses_at_capacity": [ds.warehouses[w].name for w in cmp["binding_warehouses"]],
        "warehouses_full_in_baseline": [w.name for w in ds.warehouses.values()
                                       if w.capacity > 0 and abs(baseline_load[w.id] - w.capacity) <= 1e-6] if valid else [],
    }
    if pins:
        facts["planner_pins"] = [{"zone": ds.zones[p["zone"]].name, "sku": ds.skus[p["sku"]].name,
                                  "warehouse": ds.warehouses[p["warehouse"]].name, "pallets": p["pallets"]} for p in pins]
    if route_pins:
        facts["planner_routes"] = [{"supplier": ds.suppliers[route["supplier"]].name,
                                   "warehouses": [ds.warehouses[warehouse].name for warehouse in route["warehouses"]],
                                   "zone": ds.zones[route["zone"]].name, "sku": ds.skus[route["sku"]].name,
                                   "pallets": route["pallets"]} for route in route_pins]
    if (pins or route_pins) and unpinned_total is not None:
        facts["cost_of_pins"] = round(co["total"] - unpinned_total, 6)
    return facts


def template_text(f: dict) -> str:
    baseline_label = "direct-delivery baseline" if f["network"]["warehouses"] == 0 and f.get("direct_pallets", 0) else "preferred-warehouse baseline"
    if f.get("baseline_valid", True):
        difference = (f"an additional cost of {_fmt(abs(f['saving']))}" if f["saving"] < 0
                      else f"a saving of {_fmt(f['saving'])}")
        parts = [f"The optimised plan costs {_fmt(f['optimised_total'])} {f['currency']} against {_fmt(f['baseline_total'])} for the "
                 f"{baseline_label}, {difference} ({_fmt(abs(f['saving_percent']))}%). Solver status is {f['solver_status']}."]
    else:
        parts = [f"The optimised plan costs {_fmt(f['optimised_total'])} {f['currency']}. The preferred-warehouse baseline could not serve all "
                 f"demand, so no saving is reported. Solver status is {f['solver_status']}."]
    drivers = sorted(f["cost_change_by_type"].items(), key=lambda kv: kv[1])
    cuts = [(k, v) for k, v in drivers if v < 0] if f.get("baseline_valid", True) else []
    if cuts:
        k, v = cuts[0]
        parts.append(f"The largest reduction is in {k} ({_fmt(abs(v))}).")
    if f["decisions_changed"]:
        c = f["largest_changes"][0]
        was = ", ".join([*(f"{_fmt(x['pallets'])} pallets from {x['warehouse']}" for x in c["baseline_from"]),
                         *(f"{_fmt(x['pallets'])} pallets directly from {x['supplier']}" for x in c.get("baseline_direct_from", []))]) or "nothing"
        now = ", ".join([*(f"{_fmt(x['pallets'])} pallets from {x['warehouse']}" for x in c["optimised_from"]),
                         *(f"{_fmt(x['pallets'])} pallets directly from {x['supplier']}" for x in c.get("optimised_direct_from", []))]) or "nothing"
        parts.append(f"{f['decisions_changed']} zone-and-SKU allocations differ from the baseline. The largest reassignment is {_fmt(c['pallets'])} pallets of {c['sku']} "
                     f"for {c['zone']}. The baseline used {was}. The optimised plan uses {now}.")
    elif f.get("baseline_valid", True):
        parts.append("The final deliveries match the baseline." if f.get("direct_pallets", 0) else "The final warehouse allocations match the baseline.")
    for movement in f.get("direct_movements", [])[:6]:
        parts.append(f"Deliver {_fmt(movement['pallets'])} pallets of {movement['sku']} directly "
                     f"from {movement['supplier']} to {movement['zone']}, without warehouse handling.")
    for movement in f.get("transfer_movements", [])[:6]:
        parts.append(f"Transfer {_fmt(movement['pallets'])} pallets of {movement['sku']} "
                     f"from {movement['from_warehouse']} to {movement['to_warehouse']}.")
    if f["warehouses_at_capacity"]:
        parts.append("Warehouses at full capacity include " + ", ".join(f["warehouses_at_capacity"]) + ".")
    if f.get("planner_pins"):
        parts.append(f"The plan includes {len(f['planner_pins'])} final-delivery decision(s) fixed by hand.")
    for route in f.get("planner_routes", []):
        path = " to ".join([route["supplier"], *route["warehouses"], route["zone"]])
        parts.append(f"The planner reserved {_fmt(route['pallets'])} pallets of {route['sku']} along {path}.")
    if "cost_of_pins" in f:
        parts.append(f"The cost difference from the original plan is {_fmt(f['cost_of_pins'])}.")
    parts.append("A planner should review this before approving.")
    return " ".join(parts)


_ID = re.compile(r"\b[A-Za-z]+[-_]\d+\b|\b[A-Z]{1,3}\d+\b")          # SKU-07, Z3, WA2 are identifiers, not quantities
_NUM = re.compile(r"(?<![\w.])\d[\d,]*(?:\.\d+)?")


def _leaf_numbers(x, out: set):
    if isinstance(x, bool):
        return
    if isinstance(x, (int, float)):
        out.add(abs(float(x)))      # the text regex reads magnitudes, so signs are dropped
    elif isinstance(x, str):
        for m in _NUM.findall(x):
            try: out.add(float(m.replace(",", "")))
            except ValueError: pass
    elif isinstance(x, dict):
        for k, v in x.items():
            _leaf_numbers(k, out); _leaf_numbers(v, out)
    elif isinstance(x, (list, tuple)):
        for v in x:
            _leaf_numbers(v, out)


_SPACES = "".join(map(chr, (0x202F, 0x00A0, 0x2009, 0x2007, 0x2060)))   # narrow no-break, no-break, thin, figure space, word joiner


def clean_text(text: str) -> str:
    """Models often write 32 698 with a no-break space; turn digit groups into 32,698 and other odd spaces into plain ones."""
    text = re.sub(rf"(?<=\d)[{_SPACES}](?=\d{{3}}(?!\d))", ",", text)
    text = re.sub(rf"[{_SPACES}]", " ", text)
    return text.replace(chr(0x2011), "-").replace(chr(0x2212), "-").strip()


def check_numbers(text: str, facts: dict) -> list[str]:
    """Return the numbers in text that are not in the facts (empty list = all numbers are supported)."""
    allowed: set[float] = set()
    _leaf_numbers(facts, allowed)
    unmatched = []
    for m in _NUM.findall(_ID.sub(" ", text)):
        s = m.rstrip(",").replace(",", "")
        if not s:
            continue
        dec = len(s.split(".")[1]) if "." in s else 0
        tol = 0.5 * 10 ** (-dec) + 1e-9
        if not any(abs(float(s) - v) <= tol for v in allowed):
            unmatched.append(m)
    return unmatched


SYSTEM = (
    "You are explaining a warehouse allocation result to a logistics planner who must decide whether to approve it. "
    "Write in plain English, in three short paragraphs separated by a blank line, 160 to 230 words in total, no headings, "
    "no bullet points.\n"
    "Paragraph 1 - the result: the optimised cost against the preferred-warehouse baseline, the saving and its percentage, "
    "and a brief description of the baseline_rule.\n"
    "Paragraph 2 - why: which cost types went down or up (cost_change_by_type) and what moved. Use largest_changes: say which "
    "warehouse served the zone and SKU before and after, and explain the move with the route cost per pallet figures and "
    "route_cost_difference_per_pallet as cheapest-supplier estimates. Describe warehouses_full_in_baseline and warehouses_at_capacity "
    "as capacity observations. Describe transfer_movements as individual warehouse-to-warehouse legs. "
    "Describe direct_movements as supplier-to-customer deliveries that do not visit a warehouse or pay warehouse handling. "
    "largest_changes can include baseline_direct_from or optimised_direct_from suppliers alongside final warehouses; "
    "do not describe a direct supplier as a warehouse. "
    "transfer_pallet_legs counts visits across legs, so one pallet can appear more than once. "
    "If baseline_valid is false, omit all savings, cost-change and reassignment comparisons.\n"
    "Paragraph 3 - what to check: any planner decisions, capacity constraints, and what the planner should review "
    "before approving. planner_routes reserves quantities along complete ordered paths. "
    "cost_of_pins compares the full plan with its original unpinned reference. "
    "Do not invent a discount or business benefit from a planner choice.\n"
    "Rules: use ONLY the numbers and names in the JSON facts. Never calculate, add up, estimate or invent numbers, "
    "percentages, causes or names. Do not give a reason that the facts do not support; if a move has no route cost figures, "
    "just describe it. Refer to warehouses, zones and SKUs by name. Preserve supplied precision for costs and quantities.")


def explain(facts: dict, client: GroqClient | None = None, use_llm: bool = True) -> dict:
    tmpl = template_text(facts)
    if not use_llm:
        return {"text": tmpl, "source": "deterministic", "reason": None, "unsupported_numbers": []}
    client = client or GroqClient()
    if not client.enabled:
        return {"text": tmpl, "source": "deterministic", "reason": "no LLM key configured", "unsupported_numbers": []}
    try:
        text = client.chat([{"role": "system", "content": SYSTEM},
                            {"role": "user", "content": "Facts (JSON):\n" + json.dumps(facts, indent=1)}])
    except LLMError as e:
        return {"text": tmpl, "source": "deterministic", "reason": str(e), "unsupported_numbers": []}
    text = clean_text(text)
    bad = check_numbers(text, facts)
    if bad:
        return {"text": tmpl, "source": "deterministic", "reason": "LLM text rejected: numbers not in facts " + ", ".join(bad),
                "unsupported_numbers": bad}
    return {"text": text, "source": f"groq:{client.model}", "reason": None, "unsupported_numbers": []}
