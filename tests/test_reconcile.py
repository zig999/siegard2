"""The reconciliation record: the justification a bind gets when no delivery wrote the source.

Two halves are held here, and the second is the one that carries the risk. `--reconciliation`
decides whether a record holds — the contract, and then whether its own paths add up, which the
schema cannot state because it is a relation between three lists. The rest holds the join to
`--bind-record`: a node the judgment refused carries no `encoded_at`, so the binding form cannot
reach it however anyone invokes it. That is the whole guarantee this file class exists to give, and
it is structural rather than written down in a prompt — which is exactly why it is testable.

The other half of that join is the receipt. Binding is per node because the judgment is, so a record
carrying a finding writes the rest and stops; what the bind owes then is to say which nodes it did
not write, or a partial reconciliation prints the same shape as a complete one.
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
    """A consumer repository shaped the way trace.py's own suite shapes one: a git toplevel with
    the software under `backend/` and the specification beside it."""
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True, capture_output=True)
    spec_root = tmp_path / "specs"
    shutil.copytree(FIXTURE, spec_root)
    shutil.rmtree(spec_root / "projections", ignore_errors=True)
    target = tmp_path / "backend"
    (target / "src/orders").mkdir(parents=True)
    (target / FILE).write_text("export function place() {}\n", encoding="utf-8")
    (target / SECOND).write_text("export function bill() {}\n", encoding="utf-8")
    (tmp_path / "siegard-reconcile").mkdir()
    return tmp_path


def record_of(nodes: list[dict], files: list[dict] | None = None, **rest) -> dict:
    front = {
        "contract_version": "siegard-reconcile/7",
        "title": "Hand correction to order placement",
        "summary": "place() answered with the row; corrected by hand and confirmed correct.",
        "target": "backend",
        "files": files if files is not None else [
            {"path": FILE, "change": "answers with the persisted order_number"}],
        "nodes": nodes,
    }
    front.update(rest)
    return front


@pytest.fixture
def write_record(consumer: Path):
    def put(front: dict, slug: str = "order-fix", where: str = "siegard-reconcile") -> Path:
        home = consumer / where
        home.mkdir(parents=True, exist_ok=True)
        path = home / f"{slug}.md"
        text = yaml.safe_dump(front, sort_keys=False, allow_unicode=True)
        path.write_text(f"---\n{text}---\n\n## Notes\nNone.\n", encoding="utf-8")
        return path
    return put


CLEARED = {"node": NODE, "conforms": True,
           "how": "`return persisted.order_number` is what the entry point now answers with",
           "encoded_at": [FILE]}
REFUSED = {"node": NODE, "conforms": False,
           "how": "the source states `if (order.invoices.length >= 1)`, which no node holds",
           "observed_at": [FILE]}


# ------------------------------------------------------------------ the contract holds


def test_the_contracts_own_examples_pass_the_gate_that_will_judge_real_records(write_record):
    """An example that its own validator refuses teaches the wrong shape to every reader who
    copies it, and the contract is the one place a reader looks first."""
    schema = json.loads(
        (REPO / "src/claude/schemas/reconciliation.json").read_text(encoding="utf-8"))
    assert schema["examples"], "the contract demonstrates nothing"
    for example in schema["examples"]:
        done = run("--reconciliation", write_record(example, slug=example["title"][:20].lower()
                                                    .replace(" ", "-")))
        assert done.returncode == 0, done.stdout + done.stderr


def test_the_contract_demonstrates_every_outcome():
    """One example each way — cleared, refused, cleared with a certification, and cleared with a
    certification refused and its remainder named — because the four differ by which fields they
    carry and a contract showing only the cleared shape teaches that the others are variations on
    it."""
    schema = json.loads(
        (REPO / "src/claude/schemas/reconciliation.json").read_text(encoding="utf-8"))
    entries = [entry for example in schema["examples"] for entry in example["nodes"]]
    assert sorted(entry["conforms"] for entry in entries) == [False, True, True, True]
    certified = [entry for entry in entries if entry.get("decided_by") == "test"]
    assert len(certified) == 1 and certified[0]["conforms"] is True
    refused = [entry for entry in entries if entry.get("decided_by") == "reading"]
    assert len(refused) == 1 and refused[0]["conforms"] is True
    assert refused[0]["remainder"] == "testable" and refused[0]["remainder_why"]


# ------------------------------------------------------------------ certification


PROOF = "tests/orders/place.spec.ts"
CERTIFIED = dict(CLEARED, decided_by="test", step="test", proof=[PROOF])


def proof_at(consumer: Path, text: str = "it('answers the order_number', () => {})\n") -> Path:
    path = consumer / "backend" / PROOF
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def test_a_certified_node_holds_and_the_gate_says_so(write_record):
    done = run("--reconciliation", write_record(record_of([CERTIFIED])))
    assert done.returncode == 0, done.stdout + done.stderr
    assert "1 node(s) certified as decided by a test" in done.stdout
    assert f"{NODE} by step `test` over {PROOF}" in done.stdout


def test_a_certification_cannot_ride_a_node_the_judgment_refused(write_record):
    """A test-decided binding rests on a reading that cleared the node once; a node the judgment
    refused has none to rest on, and the contract says so before the fold can."""
    done = run("--reconciliation",
               write_record(record_of([dict(REFUSED, decided_by="test", step="test",
                                            proof=[PROOF])])))
    assert done.returncode == 1, done.stdout + done.stderr
    assert "binds nothing until" in done.stdout


def test_a_certification_names_its_step_and_proof_or_is_not_one(write_record):
    without_step = dict(CLEARED, decided_by="test", proof=[PROOF])
    done = run("--reconciliation", write_record(record_of([without_step])))
    assert done.returncode == 1, done.stdout + done.stderr
    step_without_claim = dict(CLEARED, step="test")
    done = run("--reconciliation", write_record(record_of([step_without_claim])))
    assert done.returncode == 1, done.stdout + done.stderr


def test_bind_record_writes_a_certified_binding_and_pins_the_proof(consumer, write_record):
    proof_at(consumer)
    record = write_record(record_of([CERTIFIED]))
    done = run("--bind-record", consumer / "backend", consumer / "specs", record)
    assert done.returncode == 0, done.stdout + done.stderr
    assert f"{NODE} is decided by a test from here: step `test` over backend/{PROOF}" in done.stdout
    declared = json.loads((consumer / "siegard-trace.json").read_text(encoding="utf-8"))
    entry = declared["bindings"][0]
    assert entry["decided_by"] == "test"
    assert entry["step"] == "test"
    assert [p["path"] for p in entry["proof"]] == [f"backend/{PROOF}"]
    assert entry["proof"][0]["digest"].startswith("sha256:")
    assert [f["path"] for f in entry["files"]] == [f"backend/{FILE}"], \
        "the files a node encodes stay the source's; a test decides whether, never where"
    sound = run(consumer / "backend")
    assert "1 binding(s), 1 of them decided by a certified test" in sound.stdout


def test_a_certified_proof_that_is_missing_refuses_the_record_whole(consumer, write_record):
    record = write_record(record_of([CERTIFIED]))
    done = run("--bind-record", consumer / "backend", consumer / "specs", record)
    assert done.returncode == 1, done.stdout + done.stderr
    assert "proof" in done.stdout and "does not exist" in done.stdout
    assert not (consumer / "siegard-trace.json").exists()


def test_a_rebind_carries_a_certification_while_the_proof_stands(consumer, write_record):
    """A bind over a file the node encodes is not a judgment about the test that decides the
    node, so the certification rides through — the entry is rewritten whole, and dropping it
    with the entry would lose a claim nobody withdrew."""
    proof_at(consumer)
    run("--bind-record", consumer / "backend", consumer / "specs", write_record(record_of([CERTIFIED])))
    done = run("--bind", consumer / "backend", consumer / "specs", NODE, FILE)
    assert done.returncode == 0, done.stdout + done.stderr
    entry = json.loads((consumer / "siegard-trace.json").read_text(encoding="utf-8"))["bindings"][0]
    assert entry["decided_by"] == "test" and entry["step"] == "test"


def test_a_rebind_carries_a_certification_whose_proof_changed_and_says_so(consumer, write_record):
    """A test whose text changed is what `--check` reports under `proof`, and what every reader of
    a certification recomputes before trusting it. Dropping the certification instead would throw
    away the one record of which test decided the node — silently, since the entry written
    afterwards reads exactly like one never certified. Kept, the loss is a finding with a route."""
    proof_at(consumer)
    run("--bind-record", consumer / "backend", consumer / "specs", write_record(record_of([CERTIFIED])))
    proof_at(consumer, "it('asserts something else', () => {})\n")
    done = run("--bind", consumer / "backend", consumer / "specs", NODE, FILE)
    assert done.returncode == 0, done.stdout + done.stderr
    assert f"{NODE} is decided by a test whose text moved" in done.stdout
    assert "carried as it was" in done.stdout and "`proof`" in done.stdout
    entry = json.loads((consumer / "siegard-trace.json").read_text(encoding="utf-8"))["bindings"][0]
    assert entry["decided_by"] == "test" and entry["step"] == "test"
    assert [p["path"] for p in entry["proof"]] == [f"backend/{PROOF}"]

    checked = run("--check", consumer / "backend")
    assert checked.returncode == 1
    assert "1 proof:" in checked.stdout, checked.stdout
    assert "whose text changed since it was certified" in checked.stdout


def test_a_carried_certification_over_moved_text_is_not_live_for_any_reader(consumer, write_record):
    """Carried is not trusted: `test_decided` recomputes the proof's digests, so a certification
    over moved text decides nothing and the next judgment re-reads the node as uncertified."""
    proof_at(consumer)
    run("--bind-record", consumer / "backend", consumer / "specs", write_record(record_of([CERTIFIED])))
    proof_at(consumer, "it('asserts something else', () => {})\n")
    run("--bind", consumer / "backend", consumer / "specs", NODE, FILE)
    declared = json.loads((consumer / "siegard-trace.json").read_text(encoding="utf-8"))
    assert trace.test_decided(declared, consumer, "backend") == {}


def test_a_record_that_refused_the_certification_releases_the_standing_one(consumer, write_record):
    """The auditor may find, over a test whose text never moved, that it cannot fail. Carrying the
    certification then would leave the trace deciding by a test a judgment has just refused, while
    the record's own notes say the node is decided by reading."""
    proof_at(consumer)
    run("--bind-record", consumer / "backend", consumer / "specs",
        write_record(record_of([CERTIFIED]), slug="first"))
    refused = write_record(record_of([dict(CLEARED, decided_by="reading")]), slug="second")
    done = run("--bind-record", consumer / "backend", consumer / "specs", refused)
    assert done.returncode == 0, done.stdout + done.stderr
    assert f"{NODE} is decided by reading from here" in done.stdout
    entry = json.loads((consumer / "siegard-trace.json").read_text(encoding="utf-8"))["bindings"][0]
    assert "decided_by" not in entry and "proof" not in entry and "step" not in entry
    assert run("--check", consumer / "backend").returncode == 0, \
        "releasing a certification is not itself drift"


