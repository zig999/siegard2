"""trace.py — the one writer of siegard-trace.json: binds a specification node to the code it
produced, once, and reports drift once either side moves without the other."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

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


def test_a_bind_over_a_foreign_binding_prints_the_stale_receipt(repo):
    """A bind restamps only the nodes it was handed. Restamping a file another node's binding
    still claims leaves that binding stale — knowable right now, silent afterwards — so the bind
    says so at the one moment the maker of the change is still holding it."""
    bind(repo)
    (repo / "backend" / FILE).write_text("export function place(x) {}\n", encoding="utf-8")
    done = bind(repo, node="domain/troubleshooting/case-id")
    assert done.returncode == 0, done.stdout + done.stderr
    assert "leaves 1 binding(s) stale" in done.stdout
    assert f"{NODE}: backend/{FILE} — this act restamped the file under another node" \
        in done.stdout
    assert "a reconciliation over these paths is the route" in done.stdout


def test_a_bind_carrying_forward_a_changed_file_prints_the_stale_receipt(repo):
    """The extend default carries earlier files at their old digests. One that changed on its own
    is stale the moment this bind writes, and this bind is where both sides are in hand."""
    bind(repo)
    (repo / "backend" / FILE).write_text("export function place(x) {}\n", encoding="utf-8")
    (repo / "backend" / "src/orders/helpers.ts").write_text("export const h = 1;\n",
                                                            encoding="utf-8")
    done = bind(repo, file="src/orders/helpers.ts")
    assert done.returncode == 0, done.stdout + done.stderr
    assert "leaves 1 binding(s) stale" in done.stdout
    assert (f"{NODE}: backend/{FILE} — carried forward from an earlier bind, and the file has "
            f"since changed") in done.stdout


def test_a_clean_bind_prints_no_stale_receipt(repo):
    """The receipt reads only this act's neighborhood; a bind that leaves nothing stale says
    nothing, so the line means something the day it appears."""
    bind(repo)
    (repo / "backend" / "src/orders/helpers.ts").write_text("export const h = 1;\n",
                                                            encoding="utf-8")
    done = bind(repo, node="domain/troubleshooting/case-id", file="src/orders/helpers.ts")
    assert done.returncode == 0, done.stdout + done.stderr
    assert "stale" not in done.stdout


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


# ------------------------------------------------- every binding one record states, as one act


SECOND = "domain/troubleshooting/evidence"
OTHER_FILE = "src/orders/evidence.ts"


def record_at(repo: Path, entries: list[dict], name: str = "record.md") -> Path:
    """An implementation record shaped as one is: frontmatter, then the two headings. Only `nodes`
    matters here — bin/deliver.py validated the rest before a bind is ever run."""
    path = repo / "delivery" / "implementation" / "checkout"
    path.mkdir(parents=True, exist_ok=True)
    front = yaml.safe_dump({
        "title": "Record a placed order",
        "summary": "What this delivery wrote.",
        "task": "sha256:" + "0" * 64,
        "files": [{"path": FILE, "effect": "persists the order"}],
        "criteria": [{"criterion": "It works.", "met": True, "how": "it does"}],
        "nodes": entries,
    }, sort_keys=False, allow_unicode=True)
    written = path / name
    written.write_text(f"---\n{front}---\n## What it is\nProse.\n\n## Notes\nNone.\n",
                       encoding="utf-8")
    return written


def bind_record(repo: Path, record: Path, replace: bool = False) -> subprocess.CompletedProcess:
    args = ["--bind-record", repo / "backend", repo / "specs", record]
    if replace:
        args.append("--replace")
    return run(*args)


def test_a_record_binds_every_node_it_encodes_in_one_write(repo):
    (repo / "backend/src/orders/evidence.ts").write_text("export {}\n", encoding="utf-8")
    record = record_at(repo, [
        {"node": NODE, "encoded_at": [FILE], "how": "the case is what place() persists"},
        {"node": SECOND, "encoded_at": [FILE, OTHER_FILE], "how": "evidence is carried on it"},
    ])
    done = bind_record(repo, record)
    assert done.returncode == 0, done.stdout + done.stderr
    declared = json.loads((repo / "siegard-trace.json").read_text(encoding="utf-8"))
    assert [entry["node"] for entry in declared["bindings"]] == [NODE, SECOND]
    assert [f["path"] for f in declared["bindings"][1]["files"]] == \
        ["backend/src/orders/evidence.ts", "backend/src/orders/place.ts"]
    assert "2 binding(s) written" in done.stdout


def test_a_node_the_record_answers_only_by_how_is_not_bound(repo):
    """There is no file to name, and a bind with none is refused — so an entry carrying `how`
    alone is passed over rather than turned into an empty binding."""
    record = record_at(repo, [
        {"node": NODE, "encoded_at": [FILE], "how": "encoded here"},
        {"node": SECOND, "how": "the work honors it and encodes nothing of it"},
    ])
    done = bind_record(repo, record)
    assert done.returncode == 0, done.stdout + done.stderr
    declared = json.loads((repo / "siegard-trace.json").read_text(encoding="utf-8"))
    assert [entry["node"] for entry in declared["bindings"]] == [NODE]


def test_a_record_encoding_nothing_binds_nothing_and_is_not_a_defect(repo):
    done = bind_record(repo, record_at(repo, [{"node": NODE, "how": "constrained, encoded nowhere"}]))
    assert done.returncode == 0, done.stdout + done.stderr
    assert "nothing to bind" in done.stdout
    assert not (repo / "siegard-trace.json").exists(), \
        "a trace file created for nothing would say a delivery was linked"


def test_a_record_naming_a_node_the_specification_does_not_hold_binds_none_of_it(repo):
    record = record_at(repo, [
        {"node": NODE, "encoded_at": [FILE], "how": "encoded here"},
        {"node": "domain/troubleshooting/nowhere", "encoded_at": [FILE], "how": "encoded here"},
    ])
    done = bind_record(repo, record)
    assert done.returncode == 1, done.stdout
    assert "holds no node domain/troubleshooting/nowhere" in done.stdout
    assert not (repo / "siegard-trace.json").exists(), \
        "a record's bindings are one act; half of them written would read like all of them"


def test_a_record_naming_a_file_the_tree_does_not_hold_binds_none_of_it(repo):
    record = record_at(repo, [
        {"node": NODE, "encoded_at": [FILE], "how": "encoded here"},
        {"node": SECOND, "encoded_at": ["src/orders/gone.ts"], "how": "encoded here"},
    ])
    done = bind_record(repo, record)
    assert done.returncode == 1, done.stdout
    assert "gone.ts does not exist" in done.stdout
    assert not (repo / "siegard-trace.json").exists()


def test_the_refusal_names_the_anchor_a_missing_path_was_read_against(repo):
    """The two anchors are the likeliest reason a path is missing, and `backend/backend/src/...`
    is a stranger thing to be handed than the reason for it: findings and trace entries are spelled
    from the git toplevel, and everything read here is spelled from the target source root."""
    record = record_at(repo, [
        {"node": NODE, "encoded_at": [f"backend/{FILE}"], "how": "encoded here"},
    ])
    done = bind_record(repo, record)
    assert done.returncode == 1, done.stdout
    assert "target source root" in done.stdout
    assert str(repo / "backend") in done.stdout


def test_a_record_bind_extends_what_an_earlier_bind_held(repo):
    """The same merge the per-node form has, for the same reason: two tasks landing one node in two
    files is not one of them undoing the other's work."""
    bind(repo)
    (repo / "backend/src/orders/other.ts").write_text("export {}\n", encoding="utf-8")
    done = bind_record(repo, record_at(repo, [
        {"node": NODE, "encoded_at": ["src/orders/other.ts"], "how": "and here too"}]))
    assert done.returncode == 0, done.stdout + done.stderr
    declared = json.loads((repo / "siegard-trace.json").read_text(encoding="utf-8"))
    assert [f["path"] for f in declared["bindings"][0]["files"]] == \
        ["backend/src/orders/other.ts", "backend/src/orders/place.ts"]

    done = bind_record(repo, record_at(repo, [
        {"node": NODE, "encoded_at": ["src/orders/other.ts"], "how": "only here now"}]),
        replace=True)
    assert done.returncode == 0, done.stdout + done.stderr
    declared = json.loads((repo / "siegard-trace.json").read_text(encoding="utf-8"))
    assert [f["path"] for f in declared["bindings"][0]["files"]] == \
        ["backend/src/orders/other.ts"]


