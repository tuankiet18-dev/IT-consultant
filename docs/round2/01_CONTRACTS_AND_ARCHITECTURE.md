# NORDIC FLOW ROUND 2 — PROPOSED TECHNICAL CONTRACTS

**Status: DRAFT — freeze after team reviews `00_TEAM_DECISIONS_DRAFT.md`.** This is a design spec, **not documentation of currently running code**.

## A. Context boundary — truthful Round 2 build-a-thon version

```text
Planner (simulated single local user)
         |
         | browser actions / downloads
         v
  [Nordic Flow Web App — LOCAL]
       | UI (Jinja2 / HTML / JS)
       | HTTP JSON API (FastAPI)
       | Application services:
       |   ScenarioService -> RunService -> DecisionService
       |   independent verifier + cost report + ExportService
       | Core optimisation (existing `nordic_flow`, OR-Tools)
       | SQLite scenario/run/approval/audit data
         ^
         |
  Synthetic example CSV data / optional user-imported CSV ZIP
         |
         +--> output proposed inbound/outbound allocation CSV files

External systems (Company A ERP/WMS/TMS): FUTURE INTEGRATION ONLY.
Optional LLM provider (only if implemented): EXTERNAL service, disabled-by-default.
```

**Never draw live bidirectional ERP/WMS/TMS API calls if these are not implemented.** R1 proposed those integrations for the commercial pilot; the Round 2 prototype uses CSV import/export and synthetic data. The output is a proposal to a planner, not autonomous transportation execution.

## B. Lean repository tree and file ownership

```text
mvp/
  nordic_flow/                  # EXISTING pure-python core; Core owner
    schema.py io.py validation.py baseline.py optimiser.py
    verify.py report.py diagnosis.py synth.py cli.py
  app/                          # NEW API & UI app; separate owners
    main.py                     # FastAPI app entrypoint
    api.py                      # Route definitions, thin validation only
    contracts.py                # Pydantic request/response DTOs
    services.py                 # scenario/run/decision orchestration
    storage.py                  # SQLite persistence and migrations/init
    templates/index.html        # Server-rendered shell
    static/app.js               # Dynamic UI; API calls
    static/style.css            # Styling only
  tests/
    test_golden.py              # Existing
    test_demo_data.py           # Existing
    test_validation_and_diagnosis.py
    test_baseline_guards.py     # NEW: T05 and invalid saving tests
    test_api_contract.py        # NEW: smoke / negative response tests
    test_decision_workflow.py   # NEW: override and immutable approvals
  requirements.txt              # pin or lock versions after green install
  README.md

docs/round2/
  DECISIONS.md
  CONTRACTS.md
  ARCHITECTURE.md
  TEST_PLAN.md
  AI_USAGE_LOG.md
```

**Avoid:** separate frontend deployment, Redux, microservices, Redis, Celery, cloud, Docker unless an actual blocker justifies them. A single local Python process and one SQLite file are adequate for the judging video.

## C. Canonical model and units

- `supplier_id`, `warehouse_id`, `zone_id`, `sku_id` are strings. No external customer name required.
- `demand[zone,sku]` in pallet quantities; `supply[supplier,sku]` max pallets per planning period; `warehouse.capacity` in pallet-equivalents; `sku.pallet_factor > 0`.
- `inbound_rates[supplier,warehouse]` and `outbound_rates[warehouse,zone]` synthetic **cost units per pallet**. A missing lane is forbidden, not zero-cost.
- Demand must be met exactly; warehouse flow balanced; supply and capacity are upper bounds. No carry-over stock model.
- Solver mode `milp` is default for whole pallets, continuous LP for tutorial/testing only.
- For two plans to be compared, both must have **0 shortfall**, the same `scenario_id` and verified constraints.

The current core can represent two independently selected flows (supplier→warehouse and warehouse→zone), balanced by `(warehouse,sku)`. It does not persist a direct supplier→warehouse→zone path for each pallet. UI must not invent supplier-specific end-to-end parcel paths not in the result.

## D. API contract v0.1 (proposed; exact names to freeze)

**Base:** `/api`; success JSON; error JSON `{ "code":"...", "message":"human readable", "details":[] }`. No raw stack traces in browser.

| Method | Path | Purpose | Key return / restriction |
|---|---|---|---|
| POST | `/scenarios/demo` | Load deterministic in-repo demo | `scenario_id`, `source=synthetic_demo`, counts, issues |
| POST | `/scenarios/import` | Upload allowlisted ZIP of 8/9 CSVs | `scenario_id`, `source=uploaded_csv`, errors by file/row, dataset_hash |
| GET | `/scenarios/{id}` | Get metadata + validation status | counts, validity, synthetic label |
| POST | `/scenarios/{id}/runs` | Solve baseline + MILP + verify | `run_id`, `solver_status`, `baseline_valid`, `saving_pct` nullable |
| GET | `/runs/{id}` | Fetch breakdown and plan | complete summary, verification, allocations |
| POST | `/runs/{id}/override` | Apply **exact pin** and re-solve | `child_run_id`, original unchanged, errors if infeasible |
| POST | `/runs/{id}/decision` | Approve / Reject | new immutable decision status; comment |
| GET | `/runs/{id}/export` | Download approved inbound/outbound CSV | 409 if not approved, no auto-execution |
| GET | `/runs/{id}/audit` | Read event list | timestamped events; simulated actor |
| GET | `/runs/{id}/explanation` | Optional deterministic / LLM-assisted explanation | clearly tagged provenance, no unexplained numbers |

