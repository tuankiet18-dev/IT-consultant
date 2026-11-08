# Round 1 alignment: what the MVP does, adds and does not claim

Use this page for the video script, the User Journey and the AI Journal. Round 2 asks teams to explain any change since Round 1 and why it was necessary. Source: the submitted Round 1 proposal (`docs/round1/`, slides 1 to 10) and the Round 2 brief.

## 1. What Round 1 committed to, and where the MVP shows it

| Round 1 commitment (slide) | In the MVP |
|---|---|
| Problem: which source and existing warehouse should serve each order (1) | Core of the product: supplier to existing warehouse to customer zone, lowest total cost |
| MVP: 2 suppliers, 3 warehouses, 20 SKUs, one weekly run (1, 4) | Synthetic demo has exactly this size. It is the first example on the Data page |
| Compare the current allocation with a feasible lower-cost plan, with cost by leg (4) | Results: baseline vs optimised, cost by type, route diagram, full-route cost ranking |
| Planner approves; every override is logged (4, 5) | Approve or reject, planner decisions with a required reason, audit trail |
| Nothing is replaced; ERP, WMS and TMS execute (1, 5) | Export ZIP after approval only; nothing is written back; ERP, WMS and TMS drawn as not connected |
| Solver status always shown, infeasible with a diagnosis (6) | OPTIMAL or FEASIBLE shown; what-if closing a warehouse shows likely causes |
| LP for divisible quantities, MILP for whole pallets (6) | Method choice in Data, Advanced settings |
| AI: explanations, data mapping, always with a human approving (6) | Explanation with a number guard; optional SKU matching helper; both stay drafts until a person confirms |
| Validated feasible baseline, no savings against a weak baseline (8, 10) | Saving is shown only when the baseline is feasible and independently verified; otherwise "unusable" |
| Zero hard-constraint violations (8) | Independent verifier re-checks supply, demand, capacity and lanes without the solver |
| Worked example 700 to 500 (7) | "Worked example" sample reproduces it |

## 2. What changed since Round 1, and why

| Change | Why it was necessary or useful |
|---|---|
| Synthetic data instead of Company A data | No Company A data exists for the build-a-thon. Every screen says synthetic and costs are cost units |
| What-if scenarios, audit trail, approval gate added | Make "planner approves, every decision is logged" demonstrable rather than described |
| Learning from planner overrides (Phase 2 in Round 1) not built | Out of MVP scope as stated in Round 1 |
| No ERP, WMS or TMS connection | Round 1 said CSV adapters first; the MVP uses CSV in and out |

## 3. Optional extensions beyond the Round 1 pilot

These go further than the pilot. They are off by default and appear only when the optional input files are supplied (`transfer_rates.csv`, `direct_rates.csv`). The pilot data uses neither.

| Extension | Reason to include | Boundary |
|---|---|---|
| Transfers between existing warehouses (multi-leg paths) | Real networks often rebalance stock through regional hubs; it also strengthens "see total cost across all legs" (Round 1, slide 7) | Still existing warehouses only. No new sites. Network must not contain loops |
| Direct supplier-to-customer lanes | Some goods ship factory to customer; the model can price them next to warehouse routes | Not a Round 1 focus. Listed only as an optional lane; no claim that it matches Company A practice |
| Manual route reservations | Gives the planner a way to override with a complete path and a reason, as Round 1 promised ("override logged") | Reasons are recorded and do not create a discount |

How to present it: the pilot proves the core idea on the Round 1 scale; the extensions show the same engine handles a deeper network without a redesign. Do not describe the extensions as Round 1 scope.

## 4. What the MVP does not claim

- No forecast of savings for Company A. The ~4% figure on the demo data comes from how the synthetic data was built.
- No evidence yet for the 5% cost gate, the 30% planner-time gate or the on-time-in-full gate. The MVP can show a computed cost difference and zero hard-constraint violations, and nothing else from slide 8.
- No integration with ERP, WMS or TMS, no automatic execution, no vehicle routing, no forecasting, no new warehouses.
- The audit trail is tamper-evident, not tamper-proof.
- AI never calculates. It rewrites facts our code computed, and the planner approves the text.
