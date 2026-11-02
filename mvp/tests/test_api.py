import io
import json
import zipfile
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from api.main import create_app
from nordic_flow.llm import LLMError

GOLDEN = Path(__file__).parent.parent / "data" / "golden"


class FakeLLM:
    def __init__(self, reply=None, enabled=True): self.reply, self.enabled, self.model = reply, enabled, "fake"
    def chat(self, messages, **kw):
        if self.reply is None: raise LLMError("down")
        return self.reply


@pytest.fixture
def client(tmp_path):
    holder = {"llm": FakeLLM(None, enabled=False)}
    app = create_app(tmp_path / "t.db", llm_factory=lambda: holder["llm"])
    c = TestClient(app)
    c.holder = holder
    return c


def golden(client):
    return client.post("/api/scenarios/sample", json={"name": "golden"}).json()


def test_sample_scenario_run_matches_the_round1_example(client):
    s = golden(client)
    assert s["valid"] and s["summary"]["warehouses"] == 2
    r = client.post(f"/api/scenarios/{s['id']}/runs", json={"mode": "milp"}).json()
    assert r["status"] == "OPTIMAL"
    assert r["comparison"]["baseline"]["total"] == 700 and r["comparison"]["optimised"]["total"] == 500
    assert r["verify"] == {"baseline_violations": [], "optimised_violations": []}


def test_upload_with_errors_is_blocked_with_file_and_row(client):
    files = []
    for p in GOLDEN.glob("*.csv"):
        text = p.read_text()
        if p.name == "inbound_rates.csv":
            text = text.replace("S1,A,2", "S1,A,-2")
        files.append(("files", (p.name, text, "text/csv")))
    s = client.post("/api/scenarios", files=files).json()
    assert not s["valid"]
    assert any(i["file"] == "inbound_rates.csv" and i["row"] == 2 for i in s["issues"])
    r = client.post(f"/api/scenarios/{s['id']}/runs", json={})
    assert r.status_code == 422 and r.json()["code"] == "invalid_data"


def test_override_costs_more_is_recorded_and_can_be_approved(client):
    s = golden(client)
    run = client.post(f"/api/scenarios/{s['id']}/runs", json={}).json()
    bad = client.post(f"/api/runs/{run['id']}/overrides",
                      json={"zone": "S", "sku": "SKU-01", "warehouse": "A", "pallets": 40, "reason": ""})
    assert bad.status_code == 422 and bad.json()["code"] == "reason_required"
    o = client.post(f"/api/runs/{run['id']}/overrides",
                    json={"zone": "S", "sku": "SKU-01", "warehouse": "A", "pallets": 40, "reason": "Customer contract names A"}).json()
    assert o["kind"] == "override" and o["comparison"]["optimised"]["total"] == 700
    assert o["cost_of_planner_decisions"] == 200
    d = client.post(f"/api/runs/{o['id']}/decision", json={"decision": "approve", "comment": "ok"}).json()
    assert d["state"] == "approved"
    locked = client.post(f"/api/runs/{o['id']}/overrides",
                         json={"zone": "N", "sku": "SKU-01", "warehouse": "A", "pallets": 60, "reason": "again"})
    assert locked.status_code == 409 and locked.json()["code"] == "run_locked"


def test_impossible_override_is_rejected_and_logged(client):
    s = golden(client)
    run = client.post(f"/api/scenarios/{s['id']}/runs", json={}).json()
    r = client.post(f"/api/runs/{run['id']}/overrides",
                    json={"zone": "N", "sku": "SKU-01", "warehouse": "B", "pallets": 70, "reason": "try"})
    assert r.status_code == 409 and r.json()["code"] == "pins_infeasible"
    types = [e["type"] for e in client.get("/api/audit", params={"run_id": run["id"]}).json()]
    assert "OVERRIDE_REJECTED" in types


