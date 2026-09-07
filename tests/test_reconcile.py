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
        "contract_version": "siegard-reconcile/3",
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


def test_the_contract_demonstrates_both_outcomes():
    """One example each way, because the two differ by which field they carry and a contract
    showing only the cleared shape teaches that the other one is a variation on it."""
    schema = json.loads(
        (REPO / "src/claude/schemas/reconciliation.json").read_text(encoding="utf-8"))
    answers = sorted(entry["conforms"] for example in schema["examples"]
                     for entry in example["nodes"])
    assert answers == [False, True]


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
    assert "--all only applies to --check, --owed and --rank" in done.stderr