def test_a_record_that_cannot_be_read_is_a_refusal_to_run(repo):
    done = bind_record(repo, repo / "delivery/nowhere.md")
    assert done.returncode == trace.CANNOT_RUN
    assert "does not exist" in done.stderr

    stray = repo / "delivery" / "stray.md"
    stray.parent.mkdir(parents=True, exist_ok=True)
    stray.write_text("no fence here\n", encoding="utf-8")
    done = bind_record(repo, stray)
    assert done.returncode == trace.CANNOT_RUN
    assert "carries no frontmatter fence" in done.stderr


def test_a_record_bind_over_an_unsound_specification_writes_nothing(repo):
    (repo / "specs" / f"{NODE}.md").unlink()
    done = bind_record(repo, record_at(repo, [
        {"node": SECOND, "encoded_at": [FILE], "how": "encoded here"}]))
    assert done.returncode == 1, done.stdout
    assert "is not sound; nothing was bound." in done.stdout
    assert not (repo / "siegard-trace.json").exists()


def test_bind_and_bind_record_are_mutually_exclusive(repo):
    done = run("--bind", "--bind-record", repo / "backend")
    assert done.returncode == trace.CANNOT_RUN
    assert "mutually exclusive" in done.stderr


# -------------------------------------------------------------------------- --prune

