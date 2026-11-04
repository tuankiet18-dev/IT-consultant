export const fmt = (n, d = 0) =>
  n == null ? "n/a" : Number(n).toLocaleString("en-US", { minimumFractionDigits: d, maximumFractionDigits: d });
export const pct = (x) => fmt(x * 100, 0) + "%";

export const COST = [
  { key: "inbound_freight", label: "Inbound freight", color: "#1E293B" },
  { key: "inbound_handling", label: "Inbound handling", color: "#94A3B8" },
  { key: "outbound_freight", label: "Outbound freight", color: "#2563EB" },
  { key: "outbound_handling", label: "Outbound handling", color: "#93C5FD" },
];

// {"zone|sku": {warehouse: pallets}}
export function allocMap(rows) {
  const m = {};
  for (const r of rows) {
    const k = r.zone + "|" + r.sku;
    (m[k] = m[k] || {})[r.warehouse] = r.pallets;
  }
  return m;
}

export const payloadText = (p) =>
  Object.entries(p).map(([k, v]) => `${k}=${typeof v === "object" ? JSON.stringify(v) : v}`).join("  ").slice(0, 220);

export const solverText = (status) =>
  status === "OPTIMAL" ? "Proven optimal" : status === "FEASIBLE" ? "Best found within time limit" : status;
export const stateText = (s) => (s === "approved" ? "Approved" : s === "rejected" ? "Rejected" : "Draft");
export const kindText = (k) => (k === "override" ? "Planner-adjusted" : k === "whatif" ? "What-if" : "Original");

const EVENTS = {
  SCENARIO_UPLOADED: "Data loaded",
  RUN_COMPLETED: "Plan calculated",
  OVERRIDE_APPLIED: "Planner decision applied",
  OVERRIDE_REJECTED: "Planner decision rejected by the solver",
  WHATIF_RUN: "What-if calculated",
  WHATIF_INFEASIBLE: "What-if had no feasible plan",
  EXPLANATION_GENERATED: "Explanation drafted",
  EXPLANATION_APPROVED: "Explanation approved",
  PLAN_APPROVED: "Plan approved",
  PLAN_REJECTED: "Plan rejected",
  EXPORT_DOWNLOADED: "Approved plan exported",
  MAPPING_CONFIRMED: "SKU match confirmed",
};
export const eventText = (t) => EVENTS[t] || t.replaceAll("_", " ").toLowerCase().replace(/^./, (c) => c.toUpperCase());
export const when = (ts) => {
  const d = new Date(ts);
  return isNaN(d) ? ts : d.toLocaleString("en-GB", { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" });
};
