"""Use cases: scenarios, runs, overrides, what-if, explanations, approvals, export."""
from __future__ import annotations
import csv
import io
import json
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from nordic_flow.baseline import baseline
from nordic_flow.diagnosis import diagnose
from nordic_flow.explain import build_facts, explain
from nordic_flow.io import load_dataset, REQUIRED, OPTIONAL
from nordic_flow.optimiser import solve
from nordic_flow.report import compare, cost_breakdown
from nordic_flow.schema import Dataset, Plan
from nordic_flow.validation import has_errors, validate
from nordic_flow.verify import verify_plan
from nordic_flow.whatif import ChangeError, apply_changes, describe
from . import audit
from .db import Database, dumps

SAMPLES = Path(__file__).resolve().parent.parent / "data"
SAMPLE_NAMES = {"demo": "Synthetic demo (2 suppliers, 3 warehouses, 6 zones, 20 SKUs)",
                "golden": "Worked example from the Round 1 deck (baseline 700, optimum 500)"}
ALLOWED_FILES = set(REQUIRED) | set(OPTIONAL)


class ApiError(Exception):
    def __init__(self, status: int, code: str, message: str, details=None):
        self.status, self.code, self.message, self.details = status, code, message, details
        super().__init__(message)


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


MAX_ZIP_BYTES, MAX_ZIP_FILES, MAX_FILE_BYTES = 5_000_000, 12, 2_000_000


def read_zip(raw: bytes) -> dict[str, str]:
    """Safely expand an uploaded ZIP: flat allow-listed CSV names only, bounded size, no paths or links."""
    try:
        z = zipfile.ZipFile(io.BytesIO(raw))
    except zipfile.BadZipFile:
        raise ApiError(422, "bad_zip", "The uploaded file is not a valid ZIP archive.")
    infos = [i for i in z.infolist() if not i.is_dir()]
    if len(infos) > MAX_ZIP_FILES or sum(i.file_size for i in infos) > MAX_ZIP_BYTES:
        raise ApiError(422, "zip_too_large", "The ZIP has too many files or is too large.")
    out: dict[str, str] = {}
    for i in infos:
        name = i.filename
        if "/" in name or "\\" in name or ".." in name or name.startswith("."):
            raise ApiError(422, "unsafe_zip", f"Unsafe path in ZIP: {name!r}. Put the CSV files at the top level.")
        if (i.external_attr >> 16) & 0o170000 == 0o120000:
            raise ApiError(422, "unsafe_zip", f"Links are not allowed in the ZIP: {name!r}.")
        if name not in ALLOWED_FILES:
            raise ApiError(422, "unexpected_file", f"Unexpected file {name!r}; allowed: {sorted(ALLOWED_FILES)}")
        if name in out:
            raise ApiError(422, "duplicate_file", f"Duplicate file {name!r}")
        if i.file_size > MAX_FILE_BYTES:
            raise ApiError(422, "zip_too_large", f"{name} is too large")
        try:
            out[name] = z.read(i).decode("utf-8-sig")
        except UnicodeDecodeError:
            raise ApiError(422, "bad_encoding", f"{name} is not UTF-8 text")
    return out


# ---------- scenarios ----------
def _load(files: dict[str, str]) -> tuple[Dataset, list]:
    with tempfile.TemporaryDirectory() as d:
        for name, text in files.items():
            (Path(d) / name).write_text(text, encoding="utf-8")
        return load_dataset(d)


def _issue_dicts(issues) -> list[dict]:
    return [{"severity": i.severity, "file": i.file, "row": i.row, "message": i.message} for i in issues]


def create_scenario(db: Database, name: str, files: dict[str, str], source: str) -> dict:
    extra = [f for f in files if f not in ALLOWED_FILES]
    files = {k: v for k, v in files.items() if k in ALLOWED_FILES}
    ds, issues = _load(files)
    issues = list(issues) + validate(ds, "milp")
    from nordic_flow.schema import Issue
    for f in extra:
        issues.append(Issue("warning", f, None, "unrecognised file ignored"))
    issues_d = _issue_dicts(issues)
    valid = not has_errors(issues)
    sid = db.execute("INSERT INTO scenarios(created_at,name,source,files_json,issues_json,valid) VALUES(?,?,?,?,?,?)",
                     (now(), name, source, dumps(files), dumps(issues_d), int(valid)))
    audit.record(db, "SCENARIO_UPLOADED", "planner", sid, None,
                 {"name": name, "source": source, "valid": valid,
                  "errors": sum(i["severity"] == "error" for i in issues_d),
                  "warnings": sum(i["severity"] == "warning" for i in issues_d)})
    return scenario_detail(db, sid)


