import pytest

from core.sandbox import run_in_sandbox

pytestmark = pytest.mark.docker


def test_valid_extractor_passes_and_output_matches_schema():
    code = (
        "def extract(raw):\n"
        "    return [\n"
        "        {'external_id': i['id'], 'display_name': i['name'],\n"
        "         'amount_cents': int(round(i['amount'] * 100))}\n"
        "        for i in raw\n"
        "    ]\n"
    )
    raw = [{"id": 1, "name": "user_1", "amount": 9.99}]

    verdict = run_in_sandbox(code, raw)

    assert verdict["passed"] is True
    assert verdict["records"] == [
        {"external_id": 1, "display_name": "user_1", "amount_cents": 999}
    ]


def test_broken_extractor_returns_a_real_python_stack_trace():
    code = "def extract(raw):\n    return raw['this_key_does_not_exist']\n"

    verdict = run_in_sandbox(code, {"id": 1})

    assert verdict["passed"] is False
    assert "KeyError" in verdict["stack_trace"]
    assert "extract" in verdict["stack_trace"]  # real traceback, not a generic message


def test_output_violating_target_schema_is_rejected():
    """The sandbox must reject output that doesn't match TargetRecord,
    not just code that raises — a "successful" extraction with the wrong
    shape is exactly the kind of drift that should never reach the DB."""
    code = "def extract(raw):\n    return [{'external_id': 'not-an-int', 'display_name': 'x'}]\n"

    verdict = run_in_sandbox(code, {})

    assert verdict["passed"] is False
    assert "schema_validation_failed" in verdict["reason"]


def test_network_access_is_blocked_at_the_sandbox_level_independent_of_the_scanner():
    """Defense-in-depth, tested in isolation: this deliberately skips
    static_scan() and calls the sandbox directly with code a scanner
    would reject, to prove the *second* layer (network_disabled=True)
    holds on its own even if the first layer were bypassed."""
    code = (
        "import socket\n"
        "def extract(raw):\n"
        "    socket.create_connection(('example.com', 80), timeout=2)\n"
        "    return []\n"
    )

    verdict = run_in_sandbox(code, {})

    assert verdict["passed"] is False
