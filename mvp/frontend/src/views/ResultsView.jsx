import { ArrowRight } from "lucide-react";
import { useApp } from "../store.jsx";
import { Kpi, Note, PageHead, RunBanner, Section } from "../components/ui.jsx";
import { CostChart, LoadChart } from "../components/charts.jsx";
import PlanDetails from "./PlanView.jsx";
import { fmt, solverText } from "../utils";

export default function ResultsView() {
  const { run: r, ent, go } = useApp();
  const c = r.comparison;
  const failed = r.verify.optimised_violations.length > 0;
  return (
    <div>
      <PageHead title="Results" lead="How the optimised plan compares with the preferred-warehouse baseline.">
        <button type="button" className="btn btn-primary" onClick={() => go("review")}>Review & approve <ArrowRight size={16} aria-hidden="true" /></button>
      </PageHead>
      <RunBanner run={r} />
      {!c.baseline_valid && <Note tone="err">The preferred-warehouse baseline could not serve all demand, so no saving is reported. The optimised plan below is still valid.</Note>}
      {r.status === "FEASIBLE" && <Note tone="warn">The solver stopped at its time limit. This plan is feasible, not proven optimal.</Note>}

      {c.saving != null && (
        <div className="mt-6 rounded-xl border border-emerald-200 bg-emerald-50 px-5 py-4 text-emerald-900">
          <p className="text-lg font-semibold">The optimised plan is {fmt(c.saving_pct, 1)}% cheaper than the baseline.</p>
          <p className="mt-1 text-sm">It saves {fmt(c.saving)} cost units by choosing which warehouse serves each zone.</p>
        </div>
      )}
      <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Kpi label="Saving" big tone={c.saving != null ? "good" : "default"}
          value={c.saving == null ? "n/a" : fmt(c.saving)}
          sub={c.saving_pct == null ? "no valid baseline" : fmt(c.saving_pct, 1) + "% of baseline (cost units)"} />
        <Kpi label="Optimised plan" tone="brand" value={fmt(c.optimised.total)}
          sub={r.pins.length && r.status === "OPTIMAL" ? "optimal with your decisions fixed" : solverText(r.status).toLowerCase()} />
        <Kpi label="Preferred-warehouse baseline" value={c.baseline_valid ? fmt(c.baseline.total) : "unusable"} sub="synthetic rule, not Company A's actual plan" />
        <Kpi label="Plan checks" tone={failed ? "bad" : "default"} value={failed ? "Failed" : "Passed"} sub="demand, supply, capacity and lanes verified independently" />
      </div>

      <Section title="Where the cost sits" hint="Cost units, by type. The table gives the exact numbers behind the bars.">
        <div className="card card-pad"><CostChart c={c} /></div>
      </Section>
      <Section title="Warehouse load" hint="Share of weekly capacity used.">
        <div className="card card-pad"><LoadChart c={c} ent={ent} /></div>
      </Section>
      <Section title="Plan details" hint="Which warehouse serves each zone and SKU, in pallets per week. Highlighted rows differ from the baseline.">
        <PlanDetails />
      </Section>
      <Note tone="info">{c.changes.length} zone-and-SKU decision(s) differ from the baseline. Costs are in synthetic cost units, not a forecast for Company A.</Note>
    </div>
  );
}
