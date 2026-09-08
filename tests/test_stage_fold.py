"""The staged reconciliation and the mechanical fold: `--stage` and `--fold`.

Two halves, and each exists to take a hand off a wheel. `--stage` computes what every judgment
needs before any judgment runs — the node set per file, a pack restating each set's node text
byte for byte, the batch's candidate index, and the pairs whose re-judgment would buy a second
reading of text that did not move. `--fold` writes the record from the delegations' saved returns
by rules that ask for no judgment, which is why every rule is a test here: a fold applied by a
context that could misremember one between node forty and node eighty is exactly what these two
forms replace.

The omission guard is the half that carries the risk, so it is tested live: a pair is omittable
only while the binding computes at the file's content and no record holds an open finding against
it, and both halves are recomputed at bind time — a record whose omission claim went stale
between staging and binding refuses whole.
"""
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
OTHER = "domain/troubleshooting/evidence"
FILE = "src/orders/place.ts"
SECOND = "src/orders/bill.ts"


def run(*args) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(TRACE_PY), *map(str, args)],
                          capture_output=True, text=True)


@pytest.fixture
def consumer(tmp_path: Path) -> Path:
    """A consumer repository with two files bound and one of them drifted: NODE is bound to both
    files, OTHER to the first alone, and the first file then changes — so its pairs are stale
    while (NODE, SECOND) still computes."""
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True, capture_output=True)
    spec_root = tmp_path / "specs"
    shutil.copytree(FIXTURE, spec_root)
    shutil.rmtree(spec_root / "projections", ignore_errors=True)
    target = tmp_path / "backend"
    (target / "src/orders").mkdir(parents=True)
    (target / FILE).write_text("export function place() {}\n", encoding="utf-8")
    (target / SECOND).write_text("export function bill() {}\n", encoding="utf-8")
    (tmp_path / "siegard.json").write_text(json.dumps(
        {"specification_root": "specs", "targets": {"backend": "backend"}}) + "\n",
        encoding="utf-8")
    assert run("--bind", target, spec_root, NODE, FILE, SECOND).returncode == 0
    assert run("--bind", target, spec_root, OTHER, FILE).returncode == 0
    with (target / FILE).open("a", encoding="utf-8") as drifted:
        drifted.write("// drift\n")
    return tmp_path


def staged(consumer: Path, slug: str = "round", files: list[str] | None = None):
    workspace = consumer / f"ws-{slug}"
    done = run("--stage", consumer / "backend", consumer / "specs", slug, workspace,
               *(files or [FILE, SECOND]))
    return done, workspace


def manifest_of(workspace: Path) -> dict:
    return json.loads((workspace / "manifest.json").read_text(encoding="utf-8"))


def save_return(consumer: Path, slug: str, given: str, front: dict) -> Path:
    path = consumer / "siegard-reconcile" / f"{slug}.returns" / (given.replace("/", "__")
                                                                 + ".yaml")
    path.write_text(yaml.safe_dump(front, sort_keys=False), encoding="utf-8")
    return path


def clean_return(nodes: list[str], **rest) -> dict:
    front = {"read": [{"node": node, "held_at": "the declaration, line 1",
                       "evidence": "export function place() {}"} for node in nodes]}
    front.update(rest)
    return front


PREMISE = {"title": "Hand drift on order placement",
           "summary": "place() gained a line by hand; the human states the behavior is correct.",
           "target": "backend",
           "files": [{"path": FILE, "change": "carries a stray line; behavior unchanged"},
                     {"path": SECOND, "change": "unchanged; reconciled at its current content"}]}


def premised(consumer: Path, front: dict | None = None) -> Path:
    path = consumer / "premise.yaml"
    path.write_text(yaml.safe_dump(front or PREMISE, sort_keys=False), encoding="utf-8")
    return path


def folded(consumer: Path, slug: str = "round", premise: dict | None = None):
    record = consumer / "siegard-reconcile" / f"{slug}.md"
    done = run("--fold", consumer / "backend", consumer / f"ws-{slug}",
               premised(consumer, premise), record)
    return done, record


# ---------------------------------------------------------------- --stage


def test_stage_assigns_the_stale_pairs_and_omits_the_current_unowed_one(consumer):
    done, workspace = staged(consumer)
    assert done.returncode == 0, done.stdout + done.stderr
    manifest = manifest_of(workspace)
    assert manifest["files"] == {FILE: {"nodes": [NODE, OTHER], "also": [],
                                        "pack": str(workspace / "packs"
                                                    / (FILE.replace("/", "__") + ".md"))}}
    assert manifest["all_current"] == [SECOND]
    assert [(entry["node"], entry["file"]) for entry in manifest["omitted"]] == [(NODE, SECOND)]


def test_the_pack_restates_each_node_byte_for_byte_and_names_its_source(consumer):
    _, workspace = staged(consumer)
    pack = Path(manifest_of(workspace)["files"][FILE]["pack"]).read_text(encoding="utf-8")
    for node in (NODE, OTHER):
        source = consumer / "specs" / f"{node}.md"
        assert source.read_text(encoding="utf-8").rstrip("\n") in pack, \
            "a pack is a reading copy; anything less than the node's own text is a summary"
        assert str(source) in pack, "a doubted line needs the one authority to open"
    assert "digest: sha256:" in pack


def test_the_candidate_index_names_every_assigned_node_with_its_files(consumer):
    _, workspace = staged(consumer)
    index = (workspace / "candidates.txt").read_text(encoding="utf-8")
    assert f"{NODE} — bound in this batch to: {FILE}" in index
    assert f"{OTHER} — bound in this batch to: {FILE}" in index


def test_a_taken_slug_is_a_stop_for_the_record_and_the_returns_alike(consumer):
    assert staged(consumer, "taken")[0].returncode == 0
    again, _ = staged(consumer, "taken")
    assert again.returncode == 2
    assert "already exists" in again.stderr


def test_a_file_the_trace_binds_nothing_to_is_staged_under_unbound(consumer):
    loose = consumer / "backend/src/orders/loose.ts"
    loose.write_text("export {}\n", encoding="utf-8")
    done, workspace = staged(consumer, files=[FILE, SECOND, "src/orders/loose.ts"])
    assert done.returncode == 0
    assert manifest_of(workspace)["unbound"] == ["src/orders/loose.ts"]


def test_an_orphaned_binding_is_excluded_from_the_judgment_and_named(consumer):
    (consumer / "specs" / f"{OTHER}.md").unlink()
    done, workspace = staged(consumer)
    assert done.returncode == 1
    assert "not sound" in done.stdout + done.stderr, \
        "the fixture's specification references evidence; deleting it must break soundness " \
        "before staging, which is the situate stop — this test needs a node nothing references"


