# Nordic Flow

Nordic Flow is the NEW AURA team's local MVP for IT Consultant Challenge 2026. It decides which supplier and which existing warehouse should serve each order at the lowest total cost, and a planner reviews and approves every plan. That is the Round 1 pilot: suppliers, existing warehouses and customer zones. Two optional extensions go beyond the pilot, transfers between existing warehouses and direct supplier-to-customer lanes. Pilot data uses neither. See `docs/round2/ROUND1-ALIGNMENT.md` for how the MVP maps to the Round 1 proposal.

Round 1 material is in `docs/round1/`. The Round 2 deadline is 22:00 GMT+7 on 9 November 2026.

## Start here

- `mvp/README.md` covers installation, samples, data files and the API.
- `docs/MVP-SPEC-v0.1.md` is the current specification, updated for multi-warehouse transfers.
- `docs/round2/01_CONTRACTS_AND_ARCHITECTURE.md` is the canonical input, optimisation and API contract.
- `docs/round2/AS_BUILT.md` describes the current implementation.
- `docs/round2/ROUND1-ALIGNMENT.md` maps the Round 1 proposal to what the MVP does, what it adds and what it does not claim.
- `deliverables/` contains the four submission files and their status in `deliverables/README.md`.

The Markdown specification and contract describe the current implementation, including direct delivery, multi-warehouse routing and the in-app guide. Existing DOCX/PDF files and submission artifacts are draft snapshots awaiting a final refresh after the MVP is agreed.

## Repository layout

```text
mvp/
  nordic_flow/     Python core, optimisation, verification and reporting
  api/             FastAPI, use cases, SQLite and audit
  frontend/        React and Vite source
  web/             Production frontend build served by FastAPI
  data/            Golden, synthetic demo and multi-warehouse examples
  tests/           Python tests and browser walkthrough
docs/
  reference/       Organiser case, brief and AI Journal template
  round1/          Submitted proposal and evidence
  round2/          Current contracts, implementation notes and test evidence
deliverables/      Submission PDFs, video and editable sources
```

## Quick start on Windows

```powershell
cd mvp
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m uvicorn api.main:app --port 8000
```

Open `http://localhost:8000`. Choose **Multi-warehouse example** for factory → A/B/C → D/E/F → customer, **Warehouse transfer chain** for supplier → HUB → REG → LOCAL, or **Worked example** for the hand-worked 700 to 500 case.

## Transfer input

The original eight required CSV files remain required. Optional `transfer_rates.csv` adds directed warehouse-to-warehouse links using `from_warehouse_id,to_warehouse_id,cost_per_pallet` and optional `max_pallets`. Every warehouse is listed in `warehouses.csv`. The declared transfer graph must be acyclic.

Optional `direct_rates.csv` adds genuine supplier-to-customer routes using `supplier_id,zone_id,cost_per_pallet` and optional `max_pallets`. No warehouse handling is charged. Open **User guide** in the app for every input column and downloadable ZIP cases for0/3/4/5/8/12 warehouses, plus mixed direct/warehouse delivery.

Capacity counts receipts at every visited warehouse. Costs include transfer freight and receiving/shipping handling. Detailed units, constraints, compatibility and examples are in the technical contract.

## Repository rules

- Keep passwords and API keys in environment variables. Use `mvp/.env.example` for variable names.
- Keep organiser case material private.
- Identify sample data as synthetic when presenting results.