def test_a_record_that_never_asked_carries_the_certification_and_says_nothing(consumer,
                                                                              write_record):
    """Absence is not refusal: a reconciliation that did not ask about the test has no business
    releasing what stands, and a receipt for a release that did not happen is noise."""
    proof_at(consumer)
    run("--bind-record", consumer / "backend", consumer / "specs",
        write_record(record_of([CERTIFIED]), slug="first"))
    done = run("--bind-record", consumer / "backend", consumer / "specs",
               write_record(record_of([CLEARED]), slug="second"))
    assert done.returncode == 0, done.stdout + done.stderr
    assert "decided by reading from here" not in done.stdout
    entry = json.loads((consumer / "siegard-trace.json").read_text(encoding="utf-8"))["bindings"][0]
    assert entry["decided_by"] == "test"


def test_a_refusal_over_a_node_that_was_never_certified_prints_no_receipt(consumer, write_record):
    proof_at(consumer)
    done = run("--bind-record", consumer / "backend", consumer / "specs",
               write_record(record_of([dict(CLEARED, decided_by="reading")])))
    assert done.returncode == 0, done.stdout + done.stderr
    assert "decided by reading from here" not in done.stdout


def test_encodes_names_a_file_the_trace_pins_as_a_proof(consumer, write_record):
    """A test the trace pins as some node's proof is named by path in the trace, so answering that
    the trace binds nothing to it is false. It is said apart from a binding, because a proof
    answers whether the fact holds and never where it lives."""
    proof_at(consumer)
    run("--bind-record", consumer / "backend", consumer / "specs", write_record(record_of([CERTIFIED])))
    done = run("--encodes", consumer / "backend", PROOF)
    assert done.returncode == 0, done.stdout + done.stderr
    assert "the trace binds nothing to this file" not in done.stdout
    assert "pins it as the proof of 1 binding(s)" in done.stdout
    assert f"proof of {NODE} — certified over this text" in done.stdout

    proof_at(consumer, "it('asserts something else', () => {})\n")
    later = run("--encodes", consumer / "backend", PROOF)
    assert f"proof of {NODE} — the test changed since it was certified" in later.stdout


