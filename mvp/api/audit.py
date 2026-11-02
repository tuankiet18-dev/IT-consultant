"""Append-only audit log with a hash chain: each event's hash covers the previous hash, so any edit is detectable."""
from __future__ import annotations
import hashlib
import json
from datetime import datetime, timezone
from .db import Database, dumps

GENESIS = "0" * 64


def _digest(prev: str, ts: str, type_: str, actor: str, scenario_id, run_id, payload_json: str) -> str:
    body = json.dumps([prev, ts, type_, actor, scenario_id, run_id, payload_json], sort_keys=True)
    return hashlib.sha256(body.encode()).hexdigest()


def record(db: Database, type_: str, actor: str = "system", scenario_id: int | None = None,
           run_id: int | None = None, payload: dict | None = None) -> int:
    with db.lock:
        last = db.one("SELECT hash FROM audit_events ORDER BY id DESC LIMIT 1")
        prev = last["hash"] if last else GENESIS
        ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
        pj = dumps(payload or {})
        return db.execute(
            "INSERT INTO audit_events(ts,type,actor,scenario_id,run_id,payload_json,prev_hash,hash) VALUES(?,?,?,?,?,?,?,?)",
            (ts, type_, actor, scenario_id, run_id, pj, prev, _digest(prev, ts, type_, actor, scenario_id, run_id, pj)))


def events(db: Database, run_id: int | None = None, scenario_id: int | None = None) -> list[dict]:
    sql, args = "SELECT * FROM audit_events", ()
    if run_id is not None:
        sql, args = sql + " WHERE run_id=?", (run_id,)
    elif scenario_id is not None:
        sql, args = sql + " WHERE scenario_id=?", (scenario_id,)
    return [{"id": r["id"], "ts": r["ts"], "type": r["type"], "actor": r["actor"], "scenario_id": r["scenario_id"],
             "run_id": r["run_id"], "payload": json.loads(r["payload_json"]), "hash": r["hash"][:12]}
            for r in db.all(sql + " ORDER BY id", args)]


def verify_chain(db: Database) -> dict:
    prev = GENESIS
    for r in db.all("SELECT * FROM audit_events ORDER BY id"):
        ok = r["prev_hash"] == prev and r["hash"] == _digest(prev, r["ts"], r["type"], r["actor"], r["scenario_id"],
                                                             r["run_id"], r["payload_json"])
        if not ok:
            return {"ok": False, "broken_at_event": r["id"]}
        prev = r["hash"]
    return {"ok": True, "events": db.one("SELECT COUNT(*) c FROM audit_events")["c"]}
