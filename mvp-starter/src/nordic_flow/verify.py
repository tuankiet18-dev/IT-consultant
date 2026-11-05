"""Independently check a plan against its original input data."""

from collections import Counter
from dataclasses import dataclass
from decimal import Decimal

from .models import AllocationResult, Problem, Status


@dataclass(frozen=True)
class VerificationIssue:
    code: str
    message: str


@dataclass(frozen=True)
class CostBreakdown:
    inbound_cost: Decimal
    handling_cost: Decimal
    outbound_cost: Decimal

    @property
    def total_cost(self) -> Decimal:
        return self.inbound_cost + self.handling_cost + self.outbound_cost


@dataclass(frozen=True)
class VerificationReport:
    issues: tuple[VerificationIssue, ...]
    costs: CostBreakdown | None = None

    @property
    def ok(self) -> bool:
        return not self.issues and self.costs is not None


def _flow_issue(key: object, quantity: object, leg: str) -> VerificationIssue | None:
    if (
        not isinstance(key, tuple)
        or len(key) != 3
        or not all(isinstance(part, str) and part.strip() for part in key)
    ):
        return VerificationIssue("flow_key", f"{leg} flow has invalid key: {key!r}")
    if type(quantity) is not int or quantity < 0:
        return VerificationIssue(
            "quantity", f"{leg} flow {key!r} must have a non-negative integer pallet count"
        )
    return None


def verify_plan(problem: Problem, result: AllocationResult) -> VerificationReport:
    """Check feasibility and cost, without the optimizer or its constraint matrix.

    A passing report does not prove optimality. Costs are omitted if any flow
    is malformed or cannot be priced; otherwise they describe the submitted plan
    even if a constraint or its reported total is wrong.
    """
    if result.status not in (Status.OPTIMAL, Status.FEASIBLE):
        return VerificationReport(
            (VerificationIssue("status", f"{result.status} does not contain a plan to verify"),)
        )

    issues: list[VerificationIssue] = []
    by_supply: Counter[tuple[str, str]] = Counter()
    by_demand: Counter[tuple[str, str]] = Counter()
    warehouse_load: Counter[str] = Counter()
    warehouse_in: Counter[tuple[str, str]] = Counter()
    warehouse_out: Counter[tuple[str, str]] = Counter()
    inbound_cost = handling_cost = outbound_cost = Decimal(0)
    can_price = True

    for key, quantity in result.inbound.items():
        issue = _flow_issue(key, quantity, "inbound")
        if issue is not None:
            issues.append(issue)
            can_price = False
            continue
        source, warehouse, sku = key
        by_supply[source, sku] += quantity
        warehouse_load[warehouse] += quantity
        warehouse_in[warehouse, sku] += quantity
        rate = problem.inbound_rates.get((source, warehouse))
        facility = problem.warehouses.get(warehouse)
        if rate is None or facility is None:
            issues.append(VerificationIssue("lane", f"inbound lane {source!r} → {warehouse!r} is not allowed"))
            can_price = False
        else:
            inbound_cost += rate * quantity
            handling_cost += facility.handling_cost_per_pallet * quantity

    for key, quantity in result.outbound.items():
        issue = _flow_issue(key, quantity, "outbound")
        if issue is not None:
            issues.append(issue)
            can_price = False
            continue
        warehouse, destination, sku = key
        by_demand[destination, sku] += quantity
        warehouse_out[warehouse, sku] += quantity
        rate = problem.outbound_rates.get((warehouse, destination))
        if rate is None or warehouse not in problem.warehouses:
            issues.append(VerificationIssue("lane", f"outbound lane {warehouse!r} → {destination!r} is not allowed"))
            can_price = False
        else:
            outbound_cost += rate * quantity

    for key, quantity in by_supply.items():
        limit = problem.supply.get(key)
        if limit is None:
            issues.append(VerificationIssue("supply", f"no supply declared for {key!r}"))
        elif quantity > limit:
            issues.append(VerificationIssue("supply", f"{key!r} ships {quantity} pallets but has only {limit}"))

    for key, required in problem.demand.items():
        delivered = by_demand[key]
        if delivered != required:
            issues.append(VerificationIssue("demand", f"{key!r} receives {delivered} pallets, expected {required}"))
    for key in by_demand:
        if key not in problem.demand:
            issues.append(VerificationIssue("demand", f"no demand declared for {key!r}"))

    for warehouse, facility in problem.warehouses.items():
        quantity = warehouse_load[warehouse]
        if quantity > facility.capacity_pallets:
            issues.append(VerificationIssue(
                "capacity", f"{warehouse!r} receives {quantity} pallets, capacity {facility.capacity_pallets}"
            ))

    for key in dict.fromkeys((*warehouse_in, *warehouse_out)):
        arrived, departed = warehouse_in[key], warehouse_out[key]
        if arrived != departed:
            issues.append(VerificationIssue("balance", f"{key!r} has {arrived} pallets in and {departed} out"))

    costs = CostBreakdown(inbound_cost, handling_cost, outbound_cost) if can_price else None
    if costs is not None and (
        not isinstance(result.total_cost, Decimal)
        or not result.total_cost.is_finite()
        or result.total_cost != costs.total_cost
    ):
        issues.append(VerificationIssue(
            "cost", f"reported cost {result.total_cost} does not match recalculated cost {costs.total_cost}"
        ))
    return VerificationReport(tuple(issues), costs)


def require_verified_costs(problem: Problem, result: AllocationResult) -> CostBreakdown:
    """Return independently verified costs or reject the entire plan."""
    report = verify_plan(problem, result)
    if report.issues:
        details = "; ".join(f"{issue.code}: {issue.message}" for issue in report.issues)
        raise ValueError(f"plan verification failed: {details}")
    assert report.costs is not None  # A report without issues always has costs.
    return report.costs
