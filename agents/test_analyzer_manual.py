import requests, json, inspect
from agents.analyzer import analyze_incident
import extractors.extractor_v1 as extractor_module

raw = requests.get("http://127.0.0.1:9000/data").json()
previous_code = inspect.getsource(extractor_module)

try:
    extractor_module.extract(raw)
    print("No failure detected — make sure the mock source is set to 'nested' mode first.")
except Exception as e:
    result = analyze_incident(raw, previous_code, str(e))
    print(json.dumps(result, indent=2))