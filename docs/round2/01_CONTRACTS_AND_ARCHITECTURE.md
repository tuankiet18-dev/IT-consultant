# Nordic Flow technical contracts and architecture

Version 0.2, updated 7 November 2026. This is the canonical contract for the current local MVP, including direct factory-to-customer delivery and transfers through multiple warehouses. Earlier decision drafts describe the planning history. The implementation entry point is `mvp/api/main.py`.

## System and component boundaries

```text
Planner
  |
  | local browser actions and file exchange
  v
React UI built by Vite and served from mvp/web/
  |
  | HTTP and JSON under /api
  v
FastAPI routes in api/main.py
  |
  v
Use cases in api/service.py
  |                         |
  | Python calls            | SQL
  v                         v
nordic_flow core          SQLite
  |
  | optional HTTPS request containing computed facts or SKU candidates
  v
Groq API
```

The application proposes allocations for one planning period. A planner reviews, adjusts, approves and exports a plan. Input and output files are the boundary for operational data exchange.

The core owns data validation, baseline construction, optimisation, independent verification and cost calculations. The API owns persistence, approval state, exports and audit events. The browser presents those results. Groq can draft explanations and assist SKU matching when requested.

The browser keeps three primary steps: Data, Results and Review & approve. Manual-route and final-delivery editing are transient Results subviews, rather than forms embedded in approval. Review displays explanation, read-only decision summaries and approval/export; source selection, detailed Results tables and version history expand on demand. These presentation changes do not change input or API contracts.

**User guide** is available in the application navigation before loading data. It contains a detailed field-by-field input guide, the planning/review workflow, cost and capacity explanations, common questions and downloadable complete ZIP examples. Its sample download links use the static `/examples/{filename}.zip` path, outside the `/api` prefix.

## Input contract

A scenario consists of eight required CSV files and up to three optional CSV files. Upload them together or in one flat ZIP. CSV files use UTF-8 and comma-separated columns, with the exact header names below; a data row must contain the same number of cells as its header. IDs are case-sensitive strings and must match referenced records. Numeric values must be finite. Costs and capacities are nonnegative.

| File | Required columns | Meaning and constraints |
|---|---|---|
| `suppliers.csv` | `supplier_id,name` | One unique row per supplier |
| `warehouses.csv` | `warehouse_id,name,capacity_pallets,handling_in,handling_out` | One row per warehouse, including intermediate and final-delivery warehouses |
| `zones.csv` | `zone_id,name,preferred_warehouse` | Preferred warehouse is the baseline's final serving warehouse; may be blank when the zone has a positive declared direct-delivery lane |
| `skus.csv` | `sku_id,name,pallet_factor` | Positive capacity factor for each SKU |
| `inbound_rates.csv` | `supplier_id,warehouse_id,cost_per_pallet` | Allowed directed supplier-to-warehouse links |
| `outbound_rates.csv` | `warehouse_id,zone_id,cost_per_pallet` | Allowed directed warehouse-to-zone links |
| `supply.csv` | `supplier_id,sku_id,max_pallets` | Supplier availability per SKU and period |
| `demand.csv` | `zone_id,sku_id,pallets` | Exact customer-zone demand per SKU and period |
| `warehouse_skus.csv` optional | `warehouse_id,sku_id` | If present, an allowlist of SKUs at each warehouse, including transit warehouses |
| `transfer_rates.csv` optional | `from_warehouse_id,to_warehouse_id,cost_per_pallet` | Allowed directed warehouse-to-warehouse links |
| `direct_rates.csv` optional | `supplier_id,zone_id,cost_per_pallet` | Allowed directed factory/supplier-to-customer links with no warehouse visit |

Every warehouse belongs in `warehouses.csv`. Its role follows from its incoming and outgoing links. A warehouse can receive from suppliers, receive transfers, send transfers and deliver to zones when the corresponding links exist.

A scenario using no warehouses must still include all eight required files. In that case `warehouses.csv`, `inbound_rates.csv` and `outbound_rates.csv` contain their header rows and no data rows. Keep the `preferred_warehouse` column in `zones.csv`, with a blank value for a directly served zone. A nonblank preferred warehouse ID must refer to an existing warehouse.

### Direct-delivery fields

