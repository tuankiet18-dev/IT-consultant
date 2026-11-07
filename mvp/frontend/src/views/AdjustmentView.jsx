import { ArrowLeft } from "lucide-react";
import { useApp } from "../store.jsx";
import { Note, PageHead } from "../components/ui.jsx";
import ManualRouteForm from "../components/ManualRouteForm.jsx";
import FinalDeliveryForm from "../components/FinalDeliveryForm.jsx";
import { fmt } from "../utils";

function AdjustmentView({ route }) {
  const { run: r, go } = useApp();
  const locked = r.state !== "draft";
  return (
    <div>
      <PageHead title={route ? "Manual route" : "Delivery warehouse"} lead={route ? "Choose the complete path for your goods." : "Fix the final warehouse; upstream routes are recalculated."}>
        <button type="button" className="btn btn-secondary" onClick={() => go("results")}><ArrowLeft size={15} aria-hidden="true" />Back to Results</button>
      </PageHead>
      <div className="mb-5 flex flex-wrap gap-x-6 gap-y-1 rounded-lg border border-slate-200 bg-white px-4 py-3 text-sm text-slate-600">
        <span>Current plan <b className="text-slate-900">{fmt(r.comparison.optimised.total)}</b></span>
        <span>Original plan <b className="text-slate-900">{fmt(r.optimum_total)}</b></span>
        <span>Changes create a new version</span>
      </div>
      {locked ? <Note>This plan is {r.state}. Start a new version from Results to make changes.</Note> : route ? <ManualRouteForm key={r.id} locked={false} /> : <FinalDeliveryForm key={r.id} locked={false} />}
      {!locked && (!route || r.network?.outbound_lanes.length > 0) && <div className="mt-4 text-sm text-slate-500">
        <button type="button" className="cursor-pointer text-brand-800 underline underline-offset-2" onClick={() => go(route ? "delivery" : "route")}>{route ? "Only change the delivery warehouse" : "Choose a complete route instead"}</button>
      </div>}
    </div>
  );
}

export function ManualRouteView() { return <AdjustmentView route />; }
export function DeliveryWarehouseView() { return <AdjustmentView route={false} />; }
