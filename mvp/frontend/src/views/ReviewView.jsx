import { useEffect, useMemo, useState } from "react";
import { Sparkles } from "lucide-react";
import { useApp } from "../store.jsx";
import { DecisionPanel } from "./ApproveView.jsx";
import { Field, Note, PageHead, RunBanner, Section, Tag } from "../components/ui.jsx";
import { allocMap, fmt, kindText, solverText, stateText } from "../utils";

function Explanation({ locked }) {
  const { explanation: e, explain, approveExpl, clearExplanation, config } = useApp();
  const [text, setText] = useState("");
  useEffect(() => { setText(e ? e.text : ""); }, [e]);
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
          <textarea className="input mt-3 min-h-[160px] text-[15px] leading-relaxed" value={text} onChange={(ev) => setText(ev.target.value)} aria-label="Explanation text" />
          <div className="mt-3 flex flex-wrap gap-3">
            <button type="button" className="btn btn-success" disabled={locked || e.status === "approved"} onClick={() => approveExpl(text)}>Approve explanation</button>
            <button type="button" className="btn btn-secondary" onClick={clearExplanation}>Start over</button>
          </div>
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
