# NEW AURA — ROUND 2 TEAM DECISIONS & IMPLEMENTATION BLUEPRINT

**Version:** 0.2 — TEAM REVIEW DRAFT, not approved  
**Prepared:** 02 Nov 2026  
**Deadline:** 22:00 GMT+7, 09 Nov 2026. Internal target: submit by 18:00.  
**Purpose:** agree on product scope, architecture, contracts, verification and working rules BEFORE AI agents implement new modules.  
**Confidentiality:** keep organiser's case, solution and raw files in the team's private repository; do not publish or upload secrets.

## 0. Source hierarchy and status legend

**Source of truth, in priority order:** (1) `NEW-AURA.pdf` *actually submitted* in Round 1; (2) `IT Consultant Challenge 2026 - Round 2.pdf`; (3) `AI JOURNAL TEMPLATE.docx`; (4) the repository's current code and executable tests; (5) `docs/MVP-SPEC-v0.1.md` and `docs/MVP-plan-7-days.md` as **drafts**, not an approved contract. The new `NEW-AURA.pdf` exactly matches the Round 1 proposal PDF stored in the ZIP (verified SHA-256). Anything proposed in this document remains **UNAPPROVED until the three-person team signs off**.

- **FACT (R1)** = stated in submitted Round 1 proposal. May be an *assumption in that proposal*, not an observed Company A fact.
- **FACT (BTC)** = organiser's Round 2 requirement.
- **IMPLEMENTED** = code exists in the shared ZIP. This does not automatically mean integration or tests have been executed successfully here.
- **PROPOSED** = this review's team recommendation, subject to approval.
- **OPEN** = decision or real-world information not yet settled.

### Traceability to Round 1 (preserve or explicitly explain a deviation)

| ID | Official submitted commitment | Source | Round 2 implication |
|---|---|---|---|
| R1-01 | Optimise supply → **existing** warehouses → order zones; total *variable* inbound + handling + outbound costs | R1 slides 1, 4, 6 | Keep mathematical model; do not claim warehouse construction, VRP or ERP replacement |
| R1-02 | Illustrative Swedish pilot: **one region, 2 suppliers, 3 warehouses, 20 palletised SKUs, weekly planning** | R1 slide 4 | Synthetic demo should mirror these dimensions; 6 zones may be a demo-specific assumption |
| R1-03 | Planner reviews/approves; changes/overrides logged; exports plan; no automatic execution | R1 slides 4–5 | Approval and at least a limited auditable override should be demonstrated |
| R1-04 | LP/MILP; hard constraints supply, demand, capacity, allowed lanes, SKU eligibility; status visible | R1 slide 6 | Deterministic numerical engine + independent verifier |
| R1-05 | AI for data mapping, plain-language explanation; learning from corrections later | R1 slide 6 | Explain any deferred runtime AI capability, and ensure human validation |
| R1-06 | 700 → 500 (=28.6%) **synthetic** illustration; not Company A savings | R1 slide 7 | Golden test must match; always label numbers as synthetic |
| R1-07 | Real pilot hypotheses: cost ≥5% better vs validated feasible baseline, planner prep time ≥30% lower, OTIF not deteriorate, 0 hard violations | R1 slide 8 | Build-a-thon can demonstrate computed cost + feasibility; cannot honestly assert actual time/OTIF outcome |
| R1-08 | Sweden first is conditional on Week-1 discovery, then other markets | R1 slides 9–10 | Local synthetic MVP is NOT the 8-week commercial pilot; country rollout is future plan |

### Round 2 deliverables and judging

- `MVP.mp4` — **max 7 minutes**; explanatory narration/on-screen text; English recommended. Demonstrate actual running Web/Mobile/Desktop app. Local is acceptable; not production-ready. Explain any changes vs Round 1. (BTC slides 4, 6)
- `User Journey.pdf` — **max 2 pages**, at least one genuine end-to-end path (BTC slide 7).
- `System Context Diagram.pdf` — **max 2 pages**, show actual MVP system boundary, external actors/systems and interactions (BTC slide 8).
- `AI Journal.pdf` — complete organiser template; strategy ≤150 words; usage log ≤5 tasks; 2–3 decisions; reflections 2–4 sentences each (BTC slide 10 + template).
- Email **EB.VN@netcompany.com**, subject `Round 2 – New Aura` **if this is the registered team name**; deadline 22:00 GMT+7 09 Nov 2026; check access and no keys/passwords/confidential information in submitted files (BTC slides 12–13).
- Judged on engineering quality, reasonable architecture, appropriate AI usage with **human validation**, clear technical reasoning aligned to Round 1. No published weights (BTC slide 15).

