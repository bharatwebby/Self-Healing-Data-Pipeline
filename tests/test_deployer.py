import core.deployer as deployer


def _isolate(monkeypatch, tmp_path):
    """Point the deployer at a scratch directory instead of the real
    extractors/ folder, so tests never touch production version files."""
    monkeypatch.setattr(deployer, "EXTRACTORS_DIR", str(tmp_path))
    monkeypatch.setattr(deployer, "VERSION_POINTER_FILE", str(tmp_path / "active_version.txt"))


def test_get_active_version_defaults_to_1_with_no_pointer_file(tmp_path, monkeypatch):
    _isolate(monkeypatch, tmp_path)
    assert deployer.get_active_version() == 1


def test_get_next_version_number_increments_past_existing_versions(tmp_path, monkeypatch):
    _isolate(monkeypatch, tmp_path)
    (tmp_path / "extractor_v1.py").write_text("def extract(raw):\n    return raw\n")
    (tmp_path / "extractor_v2.py").write_text("def extract(raw):\n    return raw\n")

    assert deployer.get_next_version_number() == 3


def test_deploy_writes_versioned_file_and_flips_active_pointer(tmp_path, monkeypatch):
    _isolate(monkeypatch, tmp_path)
    (tmp_path / "extractor_v1.py").write_text("def extract(raw):\n    return raw\n")
    new_code = "def extract(raw):\n    return raw['items']\n"

    version = deployer.deploy(new_code)

    assert version == 2
    assert (tmp_path / "extractor_v2.py").read_text() == new_code
    assert deployer.get_active_version() == 2


def test_deploy_never_deletes_prior_versions(tmp_path, monkeypatch):
    # Old versions are the rollback history — deploy() must be additive only.
    _isolate(monkeypatch, tmp_path)
    (tmp_path / "extractor_v1.py").write_text("def extract(raw):\n    return raw\n")

    deployer.deploy("def extract(raw):\n    return raw['items']\n")

    assert (tmp_path / "extractor_v1.py").exists()


def test_deploy_leaves_no_leftover_tmp_file_from_the_atomic_swap(tmp_path, monkeypatch):
    _isolate(monkeypatch, tmp_path)
    (tmp_path / "extractor_v1.py").write_text("def extract(raw):\n    return raw\n")

    deployer.deploy("def extract(raw):\n    return raw\n")

    assert not (tmp_path / "active_version.txt.tmp").exists()