def test_a_current_pair_with_an_open_owed_finding_is_never_omitted(consumer, tmp_path):
    record = consumer / "siegard-reconcile" / "earlier.md"
    record.parent.mkdir(exist_ok=True)
    front = {"contract_version": "siegard-reconcile/3",
             "title": "Earlier round", "summary": "found against and never cleared.",
             "target": "backend",
             "files": [{"path": SECOND, "change": "judged earlier"}],
             "nodes": [{"node": NODE, "conforms": False,
                        "how": "the file states a cap no node holds",
                        "observed_at": [SECOND]}]}
    record.write_text(f"---\n{yaml.safe_dump(front, sort_keys=False)}---\n", encoding="utf-8")
    done, workspace = staged(consumer)
    assert done.returncode == 0
    manifest = manifest_of(workspace)
    assert manifest["omitted"] == [], \
        "a bind covered the pair's only symptom once; omitting it would do it again"
    assert manifest["files"][SECOND]["nodes"] == [NODE]


def test_an_audit_stages_every_standing_claim_and_omits_nothing(consumer):
    workspace = consumer / "ws-audit"
    done = run("--stage", consumer / "backend", consumer / "specs", "audit", workspace,
               FILE, SECOND, "--audit")
    assert done.returncode == 0, done.stdout + done.stderr
    manifest = manifest_of(workspace)
    assert manifest["audit"] is True
    assert manifest["omitted"] == [], \
        "an audit is the deliberate re-judgment of exactly the pairs the omission guard skips"
    assert manifest["files"][SECOND]["nodes"] == [NODE], \
        "the current, unowed pair is the one an audit exists to hand a judge"
    assert "staged as an audit" in done.stdout


def test_an_audit_stages_no_candidate_tier(consumer):
    """A candidate lets a judge attribute a fact its own nodes do not hold to a node another file
    carries. An audit asks whether one claim stands, and both answers a candidate separates release
    that same claim — binding the node that does hold the fact is a delivery's act, which no
    reconciliation performs. So the tier buys a better sentence about an outcome it cannot change,
    at the price of every candidate node a judge opens to write it, and an audit stages none."""
    workspace = consumer / "ws-audit"
    done = run("--stage", consumer / "backend", consumer / "specs", "audit", workspace,
               FILE, SECOND, "--audit")
    assert done.returncode == 0, done.stdout + done.stderr
    assert not (workspace / "candidates.txt").exists(), \
        "an audit writes no candidate index; there is nothing for a prompt to hand over"
    assert manifest_of(workspace)["candidates"] == {}
    assert "no candidate index" in done.stdout


def test_the_ordinary_route_still_stages_the_candidate_tier(consumer):
    """The opposite reason keeps it here: a misattribution reported as a gap is a false finding, a
    false finding blocks its node, and undoing one costs a fresh delegation over the whole file."""
    _, workspace = staged(consumer)
    assert (workspace / "candidates.txt").is_file()
    assert manifest_of(workspace)["candidates"] != {}


def test_an_audits_record_says_it_was_one(consumer):
    workspace = consumer / "ws-audit"
    run("--stage", consumer / "backend", consumer / "specs", "audit", workspace,
        FILE, SECOND, "--audit")
    save_return(consumer, "audit", FILE, clean_return([NODE, OTHER]))
    save_return(consumer, "audit", SECOND, clean_return([NODE]))
    record = consumer / "siegard-reconcile" / "audit.md"
    done = run("--fold", consumer / "backend", workspace, premised(consumer), record)
    assert done.returncode == 0, done.stdout + done.stderr
    front = yaml.safe_load(record.read_text(encoding="utf-8").split("---")[1])
    assert "Staged as an audit" in front["notes"], \
        "a later reader must know a clean answer here re-read standing claims on purpose"
    assert "pairs_omitted" not in front


def test_audit_is_a_mode_of_stage_alone(consumer):
    done = run("--check", consumer / "backend", "--audit")
    assert done.returncode == 2
    assert "--audit is a mode of --stage" in done.stderr


# ---------------------------------------------------------------- --rank


def test_rank_states_both_accretion_axes_as_counts(consumer):
    done = run("--encodes", "--rank", consumer / "backend")
    assert done.returncode == 0, done.stdout + done.stderr
    assert "files by bindings held" in done.stdout
    assert "nodes by files bound" in done.stdout
    assert f"2  backend/{FILE}" in done.stdout, "place.ts holds two bindings"
    assert f"2  {NODE}" in done.stdout, "the case node is bound to both files"
    assert "3 binding pair(s) over 2 file(s) and 2 node(s)" in done.stdout


def test_rank_holds_the_tail_back_and_all_lists_every_row(consumer):
    spec_root, target = consumer / "specs", consumer / "backend"
    for n in range(20):
        path = f"src/orders/extra{n:02d}.ts"
        (target / path).write_text(f"export const x{n} = {n};\n", encoding="utf-8")
        assert run("--bind", target, spec_root, OTHER, path).returncode == 0
    held = run("--encodes", "--rank", target)
    assert "more; --all lists every one" in held.stdout
    everything = run("--encodes", "--rank", target, "--all")
    assert "more; --all lists every one" not in everything.stdout
    assert "extra19.ts" in everything.stdout


def test_rank_is_a_mode_of_encodes_alone(consumer):
    done = run("--check", consumer / "backend", "--rank")
    assert done.returncode == 2
    assert "--rank is a mode of --encodes" in done.stderr


def test_rank_counts_only_the_named_targets_files(consumer, tmp_path):
    sibling = consumer / "elsewhere"
    (sibling / "src").mkdir(parents=True)
    (sibling / "src/other.ts").write_text("export {}\n", encoding="utf-8")
    assert run("--bind", consumer / "backend", consumer / "specs", OTHER,
               "../elsewhere/src/other.ts").returncode != 0, \
        "a path outside the target cannot be bound, so the fixture stays two-file"
    done = run("--encodes", "--rank", consumer / "backend")
    assert "elsewhere" not in done.stdout


# ---------------------------------------------------------------- --fold


def test_a_clean_return_clears_its_nodes_and_the_how_quotes_the_reading(consumer):
    staged(consumer)
    save_return(consumer, "round", FILE, clean_return([NODE, OTHER]))
    done, record = folded(consumer)
    assert done.returncode == 0, done.stdout + done.stderr
    front = yaml.safe_load(record.read_text(encoding="utf-8").split("---")[1])
    entries = {entry["node"]: entry for entry in front["nodes"]}
    assert entries[NODE]["conforms"] is True
    assert entries[NODE]["encoded_at"] == [FILE]
    assert "export function place() {}" in entries[NODE]["how"]
    assert [(e["node"], e["file"]) for e in front["pairs_omitted"]] == [(NODE, SECOND)]
    assert run("--reconciliation", record).returncode == 0
    assert run("--bind-record", consumer / "backend", consumer / "specs",
               record).returncode == 0


