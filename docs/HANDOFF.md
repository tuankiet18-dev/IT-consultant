# Handoff: cloud session to local session (4 Nov 2026)

Paste or point the local Claude Code session at this file first. Everything below is in the repo; nothing important lives only in the cloud session.

## Where things stand

Project: NEW AURA, Nordic Flow, IT Consultant Challenge 2026 **Round 2 (build-a-thon)**. Deadline **22:00 GMT+7, Mon 9 Nov 2026**; aim to email by 18:00. Subject "Round 2 – NEW AURA" to EB.VN@netcompany.com. Round 1 proposal (submitted) is in `docs/round1/`.

Branch with all work: `main-v1plz3` (the default `main` is older and still holds Round 1 drafts). Last cloud commit: "Add User Journey and System Context Diagram PDFs with sources".

| Area | State |
|---|---|
| MVP (FastAPI + SQLite + OR-Tools + static web UI, English) | Built and working; 52 pytest cases pass; Playwright walk-through of the full journey ran with no browser errors |
| `deliverables/User Journey.pdf` | Draft done, 2 pages, built from screenshots of the running app |
| `deliverables/System Context Diagram.pdf` | Draft done, 2 pages |
| `AI Journal.pdf` | **Not started.** Template: `docs/reference/AI Journal template.docx`. `docs/ai-usage-log.md` has rows but the time columns are empty (only the team knows real times) |
| `MVP.mp4` (max 7 min, English) | **Not started.** Script idea in `docs/MVP-plan-7-days.md` section 7 and `docs/round2/00_TEAM_DECISIONS_DRAFT.md` section 9 |
| Groq (LLM) | **Never run against the live service** (no key and restricted network in the cloud). Only tested with a fake client |
| Team decisions | Teammate drafts in `docs/round2/` (D01-D16) are still OPEN. `docs/round2/AS_BUILT.md` lists where the code differs from them |

## Run it locally

```bash
git fetch origin && git checkout main-v1plz3 && git pull
cd mvp
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pytest -q                                              # expect 52 passed
export GROQ_API_KEY=...                                # optional; Windows PowerShell: $env:GROQ_API_KEY="..."
uvicorn api.main:app --port 8000                       # http://localhost:8000
```

Free Groq key: console.groq.com/keys. Model is set by `GROQ_MODEL` (default `openai/gpt-oss-120b`, verified live on 4 Nov 2026; `llama-3.3-70b-versatile` was no longer available; free-tier names change, so check the console if the call returns an error). The "Generate with AI (Groq)" button only enables when a key is present.

## What to do next, in order

1. **Install and run on your own machine**, click through the six tabs, and fix anything that breaks (Windows or Mac issues are the main unknown; nobody but the cloud session has run it).
2. **Try Groq once** with a real key: Review & adjust, "Generate with AI". Check that it returns text, that the "AI draft" tag appears, and that a made-up number would be rejected. If the model name is wrong, set `GROQ_MODEL`.
3. **Ask teammates to decide** the open items in `docs/round2/AS_BUILT.md`: folder and path names, whether to keep the extras (what-if, SKU mapping helper, hash-chained audit), roles. Fill the role table in `docs/MVP-SPEC-v0.1.md` section 15.
4. **Fill `docs/ai-usage-log.md`** with real estimated and actual times, then complete the AI Journal template and save it as `deliverables/AI Journal.pdf`. The template allows at most 5 logged tasks, a 150-word strategy, 2-3 key decisions, and four short reflections.
5. **Record `MVP.mp4`** (screen recording plus narration or subtitles, max 7 min). Must say what changed since Round 1 (synthetic data, what-if and audit added, no learning-from-overrides, no ERP link). Suggested path: demo data, run, results, plan, explanation, exact pallet decision (Zone 1, Cement standard, Warehouse B, 8 pallets, with reason), approve, export, then what-if "close Warehouse A" (shows an infeasible case with hints).
6. **Rebuild the two PDFs** if the UI or architecture changes: `cd deliverables/src && NODE_PATH=$(npm root -g) node build_pdfs.js` (needs Playwright + Chromium, and the app running on port 8766 only for re-capturing screenshots; see `mvp/tests/e2e_ui.js` for the walk-through).
7. **Final checks before emailing:** files open, short clear names (`MVP.mp4`, `User Journey.pdf`, `System Context Diagram.pdf`, `AI Journal.pdf`), no keys or passwords anywhere, email sent before 18:00 with a Sent copy saved.

## Things the next session must not get wrong

- **Never report a saving against an unusable baseline.** The code returns `null` and the UI says "unusable"; keep it that way.
- **The baseline is a synthetic preferred-warehouse rule**, not Company A's actual plan. All data is synthetic; costs are "cost units". The ~4.2% saving on the demo data comes from how the data was built; it is not a forecast and not evidence that the Round 1 5% gate is met.
- **The LLM never calculates.** It only phrases facts computed in code, is opt-in per request, stays a draft until the planner approves, and falls back to the deterministic summary on any problem.
- **No secrets in the repo** (`.env` is git-ignored; use `mvp/.env.example` for names only). The Round 1 and Round 2 organiser PDFs are confidential, so keep the repo private.
- **Do not claim ERP/WMS/TMS integration.** The system context diagram draws it dashed and "not connected".
- Audit log is hash-chained: call it "tamper-evident", never "tamper-proof".

## Repo map

```
README.md                  overview and quick start
mvp/                       the app: nordic_flow/ (core), api/ (FastAPI, SQLite, audit), web/ (UI), tests/, data/
docs/MVP-SPEC-v0.1.md      specification (also .pdf, .docx); docs/MVP-plan-7-days.md the day plan
docs/round2/               teammate decision drafts, contracts, AGENTS draft, AS_BUILT.md
docs/round1/               submitted Round 1 deck and verified evidence
docs/reference/            organiser material (confidential): Round 1 case, Round 2 brief, AI Journal template
deliverables/              files to send; src/ holds the HTML and screenshots used to build the PDFs
```

## Environment notes (cloud vs local)

- The cloud session used a throwaway virtualenv outside the repo; it is not needed locally. `mvp/var/` (SQLite file) and `mvp/out/` are git-ignored.
- Python 3.11+ is fine (cloud used 3.13; OR-Tools 9.15 installed there).
- The cloud had no live Groq access. Anything involving the real Groq call is untested.
- `pip install` pulls the latest compatible versions (`requirements.txt` has lower bounds only); pin them after the first green install if you want a reproducible setup.
