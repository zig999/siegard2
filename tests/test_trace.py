"""trace.py — the one writer of siegard-trace.json: binds a specification node to the code it
produced, once, and reports drift once either side moves without the other."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

import trace

REPO = Path(__file__).resolve().parent.parent
TRACE_PY = Path(trace.__file__)
FIXTURE = REPO / "tests" / "fixtures" / "spec-model"

NODE = "domain/troubleshooting/case"
FILE = "src/orders/place.ts"


def run(*args) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(TRACE_PY), *map(str, args)],
                          capture_output=True, text=True)


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """A consumer repository: a git toplevel holding a target source root and a specification,
    the software living under `backend/` rather than at the toplevel — the case the path anchor
    exists for."""
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True, capture_output=True)
    spec_root = tmp_path / "specs"
    shutil.copytree(FIXTURE, spec_root)
    shutil.rmtree(spec_root / "projections", ignore_errors=True)
    target = tmp_path / "backend"
    (target / "src/orders").mkdir(parents=True)
    (target / "src/orders/place.ts").write_text("export function place() {}\n", encoding="utf-8")
    return tmp_path


def bind(repo: Path, node: str = NODE, file: str = FILE,
         spec_dir: str = "specs", replace: bool = False) -> subprocess.CompletedProcess:
    args = ["--bind", repo / "backend", repo / spec_dir, node, file]
    if replace:
        args.append("--replace")
    return run(*args)


# --------------------------------------------------------------------- no file yet


def test_no_file_declares_nothing_and_is_not_a_defect(repo):
    done = run(repo / "backend")
    assert done.returncode == 0, done.stdout + done.stderr
    assert "nothing has been bound yet" in done.stdout


# --------------------------------------------------------------------------- bind


def test_binding_creates_the_file_beside_where_siegard_json_would_sit(repo):
    done = bind(repo)
    assert done.returncode == 0, done.stdout + done.stderr
    declared = json.loads((repo / "siegard-trace.json").read_text(encoding="utf-8"))
    assert declared["specification"] == "specs"
    assert len(declared["bindings"]) == 1
    entry = declared["bindings"][0]
    assert entry["node"] == NODE
    assert entry["digest"].startswith("sha256:")
    assert entry["files"] == [{"path": "backend/src/orders/place.ts",
                               "digest": entry["files"][0]["digest"]}]


def test_a_rebind_extends_the_files_list_by_default(repo):
    """Two tasks landing the same node in two different files — the common case a plan produces
    when it shares a directory across tasks — must not have the second erase the first."""
    bind(repo)
    (repo / "backend/src/orders/other.ts").write_text("export {}\n", encoding="utf-8")
    done = bind(repo, file="src/orders/other.ts")
    assert done.returncode == 0, done.stdout + done.stderr
    declared = json.loads((repo / "siegard-trace.json").read_text(encoding="utf-8"))
    assert len(declared["bindings"]) == 1
    paths = sorted(f["path"] for f in declared["bindings"][0]["files"])
    assert paths == sorted(["backend/src/orders/place.ts", "backend/src/orders/other.ts"])


def test_a_rebind_of_the_same_file_updates_its_digest_in_place(repo):
    bind(repo)
    before = json.loads((repo / "siegard-trace.json").read_text(encoding="utf-8"))
    original_digest = before["bindings"][0]["files"][0]["digest"]
    path = repo / "backend" / FILE
    path.write_text(path.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    done = bind(repo)
    assert done.returncode == 0, done.stdout + done.stderr
    declared = json.loads((repo / "siegard-trace.json").read_text(encoding="utf-8"))
    files = declared["bindings"][0]["files"]
    assert len(files) == 1
    assert files[0]["path"] == "backend/src/orders/place.ts"
    assert files[0]["digest"] != original_digest


def test_replace_drops_a_file_the_call_does_not_name(repo):
    bind(repo)
    (repo / "backend/src/orders/other.ts").write_text("export {}\n", encoding="utf-8")
    done = bind(repo, file="src/orders/other.ts", replace=True)
    assert done.returncode == 0, done.stdout + done.stderr
    declared = json.loads((repo / "siegard-trace.json").read_text(encoding="utf-8"))
    paths = [f["path"] for f in declared["bindings"][0]["files"]]
    assert paths == ["backend/src/orders/other.ts"]


def test_replace_without_bind_is_refused(repo):
    done = run("--replace", repo / "backend")
    assert done.returncode == trace.CANNOT_RUN
    assert "--replace only applies to --bind" in done.stderr


def test_binding_a_second_node_adds_an_entry_sorted_by_identity(repo):
    bind(repo)
    second = "domain/troubleshooting/case-id"
    done = bind(repo, node=second)
    assert done.returncode == 0, done.stdout + done.stderr
    declared = json.loads((repo / "siegard-trace.json").read_text(encoding="utf-8"))
    assert [entry["node"] for entry in declared["bindings"]] == sorted([NODE, second])


def test_binding_an_unknown_node_is_refused(repo):
    done = bind(repo, node="domain/troubleshooting/ghost")
    assert done.returncode == 1
    assert "holds no node" in done.stdout
    assert not (repo / "siegard-trace.json").is_file()


def test_binding_a_missing_file_is_refused(repo):
    done = bind(repo, file="src/orders/missing.ts")
    assert done.returncode == 1
    assert "does not exist" in done.stdout
    assert not (repo / "siegard-trace.json").is_file()


def test_binding_over_an_unsound_specification_is_refused(repo):
    (repo / "specs/decision-log.md").unlink()
    done = bind(repo)
    assert done.returncode == 1
    assert "is not sound; nothing was bound" in done.stdout


def test_binding_against_a_second_specification_is_refused(repo):
    bind(repo)
    shutil.copytree(repo / "specs", repo / "other-specs")
    done = bind(repo, spec_dir="other-specs")
    assert done.returncode == 1
    assert "already traces against" in done.stdout
    assert "specs" in done.stdout and "other-specs" in done.stdout


# ------------------------------------------------------------------------- validate


def test_validate_reports_the_binding_count(repo):
    bind(repo)
    done = run(repo / "backend")
    assert done.returncode == 0, done.stdout + done.stderr
    assert "trace sound: 1 binding(s)" in done.stdout


def test_an_invalid_trace_file_is_refused(repo):
    (repo / "siegard-trace.json").write_text(json.dumps({"specification": "specs"}),
                                             encoding="utf-8")
    done = run(repo / "backend")
    assert done.returncode == 1
    assert "'bindings' is a required property" in done.stdout


def test_duplicate_node_entries_are_refused(repo):
    bind(repo)
    path = repo / "siegard-trace.json"
    declared = json.loads(path.read_text(encoding="utf-8"))
    declared["bindings"].append(declared["bindings"][0])
    path.write_text(json.dumps(declared), encoding="utf-8")
    done = run(repo / "backend")
    assert done.returncode == 1
    assert "is bound 2 times" in done.stdout


# ------------------------------------------------------------------------- --check


def test_check_finds_no_drift_right_after_a_bind(repo):
    bind(repo)
    done = run("--check", repo / "backend")
    assert done.returncode == 0, done.stdout + done.stderr
    assert "no drift: 1 binding(s)" in done.stdout


def test_check_reports_a_specification_node_that_moved(repo):
    bind(repo)
    path = repo / "specs" / f"{NODE}.md"
    path.write_text(path.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    done = run("--check", repo / "backend")
    assert done.returncode == 1
    assert "the specification moved since this bind" in done.stdout


def test_check_reports_a_file_that_moved_without_a_rebind(repo):
    bind(repo)
    path = repo / "backend" / FILE
    path.write_text(path.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    done = run("--check", repo / "backend")
    assert done.returncode == 1
    assert "the file changed without a rebind" in done.stdout


def test_check_reports_a_node_that_left_the_specification_without_breaking_it(repo):
    """A constraint is not held to reachability, so removing it leaves everything else sound —
    the one case where a node can vanish without the whole base going unsound around it."""
    bind(repo, node="constraints/asynchronous-events", file=FILE)
    (repo / "specs/constraints/asynchronous-events.md").unlink()
    done = run("--check", repo / "backend")
    assert done.returncode == 1
    assert "no longer in the specification; the binding is stale" in done.stdout


def test_check_over_a_specification_gone_unsound_names_that_instead(repo):
    bind(repo)
    (repo / "specs" / f"{NODE}.md").unlink()
    done = run("--check", repo / "backend")
    assert done.returncode == 1
    assert "is not sound; run spec.py against it directly" in done.stdout


def test_check_and_bind_are_mutually_exclusive(repo):
    done = run("--check", "--bind", repo / "backend")
    assert done.returncode == trace.CANNOT_RUN
    assert "mutually exclusive" in done.stderr
