import { useEffect, useMemo, useState } from "react";
import { useApp } from "../store.jsx";
import { Field } from "./ui.jsx";
import { allocMap, fmt } from "../utils";

export default function FinalDeliveryForm({ locked }) {
  const { run: r, ent, applyOverride, busy } = useApp();
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
      <p className="hint">Choose the final warehouse serving this zone. Recalculation finds the supply and transfer routes, creates a new plan and shows the cost difference.</p>
      <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Field label="Zone"><select className="input" value={zone} onChange={(e) => setZone(e.target.value)}>{zones.map((z) => <option key={z} value={z}>{ent.zone(z)}</option>)}</select></Field>
        <Field label="SKU"><select className="input" value={sku} onChange={(e) => setSku(e.target.value)}>{skus.map((s) => <option key={s} value={s}>{ent.sku(s)}</option>)}</select></Field>
        <Field label="Serve from"><select className="input" value={wh} onChange={(e) => setWh(e.target.value)}>{Object.keys(ent.raw.warehouses).map((w) => <option key={w} value={w}>{ent.wh(w)}</option>)}</select></Field>
        <Field label="Exactly (pallets)"><input className="input" type="number" min={0} step={r.mode === "milp" ? 1 : "any"} value={pallets} onChange={(e) => setPallets(e.target.value)} /></Field>
      </div>
      <p className="hint mt-2">Currently: {Object.entries(now).map(([w, p]) => `${ent.wh(w)} ${fmt(p)}`).join(", ") || "–"}</p>
      <Field label="Reason (required)" className="mt-4">
        <input className="input" value={reason} onChange={(e) => setReason(e.target.value)} placeholder="e.g. Customer contract names this warehouse" />
      </Field>
      <button type="button" className="btn btn-primary mt-4" disabled={locked || busy || reason.trim().length < 3 || pallets === "" || !Number.isFinite(+pallets) || +pallets < 0 || (r.mode === "milp" && !Number.isInteger(+pallets))}
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