def test_an_unattributed_finding_holds_every_node_of_its_file_and_marks_the_uncontested_collateral(
        consumer):
    staged(consumer)
    front = clean_return([NODE])
    front["read"].append({"node": OTHER, "held_at": "nowhere",
                          "evidence": "nothing in the file states the evidence shape"})
    front["findings"] = [{"where": "the last line", "evidence": "// drift",
                          "cost": "prose carrying a fact no node holds",
                          "kind": "contradicts"}]
    save_return(consumer, "round", FILE, front)
    done, record = folded(consumer)
    assert done.returncode == 0, done.stdout + done.stderr
    entries = {entry["node"]: entry
               for entry in yaml.safe_load(record.read_text(encoding="utf-8")
                                           .split("---")[1])["nodes"]}
    assert entries[NODE]["conforms"] is False and entries[NODE].get("collateral") is True, \
        "nothing contested this node's own substance; the mark is what tells a reader so"
    assert entries[OTHER]["conforms"] is False and "collateral" not in entries[OTHER], \
        "a fact held nowhere is a substantive answer, not collateral"


def test_an_unstated_finding_blocks_no_binding_and_lands_in_its_own_list(consumer):
    """The class this contract exists for. A fact no node holds is the specification's, not the
    pair's: no rebind reaches it, so holding a binding hostage to it waits on a thing that never
    comes. The node its judge read it beside still binds on its own reading."""
    staged(consumer)
    front = clean_return([NODE, OTHER])
    front["findings"] = [{"where": "line 9", "evidence": "const DEFAULT = 'unavailable';",
                          "cost": "which ending an unclassified status resolves to lives only here",
                          "kind": "unstated", "node": NODE}]
    save_return(consumer, "round", FILE, front)
    done, record = folded(consumer)
    assert done.returncode == 0, done.stdout + done.stderr
    front_out = yaml.safe_load(record.read_text(encoding="utf-8").split("---")[1])
    assert [e["node"] for e in front_out["nodes"] if e["conforms"] is False] == [], \
        "an unstated fact is not a contradiction; it blocks no node"
    assert front_out["unstated"] == [{
        "file": FILE, "where": "line 9", "evidence": "const DEFAULT = 'unavailable';",
        "cost": "which ending an unclassified status resolves to lives only here"}], \
        "it lands keyed by file: a fact no node holds has no node to be about"
    assert "Unstated: 1 fact(s)" in front_out["notes"]


def test_an_unstated_finding_is_routed_on_its_word_not_on_naming_a_node(consumer):
    """Its judge named the node it stood beside — where it read the fact, not what the fact
    belongs to. Routing on `node` instead of on `kind` is exactly the fold that put a
    specification gap onto whichever node shared its file."""
    staged(consumer)
    front = clean_return([NODE, OTHER])
    front["findings"] = [{"where": "line 4", "evidence": "throw new NotResolvedError();",
                          "cost": "what the call answers when it cannot resolve is stated nowhere",
                          "kind": "unstated"}]
    save_return(consumer, "round", FILE, front)
    done, record = folded(consumer)
    assert done.returncode == 0, done.stdout + done.stderr
    front_out = yaml.safe_load(record.read_text(encoding="utf-8").split("---")[1])
    assert all(e["conforms"] is True for e in front_out["nodes"]), \
        "naming no node makes it collateral only when it is a contradiction"
    assert len(front_out["unstated"]) == 1


def test_a_finding_naming_a_batch_node_lands_on_it_wherever_its_own_judge_stood(consumer):
    staged(consumer)
    front = clean_return([NODE, OTHER])
    front["findings"] = [{"where": "line 2", "evidence": "// drift",
                          "cost": "states a fact differently from the node",
                          "kind": "contradicts", "node": NODE}]
    save_return(consumer, "round", FILE, front)
    done, record = folded(consumer)
    assert done.returncode == 0
    entries = {entry["node"]: entry
               for entry in yaml.safe_load(record.read_text(encoding="utf-8")
                                           .split("---")[1])["nodes"]}
    assert entries[NODE]["conforms"] is False and "// drift" in entries[NODE]["how"]
    assert entries[OTHER]["conforms"] is True, "a named finding lands on its node and nowhere else"


def test_a_finding_naming_a_node_outside_the_batch_blocks_nothing_and_lands_in_notes(consumer):
    staged(consumer)
    front = clean_return([NODE, OTHER])
    front["findings"] = [{"where": "line 1", "evidence": "export function place() {}",
                          "cost": "a fact a sibling context governs", "kind": "contradicts",
                          "node": "rules/troubleshooting/case-transitions"}]
    save_return(consumer, "round", FILE, front)
    done, record = folded(consumer)
    assert done.returncode == 0
    front = yaml.safe_load(record.read_text(encoding="utf-8").split("---")[1])
    assert all(entry["conforms"] for entry in front["nodes"])
    assert "rules/troubleshooting/case-transitions" in front["notes"]
    assert "owed a route of its own" in front["notes"]


def test_a_fact_that_left_one_of_two_files_blocks_the_node_and_hands_the_release_route(consumer):
    with (consumer / "backend" / SECOND).open("a", encoding="utf-8") as drifted:
        drifted.write("// drift too\n")
    staged(consumer)
    save_return(consumer, "round", FILE, clean_return([NODE, OTHER]))
    second = {"read": [{"node": NODE, "held_at": "nowhere",
                        "evidence": "nothing in the file answers for the case"}]}
    save_return(consumer, "round", SECOND, second)
    done, record = folded(consumer)
    assert done.returncode == 0, done.stdout + done.stderr
    entries = {entry["node"]: entry
               for entry in yaml.safe_load(record.read_text(encoding="utf-8")
                                           .split("---")[1])["nodes"]}
    assert entries[NODE]["conforms"] is False
    assert sorted(entries[NODE]["observed_at"]) == [SECOND, FILE]
    assert "--replace" in entries[NODE]["how"], \
        "the pair that stopped holding the fact has exactly one exit, and the record names it"
    assert "collateral" not in entries[NODE], "a fact that left a file is substance, not collateral"


def test_a_fact_held_nowhere_with_no_finding_binds_nothing_and_says_why(consumer):
    staged(consumer)
    front = clean_return([NODE])
    front["read"].append({"node": OTHER, "held_at": "nowhere",
                          "evidence": "nothing in the file states the evidence shape"})
    save_return(consumer, "round", FILE, front)
    done, record = folded(consumer)
    assert done.returncode == 0
    entries = {entry["node"]: entry
               for entry in yaml.safe_load(record.read_text(encoding="utf-8")
                                           .split("---")[1])["nodes"]}
    assert entries[OTHER]["conforms"] is False
    assert "no named file holds this fact now" in entries[OTHER]["how"], \
        "clearing by silence would rebind a file the judge just read the fact out of"


def test_a_return_short_one_node_is_a_delegation_to_run_again(consumer):
    staged(consumer)
    save_return(consumer, "round", FILE, clean_return([NODE]))
    done, _ = folded(consumer)
    assert done.returncode == 1
    assert OTHER in done.stdout and "run again" in done.stdout, \
        "a fold that filled the gap itself would clear the missing node by silence"


