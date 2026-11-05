"""Command-line entry point for testing the complete allocation pipeline."""

import argparse
import sys
from pathlib import Path

from .models import Status
from .service import run_allocation


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Optimize pallet allocation and export verified CSVs.")
    parser.add_argument("input_dir", type=Path, help="directory containing the five input CSVs")
    parser.add_argument("output_dir", type=Path, help="new directory for the three result CSVs")
    parser.add_argument("--time-limit", type=float, metavar="SECONDS", help="optional solver time limit")
    args = parser.parse_args(argv)
    result = run_allocation(
        args.input_dir,
        output_dir=args.output_dir,
        time_limit_seconds=args.time_limit,
    )
    if result.status in (Status.OPTIMAL, Status.FEASIBLE):
        print(f"{result.status.value}: total cost {result.total_cost}. CSVs: {args.output_dir}")
        return 0
    print(f"{result.status.value}: {result.message or 'no plan returned'}", file=sys.stderr)
    return 2 if result.status == Status.INFEASIBLE else 1


if __name__ == "__main__":
    raise SystemExit(main())