def test_a_lapsed_certification_is_reported_as_lapsed_by_every_form(consumer, write_record):
    """`--check` says the certification lapsed and that the binding is decided by reading until
    it is certified again. Any other form still calling it live would tell a reader, in the same
    breath, that a run answers for the pair — and acting on that skips the reading."""
    proof_at(consumer)
    run("--bind-record", consumer / "backend", consumer / "specs", write_record(record_of([CERTIFIED])))
    proof_at(consumer, "it('asserts something else', () => {})\n")
    (consumer / "backend" / FILE).write_text("export function place() { return 1 }\n",
                                             encoding="utf-8")

    drift = run("--check", consumer / "backend")
    assert "1 proof:" in drift.stdout
    assert "sit on a binding a certified test decides" not in drift.stdout, \
        "one report cannot say the certification lapsed and that its step answers for the pair"

    assert "a certified test decides it" not in run("--encodes", consumer / "backend", FILE).stdout
    assert "by a certified test" not in run("--encodes", "--rank", consumer / "backend").stdout
    assert "decided by a certified test" not in run(consumer / "backend").stdout


def with_registry(consumer: Path, *steps: str) -> None:
    """A project file and a registry declaring the named steps, so the step half of a
    certification has something to be held against."""
    (consumer / "standard.yaml").write_text(yaml.safe_dump({
        "contract_version": "siegard-standard/1", "standard": "backend", "summary": "a test's",
        "rules": [], "commands": [{"step": s, "command": f"npm run {s}", "timeout_seconds": 60}
                                  for s in steps]}), encoding="utf-8")
    (consumer / "siegard.json").write_text(json.dumps(
        {"specification_root": "specs", "targets": {"backend": "backend"},
         "standard": {"backend": "standard.yaml"}}) + "\n", encoding="utf-8")


def test_a_certification_naming_a_step_the_registry_does_not_declare_is_refused(consumer,
                                                                                write_record):
    """Symmetric with `--stage --certify`, which refuses the same string. A binding naming a step
    nothing can run would be read by every later form as decided by a run that cannot happen."""
    proof_at(consumer)
    with_registry(consumer, "verify")
    done = run("--bind-record", consumer / "backend", consumer / "specs",
               write_record(record_of([CERTIFIED])))
    assert done.returncode == 1, done.stdout + done.stderr
    assert "does not declare" in done.stdout and "verify" in done.stdout
    assert not (consumer / "siegard-trace.json").exists()


def test_a_certification_lapses_when_the_registry_drops_its_step(consumer, write_record):
    """The step is a frozen string in the trace, and a registry may rename it. Left unchecked the
    binding reads as decided by a run nothing can perform — and a reconciliation would stage it in
    a mechanical tier with no runnable step, which is the one state this route has no exit from."""
    proof_at(consumer)
    with_registry(consumer, "test")
    assert run("--bind-record", consumer / "backend", consumer / "specs",
               write_record(record_of([CERTIFIED]))).returncode == 0
    assert "1 of them decided by a certified test" in run(consumer / "backend").stdout

    with_registry(consumer, "verify")
    drift = run("--check", consumer / "backend")
    assert drift.returncode == 1, drift.stdout + drift.stderr
    assert "the project's registry no longer declares" in drift.stdout
    assert "1 proof:" in drift.stdout
    assert "decided by a certified test" not in run(consumer / "backend").stdout
    assert "a certified test decides it" not in run("--encodes", consumer / "backend",
                                                    FILE).stdout


def test_check_reports_a_changed_proof_under_its_own_class(consumer, write_record):
    """The proof is pinned the way the files are and moves the same way; what differs is the
    remedy — a fresh certification, never a rebind of the file — so the class is its own, and the
    file's own `code` class is untouched by it."""
    proof_at(consumer)
    run("--bind-record", consumer / "backend", consumer / "specs", write_record(record_of([CERTIFIED])))
    clean = run("--check", consumer / "backend")
    assert clean.returncode == 0, clean.stdout + clean.stderr
    proof_at(consumer, "it('asserts something else', () => {})\n")
    done = run("--check", consumer / "backend")
    assert done.returncode == 1, done.stdout + done.stderr
    assert f"{NODE}: certified over backend/{PROOF}, whose text changed since" in done.stdout
    assert "1 proof:" in done.stdout
    assert "0 code" in done.stdout