def create_sample(db: Database, sample: str) -> dict:
    if sample not in SAMPLE_NAMES:
        raise ApiError(404, "unknown_sample", f"unknown sample {sample!r}; choose one of {sorted(SAMPLE_NAMES)}")
    folder = SAMPLES / sample
    files = {p.name: p.read_text(encoding="utf-8") for p in folder.glob("*.csv")}
    return create_scenario(db, SAMPLE_NAMES[sample], files, f"sample:{sample}")


def _scenario_row(db: Database, sid: int):
    r = db.one("SELECT * FROM scenarios WHERE id=?", (sid,))
    if r is None:
        raise ApiError(404, "scenario_not_found", f"scenario {sid} does not exist")
    return r


def scenario_dataset(db: Database, sid: int) -> Dataset:
    return _load(json.loads(_scenario_row(db, sid)["files_json"]))[0]


def scenario_detail(db: Database, sid: int) -> dict:
    r = _scenario_row(db, sid)
    ds = scenario_dataset(db, sid)
    return {
        "id": sid, "name": r["name"], "source": r["source"], "created_at": r["created_at"], "valid": bool(r["valid"]),
        "issues": json.loads(r["issues_json"]),
        "summary": {"suppliers": len(ds.suppliers), "warehouses": len(ds.warehouses), "zones": len(ds.zones),
                    "skus": len(ds.skus), "demand_pallets": sum(ds.demand.values()),
                    "capacity_total": sum(w.capacity for w in ds.warehouses.values())},
        "entities": {
            "suppliers": {s.id: s.name for s in ds.suppliers.values()},
            "warehouses": {w.id: {"name": w.name, "capacity": w.capacity} for w in ds.warehouses.values()},
            "zones": {z.id: {"name": z.name, "preferred_warehouse": z.preferred_warehouse} for z in ds.zones.values()},
            "skus": {s.id: s.name for s in ds.skus.values()}},
    }


def list_scenarios(db: Database) -> list[dict]:
    return [{"id": r["id"], "name": r["name"], "valid": bool(r["valid"]), "created_at": r["created_at"]}
            for r in db.all("SELECT id,name,valid,created_at FROM scenarios ORDER BY id DESC")]


def _diag(ds: Dataset) -> dict:
    d = diagnose(ds)
    d["unmet_by_zone_sku"] = [{"zone": z, "sku": k, "pallets": q} for (z, k), q in sorted(d["unmet_by_zone_sku"].items())]
    return d


# ---------- plans ----------
def plan_to_json(p: Plan) -> dict:
    return {"status": p.status, "mode": p.mode, "objective": p.objective, "solve_seconds": round(p.solve_seconds, 4),
            "inbound": [{"supplier": s, "warehouse": w, "sku": k, "pallets": q} for (s, w, k), q in sorted(p.inbound.items())],
            "outbound": [{"warehouse": w, "zone": z, "sku": k, "pallets": q} for (w, z, k), q in sorted(p.outbound.items())],
            "shortfall": [{"zone": z, "sku": k, "pallets": q} for (z, k), q in sorted(p.shortfall.items())]}


def _plan_from_json(d: dict) -> Plan:
    return Plan(status=d["status"], mode=d["mode"], objective=d["objective"], solve_seconds=d["solve_seconds"],
                inbound={(r["supplier"], r["warehouse"], r["sku"]): r["pallets"] for r in d["inbound"]},
                outbound={(r["warehouse"], r["zone"], r["sku"]): r["pallets"] for r in d["outbound"]},
                shortfall={(r["zone"], r["sku"]): r["pallets"] for r in d["shortfall"]})


def _pins_dict(pins: list[dict]) -> dict:
    return {(p["warehouse"], p["zone"], p["sku"]): p["pallets"] for p in pins}