ORPHAN = "constraints/asynchronous-events"


def orphan(repo: Path) -> None:
    """Bind a node, then take it out of the specification. A constraint is not held to
    reachability, so its removal leaves the base sound — the one way a node can vanish without
    everything around it going unsound, and therefore the only way to reach this class at all."""
    bind(repo, node=ORPHAN, file=FILE)
    (repo / f"specs/{ORPHAN}.md").unlink()


def test_prune_drops_a_binding_to_a_node_the_specification_no_longer_holds(repo):
    """The class that had no exit. `--bind` refuses a node the specification does not hold and
    this script is the trace's one writer, so before `--prune` the entry could not be repaired by
    anything and its finding repeated on every run forever."""
    orphan(repo)
    done = run("--prune", repo / "backend")
    assert done.returncode == 0, done.stdout + done.stderr
    assert f"dropped {ORPHAN}" in done.stdout
    assert "1 binding(s) pruned" in done.stdout
    declared = json.loads((repo / "siegard-trace.json").read_text(encoding="utf-8"))
    assert declared["bindings"] == []
    assert run("--check", repo / "backend").returncode == 0


def test_prune_leaves_a_file_that_moved_exactly_where_it_was(repo):
    """The refusal is the point. A file that drifted is drift with an owner and a remedy — the
    node is still in the base, still answered by code somewhere — and dropping the binding would
    destroy the one record of which node that code answers to while reporting the tree clean."""
    bind(repo)
    path = repo / "backend" / FILE
    path.write_text(path.read_text(encoding="utf-8") + "\n", encoding="utf-8")

    done = run("--prune", repo / "backend")
    assert done.returncode == 0, done.stdout + done.stderr
    assert "nothing to prune" in done.stdout
    declared = json.loads((repo / "siegard-trace.json").read_text(encoding="utf-8"))
    assert [entry["node"] for entry in declared["bindings"]] == [NODE]
    assert run("--check", repo / "backend").returncode == 1


def test_prune_clears_the_stale_class_and_keeps_the_drift_underneath_it(repo):
    """What the pile costs: the real finding is still there afterwards, and now it is readable."""
    bind(repo)
    orphan(repo)
    path = repo / "backend" / FILE
    path.write_text(path.read_text(encoding="utf-8") + "\n", encoding="utf-8")

    done = run("--prune", repo / "backend")
    assert done.returncode == 0, done.stdout + done.stderr
    declared = json.loads((repo / "siegard-trace.json").read_text(encoding="utf-8"))
    assert [entry["node"] for entry in declared["bindings"]] == [NODE]

    after = run("--check", repo / "backend")
    assert after.returncode == 1
    assert "the file changed without a rebind" in after.stdout
    assert "the binding is stale" not in after.stdout


def test_prune_over_a_specification_gone_unsound_deletes_nothing(repo):
    """Every node of a base nobody could read looks stale. Pruning on the strength of not having
    been able to see them would delete bindings for nodes that exist."""
    bind(repo)
    (repo / "specs" / f"{NODE}.md").unlink()
    done = run("--prune", repo / "backend")
    assert done.returncode == 1, done.stdout
    assert "nothing was pruned" in done.stdout
    declared = json.loads((repo / "siegard-trace.json").read_text(encoding="utf-8"))
    assert [entry["node"] for entry in declared["bindings"]] == [NODE]


def test_prune_with_nothing_stale_writes_nothing_and_says_so(repo):
    bind(repo)
    done = run("--prune", repo / "backend")
    assert done.returncode == 0, done.stdout + done.stderr
    assert "nothing to prune" in done.stdout