def test_a_return_answering_for_a_node_it_was_never_handed_is_refused(consumer):
    staged(consumer)
    front = clean_return([NODE, OTHER])
    front["read"].append({"node": "rules/troubleshooting/case-transitions",
                          "held_at": "line 1", "evidence": "export function place() {}"})
    save_return(consumer, "round", FILE, front)
    done, _ = folded(consumer)
    assert done.returncode == 1
    assert "never answered for in `read`" in done.stdout


def test_a_missing_return_names_the_delegation_owed(consumer):
    staged(consumer)
    done, _ = folded(consumer)
    assert done.returncode == 1
    assert FILE in done.stdout and "no return at" in done.stdout


def test_a_return_nobody_staged_is_refused(consumer):
    staged(consumer)
    save_return(consumer, "round", FILE, clean_return([NODE, OTHER]))
    save_return(consumer, "round", "src/orders/stray.ts", clean_return([NODE]))
    done, _ = folded(consumer)
    assert done.returncode == 1
    assert "no staged file explains" in done.stdout


def test_the_premise_accounts_for_every_staged_file_and_widens_nothing(consumer):
    staged(consumer)
    save_return(consumer, "round", FILE, clean_return([NODE, OTHER]))
    short = dict(PREMISE, files=[PREMISE["files"][0]])
    done, _ = folded(consumer, premise=short)
    assert done.returncode == 1 and SECOND in done.stdout
    wide = dict(PREMISE, files=PREMISE["files"]
                + [{"path": "src/orders/stray.ts", "change": "never staged"}])
    done, _ = folded(consumer, premise=wide)
    assert done.returncode == 1 and "never staged" in done.stdout


def test_a_premise_naming_a_target_the_project_file_does_not_declare_cannot_fold(consumer):
    """The same mistake `--reconciliation` refuses on the record it would have written, caught
    one step earlier: a bad `target` here never becomes a file on disk that a human then has to
    hand-edit to fix."""
    staged(consumer)
    save_return(consumer, "round", FILE, clean_return([NODE, OTHER]))
    misnamed = dict(PREMISE, target="backend/src")
    done, record = folded(consumer, premise=misnamed)
    assert done.returncode == 1, done.stdout + done.stderr
    assert "backend/src" in done.stdout
    assert "does not declare" in done.stdout
    assert not record.is_file()


CONSTRAINT = "constraints/asynchronous-events"


def registry_deciding(consumer: Path, *constraints: str) -> None:
    """A registry whose `lint` step decides the named constraints, declared for the backend
    target. Read by trace.py defensively — deliver.py is what holds it to its contract."""
    (consumer / "standard.yaml").write_text(yaml.safe_dump({
        "contract_version": "siegard-standard/1", "standard": "backend", "summary": "a test's",
        "rules": [], "commands": [{"step": "lint", "command": "npm run lint",
                                   "timeout_seconds": 60, "decides": list(constraints)}]}),
        encoding="utf-8")
    declared = json.loads((consumer / "siegard.json").read_text(encoding="utf-8"))
    declared["standard"] = {"backend": "standard.yaml"}
    (consumer / "siegard.json").write_text(json.dumps(declared) + "\n", encoding="utf-8")


def test_stage_hands_no_judge_a_pair_a_registry_step_decides(consumer):
    """A constraint the registry's step decides is answered by running that step, not by a
    reading that would re-decide it at a model's recall and at the price of the whole file's
    delegation. The staging separates the pair and hands the caller the run to capture."""
    target = consumer / "backend"
    assert run("--bind", target, consumer / "specs", CONSTRAINT, FILE).returncode == 0
    with (target / FILE).open("a", encoding="utf-8") as drifted:
        drifted.write("// more drift\n")
    registry_deciding(consumer, CONSTRAINT)
    done, workspace = staged(consumer)
    assert done.returncode == 0, done.stdout + done.stderr
    manifest = manifest_of(workspace)
    assert manifest["mechanical"] == [{"node": CONSTRAINT, "file": FILE, "step": "lint",
                                       "decided_by": "step"}]
    assert CONSTRAINT not in manifest["files"][FILE]["nodes"], \
        "a pair a run decides is not also read by a judge"
    assert "decided by a run, not by a judge" in done.stdout
    assert "--run round --cwd" in done.stdout and '--step lint=' in done.stdout


def test_stage_separates_nothing_where_the_project_declares_no_registry(consumer):
    done, workspace = staged(consumer)
    assert done.returncode == 0, done.stdout + done.stderr
    assert manifest_of(workspace)["mechanical"] == []
    assert "decided by a run" not in done.stdout


def test_a_node_whose_text_moved_goes_back_to_a_judge(consumer):
    """A step decided the constraint as the node then stated it, and nothing asked it about the
    sentence that replaced it. The same guard holds for a certified test."""
    target = consumer / "backend"
    assert run("--bind", target, consumer / "specs", CONSTRAINT, FILE).returncode == 0
    with (target / FILE).open("a", encoding="utf-8") as drifted:
        drifted.write("// more drift\n")
    registry_deciding(consumer, CONSTRAINT)
    node_file = consumer / "specs" / f"{CONSTRAINT}.md"
    node_file.write_text(node_file.read_text(encoding="utf-8").replace(
        "## Description", "## Description\n\nA sentence the bind never saw.\n"), encoding="utf-8")
    done, workspace = staged(consumer)
    assert done.returncode == 0, done.stdout + done.stderr
    manifest = manifest_of(workspace)
    assert manifest["mechanical"] == []
    assert CONSTRAINT in manifest["files"][FILE]["nodes"]


# ---------------------------------------------------------------- --certify


PROOF = "tests/place.spec.ts"


def certifying(consumer: Path, *entries: dict) -> Path:
    path = consumer / "certify.yaml"
    path.write_text(yaml.safe_dump(list(entries), sort_keys=False), encoding="utf-8")
    return path


def proof_at(consumer: Path) -> Path:
    path = consumer / "backend" / PROOF
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("it('holds', () => {})\n", encoding="utf-8")
    return path


def save_certification(consumer: Path, slug: str, node: str, front: dict) -> Path:
    path = (consumer / "siegard-reconcile" / f"{slug}.returns"
            / ("certify__" + node.replace("/", "__") + ".yaml"))
    path.write_text(yaml.safe_dump(front, sort_keys=False), encoding="utf-8")
    return path


COVERED = {"certified": [{"node": NODE, "state": "covered", "tests": [{"file": PROOF}]}]}


