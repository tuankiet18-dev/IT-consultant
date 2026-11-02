import pytest
from nordic_flow.baseline import baseline
from nordic_flow.io import load_dataset
from nordic_flow.optimiser import solve
from nordic_flow.report import compare
from nordic_flow.synth import generate
from nordic_flow.validation import has_errors, validate
from nordic_flow.verify import verify_plan


@pytest.fixture(scope="module")
def ds(tmp_path_factory):
    d = generate(tmp_path_factory.mktemp("demo"), seed=7)
    data, issues = load_dataset(d)
    assert not issues
    return data


def test_demo_data_is_valid_and_has_expected_size(ds):
    assert not has_errors(validate(ds))
    assert (len(ds.suppliers), len(ds.warehouses), len(ds.zones), len(ds.skus)) == (2, 3, 6, 20)


def test_optimised_plan_is_valid_and_cheaper_than_baseline(ds):
    b, o = baseline(ds), solve(ds, "milp", 20)
    assert b.status == "BASELINE" and o.status in ("OPTIMAL", "FEASIBLE")
    assert not verify_plan(ds, b) and not verify_plan(ds, o)
    c = compare(ds, b, o)
    assert 1.0 < c["saving_pct"] < 10.0      # a few percent, as expected from the Round 1 hypothesis
    assert c["optimised"]["total"] <= c["baseline"]["total"]


def test_lp_is_a_lower_bound_for_milp(ds):
    lp, milp = solve(ds, "lp"), solve(ds, "milp", 20)
    assert lp.objective <= milp.objective + 1e-6


def test_generator_is_deterministic(tmp_path):
    a = generate(tmp_path / "a", 3); b = generate(tmp_path / "b", 3)
    assert (a / "demand.csv").read_text() == (b / "demand.csv").read_text()
