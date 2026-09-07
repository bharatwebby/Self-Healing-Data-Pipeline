from core.memory import ast_diff


def test_identical_code_produces_empty_diff():
    code = "def extract(raw):\n    return raw\n"
    assert ast_diff(code, code) == ""


def test_structurally_changed_code_produces_a_nonempty_diff():
    old = "def extract(raw):\n    return raw['items']\n"
    new = "def extract(raw):\n    return raw['payload']['items']\n"
    assert ast_diff(old, new) != ""


def test_diff_is_capped_so_context_usage_stays_small():
    # core/memory.py truncates to 2000 chars specifically so retries don't
    # exhaust context by resending huge diffs — verify that cap holds.
    old = "def extract(raw):\n    " + "x = 1\n    " * 500 + "return raw\n"
    new = "def extract(raw):\n    " + "y = 2\n    " * 500 + "return raw\n"
    assert len(ast_diff(old, new)) <= 2000


def test_unparseable_code_degrades_gracefully_instead_of_raising():
    # This runs inside the orchestrator's retry loop; it must never crash
    # the loop even if a generated attempt was syntactically broken.
    diff = ast_diff("def extract(raw)", "def extract(raw):\n    return raw\n")
    assert isinstance(diff, str)
