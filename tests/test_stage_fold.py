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
    assert manifest["files"] == {FILE: {"nodes": [NODE, OTHER],
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
    front = {"contract_version": "siegard-reconcile/2",
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
                          "cost": "prose carrying a fact no node holds"}]
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


def test_a_finding_naming_a_batch_node_lands_on_it_wherever_its_own_judge_stood(consumer):
    staged(consumer)
    front = clean_return([NODE, OTHER])
    front["findings"] = [{"where": "line 2", "evidence": "// drift",
                          "cost": "states a fact differently from the node",
                          "node": NODE}]
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
                          "cost": "a fact a sibling context governs",
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