`direct_rates.csv` accepts the optional column `max_pallets`. Missing/blank means there is no separate lane limit, zero closes the lane, and a positive value limits the total pallets of all SKUs delivered directly on that supplier-to-zone lane in the period. Supplier supply and customer demand still apply.

```csv
supplier_id,zone_id,cost_per_pallet,max_pallets
SUP1,Z1,7,10
```

The direct leg pays only its declared freight rate. It incurs no warehouse receipt/dispatch fee and consumes no warehouse capacity. Omitting `direct_rates.csv` forbids direct supplier-to-customer movement; a supplier-to-warehouse shortcut is not the same as a zero-warehouse direct delivery.

### Transfer fields and examples

`transfer_rates.csv` accepts an additional optional column, `max_pallets`. A blank value gives an unlimited link. Zero closes that link. A positive value limits the sum of all SKUs transferred on that link in the planning period, measured in pallets.

The following is an illustrative input format. Each direction needs its own row.

```csv
from_warehouse_id,to_warehouse_id,cost_per_pallet,max_pallets
HUB,REG,3,20
REG,LOCAL,2,20
```

These IDs must also exist in `warehouses.csv`. A missing link forbids movement along that link. Omitting the entire optional file gives an empty transfer network, preserving the existing single-warehouse-per-route datasets.

The declared transfer graph must be acyclic. Self-links and cycles are input errors, including cycles containing a zero-capacity link. A valid chain may contain any number of intermediate warehouses supported by the supplied graph.

### Units and timing

- Quantities, transfer-link limits and direct-delivery link limits use pallets.
- `capacity_pallets` is warehouse handling capacity in pallet-equivalents per planning period. Each receipt uses `pallets * pallet_factor`.
- Both supplier receipts and transfer receipts consume handling capacity at the receiving warehouse.
- `handling_in`, `handling_out` and all freight rates use cost units per pallet.
- Every leg completes within the same planning period. Inventory carried between periods and transport lead times require a separate model.
- MILP uses whole pallet quantities. LP permits fractional quantities.

For example, ten pallets with `pallet_factor=2` travelling through HUB and REG consume twenty capacity units at HUB and twenty at REG. Handling is counted at each warehouse visit.

## Optimisation contract

For each SKU, the plan contains four flow families.

```text
x[supplier,warehouse,sku]       supplier receipt
t[from_warehouse,to_warehouse,sku]   warehouse transfer
y[warehouse,zone,sku]          final customer delivery
d[supplier,zone,sku]           direct delivery without a warehouse
```

At every warehouse and SKU, conservation requires

```text
supplier receipts + incoming transfers
    = customer deliveries + outgoing transfers
```

Supplier supply is shared by supplier-to-warehouse receipts and direct deliveries. Customer demand is met by warehouse-to-zone deliveries plus direct deliveries. Warehouse conservation remains unchanged for goods that visit warehouses. Constraints include every visited warehouse's handling capacity, optional transfer/direct link capacities, allowed links and warehouse SKU eligibility. Direct deliveries do not require a warehouse SKU allowlist entry. A final-delivery pin fixes a variable `y`. Manual complete paths reserve summed lower bounds on their flow variables, including `d` for a direct path; residual demand remains optimised. Reserved complete paths are balanced, so subtracting their quantities leaves a valid residual flow.

The objective contains

```text
supplier freight + handling_in on supplier receipts
+ transfer freight + source handling_out + destination handling_in on transfers
+ final-delivery freight + handling_out on customer deliveries
+ direct supplier-to-customer freight, with no warehouse handling
```

A transfer therefore pays receiving handling at its destination and shipping handling at its source. Each operation is charged once.

The report exposes six cost categories.

| Key | Cost included |
|---|---|
| `inbound_freight` | Supplier-to-warehouse freight |
| `transfer_freight` | Warehouse-to-warehouse freight |
| `outbound_freight` | Warehouse-to-zone freight |
| `direct_freight` | Supplier-to-zone freight without a warehouse |
| `inbound_handling` | All receipts, including transfer arrivals |
| `outbound_handling` | All departures, including transfer departures |

The model represents aggregate flows per SKU. It records each leg and quantity. Assigning a specific pallet or customer order to one complete supplier-to-zone path requires an additional traceability representation.

## Baseline and comparison

