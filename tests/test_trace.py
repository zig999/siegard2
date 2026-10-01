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
def consumer(tmp_path: Path) -> Path:
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


def bind(consumer: Path, node: str = NODE, file: str = FILE,
         spec_dir: str = "specs", replace: bool = False) -> subprocess.CompletedProcess:
    args = ["--bind", consumer / "backend", consumer / spec_dir, node, file]
    if replace:
        args.append("--replace")
    return run(*args)


# --------------------------------------------------------------------- no file yet


def test_no_file_declares_nothing_and_is_not_a_defect(consumer):
    done = run(consumer / "backend")
    assert done.returncode == 0, done.stdout + done.stderr
    assert "nothing has been bound yet" in done.stdout


# --------------------------------------------------------------------------- bind


def test_binding_creates_the_file_beside_where_siegard_json_would_sit(consumer):
    done = bind(consumer)
    assert done.returncode == 0, done.stdout + done.stderr
    declared = json.loads((consumer / "siegard-trace.json").read_text(encoding="utf-8"))
    assert declared["specification"] == "specs"
    assert len(declared["bindings"]) == 1
    entry = declared["bindings"][0]
    assert entry["node"] == NODE
    assert entry["digest"].startswith("sha256:")
    assert entry["files"] == [{"path": "backend/src/orders/place.ts",
                               "digest": entry["files"][0]["digest"],
                               "node_digest": entry["digest"]}]


def test_a_rebind_extends_the_files_list_by_default(consumer):
    """Two tasks landing the same node in two different files — the common case a plan produces
    when it shares a directory across tasks — must not have the second erase the first."""
    bind(consumer)
    (consumer / "backend/src/orders/other.ts").write_text("export {}\n", encoding="utf-8")
    done = bind(consumer, file="src/orders/other.ts")
    assert done.returncode == 0, done.stdout + done.stderr
    declared = json.loads((consumer / "siegard-trace.json").read_text(encoding="utf-8"))
    assert len(declared["bindings"]) == 1
    paths = sorted(f["path"] for f in declared["bindings"][0]["files"])
    assert paths == sorted(["backend/src/orders/place.ts", "backend/src/orders/other.ts"])


