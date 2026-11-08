# Handoff: where the project stands (8 Nov 2026)

Project: NEW AURA, Nordic Flow, IT Consultant Challenge 2026 **Round 2 (build-a-thon)**. Deadline **22:00 GMT+7, Mon 9 Nov 2026**; aim to email by 18:00 (`docs/round2/EMAIL.md`).

Working branch: **`final-round2`**. Do not use `main` (old), `main-v1plz3` (earlier frozen build) or `codex/round2-mvp-routing-ux` (before the honesty fixes). New teammates start with `docs/round2/TEAMMATE-GUIDE.md`; to understand the whole system read `docs/HIEU-DU-AN.md`.

| Area | State |
|---|---|
| MVP (FastAPI, SQLite, OR-Tools, React + Tailwind web UI, English) | Done. 274 Python tests and 7 browser walk-throughs pass |
| Groq explanation | Checked live (`docs/round2/GROQ-CHECK.md`); optional, key only from `GROQ_API_KEY`; number guard and fallback in place |
| Robustness evidence | `docs/round2/ROBUSTNESS.md` (11 synthetic cases, 1.75% to 4.97%), `python -m nordic_flow demo-guard` |
| `deliverables/User Journey.pdf`, `System Context Diagram.pdf` | Done, 2 pages each, built from the final UI (`deliverables/src`, rebuild with `build_pdfs.js`) |
| `AI Journal.pdf` | Draft in `docs/round2/AI-Journal-DRAFT.docx`; real times still to be filled, then `deliverables/export-ai-journal.ps1` |
| `MVP.mp4` | Nhật Anh records it with `deliverables/video-kit/` (script: `docs/round2/VIDEO-SCRIPT.md`, 6:40) |
| Final check | `python deliverables/check-submission.py` |

## Run it

```powershell
cd mvp
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest -q                                   # 274 passed
.\.venv\Scripts\python.exe -m uvicorn api.main:app --port 8000            # http://localhost:8000
```
Optional AI: set `GROQ_API_KEY` (and `GROQ_MODEL`, default `openai/gpt-oss-120b`) in the environment before starting. Never write a key into a file.

## Things nobody may get wrong

- **Never report a saving against an unusable baseline.** The code returns `null` and the UI says "unusable".
- The baseline is a **synthetic preferred-warehouse rule**, not Company A's actual plan. All data is synthetic; costs are cost units. The 4.2% on the demo is not a forecast, and it is one of the highest of 11 synthetic cases (median 2.86%). It is not evidence that the Round 1 5% gate is met.
- **The LLM never calculates.** It rewrites facts computed in code, is opt-in, and stays a draft until a planner approves. The number guard does not prove the wording is right; a person reads it.
- No planner-time or OTIF result is claimed (not measured). No ERP, WMS or TMS integration is claimed.
- The audit log is hash-chained: call it **tamper-evident**, never tamper-proof.
- Transfers between warehouses and direct supplier-to-customer lanes are **optional extensions beyond the Round 1 pilot** (`docs/round2/ROUND1-ALIGNMENT.md`).
- No secrets in the repo. The Groq key pasted into chat on 4 Nov must be revoked. The team decided the repo may stay public; `docs/reference/` holds the organiser's confidential material, so do not add more.

## Repo map

```
README.md                  overview and quick start
mvp/                       the app: nordic_flow/ (core), api/, frontend/ (source), web/ (build), tests/, data/
docs/HIEU-DU-AN.md         full project guide (Vietnamese)
docs/round2/               plan, cases, video script, Round 1 alignment, evidence, teammate guide, email
docs/round1/               submitted Round 1 proposal
docs/reference/            organiser material (confidential)
deliverables/              the files to send, their sources, the video kit and the final check
```