## 1. Current repository audit — verified from shared ZIP, 02 Nov

**Implemented in `mvp/nordic_flow/`:** domain dataclasses, CSV loader, validation, greedy preferred-warehouse baseline, OR-Tools LP/MILP optimiser, independent plan verifier, high-level diagnosis, cost reports, synthetic generator, CLI, golden/demo data. Test files **define 14 test cases**; tests were **not rerun successfully in this review environment** because `ortools` was unavailable. `requirements.txt` currently uses unpinned `ortools>=9.10`, `pytest>=8.0`.

**Not found as working features in ZIP:** FastAPI app, frontend, SQLite storage, user-approved plan workflow, planner override/re-solve, audit event persistence, runtime LLM explanation, Round 2 submission artifacts. The existing `docs/MVP-SPEC-v0.1.md` is a detailed proposal, **not evidence that features F-08–F-16 work**.

### Highest-risk core issues (fix before UI integration)

| Risk | Evidence in code | Required gate |
|---|---|---|
| **G0-01: invalid baseline can produce fake savings** | `baseline.py` can return `BASELINE_INFEASIBLE` with `shortfall`; `cli.py` calls `compare(...)` without first rejecting it; `verify.py` treats `shortfall` as making demand appear met | Never report cost saving unless **both** baseline and optimised plans fulfil **100% demand** and pass independent verification, under identical scope/cost/rules. Add adversarial test where greedy baseline fails but solver succeeds |
| **G0-02: `verify_plan` accepts unmet demand via shortfall** | `verify.py`: `got = dem.get(k,0) + plan.shortfall.get(k,0)` | For any plan used as approved/exported/compared, require `shortfall==0`; diagnosis-only relaxed solutions must never be an approvable plan |
| **G0-03: “current allocation” is a synthetic heuristic** | Baseline follows preferred warehouse, not imported Company A's actual historical plan | UI label: **“Synthetic preferred-warehouse baseline”**; never call it *Company A current cost*. Future actual baseline requires company-approved plan import or operational data |
| **G0-04: infeasibility explanation is approximate** | `diagnosis.py` computes broad likely causes, not a proof of unique root cause | Label “likely causes / diagnostic hints,” not guaranteed root-cause diagnosis; guard failed/timeout status |
| **G0-05: numeric-verification for LLM is insufficient in spec** | Spec says reject numbers not in facts; simplistic matching may accept wrong relationships or wrongly reject SKU IDs | Prefer deterministic fact template. Optional LLM adds prose only; facts displayed from code; don't present AI statements as validated solely by a number whitelist |
| **G0-06: override semantics ambiguous** | Draft uses `y[warehouse,zone,SKU] = quantity`; “pin 20 pallets” might mean exactly 20 or at least 20 | Decide **EXACT** pin and show in UI; validate and re-solve; don't silently mutate original plan; create child run |
| **G0-07: demos can be mistaken for actual commercial ROI** | `data/demo` synthetic ~4.2% (per README), golden 28.6% | Always display “Synthetic example — not a forecast”; don't claim Round 1 ≥5% real-pilot gate is attained |

**Recommendation:** G0-01 to G0-03 are blocking issues for a trustworthy MVP. Fix them before new API or UI starts displaying financial results.

## 2. Team decision register (each item must receive Owner + Accepted/Modified/Rejected)