def test_a_code_drift_on_a_certified_binding_carries_the_receipt(consumer, write_record):
    proof_at(consumer)
    run("--bind-record", consumer / "backend", consumer / "specs", write_record(record_of([CERTIFIED])))
    (consumer / "backend" / FILE).write_text("export function place() { return 1 }\n",
                                             encoding="utf-8")
    done = run("--check", consumer / "backend")
    assert done.returncode == 1, done.stdout + done.stderr
    assert "sit on a binding a certified test decides" in done.stdout
    assert f"{NODE} over backend/{FILE} (step `test`)" in done.stdout
    marked = run("--encodes", consumer / "backend", FILE)
    assert f"{NODE} — stale: the file changed without a rebind; a certified test decides it " \
           f"(step `test`)" in marked.stdout


def test_a_sound_record_holds_and_says_what_it_will_bind(write_record):
    done = run("--reconciliation", write_record(record_of([CLEARED])))
    assert done.returncode == 0, done.stdout + done.stderr
    assert "1 node(s) the judgment cleared" in done.stdout


def test_a_record_naming_a_target_the_project_file_does_not_declare_cannot_hold(
        consumer, write_record):
    """The same fact `--owed` reports later, caught at the gate instead: a record whose `target`
    is not a key `siegard.json` declares is one `--owed` can never resolve, and left to land it
    reads that way forever. Refusing it here is where a human still edits the field."""
    (consumer / "siegard.json").write_text(
        json.dumps({"specification_root": "specs", "targets": {"backend": "backend"}}, indent=2),
        encoding="utf-8")
    record = write_record(record_of([CLEARED], target="backend/app"))

    done = run("--reconciliation", record)
    assert done.returncode == 1, done.stdout + done.stderr
    assert "backend/app" in done.stdout
    assert "does not declare" in done.stdout


def test_a_record_naming_its_target_holds_with_no_project_file_to_check_it_against(write_record):
    """A `target` naming nothing `siegard.json` declares and no `siegard.json` to declare it are
    different facts; the gate has nothing to compare against in the second and holds the record
    rather than reading absence as a mismatch."""
    done = run("--reconciliation", write_record(record_of([CLEARED])))
    assert done.returncode == 0, done.stdout + done.stderr


def test_a_record_filed_anywhere_else_cannot_run(write_record):
    """The location is contract, not convention: a justification the next reader cannot find is a
    binding resting on nothing, and the trace outlives every other root."""
    done = run("--reconciliation", write_record(record_of([CLEARED]), where="notes"))
    assert done.returncode == 2
    assert "siegard-reconcile/" in done.stderr


def test_a_record_of_another_contract_version_is_refused(write_record):
    front = record_of([CLEARED])
    front["contract_version"] = "siegard-reconcile/1"
    done = run("--reconciliation", write_record(front))
    assert done.returncode == 1
    assert "contract_version" in done.stdout


def test_a_file_with_no_frontmatter_is_not_a_record(consumer):
    path = consumer / "siegard-reconcile" / "loose.md"
    path.write_text("Some prose about a fix.\n", encoding="utf-8")
    done = run("--reconciliation", path)
    assert done.returncode == 2
    assert "frontmatter" in done.stderr


# ------------------------------------------------- the judgment's answer is the field name


def test_a_refused_node_may_not_carry_the_field_that_binds(write_record):
    """The one guard the whole route rests on. A node the conformance pass did not clear cannot
    declare where it is encoded, so `--bind-record` — which reads that field and nothing else —
    has nothing to reach. A prose rule asking a skill not to bind would be a rule the next
    invocation could simply not follow."""
    front = record_of([{**REFUSED, "encoded_at": [FILE]}])
    done = run("--reconciliation", write_record(front))
    assert done.returncode == 1
    assert "encoded_at" in done.stdout


def test_a_cleared_node_must_say_where_it_is_encoded(write_record):
    front = record_of([{"node": NODE, "conforms": True, "how": "unchanged in substance",
                        "observed_at": [FILE]}])
    done = run("--reconciliation", write_record(front))
    assert done.returncode == 1
    assert "encoded_at" in done.stdout


def test_a_record_the_judgment_refused_holds_and_binds_nothing(consumer, write_record):
    """Refused is not invalid. The record of a reconciliation that stopped is the one worth
    keeping most, and it validates so that it can be written and committed."""
    record = write_record(record_of([REFUSED]))
    done = run("--reconciliation", record)
    assert done.returncode == 0, done.stdout + done.stderr
    assert "0 node(s) the judgment cleared" in done.stdout

    bound = run("--bind-record", consumer / "backend", consumer / "specs", record)
    assert bound.returncode == 0, bound.stdout + bound.stderr
    assert "names no node with `encoded_at`" in bound.stdout
    assert not (consumer / "siegard-trace.json").exists()


def test_the_cleared_nodes_of_a_record_are_what_lands_in_the_trace(consumer, write_record):
    record = write_record(record_of(
        [CLEARED, {"node": OTHER, "conforms": False,
                   "how": "the second file states a threshold no node holds",
                   "observed_at": [SECOND]}],
        files=[{"path": FILE, "change": "answers with the persisted order_number"},
               {"path": SECOND, "change": "refuses a second bill"}]))
    assert run("--reconciliation", record).returncode == 0

    bound = run("--bind-record", consumer / "backend", consumer / "specs", record)
    assert bound.returncode == 0, bound.stdout + bound.stderr
    declared = json.loads((consumer / "siegard-trace.json").read_text(encoding="utf-8"))
    assert [entry["node"] for entry in declared["bindings"]] == [NODE]
    assert run("--check", consumer / "backend").returncode == 0

    # The refused node is one this specification holds — binding it by hand succeeds. So what kept
    # it out of the trace was the record refusing to say where it was encoded, and not an identity
    # `--bind-record` would have rejected anyway, which is the way this test could pass vacuously.
    direct = run("--bind", consumer / "backend", consumer / "specs", OTHER, SECOND)
    assert direct.returncode == 0, direct.stdout + direct.stderr


