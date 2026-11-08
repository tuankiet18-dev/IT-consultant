# Nordic Flow MVP

Nordic Flow decides which supplier and which existing warehouse should serve each customer zone, at the lowest transport and handling cost subject to supply, demand, warehouse and lane limits. A planner reviews and approves the result. This is the Round 1 pilot scope. Optional extensions, enabled only by extra input files, allow transfers between existing warehouses (`transfer_rates.csv`) and direct supplier-to-customer lanes (`direct_rates.csv`); the pilot data uses neither.

The local app uses FastAPI, SQLite, OR-Tools and a React interface built with Vite. The checked-in `web/` build is served by Python. The current specification is `../docs/MVP-SPEC-v0.1.md`, and the detailed input/API contract is `../docs/round2/01_CONTRACTS_AND_ARCHITECTURE.md`.

## Run on Windows

From the repository root in PowerShell

```powershell
cd mvp
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m uvicorn api.main:app --port 8000
```

Open `http://localhost:8000`. Python 3.11.4 has been used for Windows validation. On macOS/Linux, activate a virtual environment and use the corresponding `python`, `pip`, `pytest` and `uvicorn` commands.

For optional Groq wording, set `GROQ_API_KEY` in the server environment before starting. Use `GROQ_MODEL` to select a different model. The standard summary remains available through its own button. Model access errors or rejected numeric tokens trigger that summary as a fallback.

## Planning workflow

1. **Data** loads Synthetic demo, Worked example, Multi-warehouse example, Warehouse transfer chain, or uploaded CSVs/ZIP. After loading, the source picker collapses under **Change data**. The selected scenario, checks and Calculate action remain visible. The Multi-warehouse example previews all candidate routes before calculation.
2. **Results** compares the preferred-warehouse baseline with the optimised plan. KPIs, the flow diagram and full-path ranking stay visible; cost breakdown, warehouse load and allocation details expand on demand. The diagram shows selected flows in colour, unused options in grey dashes and locally unavailable links in red dashes. Line width represents volume, not cost. **Create manual route** opens a focused editor containing only route adjustments; saving returns to a new Results version. **Back to Results** discards unsaved form input.
3. **Review & approve** shows explanation, read-only manual decisions, approval/rejection and approved exports. It contains no route or final-warehouse edit form. **Adjust plan** opens either the manual-route editor or a separate delivery-warehouse editor. Manual decisions and version history use disclosures. Opening a previous version reloads that version's saved explanation. The export button appears after approval.
4. **Audit trail** shows scenario and run events.
5. **What-if** tests warehouse closures, capacity changes and demand changes on copied data.

**User guide** is available in the sidebar even before data loads, or through **Input format guide** on Data. It explains the workflow, every CSV column/type/unit, UTF-8/comma/ZIP rules, errors, limitations and downloadable cases. Guidance is in Vietnamese with exact English field names. The guide's CSV sample headers are checked against the real parser.

`Serve from` pins the final warehouse delivering to the customer zone. Upstream suppliers and intermediate warehouses are selected by the optimiser around that decision.

`Create manual route` chooses a supplier, ordered warehouse stops, customer zone, SKU and pallet quantity. Each complete path reserves at least that quantity on its legs; the optimiser allocates remaining demand around all reservations. Multiple routes add their reserved quantities on shared legs. Supply, demand, capacities, eligibility and existing final-delivery pins still apply. A required reason is recorded without changing rates. A negotiated price must be entered in the input rates. Saving or removing a manual route creates a child run, preserves the original and shows the total cost difference. Approved/rejected plans stay locked.

The **Complete route cost ranking** below the diagram sorts full supplier-to-customer paths by freight plus handling per pallet. Filter by customer/product and choose a comparison quantity. Rows show a standalone capacity limit, a quantity quote only when that quantity fits, and an accounting of the current plan's path quantities/costs. For branching, the plan accounts for A→D six pallets at42 plus B→E six at60, totalling102. Select a row to preview exactly that full path in amber, revealing unused nodes if needed; this does not change shipments. Capacity limits ignore competing allocations. Where goods merge, path quantities are an accounting decomposition, not physical pallet tracking.

Warehouse letters do not determine stage. A declared factory→E→A→customer network is supported; upload `data/testcases/09_reordered_warehouses.zip` to try it (156 cost units for twelve pallets). Every required lane must exist. The MVP still requires an acyclic transfer graph, so adding E→A while retaining A→E is rejected as a cycle.

## Input files and transfers

Eight CSV files are required.

