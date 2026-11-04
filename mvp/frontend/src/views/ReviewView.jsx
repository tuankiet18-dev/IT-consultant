import { useEffect, useMemo, useState } from "react";
import { ArrowRight, Sparkles } from "lucide-react";
import { useApp } from "../store.jsx";
import { Field, Note, PageHead, RunBanner, Section, Tag } from "../components/ui.jsx";
import { allocMap, fmt } from "../utils";

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
          <p className="hint mt-1">No explanation yet. The default is a deterministic summary built only from the calculated numbers. The AI option (Groq) writes it in smoother prose, but its numbers are checked and it stays a draft until you approve it.</p>
          <div className="mt-4 flex flex-wrap gap-3">
            <button type="button" className="btn btn-secondary" onClick={() => explain(false)}>Generate summary</button>
            <button type="button" className="btn btn-primary" disabled={!llmOn} title={llmOn ? "" : "Set GROQ_API_KEY to enable"} onClick={() => explain(true)}>
              <Sparkles size={16} aria-hidden="true" /> Generate with AI (Groq)
            </button>
          </div>
        </>
      ) : (
        <>
          <div className="mt-3 flex flex-wrap gap-2">
            <Tag tone={e.source === "deterministic" ? "info" : "warn"}>{e.source === "deterministic" ? "Deterministic summary" : "AI draft · " + e.source}</Tag>
            <Tag tone={e.status === "approved" ? "good" : "neutral"}>{e.status === "approved" ? `Approved by ${e.approved_by}${e.edited ? " (edited)" : ""}` : "Draft: needs your review"}</Tag>
          </div>
          {e.reason && <Note tone="warn">AI not used: {e.reason}</Note>}
          <textarea className="input mt-3 min-h-[160px] text-[15px] leading-relaxed" value={text} onChange={(ev) => setText(ev.target.value)} aria-label="Explanation text" />
          <div className="mt-3 flex flex-wrap gap-3">
            <button type="button" className="btn btn-success" disabled={locked || e.status === "approved"} onClick={() => approveExpl(text)}>Approve explanation</button>
            <button type="button" className="btn btn-secondary" onClick={clearExplanation}>Regenerate</button>
          </div>
          <p className="hint mt-3">The numbers on the Results tab are the source of truth. This text only restates them.</p>
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
        onClick={() => applyOverride({ zone, sku, warehouse: wh, pallets: +pallets, reason })}>Apply and re-optimise</button>
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
  const { run: r, runs, openRun, go } = useApp();
  const locked = r.state !== "draft";
  return (
    <div>
      <PageHead title="Review & adjust" lead="Read the explanation, then change a decision if the business needs it. Every change needs a reason and is logged.">
        <button type="button" className="btn btn-primary" onClick={() => go("approve")}>Approve & audit <ArrowRight size={16} aria-hidden="true" /></button>
      </PageHead>
      <RunBanner run={r} />
      <div className="mt-6"><Explanation locked={locked} /></div>
      <Section title="Change a decision"><Override locked={locked} /></Section>
      {runs.length > 1 && (
        <Section title="Runs for this scenario">
          <div className="card overflow-x-auto">
            <table className="tbl">
              <thead><tr><th>Run</th><th>Kind</th><th>State</th><th>Status</th><th /></tr></thead>
              <tbody>
                {runs.map((x) => (
                  <tr key={x.id} className={x.id === r.id ? "row-changed" : ""}>
                    <td>{x.id}</td><td>{x.kind}</td><td>{x.state}</td><td>{x.status}</td>
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