def test_a_partial_bind_says_which_nodes_it_did_not_write(consumer, write_record):
    """The bind writes what cleared, and its own output is where the rest of the set is stated.

    Without this the partial act was legible only from `--reconciliation`, one invocation earlier:
    the bind listed what it bound and stopped, so thirty-eight bindings out of forty printed the
    same shape as forty out of forty at the one moment the person who ran it was still looking."""
    record = write_record(record_of(
        [CLEARED, {"node": OTHER, "conforms": False,
                   "how": "the second file states a threshold no node holds",
                   "observed_at": [SECOND]}],
        files=[{"path": FILE, "change": "answers with the persisted order_number"},
               {"path": SECOND, "change": "refuses a second bill"}]))
    bound = run("--bind-record", consumer / "backend", consumer / "specs", record)
    assert bound.returncode == 0, bound.stdout + bound.stderr
    assert "1 node(s) of order-fix.md the judgment did not clear" in bound.stdout
    assert OTHER in bound.stdout.split("did not clear", 1)[1]
    assert "still a finding on the next --check" in bound.stdout


def test_a_bind_that_cleared_everything_says_nothing_about_nodes_it_held_back(consumer,
                                                                             write_record):
    """The receipt is a statement about a partial act, and a complete one must not carry it —
    a line that prints on every bind is a line nobody reads on the bind that needed it."""
    record = write_record(record_of([CLEARED]))
    bound = run("--bind-record", consumer / "backend", consumer / "specs", record)
    assert bound.returncode == 0, bound.stdout + bound.stderr
    assert "did not clear" not in bound.stdout


def test_a_delivery_record_carries_no_such_class(consumer, write_record):
    """`--bind-record` serves both forms, and only one of them has a node the judgment refused.
    A delivery record is read for two field names and must fall through every part of the guard."""
    record = write_record(record_of([CLEARED]), where="delivery/orders/implementation")
    assert trace.withheld(record) == []


def test_the_drift_a_partial_bind_leaves_is_exactly_what_it_did_not_clear(consumer, write_record):
    """The measurement the older rule rested on being false.

    That rule held the cleared bindings back because a trace holding half the set was said to read
    exactly like a trace holding all of it. It does not: the nodes that cleared are restamped and
    stop reporting, the node that did not is untouched and still reports, and the count `--check`
    prints is the remainder. So the two states are distinguishable by the same signal that
    surfaced the drift, and holding thirty-eight bindings back only made forty findings look
    equally unexamined while paying to judge the thirty-eight again."""
    target = consumer / "backend"
    assert run("--bind", target, consumer / "specs", NODE, FILE).returncode == 0
    assert run("--bind", target, consumer / "specs", OTHER, SECOND).returncode == 0
    assert run("--check", target).returncode == 0

    (target / FILE).write_text("export function place() { return persisted.order_number }\n",
                               encoding="utf-8")
    (target / SECOND).write_text("export function bill() { if (n >= 1) {} }\n", encoding="utf-8")
    drifted = run("--check", target)
    assert drifted.returncode == 1
    assert "2 drift finding(s)" in drifted.stdout

    record = write_record(record_of(
        [CLEARED, {"node": OTHER, "conforms": False,
                   "how": "the source states `if (n >= 1)`, which no node holds",
                   "observed_at": [SECOND]}],
        files=[{"path": FILE, "change": "answers with the persisted order_number"},
               {"path": SECOND, "change": "refuses a second bill"}]))
    assert run("--reconciliation", record).returncode == 0
    bound = run("--bind-record", target, consumer / "specs", record)
    assert bound.returncode == 0, bound.stdout + bound.stderr

    after = run("--check", target)
    assert after.returncode == 1
    assert "1 drift finding(s)" in after.stdout
    assert OTHER in after.stdout
    assert NODE not in after.stdout


# ---------------------------------------------------------------------- the accounting


def test_a_node_may_not_reach_a_file_the_record_never_named(write_record):
    """The check the schema cannot state, and the one that matters: `--bind-record` binds every
    path `encoded_at` names, so a path that never reached the file set is ground the human never
    scoped, asserted in the file that outlives every plan."""
    front = record_of([{**CLEARED, "encoded_at": [FILE, "src/orders/refund.ts"]}])
    done = run("--reconciliation", write_record(front))
    assert done.returncode == 1
    assert "src/orders/refund.ts" in done.stdout
    assert "does not" in done.stdout


def test_a_named_file_no_node_accounts_for_is_a_problem(write_record):
    front = record_of([CLEARED],
                      files=[{"path": FILE, "change": "answers with the order_number"},
                             {"path": SECOND, "change": "refuses a second bill"}])
    done = run("--reconciliation", write_record(front))
    assert done.returncode == 1
    assert SECOND in done.stdout
    assert "unbound" in done.stdout


def test_a_named_file_the_trace_binds_nothing_to_is_declared_and_holds(write_record):
    front = record_of([CLEARED],
                      files=[{"path": FILE, "change": "answers with the order_number"},
                             {"path": SECOND, "change": "refuses a second bill"}],
                      unbound=[SECOND])
    done = run("--reconciliation", write_record(front))
    assert done.returncode == 0, done.stdout + done.stderr
    assert "1 file(s) the trace binds nothing to" in done.stdout


def test_a_record_whose_files_the_trace_binds_nothing_to_holds_with_no_nodes(write_record):
    """The outcome the locate step reaches when every named file is untraced. It is a real answer
    and not an empty one: the record says the trace holds nothing about these files, which is the
    thing a later reader would otherwise have to rediscover to learn nothing from."""
    front = record_of([], unbound=[FILE])
    done = run("--reconciliation", write_record(front))
    assert done.returncode == 0, done.stdout + done.stderr
    assert "0 node(s) the judgment cleared" in done.stdout
    assert "1 file(s) the trace binds nothing to" in done.stdout


def test_a_file_is_unbound_or_accounted_for_and_never_both(write_record):
    front = record_of([CLEARED], unbound=[FILE])
    done = run("--reconciliation", write_record(front))
    assert done.returncode == 1
    assert "one or the other" in done.stdout