def test_a_rebind_of_the_same_file_updates_its_digest_in_place(consumer):
    bind(consumer)
    before = json.loads((consumer / "siegard-trace.json").read_text(encoding="utf-8"))
    original_digest = before["bindings"][0]["files"][0]["digest"]
    path = consumer / "backend" / FILE
    path.write_text(path.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    done = bind(consumer)
    assert done.returncode == 0, done.stdout + done.stderr
    declared = json.loads((consumer / "siegard-trace.json").read_text(encoding="utf-8"))
    files = declared["bindings"][0]["files"]
    assert len(files) == 1
    assert files[0]["path"] == "backend/src/orders/place.ts"
    assert files[0]["digest"] != original_digest


def test_replace_drops_a_file_the_call_does_not_name(consumer):
    bind(consumer)
    (consumer / "backend/src/orders/other.ts").write_text("export {}\n", encoding="utf-8")
    done = bind(consumer, file="src/orders/other.ts", replace=True)
    assert done.returncode == 0, done.stdout + done.stderr
    declared = json.loads((consumer / "siegard-trace.json").read_text(encoding="utf-8"))
    paths = [f["path"] for f in declared["bindings"][0]["files"]]
    assert paths == ["backend/src/orders/other.ts"]


def test_replace_without_bind_is_refused(consumer):
    done = run("--replace", consumer / "backend")
    assert done.returncode == trace.CANNOT_RUN
    assert "--replace only applies to --bind" in done.stderr


def test_binding_a_second_node_adds_an_entry_sorted_by_identity(consumer):
    bind(consumer)
    second = "domain/troubleshooting/case-id"
    done = bind(consumer, node=second)
    assert done.returncode == 0, done.stdout + done.stderr
    declared = json.loads((consumer / "siegard-trace.json").read_text(encoding="utf-8"))
    assert [entry["node"] for entry in declared["bindings"]] == sorted([NODE, second])


def test_a_bind_over_a_foreign_binding_prints_the_stale_receipt(consumer):
    """A bind restamps only the nodes it was handed. Restamping a file another node's binding
    still claims leaves that binding stale — knowable right now, silent afterwards — so the bind
    says so at the one moment the maker of the change is still holding it."""
    bind(consumer)
    (consumer / "backend" / FILE).write_text("export function place(x) {}\n", encoding="utf-8")
    done = bind(consumer, node="domain/troubleshooting/case-id")
    assert done.returncode == 0, done.stdout + done.stderr
    assert "leaves 1 binding(s) stale" in done.stdout
    assert f"{NODE}: backend/{FILE} — this act restamped the file under another node" \
        in done.stdout
    assert "a reconciliation over these paths is the route" in done.stdout


def test_a_bind_carrying_forward_a_changed_file_prints_the_stale_receipt(consumer):
    """The extend default carries earlier files at their old digests. One that changed on its own
    is stale the moment this bind writes, and this bind is where both sides are in hand."""
    bind(consumer)
    (consumer / "backend" / FILE).write_text("export function place(x) {}\n", encoding="utf-8")
    (consumer / "backend" / "src/orders/helpers.ts").write_text("export const h = 1;\n",
                                                            encoding="utf-8")
    done = bind(consumer, file="src/orders/helpers.ts")
    assert done.returncode == 0, done.stdout + done.stderr
    assert "leaves 1 binding(s) stale" in done.stdout
    assert (f"{NODE}: backend/{FILE} — carried forward from an earlier bind, and the file has "
            f"since changed") in done.stdout


def test_a_raw_bind_prints_the_no_record_receipt(consumer):
    """`--bind` is the one bind no record backs — the skills all go through `--bind-record` —
    and the entry it writes reads afterwards exactly like one a record justified, so the
    receipt is the only trace of the difference."""
    done = bind(consumer)
    assert done.returncode == 0, done.stdout + done.stderr
    assert "rests on no record" in done.stdout


def test_a_record_bind_prints_no_such_receipt(consumer):
    """The receipt says a judgment lives nowhere; a bind read out of a record is exactly the
    case where it does, and printing the line there would teach every reader to skip it."""
    record = record_at(consumer, [
        {"node": NODE, "encoded_at": [FILE], "how": "the case is what place() persists"},
    ])
    done = bind_record(consumer, record)
    assert done.returncode == 0, done.stdout + done.stderr
    assert "rests on no record" not in done.stdout


def test_a_clean_bind_prints_no_stale_receipt(consumer):
    """The receipt reads only this act's neighborhood; a bind that leaves nothing stale says
    nothing, so the line means something the day it appears."""
    bind(consumer)
    (consumer / "backend" / "src/orders/helpers.ts").write_text("export const h = 1;\n",
                                                            encoding="utf-8")
    done = bind(consumer, node="domain/troubleshooting/case-id", file="src/orders/helpers.ts")
    assert done.returncode == 0, done.stdout + done.stderr
    assert "stale" not in done.stdout


def test_binding_a_context_descriptor_is_refused(consumer):
    done = bind(consumer, node="domain/troubleshooting/_context")
    assert done.returncode == 1
    assert "is a context descriptor" in done.stdout
    assert not (consumer / "siegard-trace.json").is_file()


def test_binding_an_unknown_node_is_refused(consumer):
    done = bind(consumer, node="domain/troubleshooting/ghost")
    assert done.returncode == 1
    assert "holds no node" in done.stdout
    assert not (consumer / "siegard-trace.json").is_file()


def test_binding_a_missing_file_is_refused(consumer):
    done = bind(consumer, file="src/orders/missing.ts")
    assert done.returncode == 1
    assert "does not exist" in done.stdout
    assert not (consumer / "siegard-trace.json").is_file()


def test_binding_over_an_unsound_specification_is_refused(consumer):
    (consumer / "specs/domain/troubleshooting/_context.md").unlink()
    done = bind(consumer)
    assert done.returncode == 1
    assert "is not sound; nothing was bound" in done.stdout


def test_binding_against_a_second_specification_is_refused(consumer):
    bind(consumer)
    shutil.copytree(consumer / "specs", consumer / "other-specs")
    done = bind(consumer, spec_dir="other-specs")
    assert done.returncode == 1
    assert "already traces against" in done.stdout
    assert "specs" in done.stdout and "other-specs" in done.stdout


# ------------------------------------------------------------------------- validate


def test_validate_reports_the_binding_count(consumer):
    bind(consumer)
    done = run(consumer / "backend")
    assert done.returncode == 0, done.stdout + done.stderr
    assert "trace sound: 1 binding(s)" in done.stdout


def test_an_invalid_trace_file_is_refused(consumer):
    (consumer / "siegard-trace.json").write_text(json.dumps({"specification": "specs"}),
                                             encoding="utf-8")
    done = run(consumer / "backend")
    assert done.returncode == 1
    assert "'bindings' is a required property" in done.stdout


def test_duplicate_node_entries_are_refused(consumer):
    bind(consumer)
    path = consumer / "siegard-trace.json"
    declared = json.loads(path.read_text(encoding="utf-8"))
    declared["bindings"].append(declared["bindings"][0])
    path.write_text(json.dumps(declared), encoding="utf-8")
    done = run(consumer / "backend")
    assert done.returncode == 1
    assert "is bound 2 times" in done.stdout


# ------------------------------------------------------------------------- --check


def test_check_finds_no_drift_right_after_a_bind(consumer):
    bind(consumer)
    done = run("--check", consumer / "backend")
    assert done.returncode == 0, done.stdout + done.stderr
    assert "no drift: 1 binding(s)" in done.stdout


def test_check_names_the_trace_file_it_read(consumer):
    """A drift report is a claim about a tree and the trace is its source, so the report names it —
    the way the absent case already does. It also makes the one redundant invocation visible: a
    trace is one file per git toplevel, so a second target under that toplevel re-reads this exact
    file and prints this exact report, and two runs naming one path is what says so."""
    bind(consumer)
    done = run("--check", consumer / "backend")
    assert done.returncode == 0, done.stdout + done.stderr
    assert f"trace: {consumer / 'siegard-trace.json'}" in done.stdout
    assert "one file per git toplevel" in done.stdout

    # The second target of the same toplevel prints the identical report, path included.
    twin = run("--check", consumer / "frontend") if (consumer / "frontend").is_dir() else done
    assert f"trace: {consumer / 'siegard-trace.json'}" in twin.stdout


def test_check_reports_a_specification_node_that_moved(consumer):
    bind(consumer)
    path = consumer / "specs" / f"{NODE}.md"
    path.write_text(path.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    done = run("--check", consumer / "backend")
    assert done.returncode == 1
    assert "the specification moved since this bind" in done.stdout


CONSTRAINT = "constraints/asynchronous-events"


def registry_deciding(consumer: Path, *constraints: str) -> None:
    """A project file naming a registry whose `lint` step decides the named constraints."""
    (consumer / "standard.yaml").write_text(yaml.safe_dump({
        "contract_version": "siegard-standard/1", "standard": "backend", "summary": "a test's",
        "rules": [], "commands": [{"step": "lint", "command": "npm run lint",
                                   "timeout_seconds": 60, "decides": list(constraints)}]}),
        encoding="utf-8")
    (consumer / "siegard.json").write_text(json.dumps(
        {"specification_root": "specs", "targets": {"backend": "backend"},
         "standard": {"backend": "standard.yaml"}}) + "\n", encoding="utf-8")


def test_check_names_the_code_findings_that_sit_on_a_constraint_a_step_decides(consumer):
    """The drift is real and stays in the `code` class — the digest is stale. What the receipt
    adds is which of those lines a reading would only re-decide: the registry's step already
    decides the constraint over the tree, so a reader weighing the list knows which findings a
    run of that step answers."""
    bind(consumer)
    bind(consumer, node=CONSTRAINT)
    registry_deciding(consumer, CONSTRAINT)
    (consumer / "backend/src/orders/place.ts").write_text("export function place() { return 1 }\n",
                                                          encoding="utf-8")
    done = run("--check", consumer / "backend")
    assert done.returncode == 1, done.stdout + done.stderr
    assert "2 code over 1 file(s)" in done.stdout
    assert "1 of the `code` finding(s) sit on a constraint a registry step decides" in done.stdout
    assert f"{CONSTRAINT} over backend/src/orders/place.ts (step `lint`)" in done.stdout


def test_check_carries_no_such_receipt_where_no_step_decides_the_drifted_constraint(consumer):
    bind(consumer, node=CONSTRAINT)
    (consumer / "backend/src/orders/place.ts").write_text("export function place() { return 1 }\n",
                                                          encoding="utf-8")
    done = run("--check", consumer / "backend")
    assert done.returncode == 1, done.stdout + done.stderr
    assert "registry step decides" not in done.stdout


def test_encodes_marks_the_binding_a_registry_step_decides(consumer):
    bind(consumer)
    bind(consumer, node=CONSTRAINT)
    registry_deciding(consumer, CONSTRAINT)
    done = run("--encodes", consumer / "backend", FILE)
    assert done.returncode == 0, done.stdout + done.stderr
    assert f"{CONSTRAINT} — matches; a registry step decides it (`lint`)" in done.stdout
    assert f"{NODE} — matches\n" in done.stdout


def test_rank_counts_a_files_bindings_by_whether_a_reading_decides_them(consumer):
    """One judge is spawned per file and reads every binding on it, so the number a
    reconciliation's cost turns on is how many of a file's bindings a reading still decides —
    with the step-decided remainder beside it, never subtracted silently."""
    bind(consumer)
    bind(consumer, node=CONSTRAINT)
    registry_deciding(consumer, CONSTRAINT)
    done = run("--encodes", "--rank", consumer / "backend")
    assert done.returncode == 0, done.stdout + done.stderr
    assert "files by bindings a reading decides" in done.stdout
    assert "  1  backend/src/orders/place.ts  (1 decided by a registry step)" in done.stdout


def test_check_reports_a_file_that_moved_without_a_rebind(consumer):
    bind(consumer)
    path = consumer / "backend" / FILE
    path.write_text(path.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    done = run("--check", consumer / "backend")
    assert done.returncode == 1
    assert "the file changed without a rebind" in done.stdout


def test_check_lists_the_code_class_per_file_not_per_binding(consumer):
    """One file bound by many nodes that changes once is one act to take, not one line per
    binding: the remedy is a reconciliation, invoked over a file set, so the listing is keyed
    by file. The tally still counts bindings — grouping is the listing's business only."""
    bind(consumer)
    bind(consumer, node="constraints/asynchronous-events")
    path = consumer / "backend" / FILE
    path.write_text(path.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    done = run("--check", consumer / "backend")
    assert done.returncode == 1
    assert done.stdout.count("the file changed without a rebind") == 1
    assert (f"backend/{FILE}: the file changed without a rebind — 2 binding(s): "
            f"constraints/asynchronous-events, {NODE}") in done.stdout
    assert "2 code over 1 file(s):" in done.stdout


def test_check_reports_a_node_that_left_the_specification_without_breaking_it(consumer):
    """A constraint is not held to reachability, so removing it leaves everything else sound —
    the one case where a node can vanish without the whole base going unsound around it."""
    bind(consumer, node="constraints/asynchronous-events", file=FILE)
    (consumer / "specs/constraints/asynchronous-events.md").unlink()
    done = run("--check", consumer / "backend")
    assert done.returncode == 1
    assert "no longer in the specification; the binding is stale" in done.stdout


def test_check_over_a_specification_gone_unsound_names_that_instead(consumer):
    bind(consumer)
    (consumer / "specs" / f"{NODE}.md").unlink()
    done = run("--check", consumer / "backend")
    assert done.returncode == 1
    assert "is not sound; run spec.py against it directly" in done.stdout


def test_check_and_bind_are_mutually_exclusive(consumer):
    done = run("--check", "--bind", consumer / "backend")
    assert done.returncode == trace.CANNOT_RUN
    assert "mutually exclusive" in done.stderr


# ------------------------------------------------- every binding one record states, as one act


SECOND = "domain/troubleshooting/evidence"
OTHER_FILE = "src/orders/evidence.ts"


def record_at(consumer: Path, entries: list[dict], name: str = "record.md") -> Path:
    """An implementation record shaped as one is: frontmatter, then the two headings. Only `nodes`
    matters here — bin/deliver.py validated the rest before a bind is ever run."""
    path = consumer / "delivery" / "implementation" / "checkout"
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


def bind_record(consumer: Path, record: Path, replace: bool = False) -> subprocess.CompletedProcess:
    args = ["--bind-record", consumer / "backend", consumer / "specs", record]
    if replace:
        args.append("--replace")
    return run(*args)


def test_a_record_binds_every_node_it_encodes_in_one_write(consumer):
    (consumer / "backend/src/orders/evidence.ts").write_text("export {}\n", encoding="utf-8")
    record = record_at(consumer, [
        {"node": NODE, "encoded_at": [FILE], "how": "the case is what place() persists"},
        {"node": SECOND, "encoded_at": [FILE, OTHER_FILE], "how": "evidence is carried on it"},
    ])
    done = bind_record(consumer, record)
    assert done.returncode == 0, done.stdout + done.stderr
    declared = json.loads((consumer / "siegard-trace.json").read_text(encoding="utf-8"))
    assert [entry["node"] for entry in declared["bindings"]] == [NODE, SECOND]
    assert [f["path"] for f in declared["bindings"][1]["files"]] == \
        ["backend/src/orders/evidence.ts", "backend/src/orders/place.ts"]
    assert "2 binding(s) written" in done.stdout


def test_a_node_the_record_answers_only_by_how_is_not_bound(consumer):
    """There is no file to name, and a bind with none is refused — so an entry carrying `how`
    alone is passed over rather than turned into an empty binding."""
    record = record_at(consumer, [
        {"node": NODE, "encoded_at": [FILE], "how": "encoded here"},
        {"node": SECOND, "how": "the work honors it and encodes nothing of it"},
    ])
    done = bind_record(consumer, record)
    assert done.returncode == 0, done.stdout + done.stderr
    declared = json.loads((consumer / "siegard-trace.json").read_text(encoding="utf-8"))
    assert [entry["node"] for entry in declared["bindings"]] == [NODE]


def test_a_record_encoding_nothing_binds_nothing_and_is_not_a_defect(consumer):
    done = bind_record(consumer, record_at(consumer, [{"node": NODE, "how": "constrained, encoded nowhere"}]))
    assert done.returncode == 0, done.stdout + done.stderr
    assert "nothing to bind" in done.stdout
    assert not (consumer / "siegard-trace.json").exists(), \
        "a trace file created for nothing would say a delivery was linked"


def test_a_record_naming_a_node_the_specification_does_not_hold_binds_none_of_it(consumer):
    record = record_at(consumer, [
        {"node": NODE, "encoded_at": [FILE], "how": "encoded here"},
        {"node": "domain/troubleshooting/nowhere", "encoded_at": [FILE], "how": "encoded here"},
    ])
    done = bind_record(consumer, record)
    assert done.returncode == 1, done.stdout
    assert "holds no node domain/troubleshooting/nowhere" in done.stdout
    assert not (consumer / "siegard-trace.json").exists(), \
        "a record's bindings are one act; half of them written would read like all of them"


def test_a_record_naming_a_file_the_tree_does_not_hold_binds_none_of_it(consumer):
    record = record_at(consumer, [
        {"node": NODE, "encoded_at": [FILE], "how": "encoded here"},
        {"node": SECOND, "encoded_at": ["src/orders/gone.ts"], "how": "encoded here"},
    ])
    done = bind_record(consumer, record)
    assert done.returncode == 1, done.stdout
    assert "gone.ts does not exist" in done.stdout
    assert not (consumer / "siegard-trace.json").exists()


def test_the_refusal_names_the_anchor_a_missing_path_was_read_against(consumer):
    """The two anchors are the likeliest reason a path is missing, and `backend/backend/src/...`
    is a stranger thing to be handed than the reason for it: findings and trace entries are spelled
    from the git toplevel, and everything read here is spelled from the target source root."""
    record = record_at(consumer, [
        {"node": NODE, "encoded_at": [f"backend/{FILE}"], "how": "encoded here"},
    ])
    done = bind_record(consumer, record)
    assert done.returncode == 1, done.stdout
    assert "target source root" in done.stdout
    assert str(consumer / "backend") in done.stdout
    assert f"from the target it is `{FILE}`" in done.stdout, \
        "a refusal naming the rule alone sends the caller into a fix-and-rerun cycle; " \
        "the corrected spelling is what ends the class in one"


def test_a_missing_path_that_stands_outside_the_target_is_said_to(consumer):
    """The other half of the anchor diagnosis: a file that does exist at the toplevel's spelling
    but sits outside the target source root cannot be bound under any spelling, and saying so is
    the honest refusal rather than a corrected path that the climb-out check would then refuse."""
    (consumer / "README.md").write_text("prose\n", encoding="utf-8")
    record = record_at(consumer, [
        {"node": NODE, "encoded_at": ["README.md"], "how": "encoded here"},
    ])
    done = bind_record(consumer, record)
    assert done.returncode == 1, done.stdout
    assert "where no binding can name it" in done.stdout


def test_a_record_bind_extends_what_an_earlier_bind_held(consumer):
    """The same merge the per-node form has, for the same reason: two tasks landing one node in two
    files is not one of them undoing the other's work."""
    bind(consumer)
    (consumer / "backend/src/orders/other.ts").write_text("export {}\n", encoding="utf-8")
    done = bind_record(consumer, record_at(consumer, [
        {"node": NODE, "encoded_at": ["src/orders/other.ts"], "how": "and here too"}]))
    assert done.returncode == 0, done.stdout + done.stderr
    declared = json.loads((consumer / "siegard-trace.json").read_text(encoding="utf-8"))
    assert [f["path"] for f in declared["bindings"][0]["files"]] == \
        ["backend/src/orders/other.ts", "backend/src/orders/place.ts"]

    done = bind_record(consumer, record_at(consumer, [
        {"node": NODE, "encoded_at": ["src/orders/other.ts"], "how": "only here now"}]),
        replace=True)
    assert done.returncode == 0, done.stdout + done.stderr
    declared = json.loads((consumer / "siegard-trace.json").read_text(encoding="utf-8"))
    assert [f["path"] for f in declared["bindings"][0]["files"]] == \
        ["backend/src/orders/other.ts"]


def test_a_record_that_cannot_be_read_is_a_refusal_to_run(consumer):
    done = bind_record(consumer, consumer / "delivery/nowhere.md")
    assert done.returncode == trace.CANNOT_RUN
    assert "does not exist" in done.stderr

    stray = consumer / "delivery" / "stray.md"
    stray.parent.mkdir(parents=True, exist_ok=True)
    stray.write_text("no fence here\n", encoding="utf-8")
    done = bind_record(consumer, stray)
    assert done.returncode == trace.CANNOT_RUN
    assert "carries no frontmatter fence" in done.stderr


def test_a_record_bind_over_an_unsound_specification_writes_nothing(consumer):
    (consumer / "specs" / f"{NODE}.md").unlink()
    done = bind_record(consumer, record_at(consumer, [
        {"node": SECOND, "encoded_at": [FILE], "how": "encoded here"}]))
    assert done.returncode == 1, done.stdout
    assert "is not sound; nothing was bound." in done.stdout
    assert not (consumer / "siegard-trace.json").exists()


def test_bind_and_bind_record_are_mutually_exclusive(consumer):
    done = run("--bind", "--bind-record", consumer / "backend")
    assert done.returncode == trace.CANNOT_RUN
    assert "mutually exclusive" in done.stderr


# -------------------------------------------------------------------------- --prune

ORPHAN = "constraints/asynchronous-events"


def orphan(consumer: Path) -> None:
    """Bind a node, then take it out of the specification. A constraint is not held to
    reachability, so its removal leaves the base sound — the one way a node can vanish without
    everything around it going unsound, and therefore the only way to reach this class at all."""
    bind(consumer, node=ORPHAN, file=FILE)
    (consumer / f"specs/{ORPHAN}.md").unlink()


def test_prune_drops_a_binding_to_a_node_the_specification_no_longer_holds(consumer):
    """The class that had no exit. `--bind` refuses a node the specification does not hold and
    this script is the trace's one writer, so before `--prune` the entry could not be repaired by
    anything and its finding repeated on every run forever."""
    orphan(consumer)
    done = run("--prune", consumer / "backend")
    assert done.returncode == 0, done.stdout + done.stderr
    assert f"dropped {ORPHAN}" in done.stdout
    assert "1 binding(s) pruned" in done.stdout
    declared = json.loads((consumer / "siegard-trace.json").read_text(encoding="utf-8"))
    assert declared["bindings"] == []
    assert run("--check", consumer / "backend").returncode == 0


def test_prune_leaves_a_file_that_moved_exactly_where_it_was(consumer):
    """The refusal is the point. A file that drifted is drift with an owner and a remedy — the
    node is still in the base, still answered by code somewhere — and dropping the binding would
    destroy the one record of which node that code answers to while reporting the tree clean."""
    bind(consumer)
    path = consumer / "backend" / FILE
    path.write_text(path.read_text(encoding="utf-8") + "\n", encoding="utf-8")

    done = run("--prune", consumer / "backend")
    assert done.returncode == 0, done.stdout + done.stderr
    assert "nothing to prune" in done.stdout
    declared = json.loads((consumer / "siegard-trace.json").read_text(encoding="utf-8"))
    assert [entry["node"] for entry in declared["bindings"]] == [NODE]
    assert run("--check", consumer / "backend").returncode == 1


def test_prune_clears_the_stale_class_and_keeps_the_drift_underneath_it(consumer):
    """What the pile costs: the real finding is still there afterwards, and now it is readable."""
    bind(consumer)
    orphan(consumer)
    path = consumer / "backend" / FILE
    path.write_text(path.read_text(encoding="utf-8") + "\n", encoding="utf-8")

    done = run("--prune", consumer / "backend")
    assert done.returncode == 0, done.stdout + done.stderr
    declared = json.loads((consumer / "siegard-trace.json").read_text(encoding="utf-8"))
    assert [entry["node"] for entry in declared["bindings"]] == [NODE]

    after = run("--check", consumer / "backend")
    assert after.returncode == 1
    assert "the file changed without a rebind" in after.stdout
    assert "the binding is stale" not in after.stdout


def test_prune_over_a_specification_gone_unsound_deletes_nothing(consumer):
    """Every node of a base nobody could read looks stale. Pruning on the strength of not having
    been able to see them would delete bindings for nodes that exist."""
    bind(consumer)
    (consumer / "specs" / f"{NODE}.md").unlink()
    done = run("--prune", consumer / "backend")
    assert done.returncode == 1, done.stdout
    assert "nothing was pruned" in done.stdout
    declared = json.loads((consumer / "siegard-trace.json").read_text(encoding="utf-8"))
    assert [entry["node"] for entry in declared["bindings"]] == [NODE]


def test_prune_with_nothing_stale_writes_nothing_and_says_so(consumer):
    bind(consumer)
    done = run("--prune", consumer / "backend")
    assert done.returncode == 0, done.stdout + done.stderr
    assert "nothing to prune" in done.stdout


def test_prune_before_any_bind_is_not_a_defect(consumer):
    done = run("--prune", consumer / "backend")
    assert done.returncode == 0, done.stdout + done.stderr
    assert "nothing to prune" in done.stdout


def test_check_tallies_drift_by_class(consumer):
    """The tally is what a reader acts on, and the orphaned count is what says how much of the
    report no rebind will ever shorten."""
    bind(consumer)
    orphan(consumer)
    path = consumer / "backend" / FILE
    path.write_text(path.read_text(encoding="utf-8") + "\n", encoding="utf-8")

    done = run("--check", consumer / "backend")
    assert done.returncode == 1
    assert "1 orphaned:" in done.stdout
    assert "0 moved:" in done.stdout
    assert "2 code over 1 file(s):" in done.stdout, done.stdout
    assert "`--prune` is the only thing that clears them" in done.stdout


def test_prune_and_check_are_mutually_exclusive(consumer):
    done = run("--prune", "--check", consumer / "backend")
    assert done.returncode == trace.CANNOT_RUN
    assert "mutually exclusive" in done.stderr


# ------------------------------------------------------------------------ --release


def test_release_refuses_a_file_the_tree_still_holds(consumer):
    """A file that exists is reconciled, never released: the link is the one record of which node
    that code answers to, and a file on disk is a file a judge can still read."""
    bind(consumer)
    before = (consumer / "siegard-trace.json").read_text(encoding="utf-8")
    done = run("--release", consumer / "backend", f"backend/{FILE}")
    assert done.returncode == trace.CANNOT_RUN, done.stdout + done.stderr
    assert f"backend/{FILE} still exists; a file that exists is reconciled, never released" \
        in done.stderr
    assert (consumer / "siegard-trace.json").read_text(encoding="utf-8") == before


def test_release_removes_the_path_and_the_binding_it_emptied(consumer):
    """A bound file gone from the tree is drift nothing else answers: no staging reads it and no
    prune touches it. The release drops the path from every binding naming it, drops a binding
    left with nothing, and says both."""
    bind(consumer)
    (consumer / "backend/src/orders/other.ts").write_text("export {}\n", encoding="utf-8")
    second = "domain/troubleshooting/case-id"
    bind(consumer, node=second, file=FILE)
    bind(consumer, node=second, file="src/orders/other.ts")
    (consumer / "backend" / FILE).unlink()

    done = run("--release", consumer / "backend", f"backend/{FILE}")
    assert done.returncode == 0, done.stdout + done.stderr
    assert f"--release released 1 path(s) the tree no longer holds; {NODE} no longer claims " \
           f"backend/{FILE}" in done.stdout
    assert f"{second} no longer claims backend/{FILE}" in done.stdout
    assert f"{NODE} held nothing else and is gone from the trace" in done.stdout
    assert f"{second} held nothing else" not in done.stdout
    declared = json.loads((consumer / "siegard-trace.json").read_text(encoding="utf-8"))
    assert [entry["node"] for entry in declared["bindings"]] == [second]
    assert [f["path"] for f in declared["bindings"][0]["files"]] == \
        ["backend/src/orders/other.ts"]
    assert run("--check", consumer / "backend").returncode == 0


def test_release_reads_the_targets_own_spelling_too(consumer):
    bind(consumer)
    (consumer / "backend" / FILE).unlink()
    done = run("--release", consumer / "backend", FILE)
    assert done.returncode == 0, done.stdout + done.stderr
    assert f"{NODE} no longer claims backend/{FILE}" in done.stdout


def test_release_refuses_a_path_no_binding_names(consumer):
    bind(consumer)
    done = run("--release", consumer / "backend", "backend/src/orders/nothing.ts")
    assert done.returncode == 1, done.stdout + done.stderr
    assert "backend/src/orders/nothing.ts: no binding names it" in done.stdout
    declared = json.loads((consumer / "siegard-trace.json").read_text(encoding="utf-8"))
    assert [entry["node"] for entry in declared["bindings"]] == [NODE]


def test_release_refuses_the_whole_call_before_writing_any_of_it(consumer):
    bind(consumer)
    (consumer / "backend/src/orders/other.ts").write_text("export {}\n", encoding="utf-8")
    bind(consumer, file="src/orders/other.ts")
    (consumer / "backend" / FILE).unlink()
    done = run("--release", consumer / "backend", f"backend/{FILE}",
               "backend/src/orders/other.ts")
    assert done.returncode == trace.CANNOT_RUN, done.stdout + done.stderr
    declared = json.loads((consumer / "siegard-trace.json").read_text(encoding="utf-8"))
    assert len(declared["bindings"][0]["files"]) == 2


def test_check_names_the_release_route_for_a_file_that_is_gone(consumer):
    bind(consumer)
    (consumer / "backend" / FILE).unlink()
    done = run("--check", consumer / "backend")
    assert done.returncode == 1
    assert f"backend/{FILE}: the file no longer exists — `--release` is what answers a deleted " \
           f"file" in done.stdout, done.stdout


def test_release_and_prune_are_mutually_exclusive(consumer):
    done = run("--release", "--prune", consumer / "backend", FILE)
    assert done.returncode == trace.CANNOT_RUN
    assert "mutually exclusive" in done.stderr


# ------------------------------------------------------------ --prune follows a rename

RENAMED = "constraints/async-events"


def git(consumer: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(consumer), "-c", "user.email=t@t", "-c", "user.name=t",
                    *args], check=True, capture_output=True)


def renamed(consumer: Path) -> None:
    """Bind a node, commit, move its file under git, commit again: the one shape in which a node
    leaves the specification while git still knows where it went."""
    bind(consumer, node=ORPHAN, file=FILE)
    git(consumer, "add", "-A")
    git(consumer, "commit", "-qm", "base")
    git(consumer, "mv", f"specs/{ORPHAN}.md", f"specs/{RENAMED}.md")
    git(consumer, "commit", "-qm", "rename")


def test_check_says_where_an_orphaned_node_went_when_git_knows(consumer):
    renamed(consumer)
    done = run("--check", consumer / "backend")
    assert done.returncode == 1
    assert f"{ORPHAN}: no longer in the specification; the binding is stale — renamed to " \
           f"{RENAMED}; `--prune` follows it" in done.stdout, done.stdout


def test_prune_follows_a_renamed_node_and_keeps_its_files(consumer):
    """A `git mv` of a node is the node under a new identity, not a node that left. Dropping
    the binding would lose the one link the trace exists to keep; following the rename keeps
    the files and the digest, and a node whose text also moved reads as `moved` afterwards."""
    renamed(consumer)
    before = json.loads((consumer / "siegard-trace.json").read_text(encoding="utf-8"))
    done = run("--prune", consumer / "backend")
    assert done.returncode == 0, done.stdout + done.stderr
    assert f"followed rename {ORPHAN} → {RENAMED} (1 file(s) kept)" in done.stdout
    assert f"dropped {ORPHAN}" not in done.stdout
    assert "0 binding(s) pruned and 1 followed to a renamed node" in done.stdout
    declared = json.loads((consumer / "siegard-trace.json").read_text(encoding="utf-8"))
    assert [entry["node"] for entry in declared["bindings"]] == [RENAMED]
    assert declared["bindings"][0]["files"] == before["bindings"][0]["files"]
    assert declared["bindings"][0]["digest"] == before["bindings"][0]["digest"]
    assert run("--check", consumer / "backend").returncode == 0


def test_prune_follows_a_chain_of_renames_to_the_latest(consumer):
    renamed(consumer)
    git(consumer, "mv", f"specs/{RENAMED}.md", "specs/constraints/events-async.md")
    git(consumer, "commit", "-qm", "rename again")
    done = run("--prune", consumer / "backend")
    assert done.returncode == 0, done.stdout + done.stderr
    assert f"followed rename {ORPHAN} → constraints/events-async (1 file(s) kept)" in done.stdout
    declared = json.loads((consumer / "siegard-trace.json").read_text(encoding="utf-8"))
    assert [entry["node"] for entry in declared["bindings"]] == ["constraints/events-async"]


def test_prune_joins_a_followed_rename_to_a_binding_the_new_identity_already_holds(consumer):
    renamed(consumer)
    (consumer / "backend/src/orders/other.ts").write_text("export {}\n", encoding="utf-8")
    bind(consumer, node=RENAMED, file="src/orders/other.ts")
    done = run("--prune", consumer / "backend")
    assert done.returncode == 0, done.stdout + done.stderr
    assert f"followed rename {ORPHAN} → {RENAMED} (1 file(s) kept, joined to the binding " \
           f"{RENAMED} already holds)" in done.stdout
    declared = json.loads((consumer / "siegard-trace.json").read_text(encoding="utf-8"))
    assert [entry["node"] for entry in declared["bindings"]] == [RENAMED]
    assert sorted(f["path"] for f in declared["bindings"][0]["files"]) == \
        ["backend/src/orders/other.ts", "backend/src/orders/place.ts"]


def test_prune_drops_an_orphan_whose_rename_target_is_gone_too(consumer):
    renamed(consumer)
    (consumer / f"specs/{RENAMED}.md").unlink()
    done = run("--prune", consumer / "backend")
    assert done.returncode == 0, done.stdout + done.stderr
    assert f"dropped {ORPHAN}" in done.stdout
    assert "followed rename" not in done.stdout
    declared = json.loads((consumer / "siegard-trace.json").read_text(encoding="utf-8"))
    assert declared["bindings"] == []


def test_prune_drops_as_before_where_git_holds_no_history_of_the_node(consumer):
    """No commit is the limit case of no git: `git log` answers nothing either way, and a rename
    nobody recorded is a rename nothing can follow."""
    bind(consumer, node=ORPHAN, file=FILE)
    (consumer / f"specs/{ORPHAN}.md").rename(consumer / f"specs/{RENAMED}.md")
    done = run("--check", consumer / "backend")
    assert "renamed to" not in done.stdout
    done = run("--prune", consumer / "backend")
    assert done.returncode == 0, done.stdout + done.stderr
    assert f"dropped {ORPHAN}" in done.stdout
    declared = json.loads((consumer / "siegard-trace.json").read_text(encoding="utf-8"))
    assert declared["bindings"] == []


# ------------------------------------------------- what a --replace stops claiming

def second_file(consumer: Path) -> None:
    (consumer / "backend" / OTHER_FILE).write_text("export {}\n", encoding="utf-8")


def test_replace_names_every_path_it_stops_claiming(consumer):
    """The last silent loss in this writer. `--replace` substitutes the whole entry, so a path an
    earlier bind put there and this call leaves off is gone — and gone invisibly, because the
    trace it writes is internally consistent and `--check` comes back clean over it."""
    second_file(consumer)
    bind(consumer)
    done = bind(consumer, file=OTHER_FILE, replace=True)
    assert done.returncode == 0, done.stdout + done.stderr
    assert "--replace released 1 path(s)" in done.stdout
    assert "backend/src/orders/place.ts" in done.stdout
    declared = json.loads((consumer / "siegard-trace.json").read_text(encoding="utf-8"))
    assert [f["path"] for f in declared["bindings"][0]["files"]] == \
        ["backend/src/orders/evidence.ts"]


def test_the_receipt_is_a_receipt_and_not_a_refusal(consumer):
    """Dropping a file is what `--replace` is for, and the ordinary use — omitting a path that no
    longer exists, which `traced_files_of` refuses to name — is the correct one. An alarm on the
    correct path is an alarm nobody reads by the third time."""
    second_file(consumer)
    bind(consumer)
    (consumer / "backend" / FILE).unlink()
    done = bind(consumer, file=OTHER_FILE, replace=True)
    assert done.returncode == 0, done.stdout + done.stderr
    assert "cannot" not in done.stdout
    assert "backend/src/orders/place.ts" in done.stdout, \
        "the receipt confirms exactly the vanished path the caller meant to let go"
    assert run("--check", consumer / "backend").returncode == 0


def test_a_replace_that_drops_nothing_prints_no_receipt(consumer):
    bind(consumer)
    done = bind(consumer, replace=True)
    assert done.returncode == 0, done.stdout + done.stderr
    assert "released" not in done.stdout


def test_the_union_default_never_prints_a_receipt(consumer):
    """Nothing is dropped without --replace, so a receipt there would name a loss that did not
    happen — which is worse than the silence it replaces."""
    second_file(consumer)
    bind(consumer)
    done = bind(consumer, file=OTHER_FILE)
    assert done.returncode == 0, done.stdout + done.stderr
    assert "released" not in done.stdout
    declared = json.loads((consumer / "siegard-trace.json").read_text(encoding="utf-8"))
    assert len(declared["bindings"][0]["files"]) == 2


def test_a_record_replace_reports_what_a_sibling_record_had_bound(consumer):
    """The trap as the consumer met it: two records answering one node, replaced from the second.
    The receipt names paths and never the record that put them there — which delivery bound a file
    is not something this file stores."""
    second_file(consumer)
    first = record_at(consumer, [{"node": NODE, "encoded_at": [FILE], "how": "here"}], name="a.md")
    later = record_at(consumer, [{"node": NODE, "encoded_at": [OTHER_FILE], "how": "moved"}],
                      name="b.md")
    assert bind_record(consumer, first).returncode == 0
    done = bind_record(consumer, later, replace=True)
    assert done.returncode == 0, done.stdout + done.stderr
    assert "backend/src/orders/place.ts" in done.stdout
    assert "1 path(s) released across 1 node(s)" in done.stdout


# ------------------------------------------------ a target whose surface is edited by hand


def declare_freely(consumer: Path, *keys: str, targets: dict | None = None) -> None:
    """The consumer's own project file, declaring which targets a person edits without a task.
    Written here rather than by a fixture because what these tests vary is exactly this file."""
    (consumer / "siegard.json").write_text(json.dumps({
        "specification_root": "specs",
        "targets": targets or {"backend": "backend"},
        "work_root": "work",
        "delivery_root": "delivery",
        "edits_freely": list(keys),
    }, indent=2) + "\n", encoding="utf-8")


def drifted(consumer: Path, file: str = FILE) -> None:
    path = consumer / "backend" / file
    path.write_text(path.read_text(encoding="utf-8") + "\n", encoding="utf-8")


def test_a_project_declaring_nothing_is_held_to_every_class(consumer):
    """The state every project was in before the field existed, and the one a backend stays in."""
    bind(consumer)
    drifted(consumer)
    done = run("--check", consumer / "backend")
    assert done.returncode == 1
    assert "the file changed without a rebind" in done.stdout
    assert "suppressed" not in done.stdout


def test_a_declared_target_stops_listing_the_code_class(consumer):
    bind(consumer)
    drifted(consumer)
    declare_freely(consumer, "backend")
    done = run("--check", consumer / "backend")
    assert done.returncode == 0, done.stdout + done.stderr
    assert "the file changed without a rebind" not in done.stdout
    assert "suppressed 1 `code` finding(s) over 1 file(s) under backend" in done.stdout


def test_the_receipt_is_what_keeps_the_declaration_measurable(consumer):
    """A suppression a consumer cannot count is one they forget they turned on. The count rides
    the class's own tally line too, so `0 code` is never the last thing a reader sees."""
    bind(consumer)
    drifted(consumer)
    orphan(consumer)
    declare_freely(consumer, "backend")
    done = run("--check", consumer / "backend")
    assert done.returncode == 1
    assert "0 code (1 suppressed)" in done.stdout
    assert "suppressed 1 `code` finding(s)" in done.stdout


def test_all_lists_what_the_declaration_held_back(consumer):
    bind(consumer)
    drifted(consumer)
    declare_freely(consumer, "backend")
    done = run("--check", "--all", consumer / "backend")
    assert done.returncode == 1, done.stdout + done.stderr
    assert "the file changed without a rebind" in done.stdout
    assert "suppressed" not in done.stdout


def test_the_other_two_classes_are_untouched_by_the_declaration(consumer):
    """`moved` says the specification shifted under these files and `orphaned` says the node is
    gone; neither depends on how often the files themselves move, so neither is held back."""
    bind(consumer)
    orphan(consumer)
    (consumer / "specs" / f"{NODE}.md").write_text(
        (consumer / "specs" / f"{NODE}.md").read_text(encoding="utf-8") + "\nA later sentence.\n",
        encoding="utf-8")
    declare_freely(consumer, "backend")
    done = run("--check", consumer / "backend")
    assert done.returncode == 1
    assert "the binding is stale" in done.stdout
    assert "the specification moved since this bind" in done.stdout


def test_a_sibling_target_keeps_every_finding(consumer):
    """The monorepo case, and the reason the filter is a path prefix rather than the invocation:
    one trace serves every target under a toplevel, so a declared frontend must not cost the
    backend a finding — whichever target the check was pointed at."""
    (consumer / "web").mkdir()
    (consumer / "web" / "app.tsx").write_text("export const App = () => null;\n", encoding="utf-8")
    bind(consumer)
    drifted(consumer)
    declare_freely(consumer, "web", targets={"backend": "backend", "web": "web"})
    done = run("--check", consumer / "backend")
    assert done.returncode == 1
    assert "the file changed without a rebind" in done.stdout
    assert "suppressed" not in done.stdout


def test_a_target_named_in_the_declaration_and_absent_from_targets_suppresses_nothing(consumer):
    """A key that resolves to no path reaches no file. Said by doing nothing rather than by
    refusing: project.py is what holds that file to its contract, and a drift report is the wrong
    place to learn the project file is wrong."""
    bind(consumer)
    drifted(consumer)
    declare_freely(consumer, "frontend")
    assert run("--check", consumer / "backend").returncode == 1


def test_all_without_check_is_refused(consumer):
    done = run("--all", consumer / "backend")
    assert done.returncode == 2
    assert "--all only applies to --check" in done.stderr


def test_a_trace_naming_an_absolute_specification_is_refused(consumer):
    """`trace.py` composes `home / declared["specification"]`, and an absolute value wins that
    join — `Path("/repo") / "/etc"` is `/etc`. Nothing this script writes can be absolute
    (`opened` computes the value with `os.path.relpath`), so this is reachable only by a hand-
    edited trace; the module docstring already states the rule for every path the file holds, and
    until the pattern existed the schema did not. `deliver.py` guards the identical hazard."""
    bind(consumer)
    path = consumer / "siegard-trace.json"
    declared = json.loads(path.read_text(encoding="utf-8"))
    declared["specification"] = "/etc"
    path.write_text(json.dumps(declared, indent=2) + "\n", encoding="utf-8")
    done = run(consumer / "backend")
    assert done.returncode == 1, done.stdout + done.stderr
    assert "specification" in done.stdout, done.stdout


# ------------------------------------------------------------ impact from a change


def committed(consumer: Path) -> None:
    subprocess.run(["git", "-C", str(consumer), "add", "-A"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(consumer), "-c", "user.email=t@t", "-c", "user.name=t",
                    "commit", "-qm", "base"], check=True, capture_output=True)


def test_changed_reads_the_file_set_off_the_working_tree(consumer):
    """Impact runs forward everywhere else — from node identities, or from paths a caller listed.
    The question a change raises runs the other way: these files moved, which nodes do they
    encode."""
    bind(consumer)
    committed(consumer)
    drifted(consumer)
    done = run("--encodes", "--changed", consumer / "backend")
    assert done.returncode == 0, done.stdout + done.stderr
    assert "1 path(s) changed in the working tree against HEAD" in done.stdout, done.stdout
    assert f"{FILE}: 1 binding(s)" in done.stdout
    assert NODE in done.stdout


def test_changed_converts_the_anchor_git_prints_to_the_one_encodes_reads(consumer):
    """Git names every path from the toplevel and `--encodes` reads every path from the target
    source root. Composing the two by hand is the step a caller gets wrong: handing git's own
    spelling straight to `--encodes` is a refusal per path, and this form is what makes the
    composition right once instead of at every call site."""
    bind(consumer)
    committed(consumer)
    drifted(consumer)

    by_hand = run("--encodes", consumer / "backend", f"backend/{FILE}")
    assert by_hand.returncode == trace.CANNOT_RUN, \
        "the toplevel's spelling is what this form exists to convert, and it must still be a " \
        "refusal when a caller passes it directly"
    done = run("--encodes", "--changed", consumer / "backend")
    assert done.returncode == 0, done.stdout + done.stderr
    assert "does not exist" not in done.stdout + done.stderr


def test_changed_drops_what_sits_outside_the_target_rather_than_refusing_it(consumer):
    """One commit touching two targets is an ordinary commit, and the answer over this target is
    still the whole answer over this target."""
    bind(consumer)
    committed(consumer)
    (consumer / "docs").mkdir()
    (consumer / "docs" / "note.md").write_text("a note\n", encoding="utf-8")
    done = run("--encodes", "--changed", consumer / "backend")
    assert done.returncode == 0, done.stdout + done.stderr
    assert "1 under another target" in done.stdout, done.stdout
    assert "nothing changed under this target source root" in done.stdout


def test_changed_over_a_ref_reads_what_the_branch_changed(consumer):
    bind(consumer)
    committed(consumer)
    drifted(consumer)
    subprocess.run(["git", "-C", str(consumer), "add", "-A"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(consumer), "-c", "user.email=t@t", "-c", "user.name=t",
                    "commit", "-qm", "second"], check=True, capture_output=True)
    done = run("--encodes", "--changed", consumer / "backend", "HEAD~1")
    assert done.returncode == 0, done.stdout + done.stderr
    assert "against HEAD~1" in done.stdout
    assert f"{FILE}: 1 binding(s)" in done.stdout


def test_changed_counts_a_file_the_tree_deleted_rather_than_refusing_it(consumer):
    """A deleted file has no digest to read, and what its bindings are now is `--check`'s
    question — this one is about files a judge could still open."""
    bind(consumer)
    committed(consumer)
    (consumer / "backend" / FILE).unlink()
    done = run("--encodes", "--changed", consumer / "backend")
    assert done.returncode == 0, done.stdout + done.stderr
    assert "no longer on disk" in done.stdout


def test_changed_and_rank_are_refused_together(consumer):
    done = run("--encodes", "--changed", "--rank", consumer / "backend")
    assert done.returncode == trace.CANNOT_RUN
    assert "--changed names a file set and --rank reads them all" in done.stderr


def test_changed_names_the_cause_where_the_tree_holds_no_commit(consumer):
    """Git's own message for this is its usage blurb, which says nothing a reader can act on.
    Before the first commit every file is new, so the whole tree would be the answer — which is
    no answer about a change."""
    done = run("--encodes", "--changed", consumer / "backend")
    assert done.returncode == trace.CANNOT_RUN
    assert "holds no commit yet" in done.stderr, done.stderr
    assert "name a ref" in done.stderr


# ----------------------------------------------------- every node in one state


def planned(consumer: Path, slug: str = "first") -> Path:
    """One initiative under the consumer's work root: an epic covering three nodes, a task
    implementing the bound one, a task implementing one nothing binds, and the third declared
    uncovered with a reason."""
    work = consumer / "work" / slug
    (work / "epic").mkdir(parents=True)
    (work / "task" / "cases").mkdir(parents=True)
    def put(rel: str, front: dict) -> None:
        (work / rel).write_text("---\n" + yaml.safe_dump(front, sort_keys=False) + "---\n"
                                "## What it is\nProse.\n\n## Notes\nNone.\n", encoding="utf-8")
    put("epic/cases.md", {"title": "Cases", "summary": "Everything a case needs.",
                          "covers": [NODE, "domain/troubleshooting/case-id", CONSTRAINT],
                          "uncovered": [{"node": "domain/troubleshooting/case-id",
                                         "why": "the store issues it; no task adds to that"}]})
    put("task/cases/record-case.md", {"title": "Record case", "summary": "Persist a case.",
                                      "objective": "A case is persisted.",
                                      "criteria": ["Opening a case returns its id."],
                                      "implements": [NODE]})
    put("task/cases/events.md", {"title": "Events", "summary": "Publish asynchronously.",
                                 "objective": "Events leave the process asynchronously.",
                                 "criteria": ["No handler awaits a subscriber."],
                                 "implements": [CONSTRAINT]})
    return consumer / "work"


def test_convergence_puts_every_node_in_exactly_one_state(consumer):
    """The four readings this composes are each correct alone, and composed by hand they answer
    wrongly: an uncovered node reads as a gap, a planned one as never planned. One state per node,
    by class, is what a reader could not assemble without knowing all four semantics."""
    bind(consumer)
    work = planned(consumer)
    done = run("--convergence", consumer / "backend", consumer / "specs", work)
    assert done.returncode == 0, done.stdout + done.stderr
    assert "1 current:" in done.stdout, done.stdout
    assert "0 stale:" in done.stdout
    assert "1 planned-unbound:" in done.stdout
    assert "1 declared-uncovered:" in done.stdout
    assert "unreached:" in done.stdout and "0 unreached" not in done.stdout
    assert "1 initiative(s) read under" in done.stdout


def test_convergence_reports_a_drifted_binding_as_stale(consumer):
    bind(consumer)
    work = planned(consumer)
    drifted(consumer)
    done = run("--convergence", consumer / "backend", consumer / "specs", work)
    assert done.returncode == 0, done.stdout + done.stderr
    assert "0 current:" in done.stdout and "1 stale:" in done.stdout, done.stdout


def test_convergence_names_a_bound_node_no_initiative_named(consumer):
    """Bound by a reconciliation over source that entered outside any task, or by a raw bind:
    the one class `--unplanned` cannot separate from a node nothing reached."""
    bind(consumer)
    bind(consumer, node="domain/monitoring/alert")
    work = planned(consumer)
    done = run("--convergence", consumer / "backend", consumer / "specs", work, "--all")
    assert done.returncode == 0, done.stdout + done.stderr
    assert "1 bound node(s) no initiative names" in done.stdout, done.stdout
    assert "domain/monitoring/alert" in done.stdout


def test_convergence_keeps_the_judged_side_apart(consumer):
    """A binding that computes is a fact about bytes; a record that found against a node is a
    fact about a reading. A tally that added them would be a reading of neither."""
    bind(consumer)
    work = planned(consumer)
    done = run("--convergence", consumer / "backend", consumer / "specs", work)
    assert done.returncode == 0, done.stdout + done.stderr
    assert "Kept apart" in done.stdout and "`--owed` names each record" in done.stdout


def test_convergence_exits_zero_over_a_tree_nothing_reached(consumer):
    (consumer / "work").mkdir()
    done = run("--convergence", consumer / "backend", consumer / "specs", consumer / "work")
    assert done.returncode == 0, done.stdout + done.stderr
    assert "nothing has been bound yet" in done.stdout
    assert "0 current:" in done.stdout


def test_convergence_lists_the_nodes_of_each_state_under_all(consumer):
    bind(consumer)
    work = planned(consumer)
    done = run("--convergence", consumer / "backend", consumer / "specs", work, "--all")
    assert done.returncode == 0, done.stdout + done.stderr
    assert f"      {NODE}" in done.stdout


def test_convergence_refuses_a_specification_the_trace_was_not_written_against(consumer):
    bind(consumer)
    shutil.copytree(consumer / "specs", consumer / "specs2")
    work = planned(consumer)
    done = run("--convergence", consumer / "backend", consumer / "specs2", work)
    assert done.returncode == trace.CANNOT_RUN
    assert "an answer about a different specification" in done.stderr


def test_convergence_refuses_one_initiative_in_place_of_their_parent(consumer):
    bind(consumer)
    work = planned(consumer)
    done = run("--convergence", consumer / "backend", consumer / "specs", work / "first")
    assert done.returncode == trace.CANNOT_RUN
    assert "one initiative rather than the directory they sit in" in done.stderr


def test_convergence_and_check_are_mutually_exclusive(consumer):
    done = run("--convergence", "--check", consumer / "backend", consumer / "specs",
               consumer / "work")
    assert done.returncode == trace.CANNOT_RUN


# --------------------------------------------------------------------------- untraced


def tracked(consumer: Path, *paths: str) -> None:
    for rel in paths:
        (consumer / "backend" / rel).parent.mkdir(parents=True, exist_ok=True)
        if not (consumer / "backend" / rel).exists():
            (consumer / "backend" / rel).write_text("export {}\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(consumer), "add", "--", "backend"], check=True)


def test_untraced_names_every_tracked_file_with_no_trace_yet(consumer):
    """Code no delivery wrote is in no drift report: nothing binds it, so nothing changes. This
    is the one report that sees it, and with no trace every tracked file is untraced."""
    tracked(consumer, "src/orders/cancel.ts")
    done = run("--untraced", consumer / "backend")
    assert done.returncode == 0, done.stdout + done.stderr
    assert "2 tracked file(s) under backend: 0 bound, 2 no binding names" in done.stdout
    assert "no trace file" in done.stdout
    assert "backend/src/orders" in done.stdout


def test_untraced_leaves_out_what_a_binding_names_and_what_git_does_not_track(consumer):
    tracked(consumer, "src/orders/cancel.ts")
    (consumer / "backend/src/orders/scratch.ts").write_text("x\n", encoding="utf-8")
    assert bind(consumer).returncode == 0
    done = run("--untraced", consumer / "backend", "--all")
    assert done.returncode == 0, done.stdout + done.stderr
    assert "2 tracked file(s) under backend: 1 bound, 1 no binding names" in done.stdout
    assert "unsurveyed:\n  backend/src/orders/cancel.ts" in done.stdout
    assert "place.ts" not in done.stdout.split("unsurveyed:\n")[1]
    assert "scratch.ts" not in done.stdout


def test_untraced_refuses_nothing_when_every_file_is_bound(consumer):
    tracked(consumer)
    assert bind(consumer).returncode == 0
    done = run("--untraced", consumer / "backend")
    assert done.returncode == 0
    assert "1 tracked file(s) under backend: 1 bound, 0 no binding names" in done.stdout


def certified(consumer: Path, proof: str) -> None:
    """The binding of NODE as a certification leaves it: decided by a test whose file is pinned
    beside the files', written here directly because only the paths are what --untraced reads."""
    trace_file = consumer / "siegard-trace.json"
    declared = json.loads(trace_file.read_text(encoding="utf-8"))
    entry = next(e for e in declared["bindings"] if e["node"] == NODE)
    entry.update({"decided_by": "test", "step": "test",
                  "proof": [{"path": f"backend/{proof}",
                             "digest": trace.spec.digest_of(consumer / "backend" / proof)}]})
    trace_file.write_text(json.dumps(declared, indent=2) + "\n", encoding="utf-8")


def test_untraced_counts_a_certification_s_proof_as_bound(consumer):
    """SPEC-005 R5: bound is a binding naming the file, and a certified binding names its proof:
    the trace pins that file's digest and reports its drift, so it is never unsurveyed."""
    tracked(consumer, "src/orders/place.spec.ts", "src/orders/cancel.ts")
    assert bind(consumer).returncode == 0
    certified(consumer, "src/orders/place.spec.ts")
    done = run("--untraced", consumer / "backend", "--all")
    assert done.returncode == 0, done.stdout + done.stderr
    assert ("3 tracked file(s) under backend: 2 bound (1 as a certification's proof), "
            "1 no binding names") in done.stdout
    assert "place.spec.ts" not in done.stdout.split("unsurveyed:\n")[1]


def test_untraced_is_its_own_form(consumer):
    done = run("--untraced", consumer / "backend", "--check")
    assert done.returncode == 2
    assert "mutually exclusive" in done.stderr


def test_convergence_counts_the_files_no_binding_names(consumer):
    tracked(consumer, "src/orders/cancel.ts")
    bind(consumer)
    work = planned(consumer)
    done = run("--convergence", consumer / "backend", consumer / "specs", work)
    assert done.returncode == 0, done.stdout + done.stderr
    assert ("files under backend: 2 tracked, 1 bound, 1 no binding names (1 unsurveyed) — "
            "`--untraced` lists them") in done.stdout


def test_convergence_reads_a_work_root_nobody_planned_into_as_no_initiative(consumer):
    """A project whose code arrived by adoption has no initiative yet, so its work root does not
    exist; that is a count of zero, and a path that exists and is not a directory is still a stop."""
    bind(consumer)
    done = run("--convergence", consumer / "backend", consumer / "specs", consumer / "no-work-yet")
    assert done.returncode == 0, done.stdout + done.stderr
    assert "0 initiative(s) read under" in done.stdout and "it does not exist" in done.stdout
    assert "1 current:" in done.stdout
    (consumer / "a-file").write_text("x\n", encoding="utf-8")
    done = run("--convergence", consumer / "backend", consumer / "specs", consumer / "a-file")
    assert done.returncode == 2 and "is not a directory" in done.stderr


# ------------------------------------------- a file is stamped against the node it was read at


def test_a_bind_restamps_only_the_files_its_record_names(consumer):
    """A node bound to two files and rebound from a record naming one: the other file keeps the
    node text it was read against, and `--check` reports it moved on its own — the cross-target
    restamp that once silenced 22 files' drift."""
    other = "src/orders/ship.ts"
    (consumer / "backend" / other).write_text("export function ship() {}\n", encoding="utf-8")
    assert bind(consumer).returncode == 0
    node_file = consumer / "specs" / f"{NODE}.md"
    node_file.write_text(node_file.read_text(encoding="utf-8") + "\nMoved.\n", encoding="utf-8")
    assert bind(consumer, file=other).returncode == 0
    trace_file = json.loads((consumer / "siegard-trace.json").read_text(encoding="utf-8"))
    [entry] = [e for e in trace_file["bindings"] if e["node"] == NODE]
    stamped = {f["path"]: f["node_digest"] for f in entry["files"]}
    assert stamped[f"backend/{other}"] == entry["digest"]
    assert stamped[f"backend/{FILE}"] != entry["digest"], "kept at the text it was read against"
    done = run("--check", consumer / "backend")
    assert done.returncode == 1, done.stdout
    assert f"{NODE}: backend/{FILE} was stamped against" in done.stdout
    assert "1 moved:" in done.stdout and "0 code" in done.stdout


def test_a_file_stamped_before_the_field_existed_reads_as_stamped_at_the_binding(consumer):
    assert bind(consumer).returncode == 0
    path = consumer / "siegard-trace.json"
    declared = json.loads(path.read_text(encoding="utf-8"))
    for entry in declared["bindings"]:
        for held in entry["files"]:
            held.pop("node_digest", None)
    path.write_text(json.dumps(declared, indent=2) + "\n", encoding="utf-8")
    done = run("--check", consumer / "backend")
    assert done.returncode == 0, done.stdout + done.stderr
