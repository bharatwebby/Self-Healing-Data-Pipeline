import importlib
from datetime import datetime
from schema.target import TargetRecord
from core.deployer import get_active_version
from core.fetcher import fetch_raw
from core.database import init_db, write_records

init_db()

def load_active_extractor():
    version = get_active_version()
    module_name = f"extractors.extractor_v{version}"
    module = importlib.import_module(module_name)
    importlib.reload(module)
    return module, version

def run_once():
    module, version = load_active_extractor()
    raw = fetch_raw()

    try:
        raw_records = module.extract(raw)
        validated = [TargetRecord(**r) for r in raw_records]
        write_records(validated)
        print(f"[{datetime.now()}] SUCCESS (v{version}) - extracted {len(validated)} records, written to DB")
        for v in validated[:3]:
            print("   ", v)
        return True, None, raw
    except Exception as e:
        print(f"[{datetime.now()}] FAILURE (v{version}) - {e}")
        return False, str(e), raw

if __name__ == "__main__":
    run_once()