def test_stage_certify_refuses_what_it_cannot_judge(consumer):
    """A node no named file encodes has no reading here to ride, a proof that is not there is a
    test nobody can open, and a step the registry does not declare is one no run answers for.
    Each is refused before anything is written, and all of them at once."""
    registry_deciding(consumer)
    proof_at(consumer)
    ask = certifying(consumer,
                     {"node": "domain/troubleshooting/hypothesis", "proof": [PROOF], "step": "lint"},
                     {"node": NODE, "proof": ["tests/missing.spec.ts"], "step": "lint"},
                     {"node": OTHER, "proof": [PROOF], "step": "suite"})
    done = run("--stage", consumer / "backend", consumer / "specs", "round", consumer / "ws",
               FILE, SECOND, "--certify", ask)
    assert done.returncode == 2, done.stdout + done.stderr
    assert "domain/troubleshooting/hypothesis is bound to none of the named files" in done.stderr
    assert "tests/missing.spec.ts" in done.stderr and "does not exist" in done.stderr
    assert "declares no step `suite`" in done.stderr
    assert not (consumer / "siegard-reconcile" / "round.returns").exists()


def test_stage_certify_stages_the_pack_and_never_omits_the_certified_nodes_pairs(consumer):
    """The certification rides a fresh reading of the node against the file, so the pair (NODE,
    SECOND) — current, unowed, and omittable on any other staging — is judged here."""
    registry_deciding(consumer)
    proof_at(consumer)
    ask = certifying(consumer, {"node": NODE, "proof": [PROOF], "step": "lint"})
    done = run("--stage", consumer / "backend", consumer / "specs", "round", consumer / "ws",
               FILE, SECOND, "--certify", ask)
    assert done.returncode == 0, done.stdout + done.stderr
    manifest = manifest_of(consumer / "ws")
    assert manifest["omitted"] == []
    assert manifest["files"][SECOND]["nodes"] == [NODE]
    [entry] = manifest["certify"]
    assert entry["node"] == NODE and entry["proof"] == [PROOF] and entry["step"] == "lint"
    assert Path(entry["pack"]).is_file()
    pack = Path(entry["pack"]).read_text(encoding="utf-8")
    assert f"=== {NODE}" in pack and "would the proof below fail" in pack
    assert str((consumer / "backend" / PROOF).resolve()) in pack
    assert "1 certification(s) staged" in done.stdout
    assert "certify__<node with '/' as '__'>.yaml" in done.stdout


def test_certify_is_a_mode_of_stage_alone(consumer):
    ask = certifying(consumer, {"node": NODE, "proof": [PROOF], "step": "lint"})
    for extra in (["--audit"], ["--review"]):
        done = run("--stage", consumer / "backend", consumer / "specs", "round", consumer / "ws",
                   FILE, "--certify", ask, *extra)
        assert done.returncode == 2 and "--certify is a mode of --stage alone" in done.stderr
    done = run("--check", consumer / "backend", "--certify", ask)
    assert done.returncode == 2


def staged_with_certification(consumer: Path):
    registry_deciding(consumer)
    proof_at(consumer)
    ask = certifying(consumer, {"node": NODE, "proof": [PROOF], "step": "lint"})
    done = run("--stage", consumer / "backend", consumer / "specs", "round", consumer / "ws-round",
               FILE, SECOND, "--certify", ask)
    assert done.returncode == 0, done.stdout + done.stderr
    save_return(consumer, "round", FILE, clean_return([NODE, OTHER]))
    save_return(consumer, "round", SECOND, clean_return([NODE]))


def test_fold_writes_a_certification_where_the_auditor_covered_and_the_node_cleared(consumer):
    staged_with_certification(consumer)
    save_certification(consumer, "round", NODE, COVERED)
    done, record = folded(consumer)
    assert done.returncode == 0, done.stdout + done.stderr
    front = yaml.safe_load(record.read_text(encoding="utf-8").split("---\n")[1])
    assert front["contract_version"] == "siegard-reconcile/4"
    [entry] = [e for e in front["nodes"] if e["node"] == NODE]
    assert entry["conforms"] is True
    assert entry["decided_by"] == "test" and entry["step"] == "lint" and entry["proof"] == [PROOF]
    assert f"Certified {NODE} as decided by step `lint`" in front["notes"]
    gate = run("--reconciliation", record)
    assert gate.returncode == 0, gate.stdout + gate.stderr
    bound = run("--bind-record", consumer / "backend", consumer / "specs", record)
    assert bound.returncode == 0, bound.stdout + bound.stderr
    trace_entry = [e for e in json.loads((consumer / "siegard-trace.json")
                                         .read_text(encoding="utf-8"))["bindings"]
                   if e["node"] == NODE][0]
    assert trace_entry["decided_by"] == "test"
    assert [p["path"] for p in trace_entry["proof"]] == [f"backend/{PROOF}"]


def test_the_certification_pins_what_the_auditor_cited_not_what_was_offered(consumer):
    """A human may offer more tests than bear on the fact. Pinning the whole offer would let an
    edit to a file the auditor never cited lapse a certification no reading of it supported."""
    registry_deciding(consumer)
    proof_at(consumer)
    bystander = consumer / "backend" / "tests/bystander.spec.ts"
    bystander.write_text("it('bears on nothing here', () => {})\n", encoding="utf-8")
    ask = certifying(consumer, {"node": NODE, "step": "lint",
                                "proof": [PROOF, "tests/bystander.spec.ts"]})
    assert run("--stage", consumer / "backend", consumer / "specs", "round",
               consumer / "ws-round", FILE, SECOND, "--certify", ask).returncode == 0
    save_return(consumer, "round", FILE, clean_return([NODE, OTHER]))
    save_return(consumer, "round", SECOND, clean_return([NODE]))
    save_certification(consumer, "round", NODE, COVERED)

    done, record = folded(consumer)
    assert done.returncode == 0, done.stdout + done.stderr
    [entry] = [e for e in yaml.safe_load(record.read_text(encoding="utf-8").split("---\n")[1])
               ["nodes"] if e["node"] == NODE]
    assert entry["proof"] == [PROOF], "the offered bystander is not what the auditor certified"

    assert run("--bind-record", consumer / "backend", consumer / "specs",
               record).returncode == 0
    bystander.write_text("it('renamed, and still bears on nothing', () => {})\n",
                         encoding="utf-8")
    check = run("--check", consumer / "backend")
    assert check.returncode == 0, \
        f"an edit to a test the auditor never cited lapsed the certification:\n{check.stdout}"
    assert "no drift" in check.stdout


def test_fold_records_a_refused_certification_as_reading_not_as_absence(consumer):
    """A refusal is said structurally, the way a cleared node's `encoded_at` is. Left as absence
    it would read exactly like a reconciliation that never asked — and the bind would carry a
    standing certification past the judgment that just refused it."""
    staged_with_certification(consumer)
    save_certification(consumer, "round", NODE, {"certified": [
        {"node": NODE, "state": "partial", "tests": [{"file": PROOF}],
         "why": "the refusal half of the fact goes unexercised"}]})
    done, record = folded(consumer)
    assert done.returncode == 0, done.stdout + done.stderr
    front = yaml.safe_load(record.read_text(encoding="utf-8").split("---\n")[1])
    [entry] = [e for e in front["nodes"] if e["node"] == NODE]
    assert entry["conforms"] is True
    assert entry["decided_by"] == "reading"
    assert "step" not in entry and "proof" not in entry
    assert f"Certification of {NODE} did not hold: the auditor answered `partial`" in front["notes"]
    assert "refusal half" in front["notes"]
    assert run("--reconciliation", record).returncode == 0


