# AGENTS.md — AI CODING AGENT RULES (DRAFT, APPROVAL REQUIRED)

**Project:** NEW AURA / Nordic Flow / Round 2 Build-a-thon 2026.

## Read first

1. Official Round 1: `docs/round1/NEW AURA - Round 1 proposal.pdf` (private).
2. Round 2 organiser brief (private).
3. Approved `docs/round2/DECISIONS.md` and only the relevant sections of `docs/round2/CONTRACTS.md`. Architecture and tests are in those documents until separately extracted; do not assume other files exist.
4. `mvp/README.md`, existing `mvp/nordic_flow/` and tests.

## Immutable guardrails

- Problem remains supplier → existing warehouse → customer zone allocation; no VRP, forecasting, warehouse construction, ERP replacement, real-world integration, multi-country deployment.
- Dataset demo is **synthetic**; never claim savings or 5%/30%/OTIF are results measured at Company A.
- OR-Tools core is numeric authority; LLM cannot create cost figures, solve allocation or auto-approve plan.
- Both baseline and solution must meet full demand and pass independent verification before showing saving%; baseline invalid means `saving=null` and explicit warning.
- `OPTIMAL` and `FEASIBLE` must be distinguished; exact pin reruns solver and stores separate child run; approval does not execute logistics.
- No new framework, DB, service, route contract, schema or core mathematical objective without a team-reviewed ADR.
- No hardcoded secrets, `.env`, access tokens or sensitive organiser documents in public code, logging or external prompts. Repo stays private.

## Workflow per task

1. Read `AGENTS.md` and the **relevant** approved decision/contract sections; identify **one** feature ID. Avoid repeatedly loading unrelated long docs into every AI agent context.
2. State plan, exact files touched, dependencies, tests, acceptance and open questions BEFORE edits.
3. Keep smallest change. Do not rewrite an unrelated module or reorganise repository opportunistically.
4. Implement real logic, not hard-coded demo values. Mock only where documented and clearly labelled.
5. Run targeted tests, then full relevant suite; report verbatim pass/fail counts and actual commands.
6. Show changed files, design decisions, tests, unverified items and manual verification steps.
7. Open a small PR and request a human review; do not merge/push to `main` automatically.
8. Update `docs/round2/AI_USAGE_LOG.md` with **truthful** AI actions, estimated vs actual time, human reviewer, outcome.

## Required definition of done

- [ ] Contract unchanged or ADR approved
- [ ] Function works on actual local run, not just mocked screenshots
- [ ] Automated tests added/updated; golden 700→500 unchanged
- [ ] Baseline invalid case doesn't produce fabricated saving
- [ ] User-facing failures are understandable, no secrets or stack traces
- [ ] Another team member reviewed and re-ran key workflow
- [ ] Relevant docs & AI journal updated

## Bounded prompt template

> Implement feature [F-ID] only. Read team decisions/contracts and existing code first. Allowed files: [...]. Do not change API schema, CSV schema, mathematical objective, baseline validation, or approval semantics. Provide an implementation plan and proposed tests before writing. After changes, run [...], show exact output and list limitations. If requirements conflict, ask for a team decision instead of guessing.