def test_prune_before_any_bind_is_not_a_defect(repo):
    done = run("--prune", repo / "backend")
    assert done.returncode == 0, done.stdout + done.stderr
    assert "nothing to prune" in done.stdout


def test_check_tallies_drift_by_class(repo):
    """The tally is what a reader acts on, and the orphaned count is what says how much of the
    report no rebind will ever shorten."""
    bind(repo)
    orphan(repo)
    path = repo / "backend" / FILE
    path.write_text(path.read_text(encoding="utf-8") + "\n", encoding="utf-8")

    done = run("--check", repo / "backend")
    assert done.returncode == 1
    assert "1 orphaned:" in done.stdout
    assert "0 moved:" in done.stdout
    assert "2 code:" in done.stdout, done.stdout
    assert "`--prune` is the only thing that clears them" in done.stdout


def test_prune_and_check_are_mutually_exclusive(repo):
    done = run("--prune", "--check", repo / "backend")
    assert done.returncode == trace.CANNOT_RUN
    assert "mutually exclusive" in done.stderr


# ------------------------------------------------- what a --replace stops claiming

def second_file(repo: Path) -> None:
    (repo / "backend" / OTHER_FILE).write_text("export {}\n", encoding="utf-8")


def test_replace_names_every_path_it_stops_claiming(repo):
    """The last silent loss in this writer. `--replace` substitutes the whole entry, so a path an
    earlier bind put there and this call leaves off is gone — and gone invisibly, because the
    trace it writes is internally consistent and `--check` comes back clean over it."""
    second_file(repo)
    bind(repo)
    done = bind(repo, file=OTHER_FILE, replace=True)
    assert done.returncode == 0, done.stdout + done.stderr
    assert "--replace released 1 path(s)" in done.stdout
    assert "backend/src/orders/place.ts" in done.stdout
    declared = json.loads((repo / "siegard-trace.json").read_text(encoding="utf-8"))
    assert [f["path"] for f in declared["bindings"][0]["files"]] == \
        ["backend/src/orders/evidence.ts"]


def test_the_receipt_is_a_receipt_and_not_a_refusal(repo):
    """Dropping a file is what `--replace` is for, and the ordinary use — omitting a path that no
    longer exists, which `traced_files_of` refuses to name — is the correct one. An alarm on the
    correct path is an alarm nobody reads by the third time."""
    second_file(repo)
    bind(repo)
    (repo / "backend" / FILE).unlink()
    done = bind(repo, file=OTHER_FILE, replace=True)
    assert done.returncode == 0, done.stdout + done.stderr
    assert "cannot" not in done.stdout
    assert "backend/src/orders/place.ts" in done.stdout, \
        "the receipt confirms exactly the vanished path the caller meant to let go"
    assert run("--check", repo / "backend").returncode == 0


def test_a_replace_that_drops_nothing_prints_no_receipt(repo):
    bind(repo)
    done = bind(repo, replace=True)
    assert done.returncode == 0, done.stdout + done.stderr
    assert "released" not in done.stdout


def test_the_union_default_never_prints_a_receipt(repo):
    """Nothing is dropped without --replace, so a receipt there would name a loss that did not
    happen — which is worse than the silence it replaces."""
    second_file(repo)
    bind(repo)
    done = bind(repo, file=OTHER_FILE)
    assert done.returncode == 0, done.stdout + done.stderr
    assert "released" not in done.stdout
    declared = json.loads((repo / "siegard-trace.json").read_text(encoding="utf-8"))
    assert len(declared["bindings"][0]["files"]) == 2


def test_a_record_replace_reports_what_a_sibling_record_had_bound(repo):
    """The trap as the consumer met it: two records answering one node, replaced from the second.
    The receipt names paths and never the record that put them there — which delivery bound a file
    is not something this file stores."""
    second_file(repo)
    first = record_at(repo, [{"node": NODE, "encoded_at": [FILE], "how": "here"}], name="a.md")
    later = record_at(repo, [{"node": NODE, "encoded_at": [OTHER_FILE], "how": "moved"}],
                      name="b.md")
    assert bind_record(repo, first).returncode == 0
    done = bind_record(repo, later, replace=True)
    assert done.returncode == 0, done.stdout + done.stderr
    assert "backend/src/orders/place.ts" in done.stdout
    assert "1 path(s) released across 1 node(s)" in done.stdout
