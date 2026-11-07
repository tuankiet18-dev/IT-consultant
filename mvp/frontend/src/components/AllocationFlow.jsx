import { useEffect, useState } from "react";
import { fmt } from "../utils";

function routes(rows, origin, destination) {
  const totals = new Map();
  for (const row of rows || []) {
    const key = JSON.stringify([row[origin], row[destination]]);
    const route = totals.get(key) || { from: row[origin], to: row[destination], pallets: 0 };
    route.pallets += row.pallets;
    totals.set(key, route);
  }
  return [...totals.values()].filter(route => route.pallets > 0);
}

function withOptions(options, used, origin, destination) {
  const all = new Map((options || []).map(row => [JSON.stringify([row[origin], row[destination]]), {
    ...row, from: row[origin], to: row[destination], pallets: 0,
  }]));
  for (const route of used) {
    const key = JSON.stringify([route.from, route.to]);
    all.set(key, { ...all.get(key), ...route });
  }
  return [...all.values()];
}

function connectedWarehouses(start, transfers, reverse) {
  const visited = new Set([start]);
  const queue = [start];
  for (let index = 0; index < queue.length; index += 1) {
    for (const route of transfers) {
      const origin = reverse ? route.to : route.from;
      const destination = reverse ? route.from : route.to;
      if (origin === queue[index] && !visited.has(destination)) {
        visited.add(destination);
        queue.push(destination);
      }
    }
  }
  return visited;
}

