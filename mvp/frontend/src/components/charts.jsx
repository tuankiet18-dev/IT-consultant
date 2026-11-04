import { COST, fmt, pct } from "../utils";
import { Legend } from "./ui";

// Stacked horizontal bars: baseline vs optimised. Values are written out in the table below, so colour is never the only cue.
export function CostChart({ c }) {
  const max = Math.max(c.baseline.total, c.optimised.total, 1);
  const Row = ({ label, d, valid }) => (
    <div className="grid grid-cols-[84px_1fr_88px] items-center gap-3 py-2 text-sm">
      <div className="font-medium text-slate-700">{label}</div>
      {valid ? (
        <div className="flex h-8 overflow-hidden rounded-md bg-slate-100" style={{ width: `${(d.total / max) * 100}%` }}
          role="img" aria-label={`${label} total ${fmt(d.total)} cost units`}>
          {COST.map((k) => (
            <div key={k.key} title={`${k.label}: ${fmt(d[k.key])}`} style={{ width: `${d.total ? (d[k.key] / d.total) * 100 : 0}%`, background: k.color }} />
          ))}
        </div>
      ) : (
        <div className="h-8 rounded-md border border-dashed border-slate-300 bg-slate-50" />
      )}
      <div className="text-right font-semibold text-slate-900">{valid ? fmt(d.total) : "unusable"}</div>
    </div>
  );
  return (
    <div>
      <Row label="Baseline" d={c.baseline} valid={c.baseline_valid} />
      <Row label="Optimised" d={c.optimised} valid />
      <Legend items={COST.map((k) => [k.label, k.color])} />
      <div className="mt-4 overflow-x-auto">
        <table className="tbl">
          <thead>
            <tr><th>Cost type</th><th className="num">Baseline</th><th className="num">Optimised</th><th className="num">Change</th></tr>
          </thead>
          <tbody>
            {COST.map((k) => {
              const d = c.optimised[k.key] - c.baseline[k.key];
              return (
                <tr key={k.key}>
                  <td><span className="mr-2 inline-block h-2.5 w-2.5 rounded-sm" style={{ background: k.color }} aria-hidden="true" />{k.label}</td>
                  <td className="num">{c.baseline_valid ? fmt(c.baseline[k.key]) : "n/a"}</td>
                  <td className="num">{fmt(c.optimised[k.key])}</td>
                  <td className={"num font-medium " + (!c.baseline_valid ? "" : d < 0 ? "text-emerald-700" : d > 0 ? "text-amber-700" : "")}>
                    {c.baseline_valid ? (d > 0 ? "+" : "") + fmt(d) : "n/a"}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export function LoadChart({ c, ent }) {
  const Bar = ({ value, color, label }) => (
    <div className="flex items-center gap-3">
      <span className="w-20 shrink-0 text-xs text-slate-500">{label}</span>
      <div className="relative h-3 flex-1 rounded-full bg-slate-100">
        <div className="h-full rounded-full" style={{ width: `${Math.min(value, 1) * 100}%`, background: color }} />
        <span className="absolute -top-1 -bottom-1 right-0 border-r-2 border-dashed border-slate-400" aria-hidden="true" />
      </div>
      <span className="w-12 shrink-0 text-right text-sm font-medium text-slate-800">{pct(value)}</span>
    </div>
  );
  return (
    <div>
      <div className="grid gap-4 md:grid-cols-3">
        {Object.keys(c.utilisation_optimised).map((w) => (
          <div key={w} className="rounded-lg border border-slate-200 p-4">
            <div className="flex items-baseline justify-between">
              <b className="text-sm text-slate-900">{ent.wh(w)}</b>
              <span className="text-xs text-slate-500">capacity {fmt(ent.capacity(w))}</span>
            </div>
            <div className="mt-3 space-y-2">
              <Bar value={c.utilisation_baseline[w]} color="#94A3B8" label="Baseline" />
              <Bar value={c.utilisation_optimised[w]} color="#2563EB" label="Optimised" />
            </div>
          </div>
        ))}
      </div>
      <Legend items={[["Baseline", "#94A3B8"], ["Optimised", "#2563EB"], ["Dashed line = 100% of weekly capacity", "#94A3B8"]]} />
    </div>
  );
}
