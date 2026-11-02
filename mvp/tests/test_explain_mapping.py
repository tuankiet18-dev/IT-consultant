from pathlib import Path
import pytest
from nordic_flow.baseline import baseline
from nordic_flow.explain import build_facts, check_numbers, explain, template_text
from nordic_flow.io import load_dataset
from nordic_flow.llm import GroqClient, LLMError
from nordic_flow.mapping import score, suggest
from nordic_flow.optimiser import solve
from nordic_flow.report import compare

GOLDEN = Path(__file__).parent.parent / "data" / "golden"


class FakeClient:
    enabled = True
    model = "fake"
    def __init__(self, reply=None, error=None): self.reply, self.error = reply, error
    def chat(self, messages, **kw):
        if self.error: raise LLMError(self.error)
        return self.reply


@pytest.fixture(scope="module")
def ctx():
    ds = load_dataset(GOLDEN)[0]
    b, o = baseline(ds), solve(ds, "milp")
    return ds, build_facts(ds, b, o, compare(ds, b, o))


def test_facts_come_from_solver_numbers(ctx):
    _, f = ctx
    assert (f["baseline_total"], f["optimised_total"], f["saving"], f["saving_percent"]) == (700, 500, 200, 28.6)
    assert f["decisions_changed"] == 1 and f["largest_changes"][0]["pallets"] == 40


def test_template_passes_its_own_number_check(ctx):
    _, f = ctx
    t = template_text(f)
    assert check_numbers(t, f) == []
    assert "200" in t and "28.6%" in t


def test_check_numbers_rejects_invented_values(ctx):
    _, f = ctx
    assert check_numbers("The plan saves 28.6% or 200 units.", f) == []
    assert check_numbers("The plan saves 35% overall.", f) == ["35"]
    assert check_numbers("Costs fall from 700 to 480.", f) == ["480"]


def test_identifiers_are_not_treated_as_numbers(ctx):
    _, f = ctx
    assert check_numbers("SKU-01 and Z3 moved.", f) == []


def test_llm_text_is_used_when_numbers_match(ctx):
    _, f = ctx
    r = explain(f, FakeClient("Cost falls from 700 to 500, saving 200 (28.6%). The planner should review before approving."))
    assert r["source"] == "groq:fake" and r["unsupported_numbers"] == []


def test_llm_text_with_invented_number_falls_back_to_template(ctx):
    _, f = ctx
    r = explain(f, FakeClient("Cost falls by 41% thanks to routing."))
    assert r["source"] == "deterministic" and r["unsupported_numbers"] == ["41"]


def test_llm_error_and_missing_key_fall_back(ctx):
    _, f = ctx
    assert explain(f, FakeClient(error="boom"))["source"] == "deterministic"
    assert explain(f, GroqClient(api_key=""))["reason"] == "no LLM key configured"


def test_sku_mapping_ranks_the_right_item_first():
    ds = load_dataset(Path(__file__).parent.parent / "data" / "demo")[0]
    res = suggest([{"code": "CEM-25", "name": "cement standard"}, {"code": "X", "name": "Roofing sheet large"}], ds)
    assert res[0]["candidates"][0]["name"] == "Cement standard"
    assert res[1]["candidates"][0]["name"] == "Roofing sheet large"
    assert score("Cement standard", "Cement standard") > score("Cement standard", "Paint pail large")


def test_llm_mapping_pick_is_ignored_unless_it_is_a_candidate():
    ds = load_dataset(Path(__file__).parent.parent / "data" / "demo")[0]
    ok = suggest([{"code": "", "name": "cement standard"}], ds, client=FakeClient('{"sku_id": "SKU-01", "reason": "same"}'))
    bad = suggest([{"code": "", "name": "cement standard"}], ds, client=FakeClient('{"sku_id": "SKU-99", "reason": "?"}'))
    assert ok[0]["llm_pick"]["sku_id"] == "SKU-01" and bad[0]["llm_pick"] is None