def test_explanation_template_then_llm_with_number_guard_and_approval(client):
    s = golden(client)
    run = client.post(f"/api/scenarios/{s['id']}/runs", json={}).json()
    e = client.post(f"/api/runs/{run['id']}/explanation").json()
    assert e["source"] == "deterministic" and "200" in e["text"] and e["status"] == "draft"
    client.holder["llm"] = FakeLLM("Savings reach 99% here.")
    e = client.post(f"/api/runs/{run['id']}/explanation").json()          # LLM is opt-in: still deterministic
    assert e["source"] == "deterministic" and e["reason"] is None
    e = client.post(f"/api/runs/{run['id']}/explanation", json={"use_llm": True}).json()
    assert e["source"] == "deterministic" and "not in facts" in e["reason"]
    client.holder["llm"] = FakeLLM("Cost falls from 700 to 500, saving 200 (28.6%). The planner should review before approving.")
    e = client.post(f"/api/runs/{run['id']}/explanation", json={"use_llm": True}).json()
    assert e["source"] == "groq:fake"
    a = client.post(f"/api/runs/{run['id']}/explanation/approve", json={"text": e["text"] + " Edited.", "actor": "Kiet"}).json()
    assert a["status"] == "approved" and a["edited"] and a["approved_by"] == "Kiet"


def test_whatif_close_warehouse_feasible_and_infeasible(client):
    s = golden(client)
    base = client.post(f"/api/scenarios/{s['id']}/runs", json={}).json()
    w = client.post(f"/api/scenarios/{s['id']}/whatif",
                    json={"changes": [{"type": "close_warehouse", "warehouse": "B"}]}).json()
    assert w["feasible"] and w["comparison"]["optimised"]["total"] == 700
    assert w["reference"]["run_id"] == base["id"] and w["reference"]["delta"] == 200
    x = client.post(f"/api/scenarios/{s['id']}/whatif",
                    json={"changes": [{"type": "close_warehouse", "warehouse": "A"}]}).json()
    assert x["feasible"] is False and any("capacity" in c for c in x["diagnosis"]["likely_causes"])
    bad = client.post(f"/api/scenarios/{s['id']}/whatif", json={"changes": [{"type": "nope"}]})
    assert bad.status_code == 422


def test_audit_chain_detects_tampering(client):
    s = golden(client)
    client.post(f"/api/scenarios/{s['id']}/runs", json={})
    assert client.get("/api/audit/verify").json()["ok"] is True
    db = client.app.state.db
    db.execute("UPDATE audit_events SET payload_json='{\"x\":1}' WHERE id=1")
    assert client.get("/api/audit/verify").json() == {"ok": False, "broken_at_event": 1}


def test_export_zip_contents_and_status(client):
    s = golden(client)
    run = client.post(f"/api/scenarios/{s['id']}/runs", json={}).json()
    blocked = client.get(f"/api/runs/{run['id']}/export")
    assert blocked.status_code == 409 and blocked.json()["code"] == "export_not_approved"
    client.post(f"/api/runs/{run['id']}/decision", json={"decision": "approve", "comment": "ok"})
    z = zipfile.ZipFile(io.BytesIO(client.get(f"/api/runs/{run['id']}/export").content))
    names = set(z.namelist())
    assert {"STATUS.txt", "optimised_outbound.csv", "baseline_outbound.csv", "comparison.json", "audit_log.json"} <= names
    assert "APPROVED" in z.read("STATUS.txt").decode()


def test_mapping_endpoint_and_errors_are_json(client):
    s = golden(client)
    m = client.post("/api/mapping/suggest", json={"scenario_id": s["id"], "items": [{"code": "X", "name": "example sku"}]})
    assert m.status_code == 200 and m.json()[0]["candidates"][0]["sku_id"] == "SKU-01"
    nf = client.get("/api/runs/999")
    assert nf.status_code == 404 and nf.json()["code"] == "run_not_found"


def test_mapping_confirmation_is_audited(client):
    s = golden(client)
    r = client.post("/api/mapping/confirm", json={"scenario_id": s["id"], "external": {"code": "X"}, "sku_id": "SKU-01"})
    assert r.json() == {"confirmed": True}
    assert any(e["type"] == "MAPPING_CONFIRMED" for e in client.get("/api/audit").json())
    assert client.post("/api/mapping/confirm", json={"scenario_id": s["id"], "external": {}, "sku_id": "NOPE"}).status_code == 422
