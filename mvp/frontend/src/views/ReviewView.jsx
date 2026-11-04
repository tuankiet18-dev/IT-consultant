import { useEffect, useMemo, useRef, useState } from "react";
import { Sparkles } from "lucide-react";
import { useApp } from "../store.jsx";
import { DecisionPanel } from "./ApproveView.jsx";
import { Field, Note, PageHead, RunBanner, Section, Tag } from "../components/ui.jsx";
import { allocMap, fmt, kindText, solverText, stateText } from "../utils";

function Evidence({ f }) {
  const rows = (f.largest_changes || []).filter((c) => c.route_cost_difference_per_pallet != null);
  const from = (arr) => arr.map((x) => `${x.warehouse} ${fmt(x.pallets)}`).join(", ");
  return (
    <details className="mt-4 rounded-lg border border-slate-200 bg-slate-50 px-4 py-3">
      <summary className="cursor-pointer text-sm font-medium text-slate-700">What this explanation is based on</summary>
      <p className="hint mt-2">The text only restates these figures, which the system calculated from your data. The AI assistant does no calculation.</p>
      <dl className="mt-3 grid gap-x-6 gap-y-1 text-sm sm:grid-cols-2">
        <div className="flex justify-between gap-3"><dt className="text-slate-500">Baseline cost</dt><dd className="font-medium">{f.baseline_total == null ? "unusable" : fmt(f.baseline_total)}</dd></div>
        <div className="flex justify-between gap-3"><dt className="text-slate-500">Optimised cost</dt><dd className="font-medium">{fmt(f.optimised_total)}</dd></div>
        {Object.entries(f.cost_change_by_type || {}).map(([k, v]) => (
          <div key={k} className="flex justify-between gap-3"><dt className="text-slate-500 capitalize">{k}</dt><dd className="font-medium">{(v > 0 ? "+" : "") + fmt(v)}</dd></div>
        ))}
        <div className="flex justify-between gap-3"><dt className="text-slate-500">Total demand (pallets)</dt><dd className="font-medium">{fmt(f.total_demand_pallets)}</dd></div>
        <div className="flex justify-between gap-3"><dt className="text-slate-500">Weekly capacity</dt><dd className="font-medium">{fmt(f.total_weekly_capacity)}</dd></div>
        <div className="flex justify-between gap-3"><dt className="text-slate-500">Full in baseline</dt><dd className="font-medium">{(f.warehouses_full_in_baseline || []).join(", ") || "none"}</dd></div>
        <div className="flex justify-between gap-3"><dt className="text-slate-500">Full in optimised plan</dt><dd className="font-medium">{(f.warehouses_at_capacity || []).join(", ") || "none"}</dd></div>
      </dl>
      {rows.length > 0 && (
        <div className="mt-4 overflow-x-auto rounded-lg border border-slate-200 bg-white">
          <table className="tbl">
            <thead><tr><th>Zone and SKU</th><th>Baseline</th><th>Optimised</th><th className="num">Route cost per pallet (before, after)</th><th className="num">Saved per pallet</th></tr></thead>
            <tbody>
              {rows.map((c, i) => (
                <tr key={i}><td>{c.zone} · {c.sku}</td><td>{from(c.baseline_from)}</td><td>{from(c.optimised_from)}</td>
                  <td className="num">{fmt(c.baseline_route_cost_per_pallet, 1)} → {fmt(c.optimised_route_cost_per_pallet, 1)}</td>
                  <td className="num font-medium text-emerald-700">{fmt(c.route_cost_difference_per_pallet, 1)}</td></tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      <p className="hint mt-2">Route cost per pallet = cheapest supplier to the warehouse + handling in + warehouse to zone + handling out.</p>
    </details>
  );
}

function Explanation({ locked }) {
  const { explanation: e, explain, approveExpl, clearExplanation, config } = useApp();
  const [text, setText] = useState("");
  const ref = useRef(null);
  useEffect(() => { setText(e ? e.text : ""); }, [e]);
  // Grow the box to fit the whole explanation, and re-fit when the width changes (so nothing hides behind a scrollbar).
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const fit = () => { if (el.clientWidth < 200) return; el.style.height = "auto"; el.style.height = el.scrollHeight + 2 + "px"; };
    fit();
    const ro = new ResizeObserver(fit);
    ro.observe(el.parentElement);
    return () => ro.disconnect();
  }, [text, e]);
  const llmOn = config && config.llm_enabled;
  return (
    <div className="card card-pad">
      <h3 className="text-base font-semibold text-slate-900">Explanation</h3>
      {!e ? (
        <>
          <p className="hint mt-1">No explanation yet. The standard summary is built only from the calculated numbers. The AI assistant can write it in smoother prose; its numbers are checked and it stays a draft until you approve it.</p>
          <div className="mt-4 flex flex-wrap gap-3">
            <button type="button" className="btn btn-secondary" onClick={() => explain(false)}>Write standard summary</button>
            <button type="button" className="btn btn-primary" disabled={!llmOn} title={llmOn ? "" : "The AI assistant is not configured"} onClick={() => explain(true)}>
              <Sparkles size={16} aria-hidden="true" /> Write with AI assistant
            </button>
          </div>
        </>
      ) : (
        <>
          <div className="mt-3 flex flex-wrap gap-2">
            <Tag tone={e.source === "deterministic" ? "info" : "warn"}>{e.source === "deterministic" ? "Standard summary" : "AI draft"}</Tag>
            <Tag tone={e.status === "approved" ? "good" : "neutral"}>{e.status === "approved" ? `Approved by ${e.approved_by}${e.edited ? " (edited)" : ""}` : "Draft: needs your review"}</Tag>
          </div>
          {e.reason && <Note tone="warn">The AI assistant could not be used this time, so the standard summary is shown instead.</Note>}
          <textarea ref={ref} className="input mt-3 resize-none overflow-hidden px-4 py-3 text-base leading-7" style={{ minHeight: 220 }} value={text} onChange={(ev) => setText(ev.target.value)} aria-label="Explanation text" />
          <div className="mt-3 flex flex-wrap gap-3">
            <button type="button" className="btn btn-success" disabled={locked || e.status === "approved"} onClick={() => approveExpl(text)}>Approve explanation</button>
            <button type="button" className="btn btn-secondary" onClick={clearExplanation}>Start over</button>
          </div>
          {e.facts && <Evidence f={e.facts} />}
          <p className="hint mt-3">The Results page holds the official numbers. This text only restates them.</p>
        </>
      )}
    </div>
  );
}

function Override({ locked }) {
  const { run: r, ent, applyOverride } = useApp();
  const cur = useMemo(() => allocMap(r.optimised.outbound), [r]);
  const pairs = useMemo(() => Object.keys(cur).sort(), [cur]);
  const zones = useMemo(() => [...new Set(pairs.map((k) => k.split("|")[0]))], [pairs]);
  const [zone, setZone] = useState(zones[0] || "");
  const skus = pairs.filter((k) => k.startsWith(zone + "|")).map((k) => k.split("|")[1]);
  const [sku, setSku] = useState("");
  const [wh, setWh] = useState(Object.keys(ent.raw.warehouses)[0] || "");
  const [pallets, setPallets] = useState(0);
  const [reason, setReason] = useState("");

  useEffect(() => { if (!skus.includes(sku)) setSku(skus[0] || ""); }, [zone, r]); // eslint-disable-line
  const now = cur[zone + "|" + sku] || {};
  useEffect(() => {
    const first = Object.entries(now)[0];
    if (first) { setWh(first[0]); setPallets(first[1]); }
  }, [zone, sku, r]); // eslint-disable-line

  return (
    <div className="card card-pad">
      <p className="hint">Fix exactly this many pallets of one SKU from one warehouse to one zone. The rest of the plan is re-optimised around it, and the extra cost is shown.</p>
      <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Field label="Zone"><select className="input" value={zone} onChange={(e) => setZone(e.target.value)}>{zones.map((z) => <option key={z} value={z}>{ent.zone(z)}</option>)}</select></Field>
        <Field label="SKU"><select className="input" value={sku} onChange={(e) => setSku(e.target.value)}>{skus.map((s) => <option key={s} value={s}>{ent.sku(s)}</option>)}</select></Field>
        <Field label="Serve from"><select className="input" value={wh} onChange={(e) => setWh(e.target.value)}>{Object.keys(ent.raw.warehouses).map((w) => <option key={w} value={w}>{ent.wh(w)}</option>)}</select></Field>
        <Field label="Exactly (pallets)"><input className="input" type="number" min={0} step={1} value={pallets} onChange={(e) => setPallets(e.target.value)} /></Field>
      </div>
      <p className="hint mt-2">Currently: {Object.entries(now).map(([w, p]) => `${ent.wh(w)} ${fmt(p)}`).join(", ") || "–"}</p>
      <Field label="Reason (required)" className="mt-4">
        <input className="input" value={reason} onChange={(e) => setReason(e.target.value)} placeholder="e.g. Customer contract names this warehouse" />
      </Field>
      <button type="button" className="btn btn-primary mt-4" disabled={locked}
        onClick={() => applyOverride({ zone, sku, warehouse: wh, pallets: +pallets, reason })}>Apply decision and recalculate</button>
      {r.pins.length > 0 && (
        <div className="mt-6">
          <h4 className="text-sm font-semibold text-slate-900">Planner decisions in this run</h4>
          <div className="mt-2 overflow-x-auto rounded-lg border border-slate-200">
            <table className="tbl">
              <thead><tr><th>Zone</th><th>SKU</th><th>Warehouse</th><th>Pallets</th><th>Reason</th></tr></thead>
              <tbody>{r.pins.map((p, i) => <tr key={i}><td>{ent.zone(p.zone)}</td><td>{ent.sku(p.sku)}</td><td>{ent.wh(p.warehouse)}</td><td>{fmt(p.pallets)}</td><td>{p.reason}</td></tr>)}</tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

export default function ReviewView() {
  const { run: r, runs, openRun } = useApp();
  const locked = r.state !== "draft";
  return (
    <div>
      <PageHead title="Review & approve" lead="Read the explanation, change a decision if the business needs it, then approve or reject the plan. Every change needs a reason and is logged." />
      <RunBanner run={r} />
      <div className="mt-6"><Explanation locked={locked} /></div>
      {!locked && <Section title="Change a decision" hint="Optional. Use this when the business needs a specific warehouse for a specific product."><Override locked={locked} /></Section>}
      <DecisionPanel />
      {runs.length > 1 && (
        <Section title="Plan versions" hint="Each decision you apply creates a new version. Open an earlier one to compare.">
          <div className="card overflow-x-auto">
            <table className="tbl">
              <thead><tr><th>Plan</th><th>Type</th><th>Status</th><th>Result</th><th /></tr></thead>
              <tbody>
                {runs.map((x) => (
                  <tr key={x.id} className={x.id === r.id ? "row-changed" : ""}>
                    <td>Plan {x.id}</td><td>{kindText(x.kind)}</td><td>{stateText(x.state)}</td><td>{solverText(x.status)}</td>
                    <td>{x.id === r.id ? <Tag tone="info">open</Tag> : <button type="button" className="btn btn-secondary" onClick={() => openRun(x.id)}>Open</button>}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Section>
      )}
    </div>
  );
}
