import { useState } from "react";
import { Plus, X } from "lucide-react";
import { useApp } from "../store.jsx";
import { Field, Kpi, Note, PageHead, Section } from "../components/ui.jsx";
import { fmt, solverText } from "../utils";

export default function WhatIfView() {
  const { ent, whatif: w, setWhatifChanges, runWhatIf, openRun, busy } = useApp();
  const [type, setType] = useState("close_warehouse");
  const [param, setParam] = useState("");
  const [value, setValue] = useState(100);

  const whs = Object.keys(ent.raw.warehouses), zones = Object.keys(ent.raw.zones);
  const p = param || (type === "scale_demand" ? zones[0] : whs[0]);
  const onType = (t) => { setType(t); setParam(""); setValue(t === "scale_demand" ? 1.2 : 100); };
  const describe = (c) => c.type === "close_warehouse" ? `Close ${ent.wh(c.warehouse)}`
    : c.type === "set_capacity" ? `${ent.wh(c.warehouse)} capacity = ${c.capacity}` : `${ent.zone(c.zone)} demand × ${c.factor}`;
  const add = () => {
    const ch = type === "close_warehouse" ? { type, warehouse: p } : type === "set_capacity" ? { type, warehouse: p, capacity: +value } : { type, zone: p, factor: +value };
    setWhatifChanges((cs) => [...cs, ch]);
  };
  const res = w.result;
  const validValue = type === "close_warehouse" || (value !== "" && Number.isFinite(+value) && +value >= 0);
  return (
    <div>
      <PageHead title="What-if" lead="Test warehouse or demand changes and compare the cost with the original plan." />
      <div className="card card-pad">
        <h3 className="mb-4 text-base font-semibold text-slate-900">Build a scenario</h3>
        <div className="grid items-end gap-4 md:grid-cols-[220px_1fr_auto]">
          <Field label="Change">
            <select className="input" value={type} onChange={(e) => onType(e.target.value)}>
              <option value="close_warehouse">Close a warehouse</option>
              <option value="set_capacity">Change warehouse capacity</option>
              <option value="scale_demand">Scale demand of a zone</option>
            </select>
          </Field>
          <div className="grid gap-4 sm:grid-cols-2">
            <Field label={type === "scale_demand" ? "Zone" : "Warehouse"}>
              <select className="input" value={p} onChange={(e) => setParam(e.target.value)}>
                {(type === "scale_demand" ? zones : whs).map((x) => <option key={x} value={x}>{type === "scale_demand" ? ent.zone(x) : ent.wh(x)}</option>)}
              </select>
            </Field>
            {type !== "close_warehouse" && (
              <Field label={type === "set_capacity" ? "New capacity (pallet-equivalents)" : "Multiply demand by"}>
                <input className="input" type="number" min={0} step={type === "scale_demand" ? 0.05 : 1} value={value} onChange={(e) => setValue(e.target.value)} />
              </Field>
            )}
          </div>
          <button type="button" className="btn btn-secondary" disabled={busy || !validValue} onClick={add}><Plus size={16} aria-hidden="true" /> Add change</button>
        </div>
        {w.changes.length > 0 && (
          <div className="mt-5 border-t border-slate-100 pt-4">
            <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-500">Changes to test</p>
            <ul className="flex flex-wrap gap-2">
              {w.changes.map((c, i) => (
                <li key={i} className="inline-flex items-center gap-1 rounded-full border border-brand-200 bg-brand-50 py-1 pl-3 pr-1 text-sm text-brand-800">
                  {describe(c)}
                  <button type="button" aria-label={`Remove: ${describe(c)}`} disabled={busy} className="grid h-6 w-6 cursor-pointer place-items-center rounded-full hover:bg-brand-100 disabled:opacity-50"
                    onClick={() => setWhatifChanges((cs) => cs.filter((_, j) => j !== i))}><X size={14} aria-hidden="true" /></button>
                </li>
              ))}
            </ul>
          </div>
        )}
        {!validValue && <p className="mt-3 text-sm text-red-700">Enter zero or a positive value.</p>}
        <div className="mt-5 flex flex-wrap items-center gap-3">
          <button type="button" className="btn btn-primary" disabled={busy || !w.changes.length} onClick={runWhatIf}>Run what-if</button>
          {!w.changes.length && <p className="hint">Add a change to enable comparison.</p>}
        </div>
      </div>

      {res && (
        <Section title={"Result: " + res.description}>
          {!res.feasible ? (
            <>
              <Note tone="err">
                <p className="font-semibold">Demand cannot be met with these changes.</p>
                <p className="mt-1">{(res.diagnosis.likely_causes || []).join(". ") || "Review the available supply and warehouse capacity."}</p>
                <p className="mt-2 text-xs">These diagnostic hints are estimates. Review the affected demand below.</p>
              </Note>
              {res.diagnosis.unmet_by_zone_sku.length > 0 && (
                <div className="card mt-4 overflow-x-auto">
                  <table className="tbl">
                    <thead><tr><th>Zone</th><th>SKU</th><th className="num">Unserved pallets</th></tr></thead>
                    <tbody>{res.diagnosis.unmet_by_zone_sku.slice(0, 15).map((u, i) => <tr key={i}><td>{ent.zone(u.zone)}</td><td>{ent.sku(u.sku)}</td><td className="num">{fmt(u.pallets)}</td></tr>)}</tbody>
                  </table>
                </div>
              )}
            </>
          ) : (
            <>
              <div className="grid gap-4 md:grid-cols-3">
                <Kpi label="Original plan" value={res.reference ? fmt(res.reference.optimised_total) : "n/a"} sub={res.reference ? `Plan ${res.reference.run_id} before scenario changes` : "Calculate an original plan to compare"} />
                <Kpi label="Changed scenario" tone="brand" value={fmt(res.comparison.optimised.total)} sub={solverText(res.status).toLowerCase()} />
                <Kpi label="Cost difference" tone={res.reference && res.reference.delta > 0 ? "bad" : res.reference && res.reference.delta < 0 ? "good" : "default"}
                  value={res.reference ? (res.reference.delta > 0 ? "+" : "") + fmt(res.reference.delta) : "n/a"}
                  sub={res.reference ? res.reference.delta > 0 ? "Higher cost than the original plan" : res.reference.delta < 0 ? "Lower cost than the original plan" : "Same cost as the original plan" : "A reference plan is needed"} />
              </div>
              <button type="button" className="btn btn-secondary mt-4" onClick={() => openRun(res.id, "results")}>View full results</button>
            </>
          )}
        </Section>
      )}
    </div>
  );
}
