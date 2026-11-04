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

CATEGORY_LABEL = {"inbound_freight": "inbound freight", "inbound_handling": "inbound handling",
                  "outbound_freight": "outbound freight", "outbound_handling": "outbound handling"}


def _route_cost(ds: Dataset, w: str, z: str, p: str):
    """Best-case delivered cost of one pallet of SKU p through warehouse w to zone z (cheapest supplier)."""
    if (w, z) not in ds.outbound:
        return None
    inb = [ds.inbound[s, w] + ds.warehouses[w].handling_in for s in ds.suppliers
           if (s, w) in ds.inbound and ds.supply.get((s, p), 0) > 0]
    if not inb:
        return None
    return round(min(inb) + ds.outbound[w, z] + ds.warehouses[w].handling_out, 1)


def _main(d: dict):
    return max(d, key=lambda k: d[k]) if d else None


def build_facts(ds: Dataset, base: Plan, opt: Plan, cmp: dict, pins: list[dict] | None = None,
                unpinned_total: float | None = None) -> dict:
    changes = []
    for ch in cmp["changes"]:
        moved = sum(ch["optimised"].values())
        changes.append({
            "zone": ds.zones[ch["zone"]].name, "sku": ds.skus[ch["sku"]].name, "pallets": moved,
            "baseline_from": [{"warehouse": ds.warehouses[w].name, "pallets": q} for w, q in sorted(ch["baseline"].items())],
            "optimised_from": [{"warehouse": ds.warehouses[w].name, "pallets": q} for w, q in sorted(ch["optimised"].items())],
            "zone_preferred_warehouse": ds.warehouses[ds.zones[ch["zone"]].preferred_warehouse].name,
        })
        bw, ow = _main(ch["baseline"]), _main(ch["optimised"])
        bc = _route_cost(ds, bw, ch["zone"], ch["sku"]) if bw else None
        oc = _route_cost(ds, ow, ch["zone"], ch["sku"]) if ow else None
        if bc is not None and oc is not None:
            changes[-1].update({"baseline_route_cost_per_pallet": bc, "optimised_route_cost_per_pallet": oc,
                                "route_cost_difference_per_pallet": round(bc - oc, 1)})
    changes.sort(key=lambda c: -c["pallets"])
    cb, co = cmp["baseline"], cmp["optimised"]
    valid = cmp.get("baseline_valid", True)
    facts = {
        "currency": "cost units",
        "how_to_read": "route cost per pallet = cheapest supplier to the warehouse + handling in + warehouse to zone + handling out",
        "baseline_rule": "each zone is served from its preferred warehouse; if that warehouse is full, the next cheapest warehouse is used",
        "total_demand_pallets": round(sum(ds.demand.values())),
        "total_weekly_capacity": round(sum(w.capacity for w in ds.warehouses.values())),
        "mode": opt.mode, "solver_status": opt.status,
        "network": {"suppliers": len(ds.suppliers), "warehouses": len(ds.warehouses),
                    "zones": len(ds.zones), "skus": len(ds.skus)},
        "baseline_valid": valid,
        "baseline_total": round(cb["total"]) if valid else None, "optimised_total": round(co["total"]),
        "saving": round(cmp["saving"]) if valid else None, "saving_percent": round(cmp["saving_pct"], 1) if valid else None,
        "cost_change_by_type": {CATEGORY_LABEL[k]: round(co[k] - cb[k]) for k in CATEGORY_LABEL},
        "decisions_changed": len(cmp["changes"]),
        "largest_changes": changes[:6],
        "warehouse_load_percent": {
            ds.warehouses[w].name: {"baseline": round(cmp["utilisation_baseline"][w] * 100),
                                    "optimised": round(cmp["utilisation_optimised"][w] * 100)}
            for w in ds.warehouses},
        "warehouses_at_capacity": [ds.warehouses[w].name for w in cmp["binding_warehouses"]],
        "warehouses_full_in_baseline": [ds.warehouses[w].name for w in ds.warehouses if cmp["utilisation_baseline"][w] >= 0.995],
    }
    if pins:
        facts["planner_pins"] = [{"zone": ds.zones[p["zone"]].name, "sku": ds.skus[p["sku"]].name,
                                  "warehouse": ds.warehouses[p["warehouse"]].name, "pallets": p["pallets"]} for p in pins]
        if unpinned_total is not None:
            facts["cost_of_pins"] = round(co["total"] - unpinned_total)
    return facts


def template_text(f: dict) -> str:
    if f.get("baseline_valid", True):
        parts = [f"The optimised plan costs {f['optimised_total']:,} {f['currency']} against {f['baseline_total']:,} for the "
                 f"preferred-warehouse baseline (a synthetic rule, not Company A's actual plan), a saving of {f['saving']:,} ({f['saving_percent']}%). Solver status: {f['solver_status']}."]
    else:
        parts = [f"The optimised plan costs {f['optimised_total']:,} {f['currency']}. The preferred-warehouse baseline could not serve all "
                 f"demand, so no saving is reported. Solver status: {f['solver_status']}."]
    drivers = sorted(f["cost_change_by_type"].items(), key=lambda kv: kv[1])
    cuts = [(k, v) for k, v in drivers if v < 0] if f.get("baseline_valid", True) else []
    if cuts:
        k, v = cuts[0]
        parts.append(f"The largest reduction is in {k} ({abs(v):,}).")
    if f["decisions_changed"]:
        c = f["largest_changes"][0]
        was = ", ".join(f"{x['pallets']:g} pallets from {x['warehouse']}" for x in c["baseline_from"]) or "nothing"
        now = ", ".join(f"{x['pallets']:g} pallets from {x['warehouse']}" for x in c["optimised_from"])
        parts.append(f"{f['decisions_changed']} zone-and-SKU decisions differ from the baseline. The largest is {c['sku']} "
                     f"for {c['zone']}: the baseline used {was}; the optimised plan uses {now}.")
    else:
        parts.append("No zone-and-SKU decision differs from the baseline.")
    if f["warehouses_at_capacity"]:
        parts.append("At full capacity in the optimised plan: " + ", ".join(f["warehouses_at_capacity"]) + ".")
    if f.get("planner_pins"):
        parts.append(f"The plan includes {len(f['planner_pins'])} planner decision(s) fixed by hand" +
                     (f", costing {f['cost_of_pins']:,} more than the unconstrained optimum." if "cost_of_pins" in f else "."))
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
    "and that the baseline is a synthetic rule (see baseline_rule), not Company A's actual plan.\n"
    "Paragraph 2 - why: which cost types went down or up (cost_change_by_type) and what moved. Use largest_changes: say which "
    "warehouse served the zone and SKU before and after, and explain the move with the route cost per pallet figures and "
    "route_cost_difference_per_pallet. Mention warehouses_full_in_baseline when it explains a move, and warehouses_at_capacity "
    "as a limit on further savings.\n"
    "Paragraph 3 - what to check: that the data is synthetic, any planner decisions, and that the planner should review "
    "before approving.\n"
    "Rules: use ONLY the numbers and names in the JSON facts. Never calculate, add up, estimate or invent numbers, "
    "percentages, causes or names. Do not give a reason that the facts do not support; if a move has no route cost figures, "
    "just describe it. Refer to warehouses, zones and SKUs by name. Write numbers without extra decimals.")


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