| File | Columns |
|---|---|
| `suppliers.csv` | supplier_id, name |
| `warehouses.csv` | warehouse_id, name, capacity_pallets, handling_in, handling_out |
| `zones.csv` | zone_id, name, preferred_warehouse |
| `skus.csv` | sku_id, name, pallet_factor |
| `inbound_rates.csv` | supplier_id, warehouse_id, cost_per_pallet |
| `outbound_rates.csv` | warehouse_id, zone_id, cost_per_pallet |
| `supply.csv` | supplier_id, sku_id, max_pallets |
| `demand.csv` | zone_id, sku_id, pallets |

Three files are optional.

- `warehouse_skus.csv` has `warehouse_id,sku_id`. When present, it allowlists eligible SKUs at every warehouse, including transit warehouses.
- `transfer_rates.csv` has `from_warehouse_id,to_warehouse_id,cost_per_pallet`. Its optional `max_pallets` column limits total pallet flow across all SKUs on that link per period. A blank value is unlimited and zero closes the link.
- `direct_rates.csv` has `supplier_id,zone_id,cost_per_pallet`, with optional `max_pallets` shared across SKUs. It allows factory-to-customer delivery with zero warehouse handling/capacity. Blank limits are unlimited and zero closes the direct link. Supply/demand limits still apply. Omission forbids direct delivery.

Pure direct-delivery input still includes all eight required CSVs. `warehouses.csv`, `inbound_rates.csv` and `outbound_rates.csv` may contain just their headers, and `preferred_warehouse` may be blank for a zone with a positive declared direct route. Headers remain required. UTF-8 comma-delimited CSV only; ZIPs must be flat, with exact allowed filenames. See User guide for column examples and upload limits.

Declare every intermediate warehouse in `warehouses.csv`. The transfer graph must be directed and acyclic, including links with zero capacity. Self-links are invalid. Missing links forbid movement. Omitting the transfer file gives an empty transfer network and preserves existing datasets.

All numeric values must be finite. Rates, capacities and quantities are nonnegative, while `pallet_factor` is positive. MILP demand uses whole pallets.

### Handling capacity and cost

`capacity_pallets` represents pallet-equivalent handling capacity per period. Both supplier receipts and incoming transfers consume it. Ten pallets with factor two travelling through two warehouses consume twenty units at each warehouse.

Each transfer pays its freight rate, handling-out at its source and handling-in at its destination. The report has six categories, `direct_freight`, `inbound_freight`, `transfer_freight`, `outbound_freight`, `inbound_handling` and `outbound_handling`. Direct delivery pays only its declared freight, sharing supply/demand with warehouse routes. The handling categories include transfer operations.

All legs complete in one planning period. The quantities are aggregate SKU flows. Delivery schedules, inventory carry-over and tracing a particular pallet through a complete path need additional data.

## Samples and CLI

```bash
python -m nordic_flow run data/golden
python -m nordic_flow run data/demo --out out/demo
python -m nordic_flow run data/transshipment --out out/transshipment
python -m nordic_flow run data/branching --out out/branching
```

- `golden` is the hand-worked example with baseline 700 and optimum 500.
- `demo` is the existing synthetic pilot-sized dataset. Regenerate it with `python -m nordic_flow synth data/demo`.
- `transshipment` demonstrates ten pallets through HUB, REG and LOCAL. Its expected baseline is 210 and optimum is 170.
- `branching` has factory → A/B/C → D/E/F → customer, with all nine warehouse-transfer choices. For twelve pallets, D's capacity of six leads to A→D six and B→E six, total 102 against baseline 168. Closing D gives 120; increasing D's capacity to twelve gives 84. Ready-to-upload ZIPs and hand calculations are in `data/testcases/README.md`.

The baseline first tries each zone's preferred final warehouse, then fallback serving warehouses by outbound rate, then declared direct routes by cost for remaining demand. With transfer links it chooses the cheapest available supplier path while accounting for residual supply, node capacities and link capacities. A pure direct case uses the direct-delivery rule. A greedy baseline can fail where the optimiser succeeds, so savings require a verified baseline serving all demand.

The CLI output includes `baseline_transfers.csv`, `optimised_transfers.csv`, `baseline_direct.csv` and `optimised_direct.csv`, alongside inbound/outbound CSVs and the comparison JSON.

## API

All routes use `/api`. Errors contain `code`, `message` and `details`.

