from nordic_flow.cli import main


def test_demo_guard_accepts_supported_numbers_and_falls_back(capsys):
    assert main(["demo-guard"]) == 0
    output = capsys.readouterr().out
    assert "ACCEPTED:" in output
    assert "REJECTED: LLM text rejected: numbers not in facts" in output
    assert "STANDARD SUMMARY:" in output
