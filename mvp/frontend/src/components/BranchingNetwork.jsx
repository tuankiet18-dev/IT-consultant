import { fmt } from "../utils";

// Preview all candidate lanes for the two-stage worked sample.
export default function BranchingNetwork({ scenario }) {
  const { warehouses, transfer_lanes: lanes } = scenario.entities;
  const origins = [...new Set(lanes.map(lane => lane.from_warehouse))];
  const destinations = [...new Set(lanes.map(lane => lane.to_warehouse))];
  const nodes = [
    { id: "factory", name: "Factory", detail: `${fmt(scenario.summary.demand_pallets)} pallets available`, x: 12, y: 130 },
    ...origins.map((id, index) => ({ id, ...warehouses[id], detail: `Capacity ${fmt(warehouses[id].capacity)} pallets`, x: 232, y: 60 + index * 70 })),
    ...destinations.map((id, index) => ({ id, ...warehouses[id], detail: `Capacity ${fmt(warehouses[id].capacity)} pallets`, x: 532, y: 60 + index * 70 })),
    { id: "customer", name: "Customer", detail: `${fmt(scenario.summary.demand_pallets)} pallets needed`, x: 762, y: 130 },
  ];
  const byId = new Map(nodes.map(node => [node.id, node]));
  const links = [
    ...origins.map(id => ({ from: "factory", to: id })),
    ...lanes.map(lane => ({ from: lane.from_warehouse, to: lane.to_warehouse, rate: lane.cost_per_pallet })),
    ...destinations.map(id => ({ from: id, to: "customer" })),
  ];
  return (
    <div className="mt-5 border-t border-slate-100 pt-5">
      <h3 className="text-sm font-semibold text-slate-900">Available routes</h3>
      <p className="hint mt-1">Choose A, B or C to receive goods from the factory. Each can transfer to D, E or F before customer delivery. D can handle only 6 of the 12 pallets.</p>
      <div className="mt-3 overflow-x-auto rounded-lg bg-slate-50 p-3">
        <svg viewBox="0 0 956 280" className="block w-full min-w-[850px]" role="img" aria-label="Available routes: factory to A, B or C, then D, E or F, then customer">
          <defs><marker id="candidate-route-arrow" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto"><path d="M 0 0 L 6 3 L 0 6 Z" fill="#94A3B8" /></marker></defs>
          {[[12, "FACTORY"], [232, "RECEIVING WAREHOUSES"], [532, "DELIVERY WAREHOUSES"], [762, "CUSTOMER"]].map(([x, title]) => (
            <text key={title} x={x} y="26" fontSize="12" fontWeight="600" fill="#64748B">{title}</text>
          ))}
          {links.map(link => {
            const from = byId.get(link.from), to = byId.get(link.to);
            return <path key={`${link.from}-${link.to}`} d={`M ${from.x + 174} ${from.y + 24} C ${from.x + 198} ${from.y + 24}, ${to.x - 24} ${to.y + 24}, ${to.x - 5} ${to.y + 24}`} fill="none" stroke="#94A3B8" strokeWidth="1.5" opacity="0.7" markerEnd="url(#candidate-route-arrow)">
              <title>{from.name} → {to.name}{link.rate !== undefined ? ` · Transfer freight ${fmt(link.rate)} per pallet` : ""}</title>
            </path>;
          })}
          {nodes.map(node => (
            <g key={node.id}>
              <rect x={node.x} y={node.y} width="174" height="48" rx="8" fill="white" stroke={node.capacity < scenario.summary.demand_pallets ? "#D97706" : "#CBD5E1"} />
              <text x={node.x + 12} y={node.y + 19} fontSize="14" fontWeight="600" fill="#334155">{node.name}</text>
              <text x={node.x + 12} y={node.y + 36} fontSize="12" fill="#64748B">{node.detail}</text>
            </g>
          ))}
        </svg>
      </div>
      <p className="mt-2 flex items-center gap-2 text-xs text-amber-700"><span className="h-3 w-3 rounded border border-amber-600" aria-hidden="true" />Orange border marks a warehouse that cannot handle the full demand alone. D has capacity 6; demand is 12.</p>
      <p className="hint mt-2">All 9 warehouse-transfer options are shown above. Calculate the plan to see which routes are used and how many pallets each carries.</p>
    </div>
  );
}
