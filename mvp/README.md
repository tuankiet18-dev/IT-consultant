# Nordic Flow MVP: solver core

Goods allocation across existing warehouses at lowest total cost (supplier -> warehouse -> customer zone).
This folder holds the optimisation core and its tests. The API, web UI, audit log and AI explainer are built on top (see `../docs/MVP-SPEC-v0.1.md` and `../docs/MVP-plan-7-days.md`).

## Run

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest -q                                              # 14 tests
python -m nordic_flow run data/golden                  # Round 1 slide-7 example: 700 -> 500
python -m nordic_flow synth data/demo                  # regenerate the synthetic demo data
python -m nordic_flow run data/demo --out out/demo     # baseline vs optimised, writes CSV and comparison.json
python -m nordic_flow run data/demo --mode lp          # continuous relaxation (lower bound)
```

## Model

- `x[s,w,p]`: pallets of SKU p, supplier s -> warehouse w. `y[w,z,p]`: warehouse w -> zone z.
- Minimise `(inbound + handling_in) * x + (outbound + handling_out) * y`.
- Subject to: supply per supplier and SKU; demand met exactly; flow balance at each warehouse (no stock carry-over);
  warehouse capacity in pallet-equivalents; allowed lanes and SKU eligibility.
- LP uses GLOP. MILP (whole pallets) uses SCIP. Both come with Google OR-Tools. Solver status is always returned
  (`OPTIMAL`, `FEASIBLE` when the time limit hits, `INFEASIBLE`).
- Fixed costs that do not change with the plan are not part of the objective, so they never appear as savings.

## Modules

| File | Role |
|---|---|
| `schema.py` | Dataset, Plan and Issue types |
| `io.py` | CSV loading with file/row-level errors |
| `validation.py` | Semantic checks; errors block a run |
| `baseline.py` | "Habit" rule: preferred warehouse, cheapest supplier first, spill when full |
| `optimiser.py` | LP/MILP with OR-Tools |
| `verify.py` | Independent constraint checker (does not use the solver) |
| `report.py` | Cost breakdown, utilisation, baseline-vs-optimised comparison |
| `diagnosis.py` | Why there is no plan: supply, capacity or lanes |
| `synth.py` | Synthetic demo data generator |
| `cli.py` | Command line |

## Input CSV files (one folder per scenario)

`suppliers`, `warehouses` (capacity_pallets, handling_in, handling_out), `zones` (preferred_warehouse), `skus` (pallet_factor),
`inbound_rates`, `outbound_rates`, `supply`, `demand`, optional `warehouse_skus` (SKU eligibility). Column names are checked on load.

## Honest limits

- Demo data is synthetic. The 4.2% saving on `data/demo` comes from how that data was built (the habit rule pays high
  inbound freight at the warehouse nearest the zones). It is not a forecast for Company A.
- One planning period, no inventory carry-over, linear costs, no vehicle routing.
- The Round 1 gate (at least 5% below a validated baseline) is for Company A's real data in Week 1.