| ID | Decision | Default recommendation | Why / trade-off | Team status |
|---|---|---|---|---|
| D01 | **MVP medium** | **Local web app**, not cloud | Explicitly allowed by BTC; avoids deployment/network overhead | OPEN |
| D02 | **Technical stack** | Python + **FastAPI + Jinja2/HTML/CSS + vanilla JS + SQLite + OR-Tools + pytest** | One server, no Node/React build; keeps Python core isolated; supports parallel agents through API contract. Streamlit only as fallback if no one can own HTML/JS | OPEN |
| D03 | **Business scope** | Sweden single-region synthetic scenario: 2 suppliers, 3 warehouses, 20 SKUs, 6 zones, one weekly run | Faithful to R1; 6 zones merely demo setting | OPEN |
| D04 | **Core solver** | Preserve current Python `nordic_flow`; MILP as default, LP demonstrative/optional | Existing work; fewer rewrites; integer pallets in actual user journey | OPEN |
| D05 | **Baseline correctness** | Only compare **feasible verified** baseline and optimisation; block savings otherwise | Trustworthiness is more important than displaying a savings figure | OPEN |
| D06 | **Input workflow** | `Load demo` must work; CSV import by one **ZIP containing 8 named CSVs** (optional 9th); reject malicious archives, invalid names and files | Browser-friendly, reduces eight-click upload friction; backend reuses current loader | OPEN |
| D07 | **Planner override** | Exactly ONE `warehouse/zone/SKU/whole-pallet quantity` pin; rerun and show new cost; required reason | Protects core R1 promise without sophisticated editing UI; explicitly label EXACT semantics | OPEN |
| D08 | **Approval** | Single simulated planner, Approve/Reject with reason; immutable run snapshots; export only approved plan | Demonstrates human oversight; no production login | OPEN |
| D09 | **Audit & storage** | SQLite for scenario metadata, run snapshots, decisions, audit events; append-only through application code, no hash-chain requirement | Enough for Round 2; no claim of tamper-proof persistence | OPEN |
| D10 | **Runtime AI** | Deterministic, fact-grounded explanation guaranteed; optional LLM narrative behind feature flag; no automatic SKU mapping | Preserves demo offline. AI during development is documented regardless; runtime LLM may be postponed **with explicit R1 deviation** | OPEN |
| D11 | **UI** | Three stages: Input/Validate → Compare/Inspect → Review/Approve/Export | Easier to build/film than six disconnected pages | OPEN |
| D12 | **Data truth** | One dataset snapshot per scenario; cost units/pallet, pallet-equivalent capacity, one weekly horizon; no inventory carry-over | Matches the existing model and prevents inconsistent cost math | OPEN |
| D13 | **API contract** | Freeze request/response shapes (see `01_CONTRACTS_AND_ARCHITECTURE.md`) before parallel agent coding | Biggest protection against AI agents building incompatible pieces | OPEN |
| D14 | **Quality gates** | Golden 700→500, synthetic dataset size, invalid-data cases, baseline infeasible, approval/export, full E2E | Reliable judges' demo vs polished mockup | OPEN |
| D15 | **Feature freeze** | Functional freeze 06 Nov; docs & video 07–08 Nov; submit by 18:00 09 Nov | Leaves buffer for demo/video and final checks | OPEN |
| D16 | **Roles / merge policy** | Core QA, API/persistence, UI/docs/video owners; one integrator and reviewer for each PR | Prevents 3 parallel agents from editing the same files | OPEN |

### 2.1. Critical product scope — recommended P0/P1/P2

**P0 — shipping gate (must actually work):**
1. Load deterministic synthetic demo; optionally import ZIP of 8 required CSV files and validate content with file/row errors.
2. Compute and independently verify **baseline and optimised** plans; when baseline infeasible, **hide percentage saving** and show warning.
3. Show MILP status (OPTIMAL/FEASIBLE/INFEASIBLE/ERROR), total/leg costs, per-warehouse utilisation and selected outbound/inbound allocation changes. Never label FEASIBLE as OPTIMAL.
4. Perform one exact planner override with reason, re-optimise under pin and verify; record as *child run*; explain incremental cost vs original optimum.
5. Simulated planner Approve/Reject + optional comment; approved run immutable; export approved inbound/outbound CSV.
6. Persist minimal audit trail, scenario/run IDs and synthetic source label. UI runs locally end to end.

**P1 — if P0 end-to-end is green:** deterministic narrative explainer; LLM-assisted explanation with explicit badge `AI draft` and planner validation; one failure scenario; clearer charts.

**P2 — not for this week unless unexpected spare capacity:** AI SKU mapping, learning from overrides, advanced what-if, roles/auth, real ERP integrations, audit hash chain, cloud deployment, multi-country UI, forecasting, VRP.

**Trade-off to agree:** R1 slide 6 mentions AI explanations and data mapping. Downgrading runtime AI features is a deliberate MVP simplification; document the deviation in the video. Appropriate AI usage can be demonstrated in engineering workflow + AI Journal with human testing, but do not pretend a deterministic template is an LLM feature.