# ---------- runs ----------
def _execute(db: Database, sid: int, ds: Dataset, mode: str, time_limit: float, kind: str, pins: list[dict],
             changes: list[dict], parent: int | None, reference: int | None, optimum_total: float | None, actor: str):
    errs = [i for i in validate(ds, mode) if i.severity == "error"]
    if errs:
        raise ApiError(422, "invalid_data", "The data has errors; fix them before running.", _issue_dicts(errs))
    base = baseline(ds)
    opt = solve(ds, mode, time_limit, pins=_pins_dict(pins) if pins else None)
    if not opt.usable:
        if pins:
            raise ApiError(409, "pins_infeasible",
                           "This combination of planner decisions cannot be served within supply, capacity and lane limits.")
        raise ApiError(409, "no_feasible_plan", "No feasible plan exists for this data.", _diag(ds))
    vb, vo = verify_plan(ds, base), verify_plan(ds, opt)
    if vo:
        raise ApiError(500, "verification_failed", "The plan failed the independent constraint check.", vo)
    cmp = compare(ds, base, opt)
    cmp["baseline_valid"] = base.status == "BASELINE" and not vb
    cmp["baseline_issues"] = [] if cmp["baseline_valid"] else (vb or ["the baseline rule could not serve all demand"])
    if not cmp["baseline_valid"]:
        cmp["saving"] = cmp["saving_pct"] = None       # never report a saving against an unusable baseline
    total = cost_breakdown(ds, opt)["total"]
    if optimum_total is None:
        optimum_total = total          # first (unpinned) optimum of this scenario version
    rid = db.execute(
        "INSERT INTO runs(created_at,scenario_id,kind,parent_run_id,state,mode,status,solve_seconds,pins_json,changes_json,"
        "optimum_total,reference_run_id,baseline_json,optimised_json,comparison_json,verify_json) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (now(), sid, kind, parent, "draft", mode, opt.status, opt.solve_seconds, dumps(pins), dumps(changes),
         optimum_total, reference, dumps(plan_to_json(base)), dumps(plan_to_json(opt)), dumps(cmp),
         dumps({"baseline_violations": vb, "optimised_violations": vo})))
    return rid, opt, cmp


def run_detail(db: Database, rid: int) -> dict:
    r = db.one("SELECT * FROM runs WHERE id=?", (rid,))
    if r is None:
        raise ApiError(404, "run_not_found", f"run {rid} does not exist")
    cmp = json.loads(r["comparison_json"])
    out = {"id": rid, "scenario_id": r["scenario_id"], "kind": r["kind"], "parent_run_id": r["parent_run_id"],
           "state": r["state"], "mode": r["mode"], "status": r["status"], "solve_seconds": round(r["solve_seconds"] or 0, 4),
           "created_at": r["created_at"], "pins": json.loads(r["pins_json"]), "changes": json.loads(r["changes_json"]),
           "comparison": cmp, "baseline": json.loads(r["baseline_json"]), "optimised": json.loads(r["optimised_json"]),
           "verify": json.loads(r["verify_json"]), "optimum_total": r["optimum_total"]}
    opt_total = cmp["optimised"]["total"]
    out["cost_of_planner_decisions"] = round(opt_total - r["optimum_total"], 6) if out["pins"] else 0.0
    if r["reference_run_id"]:
        ref = json.loads(db.one("SELECT comparison_json c FROM runs WHERE id=?", (r["reference_run_id"],))["c"])
        out["reference"] = {"run_id": r["reference_run_id"], "optimised_total": ref["optimised"]["total"],
                            "delta": round(opt_total - ref["optimised"]["total"], 6)}
    return out


def list_runs(db: Database, scenario_id: int | None = None) -> list[dict]:
    rows = db.all("SELECT id,scenario_id,kind,state,mode,status,created_at,parent_run_id FROM runs" +
                  (" WHERE scenario_id=?" if scenario_id else "") + " ORDER BY id DESC", (scenario_id,) if scenario_id else ())
    return [dict(r) for r in rows]


def create_run(db: Database, sid: int, mode: str, time_limit: float, actor: str = "planner") -> dict:
    r = _scenario_row(db, sid)
    ds = scenario_dataset(db, sid)
    rid, opt, cmp = _execute(db, sid, ds, mode, time_limit, "run", [], [], None, None, None, actor)
    audit.record(db, "RUN_COMPLETED", actor, sid, rid, {
        "mode": mode, "status": opt.status, "baseline": cmp["baseline"]["total"], "optimised": cmp["optimised"]["total"],
        "saving_pct": cmp["saving_pct"], "solve_seconds": round(opt.solve_seconds, 3)})
    return run_detail(db, rid)


