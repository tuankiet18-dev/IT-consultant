"""SQLite storage. One connection guarded by a lock is enough for a local single-user MVP."""
from __future__ import annotations
import json
import sqlite3
import threading
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS scenarios(
  id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TEXT NOT NULL, name TEXT NOT NULL, source TEXT NOT NULL,
  files_json TEXT NOT NULL, issues_json TEXT NOT NULL, valid INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS runs(
  id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TEXT NOT NULL, scenario_id INTEGER NOT NULL, kind TEXT NOT NULL,
  parent_run_id INTEGER, state TEXT NOT NULL, mode TEXT NOT NULL, status TEXT NOT NULL, solve_seconds REAL,
  pins_json TEXT NOT NULL, changes_json TEXT NOT NULL, optimum_total REAL, reference_run_id INTEGER,
  baseline_json TEXT NOT NULL, optimised_json TEXT NOT NULL, comparison_json TEXT NOT NULL, verify_json TEXT NOT NULL,
  route_pins_json TEXT NOT NULL DEFAULT '[]');
CREATE TABLE IF NOT EXISTS explanations(
  id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TEXT NOT NULL, run_id INTEGER NOT NULL, text TEXT NOT NULL,
  source TEXT NOT NULL, reason TEXT, facts_json TEXT NOT NULL, status TEXT NOT NULL, approved_by TEXT, edited INTEGER NOT NULL DEFAULT 0);
CREATE TABLE IF NOT EXISTS audit_events(
  id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT NOT NULL, type TEXT NOT NULL, actor TEXT NOT NULL,
  scenario_id INTEGER, run_id INTEGER, payload_json TEXT NOT NULL, prev_hash TEXT NOT NULL, hash TEXT NOT NULL);
"""


class Database:
    def __init__(self, path: str | Path = ":memory:"):
        if str(path) != ":memory:":
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.lock = threading.RLock()
        with self.lock:
            self.conn.executescript(SCHEMA)
            # Additive migration keeps existing scenarios, approvals and audit records intact.
            columns = {row["name"] for row in self.conn.execute("PRAGMA table_info(runs)")}
            if "route_pins_json" not in columns:
                self.conn.execute("ALTER TABLE runs ADD COLUMN route_pins_json TEXT NOT NULL DEFAULT '[]'")
            self.conn.commit()

    def execute(self, sql: str, args: tuple = ()) -> int:
        with self.lock:
            cur = self.conn.execute(sql, args)
            self.conn.commit()
            return cur.lastrowid

    def one(self, sql: str, args: tuple = ()):
        with self.lock:
            return self.conn.execute(sql, args).fetchone()

    def all(self, sql: str, args: tuple = ()):
        with self.lock:
            return self.conn.execute(sql, args).fetchall()


def dumps(x) -> str:
    return json.dumps(x, sort_keys=True, default=str)
