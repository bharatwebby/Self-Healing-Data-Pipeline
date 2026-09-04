import os

EXTRACTORS_DIR = "extractors"
VERSION_POINTER_FILE = os.path.join(EXTRACTORS_DIR, "active_version.txt")

def get_active_version() -> int:
    if not os.path.exists(VERSION_POINTER_FILE):
        return 1  # extractor_v1.py is our starting point
    with open(VERSION_POINTER_FILE) as f:
        return int(f.read().strip())

def get_next_version_number() -> int:
    existing = [f for f in os.listdir(EXTRACTORS_DIR)
                if f.startswith("extractor_v") and f.endswith(".py")]
    versions = [int(f.replace("extractor_v", "").replace(".py", "")) for f in existing]
    return max(versions, default=0) + 1

def deploy(new_code: str) -> int:
    """Writes the new extractor as a new version file, then atomically
    flips the active-version pointer. Old versions are never deleted —
    that's your rollback history for free."""
    version = get_next_version_number()
    path = os.path.join(EXTRACTORS_DIR, f"extractor_v{version}.py")
    with open(path, "w") as f:
        f.write(new_code)

    # os.replace is atomic on the same filesystem — no risk of a half-written pointer
    tmp_path = VERSION_POINTER_FILE + ".tmp"
    with open(tmp_path, "w") as f:
        f.write(str(version))
    os.replace(tmp_path, VERSION_POINTER_FILE)

    return version