def _editable(db: Database, rid: int):
    r = db.one("SELECT * FROM runs WHERE id=?", (rid,))
    if r is None:
        raise ApiError(404, "run_not_found", f"run {rid} does not exist")
    if r["state"] != "draft":
        raise ApiError(409, "run_locked", f"run {rid} is {r['state']} and can no longer be changed")
    return r


def apply_override(db: Database, rid: int, zone: str, sku: str, warehouse: str, pallets: float, reason: str,
                   actor: str = "planner") -> dict:
    parent = _editable(db, rid)
    if len((reason or "").strip()) < 3:
        raise ApiError(422, "reason_required", "A reason is required for every manual change.")
    if parent["mode"] == "milp" and float(pallets) != int(pallets):
        raise ApiError(422, "whole_pallets", "In MILP mode a decision must be a whole number of pallets.")
    sid = parent["scenario_id"]
    ds = apply_changes(scenario_dataset(db, sid), json.loads(parent["changes_json"]))
    if zone not in ds.zones or sku not in ds.skus or warehouse not in ds.warehouses:
        raise ApiError(422, "unknown_reference", "Unknown zone, SKU or warehouse.")
    pins = [p for p in json.loads(parent["pins_json"]) if (p["zone"], p["sku"], p["warehouse"]) != (zone, sku, warehouse)]
    pins.append({"zone": zone, "sku": sku, "warehouse": warehouse, "pallets": pallets, "reason": reason.strip()})
    try:
        new_id, opt, cmp = _execute(db, sid, ds, parent["mode"], 30, "override", pins, json.loads(parent["changes_json"]),
                                    rid, parent["reference_run_id"], parent["optimum_total"], actor)
    except ApiError as e:
        audit.record(db, "OVERRIDE_REJECTED", actor, sid, rid,
                     {"zone": zone, "sku": sku, "warehouse": warehouse, "pallets": pallets, "reason": reason, "why": e.code})
        raise
    audit.record(db, "OVERRIDE_APPLIED", actor, sid, new_id,
                 {"from_run": rid, "zone": zone, "sku": sku, "warehouse": warehouse, "pallets": pallets, "reason": reason.strip(),
                  "new_total": cmp["optimised"]["total"], "optimum_total": parent["optimum_total"]})
    return run_detail(db, new_id)


def run_whatif(db: Database, sid: int, changes: list[dict], mode: str, time_limit: float, actor: str = "planner",
               reference_run_id: int | None = None) -> dict:
    base_ds = scenario_dataset(db, sid)
    try:
        ds = apply_changes(base_ds, changes)
    except ChangeError as e:
        raise ApiError(422, "bad_change", str(e))
    label = describe(changes, base_ds)
    if reference_run_id is None:
        ref = db.one("SELECT id FROM runs WHERE scenario_id=? AND kind='run' ORDER BY id DESC LIMIT 1", (sid,))
        reference_run_id = ref["id"] if ref else None
    errs = [i for i in validate(ds, mode) if i.severity == "error"]
    if errs:
        diag = _diag(ds)
        audit.record(db, "WHATIF_INFEASIBLE", actor, sid, None, {"changes": label, "causes": diag["likely_causes"]})
        return {"feasible": False, "description": label, "issues": _issue_dicts(errs), "diagnosis": diag}
    rid, opt, cmp = _execute(db, sid, ds, mode, time_limit, "whatif", [], changes, None, reference_run_id, None, actor)
    audit.record(db, "WHATIF_RUN", actor, sid, rid, {"changes": label, "optimised": cmp["optimised"]["total"]})
    out = run_detail(db, rid)
    out.update({"feasible": True, "description": label})
    return out


# ---------- explanation ----------
def _facts_for(db: Database, rid: int) -> dict:
    r = db.one("SELECT * FROM runs WHERE id=?", (rid,))
    ds = apply_changes(scenario_dataset(db, r["scenario_id"]), json.loads(r["changes_json"]))
    base, opt = _plan_from_json(json.loads(r["baseline_json"])), _plan_from_json(json.loads(r["optimised_json"]))
    pins = json.loads(r["pins_json"])
    return build_facts(ds, base, opt, json.loads(r["comparison_json"]), pins, r["optimum_total"])


