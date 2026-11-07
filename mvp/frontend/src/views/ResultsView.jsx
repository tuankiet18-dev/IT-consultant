import { ArrowRight } from "lucide-react";
import { useApp } from "../store.jsx";
import { Kpi, Note, PageHead, RunBanner, Section } from "../components/ui.jsx";
import { CostChart, LoadChart } from "../components/charts.jsx";
import PlanDetails from "./PlanView.jsx";
import AllocationExplorer from "../components/AllocationExplorer.jsx";
import { fmt, solverText } from "../utils";

function DetailSection({ title, hint, children }) {
  return (
    <details className="card group mt-4">
      <summary className="cursor-pointer px-5 py-4 text-slate-900">
        <h3 className="ml-1 inline text-base font-semibold">{title}</h3>
      </summary>
      <div className="border-t border-slate-100 px-5 py-4">
        <p className="hint mb-4">{hint}</p>
        {children}
      </div>
    </details>
  );
}

export default function ResultsView() {
  const { run: r, ent, go } = useApp();
  const c = r.comparison;
  const failed = r.verify.optimised_violations.length > 0;
  return (
    <div>
      <PageHead title="Results" lead="Compare cost, check capacity and see where goods will move.">
        {r.state === "draft" && <button type="button" className="btn btn-secondary" onClick={() => go("route")}>Create manual route</button>}
        <button type="button" className="btn btn-primary" onClick={() => go("review")}>Review & approve <ArrowRight size={16} aria-hidden="true" /></button>
      </PageHead>
      <RunBanner run={r} />
      {!c.baseline_valid && <Note tone="warn">The baseline leaves demand unserved. Savings are unavailable for this comparison.</Note>}
      {r.status === "FEASIBLE" && <Note tone="warn">Time limit reached. Review the best feasible allocation found so far.</Note>}
      <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Kpi label={c.saving < 0 ? "Cost increase" : "Saving"} big tone={c.saving == null ? "default" : c.saving < 0 ? "bad" : "good"}
          value={c.saving == null ? "n/a" : fmt(Math.abs(c.saving))}
          sub={c.saving_pct == null ? "Baseline comparison unavailable" : fmt(Math.abs(c.saving_pct), 1) + (c.saving < 0 ? "% above baseline" : "% below baseline")} />
        <Kpi label="Optimised plan" tone="brand" value={fmt(c.optimised.total)}
          sub={(r.pins.length || (r.route_pins || []).length) && r.status === "OPTIMAL" ? "optimal with your decisions fixed" : solverText(r.status).toLowerCase()} />
        <Kpi label={(r.network?.direct_lanes?.length || 0) > 0 ? "Rule-based baseline" : "Preferred-warehouse baseline"} value={c.baseline_valid ? fmt(c.baseline.total) : "unusable"} sub={Object.keys(ent.raw.warehouses).length === 0 ? "Direct delivery when no warehouse route exists" : (r.network?.direct_lanes?.length || 0) > 0 ? "Preferred warehouse first, direct delivery as fallback" : "Each zone uses its preferred warehouse first"} />
        <Kpi label="Plan checks" tone={failed ? "bad" : "default"} value={failed ? "Failed" : "Passed"} sub="demand, supply, capacity and lanes verified independently" />
      </div>
      <p className="mt-3 text-sm text-slate-500">{c.changes.length} zone-and-product allocations changed from baseline · Costs in cost units</p>
      {(c.transfer_changes || []).length > 0 && <p className="mt-1 text-sm text-slate-500">{c.transfer_changes.length} warehouse-transfer allocation(s) changed.</p>}

      <Section title="Allocation overview" hint="Compare available routes with the shipments selected for this plan.">
        <div className="card card-pad"><AllocationExplorer key={r.id} run={r} ent={ent} /></div>
      </Section>

      <div className="mt-8">
        <DetailSection title="Where the cost sits" hint="Compare transport and handling costs.">
          <CostChart c={c} />
        </DetailSection>
        {Object.keys(ent.raw.warehouses).length > 0 && <DetailSection title="Warehouse load" hint="Receipts from suppliers and other warehouses both count towards weekly handling capacity.">
          <LoadChart c={c} ent={ent} />
        </DetailSection>}
        <DetailSection title="Plan details" hint="Filter by zone or product. Highlighted rows show changed allocations.">
        <PlanDetails />
        </DetailSection>
      </div>
    </div>
  );
}
