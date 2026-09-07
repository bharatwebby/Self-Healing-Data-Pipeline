from core.static_scan import static_scan


def test_clean_realistic_extractor_has_no_violations():
    code = """
def extract(raw):
    items = raw.get('payload', {}).get('items', [])
    return [
        {
            'external_id': int(i['id']),
            'display_name': str(i['name']),
            'amount_cents': int(round(i['amount'] * 100)),
        }
        for i in items
    ]
"""
    assert static_scan(code) == []


def test_banned_import_is_caught():
    code = "import os\ndef extract(raw):\n    return os.listdir('.')\n"
    violations = static_scan(code)
    assert any("os" in v for v in violations)


def test_banned_from_import_is_caught():
    code = "from subprocess import run\ndef extract(raw):\n    return []\n"
    assert any("subprocess" in v for v in static_scan(code))


def test_eval_call_is_caught():
    code = "def extract(raw):\n    return eval('1+1')\n"
    assert any("eval" in v for v in static_scan(code))


def test_open_call_is_caught():
    code = "def extract(raw):\n    return open('/etc/passwd').read()\n"
    assert any("open" in v for v in static_scan(code))


def test_direct_dunder_import_call_is_caught():
    code = "def extract(raw):\n    return __import__('os').listdir('.')\n"
    assert any("__import__" in v for v in static_scan(code))


def test_getattr_bypass_of_dunder_import_is_caught():
    """The exact bypass the scanner was hardened against: smuggling a
    dangerous capability through getattr() instead of spelling it out
    literally, so a scanner that only matches on `eval`/`os` etc. as
    written text misses it entirely."""
    code = (
        "def extract(raw):\n"
        "    smuggled = getattr(__builtins__, '__import__')('os')\n"
        "    return smuggled.listdir('.')\n"
    )
    violations = static_scan(code)
    assert any("getattr" in v for v in violations)


def test_dunder_attribute_sandbox_escape_gadget_is_caught():
    """Classic Python sandbox-escape gadget: crawl the live object graph
    via dunder attributes to reach a class with eval/exec-equivalent
    power, without ever importing anything or calling eval/exec/getattr."""
    code = (
        "def extract(raw):\n"
        "    leak = ().__class__.__bases__[0].__subclasses__()\n"
        "    return leak\n"
    )
    violations = static_scan(code)
    assert any(
        "__class__" in v or "__bases__" in v or "__subclasses__" in v
        for v in violations
    )


def test_bare_dunder_name_reference_is_caught():
    code = "def extract(raw):\n    return __builtins__\n"
    violations = static_scan(code)
    assert any("__builtins__" in v for v in violations)


def test_syntax_error_is_reported_not_raised():
    violations = static_scan("def extract(raw)\n    return raw\n")  # missing colon
    assert violations and violations[0].startswith("syntax_error")


def test_legitimate_dict_and_str_methods_are_not_false_positives():
    """Guard against the hardening being too aggressive: ordinary methods
    like .get() must not be mistaken for dunder access."""
    code = (
        "def extract(raw):\n"
        "    name = raw.get('name', '').strip().upper()\n"
        "    return [{'external_id': 1, 'display_name': name, 'amount_cents': 0}]\n"
    )
    assert static_scan(code) == []