def test_fold_holds_a_certification_off_a_node_the_judgment_refused(consumer):
    """The auditor may find the test sound while the reading finds the source wrong. Both are
    recorded; the certification is not written, because a test-decided binding rests on a
    reading that cleared the node."""
    staged_with_certification(consumer)
    save_return(consumer, "round", FILE, clean_return([NODE, OTHER], findings=[
        {"where": "line 1", "evidence": "export function place() {}", "kind": "contradicts",
         "cost": "states a cap no node holds", "node": NODE}]))
    save_certification(consumer, "round", NODE, COVERED)
    done, record = folded(consumer)
    assert done.returncode == 0, done.stdout + done.stderr
    front = yaml.safe_load(record.read_text(encoding="utf-8").split("---\n")[1])
    [entry] = [e for e in front["nodes"] if e["node"] == NODE]
    assert entry["conforms"] is False and "decided_by" not in entry
    assert f"Certification of {NODE} held" in front["notes"] and "is not written" in front["notes"]


def test_fold_refuses_a_certification_return_that_is_missing_or_off_its_ask(consumer):
    staged_with_certification(consumer)
    done, _ = folded(consumer)
    assert done.returncode == 1
    assert f"certification of {NODE}: no return at" in done.stdout

    save_certification(consumer, "round", NODE, {"certified": [
        {"node": NODE, "state": "covered", "tests": [{"file": "tests/other.spec.ts"}]}]})
    done, _ = folded(consumer)
    assert done.returncode == 1
    assert "tests/other.spec.ts is not among the proof offered" in done.stdout

    save_certification(consumer, "round", NODE, {"certified": [
        {"node": OTHER, "state": "covered", "tests": [{"file": PROOF}]}]})
    done, _ = folded(consumer)
    assert done.returncode == 1
    assert f"this delegation was handed {NODE} alone" in done.stdout


# ---------------------------------------------------------------- --fold --run


def captured_run(consumer: Path, slug: str = "round", outcome: str = "passed",
                 step: str = "lint", cwd: Path | None = None) -> Path:
    """A run as bin/run.py writes one, under the returns directory where the decision put it."""
    where = consumer / "siegard-reconcile" / f"{slug}.returns" / "run" / slug
    where.mkdir(parents=True, exist_ok=True)
    (where / "run.json").write_text(json.dumps({
        "contract_version": "siegard-run/2", "run": f"run/{slug}",
        "cwd": str((cwd or (consumer / "backend")).resolve()), "timeout_seconds": 60,
        "outcome": outcome, "failed_step": None if outcome == "passed" else step,
        "steps": [{"name": step, "command": "npm run lint", "outcome": outcome,
                   "exit_code": 0 if outcome == "passed" else 1, "output": "lint.log",
                   "started_at": "2026-09-08T10:00:00Z", "ended_at": "2026-09-08T10:00:01Z"}],
        "combined_output": "run.log"}), encoding="utf-8")
    return where


def staged_mechanical(consumer: Path):
    """CONSTRAINT bound to FILE and decided by the registry's `lint` step; NODE and OTHER still
    read by a judge, so one staging carries both tiers."""
    assert run("--bind", consumer / "backend", consumer / "specs", CONSTRAINT,
               FILE).returncode == 0
    with (consumer / "backend" / FILE).open("a", encoding="utf-8") as drifted:
        drifted.write("// more drift\n")
    registry_deciding(consumer, CONSTRAINT)
    done, workspace = staged(consumer)
    assert done.returncode == 0, done.stdout + done.stderr
    save_return(consumer, "round", FILE, clean_return([NODE, OTHER]))
    return workspace


def test_the_fold_answers_the_mechanical_tier_from_the_run(consumer):
    staged_mechanical(consumer)
    where = captured_run(consumer)
    record = consumer / "siegard-reconcile" / "round.md"
    done = run("--fold", consumer / "backend", consumer / "ws-round", premised(consumer),
               record, "--run", where)
    assert done.returncode == 0, done.stdout + done.stderr
    front = yaml.safe_load(record.read_text(encoding="utf-8").split("---\n")[1])
    [entry] = [e for e in front["nodes"] if e["node"] == CONSTRAINT]
    assert entry["conforms"] is True
    assert entry["encoded_at"] == [FILE]
    assert "`lint` step of run/round passed" in entry["how"]
    assert "no judge read this pair" in entry["how"]
    assert "were decided by run/round rather than by a judge" in front["notes"]
    assert run("--reconciliation", record).returncode == 0
    assert run("--bind-record", consumer / "backend", consumer / "specs",
               record).returncode == 0


def test_a_red_step_binds_nothing_and_says_which_step_answered(consumer):
    staged_mechanical(consumer)
    where = captured_run(consumer, outcome="failed")
    record = consumer / "siegard-reconcile" / "round.md"
    done = run("--fold", consumer / "backend", consumer / "ws-round", premised(consumer),
               record, "--run", where)
    assert done.returncode == 0, done.stdout + done.stderr
    front = yaml.safe_load(record.read_text(encoding="utf-8").split("---\n")[1])
    [entry] = [e for e in front["nodes"] if e["node"] == CONSTRAINT]
    assert entry["conforms"] is False
    assert entry["observed_at"] == [FILE]
    assert "did not pass: failed (exit 1)" in entry["how"]
    assert run("--reconciliation", record).returncode == 0


def test_a_mechanical_tier_with_no_run_refuses_and_names_the_step(consumer):
    staged_mechanical(consumer)
    done, _ = folded(consumer)
    assert done.returncode == 1
    assert "1 pair(s) are decided by a run and none was given" in done.stdout
    assert "lint" in done.stdout


def test_a_run_over_another_tree_or_missing_the_step_is_refused(consumer):
    staged_mechanical(consumer)
    record = consumer / "siegard-reconcile" / "round.md"
    elsewhere = captured_run(consumer, slug="round", cwd=consumer)
    done = run("--fold", consumer / "backend", consumer / "ws-round", premised(consumer),
               record, "--run", elsewhere)
    assert done.returncode == 1 and "two runs" in done.stdout
    captured_run(consumer, step="typecheck")
    done = run("--fold", consumer / "backend", consumer / "ws-round", premised(consumer),
               record, "--run", consumer / "siegard-reconcile/round.returns/run/round")
    assert done.returncode == 1 and "holds no step named lint" in done.stdout
    assert not record.exists()