def test_an_unbound_file_outside_the_file_set_is_a_problem(write_record):
    front = record_of([CLEARED], unbound=[SECOND])
    done = run("--reconciliation", write_record(front))
    assert done.returncode == 1
    assert "not in this record's file set" in done.stdout


def test_one_entry_per_node_and_one_per_file(write_record):
    twice = write_record(record_of([CLEARED, {**CLEARED, "how": "said again"}]))
    done = run("--reconciliation", twice)
    assert done.returncode == 1
    assert "one entry per node" in done.stdout

    front = record_of([CLEARED], files=[{"path": FILE, "change": "one way"},
                                        {"path": FILE, "change": "another way"}])
    done = run("--reconciliation", write_record(front, slug="doubled"))
    assert done.returncode == 1
    assert "one entry per file" in done.stdout


# ------------------------------------------------------------------------- the wiring


def test_the_form_is_exclusive_with_every_other_one(consumer, write_record):
    record = write_record(record_of([CLEARED]))
    done = run("--reconciliation", "--check", record)
    assert done.returncode == 2
    assert "mutually exclusive" in done.stderr


def test_replace_does_not_apply_to_it(write_record):
    done = run("--reconciliation", "--replace", write_record(record_of([CLEARED])))
    assert done.returncode == 2
    assert "--replace only applies" in done.stderr


# --------------------------------------------- every node a named file answers to


def test_a_record_leaving_a_bound_node_unanswered_is_refused(consumer, write_record):
    """The contract defines the node set as every specification node the trace binds to a named
    file, and the skill says "never a subset". Until the bind checked it, a record naming a file
    and answering for one of the two nodes bound to it rebound that one and left the other
    asserting a link nobody re-read — while reading exactly like a complete reconciliation.

    Both nodes are bound to the same file here, so the record's file set reaches both."""
    for node in (NODE, OTHER):
        assert run("--bind", consumer / "backend", consumer / "specs",
                   node, FILE).returncode == 0

    record = write_record(record_of([CLEARED]))
    assert run("--reconciliation", record).returncode == 0, "the record is sound on its own terms"

    bound = run("--bind-record", consumer / "backend", consumer / "specs", record)
    assert bound.returncode == 1, bound.stdout + bound.stderr
    assert OTHER in bound.stdout, bound.stdout
    assert "never the subset" in bound.stdout, bound.stdout


def test_a_record_answering_for_every_bound_node_binds(consumer, write_record):
    """The other half, and the one that keeps the test above from passing for the wrong reason: the
    same two bindings, and a record that answers for both, is written. `conforms: false` is an
    answer — the check is about accounting for the node, not about clearing it."""
    for node in (NODE, OTHER):
        assert run("--bind", consumer / "backend", consumer / "specs",
                   node, FILE).returncode == 0

    record = write_record(record_of(
        [CLEARED, {"node": OTHER, "conforms": False,
                   "how": "the file states a threshold this node does not hold",
                   "observed_at": [FILE]}]))
    assert run("--reconciliation", record).returncode == 0

    bound = run("--bind-record", consumer / "backend", consumer / "specs", record)
    assert bound.returncode == 0, bound.stdout + bound.stderr


ORPHANABLE = "constraints/asynchronous-events"


def test_an_orphaned_binding_is_not_a_node_a_record_owes_an_answer_for(consumer, write_record):
    """A node the specification no longer holds cannot be answered for: no bind repairs it and
    `--prune` is its route, so demanding an answer would refuse a record over ground the route
    hands elsewhere.

    A constraint is the node that can leave without the base going unsound around it, which is
    what makes the case reachable at all — delete a referenced element instead and
    `sound_specification` refuses first, before any of this is consulted."""
    assert run("--bind", consumer / "backend", consumer / "specs",
               ORPHANABLE, FILE).returncode == 0
    assert run("--bind", consumer / "backend", consumer / "specs", NODE, FILE).returncode == 0
    record = write_record(record_of([CLEARED]))

    # Not vacuous, and asserted before the removal rather than after: while the node is still in
    # the specification this exact record is refused for it. So what excuses it below is the
    # orphaning and nothing else.
    still_held = run("--bind-record", consumer / "backend", consumer / "specs", record)
    assert still_held.returncode == 1 and ORPHANABLE in still_held.stdout, still_held.stdout

    (consumer / "specs" / f"{ORPHANABLE}.md").unlink()
    bound = run("--bind-record", consumer / "backend", consumer / "specs", record)
    assert bound.returncode == 0, bound.stdout + bound.stderr


# ------------------------------------------------------------------ what no bind could close


@pytest.fixture
def declared(consumer: Path) -> Path:
    """The project file `--owed` reads to anchor each record's paths on its target's source root.
    A record spells its paths from there; the trace spells them from the toplevel, and the map
    between the two lives in this file and nowhere else."""
    (consumer / "siegard.json").write_text(
        json.dumps({"specification_root": "specs", "targets": {"backend": "backend"}}, indent=2),
        encoding="utf-8")
    return consumer


def owed(root: Path, *rest) -> subprocess.CompletedProcess:
    return run("--owed", root / "backend", *rest)


def bind(root: Path, node: str, *files: str) -> subprocess.CompletedProcess:
    return run("--bind", root / "backend", root / "specs", node, *files)


TESTABLE = dict(CLEARED, decided_by="reading", remainder="testable",
                remainder_why="one input, an order with no lines, against one refusal")
UNTESTABLE = dict(CLEARED, decided_by="reading", remainder="untestable",
                  remainder_why="identity across every file that holds the case is a fact about "
                                "where the code sits")


