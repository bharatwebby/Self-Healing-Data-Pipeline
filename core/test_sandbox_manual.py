import requests, inspect, json
from agents.analyzer import analyze_incident
from agents.coder import generate_extractor_code
from core.static_scan import static_scan
from core.sandbox import run_in_sandbox
import extractors.extractor_v1 as extractor_module

raw = requests.get("http://127.0.0.1:9000/data").json()
previous_code = inspect.getsource(extractor_module)

try:
    extractor_module.extract(raw)
    print("No failure — make sure mock source is set to 'nested' mode.")
except Exception as e:
    analysis = analyze_incident(raw, previous_code, str(e))
    new_code = generate_extractor_code(
        analysis["field_mapping"], analysis["structural_change_summary"]
    )
    print("=== GENERATED CODE ===")
    print(new_code)

    print("\n=== STATIC SCAN ===")
    violations = static_scan(new_code)
    if violations:
        print("REJECTED before sandbox:", violations)
    else:
        print("No violations. Proceeding to sandbox...")
        print("\n=== SANDBOX EXECUTION ===")
        verdict = run_in_sandbox(new_code, raw)
        print(json.dumps(verdict, indent=2))