# Nordic Flow MVP

Goods allocation across existing warehouses at lowest total cost (supplier -> warehouse -> customer zone), with the planner in control.
A local web app: FastAPI + SQLite + OR-Tools, with a plain HTML/JS front end (no build step). Specification: `../docs/MVP-SPEC-v0.1.md`; what is actually built: `../docs/round2/AS_BUILT.md`.

## Run it

```bash
cd mvp
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pytest -q                                              # 53 tests
uvicorn api.main:app --port 8000                       # open http://localhost:8000
```

The app works offline. For the optional AI explanation (Groq, free tier), set a key before starting:

```bash
export GROQ_API_KEY=...        # Windows PowerShell: $env:GROQ_API_KEY="..."   (see .env.example; never commit a key)
```

Without a key, explanations are deterministic summaries built only from the calculated numbers.

## The journey in the UI

1. **Data:** load the synthetic demo or the 700 -> 500 worked example, or upload the 8 CSV files (or a ZIP of them). Errors are shown by file and row and block the run.
2. **Results:** preferred-warehouse baseline vs optimised plan, cost by type, warehouse load, independent check.
3. **Plan:** which warehouse serves each zone and SKU; changed rows highlighted.
4. **Review & adjust:** explanation (deterministic, or AI draft that the planner approves), and exact-pallet planner decisions with a reason; the plan is re-optimised around them.
5. **Approve & audit:** approve or reject a run; export is only possible for approved runs; audit log with hash chain.
6. **What-if:** close a warehouse, change capacity, scale a zone's demand; infeasible cases come with diagnostic hints.

## Rules the code enforces

- A saving is reported only when the baseline serves 100% of demand and passes the independent check; otherwise it is `null`.
- The independent verifier (`nordic_flow/verify.py`) does not use the solver and is strict about unmet demand.
- Solver `FEASIBLE` (time limit) is never shown as `OPTIMAL`.
- The LLM never calculates. It only phrases facts computed in code, is opt-in per request, is checked for invented numbers, and stays a draft until a planner approves it.
- Approved runs are immutable. A planner decision creates a new run.
- Costs are synthetic cost units per pallet. The baseline is a synthetic preferred-warehouse rule, not Company A's actual plan.

## Layout

```
nordic_flow/   Core (no web or database code): io, validation, baseline, optimiser, verify, report, diagnosis,
               whatif, explain, llm, mapping, synth, cli
api/           FastAPI app, SQLite storage, use cases (service.py), hash-chained audit log
web/           index.html, app.js, style.css
data/          golden (700 -> 500 example), demo (synthetic, regenerate with `python -m nordic_flow synth data/demo`)
tests/         pytest suite; e2e_ui.js is a Playwright walk-through of the whole journey
```

## CLI (core only)

```bash
python -m nordic_flow run data/golden               # 700 -> 500
python -m nordic_flow run data/demo --out out/demo
```

## API (all under /api; errors are JSON {code, message, details})

| Method and path | Purpose |
|---|---|
| `GET /config`, `GET /health` | Feature flags (LLM on/off), liveness |
| `POST /scenarios/sample` `{name}` | Load `demo` or `golden` |
| `POST /scenarios` (multipart `files`, one ZIP or several CSVs) | Upload and validate |
| `GET /scenarios/{id}`, `GET /scenarios` | Details, list |
| `POST /scenarios/{id}/runs` `{mode, time_limit}` | Baseline + optimise + verify |
| `GET /runs/{id}` | Full run (comparison, plans, checks) |
| `POST /runs/{id}/overrides` | Exact-pallet planner decision, re-optimise as a new run |
| `POST /runs/{id}/explanation` `{use_llm}`; `GET`; `POST .../approve` | Explanation draft and approval |
| `POST /runs/{id}/decision` `{decision, comment}` | Approve or reject (locks the run) |
| `GET /runs/{id}/export` | ZIP of the approved plan (409 until approved) |
| `POST /scenarios/{id}/whatif` | Try changes on a copy of the data |
| `GET /audit`, `GET /audit/verify` | Audit events, chain check |
| `POST /mapping/suggest`, `POST /mapping/confirm` | SKU mapping helper (suggest, then confirm) |

## Honest limits

- Demo data is synthetic. The ~4% saving on `data/demo` comes from how that data was built; it is not a forecast for Company A.
- One planning period, no inventory carry-over, linear costs, no vehicle routing, no ERP/WMS/TMS connection (CSV in, CSV out).
- Single simulated planner; no login.
- The Groq call has not been tested against the live service in the development environment (no key, restricted network); it is covered by tests with a fake client.

## Round 2 checks

Python 3.11.4 was tested on Windows. From the MVP directory:

```bash
python -m nordic_flow demo-guard
python -m nordic_flow robustness --out ../docs/round2/ROBUSTNESS.md
```

The guard demo uses simulated model responses and the production numeric check.
For a live check, set `GROQ_API_KEY` in the server environment and generate an AI explanation three times on Synthetic demo. Check for three complete paragraphs, grounded numbers, and any fallback reason.

For the browser walkthrough, install Playwright and Chromium in your Node environment, then run `node tests/e2e_ui.js` against the running app. Use `BASE_URL` for another port, `BROWSER_CHANNEL=msedge` for installed Edge, and `SHOTS` to save screenshots. Use a disposable database for the walkthrough.

## Reset the recording database

1. Stop the server. If the default local database is disposable, delete the MVP's `var/` directory. This clears local runs and audit history.
2. Restart the server and load Synthetic demo again.
