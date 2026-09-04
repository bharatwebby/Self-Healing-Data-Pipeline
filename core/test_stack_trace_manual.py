import json
from core.sandbox import run_in_sandbox

# Deliberately broken code, to confirm we get a REAL stack trace back
BROKEN_CODE = """
def extract(raw):
    return raw['this_key_does_not_exist']
"""

sample_raw = {"payload": {"items": []}}
result = run_in_sandbox(BROKEN_CODE, sample_raw)
print(json.dumps(result, indent=2))