import { useEffect, useRef, useState } from "react";
import { ChevronDown, Sparkles } from "lucide-react";
import { useApp } from "../store.jsx";
import { DecisionPanel } from "./ApproveView.jsx";
import { Field, Note, PageHead, RunBanner, Section, Tag } from "../components/ui.jsx";
import { fmt, kindText, solverText, stateText } from "../utils";

function Evidence({ f }) {
  const rows = (f.largest_changes || []).filter((c) => c.route_cost_difference_per_pallet != null);
  const from = (arr) => arr.map((x) => `${x.warehouse} ${fmt(x.pallets)}`).join(", ");
  return (
    <details className="mt-4 rounded-lg border border-slate-200 bg-slate-50 px-4 py-3">
      <summary className="cursor-pointer text-sm font-medium text-slate-700">Check the supporting figures</summary>
      <p className="hint mt-2">Compare the text with the calculated costs and allocation changes.</p>
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
        {f.transfer_pallet_legs != null && <div className="flex justify-between gap-3"><dt className="text-slate-500">Pallets across transfer legs</dt><dd className="font-medium">{fmt(f.transfer_pallet_legs)}</dd></div>}
      </dl>
      {rows.length > 0 && (
        <div className="mt-4 overflow-x-auto rounded-lg border border-slate-200 bg-white">
          <table className="tbl">
            <thead><tr><th>Zone and SKU</th><th>Baseline</th><th>Optimised</th><th className="num">Estimated route cost per pallet</th><th className="num">Difference per pallet</th></tr></thead>
            <tbody>
              {rows.map((c, i) => (
                <tr key={i}><td>{c.zone} · {c.sku}</td><td>{from(c.baseline_from)}</td><td>{from(c.optimised_from)}</td>
                  <td className="num">{fmt(c.baseline_route_cost_per_pallet)} → {fmt(c.optimised_route_cost_per_pallet)}</td>
                  <td className={"num font-medium " + (c.route_cost_difference_per_pallet >= 0 ? "text-emerald-700" : "text-amber-700")}>{fmt(c.route_cost_difference_per_pallet)}</td></tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {rows.length > 0 && <p className="hint mt-2">Route estimates use the cheapest available supplier, delivery to the zone and handling fees.</p>}
      {(f.transfer_movements || []).length > 0 && (
        <div className="mt-4 overflow-x-auto rounded-lg border border-slate-200 bg-white">
          <table className="tbl">
            <thead><tr><th>From warehouse</th><th>To warehouse</th><th>SKU</th><th className="num">Pallets</th></tr></thead>
            <tbody>{f.transfer_movements.map((movement, index) => (
              <tr key={index}><td>{movement.from_warehouse}</td><td>{movement.to_warehouse}</td><td>{movement.sku}</td><td className="num">{fmt(movement.pallets)}</td></tr>
            ))}</tbody>
          </table>
          <p className="px-3 py-2 text-xs text-slate-500">Each row is one transfer leg. The same goods can pass through several warehouses.</p>
        </div>
      )}
      {(f.direct_movements || []).length > 0 && <div className="mt-4 overflow-x-auto rounded-lg border border-slate-200 bg-white"><table className="tbl"><thead><tr><th>Factory</th><th>Customer</th><th>Product</th><th className="num">Direct pallets</th></tr></thead><tbody>{f.direct_movements.map((movement, index) => <tr key={index}><td>{movement.supplier}</td><td>{movement.zone}</td><td>{movement.sku}</td><td className="num">{fmt(movement.pallets)}</td></tr>)}</tbody></table></div>}
    </details>
  );
}

function Explanation({ locked }) {
  const { explanation: e, explain, approveExpl, clearExplanation, config, busy } = useApp();
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
          <p className="hint mt-1">{locked ? "Start a new version to add an explanation." : "Choose a calculated summary or an AI draft. Review the figures and reasoning before approving the text."}</p>
          <div className="mt-4 flex flex-wrap gap-3">
            <button type="button" className="btn btn-secondary" disabled={busy || locked} onClick={() => explain(false)}>Write standard summary</button>
            <button type="button" className="btn btn-primary" disabled={busy || locked || !llmOn} title={llmOn ? "" : "AI assistant unavailable"} onClick={() => explain(true)}>
              <Sparkles size={16} aria-hidden="true" /> Write with AI assistant
            </button>
          </div>
        </>
      ) : (
        <>
          <div className="mt-3 flex flex-wrap gap-2">
            <Tag tone={e.source === "deterministic" ? "info" : "warn"}>{e.source === "deterministic" ? "Standard summary" : "AI draft"}</Tag>
            <Tag tone={e.status === "approved" ? "good" : "neutral"}>{e.status === "approved" ? `Approved by ${e.approved_by}${e.edited ? " (edited)" : ""}` : "Needs review"}</Tag>
          </div>
          {e.reason && <Note tone="warn">{e.reason}</Note>}
          <textarea ref={ref} className="input mt-3 resize-none overflow-hidden px-4 py-3 text-base leading-7" style={{ minHeight: 220 }} value={text} readOnly={locked || e.status === "approved"} onChange={(ev) => setText(ev.target.value)} aria-label="Explanation text" />
          <div className="mt-3 flex flex-wrap gap-3">
            <button type="button" className="btn btn-success" disabled={busy || locked || e.status === "approved"} onClick={() => approveExpl(text)}>Approve explanation</button>
            <button type="button" className="btn btn-secondary" disabled={busy || locked} onClick={clearExplanation}>Start over</button>
          </div>
          {e.facts && <Evidence f={e.facts} />}
        </>
      )}
    </div>
  );
}

function PlannerDecisions({ run, ent }) {
  const routes = run.route_pins || [];
  if (!routes.length && !run.pins.length) return null;
  return (
    <details className="card mt-5">
      <summary className="cursor-pointer px-5 py-4 text-sm font-semibold text-slate-800">Manual decisions ({routes.length + run.pins.length})</summary>
      <div className="space-y-3 border-t border-slate-100 px-5 py-4">
        {routes.map((route, index) => <div key={index} className="text-sm">
          <p className="break-words font-medium text-slate-800">{[ent.supplier(route.supplier), ...route.warehouses.map(ent.wh), ent.zone(route.zone)].join(" → ")}</p>
          <p className="mt-1 text-slate-600">{ent.sku(route.sku)} · {fmt(route.pallets)} pallets · {route.reason}</p>
        </div>)}
        {run.pins.length > 0 && <div className="overflow-x-auto"><table className="tbl">
          <thead><tr><th>Customer</th><th>Product</th><th>Delivery warehouse</th><th>Pallets</th><th>Reason</th></tr></thead>
          <tbody>{run.pins.map((pin, index) => <tr key={index}><td>{ent.zone(pin.zone)}</td><td>{ent.sku(pin.sku)}</td><td>{ent.wh(pin.warehouse)}</td><td>{fmt(pin.pallets)}</td><td>{pin.reason}</td></tr>)}</tbody>
        </table></div>}
      </div>
    </details>
  );
}

export default function ReviewView() {
  const { run: r, runs, openRun, go, ent } = useApp();
  const locked = r.state !== "draft";
  return (
    <div>
      <PageHead title="Review & approve" lead="Check the explanation and decide whether to approve this plan.">
        <button type="button" className="btn btn-secondary" onClick={() => go("results")}>Back to Results</button>
        {!locked && <details className="relative">
          <summary className="btn btn-secondary cursor-pointer list-none">Adjust plan<ChevronDown size={14} aria-hidden="true" /></summary>
          <div className="absolute right-0 z-40 mt-2 w-64 rounded-lg border border-slate-200 bg-white p-2 shadow-lg">
            <button type="button" className="w-full cursor-pointer rounded px-3 py-2 text-left text-sm text-slate-700 hover:bg-slate-50" onClick={() => go("route")}>Create manual route</button>
            {r.network?.outbound_lanes.length > 0 && <button type="button" className="w-full cursor-pointer rounded px-3 py-2 text-left text-sm text-slate-700 hover:bg-slate-50" onClick={() => go("delivery")}>Change delivery warehouse</button>}
          </div>
        </details>}
      </PageHead>
      <RunBanner run={r} />
      <PlannerDecisions run={r} ent={ent} />
      <div className="mt-5"><Explanation locked={locked} /></div>
      <DecisionPanel />
      {runs.length > 1 && (
        <details className="card mt-6">
          <summary className="cursor-pointer px-5 py-4 text-sm font-semibold text-slate-800">Version history ({runs.length})</summary>
          <div className="overflow-x-auto border-t border-slate-100">
            <table className="tbl">
              <thead><tr><th>Plan</th><th>Type</th><th>Status</th><th>Result</th><th /></tr></thead>
              <tbody>{runs.map(x => <tr key={x.id} className={x.id === r.id ? "row-changed" : ""}>
                <td>Plan {x.id}</td><td>{kindText(x.kind)}</td><td>{stateText(x.state)}</td><td>{solverText(x.status)}</td>
                <td>{x.id === r.id ? <Tag tone="info">open</Tag> : <button type="button" className="btn btn-secondary" onClick={() => openRun(x.id, "review")}>Open</button>}</td>
              </tr>)}</tbody>
            </table>
          </div>
        </details>
      )}
    </div>
  );
}