def test_a_remainder_rides_a_refused_certification_or_is_not_one(write_record):
    """Two halves or neither; and only on a node decided by reading, because a remainder is what a
    refused certification says about what is left — a certified node has none, and a node nobody
    asked about was never read for one."""
    assert run("--reconciliation", write_record(record_of([TESTABLE]))).returncode == 0
    for broken in (dict(CLEARED, remainder="testable", remainder_why="an assertion"),
                   dict(CERTIFIED, remainder="testable", remainder_why="an assertion"),
                   dict(CLEARED, decided_by="reading", remainder="testable"),
                   dict(CLEARED, decided_by="reading", remainder_why="an assertion")):
        done = run("--reconciliation", write_record(record_of([broken])))
        assert done.returncode == 1, done.stdout + done.stderr


def test_owed_lists_the_testable_remainders_priced_per_file_and_never_the_untestable_ones(
        declared, write_record):
    """The list is the work a test closes, priced where the judge is paid: a node closed on a file
    whose every other binding a reading still decides frees no judge yet, and the count beside it
    says so. An untestable remainder was said once in its record and is handed to nothing — a
    list that repeated it would find something forever."""
    bind(declared, NODE, FILE)
    bind(declared, OTHER, FILE)
    write_record(record_of([TESTABLE]), slug="asked-case")
    write_record(record_of([dict(UNTESTABLE, node=OTHER)]), slug="asked-evidence")

    done = owed(declared)
    assert done.returncode == 0, done.stdout + done.stderr
    assert "1 node(s) a refused certification left decided by reading with a testable remainder" \
        in done.stdout
    assert f"{NODE} [asked-case.md]" in done.stdout
    assert "would close it: one input, an order with no lines, against one refusal" in done.stdout
    assert f"    {FILE} — 2 binding(s) a reading decides on this file" in done.stdout, \
        "the files are what the proof increment's ask names, and `stands` is spelled from the " \
        "target source root; the toplevel's spelling would be refused by `--encodes`"
    assert f"backend/{FILE}" not in done.stdout
    assert "frees its judge" not in done.stdout
    assert "asked-evidence.md" not in done.stdout and "untestable" not in done.stdout
    assert "the route that writes it is a proof increment: `/deliver-scope`" in done.stdout, \
        "every testable remainder is owed a route that runs, and the route over a node no task " \
        "implements is the proof increment — never a re-delivery of a task that does not exist"
    assert "proof-only re-delivery" not in done.stdout

    bind(declared, OTHER, SECOND, "--replace")
    done = owed(declared)
    assert f"    {FILE} — 1 binding(s) a reading decides on this file; closing this one " \
           f"frees its judge" in done.stdout


def test_a_testable_remainder_answered_by_a_later_certification_is_reported_apart(
        declared, write_record):
    """No chronology is available, so the two records are not resolved in favour of either: a live
    certification in the trace closes the question, and without one the node is named apart."""
    bind(declared, NODE, FILE)
    write_record(record_of([TESTABLE]), slug="asked")
    write_record(record_of([CERTIFIED]), slug="certified")
    done = owed(declared)
    assert "testable remainder in one record and a certification in another" in done.stdout
    assert NODE in done.stdout and "would close it" not in done.stdout

    proof_at(declared)
    bound = run("--bind-record", declared / "backend", declared / "specs",
                declared / "siegard-reconcile" / "certified.md")
    assert bound.returncode == 0, bound.stdout + bound.stderr
    done = owed(declared)
    assert "testable remainder" not in done.stdout


def test_a_finding_against_a_pair_nothing_binds_is_owed_and_no_drift_report_can_reach_it(
        declared, write_record):
    """The claim the contract used to make the other way round, and the one this form exists for.

    Drift is computed from the bindings. A judgment that found against a node the trace does not
    bind to the file it was read in — the candidate tier's whole purpose, a fact governed by a node
    another file carries — leaves no digest to disagree with, so the drift report is clean and stays
    clean however long the finding stands. Nothing about the file has to change for that to remain
    true, which is why no later `--check` reaches it either."""
    bind(declared, OTHER, FILE)
    write_record(record_of([REFUSED]))

    clean = run("--check", declared / "backend")
    assert clean.returncode == 0, clean.stdout + clean.stderr
    assert "no drift" in clean.stdout
    assert NODE not in clean.stdout

    done = owed(declared)
    assert done.returncode == 1, done.stdout + done.stderr
    assert "unseen" in done.stdout
    assert NODE in done.stdout
    assert "order-fix.md" in done.stdout


def test_a_bind_over_the_content_a_finding_was_read_in_removes_the_only_symptom(
        declared, write_record):
    """The second silence, and the one that reads most like resolution. The pair was reachable —
    a binding held it — and a bind stamped the very content the finding was read in, so the digest
    agrees and the drift report has nothing to say while the finding stands underneath it."""
    bind(declared, NODE, FILE)
    write_record(record_of([REFUSED]))

    clean = run("--check", declared / "backend")
    assert clean.returncode == 0, clean.stdout + clean.stderr
    assert "no drift" in clean.stdout

    done = owed(declared)
    assert done.returncode == 1, done.stdout + done.stderr
    assert "covered" in done.stdout
    assert NODE in done.stdout


def test_a_finding_whose_binding_is_stale_is_the_one_the_drift_report_already_carries(
        declared, write_record):
    """The third state is the honest one, and naming it apart is what keeps the other two from
    reading like it. Here `--check` does report the drift; what this adds is the record that says
    what was found in the file."""
    bind(declared, NODE, FILE)
    (declared / "backend" / FILE).write_text("export function place() { return 1 }\n",
                                             encoding="utf-8")
    write_record(record_of([REFUSED]))

    drift = run("--check", declared / "backend")
    assert drift.returncode == 1, drift.stdout + drift.stderr

    done = owed(declared)
    assert done.returncode == 1, done.stdout + done.stderr
    assert "reported" in done.stdout