def test_a_run_over_content_that_has_since_moved_is_refused(consumer):
    """The run proved the tree as it stood. Binding what stands now on the strength of it would
    stamp a claim over bytes the run never saw."""
    staged_mechanical(consumer)
    where = captured_run(consumer)
    (consumer / "backend" / FILE).write_text("export function place() { return 2 }\n",
                                             encoding="utf-8")
    done = run("--fold", consumer / "backend", consumer / "ws-round", premised(consumer),
               consumer / "siegard-reconcile" / "round.md", "--run", where)
    assert done.returncode == 1
    assert "changed since the staging" in done.stdout
    assert "a fresh invocation under a new slug" in done.stdout


def test_a_run_nothing_reads_is_refused(consumer):
    staged(consumer)
    save_return(consumer, "round", FILE, clean_return([NODE, OTHER]))
    where = captured_run(consumer)
    done = run("--fold", consumer / "backend", consumer / "ws-round", premised(consumer),
               consumer / "siegard-reconcile" / "round.md", "--run", where)
    assert done.returncode == 2
    assert "no pair of this staging is decided by a run" in done.stderr


def test_run_is_a_mode_of_fold(consumer):
    done = run("--stage", consumer / "backend", consumer / "specs", "x", consumer / "wsx",
               FILE, "--run", consumer / "anywhere")
    assert done.returncode == 2 and "--run is a mode of --fold" in done.stderr


def test_a_file_whose_every_pair_a_run_decides_is_neither_judged_nor_unbound(consumer):
    """It gets no judge and no pack, and the record still accounts for it — through the nodes the
    run answered, never under `unbound`, which would claim the trace binds it nothing."""
    third = "src/orders/ship.ts"
    (consumer / "backend" / third).write_text("export function ship() {}\n", encoding="utf-8")
    assert run("--bind", consumer / "backend", consumer / "specs", CONSTRAINT,
               third).returncode == 0
    (consumer / "backend" / third).write_text("export function ship() { return 1 }\n",
                                              encoding="utf-8")
    registry_deciding(consumer, CONSTRAINT)
    done, workspace = staged(consumer, files=[FILE, SECOND, third])
    assert done.returncode == 0, done.stdout + done.stderr
    manifest = manifest_of(workspace)
    assert third not in manifest["files"] and third not in manifest["unbound"]
    assert manifest["answered_by_run"] == [third]

    save_return(consumer, "round", FILE, clean_return([NODE, OTHER]))
    where = captured_run(consumer)
    premise = dict(PREMISE, files=PREMISE["files"] + [{"path": third, "change": "unchanged"}])
    record = consumer / "siegard-reconcile" / "round.md"
    done = run("--fold", consumer / "backend", workspace, premised(consumer, premise), record,
               "--run", where)
    assert done.returncode == 0, done.stdout + done.stderr
    front = yaml.safe_load(record.read_text(encoding="utf-8").split("---\n")[1])
    assert third in [f["path"] for f in front["files"]]
    assert third not in (front.get("unbound") or [])
    [entry] = [e for e in front["nodes"] if e["node"] == CONSTRAINT]
    assert entry["encoded_at"] == [third]