## 3. Requirements and state semantics to freeze

### 3.1. Scenario / run / approval

- `Scenario`: immutable imported or demo **dataset snapshot**, source=`synthetic_demo` or `uploaded_csv`; `scenario_id`, `dataset_hash`, timestamps. No actual Company A data assumed.
- `Run`: immutable output from baseline/optimiser with `run_id`, `scenario_id`, `parent_run_id` (for override), mode=`milp`, status, solver seconds, verified flags, cost report, allocation and reason for any override.
- `Decision`: `DRAFT` → `APPROVED` or `REJECTED`; approval freezes *that run*, not all scenarios. A new override produces a different run and requires new approval.
- `AuditEvent`: timestamp, actor=`demo_planner` or `system`, event, scenario/run IDs, concise metadata; append-only in application logic. **Do not call this tamper-proof** unless such guarantees are actually built and verified.
- No live ERP writeback. Exported CSV is a proposed plan **for later execution by existing systems**, not evidence of a successful logistics shipment.

### 3.2. Cost comparison contract

- `baseline_valid = baseline.status == BASELINE AND shortfall empty AND verify_plan(baseline) == []`.
- `opt_valid = opt.status in {OPTIMAL, FEASIBLE} AND shortfall empty AND verify_plan(opt) == []`.
- `saving` and `saving_pct` are populated **only** when `baseline_valid && opt_valid` for the same scenario, model and period; otherwise `null`, with a transparent reason. No negative-value cleanup or silent fallback.
- Never use relaxed diagnosis plans as baseline or approved plans.
- “Optimised” means a proven **global optimum** only when status `OPTIMAL`; otherwise label “feasible within time limit.”
- Historical company savings, planner time gains and OTIF improvement are **not measured** in this MVP.

### 3.3. Input and security

- Required file names: `suppliers.csv`, `warehouses.csv`, `zones.csv`, `skus.csv`, `inbound_rates.csv`, `outbound_rates.csv`, `supply.csv`, `demand.csv`. Optional: `warehouse_skus.csv`.
- Only accept ZIP file with allowlisted CSV basenames; reject traversal paths (`../`), nested files, symlinks, unexpected extensions, oversized archive, duplicate file names and invalid CSV content. Do not permit arbitrary filesystem paths from the client.
- Quantity in pallets; capacity in pallet-equivalents; costs in **synthetic cost units/pallet**. Do not attach € or SEK labels to artificial data unless sources genuinely define them.
- Do not allow browser to directly modify SQLite or the solver internals. All business checks happen in backend.

## 4. One clear User Journey (also the video backbone)

1. Planner chooses **Load synthetic demo** (or imports a CSV ZIP); sees the dimension and “Synthetic” label.
2. System validates inputs. Show a separate deliberately invalid file to demonstrate a blocked run if time permits; then reset the valid demo.
3. Planner clicks **Run optimisation**; system calculates baseline, MILP result and independently verifies both.
4. Dashboard shows cost and constraints. If baseline invalid, show warning instead of any saving figure.
5. Planner opens one allocation change and uses **Pin exactly N pallets** with a reason; backend re-solves as child run and shows the new cost and verifier status.
6. Planner **approves** a valid run; review & audit events are visible; export becomes available.
7. Planner downloads planned inbound/outbound CSV. Explain: ERP/WMS/TMS remain external and **are not connected to the local prototype**.

**What must be visible in demo video:** core solver runs for real; proof of feasibility; human approval; export; architecture; the exact difference between synthetic build-a-thon and future Swedish 8-week business pilot.

## 5. Documentation sequence — minimise churn

**Do not ask agents to produce 12 reports.** Begin with `DECISIONS.md` and `CONTRACTS.md` (both supplied here), plus `AGENTS.md`. Extract the additional files below only when their content becomes concrete; do not create empty placeholder documents. For each AI task, load only the relevant sections:

