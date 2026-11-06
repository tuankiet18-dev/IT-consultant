"""Repeatable technical evidence for the Round 2 submission."""
from pathlib import Path
from statistics import median
from tempfile import TemporaryDirectory

from .baseline import baseline
from .explain import build_facts, check_numbers, explain, template_text
from .io import load_dataset
from .optimiser import solve
from .report import compare
from .synth import generate
from .validation import has_errors, validate
from .verify import verify_plan


class SimulatedLLM:
    enabled = True
    model = "simulated"

    def __init__(self, text):
        self.text = text

    def chat(self, messages):
        return self.text


def demo_guard():
    ds, issues = load_dataset(Path(__file__).resolve().parents[1] / "data" / "demo")
    if has_errors(issues + validate(ds, "milp")):
        raise ValueError("Demo dataset failed validation")
    base, opt = baseline(ds), solve(ds)
    if not opt.usable or verify_plan(ds, opt):
        raise ValueError("Demo has no verified optimised plan")
    comparison = compare(ds, base, opt)
    comparison["baseline_valid"] = base.status == "BASELINE" and not verify_plan(ds, base)
    facts = build_facts(ds, base, opt, comparison)
    valid_text = f"The optimised plan costs {facts['optimised_total']:,} cost units."
    invented = 1_000_000
    while not check_numbers(str(invented), facts):
        invented *= 10
    accepted = explain(facts, SimulatedLLM(valid_text))
    rejected = explain(facts, SimulatedLLM(f"{valid_text} It saves {invented}%."))
    if (accepted["source"] != "groq:simulated" or rejected["source"] != "deterministic"
            or rejected["unsupported_numbers"] != [str(invented)]
            or rejected["text"] != template_text(facts)):
        raise RuntimeError("The numeric guard did not behave as expected")
    print("Simulated LLM responses, real explanation guard.")
    print(f"ACCEPTED: {accepted['text']}")
    print(f"REJECTED: {rejected['reason']}")
    print(f"STANDARD SUMMARY: {rejected['text']}")


def robustness(seeds, output):
    rows, savings, timings = [], [], []
    baseline_failures = verified = 0
    cases = [(seed, 20, 6) for seed in range(1, seeds + 1)] + [(1, 100, 12)]
    with TemporaryDirectory(prefix="nordic-robustness-") as folder:
        for seed, skus, zones in cases:
            ds, issues = load_dataset(generate(folder, seed, skus, zones))
            issues += validate(ds, "milp")
            if has_errors(issues):
                rows.append(f"| {seed} | {skus} x {zones} | n/a | n/a | Validation failed | n/a | n/a |")
                continue
            base, opt = baseline(ds), solve(ds)
            baseline_ok = base.status == "BASELINE" and not verify_plan(ds, base)
            plan_ok = opt.usable and not verify_plan(ds, opt)
            baseline_failures += not baseline_ok
            verified += plan_ok
            timings.append(opt.solve_seconds)
            saving_text = "n/a"
            if baseline_ok and plan_ok:
                saving = compare(ds, base, opt)["saving_pct"]
                savings.append(saving)
                saving_text = f"{saving:.2f}%"
            rows.append(f"| {seed} | {skus} x {zones} | {'Yes' if baseline_ok else 'No'} | {saving_text} | "
                        f"{opt.status} | {opt.solve_seconds:.3f} | {'Yes' if plan_ok else 'No'} |")

    summary = f"{min(savings):.2f}% / {median(savings):.2f}% / {max(savings):.2f}%" if savings else "n/a"
    longest = f"{max(timings):.3f} s" if timings else "n/a"
    report = "\n".join([
        "# Synthetic robustness results", "",
        "Run from `mvp` with `python -m nordic_flow robustness --out ../docs/round2/ROBUSTNESS.md`.", "",
        "MILP with a 30-second solver limit per case. Size is SKU count x zone count.", "",
        "| Seed | Size | Baseline valid | Saving | Solver status | Solve seconds | Independent check passed |",
        "| --- | --- | --- | --- | --- | --- | --- |",
        *rows, "",
        f"- Saving min / median / max across {len(savings)} comparable cases: {summary}",
        f"- Invalid baselines: {baseline_failures}. Verified plans: {verified}/{len(cases)}.",
        f"- Longest solve: {longest}.", "",
        "All data is synthetic. Savings reflect the generated inputs and cannot forecast Company A's results.", "",
    ])
    Path(output).write_text(report, encoding="utf-8")
    print(f"Wrote {output}")