The baseline first tries the zone's preferred final serving warehouse, then alternative serving warehouses ordered by outbound freight. With transfer links available, it chooses the cheapest currently available supplier-to-serving-warehouse path, respecting residual supply, warehouse capacities, transfer capacities and SKU eligibility. If warehouse choices leave demand unserved, it tries direct-delivery suppliers by direct freight rate, respecting residual supply and the direct lane limit shared across SKUs. It allocates greedily across the existing zone and SKU order. This warehouse-first reference is a synthetic rule, not a supplied company's historical plan or a cheapest-path algorithm.

Datasets without transfer or direct-delivery links retain the original baseline behaviour. A direct-only dataset can have a valid baseline. The baseline can fail even where the optimiser finds a feasible allocation. Savings are reported only for a baseline that serves all demand and passes independent verification.

Costs are recalculated from the returned flow quantities. The independent checker validates conservation, shared supply/demand, visited-warehouse capacity, transfer/direct lane limits and permitted links without invoking the solver. It checks the plan before it can be used as a successful result. `comparison.changes` retains warehouse-delivery changes; `direct_changes` separately reports rows with `supplier,zone,sku,baseline,optimised`.

## Plan and API contract

All routes use the `/api` prefix. Errors are JSON objects with `code`, `message` and `details`.

| Method and path | Request or behaviour |
|---|---|
| `GET /config`, `GET /health` | Feature configuration and health |
| `POST /scenarios/sample` | `{"name":"golden"}`, `{"name":"demo"}`, `{"name":"transshipment"}` or `{"name":"branching"}` |
| `POST /scenarios` | Multipart `files`, one flat ZIP or the CSVs together, with optional `name` |
| `GET /scenarios`, `GET /scenarios/{id}` | Stored scenario list and validation details |
| `POST /scenarios/{id}/runs` | `{"mode":"milp","time_limit":30}` |
| `GET /scenarios/{id}/runs`, `GET /runs/{id}` | Versions and complete run details |
| `GET /runs/{id}/paths` | Query `zone,sku,quantity` (default1), `limit` (default50, maximum100); ranked complete paths |
| `POST /runs/{id}/overrides` | Exact final-delivery decision with `zone,sku,warehouse,pallets,reason` |
| `POST /runs/{id}/routes` | Add or replace a complete path reservation using `supplier,warehouses,zone,sku,pallets,reason` |
| `DELETE /runs/{id}/routes/{index}` | Remove a path reservation by its index in the parent run, producing a child |
| `POST /runs/{id}/decision` | `{"decision":"approve","comment":"Reviewed"}` or `reject` with a comment |
| `GET /runs/{id}/export` | Approved plan ZIP, returns 409 until approval |
| `POST /runs/{id}/explanation` | `{"use_llm":false}` or explicit AI request |
| `GET /runs/{id}/explanation`, `POST /runs/{id}/explanation/approve` | Explanation draft and planner approval |
| `POST /scenarios/{id}/whatif` | Scenario changes followed by recalculation |
| `GET /audit`, `GET /audit/verify` | Events filtered by scenario or run, and chain verification |
| `POST /mapping/suggest`, `POST /mapping/confirm` | Suggest SKU matches and record confirmation |

Each baseline and optimised plan includes `inbound`, `transfers`, `outbound` and `direct` arrays. A transfer row uses the following shape.

```json
{
  "from_warehouse": "HUB",
  "to_warehouse": "REG",
  "sku": "SKU-01",
  "pallets": 10
}
```

Existing inbound rows use `supplier,warehouse,sku,pallets`. Existing outbound rows use `warehouse,zone,sku,pallets`. A direct-delivery row uses `supplier,zone,sku,pallets`, for example `{"supplier":"SUP1","zone":"Z1","sku":"SKU-01","pallets":10}`. Historical JSON without `transfers` or `direct` is read as an empty array. Historical reports without `transfer_freight` or `direct_freight` display zero for the missing cost category. SQLite continues to store scenario files and plans as JSON.

Each run response additionally includes a `network` object derived from that run's effective scenario, including its stored What-if changes. It contains `suppliers` and `zones` name maps, `warehouses` with `name,capacity,handling_in,handling_out`, and `inbound_lanes`, `transfer_lanes`, `outbound_lanes`, `direct_lanes`. Lane endpoints use the existing plan field names, with `cost_per_pallet,available,unavailable_reason`; transfer and direct lanes also include nullable `max_pallets`. Direct endpoints use `supplier,zone`. This is computed metadata and needs no database migration.

