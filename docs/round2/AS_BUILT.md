# As built

Updated 7 November 2026. The canonical input and API contract is `01_CONTRACTS_AND_ARCHITECTURE.md`. `00_TEAM_DECISIONS_DRAFT.md` records earlier planning decisions.

## Application structure

- React and Vite source is in `mvp/frontend/`. The production build in `mvp/web/` is served by FastAPI.
- `mvp/api/` contains HTTP routes, use cases, SQLite storage and audit logging.
- `mvp/nordic_flow/` contains the data model, validation, baseline, solver, independent verifier, reporting, explanation and What-if logic.
- SQLite stores scenarios, runs, explanations and hash-chained audit events.
- Groq is optional for explanation wording and SKU-matching assistance.

The UI has six navigation destinations: three main planning steps, Data, Results and Review & approve, plus Audit trail, What-if and User guide. The guide is available before loading data and includes detailed input fields, workflow instructions, common questions and downloadable testcase ZIPs. Separate buttons let the planner choose the standard summary or an AI draft.

Data collapses the source picker after loading. Results keeps KPIs, diagram and route ranking open, with detailed cost/load/allocation sections collapsed. **Create manual route** opens a transient editor under Results, distinct from **Review & approve**. A separate delivery-warehouse editor preserves exact final-delivery pins. Back navigation does not save draft form input; a successful edit returns to a child Results version. Review contains explanation, read-only decision summaries, approval/export and collapsed version history. Export appears only after approval. Opening an older version reloads its own saved explanation.

## Multi-warehouse allocation

A plan can contain supplier receipts, warehouse-to-warehouse transfers, final warehouse-to-zone deliveries and supplier-to-customer direct deliveries. All visited warehouses are declared in `warehouses.csv`. The eight required CSVs are retained, with three optional CSVs: `warehouse_skus.csv`, `transfer_rates.csv` and `direct_rates.csv`. Transfer/direct rate files include per-pallet freight and optional `max_pallets` limits shared across SKUs. The declared warehouse transfer network is acyclic, including zero-capacity links.

Both supplier receipts and incoming transfers consume the receiving warehouse's handling capacity. The same goods therefore use capacity at each warehouse they visit. Transfer freight, source handling-out and destination handling-in are included in cost exactly once.

Direct delivery pays its declared freight rate and uses no warehouse handling or capacity. Supplier supply is shared by warehouse receipts and direct deliveries; exact demand is met by warehouse deliveries plus direct deliveries. A direct-only scenario can have zero warehouse rows, with header-only `warehouses.csv`, `inbound_rates.csv` and `outbound_rates.csv`. The zone's `preferred_warehouse` may be blank when a positive direct lane is declared; a nonblank value must refer to a warehouse that exists.

The baseline prefers the configured final serving warehouse. When transfers are available it uses the cheapest residual feasible supplier path to that warehouse, then tries fallback serving warehouses. It uses direct delivery only for demand left unserved by warehouse choices, ordered by direct freight. The optimiser chooses all four flow families together. Old datasets without transfer/direct files keep the original route structure and costs.

The verifier independently checks transfer/direct links, SKU eligibility, balances, visited-warehouse capacities and shared transfer/direct lane limits alongside supply and demand. A closed warehouse has zero receipt capacity, which prevents transit through it but leaves factory-to-customer direct lanes available. What-if accepts `set_rate` with `kind: "direct"` alongside the existing rate kinds.

## Compatibility and output

Plan JSON has a `transfers` array using `from_warehouse,to_warehouse,sku,pallets` and a `direct` array using `supplier,zone,sku,pallets`. Missing transfer/direct arrays in old saved plans are read as empty. Historical cost breakdowns use zero for missing `transfer_freight` or `direct_freight`. Run network metadata includes `direct_lanes` from the effective scenario. Direct allocation changes are reported separately as `direct_changes`.

The existing exact-pallet override continues to select the final delivering warehouse. It creates a child run and permits the optimiser to choose the upstream path. Approved and rejected runs are locked, and export is enabled for approved plans.

Manual complete-path reservations now let a planner choose a supplier, ordered warehouse stops, customer, SKU, quantity and reason. The optimiser respects summed path reservations and finds the remaining allocation. Child versions show the original/current costs and difference, preserve the parent, support removal and retain the same approval locks. Routes and reasons are included in `manual_routes.json` on export. An additive SQLite column retains old data and audit history. A reason does not generate a discount.

Manual direct reservations use `warehouses: []` and require a declared direct lane. The API allows zero to 100 warehouse stops, with zero representing direct delivery. Direct and warehouse routes share the same supply, demand, approval and audit rules.