| Method and path | Purpose |
|---|---|
| `GET /config`, `GET /health` | Configuration and health |
| `POST /scenarios/sample` with `{name}` | Load `demo`, `golden`, `transshipment` or `branching` |
| `POST /scenarios` | Upload multipart `files` as CSVs or one flat ZIP |
| `GET /scenarios/{id}`, `GET /scenarios` | Scenario details and list |
| `POST /scenarios/{id}/runs` with `{mode,time_limit}` | Build baseline, optimise and verify |
| `GET /runs/{id}` | Full comparison, plans and checks |
| `GET /runs/{id}/paths?zone=...&sku=...&quantity=1&limit=50` | Cheapest complete paths, quoted costs, standalone limits and plan accounting |
| `POST /runs/{id}/overrides` | Final-delivery pin and child run |
| `POST /runs/{id}/routes` | Reserve `{supplier,warehouses:[...],zone,sku,pallets,reason}` on a complete path |
| `DELETE /runs/{id}/routes/{index}` | Remove a manual route in a new child run |
| `POST /runs/{id}/explanation` with `{use_llm}` | Generate explanation |
| `GET /runs/{id}/explanation`, `POST /runs/{id}/explanation/approve` | Read and approve explanation text |
| `POST /runs/{id}/decision` with `{decision,comment}` | Approve or reject and lock the run |
| `GET /runs/{id}/export` | Approved plan ZIP |
| `POST /scenarios/{id}/whatif` | Change copied data and recalculate |
| `GET /audit`, `GET /audit/verify` | Events and chain verification |
| `POST /mapping/suggest`, `POST /mapping/confirm` | Suggest and confirm SKU matches |

Plans contain `inbound`, `transfers`, `outbound` and `direct` arrays. Transfer rows have `from_warehouse,to_warehouse,sku,pallets`; direct rows use `supplier,zone,sku,pallets`. Old saved plans default missing arrays to empty and missing freight categories to zero. `network.direct_lanes` describes declared direct routes and their local availability. A manual direct path uses `warehouses:[]` and the editor's **Factory to customer** route type. Ranking includes such paths with zero handling.

ZIPs10–16 in `data/testcases/` (also downloadable in User guide) cover genuine direct70, chains of3/4/5/8/12 warehouses at130/160/190/280/400, and direct-plus-five-warehouse allocation145 against baseline190. Every case has ten pallets. Source CSVs are in `data/shipping_cases/`; matching frontend downloads live in `frontend/public/examples/` and survive builds.

Run responses also include `network` for the effective run data, including what-if changes. It contains supplier/zone names, warehouse capacities and handling rates, plus declared inbound/transfer/outbound lanes with freight rates, `available` and `unavailable_reason`. Availability checks local limits and whether a relevant product is eligible; complete-path and simultaneous feasibility still depend on the optimisation constraints.

Run responses expose `route_pins` separately from final-delivery `pins`. Older databases gain a `route_pins_json` column with an empty-list default, preserving their runs and audit history.

Approved ZIPs include the optimised inbound, transfer and outbound CSVs. A valid baseline gets matching CSVs. The ZIP also includes comparison, planner decisions, `manual_routes.json`, audit history and status.

## Validation and limits

The independent verifier checks supply, exact demand, conservation, allowed links, SKU eligibility and capacities at every visited warehouse. Transfer-link limits are summed across SKUs. Savings are null for an invalid baseline. `FEASIBLE` records the best plan found within the time limit, while `OPTIMAL` records proven optimality.

Costs and the included savings examples use synthetic inputs. A planner must review operational meaning and the wording of AI drafts. Numeric token matching is one guard and does not verify every claim in free text.

The app uses a single simulated planner and local file exchange. Groq live-call observations are recorded in `../docs/round2/GROQ-CHECK.md`. Synthetic robustness results are in `../docs/round2/ROBUSTNESS.md`.

## Development and checks

Edit the frontend in `frontend/`, then rebuild the served files.

```bash
cd frontend
npm ci
npm run build
```

From `mvp/`, the repeatable evidence commands are

```bash
python -m nordic_flow demo-guard
python -m nordic_flow robustness --out ../docs/round2/ROBUSTNESS.md
```

The guard uses simulated model responses and the production numeric check. Browser walkthroughs use Playwright. Run `node tests/e2e_ui.js` for the existing demo, `node tests/e2e_transfers.js` for the three-warehouse chain, `node tests/e2e_branching.js` for the network of alternative routes, `node tests/e2e_manual_routes.js` for higher-cost human choices/removal/reordered warehouses, `node tests/e2e_route_ranking.js` for full-path prices/highlighting, and `node tests/e2e_focused_workflow.js` for separate edit/review tasks, cancellation and version history against a disposable server. Use `BASE_URL` for another address, `BROWSER_CHANNEL=msedge` for installed Edge and `SHOTS` for screenshots.

`node tests/e2e_guide_shipping.js` additionally checks the guide before loading data, all eleven CSV contracts, seven HTTP ZIP downloads, pure direct rendering/manual choice/export, and the3/4/5/8/12-warehouse diagrams including mobile layout.

## Reset a recording database

Stop the server before clearing a disposable local database. The default is `mvp/var/app.db`. Restart the server and reload a sample.

A separate recording instance can use a temporary database by setting `NORDIC_DB` to a disposable file before starting Uvicorn. This keeps the recording data separate from other local work.