export default function AllocationFlow({ plan, ent, network, focusedPath, onClearPath }) {
  const [highlight, setHighlight] = useState("");
  const [showUnused, setShowUnused] = useState(true);
  const [selectedKey, setSelectedKey] = useState(null);
  useEffect(() => {
    if (focusedPath) { setShowUnused(true); setHighlight(""); setSelectedKey(null); }
  }, [focusedPath]);
  const previewEdges = new Set(focusedPath ? [
    ...(focusedPath.warehouses.length ? ["in-" + JSON.stringify([focusedPath.supplier, focusedPath.warehouses[0]])] : ["direct-" + JSON.stringify([focusedPath.supplier, focusedPath.zone])]),
    ...focusedPath.warehouses.slice(1).map((id, index) => "transfer-" + JSON.stringify([focusedPath.warehouses[index], id])),
    ...(focusedPath.warehouses.length ? ["out-" + JSON.stringify([focusedPath.warehouses.at(-1), focusedPath.zone])] : []),
  ] : []);
  const previewNodes = new Set(focusedPath ? ["supplier-" + focusedPath.supplier, ...focusedPath.warehouses.map(id => "warehouse-" + id), "zone-" + focusedPath.zone] : []);
  const selectedInbound = routes(plan.inbound, "supplier", "warehouse");
  const selectedTransfers = routes(plan.transfers, "from_warehouse", "to_warehouse");
  const selectedOutbound = routes(plan.outbound, "warehouse", "zone");
  const selectedDirect = routes(plan.direct, "supplier", "zone");
  const allInbound = withOptions(network?.inbound_lanes, selectedInbound, "supplier", "warehouse");
  const allTransfers = withOptions(network?.transfer_lanes, selectedTransfers, "from_warehouse", "to_warehouse");
  const allOutbound = withOptions(network?.outbound_lanes, selectedOutbound, "warehouse", "zone");
  const allDirect = withOptions(network?.direct_lanes, selectedDirect, "supplier", "zone");
  const inbound = allInbound.filter(route => showUnused || route.pallets > 0);
  const transfers = allTransfers.filter(route => showUnused || route.pallets > 0);
  const outbound = allOutbound.filter(route => showUnused || route.pallets > 0);
  const direct = allDirect.filter(route => showUnused || route.pallets > 0);
  const warehouseIds = [...new Set([
    ...inbound.map(route => route.to), ...transfers.flatMap(route => [route.from, route.to]), ...outbound.map(route => route.from),
  ])].sort();
  // Keep warehouse stages stable when hiding unused routes.
  const allWarehouseIds = [...new Set([...allInbound.map(route => route.to), ...allTransfers.flatMap(route => [route.from, route.to]), ...allOutbound.map(route => route.from)])];
  const levels = new Map(allWarehouseIds.map(id => [id, 1]));
  const indegree = new Map(allWarehouseIds.map(id => [id, 0]));
  for (const route of allTransfers) indegree.set(route.to, indegree.get(route.to) + 1);
  const queue = allWarehouseIds.filter(id => indegree.get(id) === 0);
  for (let index = 0; index < queue.length; index += 1) {
    for (const route of allTransfers.filter(route => route.from === queue[index])) {
      levels.set(route.to, Math.max(levels.get(route.to), levels.get(route.from) + 1));
      indegree.set(route.to, indegree.get(route.to) - 1);
      if (indegree.get(route.to) === 0) queue.push(route.to);
    }
  }
  const warehouseStages = allWarehouseIds.length ? Math.max(1, ...levels.values()) : 0;
  const finalStage = warehouseStages + 1;
  const columnGap = warehouseStages > 1 ? 250 : 330;
  // Trace actual flows; tracing all candidate edges would highlight almost everything.
  const upstream = highlight ? connectedWarehouses(highlight, selectedTransfers, true) : new Set(warehouseIds);
  const downstream = highlight ? connectedWarehouses(highlight, selectedTransfers, false) : new Set(warehouseIds);
  const nodes = [
    ...[...new Set([...inbound, ...direct].map(route => route.from))].sort().map(id => ({
      key: "supplier-" + id, id, stage: 0, name: ent.supplier(id),
      pallets: [...selectedInbound, ...selectedDirect].filter(route => route.from === id).reduce((sum, route) => sum + route.pallets, 0),
    })),
    ...warehouseIds.map(id => ({
      key: "warehouse-" + id, id, stage: levels.get(id), name: ent.wh(id), capacity: network?.warehouses[id]?.capacity,
      pallets: [...selectedInbound, ...selectedTransfers].filter(route => route.to === id).reduce((sum, route) => sum + route.pallets, 0),
    })),
    ...[...new Set([...outbound, ...direct].map(route => route.to))].sort().map(id => ({
      key: "zone-" + id, id, stage: finalStage, name: ent.zone(id),
      pallets: [...selectedOutbound, ...selectedDirect].filter(route => route.to === id).reduce((sum, route) => sum + route.pallets, 0),
    })),
  ];
  const columns = Array.from({ length: finalStage + 1 }, (_, stage) => nodes.filter(node => node.stage === stage));
  const height = Math.max(1, ...columns.map(column => column.length)) * 72 + 64;
  const width = finalStage * columnGap + 204;
  for (const column of columns) {
    column.forEach((node, index) => {
      node.x = 12 + node.stage * columnGap;
      node.y = 48 + (height - 64 - column.length * 72) / 2 + index * 72;
    });
  }
  const byKey = new Map(nodes.map(node => [node.key, node]));
  const wh = id => network?.warehouses[id] || {};
  const links = [
    ...direct.map(route => ({ ...route, kind: "Direct delivery", key: "direct-" + JSON.stringify([route.from, route.to]), fromKey: "supplier-" + route.from, toKey: "zone-" + route.to, color: "#EC4899", handling: 0, active: !highlight })),
    ...inbound.map(route => ({ ...route, kind: "Supplier delivery", key: "in-" + JSON.stringify([route.from, route.to]), fromKey: "supplier-" + route.from, toKey: "warehouse-" + route.to, color: "#3B82F6", handling: wh(route.to).handling_in, active: upstream.has(route.to) })),
    ...transfers.map(route => ({ ...route, kind: "Warehouse transfer", key: "transfer-" + JSON.stringify([route.from, route.to]), fromKey: "warehouse-" + route.from, toKey: "warehouse-" + route.to, color: "#8B5CF6", handling: network ? (wh(route.from).handling_out || 0) + (wh(route.to).handling_in || 0) : undefined, active: (upstream.has(route.from) && upstream.has(route.to)) || (downstream.has(route.from) && downstream.has(route.to)) })),
    ...outbound.map(route => ({ ...route, kind: "Customer delivery", key: "out-" + JSON.stringify([route.from, route.to]), fromKey: "warehouse-" + route.from, toKey: "zone-" + route.to, color: "#14B8A6", handling: wh(route.from).handling_out, active: downstream.has(route.from) })),
  ].sort((a, b) => Number(previewEdges.has(a.key)) - Number(previewEdges.has(b.key)) || Number(a.pallets > 0) - Number(b.pallets > 0));
  const maximum = links.reduce((largest, route) => Math.max(largest, route.pallets), 1);
  const selected = links.find(route => route.key === selectedKey);
  const usedCount = links.filter(route => route.pallets > 0).length;
  const unavailableCount = links.filter(route => route.available === false).length;
  const selectedName = selected ? `${byKey.get(selected.fromKey).name} → ${byKey.get(selected.toKey).name}` : "";
  const detail = route => `${route.pallets > 0 ? "Used" : route.available === false ? "Unavailable" : "Not used"} · ${fmt(route.pallets)} pallets${route.cost_per_pallet != null ? ` · Freight ${fmt(route.cost_per_pallet)} cost units/pallet` : ""}${route.handling != null ? ` · Handling ${fmt(route.handling)} cost units/pallet` : ""}${route.unavailable_reason ? ` · ${route.unavailable_reason}` : ""}`;
  if (!links.length) return <p className="hint">No routes are available for this plan.</p>;

  return (
    <div>
      <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="text-sm font-medium text-slate-700">{usedCount} routes used{network && showUnused ? ` of ${links.length} declared` : ""} · All products</p>
          <p className="mt-1 text-xs text-slate-500">Coloured lines carry goods in this plan. Width shows pallets, not cost.</p>
        </div>
        <div className="flex flex-wrap items-center gap-4">
          {network && <label className="flex cursor-pointer items-center gap-2 text-sm text-slate-600">
            <input type="checkbox" checked={showUnused} onChange={event => { setShowUnused(event.target.checked); setSelectedKey(null); onClearPath?.(); }} className="h-4 w-4 accent-brand-600" /> Show unused routes
          </label>}
          {allWarehouseIds.length > 0 && <label className="flex items-center gap-2 text-sm text-slate-600">
            Highlight a warehouse
            <select className="input w-auto" value={highlight} onChange={event => { setHighlight(event.target.value); onClearPath?.(); }}>
              <option value="">All warehouses</option>
              {allWarehouseIds.sort().map(id => <option key={id} value={id}>{ent.wh(id)}</option>)}
            </select>
          </label>}
        </div>
      </div>
      <p className="mb-3 text-xs text-slate-500">Highlighting changes the view only. Use Create manual route to change shipments and recalculate cost.</p>
      {focusedPath && <div className="mb-3 rounded-lg border border-amber-300 bg-amber-50 p-3 text-sm" aria-live="polite">
        <div className="flex flex-wrap items-start justify-between gap-3"><p className="font-semibold text-amber-950">{[ent.supplier(focusedPath.supplier), ...focusedPath.warehouses.map(ent.wh), ent.zone(focusedPath.zone)].join(" → ")}</p><button type="button" className="cursor-pointer text-xs font-medium text-amber-900 underline" onClick={onClearPath}>Clear route highlight</button></div>
        <p className="mt-1 text-amber-950">Full-path cost {fmt(focusedPath.cost_per_pallet)} per pallet = {fmt(focusedPath.freight_per_pallet)} freight + {fmt(focusedPath.handling_per_pallet)} handling.</p>
        <p className="mt-1 text-xs text-amber-900">{ent.sku(focusedPath.sku)} · Plan breakdown: {fmt(focusedPath.plan_pallets)} pallets, {fmt(focusedPath.plan_cost)} cost units · Standalone limit {fmt(focusedPath.max_pallets)} pallets. Amber previews this complete path; the plan stays unchanged.</p>
      </div>}
      <div className="max-h-[560px] overflow-auto rounded-lg bg-slate-50 p-3">
        <svg viewBox={`0 0 ${width} ${height}`} className="block w-full" style={{ minWidth: warehouseStages > 3 ? width : warehouseStages > 1 ? Math.max(900, (finalStage + 1) * 180) : Math.max(640, width) }} role="img" aria-label="Allocation flow from suppliers through warehouses to customer zones, with available options and selected shipments">
          {columns.map((column, stage) => (
            <text key={stage} x={12 + stage * columnGap} y="22" fontSize="13" fontWeight="600" fill="#64748B">
              {stage === 0 ? "SUPPLIERS" : stage === finalStage ? "CUSTOMER ZONES" : warehouseStages > 1 ? `WAREHOUSES · STAGE ${stage}` : "WAREHOUSES"}
            </text>
          ))}
          {links.map(route => {
            const from = byKey.get(route.fromKey), to = byKey.get(route.toKey);
            const bend = Math.min(65, (to.x - from.x - 180) / 2);
            const used = route.pallets > 0;
            const directBypass = route.kind === "Direct delivery" && warehouseIds.length > 0;
            const curve = directBypass
              ? `M ${from.x + 180} ${from.y + 25} Q ${from.x + 200} 34, ${from.x + 222} 34 L ${to.x - 42} 34 Q ${to.x - 20} 34, ${to.x} ${to.y + 25}`
              : `M ${from.x + 180} ${from.y + 25} C ${from.x + 180 + bend} ${from.y + 25}, ${to.x - bend} ${to.y + 25}, ${to.x} ${to.y + 25}`;
            const preview = previewEdges.has(route.key);
            const opacity = focusedPath ? (preview ? 1 : 0.12) : selectedKey === route.key ? 1 : used ? (!highlight || route.active ? 0.85 : 0.18) : 0.6;
            const label = `${from.name} → ${to.name}. ${detail(route)}`;
            return (
              <path key={route.key} data-route-kind={route.kind} data-route-from={route.from} data-route-to={route.to} data-used={used} data-available={route.available !== false} data-path-preview={preview}
                d={curve}
                fill="none" stroke={preview ? "#D97706" : used ? route.color : route.available === false ? "#DC2626" : "#94A3B8"} strokeDasharray={preview || used ? undefined : "5 5"}
                strokeWidth={preview ? 6 : used ? 3 + route.pallets / maximum * 11 : selectedKey === route.key ? 3 : 2} opacity={opacity}
                role="button" tabIndex={0} aria-label={label} className="cursor-pointer focus:outline-none focus:stroke-slate-900"
                onClick={() => setSelectedKey(route.key)} onFocus={() => setSelectedKey(route.key)}
                onKeyDown={event => { if (event.key === "Enter" || event.key === " ") { event.preventDefault(); setSelectedKey(route.key); } }}>
                <title>{label}</title>
              </path>
            );
          })}
          {nodes.map(node => {
            const warehouse = node.stage > 0 && node.stage < finalStage;
            const used = node.pallets > 0;
            const preview = previewNodes.has(node.key);
            const filled = warehouse && used && !preview;
            return (
              <g key={node.key} opacity={focusedPath && !preview ? 0.3 : 1} data-path-preview={preview}>
                <title>{node.name} · {fmt(node.pallets)} pallets{node.capacity != null ? ` · Capacity ${fmt(node.capacity)} pallet-equivalents` : ""}</title>
                <rect x={node.x} y={node.y} width="180" height="50" rx="8" fill={preview ? "#FEF3C7" : filled ? "#2563EB" : "#FFFFFF"} stroke={preview ? "#D97706" : filled ? "#2563EB" : "#CBD5E1"} strokeWidth={preview ? 2 : 1} />
                <text x={node.x + 12} y={node.y + 19} fontSize={warehouseStages > 1 ? 14 : 13} fontWeight="600" fill={filled ? "#FFFFFF" : "#334155"}>
                  {node.name.length > 21 ? node.name.slice(0, 20) + "…" : node.name}
                </text>
                <text x={node.x + 12} y={node.y + 37} fontSize="12" fill={filled ? "#DBEAFE" : "#64748B"}>{focusedPath ? preview ? `${fmt(focusedPath.plan_pallets)} accounted pallets` : "Other route" : `${fmt(node.pallets)} pallets${node.capacity === 0 ? " · Unavailable" : used ? "" : " · Not used"}`}</text>
              </g>
            );
          })}
        </svg>
      </div>
      {warehouseStages > 3 && <p className="hint mt-2">Scroll horizontally to follow all {warehouseStages} warehouse stages.</p>}
      <div className="mt-3 flex flex-wrap gap-x-5 gap-y-2 text-xs text-slate-500">
        {direct.length > 0 && <span className="flex items-center gap-2"><i className="h-2 w-5 rounded bg-pink-500" aria-hidden="true" />Factory to customer</span>}
        {inbound.length > 0 && <span className="flex items-center gap-2"><i className="h-2 w-5 rounded bg-blue-500" aria-hidden="true" />Supplier deliveries</span>}
        {transfers.length > 0 && <span className="flex items-center gap-2"><i className="h-2 w-5 rounded bg-violet-500" aria-hidden="true" />Warehouse transfers</span>}
        {outbound.length > 0 && <span className="flex items-center gap-2"><i className="h-2 w-5 rounded bg-teal-500" aria-hidden="true" />Customer deliveries</span>}
        {network && showUnused && <span className="flex items-center gap-2"><i className="w-5 border-t-2 border-dashed border-slate-400" aria-hidden="true" />Unused options</span>}
        {unavailableCount > 0 && <span className="flex items-center gap-2"><i className="w-5 border-t-2 border-dashed border-red-600" aria-hidden="true" />Unavailable</span>}
        {focusedPath && <span className="flex items-center gap-2 text-amber-800"><i className="h-1.5 w-5 rounded bg-amber-600" aria-hidden="true" />Selected complete path preview</span>}
      </div>
      {selected ? <div className="mt-4 rounded-lg border border-slate-200 bg-slate-50 px-4 py-3 text-sm" aria-live="polite">
          <p className="font-semibold text-slate-800">{selectedName}</p>
          <p className="mt-1 text-slate-600">{detail(selected)}</p>
          {selected.cost_per_pallet != null && selected.handling != null && <p className="mt-1 text-slate-600">This leg costs {fmt(selected.cost_per_pallet + selected.handling)} per pallet including handling. Complete-path costs include the other legs.</p>}
      </div> : <p className="hint mt-3">Select a line for its freight, handling and planned pallets.</p>}
    </div>
  );
}
