import { useMemo, useState } from "react";
import { ArrowRight, Search } from "lucide-react";
import { useApp } from "../store.jsx";
import { Field, PageHead, Section, Tag } from "../components/ui.jsx";
import { allocMap, fmt } from "../utils";

export default function PlanView() {
  const { run: r, ent, go } = useApp();
  const [zone, setZone] = useState("");
  const [q, setQ] = useState("");
  const [only, setOnly] = useState(false);
  const base = useMemo(() => allocMap(r.baseline.outbound), [r]);
  const opt = useMemo(() => allocMap(r.optimised.outbound), [r]);
  const keys = Object.keys(opt).sort();
  const show = (m) => Object.entries(m || {}).map(([w, p]) => `${ent.wh(w)} ${fmt(p)}`).join(", ") || "–";

  const rows = keys.filter((k) => {
    const [z, s] = k.split("|");
    const changed = JSON.stringify(base[k] || {}) !== JSON.stringify(opt[k]);
    if (zone && zone !== z) return false;
    if (only && !changed) return false;
    if (q && !ent.sku(s).toLowerCase().includes(q.toLowerCase()) && !s.toLowerCase().includes(q.toLowerCase())) return false;
    return true;
  });

  const lanes = {};
  for (const x of r.optimised.inbound) { const k = x.supplier + ">" + x.warehouse; lanes[k] = (lanes[k] || 0) + x.pallets; }

  return (
    <div>
      <PageHead title="Plan" lead="Which warehouse serves each zone and SKU, in pallets per week. Highlighted rows differ from the baseline.">
        <button type="button" className="btn btn-primary" onClick={() => go("review")}>Review & adjust <ArrowRight size={16} aria-hidden="true" /></button>
      </PageHead>

      <div className="card card-pad">
        <div className="grid items-end gap-4 md:grid-cols-[200px_1fr_auto]">
          <Field label="Zone">
            <select className="input" value={zone} onChange={(e) => setZone(e.target.value)}>
              <option value="">All zones</option>
              {Object.keys(ent.raw.zones).map((z) => <option key={z} value={z}>{ent.zone(z)}</option>)}
            </select>
          </Field>
          <Field label="SKU">
            <div className="relative">
              <Search size={16} className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" aria-hidden="true" />
              <input className="input pl-9" value={q} onChange={(e) => setQ(e.target.value)} placeholder="Search SKU" />
            </div>
          </Field>
          <label className="flex min-h-[40px] cursor-pointer items-center gap-2 text-sm text-slate-700">
            <input type="checkbox" checked={only} onChange={(e) => setOnly(e.target.checked)} className="h-4 w-4 accent-brand-600" /> Changed only
          </label>
        </div>
      </div>

      <div className="card mt-4 overflow-x-auto">
        <table className="tbl">
          <thead><tr><th>Zone</th><th>SKU</th><th>Optimised: served from (pallets)</th><th>Baseline: served from (pallets)</th><th /></tr></thead>
          <tbody>
            {rows.map((k) => {
              const [z, s] = k.split("|");
              const changed = JSON.stringify(base[k] || {}) !== JSON.stringify(opt[k]);
              return (
                <tr key={k} className={changed ? "row-changed" : ""}>
                  <td>{ent.zone(z)}</td><td className="font-medium text-slate-900">{ent.sku(s)}</td>
                  <td>{show(opt[k])}</td><td>{r.comparison.baseline_valid ? show(base[k]) : "unusable"}</td>
                  <td>{changed && <Tag tone="info">changed</Tag>}</td>
                </tr>
              );
            })}
            {!rows.length && <tr><td colSpan={5} className="py-8 text-center text-slate-500">No rows match these filters.</td></tr>}
          </tbody>
        </table>
      </div>
      <p className="hint mt-2">{rows.length} of {keys.length} zone-and-SKU rows shown.</p>

      <Section title="Inbound flows" hint="Supplier to warehouse, pallets.">
        <div className="card overflow-x-auto">
          <table className="tbl">
            <thead><tr><th>Supplier</th><th>Warehouse</th><th className="num">Pallets</th></tr></thead>
            <tbody>
              {Object.entries(lanes).sort().map(([k, v]) => {
                const [s, w] = k.split(">");
                return <tr key={k}><td>{ent.supplier(s)}</td><td>{ent.wh(w)}</td><td className="num">{fmt(v)}</td></tr>;
              })}
            </tbody>
          </table>
        </div>
      </Section>
    </div>
  );
}