def generate_explanation(db: Database, rid: int, client, use_llm: bool = False, actor: str = "planner") -> dict:
    r = db.one("SELECT * FROM runs WHERE id=?", (rid,))
    if r is None:
        raise ApiError(404, "run_not_found", f"run {rid} does not exist")
    facts = _facts_for(db, rid)
    res = explain(facts, client, use_llm=use_llm)
    eid = db.execute("INSERT INTO explanations(created_at,run_id,text,source,reason,facts_json,status) VALUES(?,?,?,?,?,?,?)",
                     (now(), rid, res["text"], res["source"], res["reason"], dumps(facts), "draft"))
    audit.record(db, "EXPLANATION_GENERATED", actor, r["scenario_id"], rid,
                 {"source": res["source"], "reason": res["reason"], "unsupported_numbers": res["unsupported_numbers"]})
    return explanation_detail(db, rid)


def explanation_detail(db: Database, rid: int) -> dict | None:
    e = db.one("SELECT * FROM explanations WHERE run_id=? ORDER BY id DESC LIMIT 1", (rid,))
    if e is None:
        return None
    return {"id": e["id"], "run_id": rid, "text": e["text"], "source": e["source"], "reason": e["reason"],
            "status": e["status"], "approved_by": e["approved_by"], "edited": bool(e["edited"]),
            "facts": json.loads(e["facts_json"])}


def approve_explanation(db: Database, rid: int, text: str | None, actor: str = "planner") -> dict:
    e = db.one("SELECT * FROM explanations WHERE run_id=? ORDER BY id DESC LIMIT 1", (rid,))
    if e is None:
        raise ApiError(404, "no_explanation", "Generate an explanation first.")
    edited = bool(text and text.strip() and text.strip() != e["text"])
    db.execute("UPDATE explanations SET status='approved', approved_by=?, edited=?, text=? WHERE id=?",
               (actor, int(edited), text.strip() if edited else e["text"], e["id"]))
    r = db.one("SELECT scenario_id FROM runs WHERE id=?", (rid,))
    audit.record(db, "EXPLANATION_APPROVED", actor, r["scenario_id"], rid, {"edited": edited, "source": e["source"]})
    return explanation_detail(db, rid)


# ---------- approval ----------
def decide(db: Database, rid: int, decision: str, comment: str, actor: str = "planner") -> dict:
    if decision not in ("approve", "reject"):
        raise ApiError(422, "bad_decision", "decision must be 'approve' or 'reject'")
    r = _editable(db, rid)
    if decision == "reject" and len((comment or "").strip()) < 3:
        raise ApiError(422, "comment_required", "Please say why the plan is rejected.")
    state = "approved" if decision == "approve" else "rejected"
    db.execute("UPDATE runs SET state=? WHERE id=?", (state, rid))
    audit.record(db, "PLAN_APPROVED" if decision == "approve" else "PLAN_REJECTED", actor, r["scenario_id"], rid,
                 {"comment": (comment or "").strip()})
    return run_detail(db, rid)


# ---------- export ----------
def _csv(rows: list[dict], cols: list[str]) -> str:
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(cols)
    for r in rows:
        w.writerow([r[c] for c in cols])
    return buf.getvalue()


def export_zip(db: Database, rid: int, actor: str = "planner") -> bytes:
    d = run_detail(db, rid)
    if d["state"] != "approved":
        raise ApiError(409, "export_not_approved", "Only an approved plan can be exported. Approve the run first.")
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("STATUS.txt", f"run {rid}: APPROVED. This is a proposed plan for the existing ERP/WMS/TMS to execute; "
                   "Nordic Flow does not execute it. Synthetic data unless the scenario source says otherwise.\n")
        for name in ("baseline", "optimised"):
            if name == "baseline" and not d["comparison"].get("baseline_valid", True):
                continue
            z.writestr(f"{name}_outbound.csv", _csv(d[name]["outbound"], ["warehouse", "zone", "sku", "pallets"]))
            z.writestr(f"{name}_inbound.csv", _csv(d[name]["inbound"], ["supplier", "warehouse", "sku", "pallets"]))
        z.writestr("comparison.json", json.dumps(d["comparison"], indent=2))
        z.writestr("planner_decisions.json", json.dumps(d["pins"], indent=2))
        z.writestr("audit_log.json", json.dumps(audit.events(db, run_id=rid), indent=2))
    audit.record(db, "EXPORT_DOWNLOADED", actor, d["scenario_id"], rid, {"state": d["state"]})
    return buf.getvalue()
