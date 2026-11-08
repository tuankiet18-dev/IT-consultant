"""Pre-flight check before recording MVP.mp4.

Runs the exact numbers the video script quotes, in-process (no server needed, nothing is saved in your real
database). If every line says PASS, the numbers on screen will match the narration.

Run from the repository root:
    mvp\\.venv\\Scripts\\python.exe deliverables\\video-kit\\scripts\\preflight.py
"""
import io
import os
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

KIT = Path(__file__).resolve().parents[1]
REPO = KIT.parents[1]
MVP = REPO / "mvp"
sys.path.insert(0, str(MVP))
sys.stdout.reconfigure(encoding="utf-8")

from fastapi.testclient import TestClient  # noqa: E402
from api.main import create_app  # noqa: E402

results = []


def check(name, ok, detail=""):
    results.append(ok)
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"  ({detail})" if detail else ""))


def upload_zip(client, path):
    return client.post("/api/scenarios", files=[("files", (path.name, path.read_bytes(), "application/zip"))],
                       data={"name": path.stem})


client = TestClient(create_app(Path(tempfile.mkdtemp()) / "preflight.db",
                               llm_factory=lambda: type("L", (), {"enabled": False, "model": ""})()))
data = KIT / "data"

# 1. The three ZIP files exist and have the 8 required CSV files at the root
required = {"suppliers.csv", "warehouses.csv", "zones.csv", "skus.csv", "inbound_rates.csv",
            "outbound_rates.csv", "supply.csv", "demand.csv"}
for name in ("nordic-flow-pilot-sample.zip", "05_invalid_warehouse_cycle.zip", "baseline-unusable.zip"):
    p = data / name
    names = set(zipfile.ZipFile(p).namelist()) if p.exists() else set()
    check(f"file {name} has the 8 required CSV files", required <= names)

# 2. Scene 3: valid upload
s = upload_zip(client, data / "nordic-flow-pilot-sample.zip").json()
sm = s.get("summary", {})
check("scene 3  sample ZIP is valid, 606 pallets, 954 capacity",
      s.get("valid") is True and sm.get("demand_pallets") == 606 and sm.get("capacity_total") == 954,
      f"valid={s.get('valid')} demand={sm.get('demand_pallets')} capacity={sm.get('capacity_total')}")

# 3. Scene 3: invalid upload is blocked with the loop message
bad = upload_zip(client, data / "05_invalid_warehouse_cycle.zip").json()
msgs = " ".join(i["message"] for i in bad.get("issues", []) if i["severity"] == "error")
check("scene 3  loop ZIP is blocked with the directed-acyclic-graph message",
      bad.get("valid") is False and "directed acyclic graph" in msgs, msgs[:80])

# 4. Scene 4: result numbers
r = client.post(f"/api/scenarios/{s['id']}/runs", json={"mode": "milp", "time_limit": 30}).json()
c = r["comparison"]
check("scene 4  baseline 32,698 / optimised 31,316 / saving 1,382 (4.2%)",
      round(c["baseline"]["total"]) == 32698 and round(c["optimised"]["total"]) == 31316
      and round(c["saving"]) == 1382 and round(c["saving_pct"], 1) == 4.2,
      f"{c['baseline']['total']:g} / {c['optimised']['total']:g} / {c['saving']:g}")
check("scene 4  status OPTIMAL and independent checks passed",
      r["status"] == "OPTIMAL" and not r["verify"]["optimised_violations"])

# 5. Scene 4: route ranking for Zone 1, Cement standard
p = client.get(f"/api/runs/{r['id']}/paths", params={"zone": "Z1", "sku": "SKU-01"}).json()
top = p["paths"][0] if p.get("paths") else {}
check("scene 4  route ranking: 6 paths, cheapest is Supplier 1 > Warehouse C at 62",
      p.get("total_paths") == 6 and top.get("supplier") == "SUP1" and top.get("warehouses") == ["WC"] and top.get("cost_per_pallet") == 62,
      f"{p.get('total_paths')} paths, top {top.get('supplier')} {top.get('warehouses')} {top.get('cost_per_pallet')}")

