import { useMemo, useState } from "react";
import { Search } from "lucide-react";
import { useApp } from "../store.jsx";
import { Field, Section, Tag } from "../components/ui.jsx";
import { allocMap, fmt } from "../utils";

export default function PlanDetails() {
  const { run: r, ent } = useApp();
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
  const transferMap = new Map();
  for (const [side, flows] of [["baseline", r.baseline.transfers || []], ["optimised", r.optimised.transfers || []]]) {
    for (const flow of flows) {
      const key = JSON.stringify([flow.from_warehouse, flow.to_warehouse, flow.sku]);
      const row = transferMap.get(key) || { ...flow, baseline: 0, optimised: 0 };
      row[side] += flow.pallets;
      transferMap.set(key, row);
    }
  }
  const transferRows = [...transferMap.values()].filter(row => {
    if (only && Math.abs(row.baseline - row.optimised) < 1e-6) return false;
    return !q || ent.sku(row.sku).toLowerCase().includes(q.toLowerCase()) || row.sku.toLowerCase().includes(q.toLowerCase());
  });
  const directMap = new Map();
  for (const [side, flows] of [["baseline", r.baseline.direct || []], ["optimised", r.optimised.direct || []]]) {
    for (const flow of flows) {
      const key = JSON.stringify([flow.supplier, flow.zone, flow.sku]);
      const row = directMap.get(key) || { ...flow, baseline: 0, optimised: 0 };
      row[side] += flow.pallets;
      directMap.set(key, row);
    }
  }
  const directRows = [...directMap.values()].filter(row => (!zone || row.zone === zone) && (!only || Math.abs(row.baseline - row.optimised) > 1e-6) && (!q || ent.sku(row.sku).toLowerCase().includes(q.toLowerCase()) || row.sku.toLowerCase().includes(q.toLowerCase())));

  return (
    <div>
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

      {keys.length > 0 && <div className="card mt-4 overflow-x-auto">
        <table className="tbl">
          <thead><tr><th>Zone</th><th>SKU</th><th>Optimised final warehouse (pallets)</th><th>Baseline final warehouse (pallets)</th><th /></tr></thead>
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
      </div>}
      {keys.length > 0 && <p className="hint mt-2">{rows.length} of {keys.length} warehouse-delivery rows shown.</p>}

      {directMap.size > 0 && <Section title="Direct deliveries" hint="Factory to customer, without warehouse handling."><div className="card overflow-x-auto"><table className="tbl"><thead><tr><th>Factory</th><th>Customer</th><th>Product</th><th className="num">Baseline pallets</th><th className="num">Optimised pallets</th></tr></thead><tbody>{directRows.map(row => <tr key={JSON.stringify([row.supplier, row.zone, row.sku])}><td>{ent.supplier(row.supplier)}</td><td>{ent.zone(row.zone)}</td><td>{ent.sku(row.sku)}</td><td className="num">{r.comparison.baseline_valid ? fmt(row.baseline) : "unusable"}</td><td className="num">{fmt(row.optimised)}</td></tr>)}{!directRows.length && <tr><td colSpan={5}>No direct deliveries match these filters.</td></tr>}</tbody></table></div></Section>}

      {transferMap.size > 0 && (
        <Section title="Warehouse transfers" hint="Pallets moved between warehouses, by product. The zone filter applies to final deliveries above.">
          <div className="card overflow-x-auto">
            <table className="tbl">
              <thead><tr><th>From warehouse</th><th>To warehouse</th><th>SKU</th><th className="num">Baseline pallets</th><th className="num">Optimised pallets</th></tr></thead>
              <tbody>
                {transferRows.map(row => (
                  <tr key={JSON.stringify([row.from_warehouse, row.to_warehouse, row.sku])} className={Math.abs(row.baseline - row.optimised) > 1e-6 ? "row-changed" : ""}>
                    <td>{ent.wh(row.from_warehouse)}</td><td>{ent.wh(row.to_warehouse)}</td><td>{ent.sku(row.sku)}</td>
                    <td className="num">{r.comparison.baseline_valid ? fmt(row.baseline) : "unusable"}</td><td className="num">{fmt(row.optimised)}</td>
                  </tr>
                ))}
                {!transferRows.length && <tr><td colSpan={5} className="py-6 text-center text-slate-500">No transfers match these filters.</td></tr>}
              </tbody>
            </table>
          </div>
          <p className="hint mt-2">Quantities are shown for each leg. Goods can appear on several consecutive legs.</p>
        </Section>
      )}

      {Object.keys(lanes).length > 0 && <Section title="Inbound flows" hint="Pallets from each supplier to each warehouse.">
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
      </Section>}
    </div>
  );
}
