import { ArrowRight } from "lucide-react";
import { useApp } from "../store.jsx";
import { Kpi, Note, PageHead, RunBanner, Section } from "../components/ui.jsx";
import { CostChart, LoadChart } from "../components/charts.jsx";
import { fmt } from "../utils";

export default function ResultsView() {
  const { run: r, ent, go } = useApp();
  const c = r.comparison;
  const failed = r.verify.optimised_violations.length > 0;
  return (
    <div>
      <PageHead title="Results" lead={`Run ${r.id} · ${r.mode.toUpperCase()} · solver ${r.status} in ${r.solve_seconds}s`}>
        <button type="button" className="btn btn-primary" onClick={() => go("plan")}>See the plan <ArrowRight size={16} aria-hidden="true" /></button>
      </PageHead>
      <RunBanner run={r} />
      {!c.baseline_valid && <Note tone="err">The preferred-warehouse baseline could not serve all demand, so no saving is reported. The optimised plan below is still valid.</Note>}
      {r.status === "FEASIBLE" && <Note tone="warn">The solver stopped at its time limit. This plan is feasible, not proven optimal.</Note>}

      <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Kpi label="Saving" big tone={c.saving != null ? "good" : "default"}
          value={c.saving == null ? "n/a" : fmt(c.saving)}
          sub={c.saving_pct == null ? "no valid baseline" : fmt(c.saving_pct, 1) + "% of baseline (cost units)"} />
        <Kpi label="Optimised plan" tone="brand" value={fmt(c.optimised.total)}
          sub={r.status !== "OPTIMAL" ? "feasible within time limit" : r.pins.length ? "optimal with your decisions fixed" : "proven optimal"} />
        <Kpi label="Preferred-warehouse baseline" value={c.baseline_valid ? fmt(c.baseline.total) : "unusable"} sub="synthetic rule, not Company A's actual plan" />
        <Kpi label="Independent check" tone={failed ? "bad" : "default"} value={failed ? "Failed" : "Passed"} sub="supply, demand, capacity, lanes, balance" />
      </div>

      <Section title="Where the cost sits" hint="Cost units, by type. The table gives the exact numbers behind the bars.">
        <div className="card card-pad"><CostChart c={c} /></div>
      </Section>
      <Section title="Warehouse load" hint="Share of weekly capacity used.">
        <div className="card card-pad"><LoadChart c={c} ent={ent} /></div>
      </Section>
      <Note tone="info">{c.changes.length} zone-and-SKU decision(s) differ from the baseline.</Note>
    </div>
  );
}