# 6. Scene 5: explanation (standard summary, no AI in this check)
e = client.post(f"/api/runs/{r['id']}/explanation", json={"use_llm": False}).json()
check("scene 5  explanation generated", bool(e.get("text")) and e.get("source") == "deterministic")

# 7. Scene 5: demo-guard command
py = MVP / ".venv" / "Scripts" / "python.exe"
out = subprocess.run([str(py if py.exists() else sys.executable), "-m", "nordic_flow", "demo-guard"], cwd=MVP,
                     capture_output=True, text=True, encoding="utf-8", env={**os.environ, "GROQ_API_KEY": ""})
check("scene 5  demo-guard prints ACCEPTED and REJECTED", "ACCEPTED" in out.stdout and "REJECTED" in out.stdout)

# 8. Scene 6: planner decision
o = client.post(f"/api/runs/{r['id']}/overrides", json={"zone": "Z1", "sku": "SKU-01", "warehouse": "WB", "pallets": 8,
                                                         "reason": "Customer contract names this warehouse"}).json()
oc = o["comparison"]
check("scene 6  decision: Plan costs 31,404 (+88), saving 1,294",
      round(oc["optimised"]["total"]) == 31404 and round(o["cost_of_planner_decisions"]) == 88 and round(oc["saving"]) == 1294,
      f"{oc['optimised']['total']:g}, +{o['cost_of_planner_decisions']:g}, saving {oc['saving']:g}")

# 9. Scene 7: lock, export, audit
check("scene 7  export before approval is refused (409)", client.get(f"/api/runs/{o['id']}/export").status_code == 409)
client.post(f"/api/runs/{o['id']}/explanation", json={"use_llm": False})
client.post(f"/api/runs/{o['id']}/explanation/approve", json={"text": "", "actor": "planner"})
d = client.post(f"/api/runs/{o['id']}/decision", json={"decision": "approve", "comment": "Reviewed"})
check("scene 7  approve works", d.status_code == 200 and d.json()["state"] == "approved")
ex = client.get(f"/api/runs/{o['id']}/export")
files = zipfile.ZipFile(io.BytesIO(ex.content)).namelist() if ex.status_code == 200 else []
check("scene 7  export ZIP has comparison.json and audit_log.json", "comparison.json" in files and "audit_log.json" in files, f"{len(files)} files")
check("scene 7  approved plan cannot be changed (409)",
      client.post(f"/api/runs/{o['id']}/overrides", json={"zone": "Z1", "sku": "SKU-01", "warehouse": "WB", "pallets": 8, "reason": "x y z"}).status_code == 409)
check("scene 7  audit trail chain verifies", client.get("/api/audit/verify").json().get("ok") is True)

# 10. Scene 8: what-if
w = client.post(f"/api/scenarios/{s['id']}/whatif", json={"changes": [{"type": "close_warehouse", "warehouse": "WA"}], "mode": "milp", "time_limit": 30}).json()
causes = " ".join(w.get("diagnosis", {}).get("likely_causes", []))
check("scene 8  closing Warehouse A: no feasible plan, 684 < 902", w.get("feasible") is False and "684" in causes and "902" in causes, causes[:90])

# 11. Optional scene: baseline unusable
u = upload_zip(client, data / "baseline-unusable.zip").json()
ur = client.post(f"/api/scenarios/{u['id']}/runs", json={"mode": "milp", "time_limit": 30}).json()
check("bonus    baseline-unusable ZIP: no saving reported", ur["comparison"]["baseline_valid"] is False and ur["comparison"]["saving"] is None)

# 12. Environment
check("app    frontend build exists (mvp/web/index.html)", (MVP / "web" / "index.html").exists())
br = subprocess.run(["git", "branch", "--show-current"], cwd=REPO, capture_output=True, text=True).stdout.strip()
check("repo   branch is final-round2", br == "final-round2", f"current: {br}")
print(f"INFO  AI will be {'ON' if os.environ.get('GROQ_API_KEY') else 'OFF'} for this terminal (key is read from GROQ_API_KEY, never printed)")

print()
print("ALL GOOD, you can record." if all(results) else f"{results.count(False)} check(s) FAILED. Fix them before recording.")
sys.exit(0 if all(results) else 1)
