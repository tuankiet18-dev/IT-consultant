"""Optimize whole-pallet flows for one period using SciPy/HiGHS MILP."""

from collections import defaultdict
from decimal import Decimal
from math import inf, isfinite

import numpy as np
from scipy.optimize import LinearConstraint, milp
from scipy.sparse import coo_array

from .models import AllocationResult, Problem, Status

Flow = tuple[str, str, str]


def _allowed_flows(problem: Problem) -> tuple[list[Flow], list[Flow]]:
    """One variable per allowed lane and SKU with positive supply or demand."""
    supply_skus: dict[str, list[str]] = defaultdict(list)
    demand_skus: dict[str, list[str]] = defaultdict(list)
    for (source, sku), pallets in problem.supply.items():
        if pallets > 0:
            supply_skus[source].append(sku)
    for (destination, sku), pallets in problem.demand.items():
        if pallets > 0:
            demand_skus[destination].append(sku)
    return (
        [(s, w, sku) for s, w in problem.inbound_rates for sku in supply_skus[s]],
        [(w, d, sku) for w, d in problem.outbound_rates for sku in demand_skus[d]],
    )


def _constraints(
    problem: Problem, inbound: list[Flow], outbound: list[Flow]
) -> LinearConstraint:
    """Build a sparse constraint matrix; inbound columns precede outbound columns."""
    row_index: list[int] = []
    col_index: list[int] = []
    entries: list[int] = []
    lower: list[float] = []
    upper: list[float] = []

    def add_row(lo: float, hi: float) -> int:
        index = len(lower)
        lower.append(lo)
        upper.append(hi)
        return index

    def add_entry(row: int, col: int, value: int = 1) -> None:
        row_index.append(row)
        col_index.append(col)
        entries.append(value)

    supply_rows = {key: add_row(-inf, count) for key, count in problem.supply.items()}
    demand_rows = {key: add_row(count, count) for key, count in problem.demand.items()}
    capacity_rows = {
        wh: add_row(-inf, warehouse.capacity_pallets)
        for wh, warehouse in problem.warehouses.items()
    }
    balance_keys = dict.fromkeys(
        [(wh, sku) for _, wh, sku in inbound] + [(wh, sku) for wh, _, sku in outbound]
    )
    balance_rows = {key: add_row(0, 0) for key in balance_keys}

    for col, (source, wh, sku) in enumerate(inbound):
        add_entry(supply_rows[source, sku], col)
        add_entry(capacity_rows[wh], col)
        add_entry(balance_rows[wh, sku], col)
    for col, (wh, destination, sku) in enumerate(outbound, start=len(inbound)):
        add_entry(demand_rows[destination, sku], col)
        add_entry(balance_rows[wh, sku], col, -1)
    matrix = coo_array(
        (entries, (row_index, col_index)),
        shape=(len(lower), len(inbound) + len(outbound)),
        dtype=float,
    ).tocsc()
    return LinearConstraint(matrix, lower, upper)


def _decode_plan(
    values: np.ndarray,
    constraints: LinearConstraint,
    inbound: list[Flow],
    outbound: list[Flow],
    unit_costs: list[Decimal],
    status: Status,
) -> AllocationResult:
    """Decode solver numbers as integers and reject unusable solver vectors."""
    if values.shape != (len(unit_costs),) or not np.all(np.isfinite(values)):
        return AllocationResult(Status.ERROR, message="solver returned an invalid flow vector")
    rounded = np.rint(values)
    if np.any(rounded < 0) or np.any(np.abs(values - rounded) > 1e-6):
        return AllocationResult(Status.ERROR, message="solver returned non-integer pallet flows")
    row_values = constraints.A @ rounded
    if np.any(row_values < constraints.lb) or np.any(row_values > constraints.ub):
        return AllocationResult(Status.ERROR, message="rounded flows violate model constraints")
    counts = [int(count) for count in rounded]
    split = len(inbound)
    return AllocationResult(
        status=status,
        inbound={key: count for key, count in zip(inbound, counts[:split]) if count},
        outbound={key: count for key, count in zip(outbound, counts[split:]) if count},
        total_cost=sum((count * cost for count, cost in zip(counts, unit_costs)), Decimal(0)),
    )


def optimize(problem: Problem, *, time_limit_seconds: float | None = None) -> AllocationResult:
    """Solve validated inputs without reading or writing files."""
    options: dict[str, float] = {"mip_rel_gap": 0.0}
    if time_limit_seconds is not None:
        if not isfinite(time_limit_seconds) or time_limit_seconds <= 0:
            raise ValueError("time_limit_seconds must be finite and positive")
        options["time_limit"] = time_limit_seconds

    if not any(problem.demand.values()):
        return AllocationResult(Status.OPTIMAL, total_cost=Decimal(0))
    inbound, outbound = _allowed_flows(problem)
    if not inbound or not outbound:
        return AllocationResult(
            Status.INFEASIBLE, message="positive demand requires allowed inbound and outbound flows"
        )

    unit_costs = [
        problem.inbound_rates[s, w] + problem.warehouses[w].handling_cost_per_pallet
        for s, w, _ in inbound
    ] + [problem.outbound_rates[w, d] for w, d, _ in outbound]
    try:
        constraints = _constraints(problem, inbound, outbound)
        result = milp(
            c=[float(cost) for cost in unit_costs],
            integrality=np.ones(len(unit_costs), dtype=np.uint8),
            constraints=constraints,
            options=options,
        )
    except (ValueError, OverflowError) as exc:
        return AllocationResult(Status.ERROR, message=f"solver rejected the model: {exc}")

    if result.status == 2:
        return AllocationResult(Status.INFEASIBLE, message=result.message)
    if result.status not in (0, 1) or result.x is None:
        return AllocationResult(Status.ERROR, message=result.message)
    status = Status.OPTIMAL if result.status == 0 else Status.FEASIBLE
    return _decode_plan(result.x, constraints, inbound, outbound, unit_costs, status)
