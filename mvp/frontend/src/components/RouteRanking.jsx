import { useEffect, useState } from "react";
import { api } from "../api";
import { Field, Tag } from "./ui.jsx";
import { fmt } from "../utils";

export default function RouteRanking({ run, ent, focusedPath, onSelectPath }) {
  const pairs = [...run.optimised.outbound, ...(run.optimised.direct || [])];
  const zones = [...new Set(pairs.map(row => row.zone))].sort();
  const [zone, setZone] = useState(zones[0] || "");
  const skus = [...new Set(pairs.filter(row => row.zone === zone).map(row => row.sku))].sort();
  const [chosenSku, setSku] = useState("");
  const sku = skus.includes(chosenSku) ? chosenSku : skus[0] || "";
  const [quantity, setQuantity] = useState(1);
  const [limit, setLimit] = useState(50);
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const q = Number(quantity);
  const validQuantity = quantity !== "" && Number.isFinite(q) && q > 0 && (run.mode !== "milp" || Number.isInteger(q));
  useEffect(() => {
    let cancelled = false;
    onSelectPath(null);
    setData(null); setError("");
    if (!zone || !sku || !validQuantity) { setLoading(false); return; }
    setLoading(true);
    const timer = setTimeout(() => {
      const params = new URLSearchParams({ zone, sku, quantity: String(q), limit: String(limit) });
      api(`/runs/${run.id}/paths?${params}`).then(result => {
        if (!cancelled) setData(result);
      }).catch(err => {
        if (!cancelled) setError(err.message);
      }).finally(() => { if (!cancelled) setLoading(false); });
    }, 150);
    return () => { cancelled = true; clearTimeout(timer); };
  }, [run.id, zone, sku, q, validQuantity, limit, onSelectPath]);
  const pathText = route => [ent.supplier(route.supplier), ...route.warehouses.map(ent.wh), ent.zone(route.zone)].join(" → ");

  return (
    <section className="mt-6 border-t border-slate-200 pt-5" aria-label="Complete route cost ranking">
      <h3 className="text-base font-semibold text-slate-900">Complete route cost ranking</h3>
      <p className="mt-1 text-sm text-slate-600">Cheapest full path first, including freight and handling at every warehouse. Select a row to highlight the entire path above.</p>
      <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <Field label="Ranking customer zone"><select className="input" value={zone} onChange={event => setZone(event.target.value)}>{zones.map(id => <option key={id} value={id}>{ent.zone(id)}</option>)}</select></Field>
        <Field label="Ranking product"><select className="input" value={sku} onChange={event => setSku(event.target.value)}>{skus.map(id => <option key={id} value={id}>{ent.sku(id)}</option>)}</select></Field>
        <Field label="Compare quantity (pallets)"><input className="input" type="number" min={run.mode === "milp" ? 1 : 0.000001} step={run.mode === "milp" ? 1 : "any"} value={quantity} onChange={event => setQuantity(event.target.value)} /></Field>
        <Field label="Routes to show"><select className="input" value={limit} onChange={event => setLimit(Number(event.target.value))}><option value={20}>20 cheapest</option><option value={50}>50 cheapest</option><option value={100}>100 cheapest</option></select></Field>
      </div>
      {!validQuantity && <p className="mt-3 text-sm text-amber-800">Enter {run.mode === "milp" ? "a positive whole number" : "a positive quantity"} of pallets.</p>}
      {loading && <p className="mt-4 text-sm text-slate-500" role="status">Calculating complete route costs…</p>}
      {error && <p className="mt-4 text-sm text-red-700" role="alert">{error}</p>}
      {data && <>
        <div className="mt-4 flex flex-wrap items-center justify-between gap-2 text-sm text-slate-600">
          <p>{data.paths.length} {data.truncated ? "cheapest " : ""}routes shown{data.total_paths != null ? ` of ${fmt(data.total_paths)}` : ""} · Sorted by full-path cost per pallet</p>
          <p>Current allocation for this customer and product: <b className="text-slate-900">{fmt(data.plan_accounting.delivered_pallets)} pallets · {fmt(data.plan_accounting.total_cost)} cost units</b></p>
        </div>
        <div className="mt-3 overflow-x-auto rounded-lg border border-slate-200">
          <table className="tbl" aria-label="Ranked complete routes">
            <thead><tr><th>Rank</th><th>Complete path</th><th className="num">Cost / pallet</th><th className="num">Cost for {fmt(q)} pallets</th><th className="num">Standalone limit</th><th className="num">Plan breakdown</th></tr></thead>
            <tbody>{data.paths.map((route, index) => {
              const active = route.id === focusedPath?.id;
              const mainLimit = route.bottlenecks.find(label => label.endsWith(" capacity")) || route.bottlenecks[0];
              return <tr key={route.id} data-path-id={route.id} data-cost-per-pallet={route.cost_per_pallet} data-path-selected={active} className={`cursor-pointer ${active ? "bg-amber-50" : "hover:bg-slate-50"}`} onClick={() => onSelectPath(route)}>
                <td><span className="font-semibold text-slate-700">{index + 1}</span></td>
                <td className="min-w-[260px]"><button type="button" className="cursor-pointer text-left text-sm font-medium text-brand-800 underline-offset-2 hover:underline focus:underline" aria-pressed={active} aria-label={`Highlight complete route ${pathText(route)}`}>{pathText(route)}</button></td>
                <td className="num font-semibold text-slate-900">{fmt(route.cost_per_pallet)}</td>
                <td className="num">{route.can_carry_quantity ? fmt(route.quoted_total) : <span className="text-amber-800">Exceeds limit</span>}</td>
                <td className="num" title={route.bottlenecks.join(" · ")}><span>{fmt(route.max_pallets)} pallets</span>{mainLimit && <p className="mt-1 whitespace-normal text-xs text-slate-500">{mainLimit}</p>}</td>
                <td className="num min-w-[120px]">{route.plan_pallets > 0 ? <><Tag tone="good">{fmt(route.plan_pallets)} pallets</Tag><p className="mt-1 text-slate-600">{fmt(route.plan_cost)} cost units</p></> : <span className="text-slate-400">0 pallets</span>}</td>
              </tr>;
            })}</tbody>
          </table>
          {data.paths.length === 0 && <p className="px-4 py-5 text-sm text-slate-500">No complete route is available for this customer and product.</p>}
        </div>
        <details className="mt-3 text-xs text-slate-500"><summary className="cursor-pointer">How costs and limits are calculated</summary><p className="mt-2 leading-relaxed">Prices include all freight and warehouse handling. Standalone limits assume this path uses the resources alone; other goods and manual decisions share those limits. Plan breakdown groups the recorded flows into complete paths; where goods merge, this is an accounting split.</p></details>
        {data.truncated && <p className="mt-2 text-xs text-slate-500">Only the cheapest {limit} paths are listed. The current plan may also use other paths.</p>}
      </>}
    </section>
  );
}
