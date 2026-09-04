import requests, inspect, json
from agents.analyzer import analyze_incident
from agents.coder import generate_extractor_code
import extractors.extractor_v1 as extractor_module

raw = requests.get("http://127.0.0.1:9000/data").json()
previous_code = inspect.getsource(extractor_module)

try:
    extractor_module.extract(raw)
    print("No failure — make sure mock source is set to 'nested' mode.")
except Exception as e:
    analysis = analyze_incident(raw, previous_code, str(e))
    print("=== ANALYSIS ===")
    print(json.dumps(analysis, indent=2))

    new_code = generate_extractor_code(
        analysis["field_mapping"],
        analysis["structural_change_summary"],
    )
    print("\n=== GENERATED CODE ===")
    print(new_code)

    # Manually test it right here (NOT the sandbox yet — just checking it's plausible)
    print("\n=== MANUAL TEST OF GENERATED CODE ===")
    namespace = {}
    exec(new_code, namespace)
    result = namespace["extract"](raw)
    print(json.dumps(result[:3], indent=2))