`available` checks positive local warehouse/route limits and the existence of a relevant supplied-and-demanded SKU eligible at the endpoints. It does not guarantee a complete path, spare residual capacity or simultaneous feasibility of all declared routes. Results draws declared but unused links in grey dashes, locally unavailable links in red dashes, and positive plan flows in colour. Line width measures pallets, not cost. Per-leg details show freight and applicable receipt/dispatch handling, separately from complete-path costs.

### Complete path comparison

`GET /runs/{id}/paths?zone=Z1&sku=SKU-01&quantity=6&limit=50` uses the effective run data. The positive finite comparison quantity must be whole in MILP. It returns `paths` sorted by complete freight plus handling per pallet, with `id,rank,supplier,warehouses,zone,sku,cost_per_pallet,freight_per_pallet,handling_per_pallet,quoted_total,max_pallets,can_carry_quantity,bottlenecks,plan_pallets,plan_cost`. `max_pallets` is the standalone minimum of supplier supply, customer demand, every visited warehouse's capacity divided by SKU pallet factor, and explicit transfer limits (floored in MILP). It is not spare capacity after other allocations.

A direct path uses `warehouses: []`, has zero `handling_per_pallet`, and its freight equals the declared direct rate. Its standalone maximum uses supply, demand and the optional direct lane limit. Direct and warehouse paths are ranked together by complete per-pallet cost.

`quoted_total` is arithmetic; the UI suppresses it as **Exceeds limit** when `can_carry_quantity=false`. A reverse-topological K-best suffix algorithm obtains the global cheapest requested paths without enumerating exponential combinations. `total_paths` gives the complete eligible path count, or null beyond the JavaScript safe-integer limit; `truncated` identifies partial lists. The UI supports20/50/100 paths and identifies truncation.

`plan_accounting` reports `method,note,delivered_pallets,total_cost` for the chosen customer/product. Manual complete paths are subtracted before deterministic residual-flow decomposition. When goods merge, other valid decompositions may exist; this is an accounting explanation, not physical tracing. Selecting a row only highlights its exact full path in amber and clears warehouse tracing. Preview node quantities show that row's accounting quantity rather than unrelated all-product totals. Viewing a row never changes the run or its optimisation constraints.

### Planner decisions and states

The final-delivery override's `warehouse` field selects the warehouse delivering to the zone. The optimiser chooses upstream suppliers and warehouses around it.

A manual route request contains, for example, `{"supplier":"SUP1","warehouses":["B","D"],"zone":"Z1","sku":"SKU-01","pallets":6,"reason":"Maintain partner allocation"}`. Warehouses are ordered stops, not fixed alphabetical stages. Every inbound/transfer/outbound connection must already be declared; no missing rate or link is invented. The route requires a positive finite quantity, whole pallets in MILP, a reason of at least three characters, distinct warehouse visits and SKU eligibility at every stop. Total reserved quantities per zone/SKU cannot exceed demand. Shared supply, warehouse/link capacities and exact final-delivery pins still apply.

The direct-delivery variant sends `warehouses: []`, for example `{"supplier":"SUP1","warehouses":[],"zone":"Z1","sku":"SKU-01","pallets":3,"reason":"Agreed direct delivery"}`. The supplier-to-zone lane must exist in `direct_rates.csv`. The API accepts zero to 100 warehouse stops, with zero reserved for direct delivery; it does not invent a direct lane from the empty list.

Run JSON exposes these reservations as `route_pins`, separate from final-delivery `pins`. The same supplier/path/zone/SKU identity is replaced on a later POST; other reservations remain. Adding, replacing or deleting creates a draft child and preserves the original, inherited What-if changes and other decisions. `cost_of_planner_decisions` compares the whole child plan with its original unpinned reference, not only the reserved goods. Reasons are recorded as human explanations and do not change rates. Agreed prices belong in the actual input rate fields.

SQLite adds `runs.route_pins_json TEXT NOT NULL DEFAULT '[]'` when opening an older database. Existing rows and audit history are retained. The independent verification checks both ordinary constraints and the summed quantities reserved on every manual path leg.