def test_a_clearance_in_the_corpus_closes_a_finding_and_the_count_is_the_receipt(
        declared, write_record):
    """A remediated pair is not owed, and listing every one of them would rebuild the unreadable
    report this script spends its receipts preventing — one consumer's history holds more than
    twice as many of those as of everything else. The count rides a line and `--all` prints the
    list, exactly as the same flag already works over `--check`."""
    write_record(record_of([REFUSED]), slug="found-against")
    write_record(record_of([CLEARED]), slug="cleared-later")

    done = owed(declared)
    assert done.returncode == 0, done.stdout + done.stderr
    assert "1 pair(s) the records answer both ways" in done.stdout
    assert "`--all` lists them" in done.stdout
    assert "unseen" not in done.stdout

    listed = owed(declared, "--all")
    assert listed.returncode == 0, listed.stdout + listed.stderr
    assert "found-against.md" in listed.stdout and "cleared-later.md" in listed.stdout


def test_a_corpus_holding_no_open_finding_says_so(declared, write_record):
    write_record(record_of([CLEARED]))
    done = owed(declared)
    assert done.returncode == 0, done.stdout + done.stderr
    assert "nothing owed" in done.stdout


def test_a_record_naming_a_target_the_project_file_does_not_declare_is_reported_never_guessed(
        declared, write_record):
    """Its paths are spelled from a root nothing here can resolve. Anchoring them on a guess would
    name files the judgment never read, and this form's whole output is which file a finding is
    about."""
    write_record(record_of([REFUSED], target="frontend"))
    done = owed(declared)
    assert "frontend" in done.stdout
    assert "does not declare" in done.stdout


def test_a_record_for_another_target_is_not_this_targets_business(consumer, write_record):
    """Every target's records share one directory, because they share one git toplevel. A status
    that folded a sibling target's findings into this one would report a tree nobody asked about."""
    (consumer / "siegard.json").write_text(
        json.dumps({"specification_root": "specs",
                    "targets": {"backend": "backend", "frontend": "web"}}, indent=2),
        encoding="utf-8")
    (consumer / "web").mkdir()
    write_record(record_of([{"node": NODE, "conforms": False,
                             "how": "the screen states a refusal no node holds",
                             "observed_at": ["app.ts"]}],
                           files=[{"path": "app.ts", "change": "hand edit"}], target="frontend"))
    done = run("--owed", consumer / "backend")
    assert done.returncode == 0, done.stdout + done.stderr
    assert "nothing owed" in done.stdout


def test_encodes_tells_an_intact_binding_from_a_file_the_trace_binds_nothing_to(declared):
    """The two states a drift report cannot separate, because it is keyed by drift and neither of
    them drifted. Telling them apart is what a reconciliation's locate step needs before it can
    hand a judge a node set."""
    bind(declared, NODE, FILE)
    bind(declared, OTHER, FILE)

    clean = run("--check", declared / "backend")
    assert clean.returncode == 0 and "no drift" in clean.stdout

    done = run("--encodes", declared / "backend", FILE, SECOND)
    assert done.returncode == 0, done.stdout + done.stderr
    assert "backend/src/orders/place.ts: 2 binding(s)" in done.stdout
    assert NODE in done.stdout and OTHER in done.stdout
    assert "backend/src/orders/bill.ts: the trace binds nothing to this file" in done.stdout


def test_encodes_says_which_bindings_no_longer_compute_without_calling_it_a_failure(declared):
    """A query and never a check: every stale binding it prints is a `code` finding `--check`
    already reports, and giving one drift two exit statuses would make a caller choose which to
    believe."""
    bind(declared, NODE, FILE)
    (declared / "backend" / FILE).write_text("export function place() { return 1 }\n",
                                             encoding="utf-8")
    done = run("--encodes", declared / "backend", FILE)
    assert done.returncode == 0, done.stdout + done.stderr
    assert "stale: the file changed without a rebind" in done.stdout


def test_the_reading_forms_are_exclusive_with_every_other_one(declared):
    for other in ("--check", "--prune", "--bind", "--bind-record", "--reconciliation"):
        for form in ("--owed", "--encodes"):
            done = run(form, declared / "backend", other)
            assert done.returncode == 2, done.stdout + done.stderr
            assert "mutually exclusive" in done.stderr


def test_all_applies_to_the_form_that_holds_something_back_and_not_to_the_query(declared):
    done = run("--encodes", declared / "backend", FILE, "--all")
    assert done.returncode == 2
    assert "--all only applies to --check, --owed, --rank, --convergence and --untraced" in done.stderr


# ------------------------------------------------------------------ an unreadable record


MERGE_MARKED = ("---\ncontract_version: siegard-reconcile/5\n<<<<<<< HEAD\ntitle: One round\n"
                "=======\ntitle: Another round\n>>>>>>> theirs\ntarget: backend\n---\n")


def test_an_unreadable_record_in_the_corpus_is_named_by_owed_and_the_exit_says_so(declared):
    """A record nobody can read may hold an open finding, and a corpus walk that skipped it
    would say nothing is owed over a finding it never opened."""
    (declared / "siegard-reconcile" / "half-merged.md").write_text(MERGE_MARKED,
                                                                   encoding="utf-8")
    done = owed(declared)
    assert done.returncode == 1, done.stdout + done.stderr
    assert "siegard-reconcile/half-merged.md" in done.stdout
    assert "a record nobody can read may hold an open finding" in done.stdout
    assert "nothing owed" not in done.stdout


def test_a_staging_refuses_to_run_while_the_corpus_holds_an_unreadable_record(declared):
    """The omission guard borrows a judgment only where no record holds an open finding against
    the pair, and a record it cannot read is one it cannot answer that question over."""
    assert bind(declared, NODE, FILE).returncode == 0
    (declared / "siegard-reconcile" / "half-merged.md").write_text(MERGE_MARKED,
                                                                   encoding="utf-8")
    done = run("--stage", declared / "backend", declared / "specs", "round",
               declared / "ws-round", FILE)
    assert done.returncode == 2, done.stdout + done.stderr
    assert "siegard-reconcile/half-merged.md" in done.stderr
    assert "a record nobody can read may hold an open finding" in done.stderr
    assert not (declared / "ws-round").exists()
    assert not (declared / "siegard-reconcile" / "round.returns").exists()
