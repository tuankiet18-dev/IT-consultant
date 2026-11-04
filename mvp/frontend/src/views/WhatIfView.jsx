import { useState } from "react";
import { Plus, X } from "lucide-react";
import { useApp } from "../store.jsx";
import { Field, Kpi, Note, PageHead, Section } from "../components/ui.jsx";
import { fmt } from "../utils";

export default function WhatIfView() {
  const { scenario, ent, whatif: w, setWhatifChanges, runWhatIf, openRun } = useApp();
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
  return (
    <div>
      <PageHead title="What-if" lead="Try a change on a copy of the data and compare it with the current plan. Nothing here alters the scenario or the approved plan." />
      <div className="card card-pad">
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
          <button type="button" className="btn btn-secondary" onClick={add}><Plus size={16} aria-hidden="true" /> Add change</button>
        </div>
        {w.changes.length > 0 && (
          <ul className="mt-4 flex flex-wrap gap-2">
            {w.changes.map((c, i) => (
              <li key={i} className="inline-flex items-center gap-1 rounded-full border border-brand-200 bg-brand-50 py-1 pl-3 pr-1 text-sm text-brand-800">
                {describe(c)}
                <button type="button" aria-label={`Remove: ${describe(c)}`} className="grid h-6 w-6 cursor-pointer place-items-center rounded-full hover:bg-brand-100"
                  onClick={() => setWhatifChanges((cs) => cs.filter((_, j) => j !== i))}><X size={14} aria-hidden="true" /></button>
              </li>
            ))}
          </ul>
        )}
        <button type="button" className="btn btn-primary mt-4" disabled={!w.changes.length} onClick={runWhatIf}>Run what-if</button>
      </div>

      {res && (
        <Section title={"Result: " + res.description}>
          {!res.feasible ? (
            <>
              <Note tone="err">
                <b>No feasible plan exists with this change. </b>Diagnostic hints (not a proof): {(res.diagnosis.likely_causes || []).join("; ") || "see data checks"}
              </Note>
              {res.diagnosis.unmet_by_zone_sku.length > 0 && (
                <div className="card mt-4 overflow-x-auto">
                  <table className="tbl">
                    <thead><tr><th>Zone</th><th>SKU</th><th className="num">Pallets that cannot be served</th></tr></thead>
                    <tbody>{res.diagnosis.unmet_by_zone_sku.slice(0, 15).map((u, i) => <tr key={i}><td>{ent.zone(u.zone)}</td><td>{ent.sku(u.sku)}</td><td className="num">{fmt(u.pallets)}</td></tr>)}</tbody>
                  </table>
                </div>
              )}
            </>
          ) : (
            <>
              <div className="grid gap-4 md:grid-cols-3">
                <Kpi label="Optimised cost with the change" tone="brand" value={fmt(res.comparison.optimised.total)} sub={`solver ${res.status}`} />
                <Kpi label="Current plan" value={res.reference ? fmt(res.reference.optimised_total) : "n/a"} sub={res.reference ? `run ${res.reference.run_id}` : "no reference run"} />
                <Kpi label="Difference" tone={res.reference && res.reference.delta > 0 ? "bad" : "default"}
                  value={res.reference ? (res.reference.delta > 0 ? "+" : "") + fmt(res.reference.delta) : "n/a"}
                  sub={res.reference && res.reference.delta > 0 ? "the change makes the plan dearer" : "cost units"} />
              </div>
              <button type="button" className="btn btn-secondary mt-4" onClick={() => openRun(res.id, "results")}>Open this what-if run</button>
            </>
          )}
        </Section>
      )}
    </div>
  );
}
