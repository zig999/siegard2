"""`assemble_dist.py` — the distribution, and the check that holds the committed one to the source.

Assembly is run into a temporary directory throughout, so the suite never rewrites `dist/`. The one
test that looks at the committed distribution only compares.
"""
from __future__ import annotations

import json
import subprocess
import sys

import pytest

import assemble_dist


@pytest.fixture
def assemble(repo, tmp_path):
    into = tmp_path / "claude"

    def run(*args) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(repo / "scripts/assemble_dist.py"), f"--into={into}", *args],
            capture_output=True, text=True)
    run.into = into
    return run


@pytest.fixture
def assembled(assemble):
    done = assemble()
    assert done.returncode == 0, done.stdout + done.stderr
    return assemble


def tree(directory) -> dict:
    return {p.relative_to(directory).as_posix(): p.read_bytes()
            for p in directory.rglob("*") if p.is_file()}


# ---- deterministic, or --check means nothing --------------------------------------------------

def test_assembling_twice_over_one_source_is_byte_identical(assembled):
    first = tree(assembled.into)
    assembled()
    assert tree(assembled.into) == first


def test_the_manifest_holds_no_key_that_could_vary_between_runs(assembled):
    manifest = json.loads((assembled.into / "siegard-manifest.json").read_text())
    assert sorted(manifest) == ["capabilities", "contract_version", "generator_version",
                                "installed", "overrides", "schemas", "source_revision"]


def test_the_revision_is_a_digest_of_the_source_and_not_a_commit(assembled):
    """A commit SHA would make the committed distribution unverifiable: assemble at N-1, record
    N-1, commit, and the next check reads HEAD as N and reports a difference nobody introduced."""
    manifest = json.loads((assembled.into / "siegard-manifest.json").read_text())
    assert manifest["source_revision"].startswith("sha256:")


# ---- what ships is decided by location ------------------------------------------------------------

@pytest.mark.parametrize("name", ["CLAUDE.md", "capabilities.declaration.json"])
def test_a_file_at_the_root_of_the_source_tree_does_not_ship(assembled, name):
    """Neither sits in an installed directory. The first governs a repository that installs the
    framework; the second is authored input to the assembler."""
    assert not (assembled.into / name).exists()


def test_the_plugin_manifest_ships(assembled):
    assert (assembled.into / ".claude-plugin/plugin.json").is_file()


def test_the_manifest_lists_every_installed_file_but_itself(assembled):
    manifest = json.loads((assembled.into / "siegard-manifest.json").read_text())
    listed = {entry["path"] for entry in manifest["installed"]}
    assert listed == set(tree(assembled.into)) - {"siegard-manifest.json"}


# ---- a capability is what has an entry point ---------------------------------------------------------

def test_every_capability_reaches_a_consumer_with_a_declaration(assembled):
    """One installed and governed by nothing is what the assembler refuses over."""
    manifest = json.loads((assembled.into / "siegard-manifest.json").read_text())
    assert [c["name"] for c in manifest["capabilities"] if "declaration" not in c] == []


def test_a_library_is_installed_and_is_not_a_capability(assembled):
    """It executes nothing and is delegated to by nothing: it ships beside the capability that
    imports it."""
    manifest = json.loads((assembled.into / "siegard-manifest.json").read_text())
    named = {c["name"] for c in manifest["capabilities"]}
    installed = {entry["path"] for entry in manifest["installed"]}
    for module in ("node_io", "change_set", "graph_edit", "graph_query", "field_ownership"):
        assert f"bin/{module}.py" in installed
        assert module.replace("_", "-") not in named


# ---- a file whose source is gone does not survive ---------------------------------------------------------

def test_check_notices_an_edited_file_and_writes_nothing_back(assembled):
    target = assembled.into / "bin" / "check_knowledge.py"
    target.write_text("tampered", encoding="utf-8")
    done = assembled("--check")
    assert done.returncode == 1
    assert "bin/check_knowledge.py" in done.stdout
    assert target.read_text(encoding="utf-8") == "tampered"


def test_assembling_repairs_it(assembled):
    target = assembled.into / "bin" / "check_knowledge.py"
    target.write_text("tampered", encoding="utf-8")
    assembled()
    assert target.read_text(encoding="utf-8") != "tampered"


def test_a_stowaway_is_reported_then_removed(assembled):
    stowaway = assembled.into / "bin" / "stowaway.py"
    stowaway.write_text("x", encoding="utf-8")
    assert assembled("--check").returncode == 1
    assembled()
    assert not stowaway.exists()


def test_a_directory_left_empty_goes_with_it(assembled):
    leftover = assembled.into / "leftover"
    leftover.mkdir()
    (leftover / "old.md").write_text("x", encoding="utf-8")
    assembled()
    assert not leftover.exists()
    assert assembled("--check").returncode == 0


# ---- it refuses rather than shipping something broken -------------------------------------------------------

def test_a_shipped_module_importing_a_file_that_does_not_ship_is_refused(assembled, bin_dir):
    """`bin/` is the import root once installed, so an import of the generator's own tree resolves
    here and raises ImportError in the consumer's hands."""
    stray = bin_dir / "_probe_for_tests.py"
    stray.write_text("from compose_domain import compose\n", encoding="utf-8")
    try:
        done = assembled("--check")
        assert done.returncode == assemble_dist.CANNOT_RUN
        assert "compose_domain" in done.stderr
        assert "scripts/compose_domain.py" in done.stderr
    finally:
        stray.unlink()
    assert assembled("--check").returncode == 0


def test_a_positional_argument_cannot_run(assembled):
    assert assembled("dist").returncode == assemble_dist.CANNOT_RUN


# ---- the committed distribution -------------------------------------------------------------------------

def test_the_committed_distribution_is_what_the_source_assembles_to(repo):
    done = subprocess.run([sys.executable, str(repo / "scripts/assemble_dist.py"), "--check"],
                          capture_output=True, text=True)
    assert done.returncode == 0, done.stdout + done.stderr
