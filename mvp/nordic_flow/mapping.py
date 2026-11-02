"""SKU mapping suggestions for catalogs that use different codes or names.

Step 1 is deterministic fuzzy matching. Step 2 (optional) asks the LLM to pick among the candidates already
found by step 1; its answer is ignored unless it names one of those candidates. Nothing is applied until a
planner confirms it in the UI.
"""
from __future__ import annotations
import difflib
import json
import re
from .llm import GroqClient, LLMError
from .schema import Dataset

_SPLIT = re.compile(r"(\d+(?:\.\d+)?)\s*([a-zA-Z]+)")


def _tokens(s: str) -> set[str]:
    s = _SPLIT.sub(r"\1 \2", s.lower())
    return {t for t in re.split(r"[^a-z0-9.]+", s) if t}


def score(a: str, b: str) -> float:
    ta, tb = _tokens(a), _tokens(b)
    jac = len(ta & tb) / len(ta | tb) if ta | tb else 0.0
    seq = difflib.SequenceMatcher(None, " ".join(sorted(ta)), " ".join(sorted(tb))).ratio()
    return round(0.6 * jac + 0.4 * seq, 3)


def suggest(external: list[dict], ds: Dataset, top_k: int = 3, client: GroqClient | None = None) -> list[dict]:
    out = []
    for row in external:
        label = f"{row.get('code', '')} {row.get('name', '')}".strip()
        cands = sorted(({"sku_id": s.id, "name": s.name, "confidence": score(label, s.name)} for s in ds.skus.values()),
                       key=lambda c: -c["confidence"])[:top_k]
        item = {"external": row, "candidates": cands, "llm_pick": None,
                "needs_review": not cands or cands[0]["confidence"] < 0.75}
        if client and client.enabled and cands:
            item["llm_pick"] = _llm_pick(client, label, cands)
        out.append(item)
    return out


def _llm_pick(client: GroqClient, label: str, cands: list[dict]) -> dict | None:
    prompt = ("Pick the catalogue item that is the same product as the external item. Answer with JSON only: "
              '{"sku_id": "<id from candidates or null>", "reason": "<short>"}.\n'
              f"External item: {label}\nCandidates: {json.dumps(cands)}")
    try:
        raw = client.chat([{"role": "user", "content": prompt}], temperature=0.0, max_tokens=120)
        data = json.loads(raw[raw.index("{"): raw.rindex("}") + 1])
    except (LLMError, ValueError, json.JSONDecodeError):
        return None
    return data if data.get("sku_id") in {c["sku_id"] for c in cands} else None
