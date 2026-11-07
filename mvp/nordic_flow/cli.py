"""Command line: python -m nordic_flow run <data_dir> | synth <out_dir>"""
from __future__ import annotations
import argparse
import csv
import json
import sys
from pathlib import Path
from .baseline import baseline
from .diagnosis import diagnose
from .evidence import demo_guard, robustness
from .io import load_dataset
from .optimiser import solve
from .report import compare
from .synth import generate
from .validation import has_errors, validate
from .verify import verify_plan


def _write_plan(folder: Path, name: str, plan):
    folder.mkdir(parents=True, exist_ok=True)
    with (folder / f"{name}_outbound.csv").open("w", newline="") as f:
        w = csv.writer(f); w.writerow(["warehouse", "zone", "sku", "pallets"])
        for (wh, z, p), q in sorted(plan.outbound.items()): w.writerow([wh, z, p, q])
    with (folder / f"{name}_inbound.csv").open("w", newline="") as f:
        w = csv.writer(f); w.writerow(["supplier", "warehouse", "sku", "pallets"])
        for (s, wh, p), q in sorted(plan.inbound.items()): w.writerow([s, wh, p, q])
    with (folder / f"{name}_transfers.csv").open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["from_warehouse", "to_warehouse", "sku", "pallets"])
        for (origin, destination, sku), quantity in sorted(plan.transfers.items()):
            writer.writerow([origin, destination, sku, quantity])
    with (folder / f"{name}_direct.csv").open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["supplier", "zone", "sku", "pallets"])
        for (supplier, zone, sku), quantity in sorted(plan.direct.items()):
            writer.writerow([supplier, zone, sku, quantity])


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="nordic_flow")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run"); r.add_argument("data"); r.add_argument("--mode", choices=["lp", "milp"], default="milp")
    r.add_argument("--time-limit", type=float, default=30); r.add_argument("--out")
    s = sub.add_parser("synth"); s.add_argument("out"); s.add_argument("--seed", type=int, default=7)
    sub.add_parser("demo-guard")
    rob = sub.add_parser("robustness")
    rob.add_argument("--seeds", type=int, default=10)
    rob.add_argument("--out", required=True)
    a = ap.parse_args(argv)

    if a.cmd == "demo-guard":
        demo_guard()
        return 0
    if a.cmd == "robustness":
        if a.seeds < 1:
            rob.error("--seeds must be positive")
        robustness(a.seeds, a.out)
        return 0

    if a.cmd == "synth":
        print("wrote", generate(a.out, a.seed)); return 0

    ds, issues = load_dataset(a.data)
    issues += validate(ds, a.mode)
    for i in issues: print(i)
    if has_errors(issues):
        print("Blocked: fix the errors above."); return 2
    base = baseline(ds)
    opt = solve(ds, a.mode, a.time_limit)
    if not opt.usable:
        print("No feasible plan:", json.dumps(diagnose(ds), indent=2)); return 3
    bad = verify_plan(ds, opt)
    if bad:
        print("Plan failed independent check:", *bad, sep="\n  "); return 4
    c = compare(ds, base, opt)
    c["baseline_valid"] = base.status == "BASELINE" and not verify_plan(ds, base)
    if not c["baseline_valid"]:
        c["saving"] = c["saving_pct"] = None
        print(f"optimised {c['optimised']['total']:.2f} ({opt.status}). The preferred-warehouse baseline "
              "could not serve all demand, so no saving is reported.")
    else:
        print(f"baseline {c['baseline']['total']:.2f} ({base.status}) -> optimised {c['optimised']['total']:.2f} "
              f"({opt.status}, {opt.solve_seconds:.2f}s)  saving {c['saving']:.2f} = {c['saving_pct']:.2f}%")
    if a.out:
        out = Path(a.out)
        if c["baseline_valid"]:
            _write_plan(out, "baseline", base)
        else:
            for flow in ("inbound", "outbound", "transfers", "direct"):
                (out / f"baseline_{flow}.csv").unlink(missing_ok=True)
        _write_plan(out, "optimised", opt)
        (out / "comparison.json").write_text(json.dumps(c, indent=2, default=str)); print("results in", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