**Example POST `/api/scenarios/{id}/runs`:**

```json
{"mode":"milp","time_limit_seconds":20}
```

**Example GET `/api/runs/{id}` response outline:**

```json
{
  "run_id":"r-123", "scenario_id":"s-123", "parent_run_id":null,
  "solver_status":"OPTIMAL", "plan_valid":true, "approval_status":"DRAFT",
  "baseline":{"status":"BASELINE", "valid":true, "total_cost":700.0},
  "optimised":{"total_cost":500.0, "cost_breakdown":{"inbound_freight":0.0, "inbound_handling":0.0, "outbound_freight":500.0, "outbound_handling":0.0}},
  "comparison":{"saving":200.0,"saving_pct":28.5714},
  "source":"synthetic_demo", "cost_unit":"synthetic_cost_unit",
  "constraints":{"verified":true,"violations":[]},
  "allocations":{"inbound":[], "outbound":[]}
}
```

The numbers above are purely an **illustrative schema** for the golden case; actual cost breakdown and allocations must come from `report.py`, never be hard-coded by frontend or an LLM.

**Example POST `/api/runs/{id}/override`:**

```json
{"zone_id":"N","sku_id":"SKU-01","warehouse_id":"A","pallets":20,"constraint":"exact","reason":"Planner has an operational requirement"}
```

A successful override produces a **new run** and does not automatically approve it. Infeasible override returns a clear conflict/error with a diagnostic hint and leaves original unchanged.

**Example POST `/api/runs/{id}/decision`:**

```json
{"decision":"APPROVED","comment":"Reviewed cost and warehouse constraints"}
```

This returns 409 if the run was already approved/rejected or if verification failed. Export is permitted only for an approved, full-demand, independently verified plan.

### API invariants: don't compromise

1. Reject incomplete/invalid data before solver invocation.
2. Always verify plans before comparison or approval, including the *baseline*.
3. Shortfall >0 means not a valid customer-fulfilling plan; diagnosis-only output cannot approve/export.
4. Return `saving=null, saving_pct=null` for unusable baseline, plus a reason.
5. `FEASIBLE` after timeout ≠ `OPTIMAL`.
6. New override generates new child run; approved run immutable.
7. Every state-changing endpoint writes audit event with actor and time.
8. Never claim external ERP/WMS/TMS integration if only CSV files exist.

## E. Optional AI integration (careful about vibe-coding pressure)

- **Required fallback:** a template explanation assembled only from verified numeric code facts. Label `Source: deterministic summary`, not `AI Generated`.
- **If LLM implemented:** backend-only external request, synthetic fact-pack only (no secrets/company data), feature flag and timeout. Output is `DRAFT` until planner approves/edits. Clear badge `AI-generated draft`.
- Naive number-presence checks aren't enough to prove a sentence true: an LLM may recombine valid numbers into a false statement. **Show original verified KPI dashboard adjacent to explanation**; do not let free text change source-of-truth values.
- Because team is **AI-assisted coding**, record actual prompt-driven scaffold/refactor/test generation and human verification in `AI Journal` even if no runtime LLM is shipped. Clarify to judges what AI did and did not do.

## F. Minimal storage and state machine

Proposed tables: `scenarios(id, source, dataset_hash, created_at, source_path_or_json)`, `runs(id, scenario_id, parent_run_id, solver_status, plan_json, baseline_json, metrics_json, verified, approval_status, created_at)`, `audit_events(id, run_id, actor, event, payload_json, timestamp)`.

For approval/rejection comments, either use a `decisions` table or a single immutable decision record in `runs`, but **don't store both as competing truths**. If adding `overrides` table, it references child run; exact pin is also stored in run metadata. All database changes via schema initialization code/versioned migrations; agent should not hand-edit SQLite from outside the app.

```text
New scenario -> Validated -> RUN (DRAFT) -> APPROVED -> EXPORTED
                                     \---> REJECTED
                                     \---> OVERRIDE -> NEW child RUN (DRAFT)
```

## G. Architecture & delivery acceptance

**System context PDF:** Planner ↔ Nordic Flow MVP ↔ CSV input/output. Optionally LLM ↔ app, **only if actually called**. Inside app can separately show browser/API/core/SQLite in a second diagram or one carefully labelled diagram (≤2 pages). Company A ERP/WMS/TMS may be pictured as **future/external export sources/targets** with dashed “not connected in MVP” lines, not solid actual integrations.

**User Journey PDF:** actual demo path from synthetic data → validate → run → inspect → override → approve → export; mark exception path if fits ≤2 pages. Add concise actor, system action, outcome and trust gate.

**README:** require commands for fresh install, virtual environment, `pip install -r requirements.txt`, `pytest -q`, `uvicorn app.main:app --reload` or agreed equivalent, `http://localhost:8000`, synthetic dataset, and fallback/offline behaviour. Windows PowerShell notes if team develops on Windows.

**Before merging:** run unit tests and API tests, rerun golden + demo, manually replay video path; capture output in PR description. Test failures require code fixes, not deleting tests or changing the golden fixture's expected numbers.