def test_the_certification_contracts_own_examples_pass_the_gate():
    from jsonschema import Draft202012Validator
    schema = json.loads((REPO / "src/claude/schemas/certification-return.json")
                        .read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    assert schema["examples"]
    for example in schema["examples"]:
        assert [] == [error.message for error in validator.iter_errors(example)]


def test_the_return_contracts_own_examples_pass_the_gate_that_will_judge_real_returns():
    from jsonschema import Draft202012Validator
    schema = json.loads((REPO / "src/claude/schemas/conformance-return.json")
                        .read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    for example in schema["examples"]:
        assert [] == [error.message for error in validator.iter_errors(example)]


# ---------------------------------------------------------------- the omission guard at bind


def test_an_omitted_pair_that_went_stale_before_the_bind_refuses_the_record_whole(consumer):
    staged(consumer)
    save_return(consumer, "round", FILE, clean_return([NODE, OTHER]))
    done, record = folded(consumer)
    assert done.returncode == 0
    with (consumer / "backend" / SECOND).open("a", encoding="utf-8") as moved:
        moved.write("// late edit\n")
    done = run("--bind-record", consumer / "backend", consumer / "specs", record)
    assert done.returncode == 1
    assert "stale" in done.stdout and "owed a judge" in done.stdout
    assert "nothing was bound" in done.stdout


def test_a_record_omitting_a_pair_it_never_declared_is_still_refused(consumer):
    staged(consumer)
    save_return(consumer, "round", FILE, clean_return([NODE, OTHER]))
    done, record = folded(consumer)
    assert done.returncode == 0
    text = record.read_text(encoding="utf-8")
    front = yaml.safe_load(text.split("---")[1])
    del front["pairs_omitted"]
    record.write_text(f"---\n{yaml.safe_dump(front, sort_keys=False)}---\n", encoding="utf-8")
    done = run("--bind-record", consumer / "backend", consumer / "specs", record)
    assert done.returncode == 1
    assert "answers for the pair nowhere" in done.stdout, \
        "an omission is said under pairs_omitted or the strict rule stands; silence is neither"


def test_a_pair_both_answered_and_omitted_is_a_contradiction_the_accounting_refuses(consumer):
    staged(consumer)
    save_return(consumer, "round", FILE, clean_return([NODE, OTHER]))
    done, record = folded(consumer)
    assert done.returncode == 0
    front = yaml.safe_load(record.read_text(encoding="utf-8").split("---")[1])
    front["pairs_omitted"].append({"node": NODE, "file": FILE,
                                   "reason": "also answered above"})
    record.write_text(f"---\n{yaml.safe_dump(front, sort_keys=False)}---\n", encoding="utf-8")
    done = run("--reconciliation", record)
    assert done.returncode == 1
    assert "judged or omitted, never both" in done.stdout


def test_a_v1_record_in_the_corpus_is_still_read_by_owed(consumer):
    record = consumer / "siegard-reconcile" / "old-round.md"
    record.parent.mkdir(exist_ok=True)
    front = {"contract_version": "siegard-reconcile/1",
             "title": "An earlier era", "summary": "written before pairs could be omitted.",
             "target": "backend",
             "files": [{"path": FILE, "change": "judged under the earlier contract"}],
             "nodes": [{"node": OTHER, "conforms": False,
                        "how": "found against and never cleared",
                        "observed_at": [FILE]}]}
    record.write_text(f"---\n{yaml.safe_dump(front, sort_keys=False)}---\n", encoding="utf-8")
    done = run("--owed", consumer / "backend")
    assert done.returncode == 1
    assert "old-round.md" in done.stdout, \
        "the corpus is append-only; a version bump that silenced old records would erase the " \
        "only home their findings have"


# ---------------------------------------------------------------- --review


def review_staged(consumer: Path, *extra, slug: str = "first-review", files=None):
    workspace = consumer / f"ws-{slug}"
    done = run("--stage", consumer / "backend", consumer / "specs", slug, workspace,
               *(files or [FILE, SECOND]), "--review", *extra)
    return done, workspace


def test_a_review_stages_every_pair_and_keeps_the_candidate_tier(consumer):
    """A delivery's own bind stamped its nodes over these exact bytes, so the omission guard would
    hand a review's judge every binding except the ones the review exists to re-read. And a
    misattribution here is a false finding against a collateral node the delivery never claimed,
    so the tier an audit drops stays."""
    done, workspace = review_staged(consumer)
    assert done.returncode == 0, done.stdout + done.stderr
    manifest = manifest_of(workspace)
    assert manifest["review"] is True and manifest["audit"] is False
    assert manifest["omitted"] == []
    assert manifest["files"][SECOND]["nodes"] == [NODE], \
        "the pair the delivery's own bind left current is exactly what a review re-reads"
    assert (workspace / "candidates.txt").is_file()
    assert manifest["candidates"] != {}
    assert "staged by a review" in done.stdout


def test_the_plans_nodes_are_read_on_every_file_and_bound_from_nowhere(consumer):
    """The plan's node goes into every pack and every return answers for it, so a fact the delivery
    wrote against a node its record never bound is still read against that node. It is never
    bound: a binding the review wrote would be a claim no implementation record made."""
    third = "domain/troubleshooting/hypothesis"
    done, workspace = review_staged(consumer, "--node", third)
    assert done.returncode == 0, done.stdout + done.stderr
    manifest = manifest_of(workspace)
    assert manifest["also"] == [third]
    for given in (FILE, SECOND):
        assert manifest["files"][given]["also"] == [third]
        assert third not in manifest["files"][given]["nodes"]
        assert f"=== {third}" in Path(manifest["files"][given]["pack"]).read_text(encoding="utf-8")
    assert third not in manifest["candidates"], \
        "a node every judge already holds is not a candidate anyone needs to open"
    save_return(consumer, "first-review", FILE, clean_return([NODE, OTHER, third]))
    save_return(consumer, "first-review", SECOND, clean_return([NODE, third]))
    record = consumer / "siegard-reconcile" / "first-review.md"
    done = run("--fold", consumer / "backend", workspace, premised(consumer), record)
    assert done.returncode == 0, done.stdout + done.stderr
    front = yaml.safe_load(record.read_text(encoding="utf-8").split("---")[1])
    assert third not in {entry["node"] for entry in front["nodes"]}
    assert "Staged by a review" in front["notes"] and third in front["notes"]
    assert run("--bind-record", consumer / "backend", consumer / "specs",
               record).returncode == 0
    trace_now = json.loads((consumer / "siegard-trace.json").read_text(encoding="utf-8"))
    assert third not in {entry["node"] for entry in trace_now["bindings"]}
    assert run("--check", consumer / "backend").stdout.count("without a rebind") == 0, \
        "the drifted file's collateral binding was restamped by the review's own bind"


def test_a_return_that_skips_a_plan_node_is_a_delegation_to_run_again(consumer):
    third = "domain/troubleshooting/hypothesis"
    _, workspace = review_staged(consumer, "--node", third)
    save_return(consumer, "first-review", FILE, clean_return([NODE, OTHER]))
    save_return(consumer, "first-review", SECOND, clean_return([NODE, third]))
    record = consumer / "siegard-reconcile" / "first-review.md"
    done = run("--fold", consumer / "backend", workspace, premised(consumer), record)
    assert done.returncode == 1
    assert f"no entry for {third}" in done.stdout


def test_a_file_the_trace_binds_nothing_to_is_still_judged_over_the_plans_nodes(consumer):
    """Outside a review an untraced file is reported and skipped. A review reads it: the file is
    part of the change, and the plan's nodes are what it was written against. Being judged and
    being unbound are two facts, and the file carries both — the record owes `unbound` for every
    named file no node accounts for, and a staging that dropped the file from `unbound` because
    a judge read it would compose a record its own contract refuses."""
    third = "domain/troubleshooting/hypothesis"
    untraced = "src/orders/new.ts"
    (consumer / "backend" / untraced).write_text("export const x = 1;\n", encoding="utf-8")
    done, workspace = review_staged(consumer, "--node", third, files=[FILE, untraced])
    assert done.returncode == 0, done.stdout + done.stderr
    manifest = manifest_of(workspace)
    assert manifest["unbound"] == [untraced]
    assert manifest["files"][untraced] == {"nodes": [], "also": [third],
                                           "pack": manifest["files"][untraced]["pack"]}
    assert "1 file(s) the trace binds nothing to, 1 of them judged over the plan's nodes alone" \
        in done.stdout
    save_return(consumer, "first-review", FILE, clean_return([NODE, OTHER, third]))
    save_return(consumer, "first-review", untraced, clean_return(
        [third], findings=[{"node": NODE, "kind": "contradicts", "where": "line 1",
                            "evidence": "export const x = 1;", "cost": "the case is misnamed"}]))
    premise = dict(PREMISE, files=[PREMISE["files"][0],
                                   {"path": untraced, "change": "new, written by the delivery"}])
    record = consumer / "siegard-reconcile" / "first-review.md"
    done = run("--fold", consumer / "backend", workspace, premised(consumer, premise), record)
    assert done.returncode == 0, done.stdout + done.stderr
    front = yaml.safe_load(record.read_text(encoding="utf-8").split("---")[1])
    assert front["unbound"] == [untraced]
    assert {entry["path"] for entry in front["files"]} == {FILE, untraced}
    case = next(entry for entry in front["nodes"] if entry["node"] == NODE)
    assert case["conforms"] is False and untraced in case["how"], \
        "a finding the untraced file's judge raised against a batch node lands on that node"
    assert case["observed_at"] == [FILE], "and the untraced file is bound from nowhere"
    assert run("--reconciliation", record).returncode == 0
    _, workspace = review_staged(consumer, slug="no-plan-nodes", files=[FILE, untraced])
    assert manifest_of(workspace)["unbound"] == [untraced], \
        "with nothing to read it against, the untraced file is reported as ever"


def test_a_plan_node_the_specification_does_not_hold_is_refused(consumer):
    done, _ = review_staged(consumer, "--node", "domain/troubleshooting/absent")
    assert done.returncode == 2
    assert "holds no node domain/troubleshooting/absent" in done.stderr


def test_review_and_node_are_modes_of_stage_and_exclude_audit(consumer):
    done = run("--check", consumer / "backend", "--review")
    assert done.returncode == 2 and "--review is a mode of --stage" in done.stderr
    done, _ = staged(consumer, slug="plain-with-node")
    done = run("--stage", consumer / "backend", consumer / "specs", "with-node",
               consumer / "ws-with-node", FILE, "--node", NODE)
    assert done.returncode == 2 and "--node is a mode of --stage --review" in done.stderr
    done = run("--stage", consumer / "backend", consumer / "specs", "both",
               consumer / "ws-both", FILE, "--review", "--audit")
    assert done.returncode == 2 and "two stagings" in done.stderr
