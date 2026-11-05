"""Run the Nordic Flow planning pipeline without any user-interface code."""

from pathlib import Path

from .csv_io import load_problem, write_result
from .models import AllocationResult, Status
from .optimizer import optimize
from .verify import require_verified_costs


def run_allocation(
    input_dir: str | Path,
    *,
    output_dir: str | Path | None = None,
    time_limit_seconds: float | None = None,
) -> AllocationResult:
    """Read, solve and verify a scenario, optionally exporting its plan."""
    try:
        problem = load_problem(input_dir)
        result = optimize(problem, time_limit_seconds=time_limit_seconds)
        if result.status not in (Status.OPTIMAL, Status.FEASIBLE):
            return result
        if output_dir is None:
            require_verified_costs(problem, result)
        else:
            write_result(problem, result, output_dir)
    except (ValueError, OSError) as exc:
        return AllocationResult(Status.ERROR, message=str(exc))
    return result