| File | Owner | Why it exists | Freeze point |
|---|---|---|---|
| `docs/round2/DECISIONS.md` (this file after approval) | Product owner / team | approved scope, rejected options, ADR links, owners | **before coding** |
| `docs/round2/CONTRACTS.md` | Core + backend owners | CSV schema, API endpoints, statuses, example payloads, error schema | **before UI and API diverge** |
| `docs/round2/ARCHITECTURE.md` | Backend owner | system boundary, components, data flow, persistence, AI, local start | after contracts |
| `docs/round2/TEST_PLAN.md` | QA owner | golden/negative/E2E acceptance cases | alongside implementation |
| `docs/round2/AI_USAGE_LOG.md` | everyone | factual AI contributions, original and actual times, human validation | continuously |
| `README.md` | integrator | environment, install, one-command run, demo steps | updated every integration |

**Only after MVP integration is stable:** create final `User Journey.pdf`, `System Context Diagram.pdf`, `AI Journal.pdf`, `MVP.mp4`. The final two diagrams must show **what actually runs**, not architecture promised but absent.

## 6. Roles and parallel work — a 3-person default

| Role placeholder | Ownership | Must not edit | Acceptance |
|---|---|---|---|
| **Core & Solver Owner** | `mvp/nordic_flow/*`; baseline fix, override constraint, golden/negative tests | UI templates, SQLite schema except agreed API contract | CLI golden, baseline invalid gate, independent verifier tests pass |
| **Backend / Integrator Owner** | `mvp/app/*` API, SQLite, snapshots, state machine, export, local startup | math core except reviewed bug fixes | API tests pass; test local server end-to-end |
| **UI / Delivery & QA Owner** | templates/static, user journey, system diagram, video, AI Journal compilation; own acceptance scenarios | solver internals, DB schema | clickable flow works; files match reality; narrative stays within 7m |

**Every person must be able to defend the core mathematical decision.** Suggested owner for the user: **Solution/QA + delivery docs**, while another engineer owns the solver and another API; move UI tasks if existing frontend skills differ. No personal names should be assigned until team confirms.

**One integrator** reviews every merge on a stable integration branch; PRs require another team member's review. Agents never push to `main` and never rewrite other people's contracts without an ADR update.

## 7. Seven-day critical path and completion gates

| Date (GMT+7) | Outcome | Exit gate |
|---|---|---|
| **02 Nov** | Read official R1, R2, inspect repo, agree D01–D16, name owners and freeze API/schema | one decision record, everyone acknowledges boundaries |
| **03 Nov** | Fix baseline correctness, solver tests; scaffold FastAPI + SQLite; UI mock using frozen contract | golden test and invalid baseline test pass; API returns real core result |
| **04 Nov** | Integrate UI import/demo, validate, optimise, compare; run single server | first real UI end-to-end compute (without approval) |
| **05 Nov** | Override as child run, approval state, audit events, export | full P0 user journey green |
| **06 Nov** | Automated tests, review security, AI explanation optional, **feature freeze** | another team member performs E2E, no false savings |
| **07 Nov** | Draft User Journey & System Context from actual app; capture screen demo; fill journal | four draft deliverables, max-page/length checks |
| **08 Nov** | Film final demo, verify all materials, dry run offline, run fresh install | no missing assets/API keys; all artifacts play/open |
| **09 Nov** | Buffer, final sign-off, email submission by **18:00**, save Sent proof | before official **22:00 deadline** |

If the 05 Nov full flow is not green, **cut P1/P2 immediately**, not tests or correctness. If internet/LLM fails, deterministic explanation stays functional.

## 8. Test matrix and non-negotiable acceptance

| ID | Input / action | Expected result |
|---|---|---|
| T01 | Golden case | Baseline **700**, optimum **500**, saving 200 cost units (28.5714%), both verified |
| T02 | Synthetic demo | 2 suppliers / 3 warehouses / 6 zones / 20 SKUs; solver returns verified feasible plan |
| T03 | Invalid header, number, unknown SKU, negative rate | blocked with file/row (where known); no run |
| T04 | Insufficient supply/capacity/route | blocked or flagged infeasible; **no fake 0 cost or fake % saving** |
| T05 | Construct case greedy baseline cannot fulfill but solver can | baseline marked **unusable**; optimized plan can display, **saving null** |
| T06 | LP & MILP | no `OPTIMAL` label for `FEASIBLE`; integer pallets for MILP |
| T07 | Planner pin feasible quantity exactly | new child run; respects the pin; verified; cost delta shown |
| T08 | Planner pin impossible quantity | explicit rejection; original plan unmodified |
| T09 | Approve valid run | approved run frozen; export allowed; audit recorded |
| T10 | Reject or unapproved run | no approved export; correct status |
| T11 | Repeat inputs/parameters | equivalent costs/constraints within tolerance |
| T12 | Malicious or unexpected ZIP file | no traversal, arbitrary read or crash; clear error |
| T13 | Open browser in fresh local installation | a colleague reproduces start and core flow using README |
| T14 | Optional runtime AI returns incorrect claim | deterministic fallback or manual rejection; no invented numerical fact used as business proof |

