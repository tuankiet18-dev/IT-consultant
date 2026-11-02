# As built (2 Nov 2026): how the code relates to the team drafts

Read together with `00_TEAM_DECISIONS_DRAFT.md` and `01_CONTRACTS_AND_ARCHITECTURE.md`. Those documents are still drafts; this file says what the code does today so the team can accept, change or reject each point. Tests: 52 pytest cases pass; a Playwright walk-through of the whole UI journey ran with no browser errors.

## Review findings (G0-xx) and what was done

| Finding | Status |
|---|---|
| G0-01 invalid baseline gives fake savings | **Fixed.** Saving and saving % are `null` unless the baseline is feasible and verified; UI shows "unusable". Test: greedy-trap dataset (`tests/test_baseline_guards.py`) |
| G0-02 verifier accepted shortfall | **Fixed.** `verify_plan` is strict by default; only diagnosis may pass `allow_shortfall=True` |
| G0-03 baseline is a synthetic heuristic | **Done in wording.** UI and text say "preferred-warehouse baseline (synthetic rule, not Company A's actual plan)" |
| G0-04 diagnosis is approximate | **Done in wording.** Shown as "diagnostic hints (not a proof)" |
| G0-05 number whitelist is not enough for LLM text | **Partly.** Deterministic summary is the default; LLM is opt-in per request, labelled "AI draft", stays a draft until approved, KPIs sit on the Results tab. The number check is kept as one guard, not as proof of truth |
| G0-06 override semantics | **Fixed as EXACT** pin, whole pallets in MILP, reason required, child run. More than one pin per run is allowed |
| G0-07 synthetic mistaken for ROI | "Synthetic data" badge on every screen, footer note, no 5%/30%/OTIF claims |

## Decision register vs. code

| ID | Draft default | Code today |
|---|---|---|
| D01, D02 | Local web, FastAPI + Jinja2/HTML/vanilla JS + SQLite | **Same, except** no Jinja2: a static `web/index.html` calls the JSON API |
| D05 | Block savings on invalid baseline | Done |
| D06 | ZIP import of the CSVs | Done (flat, allow-listed names, size limits, no paths or links; tested). Multi-file upload also works |
| D07, D08 | One exact pin; approve/reject; export only if approved | Done; export returns 409 until approved |
| D09 | SQLite audit, no hash chain required | Audit is hash-chained and labelled "tamper-evident, not tamper-proof". Easy to drop if the team prefers |
| D10 | Deterministic explanation guaranteed; LLM optional; no automatic SKU mapping | Deterministic by default; Groq opt-in. SKU mapping exists as a **suggest-then-confirm** helper (not automatic) |
| D11 | Three stages | Six tabs: Data, Results, Plan, Review & adjust, Approve & audit, What-if |
| D13 | Freeze the API | The as-built API is listed in `mvp/README.md`; names differ from the draft (see below) |

## Differences from the contract draft (decide whether to rename)

- Folders: `mvp/api/` and `mvp/web/` instead of `mvp/app/` with `templates/` and `static/`.
- Paths: `POST /scenarios/sample` (not `/scenarios/demo`), `POST /scenarios` handles ZIP and CSV upload (not `/scenarios/import`), `POST /runs/{id}/overrides` (not `/override`), `time_limit` (not `time_limit_seconds`), approvals use lower-case `approve`/`reject`.
- Beyond P0 (P2 in the draft) and already built: what-if scenarios, SKU mapping helper, hash-chained audit. They are isolated modules; cut them from the demo if the video runs long.

## Not done

- The four submission files (video, user journey, system context diagram, AI Journal).
- Dependency pinning in `requirements.txt` (versions are lower bounds).
- A live call to Groq has never been run here; only a fake client is tested.
- Demo script and test plan documents.
