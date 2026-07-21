import hashlib

import pytest

import builder.runtime as runtime_module
from builder.runtime import RuntimeManager
from identity import IdentityContext, IdentityLoader


def test_loader_reads_why_content_unchanged(tmp_path):
    source = tmp_path / "WHY.md"
    expected = "# WHY\n\nWissen bewahren.\n"
    source.write_text(expected, encoding="utf-8")

    identity = IdentityLoader(source).load()

    assert identity.content == expected


def test_loader_exposes_resolved_source(tmp_path):
    source = tmp_path / "WHY.md"
    source.write_text("identity", encoding="utf-8")

    identity = IdentityLoader(source).load()

    assert identity.source == source.resolve()


def test_loader_version_is_deterministic_sha256_across_paths(tmp_path):
    first_source = tmp_path / "first" / "WHY.md"
    second_source = tmp_path / "second" / "WHY.md"
    content = "deterministic identity"
    first_source.parent.mkdir()
    second_source.parent.mkdir()
    first_source.write_text(content, encoding="utf-8")
    second_source.write_text(content, encoding="utf-8")

    first = IdentityLoader(first_source).load()
    second = IdentityLoader(second_source).load()

    assert first.version == second.version
    assert first.version == hashlib.sha256(content.encode("utf-8")).hexdigest()


def test_loader_version_changes_with_content(tmp_path):
    source = tmp_path / "WHY.md"
    source.write_text("first identity", encoding="utf-8")
    first_version = IdentityLoader(source).load().version

    source.write_text("second identity", encoding="utf-8")
    second_version = IdentityLoader(source).load().version

    assert first_version != second_version


def test_loader_rejects_missing_why(tmp_path):
    source = tmp_path / "WHY.md"

    with pytest.raises(FileNotFoundError, match="Identitätsquelle"):
        IdentityLoader(source).load()


def test_loader_reports_invalid_utf8_with_source(tmp_path):
    source = tmp_path / "WHY.md"
    source.write_bytes(b"\xff")

    with pytest.raises(UnicodeError, match=str(source.resolve())):
        IdentityLoader(source).load()


def test_default_loader_does_not_depend_on_working_directory(
    tmp_path,
    monkeypatch,
):
    monkeypatch.chdir(tmp_path)

    identity = IdentityLoader().load()

    assert identity.source == IdentityLoader.DEFAULT_SOURCE
    assert identity.content == IdentityLoader.DEFAULT_SOURCE.read_text(
        encoding="utf-8"
    )


def test_runtime_boot_exposes_identity_and_existing_data():
    runtime = RuntimeManager().boot()

    assert isinstance(runtime.identity_context, IdentityContext)
    assert runtime.constitution is not None
    assert runtime.knowledge
    assert runtime.project_state
    assert runtime.verified_facts == runtime.project_state["verified_facts"]


def test_runtime_boot_loads_identity_once(monkeypatch):
    load_calls = []
    identity = IdentityLoader().load()

    class CountingIdentityLoader:
        def load(self):
            load_calls.append(True)
            return identity

    monkeypatch.setattr(runtime_module, "IdentityLoader", CountingIdentityLoader)

    runtime = RuntimeManager().boot()

    assert runtime.identity_context is identity
    assert len(load_calls) == 1


def test_runtime_boot_fails_when_why_is_missing(tmp_path, monkeypatch):
    missing_source = tmp_path / "WHY.md"
    monkeypatch.setattr(IdentityLoader, "DEFAULT_SOURCE", missing_source)

    with pytest.raises(FileNotFoundError, match=str(missing_source)):
        RuntimeManager().boot()


def test_runtime_singleton_keeps_same_identity(monkeypatch):
    monkeypatch.setattr(runtime_module, "_runtime", None)

    first_runtime = runtime_module.get_runtime()
    second_runtime = runtime_module.get_runtime()

    assert first_runtime is second_runtime
    assert first_runtime.identity_context is second_runtime.identity_context