**Definition of Done for feature:** code + tests + docs/API contract updated + reviewer evidence + no unrelated file edits. UI screenshot alone does NOT mean feature done.

## 9. Video story (target ~6:30, stay ≤7:00)

| Time | Narrative | On screen |
|---|---|---|
| 0:00–0:40 | Company A allocation pain and Round 1 proposed method | simplified suppliers → warehouses → zones |
| 0:40–1:10 | Explain Round 2 scope changes; synthetic demo not real pilot | labeled assumptions |
| 1:10–2:00 | Load/validate scenario | actual app + data summary |
| 2:00–3:30 | Run MILP, show baseline vs lower-cost verified plan | status, costs by leg, chosen allocation |
| 3:30–4:35 | Planner exact pin, re-solve, inspect cost/feasibility | child run and new comparison |
| 4:35–5:15 | Approve and export | audit and downloaded CSV |
| 5:15–6:10 | Context architecture, OR-Tools vs LLM, boundaries | diagram matching actual implementation |
| 6:10–6:30 | Limitations and next real pilot measurements | cost ≥5%, prep time ≥30%, OTIF, 0 violations: **future hypotheses**, not achieved claims |

Use English narration or English subtitles; ensure final **MP4**, max 7 minutes.

## 10. AI-supported vibe coding rules

1. **Human-owned contracts first.** Agent may propose changes but cannot silently re-scope features, schemas or API.
2. **One task per agent at a time:** known files, exact inputs/outputs, acceptance tests, prohibited edits.
3. **Three independent owners, one integration point:** make small PRs; avoid two agents editing the same file.
4. **Do not hallucinate test outcomes.** Agent reports exact commands, logs, changed files and unverified areas. `pytest` pass only if executed successfully.
5. **No fake data provenance:** synthetic remains labeled; 700→500 is illustrative. No savings claim on infeasible baseline.
6. **Security:** no `.env`, API keys, judge email, case documents in public apps/logs; avoid exposing raw confidential materials to unnecessary external AI providers.
7. **Use existing components.** No rewriting solver in JS, no new DB/framework/cloud/auth unless team signs an ADR.
8. **No code-only completion.** Need executable UI and documented user journey consistent with judged video.
9. **AI engineering journal is factual:** record what agent did, original time estimate, actual time, reviewer, corrections/rejections. Do not invent estimates retrospectively.
10. **Decision changes need a 4-line ADR:** context; alternatives; decision and reason; impact on MVP, API and documentation.

Reusable narrow task prompt:

> You are implementing Nordic Flow Round 2 on top of an existing private Python repository. Read `AGENTS.md` and the **relevant** sections of approved `DECISIONS.md` and `CONTRACTS.md` first. Scope ONLY [feature/ID]. Allowed files: [paths]. Prohibited: change API/CSV schema/solver objective, bypass verification, claim real Company A savings, edit unrelated modules, add dependencies without approval. Implement with tests [IDs]. Run [commands]. Return changed files, test outputs, risks, and a concise human-review checklist. If an agreed contract is insufficient, STOP and propose an ADR before coding.

## 11. Team sign-off form (copy into README or issue)

| Decision | Selected value | Owner | Date | Status |
|---|---|---|---|---|
| D01–D04 medium/stack/scope/core | TBD | TBD | TBD | OPEN |
| D05–D08 baseline/input/override/approval | TBD | TBD | TBD | OPEN |
| D09–D13 storage/AI/UI/data/contracts | TBD | TBD | TBD | OPEN |
| D14–D16 tests/freeze/roles | TBD | TBD | TBD | OPEN |

**Gate for implementation:** a single person makes a concrete proposal for any decision that remains open; all 3 confirm deviations from these defaults in the same log. Don't delay solver bugfixes or existing tests while discussing visual polish.