The `reordered` input ZIP09 demonstrates factory→E→A→customer at total156. Warehouse stage is computed from declared routes rather than IDs. Missing links and cyclic transfer networks remain invalid.

Results includes a complete-route cost ranking filtered by customer/product and comparison quantity. Full-path unit costs include all freight and handling; direct paths have zero warehouse handling. Rows show standalone limits, quantity quotes and a deterministic accounting of plan flows, reserving known manual paths first. Selecting a row highlights exactly that full path in amber, including unused alternatives; it does not change the plan. K-best DAG ranking bounds output for large networks and reports truncation.

The approved ZIP and CLI output include inbound, transfer, outbound and `*_direct.csv` files. Direct CSV columns are `supplier,zone,sku,pallets`. Empty flow families have header-only files. Comparison, planner decisions and audit history remain part of the approved export.

## Reporting and AI validation

Savings require a full-demand, independently verified baseline. The report has six cost categories: supplier freight, transfer freight, direct freight, final warehouse-delivery freight, warehouse receipt handling and warehouse dispatch handling. Facts retain report precision and distinguish reassigned pallets from total row demand, including changes between warehouse and direct sources.

Explanation approval and plan approval are separate actions. The numeric guard can reject unsupported numeric tokens. The planner still reviews units, roles, names and causal wording. Three earlier live Groq drafts had grounded numbers and causal wording flagged for review, recorded in `GROQ-CHECK.md`.

The earlier synthetic robustness results are recorded in `ROBUSTNESS.md`. They describe that run and dataset family. They are separate from the new transfer-feature acceptance cases.

## Examples and checks

- `golden` retains the hand-worked 700 to 500 comparison.
- `demo` remains the existing synthetic pilot-sized dataset.
- `transshipment` demonstrates ten pallets travelling through HUB, REG and LOCAL, with expected baseline 210 and optimum 170.
- `branching` demonstrates factory → A/B/C → D/E/F → customer with all nine transfer choices. D's six-pallet capacity splits demand twelve into A→D six and B→E six, costing 102 against baseline 168. Its Data preview explains D's limited capacity. Results shows all declared routes and highlights positive flows, with controls to hide unused options, trace a warehouse and inspect per-leg costs. Run-specific network metadata keeps closures and changed rates accurate. Manual ZIPs 07 and 08 cover the restricted and expanded D capacity cases.

The User guide links seven additional upload-ready cases with ten pallets each. Source CSVs are stored under `mvp/data/shipping_cases/`, and ZIPs are under `mvp/data/testcases/` and served from `/examples/`.

| Case | Behaviour | Baseline | Optimum |
|---|---|---:|---:|
| 10 | Direct factory → customer, zero warehouses | 70 | 70 |
| 11 | Three warehouse visits | 130 | 130 |
| 12 | Four warehouse visits | 160 | 160 |
| 13 | Five warehouse visits | 190 | 190 |
| 14 | Eight warehouse visits | 280 | 280 |
| 15 | Twelve warehouse visits | 400 | 400 |
| 16 | Direct capacity three plus five-warehouse chain | 190 | 145 |

Chain cost per pallet is `3N + 4` for N visited warehouses. Case 16 uses three direct pallets at 4 each and seven chain pallets at 19 each. No fixed three/five-warehouse depth is imposed by the solver; the supplied warehouse graph must remain acyclic.

Feature tests cover direct and transfer routes, intermediate capacity, lane limits, closures, SKU restrictions, invalid cycles, exports and historical plan JSON. Current pass counts and timing come from the actual validation run.

Validation on 7 November 2026 used Python 3.11.4 on Windows. The full Python suite passed 274 tests, including direct shipping, shared supply/demand and lane limits, direct-only input, malformed CSV rows, the eleven CSV header contracts shown in the guide, long chains and mixed direct/warehouse routes. Seven Playwright walkthroughs passed on Edge: existing demo, three-warehouse chain, branching network, manual paths, route ranking, focused workflow and guide/shipping cases. The guide/shipping walkthrough downloaded all seven ZIPs over HTTP, checked direct manual decisions and exports, verified a twelve-warehouse diagram with fourteen nodes and eleven transfer legs, and confirmed the mixed three-direct/seven-chain allocation and mobile layout. Other checks retained approval/export/audit/What-if, cancellation without mutation, version explanation reload and exact route highlighting. The production frontend build completed successfully.

## Scope assumptions

The plan covers one period with every leg completed in that period. Warehouse capacity represents handling throughput. Inventory carry-over, initial warehouse stock, transport lead times and delivery scheduling require further modelling.

Flows are aggregated by SKU. They support planning and visualisation of transfer quantities. An exact end-to-end identity for an individual pallet or order needs additional traceability data.

The planner uses local file import and export. The submission documents and video should reflect the flow types that the team demonstrates.