The layout derives warehouse stages from declared directed links. Factory→E→A→customer is valid when those three legs exist. The acyclic restriction still applies; a dataset containing both A→E and E→A is rejected.

```text
Validated scenario -> New run in draft state
Draft run -> approved or rejected
Draft run -> planner override -> new child run in draft state
Approved run -> export
```

A decision locks that run. Explanation approval and plan approval are separate actions. Export requires plan approval.

### Export contract

The ZIP contains `optimised_inbound.csv`, `optimised_transfers.csv`, `optimised_outbound.csv` and `optimised_direct.csv`. The corresponding `baseline_*.csv` files are included when the baseline is valid. Transfer CSV columns are `from_warehouse,to_warehouse,sku,pallets`; direct CSV columns are `supplier,zone,sku,pallets`. Empty flow families still receive header-only export files.

It also contains `comparison.json`, `planner_decisions.json`, `manual_routes.json`, `audit_log.json` and `STATUS.txt`. The CLI export uses the same allocation column names and transfer-file naming; manual route reservations are an API planner feature.

## What-if and explanation behaviour

A closed warehouse has zero handling capacity, preventing supplier receipts and incoming transfers at that warehouse. It does not close supplier-to-customer direct delivery. What-if can change capacities, scale zone demand and change rates using `kind` values `inbound`, `outbound`, `transfer` or `direct` in the API. Changes are applied to a copy of the original scenario.

Explanation facts include verified cost categories, changed final allocations, actual transfer legs and direct supplier-to-customer movements. Monetary values retain report precision. Changed-allocation quantities include changes between warehouse and direct sources. Capacity descriptions use actual loads and a numerical tolerance. Direct delivery is never described as a warehouse visit or charged warehouse handling.

Groq is optional and receives computed facts. The standard summary remains available through its own button. A numeric guard can reject unsupported numeric tokens and fall back to that summary. A planner reviews names, units, directions and causal statements before approving AI text.

## Acceptance cases

The hand-worked `golden` dataset remains 700 baseline and 500 optimum. The `transshipment` sample demonstrates a ten-pallet route through HUB, REG and LOCAL, with expected baseline 210 and optimum 170 cost units. The `branching` sample has three receiving warehouses A/B/C and three delivery warehouses D/E/F, with all nine transfer combinations. For demand twelve and D capacity six, the optimum sends six via A→D and six via B→E, costing 102 against baseline 168. With D capacity twelve the optimum is 84; with D closed it is 120. These are synthetic examples and use the same input contract, without an extra warehouse-stage field.

The feature checks cover required intermediate warehouses, a cheaper direct route, transit bottlenecks, transfer-link limits, warehouse closures, SKU restrictions, invalid cycles, old datasets, old saved JSON and exported transfer rows. Benchmark runtime and final test counts belong in the actual test results.

Manual examples on `branching`: reserve six pallets through B→D and the complete plan costs 132 (+30 from 102); reserve six through A→E and it costs 114 (+12). Removing the only route reservation restores 102. The uploadable `reordered` dataset sends twelve via E→A and costs 156 in both baseline and optimum.

The User guide provides downloadable cases 10–16, all with demand ten pallets and pallet factor one.

| ZIP case | Warehouse visits | Baseline | Optimum |
|---|---:|---:|---:|
| `10_direct_factory_customer.zip` | 0, supplier straight to customer | 70 | 70 |
| `11_chain_3_warehouses.zip` | 3 | 130 | 130 |
| `12_chain_4_warehouses.zip` | 4 | 160 | 160 |
| `13_chain_5_warehouses.zip` | 5 | 190 | 190 |
| `14_chain_8_warehouses.zip` | 8 | 280 | 280 |
| `15_chain_12_warehouses.zip` | 12 | 400 | 400 |
| `16_mixed_direct_chain_5.zip` | Direct plus a five-warehouse chain | 190 | 145 |

For a chain of N warehouses, freight is 2 on entry, 1 on each of N−1 transfers and 3 on final delivery; every warehouse charges 1 receipt plus 1 dispatch. The resulting unit cost is `3N + 4`. The mixed case has direct freight 4 with a shared lane limit of three pallets, so the optimum is `3 × 4 + 7 × 19 = 145`. The baseline sends all ten through the chain because it is warehouse-first.
