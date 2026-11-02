# Nordic Flow (team NEW AURA): IT Consultant Challenge 2026

Goods allocation across existing warehouses for "Company A" (Nordic building-materials retailer):
which supplier and which existing warehouse should serve each order, at the lowest total cost, with the planner approving every plan.

- **Round 1** (submitted): proposal deck, see `docs/round1/`.
- **Round 2** (current): build a working MVP. Deadline **22:00 (GMT+7), 9 Nov 2026**.

## Repository layout

```
mvp/             The application: core (nordic_flow/), API (api/), web UI (web/), tests, sample data. See mvp/README.md
docs/            Specification, plan and background
  MVP-SPEC-v0.1.md   (also .pdf, .docx)   What we build and how: read this first
  MVP-plan-7-days.md                       Day-by-day plan to 9 Nov
  round2/                                  Team decision drafts, contracts, and AS_BUILT.md (what the code does today)
  ai-usage-log.md                          Log of significant AI use (feeds the AI Journal)
  round1/                                  Submitted Round 1 proposal and verified evidence
  reference/                               Organiser material: Round 1 case, Round 2 brief, AI Journal template (confidential)
deliverables/    The five files we must send to the organiser (status in deliverables/README.md)
```

## Quick start

```bash
cd mvp
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest -q
uvicorn api.main:app --port 8000           # web app at http://localhost:8000
python -m nordic_flow run data/golden      # command line: Round 1 worked example 700 -> 500
```

## Rules for this repo

- Do not commit passwords, API keys or `.env` files. Use `.env.example` for variable names.
- Case material from the organiser is confidential: keep the repo private.
- Demo data is synthetic and must be labelled as such.
