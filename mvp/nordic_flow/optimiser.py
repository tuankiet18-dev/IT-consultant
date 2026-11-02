"""Cost-minimising allocation: supplier -> existing warehouse -> customer zone.

x[s,w,p]  pallets of SKU p moved supplier s -> warehouse w
y[w,z,p]  pallets of SKU p moved warehouse w -> zone z

min  sum (inbound + handling_in) * x + (outbound + handling_out) * y
s.t. supply, demand, flow balance at each warehouse (no stock carry-over),
     warehouse capacity (pallet-equivalents), allowed lanes and SKU eligibility.
LP (continuous) uses GLOP; MILP (whole pallets) uses SCIP. Both ship with OR-Tools.
"""
from __future__ import annotations
import math
import time
from ortools.linear_solver import pywraplp
from .schema import Dataset, Plan

_STATUS = {
    pywraplp.Solver.OPTIMAL: "OPTIMAL",
    pywraplp.Solver.FEASIBLE: "FEASIBLE",
    pywraplp.Solver.INFEASIBLE: "INFEASIBLE",
}
SHORTFALL_PENALTY = 1e6


def solve(ds: Dataset, mode: str = "milp", time_limit_s: float = 30.0, allow_shortfall: bool = False,
          pins: dict[tuple[str, str, str], float] | None = None) -> Plan:
    """allow_shortfall adds a penalised slack on demand; used only for diagnosis.

    pins fixes planner decisions: {(warehouse, zone, sku): pallets}. The rest of the plan is re-optimised
    around them. A pin on a lane or SKU that is not allowed makes the problem infeasible by design.
    """
    if mode not in ("lp", "milp"):
        raise ValueError("mode must be 'lp' or 'milp'")
    solver = pywraplp.Solver.CreateSolver("SCIP" if mode == "milp" else "GLOP")
    if solver is None:
        return Plan(status="ERROR", mode=mode)
    solver.SetTimeLimit(int(time_limit_s * 1000))
    var = solver.IntVar if mode == "milp" else solver.NumVar
    inf = solver.infinity()

    x, y = {}, {}
    for (s, w), _ in ds.inbound.items():
        for p in ds.skus:
            if ds.sku_allowed(w, p) and ds.supply.get((s, p), 0) > 0:
                x[s, w, p] = var(0, inf, f"x|{s}|{w}|{p}")
    for (w, z), _ in ds.outbound.items():
        for p in ds.skus:
            if ds.sku_allowed(w, p) and ds.demand.get((z, p), 0) > 0:
                y[w, z, p] = var(0, inf, f"y|{w}|{z}|{p}")
    pins = pins or {}
    for key, q in pins.items():
        if key not in y:
            return Plan(status="INFEASIBLE", mode=mode)     # pinned lane/SKU is not allowed or has no demand
    slack = {}
    if allow_shortfall:
        for (z, p), q in ds.demand.items():
            if q > 0:
                slack[z, p] = solver.NumVar(0, inf, f"u|{z}|{p}")

    for key, q in pins.items():
        solver.Add(y[key] == (round(q) if mode == "milp" else q))
    for (s, p), q in ds.supply.items():
        terms = [v for (s2, w, p2), v in x.items() if s2 == s and p2 == p]
        if terms:
            solver.Add(sum(terms) <= (math.floor(q) if mode == "milp" else q))
    for (z, p), q in ds.demand.items():
        if q <= 0:
            continue
        terms = [v for (w, z2, p2), v in y.items() if z2 == z and p2 == p]
        total = sum(terms) + (slack[z, p] if allow_shortfall else 0)
        solver.Add(total == q)
    for w in ds.warehouses:
        for p in ds.skus:
            ins = [v for (s, w2, p2), v in x.items() if w2 == w and p2 == p]
            outs = [v for (w2, z, p2), v in y.items() if w2 == w and p2 == p]
            if ins or outs:
                solver.Add(sum(ins) == sum(outs))
        load = [ds.skus[p].pallet_factor * v for (s, w2, p), v in x.items() if w2 == w]
        if load:
            solver.Add(sum(load) <= ds.warehouses[w].capacity)

    obj = []
    for (s, w, p), v in x.items():
        obj.append((ds.inbound[s, w] + ds.warehouses[w].handling_in) * v)
    for (w, z, p), v in y.items():
        obj.append((ds.outbound[w, z] + ds.warehouses[w].handling_out) * v)
    for v in slack.values():
        obj.append(SHORTFALL_PENALTY * v)
    solver.Minimize(sum(obj))

    t0 = time.perf_counter()
    code = solver.Solve()
    secs = time.perf_counter() - t0
    status = _STATUS.get(code, "ERROR")
    plan = Plan(status=status, mode=mode, solve_seconds=secs)
    if status in ("OPTIMAL", "FEASIBLE"):
        plan.inbound = {k: round(v.solution_value(), 6) for k, v in x.items() if v.solution_value() > 1e-9}
        plan.outbound = {k: round(v.solution_value(), 6) for k, v in y.items() if v.solution_value() > 1e-9}
        plan.shortfall = {k: round(v.solution_value(), 6) for k, v in slack.items() if v.solution_value() > 1e-9}
        plan.objective = solver.Objective().Value() - SHORTFALL_PENALTY * sum(plan.shortfall.values())
    return plan
