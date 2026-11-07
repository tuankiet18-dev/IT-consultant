import { useState } from "react";
import { Plus, Trash2 } from "lucide-react";
import { useApp } from "../store.jsx";
import { Field, Tag } from "./ui.jsx";
import { fmt } from "../utils";

export default function ManualRouteForm({ locked }) {
  const { run: r, ent, applyRoute, removeRoute, busy } = useApp();
  const network = r.network;
  const suppliers = Object.keys(network?.suppliers || ent.raw.suppliers);
  const deliveries = [...r.optimised.outbound, ...(r.optimised.direct || [])];
  const zones = [...new Set(deliveries.map(row => row.zone))];
  const [supplier, setSupplier] = useState(suppliers[0] || "");
  const [zone, setZone] = useState(zones[0] || "");
  const skus = [...new Set(deliveries.filter(row => row.zone === zone).map(row => row.sku))];
  const [chosenSku, setSku] = useState("");
  const sku = skus.includes(chosenSku) ? chosenSku : skus[0] || "";
  const [path, setPath] = useState([""]);
  const [routeType, setRouteType] = useState(network?.inbound_lanes.some(lane => lane.available !== false) ? "warehouse" : "direct");
  const isDirect = routeType === "direct";
  const directLane = network?.direct_lanes?.find(lane => lane.supplier === supplier && lane.zone === zone && lane.available !== false);
  const [pallets, setPallets] = useState(1);
  const [reason, setReason] = useState("");
  const manual = r.route_pins || [];
  const demand = deliveries.filter(row => row.zone === zone && row.sku === sku).reduce((sum, row) => sum + row.pallets, 0);
  const nextOptions = previous => (network?.transfer_lanes || []).filter(lane => lane.from_warehouse === previous && lane.available !== false).map(lane => lane.to_warehouse);
  const choices = index => [...new Set(index === 0
    ? (network?.inbound_lanes || []).filter(lane => lane.supplier === supplier && lane.available !== false).map(lane => lane.warehouse)
    : nextOptions(path[index - 1]))].filter(id => !path.slice(0, index).includes(id));
  const complete = path.every(Boolean);
  const inbound = network?.inbound_lanes.find(lane => lane.supplier === supplier && lane.warehouse === path[0] && lane.available !== false);
  const outbound = network?.outbound_lanes.find(lane => lane.warehouse === path.at(-1) && lane.zone === zone && lane.available !== false);
  const transferLegs = path.slice(1).map((id, index) => network?.transfer_lanes.find(lane => lane.from_warehouse === path[index] && lane.to_warehouse === id && lane.available !== false));
  const validPath = isDirect ? !!directLane : complete && inbound && outbound && transferLegs.every(Boolean);
  const perPallet = isDirect ? directLane?.cost_per_pallet : validPath ? inbound.cost_per_pallet + outbound.cost_per_pallet
    + transferLegs.reduce((sum, lane) => sum + lane.cost_per_pallet, 0)
    + path.reduce((sum, id) => sum + network.warehouses[id].handling_in + network.warehouses[id].handling_out, 0) : null;
  const quantity = Number(pallets);
  const validQuantity = Number.isFinite(quantity) && quantity > 0 && quantity <= demand && (r.mode !== "milp" || Number.isInteger(quantity));
  const canAddStop = complete && nextOptions(path.at(-1)).some(id => !path.includes(id));
  const textPath = route => [ent.supplier(route.supplier), ...route.warehouses.map(ent.wh), ent.zone(route.zone)].join(" → ");

  return (
    <div className="card card-pad">
      {!locked && <>
        <p className="text-sm leading-relaxed text-slate-600">Reserve goods on your chosen path. The remaining shipments are recalculated.</p>
        <div className="mt-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <Field label="Route supplier"><select className="input" value={supplier} onChange={event => { setSupplier(event.target.value); setPath([""]); }}>{suppliers.map(id => <option key={id} value={id}>{ent.supplier(id)}</option>)}</select></Field>
          <Field label="Route customer zone"><select className="input" value={zone} onChange={event => setZone(event.target.value)}>{zones.map(id => <option key={id} value={id}>{ent.zone(id)}</option>)}</select></Field>
          <Field label="Route product"><select className="input" value={sku} onChange={event => setSku(event.target.value)}>{skus.map(id => <option key={id} value={id}>{ent.sku(id)}</option>)}</select></Field>
          <Field label="Route pallets"><input className="input" type="number" min={r.mode === "milp" ? 1 : 0.000001} max={demand} step={r.mode === "milp" ? 1 : "any"} value={pallets} onChange={event => setPallets(event.target.value)} /></Field>
        </div>
        <p className="hint mt-2">Customer demand for this product: {fmt(demand)} pallets. Existing manual routes also count towards it.</p>
        {(network?.direct_lanes?.length || 0) > 0 && <Field label="Route type" className="mt-4"><select className="input" value={routeType} onChange={event => setRouteType(event.target.value)}><option value="warehouse">Via warehouses</option><option value="direct">Factory to customer</option></select></Field>}
        {isDirect ? <div className="mt-4 rounded-lg border border-slate-200 bg-slate-50 p-4 text-sm">{directLane ? <><p className="font-medium">{ent.supplier(supplier)} → {ent.zone(zone)}</p><p className="mt-1">{fmt(perPallet)} cost units per pallet · No warehouse handling{validQuantity ? ` · ${fmt(perPallet * quantity)} for ${fmt(quantity)} pallets` : ""}.</p></> : <p className="text-amber-800">No available factory-to-customer route is declared for this supplier and customer.</p>}</div> : <div className="mt-4 rounded-lg border border-slate-200 bg-slate-50 p-4">
          <p className="text-sm font-semibold text-slate-800">Warehouse order</p>
          <div className="mt-3 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {path.map((id, index) => <Field key={index} label={`Warehouse stop ${index + 1}`}>
              <select className="input" value={id} onChange={event => setPath([...path.slice(0, index), event.target.value])}>
                <option value="">Choose a warehouse</option>
                {choices(index).map(candidate => <option key={candidate} value={candidate}>{ent.wh(candidate)}</option>)}
              </select>
            </Field>)}
          </div>
          <div className="mt-3 flex flex-wrap gap-3">
            <button type="button" className="btn btn-secondary" disabled={busy || !canAddStop} onClick={() => setPath([...path, ""])}><Plus size={14} aria-hidden="true" />Add warehouse stop</button>
            {path.length > 1 && <button type="button" className="btn btn-secondary" disabled={busy} onClick={() => setPath(path.slice(0, -1))}>Remove last stop</button>}
          </div>
          {complete && !outbound && <p className="mt-3 text-sm text-amber-800">The last warehouse has no available delivery route to this customer. Add another stop or choose a different route.</p>}
          {validPath && <div className="mt-3 text-sm text-slate-700">
            <p className="break-words font-medium">{[ent.supplier(supplier), ...path.map(ent.wh), ent.zone(zone)].join(" → ")}</p>
            <p className="mt-1">{fmt(perPallet)} cost units per pallet, including all freight and handling on this path{validQuantity ? ` · ${fmt(perPallet * quantity)} for ${fmt(quantity)} pallets` : ""}.</p>
            <p className="hint mt-1">The complete plan also includes the remaining shipments. Recalculation checks shared supply, warehouse and route limits.</p>
          </div>}
        </div>}
        <Field label="Route reason (required)" className="mt-4"><input className="input" value={reason} onChange={event => setReason(event.target.value)} placeholder="e.g. Agreed partner allocation or customer request" /></Field>
        <p className="hint mt-2">Recorded rates are used. Enter negotiated prices in the input files.</p>
        <button type="button" className="btn btn-primary mt-4" disabled={busy || !validPath || !validQuantity || reason.trim().length < 3}
          onClick={() => applyRoute({ supplier, warehouses: isDirect ? [] : path, zone, sku, pallets: quantity, reason: reason.trim() })}>Save route and recalculate</button>
      </>}
      {manual.length > 0 && <div className={locked ? "" : "mt-6 border-t border-slate-100 pt-4"}>
        <h4 className="text-sm font-semibold text-slate-900">Manual routes in this plan</h4>
        <div className="mt-3 space-y-3">{manual.map((route, index) => <div key={index} className="rounded-lg border border-slate-200 p-3 text-sm">
          <div className="flex flex-wrap items-start justify-between gap-3"><p className="min-w-0 break-words font-medium text-slate-800">{textPath(route)}</p><Tag>{fmt(route.pallets)} pallets</Tag></div>
          <p className="mt-1 text-slate-600">{ent.sku(route.sku)} · {route.reason}</p>
          {!locked && <button type="button" className="btn btn-secondary mt-3" disabled={busy} onClick={() => removeRoute(index)} aria-label={`Remove manual route ${index + 1}`}><Trash2 size={14} aria-hidden="true" />Remove route constraint</button>}
        </div>)}</div>
      </div>}
      {locked && manual.length === 0 && <p className="hint">This plan contains no manual routes.</p>}
    </div>
  );
}
