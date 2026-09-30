#!/usr/bin/env python3
"""Resolve and maintain the trace: which specification node produced which file, once the plan
that wrote it is gone.

Planning and delivery are disposable — a task exists to get code written, and nothing requires
its files to survive that. `siegard-trace.json`, beside `siegard.json` at the git toplevel of the
target source root, is the one fact this framework keeps instead: for a node it has bound, the
digest it read and the file(s) it produced, each pinned the same way. A later run recomputes both
digests from what is on disk now and compares — a node whose digest no longer matches moved in
the specification since the bind; a file whose digest no longer matches moved in the code without
a rebind. Either is drift, and this script is what says so without any plan's history to consult.

What this script does, and nobody else does any of it:

    trace.py <target-root>                                        read and validate the file
    trace.py --check <target-root> [--all]                        the same, then report drift
    trace.py --bind <target-root> <spec-root> <node> <file> ...    write or extend one binding
    trace.py --bind-record <target-root> <spec-root> <record>     every binding that record states
    trace.py --bind-record ... --workspace <dir>                  the same, refusing a file or a
                                                                  node that moved since the
                                                                  staging in that workspace read it
    trace.py --bind ... --replace                                 write it in full instead
    trace.py --prune <target-root>                                drop the bindings nothing can fix,
                                                                  following a node git renamed
    trace.py --release <target-root> <file> ...                   drop a file the tree no longer
                                                                  holds from every binding naming it
    trace.py --reconciliation <record>                            hold a reconciliation to its
                                                                  contract before it is bound
    trace.py --owed <target-root> [--all]                         what the reconciliations found
                                                                  and no bind could close, and
                                                                  the nodes a test would close
    trace.py --encodes <target-root> <file> ...                   which nodes each file is bound to
    trace.py --convergence <target-root> <spec-root> <work-root>  every node of the specification
                                                                  in one state, across the trace
                                                                  and every initiative, with the
                                                                  judged side kept apart
    trace.py --encodes --changed <target-root> [<ref>]            the same, over the files the
                                                                  tree changed rather than a set
                                                                  a caller spelled out
    trace.py --stage <target-root> <spec-root> <slug> <workspace> <file> ...
                                                                  prepare a reconciliation's
                                                                  workspace: node sets, packs,
                                                                  candidates, omittable pairs
    trace.py --stage ... --audit                                  the same, omitting no pair:
                                                                  every standing claim is judged
    trace.py --stage ... --review [--node <node> ...]             a review's staging: omitting no
                                                                  pair, keeping the candidate
                                                                  tier, and reading each --node on
                                                                  every file without binding it
    trace.py --stage ... --review --demonstrated <proof-record> ...
                                                                  also stage one certification per
                                                                  node the proofs' tests claim to
                                                                  demonstrate, composed here
    trace.py --stage ... --certify <file>                         also stage a certification per
                                                                  node the file names: its pack,
                                                                  the proof offered and the step
                                                                  that runs it, omitting no pair
                                                                  of a node being certified
    trace.py --fold <target-root> <workspace> <premise> <record>  fold the delegations' returns
                                                                  into the reconciliation record
    trace.py --encodes --rank <target-root> [--all]               the accretion axes: files by
                                                                  bindings held, nodes by files
                                                                  bound

Drift is reported in four classes, because a caller can act on each differently and could act on
none of them if all four arrived as one list. A node the specification no longer holds is
`orphaned`: the fact it named is gone, and no operation here can repair the entry — `--bind`
refuses a node the specification does not hold, and this script is the trace's one writer, so the
finding repeats on every run forever. A node whose text moved is `moved`, and a file that changed
or vanished is `code`; both are true statements about real drift, and each has one route, stated
in the class's own line: `/reconcile` over the bound files re-reads them against the node as it
stands, a delivery of a task implementing the node restamps it, and a file gone from the tree is
`--release`'s. A binding a test decides whose test's text changed is `proof`:
the certification was of that text, and until a judgment certifies the test as it now stands the
binding is decided by reading again — its `code` drift, if any, is still listed, and still a
reconciliation's. Only the first is `--prune`'s, and `--prune` touches only it:
dropping a binding whose file moved would discard the one record of which node that code answers
to, which is the whole of what this file keeps.

Left unpruned, the orphaned class is what makes the other two unreadable. A tree carrying eighty
stale entries reports eighty-three findings the day three files drift, and nobody reads the three:
the report a caller stops reading is a report that says nothing, however true every line of it is.

`--prune` follows a rename before it drops. A node whose file git moved is the node under a new
identity, not a node that left: the fact stands, the code still answers it, and the binding is
the one link between the two. So where git records the orphaned node's file as renamed to a node
the specification holds now, the binding is rewritten to that identity with its files and its
digest kept — a digest that no longer computes is a `moved` finding on the next `--check`, which
is the true statement about it — and the receipt names both identities. A chain of renames is
followed to its latest link. `--check` says on the orphaned line where git says the node went, so
a reader knows before pruning which entries will be followed and which dropped. No git, no
commit, or no rename, and `--prune` drops the entry as it otherwise would.

`--release` answers the one drift no other form reaches: a bound file the tree no longer holds. A
reconciliation reads a file, and there is nothing to read; `--prune` touches the orphaned class
alone; a bind stamps a file that exists. Left there, the binding reports `code` on every run for
a path nothing will ever restamp. So this form drops the path from every binding that names it,
drops a binding left holding nothing, writes once, and prints a receipt per node — the same
receipt `--replace` prints for a path it stops claiming, because the loss is the same loss. It
refuses a path the tree still holds: a file that exists is reconciled, never released, since the
only thing releasing it would buy is a clean report over a link somebody deleted by hand. And it
refuses the whole call before writing any of it, so a release of three paths of which one still
stands is no release at all.

The `code` class has the same arithmetic inside itself, and the listing answers it the same way.
One file bound by sixteen nodes drifts sixteen findings the day it changes once — one shared
file buries the report on every edit — so the
listing prints that class per file: one line naming the file, the reason, and every binding the
change staled. The findings are still counted per binding, because that is what they are; the
grouping is the listing's, because the remedy for this class is a reconciliation and a
reconciliation is invoked over a file set — the report is keyed the way the remedy consumes it.

The same arithmetic is what `edits_freely` answers, one class over. A target whose surface changes
for reasons no node governs — a label, a colour, a column's order — produces a `code` finding per
edit, weekly, and buries `moved` and `orphaned` under a list nobody finishes. So a project may name
those targets in `siegard.json`, and `--check` stops listing that class for files sitting under
them. Three things this deliberately is not. It is not per-invocation: the declaration is read from
the project file beside this one, so a check run from anywhere reports the same tree the same way,
and a check over a traced target never loses a finding because a sibling target is exempt. It is
not a change to what is bound — `--bind-record` still writes the link, `moved` still says the
specification shifted under those files, `orphaned` still says the node is gone. And it is not
silence: a receipt says how many findings were held back and `--all` lists them, which is what
keeps a declaration a consumer can measure from becoming one it forgets it made.

A context descriptor, `domain/<context>/_context`, is never bound and never staged. It carries a
context's description and classification and no operative claim, so no file holds it and no
return contract can name it: `--bind` refuses it, and so does `--stage --review --node`.

`--bind-record` is the form a delivery uses. An implementation record names every node the source
encodes and
every file each one reached; binding them one invocation at a time pays a full specification
validation and a full read-and-rewrite of the trace per node, and leaves the rule that a bind states
exactly what the record says — never a second judgment about it — resting on prose. This reads the
record: a node it does not name cannot be bound from this form, and one it does cannot be skipped.
The whole of it is refused before anything is written, because a delivery half bound describes a
link nobody made while reading exactly like a complete one. A record naming no node with
`encoded_at` is not a failure: the nodes it answers only by `how` reached no file, a bind with none
is refused, and there is simply nothing to write.

That refusal is over form — a node this specification does not hold, a file that is not there — and
it is not the reconciliation route's per-node judgment. A reconciliation record answers node by
node, and a node the judgment did not clear carries no `encoded_at`; the nodes that cleared are
written and that one is not. Refusing the record over it would make a judgment that resolved
thirty-eight of forty nodes worth exactly as much as one that resolved none, and buy nothing for
it: the two nodes it could not write stay precisely as they were, and what the next `--check`
says about them depends on whether a binding held each pair — `--owed` is the form that says it
either way. What the bind owes instead is a receipt naming them, so a partial bind never reads
like a complete one.

A bind stamps what a judge read, and the workspace is where the staging recorded what that was.
`--bind-record --workspace <dir>` reads the staging's manifest back — the digest of every staged
file and of every node it pinned — and refuses the whole record where any of them differs from
what stands now: the judgment was over those bytes and that sentence, and a bind over what
replaced them would stamp a claim nobody read, with no later `--check` able to tell, because the
bind writes the new digest itself. The fold holds the same guard at its own moment; the interval
between the fold and the bind is the workspace's to close. An implementation record has no
workspace, and a bind without the flag reads each file fresh and stamps what stands.

`--reconciliation` is the one form here that writes nothing. It holds a reconciliation record —
source that changed outside any task, at `siegard-reconcile/<slug>.md` beside this file — to
`schemas/reconciliation.json`, so that `--bind-record` can then read it exactly as it reads an
implementation record. That split is deliberate and it is the same one the delivery route already
has: `bin/deliver.py` validates an implementation record and this script binds what it says, never
holding a second opinion about a contract it does not own. What is different is that nobody else
owns this one. A reconciliation record has no life outside the trace — it exists to justify a bind
and nothing reads it for any other purpose — so the validation lands here rather than in a script
invented to hold it. The check that matters is the accounting: every path a node claims is a path
the record's own file set names, and every file it names is claimed by a node or declared unbound.
A record that binds a file nobody declared would widen the reconciliation past what a human
scoped, silently, and the trace would carry the result forever.

`--bind` validates <spec-root> the way spec.py does, refuses a node it does not hold, reads that
node's digest and each file's digest fresh, and writes the entry. It is the one bind no record
backs — every skill binds through `--bind-record`, where an implementation or reconciliation
record holds the judgment — so every `--bind` prints a receipt saying the judgment behind this
entry lives nowhere, because the trace it writes reads afterwards exactly like one a record
justified. By default it extends whatever
that node already held: a file this call does not name but an earlier bind of the same node did
stays bound, at the digest that earlier bind recorded, because two tasks landing the same rule in
two different files is not one of them undoing the other's work. A file this call does name is
written at the digest read just now, whether or not an earlier bind already held that path.
`--replace` writes the entry in full instead: a file left off the
list is a file this bind no longer claims — for the case where a fact genuinely moved out of a
file rather than into an additional one. **It substitutes the whole entry, not the files this call
names**, so where two records answer one node, replacing from the second drops what the first
bound. That is legitimate and often intended, and it is never silent: every path a `--replace`
stops claiming is printed as a receipt once the write succeeds, because the trace it leaves is
internally consistent and `--check` would come back clean over the loss. The first bind for a
target root creates the trace file;
every later one is held to the same specification, named once, and a bind naming a different one
is refused rather than silently repointed.

`--owed` is the only form here that reads `siegard-reconcile/` as a corpus, and it exists because
the rest of this script cannot answer the question it answers. A record under that directory
nobody can read is named, never skipped: it may hold an open finding, so `--owed` lists it and
exits non-zero, and `--stage` refuses to run while it stands — an omission guard that borrows a
judgment over a corpus it could not finish reading borrows one no record is known to contest.
Drift is computed from the bindings: a judgment that found against a node writes no binding, so
there is nothing for the next `--check` to compare. Where the pair was bound before, the old
digest still reports it and the report is honest. Where it was not — a node the judge opened as a
candidate, bound to some sibling file and not to this one — or where a later bind stamped the very
content the finding was read in, `--check` is silent, and silent permanently: nothing about that
file has to change again. The findings are never lost — every one is in a record, and
`/siegard-archive` refuses to remove them — and this form is what reads them back: it says which
of three states each finding is in, writes nothing, decides nothing, and every line names the
record its finding came from.

`--encodes` answers the other question the drift report cannot. `--check` is keyed by drift, so a
file is in it because it changed: a file whose bindings are intact is absent from it and reads
exactly like a file the trace binds nothing to. Telling those two apart is what a reconciliation's
locate step needs before it can hand a judge a node set, and the only way to get it was to open the
trace and read the bindings by hand — which is unvalidated, and where a binding is missed the judge
is handed an incomplete node set and the record that results reads exactly like a complete one.

`--encodes --changed` asks that question of what the tree changed rather than of a set a caller
spelled out. Impact runs forward everywhere else here — `spec.py --impact` opens from node
identities somebody already holds, and `--encodes` from paths somebody already listed — and the
question a change actually raises runs the other way: these files moved, which nodes do they
encode. Composing it by hand means converting every path git prints from the toplevel anchor to
the target source root's, and a caller who gets that conversion wrong is handed a refusal per
path rather than an answer. With no `<ref>` the file set is what the working tree holds against
`HEAD`, tracked and untracked alike, which is the set standing before a commit; with one, it is
what the branch changed since that ref. Paths outside the target source root are dropped rather
than refused: a commit that touched a sibling target is an ordinary commit, and the answer over
this target is still the whole answer over this target.

`--convergence` is the one reading that composes what `--check`, `--owed`, `deliver.py
--outstanding` and `plan.py --unplanned` each say alone. Each is correct alone, and a reader
composing them by hand gets the composition wrong in ways that are not visible from any one of
them: a plan `/siegard-archive` removed still planned what it named, an epic's `uncovered` is a
decision, a node honored without being encoded is bound to nothing by design, and a freely-edited
target is stale in fact while held back on purpose. This form encodes those once and answers per
node, by class, in five states — and prints the judged side beside them, kept apart, because a
binding that computes and a record that found against a node are facts about different things.
A query, exit 0 always, no figure.

A CI runs `--check` and reads its exit code: non-zero is drift of any class, and the listing says
which. `moved` is the ordinary state of a tree between a specification's change and the delivery
that answers it, so a caller that runs on every push reads the classes in the listing rather than
the status alone.

`--stage` is `--encodes` carried to where the locate step actually spends: it computes each named
file's node set once, writes it where every consumer of it reads the same copy, and prepares what
each judgment needs before any judgment runs. Into a caller-named workspace it writes a manifest —
the node set per file, the candidate index for the whole batch, and every pair it found omittable —
and one node pack per file: the full text of every node that file's judge must read, each under a
header naming its source path and the digest the bind will stamp. A pack is a reading copy and
never a home — it is derived from the specification at the moment of staging, lives in a workspace
nothing commits, and a judge who doubts a line in it opens the source path its header names. It
exists because a judge's node set is known mechanically before the judge is spawned, and a context
that opens fifteen files one call at a time pays its own accumulated history fifteen times for
content one staged read carries whole. A pair is omittable only where the judgment it would buy
already exists: the binding computes at the file's content as it stands — the pair was judged over
these exact bytes and stamped by that judgment's bind — and no record in `siegard-reconcile/` holds
an open finding against it. Re-judging such a pair buys a second reading of text that did not move,
and what a second reading of unchanged input adds is not confidence. Both halves of that rule are
recomputed by `--bind-record` at bind time; the manifest's list is a preparation, never an
authority. `--stage` also reserves the reconciliation's own ground: it refuses a slug whose record
or returns directory already exists, and creates `siegard-reconcile/<slug>.returns/` empty — the
returns saved there are the evidence the record is folded from, and they outlive the workspace.

`--audit` inverts that one omission, deliberately. Every report keyed by change has a blind spot:
a binding over-broad from the day it was written never drifts, so nothing that watches for drift
ever re-examines it, and the claim stands for as long as the file does. An audit is the
re-judgment of exactly those pairs — the human names a file set whose bindings did not move, and
the staging hands every standing claim to a judge, omitting nothing. Everything downstream is the
ordinary pipeline: a claim the judge confirms is restamped with a record justifying it, a fact
held nowhere blocks its node and hands the `--bind --replace` release ready to run, and a finding
nobody acts on stays in the corpus where `--owed` repeats it. `--rank` is where an audit's file
set comes from: the two accretion counts, files by bindings held and nodes by files bound, stated
as facts — which of them is worth a judge is a person's reading.

A constraint some step of the project's registry `decides` is answered by running that step, not
by a reading. The registry's `commands[].decides` is the join that keeps which command checks a
constraint the project's choice and never the node's; a reading that judged such a pair would
re-decide what the step decides, at a model's recall and at the price of the whole file's
delegation, since one judge is spawned per file and reads it whole. So `--stage` hands no judge
such a pair and lists it in the manifest under `mechanical`, `--check` says which `code` findings
sit on one, `--encodes` marks the binding, and `--rank` counts a file's bindings by whether a
reading decides them at all. The omission guard still runs first: a pair that is current and owes
nothing needs no judge and no run either.

A binding may also be decided by a test, and that is the trace's own join rather than the
registry's. `--stage --certify <file>` takes the human's certifications — a node, the test file(s)
offered as its proof, and the registry step that runs them — refuses a node the named files do not
encode, a proof that is not there or a step the registry does not declare, never omits a pair of a
node being certified, and writes one certification pack per node beside the file packs. The
judgment that certifies is the coverage auditor's and its rule is the whole of the test: the
named tests would fail if the node's fact stopped holding. Its return is saved like every other
under `<slug>.returns/certify__<node>.yaml`; `--fold` reads it against
`schemas/certification-return.json`, and writes `decided_by: test` on a node only where the
auditor answered `covered` and the node's own reading cleared — a certification never rides a node
the judgment refused. Where the auditor answered short of `covered`, the node stays decided by
reading and its entry carries the auditor's `remainder`: whether a test could close what the
offered tests left unexercised. `--owed` lists the testable ones, each with the assertion that
would close it and the file's own count of bindings a reading decides — the saving is per file,
so a node is priced where its judge is paid. `--bind-record` then pins the proof's digests beside the files', so the
binding names the test that decides it and the text that was certified. From there `--check`
reports a changed test under `proof`, a bind over the node carries the certification forward
while the proof's text stands and releases it with a receipt the moment it does not, and every
listing that names a step-decided pair names a test-decided one the same way. What a test decides
is whether the fact holds; which file holds it stays the source's, which is why `files` and their
digests are untouched by any of this.

`--stage --review --demonstrated <proof-record> ...` composes those certifications from the
proofs themselves, for the review route. «Every claim that a test demonstrates a node is carried
to certification by the review that reads the proof» (SPEC-004 R13) — and a proof record's
`tests[]` is where the claim lives, one `demonstrates` per test. Composing the certifications
file from those entries in prose would leave it a step a skill performs in prose, which is a step
that gets skipped. So the staging reads the records: every test naming a node under
`demonstrates` is one entry per node, its `proof` the files of every such test, its `step` the
registry's command whose `role` is `suite` — the one step that proves the work, and the one
`deliver.py` holds to being declared once. A record `deliver.py` did not first hold to its
contract is read defensively, the way every record here is; a node no test claims gets no entry,
and a registry declaring no suite step is a refusal, because a certification with no step to run
its proof is one nothing can ever answer for. The human's `--certify` may ride beside it, for a
claim no proof carries; one node certified from both is refused, the way one node certified twice
in one file already is.

`--fold` writes the reconciliation record from the delegations' returns, mechanically. Every rule
it applies is a fold over structured answers — a node conforms exactly where every delegation that
read one of its files cleared it; a finding naming a node lands on that node wherever its own judge
stood; a finding naming none holds every node of the file that produced it *that its judge was
handed* — a node a run decided reached no judge, and what answered it is the step's own outcome
rather than a reading's silence about which node it meant; a node whose fact no
named file holds any more binds nothing — and none of those rules asks for judgment, so none of
them is applied by a context that could misremember one. The caller supplies the one part that is
not mechanical: a premise file carrying the human's `title`, `summary`, `target` and per-file
`change` lines. A return that does not satisfy `schemas/conformance-return.json`, answers for a
node set other than the manifest's, or is missing for a staged file refuses the fold naming the
delegation to run again — the correction for an unusable return is a fresh delegation, never a
repair applied to its answer here. The record it writes is validated against
`schemas/reconciliation.json` and its own accounting before it lands, and is then read by
`--reconciliation` and `--bind-record` exactly like one written any other way.

Every path this file holds — `specification`, and every binding's `files[].path` — is relative to
this file's own directory, exactly the way `siegard.json`'s `standard` is. `<target-root>` and
`<file>` on the command line are relative to the target source root instead, the anchor every other
contract in this framework uses — and so is every path a record's `encoded_at` carries; this script
converts, so a caller working the way every other skill already does never computes the git
toplevel itself.

Declared dependencies: PyYAML, jsonschema (this script also imports spec.py and project.py, its
siblings under bin/).

Usage:  trace.py <target-root>
        trace.py --check <target-root> [--all]
        trace.py --bind <target-root> <spec-root> <node> <file> [<file> ...] [--replace]
        trace.py --bind-record <target-root> <spec-root> <implementation-record> [--replace]
        trace.py --bind-record <target-root> <spec-root> <reconciliation-record>
                 [--workspace <workspace-dir>] [--replace]
        trace.py --prune <target-root>
        trace.py --release <target-root> <file> [<file> ...]
        trace.py --reconciliation <reconciliation-record>
        trace.py --owed <target-root> [--all]
        trace.py --encodes <target-root> <file> [<file> ...]
        trace.py --encodes --changed <target-root> [<ref>]
        trace.py --convergence <target-root> <spec-root> <work-root-parent> [--all]
        trace.py --stage <target-root> <spec-root> <slug> <workspace-dir> <file> [<file> ...]
                 [--audit | --review [--node <node> ...] [--demonstrated <proof-record> ...]]
                 [--certify <certifications-file>]
        trace.py --fold <target-root> <workspace-dir> <premise-file> <record>
        trace.py --encodes --rank <target-root> [--all]
        trace.py --help
                print this text and stop
Exit:   0 sound / drift-free / bound / pruned / released / the record holds / nothing is owed /
          staged / folded
        1 problems: an invalid file, drift found, an unsound specification, an unknown node
          or file, a record its contract refuses, a finding no bind closed, a return a
          delegation owes again
        2 cannot run
"""

from __future__ import annotations

import json
import os
import shlex
import subprocess
import sys
from pathlib import Path, PurePosixPath
from typing import NoReturn

CANNOT_RUN = 2

try:
    import yaml
    from jsonschema import Draft202012Validator
except ImportError:  # pragma: no cover - exercised by the environment, not the suite
    print("cannot run: PyYAML and jsonschema are required (pip install pyyaml jsonschema)",
          file=sys.stderr)
    raise SystemExit(CANNOT_RUN)

import plan
import project
import spec

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
TRACE_CONTRACT = PLUGIN_ROOT / "schemas" / "trace.json"
RECONCILE_CONTRACT = PLUGIN_ROOT / "schemas" / "reconciliation.json"
RETURN_CONTRACT = PLUGIN_ROOT / "schemas" / "conformance-return.json"
TRACE_FILE = "siegard-trace.json"
RECONCILE_DIR = "siegard-reconcile"
MANIFEST_FILE = "manifest.json"
RUN_DIR = "run"
NOWHERE = "nowhere"

UNSEEN, COVERED, REPORTED = "unseen", "covered", "reported"
UNSTATED_FACT = "unstated"
OWED_CLASSES = {
    UNSEEN: "nothing binds the pair — `--check` has no digest to compare and never will",
    COVERED: "bound at the content on disk now — a bind wrote over the only symptom `--check` "
             "had, and the finding stands under it",
    REPORTED: "the binding is stale, so `--check` already carries this one — the record is what "
              "says what was found",
}

ORPHANED, MOVED, PROOF, CODE = "orphaned", "moved", "proof", "code"
CLASSES = {
    ORPHANED: "bound to a node the specification no longer holds — no bind can repair these, "
              "and `--prune` is the only thing that clears them",
    MOVED: "bound to a node whose text moved since the bind; `/reconcile` over the bound files "
           "re-reads them against the node as it stands, and a delivery of a task implementing "
           "the node restamps it",
    PROOF: "decided by a test whose text changed since it was certified — the binding is "
           "decided by reading again until a judgment certifies the test as it now stands",
    CODE: "bound to a file that changed or is gone; `/reconcile` over the files re-reads a file "
          "that changed, and `--release` answers one the tree no longer holds",
}
CURRENT, STALE, PLANNED_UNBOUND, DECLARED_UNCOVERED, UNREACHED = (
    "current", "stale", "planned-unbound", "declared-uncovered", "unreached")
CONVERGENCE = {
    CURRENT: "bound, and every binding computes to what was recorded — the specification and the "
             "code stand as they did when the node was last answered",
    STALE: "bound, and some binding no longer computes — `--check` lists each by class, and its "
           "route is that class's",
    PLANNED_UNBOUND: "a task implements it or an epic covers it, and no binding holds it — whether "
                     "the task was delivered, and honored the node without encoding it, is "
                     "`deliver.py --outstanding`'s answer per initiative",
    DECLARED_UNCOVERED: "an epic looked at it and wrote down why it is not being built; a decision "
                        "somebody made, never a gap",
    UNREACHED: "no initiative names it and nothing binds it — a specification describes more than "
               "the work has reached, and this is the part it has not",
}
DECIDED_BY_TEST = "test"
JUDGED = "judged"
# The reason a review writes on a pair it omits. `omitted_problems` reads it back to know the
# omission rests on a judgment and not only on current digests, so it is matched, never paraphrased.
CLEARED_BY_JUDGMENT = ("cleared by a judgment at these bytes: a reconciliation's judgment read "
                       "this pair over the file's content and the node's text as both stand, "
                       "and no finding stands open against it")
RECORD_VERSION = "siegard-reconcile/5"
TESTABLE = "testable"
CERTIFY_PREFIX = "certify__"
CERTIFICATION_CONTRACT = PLUGIN_ROOT / "schemas" / "certification-return.json"


def home_of(target: Path) -> Path:
    """Where the trace file sits: the same directory `siegard.json` sits in."""
    return project.toplevel_of(target)


def freely_edited(home: Path) -> list[str]:
    """The path prefixes whose `code` findings this tree asked not to be listed, read from the
    project file sitting beside the trace.

    Read here rather than taken as a flag, because which targets those are is the consumer's
    standing declaration and not a thing an invocation gets to answer differently each time. Read
    defensively: a project file that does not parse, or does not declare the field, suppresses
    nothing — `project.py` is what holds that file to its contract and says so properly, and a
    drift report is the wrong place to learn the project file is broken.

    The prefixes come back spelled from this file's own directory, which is the anchor every path
    in the trace already uses, so the comparison below is a prefix test and never a pattern."""
    declared_at = home / project.PROJECT_FILE
    if not declared_at.is_file():
        return []
    try:
        declared = json.loads(declared_at.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    if not isinstance(declared, dict):
        return []
    named = declared.get("edits_freely") or []
    targets = declared.get("targets") or {}
    if not isinstance(named, list) or not isinstance(targets, dict):
        return []
    prefixes = []
    for key in named:
        where = targets.get(key) if isinstance(key, str) else None
        if isinstance(where, str) and where:
            prefixes.append(PurePosixPath(where).as_posix().rstrip("/"))
    return sorted(set(prefixes))


def target_roots(home: Path) -> dict[str, str]:
    """Each target key's source root, spelled from this file's own directory, read from the
    project file sitting beside the trace.

    Read the way `freely_edited()` reads the same file and for the same reason: `project.py` is
    what holds that file to its contract, and a report is the wrong place to learn it is broken.
    What a caller does with a target this map does not hold is the caller's: a record naming one
    is reported rather than anchored on a guess, because its paths are spelled from a root nobody
    can resolve, and resolving them wrongly would name files the judgment never read."""
    declared_at = home / project.PROJECT_FILE
    if not declared_at.is_file():
        return {}
    try:
        declared = json.loads(declared_at.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(declared, dict):
        return {}
    targets = declared.get("targets") or {}
    if not isinstance(targets, dict):
        return {}
    return {key: PurePosixPath(where).as_posix().rstrip("/")
            for key, where in targets.items()
            if isinstance(key, str) and isinstance(where, str) and where}


def registry_of(home: Path, offset: str) -> dict | None:
    """The standard the project declares for the target whose source root is `offset`, read as
    YAML and nothing more. `deliver.py --standard` is what holds a registry to its contract, and a
    report is the wrong place to learn it is broken — so a registry that does not parse, or a
    project that declares none for this target, reads as no registry at all. The path is relative
    to the project file's own directory, the way `siegard.json` spells it."""
    declared_at = home / project.PROJECT_FILE
    if not declared_at.is_file():
        return None
    try:
        declared = json.loads(declared_at.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(declared, dict):
        return None
    roots = target_roots(home)
    keys = [key for key, where in roots.items() if where == offset]
    standard = declared.get("standard")
    if isinstance(standard, dict):
        named = next((standard[key] for key in keys if isinstance(standard.get(key), str)), None)
    elif isinstance(standard, str) and len(roots) <= 1:
        named = standard
    else:
        named = None
    if not named:
        return None
    try:
        loaded = yaml.safe_load((home / named).read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return None
    return loaded if isinstance(loaded, dict) else None


def decided_constraints(home: Path, offset: str) -> dict[str, list[str]]:
    """Every constraint a step of this target's registry `decides`, with every step that does.

    Several steps may decide one constraint, and a registry writing it that way is saying each
    decides a part: a lint that finds no forbidden import decides half of "the domain reaches
    infrastructure only through ports", and the test that finds no second implementer decides the
    other. So they come back as a list and every one of them has to pass — keyed by name alone,
    one would silently win by its position in the file and the evidence the other named would
    never be run.

    This is the join `standard.json` holds so that which command checks a constraint stays the
    project's choice and never the node's. A binding on one of these is a pair a reading would
    re-decide at a model's recall, when the step already decides it over the tree — so every form
    here that hands pairs to a judge or lists them names these apart, and a caller that runs the
    step knows which pairs its run answers."""
    registry = registry_of(home, offset)
    decided: dict[str, list[str]] = {}
    for command in (registry or {}).get("commands") or []:
        if not isinstance(command, dict) or not isinstance(command.get("step"), str):
            continue
        for identity in command.get("decides") or []:
            if isinstance(identity, str) and command["step"] not in decided.setdefault(identity, []):
                decided[identity].append(command["step"])
    return decided


def offset_of(target: Path, home: Path) -> str:
    """The target source root spelled from the trace's own directory — `.` where the two are one."""
    return Path(os.path.relpath(target.resolve(), home.resolve())).as_posix()


def under(path: str, prefixes: list[str]) -> bool:
    """Whether one path of the trace sits under any of those prefixes. A prefix of `.` — a target
    that is the toplevel itself — reaches everything, which is what a project declaring its whole
    tree freely edited asked for."""
    parts = PurePosixPath(path).parts
    for prefix in prefixes:
        if prefix in (".", ""):
            return True
        if parts[:len(PurePosixPath(prefix).parts)] == PurePosixPath(prefix).parts:
            return True
    return False


def cannot_run(message: str) -> NoReturn:
    """Refuse and stop. A trace this script cannot read is never repaired into a default: the
    file is the record, and a default would bind against a record nobody wrote."""
    print(f"cannot run: {message}", file=sys.stderr)
    raise SystemExit(CANNOT_RUN)


def trace_path(target: Path) -> Path:
    return home_of(target) / TRACE_FILE


def load(target: Path) -> dict | None:
    """The trace declared at <target-root>, or None where none has been bound yet.

    A trace that does not parse, or that parses to anything but a mapping, is refused here rather
    than carried further. This is the one file the framework keeps after a plan is history, and
    it is one of the two that conflict in a worktree batch — so a trace holding merge markers is
    a state that happens, and every form of this script would otherwise end in a traceback over
    it instead of saying which file to fix."""
    path = trace_path(target)
    if not path.is_file():
        return None
    try:
        declared = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as broken:
        cannot_run(f"{path} does not parse: {broken}")
    if not isinstance(declared, dict):
        cannot_run(f"{path} holds a {type(declared).__name__}, not a trace; a trace is an object "
                   f"with a specification and its bindings")
    return declared


def problems_of(declared: dict) -> list[str]:
    """Everything wrong with a trace on its own terms: the schema, plus one entry per node."""
    schema = json.loads(TRACE_CONTRACT.read_text(encoding="utf-8"))
    problems = [f"{'.'.join(str(part) for part in error.absolute_path) or 'top level'}: "
                f"{error.message}"
                for error in sorted(Draft202012Validator(schema).iter_errors(declared), key=str)]
    counted: dict[str, int] = {}
    for entry in declared.get("bindings") or []:
        if isinstance(entry, dict) and isinstance(entry.get("node"), str):
            counted[entry["node"]] = counted.get(entry["node"], 0) + 1
    problems += [f"bindings: {node} is bound {count} times; one entry per node"
                 for node, count in sorted(counted.items()) if count > 1]
    return problems


def drift_of(declared: dict, home: Path,
             declared_steps: set[str] | None = None
             ) -> tuple[list[tuple[str, str, str | None, str]], list[str]]:
    """Every binding that no longer computes to what was recorded for it, each under the class its
    remedy belongs to — and, separately, whatever stopped the reading before any of that.

    A finding carries the path it is about where it has one, so that a caller filtering by where
    the file sits reads the path rather than the sentence. The classes about a node carry none:
    a node moved or gone is not a fact about any one file.

    The classes are not three flavours of one fact, and a caller who cannot tell them apart cannot
    act on any of them. `orphaned` is the one only `--prune` fixes: the node left the specification, `--bind` refuses a node the specification does not hold, and this
    script is the trace's one writer — so the entry stays, its finding repeats on every run, and a
    file drift that arrived today reads as one more line in a list nobody finishes. `moved` and
    `code` are the drift this file exists to report, and neither is `--prune`'s business: a
    reconciliation over the files, or the delivery that implements the node, is the answer, and
    dropping the entry instead would throw away the one record of which node that code answers
    to. The one `code` finding no reading reaches — a file the tree no longer holds — is
    `--release`'s, which drops the path and nothing else. An orphaned finding says where git
    records the node's file as having gone, when it does: the reader of the report is deciding
    whether to prune, and which entries a prune will follow rather than drop is part of that.

    Refusals come back apart from findings because they are not findings. A specification that does
    not resolve or does not hold together says nothing about any binding — reporting `orphaned` for
    every node of a specification nobody could read would be this script inventing drift out of its own
    blindness.

    A `code` finding's message carries the reason alone — the node and the path already ride the
    tuple's own slots, and the report lists this class per file (`code_report`), so a message
    restating either would be parsed back out of prose to group it. The pinned digests are not in
    the message either: the trace file holds them, and a reconciliation reads them there."""
    spec_root = home / declared["specification"]
    if not spec_root.is_dir():
        return [], [f"specification: {spec_root} is not a directory; "
                    f"{declared['specification']} no longer resolves"]
    nodes, node_problems = spec.collect(spec_root, spec.contracts())
    node_problems += spec.cross_problems(nodes, spec_root)
    if node_problems:
        return [], [f"specification: {spec_root} is not sound; run spec.py against it directly"]

    findings: list[tuple[str, str, str | None, str]] = []
    for entry in declared.get("bindings") or []:
        node_id, digest = entry["node"], entry["digest"]
        current = nodes.get(node_id)
        if current is None:
            findings.append((ORPHANED, node_id, None,
                             f"{node_id}: no longer in the specification; the binding is stale"))
        elif current["digest"] != digest:
            findings.append((MOVED, node_id, None,
                             f"{node_id}: bound at {digest}, now {current['digest']}; "
                             f"the specification moved since this bind"))
        for file_entry in entry.get("files") or []:
            where = file_entry["path"]
            path = home / where
            if not path.is_file():
                findings.append((CODE, node_id, where, "the file no longer exists — `--release` "
                                                       "is what answers a deleted file"))
                continue
            if spec.digest_of(path) != file_entry["digest"]:
                findings.append((CODE, node_id, where, "the file changed without a rebind"))
        # A test-decided binding's proof is pinned the way its files are, and moves the same way;
        # what differs is the remedy — a fresh certification of the test as it now stands, never
        # a rebind of the file — so the class is its own.
        if entry.get("decided_by") == DECIDED_BY_TEST:
            if declared_steps is not None and entry.get("step") not in declared_steps:
                findings.append((PROOF, node_id, None,
                                 f"{node_id}: certified as decided by the step "
                                 f"`{entry.get('step')}`, which the project's registry no longer "
                                 f"declares; nothing can run it, so the binding is decided by "
                                 f"reading until a judgment certifies it against a step that "
                                 f"exists"))
            for proof_entry in entry.get("proof") or []:
                where = proof_entry["path"]
                path = home / where
                if not path.is_file():
                    findings.append((PROOF, node_id, where,
                                     f"{node_id}: certified over {where}, and the test no longer "
                                     f"exists; the binding is decided by reading until a judgment "
                                     f"certifies a test that does"))
                elif spec.digest_of(path) != proof_entry["digest"]:
                    findings.append((PROOF, node_id, where,
                                     f"{node_id}: certified over {where}, whose text changed "
                                     f"since; the binding is decided by reading until a judgment "
                                     f"certifies the test as it now stands"))
    orphaned = [finding[1] for finding in findings if finding[0] == ORPHANED]
    if orphaned:
        followed = rename_targets(spec_root, orphaned, nodes)
        findings = [(cls, node_id, where,
                     f"{why} — renamed to {followed[node_id]}; `--prune` follows it"
                     if cls == ORPHANED and node_id in followed else why)
                    for cls, node_id, where, why in findings]
    return findings, []


def renamed_nodes(spec_root: Path) -> dict[str, str]:
    """Every node identity git records as renamed under the specification root, mapped to the
    identity its file carries now — the latest link of a chain. Empty where git is not on this
    machine, does not hold the root, or holds no commit: a rename nobody committed is a rename
    nothing can read, and the answer then is the one `--prune` gives without it."""
    try:
        probe = subprocess.run(["git", "-C", str(spec_root), "log", "-M", "--diff-filter=R",
                                "--name-status", "--format=", "--", "."],
                               capture_output=True, text=True)
    except OSError:
        return {}
    if probe.returncode != 0:
        return {}
    toplevel = project.toplevel_of(spec_root)
    try:
        prefix = spec_root.resolve().relative_to(toplevel.resolve()).as_posix()
    except ValueError:
        return {}

    def identity_of(spelled: str) -> str | None:
        path = PurePosixPath(spelled)
        if path.suffix != ".md":
            return None
        if prefix != ".":
            if path.parts[:len(PurePosixPath(prefix).parts)] != PurePosixPath(prefix).parts:
                return None
            path = PurePosixPath(*path.parts[len(PurePosixPath(prefix).parts):])
        return "/".join(path.with_suffix("").parts) or None

    later: dict[str, str] = {}
    for line in probe.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) != 3 or not parts[0].startswith("R"):
            continue
        old, new = identity_of(parts[1]), identity_of(parts[2])
        if old is None or new is None or old == new:
            continue
        later.setdefault(old, new)

    def latest(identity: str) -> str:
        seen = {identity}
        while identity in later and later[identity] not in seen:
            identity = later[identity]
            seen.add(identity)
        return identity

    return {old: latest(old) for old in later}


def rename_targets(spec_root: Path, orphaned: list[str],
                   nodes: dict[str, dict]) -> dict[str, str]:
    """Each orphaned node whose file git moved to a node the specification holds now, mapped to
    that identity. A rename whose target is gone too is no rename to follow."""
    if not orphaned:
        return {}
    renamed = renamed_nodes(spec_root)
    return {old: renamed[old] for old in orphaned if old in renamed and renamed[old] in nodes}


def traced_files_of(target: Path, home: Path, files: list[str]) -> tuple[list[dict], list[str]]:
    """Each named file as the trace stores it: the path re-anchored on this file's own directory,
    and the digest read now. A file that does not exist is a problem rather than an omission —
    binding a node to a path nothing holds would record a link to nowhere.

    The refusal names the anchor, because the anchor is what is usually wrong. Every path this
    script prints back — a drift finding, an entry of the trace — is spelled from the target's git
    toplevel, and every path it reads is spelled from the target source root. A caller who copies
    one into the other gets a path that is neither, and `<target>/<target>/...` is a stranger thing
    to be handed than the reason it happened."""
    offset = Path(os.path.relpath(target.resolve(), home.resolve()))
    entries, problems = [], []
    claimed: set[str] = set()
    for given in files:
        source = target / given
        if not source.is_file():
            said = (f"{source} does not exist; a path is read relative to {target}, the "
                    f"target source root, never from the repository around it")
            # The commonest wrong spelling is the right path under the toplevel anchor — this
            # script's own output spells paths that way, so a caller copying one back in makes
            # exactly this error. Naming the rule alone sent each occurrence into its own
            # fix-and-rerun cycle; handing the corrected spelling ends the class in one.
            anchored = home / given
            if anchored.is_file():
                try:
                    corrected = anchored.resolve().relative_to(target.resolve()).as_posix()
                    said += (f" — the file stands at {anchored}, which is the toplevel's "
                             f"spelling; from the target it is `{corrected}`")
                except ValueError:
                    said += (f" — a file does stand at {anchored}, and it sits outside "
                             f"{target}, where no binding can name it")
            problems.append(said)
            continue
        try:
            source.resolve().relative_to(target.resolve())
        except ValueError:
            # The sentence above is the whole rule, and `../` is the one spelling that passes
            # `is_file()` while breaking it. Stored unnormalised it would also alias: one file
            # under two spellings is two entries no reader can tell apart.
            problems.append(f"{given} climbs out of {target}, the target source root; a bound "
                            f"path is read from inside it, never from the repository around it")
            continue
        stored = given if str(offset) == "." else (offset / given).as_posix()
        if stored in claimed:
            problems.append(f"{stored} is named twice in one bind; a second entry for one path "
                            f"carries nothing the first does not, and every later reading of the "
                            f"trace would count the file twice")
            continue
        claimed.add(stored)
        entries.append({"path": stored, "digest": spec.digest_of(source)})
    return entries, problems


def fold(declared: dict, node_id: str, digest: str, traced_files: list[dict],
         replace: bool, certification: dict | None = None) -> tuple[int, list[str]]:
    """Fold one binding into the trace in place; say how many files that node now holds, and which
    ones this call stopped claiming.

    Extending what the node already held is the default: two tasks landing one node in two
    different files is not one of them undoing the other's work. `--replace` writes the entry in
    full instead, for the case where a fact genuinely moved out of a file rather than into an
    additional one.

    The second return value is why this reports at all. `--replace` substitutes the whole entry,
    not the files this call names, so a path an earlier bind put there and this one leaves off is
    gone — and gone invisibly, because the trace it writes is internally consistent and `--check`
    comes back clean over it. That is the same silent loss the union default exists to end,
    surviving behind a flag. Nothing here refuses it: dropping a file is exactly what `--replace`
    is for, and the caller who omitted a vanished path meant to. What this owes is the receipt —
    the two sides are both in hand at this moment, and one of them would otherwise be discarded
    unread.

    Paths, never records. Which delivery put a file here is not something this file stores, so the
    receipt names what stopped being claimed and says nothing about who claimed it."""
    existing = next((entry for entry in declared["bindings"]
                     if entry.get("node") == node_id), None)
    given = {entry["path"] for entry in traced_files}
    dropped = (sorted(entry["path"] for entry in existing.get("files") or []
                      if entry["path"] not in given)
               if replace and existing is not None else [])
    if replace or existing is None:
        files = traced_files
    else:
        files = [entry for entry in existing.get("files") or []
                 if entry["path"] not in given] + traced_files
    files = sorted(files, key=lambda entry: entry["path"])
    bindings = [entry for entry in declared["bindings"] if entry.get("node") != node_id]
    written = {"node": node_id, "digest": digest, "files": files}
    # The certification is the caller's to supply, fresh from a record or carried from the entry
    # this write replaces; supplied, it is written whole, and absent, the binding is a reading's.
    if certification is not None:
        written["decided_by"] = DECIDED_BY_TEST
        written["step"] = certification["step"]
        written["proof"] = sorted(certification["proof"], key=lambda entry: entry["path"])
    bindings.append(written)
    declared["bindings"] = sorted(bindings, key=lambda entry: entry["node"])
    return len(files), dropped


def carried_certification(declared: dict, node_id: str,
                          home: Path) -> tuple[dict | None, str | None]:
    """The certification the node's standing entry holds, carried whole — and the receipt where
    its proof's text no longer stands.

    A bind rewrites the whole entry, and a bind over a file the node encodes is not a judgment
    about the test that decides the node — so the certification is carried forward, not dropped
    with the entry it rode. It is carried whether or not the proof's digests still compute. A
    test whose text changed is what `--check` reports under `proof`, and what every reader of a
    certification recomputes before trusting it: `test_decided` holds a certification live only
    while its proof's bytes are the certified ones, so a carried certification over moved text
    decides nothing, stages nothing into a mechanical tier, and is re-read by the next judgment
    exactly as an uncertified node is. Dropping it instead would throw away the one record of
    which test decided the node — and drop it silently, since the entry written afterwards reads
    exactly like one never certified, and no report ever says a certification was lost. Kept, the
    loss is a `proof` finding with its route: a reconciliation that certifies the test as it now
    stands. The receipt says so at the one moment both sides are in hand."""
    existing = next((entry for entry in declared.get("bindings") or []
                     if entry.get("node") == node_id), None)
    if existing is None or existing.get("decided_by") != DECIDED_BY_TEST:
        return None, None
    carried = {"step": existing["step"], "proof": list(existing["proof"])}
    stale = []
    for proof_entry in existing.get("proof") or []:
        source = home / proof_entry["path"]
        if not source.is_file() or spec.digest_of(source) != proof_entry["digest"]:
            stale.append(proof_entry["path"])
    if stale:
        return carried, (f"  {node_id} is decided by a test whose text moved: "
                         f"{', '.join(stale)} changed since it was certified. The certification "
                         f"is carried as it was, decides nothing until the test is certified as it "
                         f"now stands, and `--check` reports it under `proof` until a "
                         f"reconciliation does — or a judgment refuses it")
    return carried, None


def certified(node_id: str, certification: dict) -> str:
    """The receipt for a certification written. A statement, and the one place the act is said at
    the moment it happens: the entry afterwards carries the fields, and nothing else says a bind
    just changed what decides a node."""
    return (f"  {node_id} is decided by a test from here: step `{certification['step']}` over "
            f"{', '.join(entry['path'] for entry in certification['proof'])}; a drift on its files "
            f"is that step's to answer, a drift on the test is a fresh certification's")


def released(node_id: str, dropped: list[str], act: str = "--replace") -> str:
    """The receipt for what a `--replace` stopped claiming, or what a `--release` dropped. A
    statement, never a warning: the ordinary use of either is a file that genuinely left, and an
    alarm on the correct path is an alarm nobody reads by the third time. It ends by pointing at
    where the entry before this write survives if it survives anywhere, which is git — stated as
    a direction rather than a guarantee, because a trace that was never committed has no earlier
    state to return to."""
    if act == "--release":
        return (f"  --release released {len(dropped)} path(s) the tree no longer holds; "
                f"{node_id} no longer claims {', '.join(dropped)}. The link those paths held is "
                f"gone from here, and the last committed trace is where it survives if anywhere")
    return (f"  --replace released {len(dropped)} path(s) this call did not name; "
            f"{node_id} no longer claims {', '.join(dropped)}. Where the fact moved out of those "
            f"files, that is what --replace is for; where another delivery had bound one of them, "
            f"that binding is gone from here, and the last committed trace is where it survives "
            f"if anywhere")


def emptied(node_id: str) -> str:
    """The receipt for a binding a `--release` dropped whole: its last path left the tree, so the
    entry linked the node to nothing. Said apart from the path receipt, because a node the trace
    stopped holding is a different fact from a path a node stopped claiming, and the route back
    is named where the loss is."""
    return (f"  {node_id} held nothing else and is gone from the trace; a delivery of a task "
            f"implementing it, or a reconciliation over the files that hold its fact now, is what "
            f"binds it again")


def unrecorded(node_id: str) -> str:
    """The receipt for a bind no record backs. A statement, never a refusal: `--bind` is the
    general form and stays open — it is the one door a tree with untraced code has — but every
    other bind this framework writes rests on a record that says which node the source encodes
    and why, and this one rests on the caller's say-so alone. The receipt is the only trace of
    that difference, because the entry this bind writes reads afterwards exactly like one a
    record justified — and how often this line shows up in reports is what will say whether the
    raw form costs more than it serves."""
    return (f"  this binding rests on no record: --bind wrote what the caller stated, and the "
            f"judgment behind it lives nowhere a reader can reopen. A delivery's record or a "
            f"reconciliation is the recorded route — for a hand edit over bound source, "
            f"/reconcile writes the same binding with the judgment kept. The trace carries no "
            f"mark of the difference on {node_id}; this line is the only one")


def stale_after(declared: dict, home: Path, acted: dict[str, str],
                bound: set[str]) -> list[tuple[str, str, str]]:
    """The bindings this act left stale, found at the one moment both sides are in hand.

    A bind restamps only the nodes it was handed. That leaves two kinds of binding asserting a
    digest the tree no longer holds, both knowable right now and both silent afterwards until
    somebody runs `--check`: another node's binding over a path this act just restamped — the
    fresh digest is already in memory and differs — and a path a bound node carried forward from
    an earlier bind whose file changed on its own. Only this act's neighborhood is read — the
    bound nodes' own entries and the paths this act wrote, never the whole trace: a receipt that
    restated every standing drift would bury the ones this act just made or met."""
    stale = []
    for entry in declared["bindings"]:
        node = entry["node"]
        for held in entry.get("files") or []:
            path, stored = held["path"], held["digest"]
            if node not in bound:
                if path in acted and stored != acted[path]:
                    stale.append((node, path, "this act restamped the file under another node"))
            elif path not in acted:
                source = home / path
                if not source.is_file():
                    stale.append((node, path,
                                  "carried forward from an earlier bind, and the file is gone"))
                elif spec.digest_of(source) != stored:
                    stale.append((node, path, "carried forward from an earlier bind, and the "
                                              "file has since changed"))
    return sorted(stale)


def code_report(findings: list[tuple[str, str, str | None, str]]) -> list[str]:
    """The `code` class, listed per file rather than per binding.

    A file bound by sixteen nodes that changes once is one act to take, not sixteen lines to
    read — one shared file buries
    the report every time it moves. The remedy for this class is a reconciliation, and a
    reconciliation is invoked over a file set, so the listing is keyed the way the remedy
    consumes it: one line per file, naming every binding the change staled. Nothing about the
    findings themselves changes — the tally still counts bindings, `suppressed()` still counts
    both, and the trace still holds one entry per node — grouping is the listing's business
    and stops there."""
    grouped: dict[tuple[str, str], list[str]] = {}
    for _, node_id, where, why in findings:
        grouped.setdefault((where, why), []).append(node_id)
    return [f"{where}: {why} — {len(nodes)} binding(s): {', '.join(sorted(nodes))}"
            for (where, why), nodes in sorted(grouped.items())]


def suppressed(held: list[tuple[str, str, str | None, str]], prefixes: list[str]) -> str:
    """The receipt for the `code` findings a declared target held back. A count, never silence,
    and it follows the same discipline `released()` already sets for the trace's other loss: what
    a report stops saying it says once, in a line, so the reader can tell a clean tree from a tree
    whose findings were filed elsewhere. Without it the declaration would be the one thing in this
    framework a consumer could turn on and never measure again.

    The number is the point rather than the list, which is why the paths are behind `--all`: a
    surface that moves weekly produces this count by the hundred, and reprinting them here would
    rebuild exactly the unreadable report the declaration exists to prevent."""
    files = sorted({finding[2] for finding in held})
    return (f"  suppressed {len(held)} `code` finding(s) over {len(files)} file(s) under "
            f"{', '.join(prefixes)} — declared freely edited in {project.PROJECT_FILE}. "
            f"`--all` lists them, and that list is what /check-source reads to hold those files "
            f"to the rules a reading decides")


def partitioned(findings: list[tuple[str, str, str | None, str]],
                prefixes: list[str]) -> tuple[list, list]:
    """The findings a report lists, and the `code` findings a freely-edited target holds back.

    One home for the partition, because two readers now compute it: the drift report, and the
    session-start receipt that prints its tally. A second copy of this predicate would be a
    receipt that counts a suppression the report does not, and the two disagreeing about what a
    tree holds is worse than neither existing."""
    def held_back(finding) -> bool:
        return finding[0] == CODE and bool(finding[2]) and under(finding[2], prefixes)
    # Partitioned by the predicate rather than by membership in the held list: two findings that
    # compare equal would suppress each other, and a membership test walks that list once per
    # finding.
    return ([f for f in findings if not held_back(f)], [f for f in findings if held_back(f)])


def tally_of(target: Path) -> tuple[dict[str, int], int, list[str]] | None:
    """The drift a target holds, counted by class, with the count held back and the files a
    reconciliation would be invoked over — or nothing where there is no trace to read, nothing
    the trace can be held to, or no git to resolve the tree.

    A tally and never a listing. What a reader acts on is the count per class and the door it
    opens; the lines themselves are `--check`'s to print, and printing them anywhere a caller did
    not ask for them is how a report becomes something nobody finishes."""
    try:
        if not target.is_dir():
            return None
        declared = load(target)
        if declared is None or problems_of(declared):
            return None
        home = home_of(target)
        findings, refusals = drift_of(declared, home, registry_steps(home, offset_of(target, home)))
        if refusals:
            return None
        listed, held = partitioned(findings, freely_edited(home))
    except (Exception, SystemExit):
        # Every caller of this is a report beside the answer somebody actually asked for. A trace
        # this cannot read is the drift report's to refuse properly, with the reason; here it is
        # silence, because a receipt that raised would take the invocation down with it. SystemExit
        # is named because `cannot_run` is how this script refuses, and it is not an `Exception`.
        return None
    counts = {cls: sum(1 for f in listed if f[0] == cls) for cls in (ORPHANED, MOVED, PROOF, CODE)}
    return counts, len(held), sorted({f[2] for f in listed if f[0] == CODE and f[2]})


def as_list(value: str | list[str]) -> list[str]:
    """One step name or several, always as a list. `--check`'s receipt serves both a certification,
    which names the one step that runs its proof, and a constraint, which may name several."""
    return [value] if isinstance(value, str) else list(value)


def step_decided(findings: list[tuple[str, str, str | None, str]],
                 decided: dict[str, str | list[str]],
                 what: str = "a constraint a registry step decides") -> str:
    """The receipt for `code` findings that sit on a binding a run decides — a constraint the
    registry's step decides, or a node a certified test decides. A statement, never a second
    class: the drift is real and the pair is still listed — what this adds is that a reading
    would re-decide what the run decides, so a reader weighing the list knows which lines a run
    of the step answers."""
    lines = [f"  {len(findings)} of the `code` finding(s) sit on {what}; the step's run over the "
             f"tree is what decides each:"]
    lines += [f"    {node} over {where} "
              f"({'steps' if len(as_list(decided[node])) > 1 else 'step'} "
              f"{', '.join(f'`{s}`' for s in as_list(decided[node]))})"
              for _, node, where, _ in sorted(findings, key=lambda f: (f[2] or "", f[1]))]
    return "\n".join(lines)


def left_stale(stale: list[tuple[str, str, str]]) -> str:
    """The receipt for the bindings a bind left stale. A statement, never a warning, the same as
    `released()`: nothing here is wrong yet — a bind restamps exactly the nodes it was handed,
    and that is the contract — but each line below is a `code` drift finding on the next
    `--check`, and this is the one moment the maker of the change is still holding it."""
    lines = [f"  this act leaves {len(stale)} binding(s) stale — a bind restamps only the nodes "
             f"it was handed:"]
    lines += [f"    {node}: {path} — {why}" for node, path, why in stale]
    lines.append("    each is a `code` drift finding on the next --check; a reconciliation over "
                 "these paths is the route, whatever wrote the change")
    return "\n".join(lines)


def opened(target: Path, spec_root: Path,
           home: Path) -> tuple[dict | None, str | None]:
    """The trace as it stands, ready to be folded into, or nothing and the reason. The first bind
    for a target root creates it; every later one is held to the same specification, and one
    naming a different specification is refused rather than silently repointed."""
    spec_relative = Path(os.path.relpath(spec_root.resolve(), home.resolve())).as_posix()
    declared = load(target) or {"specification": spec_relative, "bindings": []}
    if not isinstance(declared.get("specification"), str) or \
            not isinstance(declared.get("bindings"), list):
        return None, (f"{trace_path(target)} carries no specification and bindings; it is not a "
                      f"trace this can fold into — validate it first")
    if declared["specification"] != spec_relative:
        return None, (f"{trace_path(target)} already traces against "
                      f"{declared['specification']}, not {spec_relative}; a trace names one "
                      f"specification")
    return declared, None


def is_descriptor(node_id: str) -> bool:
    """A context descriptor — `domain/<context>/_context` — and not a node a file can answer to.

    It holds a context's description, responsibility and strategic classification, and no
    operative claim: «every operative claim lives in exactly one addressable home» (SPEC-001 R7),
    and that home is an element, a rule, a scenario, a contract or a constraint. So no file holds
    it, no judgment can return it — every return contract spells a node without the underscore —
    and a binding to it would assert a link to a fact that does not exist."""
    parts = node_id.split("/")
    return len(parts) == 3 and parts[0] == "domain" and parts[2] == "_context"


DESCRIPTOR_REFUSAL = ("is a context descriptor: it carries no operative claim, so no file holds "
                      "it and no judgment can return it")


def sound_specification(spec_root: Path) -> tuple[dict[str, dict] | None, int]:
    """Every node the specification holds, or nothing and the exit status. Read through spec.py's
    own pipeline, because a trace bound against a specification that does not hold together records
    a link to a fact nobody validated."""
    nodes, problems = spec.collect(spec_root, spec.contracts())
    problems += spec.cross_problems(nodes, spec_root)
    if problems:
        for problem in sorted(set(problems)):
            print(problem)
        print(f"\n{spec_root} is not sound; nothing was bound.")
        return None, 1
    return nodes, 0


def write_trace(target: Path, declared: dict, act: str = "bind") -> int:
    problems = problems_of(declared)
    if problems:
        for problem in problems:
            print(f"cannot {act}: {problem}")
        return 1
    trace_path(target).write_text(json.dumps(declared, indent=2) + "\n", encoding="utf-8")
    return 0


def bind(target: Path, spec_root: Path, node_id: str, files: list[str],
         replace: bool = False) -> int:
    if not target.is_dir():
        print(f"cannot run: {target} is not a directory", file=sys.stderr)
        return CANNOT_RUN
    if not spec_root.is_dir():
        print(f"cannot run: {spec_root} is not a directory", file=sys.stderr)
        return CANNOT_RUN

    nodes, status = sound_specification(spec_root)
    if nodes is None:
        return status
    if node_id not in nodes:
        print(f"cannot bind: {spec_root} holds no node {node_id}")
        return 1
    if is_descriptor(node_id):
        print(f"cannot bind: {node_id} {DESCRIPTOR_REFUSAL}")
        return 1

    home = home_of(target)
    traced, problems = traced_files_of(target, home, files)
    for problem in problems:
        print(f"cannot bind: {problem}")
    if problems:
        return 1

    declared, refusal = opened(target, spec_root, home)
    if declared is None:
        print(f"cannot bind: {refusal}")
        return 1

    carried, let_go = carried_certification(declared, node_id, home)
    held, dropped = fold(declared, node_id, nodes[node_id]["digest"], traced, replace, carried)
    if write_trace(target, declared) != 0:
        return 1
    print(f"bound {node_id} to {held} file(s) at {trace_path(target)}")
    print(unrecorded(node_id))
    if dropped:
        print(released(node_id, dropped))
    if let_go:
        print(let_go)
    stale = stale_after(declared, home, {e["path"]: e["digest"] for e in traced}, {node_id})
    if stale:
        print(left_stale(stale))
    return 0


def frontmatter_of(record: Path) -> tuple[dict | None, str | None]:
    """One record's frontmatter as a mapping, or nothing and the reason it could not be read.

    Every way a file fails to be a record at all is the same failure to both callers here, and
    saying it twice is how the two drift into disagreeing about what a record even is."""
    if not record.is_file():
        return None, f"{record} does not exist"
    text, unreadable = spec.read_node(record)
    if text is None:
        return None, f"{record}: {unreadable}"
    match = spec.FENCE.match(text)
    if not match:
        return None, f"{record} carries no frontmatter fence; it is not a record this can read"
    try:
        front = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError as broken:
        return None, f"{record}: frontmatter does not parse: {broken}"
    if not isinstance(front, dict):
        return None, f"{record}: frontmatter is not a mapping"
    return front, None


def accounted(front: dict) -> list[str]:
    """Every way a reconciliation's own paths fail to add up, once the contract has held.

    The schema says what a field may hold; this says whether the fields agree with each other, and
    it is the half that carries the risk. `--bind-record` binds every path a node's `encoded_at`
    names, so a path that reached the record without reaching its file set is ground the human
    never scoped, asserted in the one file this framework keeps after every plan is gone. The
    accounting runs both ways for the same reason a bind and a drift check do: a named file no node
    accounts for is a file somebody meant to reconcile and nothing did, and it would leave the
    record reading complete."""
    named = [entry["path"] for entry in front["files"]]
    problems = [f"files: {path} is named {named.count(path)} times; one entry per file"
                for path in sorted(set(named)) if named.count(path) > 1]

    seen: dict[str, int] = {}
    claimed: set[str] = set()
    for entry in front["nodes"]:
        node_id = entry["node"]
        seen[node_id] = seen.get(node_id, 0) + 1
        where = "encoded_at" if entry["conforms"] else "observed_at"
        for path in entry[where]:
            claimed.add(path)
            if path not in named:
                problems.append(f"{node_id}: {where} names {path}, which this record's file set "
                                f"does not; a reconciliation reaches only what the human scoped")
    problems += [f"nodes: {node_id} appears {count} times; one entry per node"
                 for node_id, count in sorted(seen.items()) if count > 1]

    unbound = front.get("unbound") or []
    for path in unbound:
        if path not in named:
            problems.append(f"unbound: {path} is not in this record's file set")
        if path in claimed:
            problems.append(f"unbound: {path} is also accounted for by a node; a file is one or "
                            f"the other, and the trace either holds a binding to it or does not")

    answered_pairs = {(entry["node"], path) for entry in front["nodes"]
                      for path in entry["encoded_at" if entry["conforms"] else "observed_at"]}
    omitted_files: set[str] = set()
    for entry in front.get("pairs_omitted") or []:
        omitted_files.add(entry["file"])
        if entry["file"] not in named:
            problems.append(f"pairs_omitted: {entry['file']} is not in this record's file set")
        if (entry["node"], entry["file"]) in answered_pairs:
            problems.append(f"pairs_omitted: {entry['node']} over {entry['file']} is also "
                            f"answered by a node entry; a pair was judged or omitted, never both")
        if entry["file"] in unbound:
            problems.append(f"pairs_omitted: {entry['file']} is also under `unbound`; a pair "
                            f"can only be omitted where a binding holds it")

    for path in sorted(set(named) - claimed - set(unbound) - omitted_files):
        problems.append(f"files: {path} is named and no node accounts for it; a file the trace "
                        f"binds nothing to belongs under `unbound`, said rather than left out")
    return problems


def reconciliation(record: Path) -> int:
    """Hold one reconciliation record to its contract, and write nothing.

    It is validated here and bound by `--bind-record`, the same split the delivery route already
    has between `bin/deliver.py` and this script. The difference is that no other script owns this
    contract: a reconciliation record exists to justify a bind and is read for nothing else, so
    inventing a script to hold it would be a fourth validator for one file class."""
    if not RECONCILE_CONTRACT.is_file():
        print(f"cannot run: {RECONCILE_CONTRACT} is missing; nothing can be validated without it",
              file=sys.stderr)
        return CANNOT_RUN

    front, refusal = frontmatter_of(record)
    if front is None:
        print(f"cannot run: {refusal}", file=sys.stderr)
        return CANNOT_RUN

    if record.parent.name != RECONCILE_DIR:
        print(f"cannot run: {record} does not sit under {RECONCILE_DIR}/; a record that justifies "
              f"a bind lives where the trace it justifies lives, and one filed anywhere else is a "
              f"judgment the next reader has no way to find", file=sys.stderr)
        return CANNOT_RUN

    schema = json.loads(RECONCILE_CONTRACT.read_text(encoding="utf-8"))
    problems = [f"{'/'.join(str(part) for part in error.path) or 'record'}: {error.message}"
                for error in Draft202012Validator(schema).iter_errors(front)]
    if not problems:
        problems = accounted(front)
    home = home_of(record.parent)
    project_file = home / project.PROJECT_FILE
    if not problems and isinstance(front.get("target"), str) and project_file.is_file():
        if front["target"] not in target_roots(home):
            problems.append(f"target: names {front['target']!r}, which {project.PROJECT_FILE} "
                            f"does not declare as a key under `targets`; `--owed` cannot resolve "
                            f"this record's paths from a root nothing here can find, and would "
                            f"read it as unreadable forever")
    if problems:
        for problem in sorted(set(problems)):
            print(f"{record.name}: {problem}")
        print(f"\n{len(set(problems))} problem(s); this record binds nothing until they are gone.")
        return 1

    binds = [entry for entry in front["nodes"] if entry["conforms"]]
    held = [entry for entry in front["nodes"] if not entry["conforms"]]
    print(f"{record.name} holds: {len(front['files'])} file(s), {len(binds)} node(s) the judgment "
          f"cleared, {len(held)} it did not, {len(front.get('unbound') or [])} file(s) the trace "
          f"binds nothing to.")
    certifies = [entry for entry in binds if entry.get("decided_by") == DECIDED_BY_TEST]
    if certifies:
        print(f"{len(certifies)} node(s) certified as decided by a test — "
              + "; ".join(f"{entry['node']} by step `{entry['step']}` over "
                          f"{', '.join(entry['proof'])}" for entry in certifies)
              + ": --bind-record writes each binding as one a test decides, pinning the proof "
                "beside the files.")
    if held:
        print(f"--bind-record will write {len(binds)} binding(s) from this record and none for "
              f"{', '.join(entry['node'] for entry in held)}: a node without `encoded_at` is a "
              f"node this form cannot bind.")
    return 0


def encoded_in(record: Path) -> tuple[list[tuple[str, list[str]]], list[str]]:
    """Every node one implementation record says the source encodes, with the files it names.

    The record is the only thing that knows which nodes reached the code and where, and a caller
    that retyped both — one node per invocation — would hold the rule that a bind states exactly
    what the record says, and never a second judgment about it, by prose alone. Reading the record
    here makes that rule structural: a node it does not name cannot be bound from this
    form, and one it does cannot be skipped.

    A node the record answers only by `how` — constrained, encoded nowhere — is not here, and that
    is not an omission: there is no file to name, and a bind with none is refused.

    Nothing here validates the record as a delivery node. `bin/deliver.py` did that before this
    runs, and a second opinion about a contract this script does not own would be a second home for
    it. What this reads is two field names, defensively — which is also why a reconciliation record
    is read by this same form: it declares the same two, and `--reconciliation` is what held it to
    its own contract first."""
    front, refusal = frontmatter_of(record)
    if front is None:
        return [], [refusal]

    pairs = []
    for entry in front.get("nodes") or []:
        if not isinstance(entry, dict) or not isinstance(entry.get("node"), str):
            continue
        where = entry.get("encoded_at")
        if not isinstance(where, list):
            continue
        files = [f for f in where if isinstance(f, str)]
        if files:
            pairs.append((entry["node"], files))
    return pairs, []


def released_in(record: Path) -> set[str]:
    """Every node a reconciliation record says a certification was asked for and did not hold.

    A record answers the certification question three ways, and the third one has to be structural
    like the other two. `decided_by: test` certifies; absence says the reconciliation never asked,
    so a standing certification is none of its business and carries forward; `decided_by: reading`
    says it asked and the auditor refused — and the bind must then release what stands, or the
    trace goes on deciding by a test a judgment has just found cannot fail while the record's own
    notes say the node is decided by reading."""
    front = as_reconciliation(record)
    if front is None:
        return set()
    return {entry["node"] for entry in front.get("nodes") or []
            if isinstance(entry, dict) and isinstance(entry.get("node"), str)
            and entry.get("decided_by") == "reading"}


def withdrawn_receipt(declared: dict, node_id: str) -> str | None:
    """The receipt for a certification this bind released because the record refused it. Nothing
    where the node had none: a record may refuse a certification for a node that was never
    certified, and a receipt for a release that did not happen is noise."""
    existing = next((entry for entry in declared.get("bindings") or []
                     if entry.get("node") == node_id), None)
    if existing is None or existing.get("decided_by") != DECIDED_BY_TEST:
        return None
    return (f"  {node_id} is decided by reading from here: this record asked whether "
            f"{', '.join(e['path'] for e in existing.get('proof') or [])} still decides it and "
            f"the judgment answered that it does not, so the standing certification is released "
            f"rather than carried past the reading that refused it")


def certified_in(record: Path) -> dict[str, dict]:
    """Every node a reconciliation record certifies as decided by a test, with the step and the
    proof paths it names — spelled from the target source root, as the record spells everything.
    Empty for a delivery record and for a reconciliation that certified nothing. Read the way
    `encoded_in` reads its two field names: defensively, because `--reconciliation` is what held
    the record to its contract first, and a second opinion here would be a second home for it."""
    front = as_reconciliation(record)
    if front is None:
        return {}
    found: dict[str, dict] = {}
    for entry in front.get("nodes") or []:
        if not isinstance(entry, dict) or entry.get("decided_by") != DECIDED_BY_TEST:
            continue
        node_id, step, proof = entry.get("node"), entry.get("step"), entry.get("proof")
        if isinstance(node_id, str) and isinstance(step, str) and isinstance(proof, list):
            paths = [p for p in proof if isinstance(p, str)]
            if paths:
                found[node_id] = {"step": step, "proof": paths}
    return found


def reconciliation_or_reason(record: Path) -> tuple[dict | None, str | None]:
    """The record read as a reconciliation, or nothing — and, where it sits under
    `siegard-reconcile/` and cannot be read at all, the reason.

    Every reader here needs the same three-part guard — it sits under `siegard-reconcile/`, its
    frontmatter parses, and it declares this contract — and a delivery record must fall through
    every one of them, since `--bind-record` serves both forms. A record under the corpus
    directory whose frontmatter does not parse is the one case that comes back with a reason:
    it may hold an open finding, and a walk over the corpus that skipped it would report the
    corpus as holding none. The gates that read one record on its way through already refused
    it by name; the walkers are what must not lose it."""
    if record.parent.name != RECONCILE_DIR:
        return None, None
    front, why = frontmatter_of(record)
    if not isinstance(front, dict):
        said = why or "unreadable"
        if said.startswith(str(record)):
            said = said[len(str(record)):].lstrip(": ")
        return None, said
    version = front.get("contract_version")
    if not isinstance(version, str) or not version.startswith("siegard-reconcile/"):
        return None, None
    return front, None


def as_reconciliation(record: Path) -> dict | None:
    """The record read as a reconciliation, or nothing where it is not one — the single-record
    reading, for the gates that already refused an unreadable record by name once."""
    return reconciliation_or_reason(record)[0]


def withheld(record: Path) -> list[str]:
    """Every node a reconciliation record answered for and did not clear. Empty for a delivery
    record, which has no such class.

    A reconciliation is bound node by node — a node without `encoded_at` is one this form cannot
    reach, which is the whole of the join between the judgment and the trace — so a record
    carrying a finding writes the bindings that cleared and stops there. That is the right act:
    every line it writes is one a judgment stands behind, and the node it could not write stays
    exactly as it stood — reported by the next `--check` where a binding holds the pair, and by
    `--owed` alone where none does.

    The bind owes saying so here. `--reconciliation` names the held nodes before anything
    is written; without the receipt below, the bind's own output lists what it bound and nothing
    else, and a partial bind reads exactly like a complete one at the only moment the person who
    ran it is still looking.
    A bind that quietly reconciles thirty-eight of forty is the report this framework spends its
    receipts preventing."""
    front = as_reconciliation(record)
    if front is None:
        return []
    return sorted({entry["node"] for entry in front.get("nodes") or []
                   if isinstance(entry, dict) and isinstance(entry.get("node"), str)
                   and entry.get("conforms") is False})


def left_owed(held: list[str], record: Path) -> str:
    """The receipt for the nodes a reconciliation did not clear, printed by the bind that wrote
    the rest. The same discipline `left_stale()` sets one class over: nothing here is wrong — the
    bind stated exactly what the judgment cleared — but each node below is still owed, and this is
    the one moment the person who ran it is still holding the whole set."""
    lines = [f"  {len(held)} node(s) of {record.name} the judgment did not clear, and this bind "
             f"wrote none of them:"]
    lines += [f"    {node}" for node in held]
    lines.append("    each stays as it stood — its drift, where the file was bound before, is "
                 "still a finding on the next --check; where it was not, --owed is the only "
                 "report that will ever say so. The record says what was found against it")
    return "\n".join(lines)


def judged(home: Path) -> tuple[dict[tuple[str, str], list[str]],
                                dict[tuple[str, str], list[str]], list[str]]:
    """Every node/file pair the reconciliation records answered for, split by the answer, with the
    records each answer came from.

    This is the one place anything reads `siegard-reconcile/` as a corpus rather than as a single
    record on its way through a gate. `--reconciliation` reads a record to decide whether it holds;
    `--bind-record` reads the nodes it may write. Neither comes back, and what stays behind is the
    framework's only account of a conformance question a judgment answered and a bind could not
    close.

    Paths come back spelled from this file's own directory, the anchor the trace already uses,
    because that is what they are compared against. A record spells its own from its target's
    source root, and which root that is comes from the project file.

    No chronology is computed, and none is available to compute one from. A record carries no
    timestamp, and the commit that added it is not the moment its judgment ran: several land in a
    single commit, and a batch that reconciles twice in one session commits both at the end — so
    ordering by commit date reverses exactly the pair a reader most wants ordered. A pair with
    answers on both sides is therefore reported as answered both ways, and never resolved in favour
    of whichever looks later. Which judgment is current is a reading of the records; it is not a
    fact about their file dates, and inventing it here would put this framework's most durable
    claim on its thinnest evidence."""
    found: dict[tuple[str, str], list[str]] = {}
    cleared: dict[tuple[str, str], list[str]] = {}
    unreadable: list[str] = []
    directory = home / RECONCILE_DIR
    if not directory.is_dir():
        return found, cleared, unreadable
    roots = target_roots(home)
    for record in sorted(directory.glob("*.md")):
        front, why = reconciliation_or_reason(record)
        if front is None:
            if why is not None:
                unreadable.append(f"{record.name}: {why} — a record nobody can read may hold an "
                                  f"open finding, and nothing here reads around it")
            continue
        named = front.get("target")
        where = roots.get(named) if isinstance(named, str) else None
        if where is None:
            unreadable.append(f"{record.name}: names target {named!r}, which "
                              f"{project.PROJECT_FILE} does not declare — its paths are spelled "
                              f"from a root nothing here can resolve, so it is read by nothing")
            continue
        for entry in front.get("nodes") or []:
            if not isinstance(entry, dict) or not isinstance(entry.get("node"), str):
                continue
            node, conforms = entry["node"], entry.get("conforms")
            sink = cleared if conforms is True else found
            for path in entry.get("encoded_at" if conforms is True else "observed_at") or []:
                if not isinstance(path, str):
                    continue
                anchored = path if where == "." else f"{where}/{path}"
                sink.setdefault((node, anchored), []).append(record.name)
    return found, cleared, unreadable


def remainders_of(home: Path) -> tuple[dict[str, list[dict]], set[str]]:
    """Every node a refused certification left with a testable remainder, with the record that
    said so, the auditor's sentence and the files the node was cleared at — and, apart, every
    node some record certified as decided by a test.

    Read from the corpus the way `judged()` reads it, and for the same reason it is kept apart:
    a pair's finding is owed to a bind, a fact no node holds is owed to the analysis, and a
    testable remainder is owed to whoever writes the test — three debts to three parties, and
    one list would let a reader take the third for the first. Only the testable ones come back.
    An untestable remainder was said once, in its record, and a list that repeated it every time
    this ran would find something forever.

    Paths come back spelled from this file's own directory, the anchor the trace uses. No
    chronology is computed: a node with a testable remainder in one record and a certification in
    another is reported as answered both ways, never resolved in favour of whichever looks later."""
    testable: dict[str, list[dict]] = {}
    certified: set[str] = set()
    directory = home / RECONCILE_DIR
    if not directory.is_dir():
        return testable, certified
    roots = target_roots(home)
    for record in sorted(directory.glob("*.md")):
        front, _ = reconciliation_or_reason(record)
        if front is None:
            continue
        named = front.get("target")
        where = roots.get(named) if isinstance(named, str) else None
        if where is None:
            continue
        for entry in front.get("nodes") or []:
            if not isinstance(entry, dict) or not isinstance(entry.get("node"), str):
                continue
            if entry.get("decided_by") == DECIDED_BY_TEST:
                certified.add(entry["node"])
            if entry.get("remainder") != TESTABLE or not isinstance(entry.get("remainder_why"), str):
                continue
            files = [path if where == "." else f"{where}/{path}"
                     for path in entry.get("encoded_at") or [] if isinstance(path, str)]
            testable.setdefault(entry["node"], []).append(
                {"record": record.name, "why": entry["remainder_why"], "files": files})
    return testable, certified


def unstated_of(home: Path) -> list[dict]:
    """Every fact the records name that the source states and no node holds, with the record that
    named it and the file it was read in.

    Read from the corpus the same way `judged()` reads it, and kept apart from it for the reason
    the class exists: a pair's finding is owed to a bind, and a fact no node holds is owed to the
    analysis that gives it one. A record that cannot be read is `judged()`'s to name, once.
    Only `siegard-reconcile/3` and later records carry the list — an earlier record folded the
    same observation into a node's `conforms`, where it is indistinguishable from a
    contradiction, and nothing here rewrites one to say otherwise."""
    stated: list[dict] = []
    directory = home / RECONCILE_DIR
    if not directory.is_dir():
        return stated
    for record in sorted(directory.glob("*.md")):
        front, _ = reconciliation_or_reason(record)
        if front is None:
            continue
        for entry in front.get("unstated") or []:
            if not isinstance(entry, dict):
                continue
            if not all(isinstance(entry.get(f), str) for f in ("file", "where", "evidence", "cost")):
                continue
            stated.append(dict(entry, record=record.name))
    return stated


def owed_reading(target: Path) -> tuple[dict | None, list[str]]:
    """Everything `--owed` says, computed and not yet printed: the findings no bind closed by class,
    the pairs the records answer both ways, the unstated facts, and the nodes a refused
    certification left with a testable remainder — or the problems that stopped the reading.

    One home for the reading, because two forms now print from it: `--owed` in full, and
    `--convergence` as a tally kept beside the binding states. A second walk over the corpus
    would be a second reader of `siegard-reconcile/`, and the one thing this file says about that
    corpus is that `--owed` is its only reader."""
    home = home_of(target)
    offset = Path(os.path.relpath(target.resolve(), home.resolve())).as_posix()
    found, cleared, unreadable = judged(home)

    declared = load(target)
    bound: dict[tuple[str, str], str] = {}
    if declared is not None:
        problems = problems_of(declared)
        if problems:
            return None, [f"{trace_path(target)}: {problem}" for problem in problems]
        for entry in declared.get("bindings") or []:
            for held in entry.get("files") or []:
                if isinstance(held, dict) and isinstance(held.get("path"), str):
                    bound[(entry.get("node"), held["path"])] = held.get("digest")

    listed: dict[str, list[tuple[str, str, str]]] = {UNSEEN: [], COVERED: [], REPORTED: []}
    answered_both_ways = []
    for (node, path), records in sorted(found.items()):
        if not under(path, [offset]):
            continue
        where = ", ".join(sorted(set(records)))
        source = home / path
        stored = bound.get((node, path))
        if (node, path) in cleared:
            answered_both_ways.append((node, path, where,
                                       ", ".join(sorted(set(cleared[(node, path)]))),
                                       "no binding" if stored is None else
                                       "bound, and stale" if not source.is_file()
                                       or spec.digest_of(source) != stored else "bound, and current"))
            continue
        if stored is None:
            listed[UNSEEN].append((node, path, where))
        elif not source.is_file() or spec.digest_of(source) != stored:
            listed[REPORTED].append((node, path, where))
        else:
            listed[COVERED].append((node, path, where))

    testable, certified = remainders_of(home)
    live = test_decided(declared, home, offset) if declared is not None else {}
    by_reading = reading_counts(declared, home, offset) if declared is not None else {}
    listed_nodes = {node: said for node, said in testable.items()
                    if node not in live and node not in certified
                    and any(under(f, [offset]) for s in said for f in s["files"])}
    both_ways = sorted(node for node in testable if node in certified and node not in live)
    return {"home": home, "offset": offset, "unreadable": unreadable, "listed": listed,
            "both_ways_pairs": answered_both_ways, "stated": unstated_of(home),
            "testable_nodes": listed_nodes, "both_ways_nodes": both_ways,
            "by_reading": by_reading,
            "total": sum(len(rows) for rows in listed.values())}, []


def owed(target: Path, show_all: bool = False) -> int:
    """What the reconciliation records found against and no bind could close, by whether the drift
    report says it too.

    Three states, and only the third is one a reader already had. A pair nothing binds is one no
    `--check` can ever reach — the judge opened it as a candidate, or the fact it names lives in a
    file this one is not bound to — so its finding has exactly one home and this is it. A pair
    bound at the content on disk now is worse: it was reachable, and a bind stamped the very
    content the finding was read in, so the symptom is gone while the finding stands. A pair whose
    binding is stale is already in the drift report, and what this adds is the record that says
    what was found in it.

    A finding some record cleared is not listed. A clearance in the corpus is a closure, and
    printing every remediated pair would rebuild the unreadable report this file spends its
    receipts preventing — wherever remediation happens at all, the remediated pairs outnumber
    everything else here. The count rides a receipt instead, and `--all` lists them, exactly as
    the same flag already works one form over: two judgments answering one pair both ways is what
    that list shows, and it is worth a reader's attention for a different reason than a finding is."""
    if not target.is_dir():
        print(f"cannot run: {target} is not a directory", file=sys.stderr)
        return CANNOT_RUN

    reading, problems = owed_reading(target)
    if reading is None:
        for problem in problems:
            print(problem)
        return 1
    home, offset = reading["home"], reading["offset"]
    for problem in reading["unreadable"]:
        print(f"{RECONCILE_DIR}/{problem}")
    listed, answered_both_ways, total = reading["listed"], reading["both_ways_pairs"], reading["total"]

    if not total and not answered_both_ways and not reading["unreadable"]:
        # Said, and not returned on: what follows is owed to other parties than a bind — the
        # analysis, a test's author — and a record holding only those is not a record holding
        # nothing. Not said over a record nobody could read: what it holds is exactly what is
        # not known.
        print(f"nothing owed: no reconciliation record under {home / RECONCILE_DIR} holds a "
              f"finding against a node under {offset} that no record cleared")

    for cls in (UNSEEN, COVERED, REPORTED):
        rows = listed[cls]
        if not rows:
            continue
        print(f"{cls}: {OWED_CLASSES[cls]}")
        grouped: dict[str, list[tuple[str, str]]] = {}
        for node, path, where in rows:
            grouped.setdefault(path, []).append((node, where))
        for path, pairs in sorted(grouped.items()):
            print(f"  {path}")
            for node, where in sorted(pairs):
                print(f"    {node} — found against in {where}")

    if total:
        files = {path for rows in listed.values() for _, path, _ in rows}
        print(f"\n{total} finding(s) no bind closed, over {len(files)} file(s):")
        for cls in (UNSEEN, COVERED, REPORTED):
            print(f"  {len(listed[cls])} {cls}: {OWED_CLASSES[cls]}")
        silent = len(listed[UNSEEN]) + len(listed[COVERED])
        if silent:
            print(f"  {silent} of them appear in no --check report, and nothing about the files "
                  f"has to change for that to stay true; this form is where they are said")

    if answered_both_ways:
        print(f"\n{len(answered_both_ways)} pair(s) the records answer both ways are not listed "
              f"above: a clearance closes a finding here. No chronology is available — a record "
              f"carries no timestamp and several land in one commit — so which judgment is "
              f"current is a reading of the records themselves.")
        if show_all:
            for node, path, against, by, state in answered_both_ways:
                print(f"  {path}")
                print(f"    {node} — found against in {against}; cleared in {by}; "
                      f"the trace holds it {state}")
        else:
            print("  `--all` lists them, each with what the trace holds for it now")

    # Reported apart from everything above, because it is owed to somebody else. A pair's finding
    # waits on a bind; a fact no node holds waits on the analysis that gives it one, and counting
    # the two together is what let a correct binding read as contested for as long as the gap stood.
    stated = reading["stated"]
    if stated:
        print(f"\n{len(stated)} unstated fact(s) the records name, over "
              f"{len({e['file'] for e in stated})} file(s) — the source states them and no node "
              f"holds them. No bind closes one and none is counted above:")
        rows = sorted(stated, key=lambda e: (e["file"], e["where"]))
        for entry in (rows if show_all else rows[:RANK_HELD_BACK]):
            print(f"  {entry['file']} — {entry['where']}: {entry['cost']} [{entry['record']}]")
        if not show_all and len(rows) > RANK_HELD_BACK:
            print(f"  ... and {len(rows) - RANK_HELD_BACK} more; `--all` lists them")
        print("  each is the analysis's to close, through the node that gives the fact a home")

    # Owed to a third party again: a certification the auditor refused while saying a test could
    # close what is left. Nothing here binds anything and nothing counts above. The file's own
    # count of bindings a reading decides is printed beside each, because the saving a test buys
    # is per file — a judge reads the whole file for the first binding a reading still decides —
    # and a node closed on a file with nine reading-decided siblings frees no judge yet.
    listed_nodes, both_ways, by_reading = (reading["testable_nodes"], reading["both_ways_nodes"],
                                           reading["by_reading"])
    if listed_nodes:
        print(f"\n{len(listed_nodes)} node(s) a refused certification left decided by reading with "
              f"a testable remainder — the auditor named the assertion that would close each, and "
              f"a node a certified test decides pays no judge again:")
        rows = sorted(listed_nodes.items())
        for node, said in (rows if show_all else rows[:RANK_HELD_BACK]):
            records = ", ".join(sorted({s["record"] for s in said}))
            print(f"  {node} [{records}]")
            for why in sorted({s["why"] for s in said}):
                print(f"    would close it: {why}")
            for path in sorted({f for s in said for f in s["files"] if under(f, [offset])}):
                spelled = (path if offset in (".", "")
                           else PurePosixPath(path).relative_to(offset).as_posix())
                counts = by_reading.get(path)
                if counts is None:
                    print(f"    {spelled} — the trace binds nothing to this file now")
                    continue
                reading_n, step, test = counts
                print(f"    {spelled} — {reading_n} binding(s) a reading decides on this file"
                      + (f", {step} by a registry step" if step else "")
                      + (f", {test} by a certified test" if test else "")
                      + ("; closing this one frees its judge" if reading_n == 1 else ""))
        if not show_all and len(rows) > RANK_HELD_BACK:
            print(f"  ... and {len(rows) - RANK_HELD_BACK} more; `--all` lists them")
        print("  each is closed by writing the test named, and the route that writes it is a "
              "proof increment: `/deliver-scope`, with an ask naming the proof increment and, "
              "per fact to close, the node, the assertion verbatim, the record in brackets and "
              "the files above, spelled from the target source root as printed — /plan-work "
              "plans one task per fact, /implement-task writes the "
              "proof alone, and the review certifies it. Which facts are worth a test is the "
              "asker's; name the ones wanted, under a new slug")
    if both_ways:
        print(f"\n{len(both_ways)} node(s) with a testable remainder in one record and a "
              f"certification in another are not listed above, and the trace holds no live "
              f"certification for them; which is current is a reading of the records: "
              f"{', '.join(both_ways)}")
    return 1 if total or reading["unreadable"] else 0


def convergence(target: Path, spec_root: Path, parent: Path, show_all: bool = False) -> int:
    """Every node of the specification in exactly one state, read across the trace and every
    initiative — live, closed, or archived out of the tree — with the judged side kept beside it.

    The four readings this composes exist and are each correct alone: `--check` says which
    bindings moved, `--owed` what the records found, `deliver.py --outstanding` what a live plan
    still owes, `plan.py --unplanned` what no plan named. Composed by hand they answer wrongly,
    and the ways they answer wrongly are the semantics this form encodes once: an initiative
    `/siegard-archive` removed still planned what it named; an epic's `uncovered` is a decision
    and not a gap; a node a delivery honored without encoding is bound to nothing by design; a
    file a project declared freely edited is stale in fact and held back from the report on
    purpose. A reader who knows three of the four reports a healthy tree as one carrying dozens of
    nodes nobody asked for.

    A query and never a check: exit 0 over whatever it finds, counted by class, no figure. A node
    the work has not reached is an ordinary state of a specification, and a form that graded it
    would be a number that must rise — and satisfying it produces bindings nobody needed. The
    judged side is printed apart and said to be apart: a binding that computes is a fact about
    bytes, and a record that found against a node is a fact about a reading, and a tally that
    added them would be a reading of neither."""
    for where, what in ((target, "target source root"), (spec_root, "specification root"),
                        (parent, "work root")):
        if not where.is_dir():
            print(f"cannot run: {what} {where} is not a directory", file=sys.stderr)
            return CANNOT_RUN
    if any((parent / kind).is_dir() for kind in plan.KINDS):
        print(f"cannot run: {parent} holds {'/'.join(plan.KINDS)} directories of its own, so it "
              f"is one initiative rather than the directory they sit in; name its parent",
              file=sys.stderr)
        return CANNOT_RUN

    spec_nodes, spec_problems = plan.load_base(spec_root)
    if spec_problems:
        for problem in spec_problems:
            print(problem, file=sys.stderr)
        print(f"cannot run: the specification at {spec_root} does not hold together "
              f"({len(spec_problems)} problem(s) above); fix it with spec.py first",
              file=sys.stderr)
        return CANNOT_RUN
    normative = {nid: node for nid, node in spec_nodes.items()
                 if node["cls"] not in ("log", "context")}

    home = home_of(target)
    declared = load(target)
    bound: set[str] = set()
    stale: set[str] = set()
    held_only: set[str] = set()
    bindings = 0
    if declared is not None:
        problems = problems_of(declared)
        if problems:
            for problem in problems:
                print(f"{trace_path(target)}: {problem}")
            return 1
        written_against = (home / declared["specification"]).resolve()
        if written_against != spec_root.resolve():
            print(f"cannot run: the trace at {trace_path(target)} was written against "
                  f"{written_against}, and a convergence read against {spec_root} would be an "
                  f"answer about a different specification", file=sys.stderr)
            return CANNOT_RUN
        bindings = len(declared.get("bindings") or [])
        bound = {e["node"] for e in declared.get("bindings") or [] if isinstance(e.get("node"), str)}
        findings, refusals = drift_of(declared, home, registry_steps(home, offset_of(target, home)))
        if refusals:
            for refusal in refusals:
                print(refusal)
            return 1
        listed, held = partitioned(findings, freely_edited(home))
        stale = {f[1] for f in findings}
        held_only = {f[1] for f in held} - {f[1] for f in listed}

    how, read, unreadable = plan.naming_on_disk(parent, plan.contract())
    archived_how, archived, unparsed, no_git = plan.naming_archived(parent)
    for node, fields in archived_how.items():
        how.setdefault(node, set()).update(fields)

    state_of: dict[str, str] = {}
    for nid in normative:
        if nid in bound:
            state_of[nid] = STALE if nid in stale else CURRENT
        elif fields := how.get(nid):
            # An epic declares a node uncovered only over a node it covers, so `covers` rides
            # beside `uncovered` on the same node and decides nothing by itself. What says the work
            # reaches a node is a task implementing it anywhere, or a cover no epic declared
            # uncovered.
            reached = "implements" in fields or ("covers" in fields and "uncovered" not in fields)
            state_of[nid] = PLANNED_UNBOUND if reached else DECLARED_UNCOVERED
        else:
            state_of[nid] = UNREACHED
    bound_unplanned = sorted(nid for nid in bound & set(normative) if nid not in how)

    print(f"{len(normative)} node(s) of {spec_root}; "
          + (f"{bindings} binding(s) in {trace_path(target)}" if declared is not None
             else f"no trace file at {trace_path(target)} — nothing has been bound yet"))
    print(f"{len(read)} initiative(s) read under {parent}"
          + (f"; {len(unreadable)} do not hold together and were read for what they state "
             f"({', '.join(unreadable)})" if unreadable else ""))
    if no_git is not None:
        print(f"  initiatives archived out of this tree, if any, were not read: {no_git}; a node "
              f"such a plan named is counted below as one nothing planned")
    else:
        print(f"  {len(archived)} archived initiative(s) read from git at the commit before each "
              f"was removed" + (f"; {unparsed} file(s) could not be parsed" if unparsed else ""))

    print()
    for state in (CURRENT, STALE, PLANNED_UNBOUND, DECLARED_UNCOVERED, UNREACHED):
        members = sorted(nid for nid, s in state_of.items() if s == state)
        by_cls: dict[str, int] = {}
        for nid in members:
            by_cls[normative[nid]["cls"]] = by_cls.get(normative[nid]["cls"], 0) + 1
        print(f"{len(members)} {state}: {CONVERGENCE[state]}")
        if by_cls:
            print("    " + ", ".join(f"{cls} {n}" for cls, n in sorted(by_cls.items())))
        if show_all:
            for nid in members:
                print(f"      {nid}")
    if held_only:
        print(f"  of the stale, {len(held_only)} node(s) are stale only under a target this project "
              f"declares freely edited — `--check` holds those back, and this form counts them")
    if bound_unplanned:
        print(f"\n{len(bound_unplanned)} bound node(s) no initiative names — bound by a "
              f"reconciliation over source that entered outside any task, or by a raw --bind; "
              + ("each:" if show_all else "`--all` lists them"))
        if show_all:
            for nid in bound_unplanned:
                print(f"    {nid}")

    reading, problems = owed_reading(target)
    print()
    if reading is None:
        for problem in problems:
            print(problem)
    else:
        listed = reading["listed"]
        print(f"Kept apart — the judged side, which no state above counts: "
              f"{reading['total']} finding(s) past reconciliations left open and no bind closed "
              f"({len(listed[UNSEEN])} unseen, {len(listed[COVERED])} covered, "
              f"{len(listed[REPORTED])} reported); {len(reading['both_ways_pairs'])} pair(s) the "
              f"records answer both ways; {len(reading['stated'])} unstated fact(s) the source "
              f"states and no node holds; {len(reading['testable_nodes'])} node(s) a refused "
              f"certification left with a testable remainder. A binding that computes is a fact "
              f"about bytes and a record that found against a node is a fact about a reading — "
              f"`--owed` names each record.")
    return 0


def encodes(target: Path, files: list[str]) -> int:
    """Which specification nodes the trace binds to each named file, and whether each binding still
    computes.

    The drift report cannot answer this and was never meant to: it is keyed by drift, so a file is
    in it because it changed. A file whose bindings are all intact is absent from it and reads
    exactly like a file the trace binds nothing to — two states a reconciliation's locate step has
    to tell apart before it can hand a judge a node set, since the second is a file to report and
    the first is a file whose nodes still have to be read. Getting it meant opening the trace and
    reading the bindings by hand, which nothing validates: a binding missed there is a judge handed
    a node set short one node, and the record that comes back reads exactly like a complete one.

    A query and never a check. Every stale binding it prints is a `code` finding `--check` already
    reports, so reporting it as a failure here would give one drift two exit statuses."""
    if not target.is_dir():
        print(f"cannot run: {target} is not a directory", file=sys.stderr)
        return CANNOT_RUN

    home = home_of(target)
    declared = load(target)
    if declared is None:
        print(f"no trace file: {trace_path(target)} does not exist; nothing has been bound in "
              f"this target, so every named file is one the trace binds nothing to")
        return 0

    traced, problems = traced_files_of(target, home, files)
    for problem in problems:
        print(f"cannot run: {problem}", file=sys.stderr)
    if problems:
        return CANNOT_RUN

    index: dict[str, list[tuple[str, str]]] = {}
    # A test the trace pins as some node's proof is a file this form is asked about like any
    # other, and answering that the trace binds nothing to it is false where the trace names it
    # by path. It is not a binding — the node is not encoded there — so it is said apart: what a
    # proof answers for is whether the fact holds, never where it lives.
    proves: dict[str, list[tuple[str, str]]] = {}
    for entry in declared.get("bindings") or []:
        for held in entry.get("files") or []:
            if isinstance(held, dict) and isinstance(held.get("path"), str):
                index.setdefault(held["path"], []).append((entry.get("node"),
                                                           held.get("digest")))
        for held in entry.get("proof") or []:
            if isinstance(held, dict) and isinstance(held.get("path"), str):
                proves.setdefault(held["path"], []).append((entry.get("node"),
                                                            held.get("digest")))
    decided = decided_constraints(home, offset_of(target, home))
    by_test = test_decided(declared, home, offset_of(target, home))

    def proof_lines(path: str, now: str) -> list[str]:
        return [f"  proof of {node} — "
                f"{'certified over this text' if stored == now else 'the test changed since it was certified'}"
                for node, stored in sorted(proves.get(path) or [])]

    for held in traced:
        path, now = held["path"], held["digest"]
        rows = sorted(index.get(path) or [])
        if not rows:
            if path in proves:
                print(f"{path}: the trace binds no node to this file, and pins it as the proof "
                      f"of {len(proves[path])} binding(s)")
                for line in proof_lines(path, now):
                    print(line)
            else:
                print(f"{path}: the trace binds nothing to this file")
            continue
        print(f"{path}: {len(rows)} binding(s)")
        for node, stored in rows:
            if node in by_test:
                beside = f"; a certified test decides it (step `{by_test[node]}`)"
            elif node in decided:
                beside = (f"; a registry step decides it "
                          f"({', '.join(f'`{s}`' for s in decided[node])})")
            else:
                beside = ""
            print(f"  {node} — "
                  f"{'matches' if stored == now else 'stale: the file changed without a rebind'}"
                  f"{beside}")
        for line in proof_lines(path, now):
            print(line)
    return 0


def changed_paths(home: Path, ref: str | None) -> tuple[list[str], str | None]:
    """Every path the tree changed, spelled from the git toplevel, and what went wrong instead.

    With no ref this is the working tree against `HEAD` — staged, unstaged and untracked
    together, which is the set standing in front of a caller about to commit. With one it is what
    the branch changed since that ref, which is the set a reviewer of the branch is holding."""
    if ref is None:
        try:
            has_head = subprocess.run(["git", "-C", str(home), "rev-parse", "--verify", "HEAD"],
                                      capture_output=True, text=True)
        except OSError:
            return [], "git is not on this machine, and the changed set is git's to name"
        if has_head.returncode != 0:
            # Git's own message for this is its usage blurb, which says nothing a reader can act
            # on. Before the first commit there is no HEAD to compare against and every file is
            # new, so the whole tree would be the answer — which is no answer about a change.
            return [], (f"{home} holds no commit yet, so there is no HEAD to compare against and "
                        f"every file in it is new; commit the tree, or name a ref this form can "
                        f"read the change against")
        commands = [["diff", "--name-only", "HEAD"],
                    ["ls-files", "--others", "--exclude-standard"]]
    else:
        commands = [["diff", "--name-only", f"{ref}...HEAD"]]
    found: list[str] = []
    for command in commands:
        try:
            probe = subprocess.run(["git", "-C", str(home), *command],
                                   capture_output=True, text=True)
        except OSError:
            return [], "git is not on this machine, and the changed set is git's to name"
        if probe.returncode != 0:
            said = probe.stderr.strip().splitlines()
            return [], (said[-1] if said else f"git {' '.join(command)} failed in {home}")
        found += [line for line in probe.stdout.splitlines() if line]
    return sorted(set(found)), None


def encodes_changed(target: Path, ref: str | None) -> int:
    """`--encodes` over what the tree changed rather than over a set a caller spelled out.

    The conversion is the whole of what this adds. Git names every path from the toplevel and
    `--encodes` reads every path from the target source root, so composing the two by hand is the
    one step a caller gets wrong — and gets wrong silently where the wrong spelling happens to
    name a file that exists. A path outside this target is dropped rather than refused: one
    commit touching two targets is an ordinary commit, and the answer over this one is still
    whole. A file the tree deleted is dropped the same way and counted in the receipt: it has no
    digest to read, and what its bindings are now is `--check`'s question, not this one."""
    if not target.is_dir():
        print(f"cannot run: {target} is not a directory", file=sys.stderr)
        return CANNOT_RUN
    home = home_of(target)
    if home.resolve() == target.resolve() and not (home / ".git").exists():
        # `toplevel_of` answers the directory itself where git does not hold it, which every
        # other form treats as an ordinary anchor. Here it would mean an empty changed set
        # reported as a clean answer, which is the one reading this must not produce.
        print(f"cannot run: git does not hold {target}, and the changed set is git's to name",
              file=sys.stderr)
        return CANNOT_RUN
    paths, refused = changed_paths(home, ref)
    if refused is not None:
        print(f"cannot run: {refused}", file=sys.stderr)
        return CANNOT_RUN

    inside, outside, gone = [], 0, 0
    for path in paths:
        whole = home / path
        try:
            spelled = whole.resolve().relative_to(target.resolve()).as_posix()
        except ValueError:
            outside += 1
            continue
        if not whole.is_file():
            gone += 1
            continue
        inside.append(spelled)

    said = (f"against {ref}" if ref is not None else "in the working tree against HEAD")
    print(f"{len(paths)} path(s) changed {said}; {len(inside)} under {target}"
          + (f", {outside} under another target" if outside else "")
          + (f", {gone} no longer on disk — `--check` is what answers for a file that is gone"
             if gone else ""))
    if not inside:
        print("nothing changed under this target source root; no binding is in question here")
        return 0
    print()
    return encodes(target, inside)


def registry_steps(home: Path, offset: str) -> set[str] | None:
    """Every step name this target's registry declares, or nothing where the project declares no
    registry for it — which is not the same as a registry declaring no step, and is why the
    absence is `None` rather than an empty set. Nothing is held to a registry nobody named."""
    registry = registry_of(home, offset)
    if registry is None:
        return None
    return {c["step"] for c in registry.get("commands") or []
            if isinstance(c, dict) and isinstance(c.get("step"), str)}


def test_decided(declared: dict, home: Path, offset: str | None = None) -> dict[str, str]:
    """Every node the trace binds as decided by a test *and whose certification still stands*,
    with the step that runs it.

    Two things are recomputed rather than taken from the fields, because a certification is a
    claim about the world and the fields are only what it claimed. The proof's digests: a
    certification whose test's text moved is what `drift_of` reports under `proof`, and what it
    says there is that the binding is decided by reading until a judgment certifies the test as it
    now stands — a reader built on the field alone would be told by one line of a report that the
    certification lapsed and by another that the step's run answers for the pair, and acting on the
    second skips the reading the first says is owed. And the step: a registry that renamed or
    dropped it leaves the binding naming a step nothing can run, which `--stage` would then put in
    a mechanical tier no run could ever answer — a pair with no judge and no runnable step is the
    one state this route has no exit from."""
    steps = registry_steps(home, offset) if offset is not None else None
    live = {}
    for entry in declared.get("bindings") or []:
        if not isinstance(entry, dict) or entry.get("decided_by") != DECIDED_BY_TEST \
                or not isinstance(entry.get("step"), str):
            continue
        if steps is not None and entry["step"] not in steps:
            continue
        proof = entry.get("proof") or []
        if all(isinstance(held, dict) and (home / held["path"]).is_file()
               and spec.digest_of(home / held["path"]) == held["digest"] for held in proof):
            live[entry["node"]] = entry["step"]
    return live


RANK_HELD_BACK = 15


def rank(target: Path, show_all: bool = False) -> int:
    """The trace's two accretion axes, as counts: files by how many bindings claim them, and
    nodes by how many of this target's files they are bound to. Facts and never verdicts — a
    count high on either axis is where an audit pays for itself, and which counts those are is a
    person's reading, not this script's.

    This is the question drift cannot ask. Every other report here is keyed by change: a binding
    over-broad from the day it was written never drifts, so nothing keyed by change ever
    re-examines it, and the only symptom it has is a count that keeps growing. Filtered to the
    named target the way `--owed` filters, because that is the scope an audit's file set is
    named in. The listing holds back the tail the way `--check` holds back a suppressed class:
    the top of a ranking is what a reader acts on, and `--all` lists every row."""
    if not target.is_dir():
        print(f"cannot run: {target} is not a directory", file=sys.stderr)
        return CANNOT_RUN
    declared = load(target)
    if declared is None:
        print(f"no trace file: {trace_path(target)} does not exist; nothing has been bound in "
              f"this target, so there is nothing to rank")
        return 0
    problems = problems_of(declared)
    if problems:
        for problem in problems:
            print(f"{trace_path(target)}: {problem}")
        return 1

    home = home_of(target)
    offset = Path(os.path.relpath(target.resolve(), home.resolve())).as_posix()
    per_file: dict[str, int] = {}
    per_node: dict[str, int] = {}
    for entry in declared.get("bindings") or []:
        held = [f["path"] for f in entry.get("files") or []
                if isinstance(f, dict) and isinstance(f.get("path"), str)
                and under(f["path"], [offset])]
        if held:
            per_node[entry["node"]] = len(held)
        for path in held:
            per_file[path] = per_file.get(path, 0) + 1

    pairs = sum(per_file.values())
    print(f"{pairs} binding pair(s) over {len(per_file)} file(s) and {len(per_node)} node(s) "
          f"under {offset}")
    for title, counted in (("files by bindings held", per_file),
                           ("nodes by files bound", per_node)):
        rows = sorted(counted.items(), key=lambda row: (-row[1], row[0]))
        shown = rows if show_all else rows[:RANK_HELD_BACK]
        print(f"\n{title}:")
        for name, count in shown:
            print(f"  {count:3d}  {name}")
        if len(rows) > len(shown):
            print(f"  ({len(rows) - len(shown)} more; --all lists every one)")

    # The third axis is the one a reconciliation's cost turns on. A judge is spawned per file and
    # reads every binding on it, so a file pays that judge in full for the one binding a reading
    # still decides — however many of its siblings a registry step already settles. Counted here
    # by what a reading decides, with the step-decided remainder beside it, so a reader sees which
    # files a tool already answers for and which still need a judge at all.
    by_reading = reading_counts(declared, home, offset)
    rows = sorted(by_reading.items(), key=lambda row: (-row[1][0], row[0]))
    shown = rows if show_all else rows[:RANK_HELD_BACK]
    print(f"\nfiles by bindings a reading decides (a judge reads the whole file for the first of "
          f"them):")
    for name, (reading, step, test) in shown:
        parts = ([f"{step} decided by a registry step"] if step else []) \
            + ([f"{test} by a certified test"] if test else [])
        beside = f"  ({', '.join(parts)})" if parts else ""
        print(f"  {reading:3d}  {name}{beside}")
    if len(rows) > len(shown):
        print(f"  ({len(rows) - len(shown)} more; --all lists every one)")
    return 0


def reading_counts(declared: dict, home: Path, offset: str) -> dict[str, tuple[int, int, int]]:
    """Each file's bindings under the offset, counted by what decides them: a reading, a registry
    step, a certified test — in that order. The first count is what a reconciliation's cost turns
    on, and `--rank` and `--owed` both print it so a reader prices a file the same way in each."""
    decided = decided_constraints(home, offset)
    by_test = test_decided(declared, home, offset)
    by_reading: dict[str, tuple[int, int, int]] = {}
    for entry in declared.get("bindings") or []:
        for held in entry.get("files") or []:
            path = held.get("path") if isinstance(held, dict) else None
            if not isinstance(path, str) or not under(path, [offset]):
                continue
            reading, step, test = by_reading.get(path, (0, 0, 0))
            if entry["node"] in by_test:
                by_reading[path] = (reading, step, test + 1)
            elif entry["node"] in decided:
                by_reading[path] = (reading, step + 1, test)
            else:
                by_reading[path] = (reading + 1, step, test)
    return by_reading


def return_name(given: str) -> str:
    """The filename one delegation's return is saved under, computed from the path it judged.
    Flat on purpose: the returns directory is read as a set keyed by file, and a nested copy of
    the source tree would make a stray return — one no staged file explains — hard to even see."""
    return given.replace("/", "__") + ".yaml"


def open_owed(home: Path, corpus: tuple | None = None) -> set[tuple[str, str]]:
    """Every node/file pair the reconciliation corpus holds an open finding against — found by
    some record and cleared by none. A pair answered both ways is not here: a clearance in the
    corpus closes a finding, which is the same reading `--owed` already reports by. A caller
    that already walked the corpus hands it over as `corpus`, and it is not walked again."""
    found, cleared, _ = corpus if corpus is not None else judged(home)
    return {pair for pair in found if pair not in cleared}


def certifications_of(path: Path) -> tuple[list[dict], list[str]]:
    """The certifications a caller asks a staging for, read from their file: a YAML list, each
    entry a `node`, its `proof` — one or more test paths spelled from the target source root — and
    the registry `step` that runs them. Shape alone is decided here; whether each names a node the
    set encodes, a test that exists and a step the registry declares is the staging's, which has
    the trace, the tree and the registry in hand."""
    if not path.is_file():
        return [], [f"{path} does not exist"]
    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as broken:
        return [], [f"{path} does not parse: {broken}"]
    if isinstance(loaded, dict) and isinstance(loaded.get("certify"), list):
        loaded = loaded["certify"]
    if not isinstance(loaded, list) or not loaded:
        return [], [f"{path} holds no list of certifications; each entry is a node, its proof "
                    f"and the step that runs it"]
    problems, entries = [], []
    for index, entry in enumerate(loaded):
        if not isinstance(entry, dict):
            problems.append(f"{path}: entry {index} is not a mapping")
            continue
        node_id, proof, step = entry.get("node"), entry.get("proof"), entry.get("step")
        if isinstance(proof, str):
            proof = [proof]
        if not isinstance(node_id, str) or not isinstance(step, str) \
                or not isinstance(proof, list) or not proof \
                or not all(isinstance(p, str) for p in proof):
            problems.append(f"{path}: entry {index} needs `node`, `step` and a non-empty `proof` "
                            f"list of paths")
            continue
        entries.append({"node": node_id, "proof": list(dict.fromkeys(proof)), "step": step})
    named = [entry["node"] for entry in entries]
    problems += [f"{path}: {node_id} is certified {named.count(node_id)} times; one certification "
                 f"per node" for node_id in sorted(set(named)) if named.count(node_id) > 1]
    return entries, problems


def demonstrated_certifications(records: list[Path], home: Path,
                                offset: str) -> tuple[list[dict], list[str]]:
    """One certification per node the named proof records' tests claim to demonstrate: its proof
    the file of every test carrying that claim, its step the registry's `role: suite` command.

    Read defensively: `deliver.py` is what holds a proof record to its contract, and a record
    that does not parse or carries no `tests` composes nothing and says so. The step is the
    registry's to name and never this script's to guess — a registry declaring no suite step, or
    a project declaring no registry for this target, refuses the composition whole, since a
    certification names the step that runs its proof and one with none can never be answered."""
    entries: dict[str, set[str]] = {}
    problems: list[str] = []
    for record in records:
        front, _, unreadable = spec.parse_node(record)
        if front is None or not isinstance(front, dict):
            problems.append(f"{record}: {unreadable or 'carries no frontmatter this can read'}")
            continue
        tests = front.get("tests")
        if not isinstance(tests, list):
            continue
        for test in tests:
            if not isinstance(test, dict):
                continue
            node_id, path = test.get("demonstrates"), test.get("file")
            if isinstance(node_id, str) and isinstance(path, str):
                entries.setdefault(node_id, set()).add(path)
    if not entries:
        return [], problems
    registry = registry_of(home, offset)
    suite = [c["step"] for c in (registry or {}).get("commands") or []
             if isinstance(c, dict) and c.get("role") == "suite" and isinstance(c.get("step"), str)]
    if len(suite) != 1:
        problems.append(
            f"the proofs claim {len(entries)} node(s) demonstrated and "
            + ("the project declares no registry for this target" if registry is None else
               f"the registry declares {len(suite)} step(s) carrying `role: suite`")
            + "; a certification names the step that runs its proof, and the suite step is the "
              "registry's to declare, once")
        return [], problems
    composed = [{"node": node_id, "proof": sorted(paths), "step": suite[0]}
                for node_id, paths in sorted(entries.items())]
    return composed, problems


def stage(target: Path, spec_root: Path, slug: str, workspace: Path,
          files: list[str], audit: bool = False, review: bool = False,
          also: list[str] | None = None, certify: Path | None = None,
          demonstrated: list[Path] | None = None) -> int:
    """Prepare a reconciliation's workspace: the node set per file, one node pack per file, the
    batch's candidate index, and every pair whose re-judgment would buy a second reading of text
    that did not move. Everything here is computed from the trace, the specification and the
    corpus — nothing is chosen, so nothing here is a judgment.

    A review stages the files a delivery just wrote, and two things differ from a reconciliation
    over a hand edit. The omission narrows to what a judgment read: a delivery's own bind stamped
    its nodes over these exact bytes without anyone reading them against the node, so current
    digests alone would hand the review's judge every binding except the ones the review exists to
    re-read. A pair
    is omitted only where its file entry carries `judged` — a reconciliation's judgment cleared it
    at these bytes — its node's text is unchanged, no finding stands against it in the corpus, and
    its node is not one of the delivery's own under `also`. And the candidate tier stays, unlike an
    audit's, because here a misattribution reported as a gap is a false finding against a collateral
    node — a binding the delivery never claimed and its record never justified — and a false finding
    blocks that node's rebind. The nodes given as `also` are the plan's: every file's judge reads
    them beside the trace's own set and answers for them, so a fact the delivery wrote against a
    node its record did not bind is still read against that node, but they are never bound from here
    — a binding the review wrote would be a claim no implementation record made. A file the trace
    binds nothing to is still handed a judge over them alone, where it would otherwise be reported
    and skipped.

    The workspace is a reading copy and never a home. The packs restate node text so a judge
    reads its whole set in one act instead of one call per node, and they are trustworthy for
    exactly as long as nothing moves — which is the reconciliation's own precondition, since the
    named files must be committed and the bind stamps what is on disk. Each pack entry names its
    source path and the digest staging read, so a doubted line has one authority to open.

    The returns directory is the one thing staged outside the workspace, because it outlives it:
    the returns are the evidence the record is folded from, and a record whose raw answers
    survive nowhere is a judgment nobody can reopen. It is created empty beside the record's own
    reserved path, and a slug either of them already holds is the same stop a taken record slug
    has always been."""
    also = list(dict.fromkeys(also or []))
    if not target.is_dir():
        print(f"cannot run: {target} is not a directory", file=sys.stderr)
        return CANNOT_RUN
    if not spec_root.is_dir():
        print(f"cannot run: {spec_root} is not a directory", file=sys.stderr)
        return CANNOT_RUN
    declared = load(target)
    if declared is None:
        print(f"no trace file: {trace_path(target)} does not exist; nothing has been bound in "
              f"this target, so there is no binding to reconcile and what the caller wants is a "
              f"delivery", file=sys.stderr)
        return CANNOT_RUN
    problems = problems_of(declared)
    if problems:
        for problem in problems:
            print(f"{trace_path(target)}: {problem}")
        return 1
    nodes, status = sound_specification(spec_root)
    if nodes is None:
        return status
    unknown = [node_id for node_id in also if node_id not in nodes]
    if unknown:
        print(f"cannot run: {spec_root} holds no node {', '.join(unknown)}; a --node is read on "
              f"every file as the specification states it, and one the specification does not "
              f"hold is nothing to read", file=sys.stderr)
        return CANNOT_RUN
    descriptors = [node_id for node_id in also if is_descriptor(node_id)]
    if descriptors:
        print(f"cannot run: --node {', '.join(descriptors)} {DESCRIPTOR_REFUSAL}; name the "
              f"context's elements, rules, scenarios, contracts or constraints instead",
              file=sys.stderr)
        return CANNOT_RUN

    home = home_of(target)
    record_path = home / RECONCILE_DIR / f"{slug}.md"
    returns_dir = home / RECONCILE_DIR / f"{slug}.returns"
    for taken in (record_path, returns_dir):
        if taken.exists():
            print(f"cannot run: {taken} already exists; a slug is one reconciliation's name, and "
                  f"what stands there is the justification for bindings still in the trace",
                  file=sys.stderr)
            return CANNOT_RUN

    traced, path_problems = traced_files_of(target, home, files)
    for problem in path_problems:
        print(f"cannot run: {problem}", file=sys.stderr)
    if path_problems:
        return CANNOT_RUN
    current = {entry["path"]: entry["digest"] for entry in traced}

    offset = Path(os.path.relpath(target.resolve(), home.resolve())).as_posix()
    stored_of = {given: (given if offset == "." else f"{offset}/{given}") for given in files}

    index: dict[str, list[tuple[str, str]]] = {}
    bound_digest: dict[str, str] = {}
    judged_pairs: set[tuple[str, str]] = set()
    for entry in declared.get("bindings") or []:
        bound_digest[entry["node"]] = entry.get("digest")
        for held in entry.get("files") or []:
            if isinstance(held, dict) and isinstance(held.get("path"), str):
                index.setdefault(held["path"], []).append((entry["node"], held["digest"]))
                if held.get(JUDGED) is True:
                    judged_pairs.add((entry["node"], held["path"]))

    # A certification asks the staging to hand a node and its offered tests to the auditor. It is
    # refused before anything is written where the ask cannot be judged: a node no named file
    # encodes has no reading here to ride, a proof that is not there is a test nobody can open,
    # and a step the registry does not declare is one no run will ever answer for.
    certify_entries: list[dict] = []
    certify_problems: list[str] = []
    if certify is not None:
        certify_entries, certify_problems = certifications_of(certify)
    if demonstrated:
        composed, composed_problems = demonstrated_certifications(demonstrated, home, offset)
        certify_problems += composed_problems
        twice = sorted({e["node"] for e in composed} & {e["node"] for e in certify_entries})
        certify_problems += [f"{node_id} is certified by --certify and claimed by a proof under "
                             f"--demonstrated; one certification per node, and a claim a proof "
                             f"carries needs no second statement" for node_id in twice]
        certify_entries += [e for e in composed if e["node"] not in twice]
    if certify_entries or certify_problems:
        registry = registry_of(home, offset) or {}
        steps = {c["step"] for c in registry.get("commands") or []
                 if isinstance(c, dict) and isinstance(c.get("step"), str)}
        for entry in certify_entries:
            node_id = entry["node"]
            if node_id not in nodes:
                certify_problems.append(f"{spec_root} holds no node {node_id}; a certification "
                                        f"is of a node the specification holds")
                continue
            bound_here = [given for given in files
                          if any(n == node_id for n, _ in index.get(stored_of[given]) or [])]
            if not bound_here:
                certify_problems.append(f"{node_id} is bound to none of the named files; a "
                                        f"certification rides the reading of a file that encodes "
                                        f"the node, so name one the trace binds it to")
            proof, absent = traced_files_of(target, home, entry["proof"])
            certify_problems += [f"{node_id}: proof {problem}" for problem in absent]
            if entry["step"] not in steps:
                certify_problems.append(
                    f"{node_id}: the registry declares no step `{entry['step']}`"
                    + (f"; it declares {', '.join(sorted(steps))}" if steps else
                       "; the project declares no registry for this target, and a step that "
                       "runs the proof has to be one the registry names"))
            entry["proof_resolved"] = [str((target / p).resolve()) for p in entry["proof"]]
        for problem in certify_problems:
            print(f"cannot run: {problem}", file=sys.stderr)
        if certify_problems:
            return CANNOT_RUN
    certify_nodes = {entry["node"] for entry in certify_entries}

    # What a run decides is not handed to a judge. A constraint some registry step decides and a
    # node a certified test decides are both answered by running that step over the tree, and a
    # reading of either re-decides mechanically what a run settles exactly — at a model's recall,
    # and at the price of the whole file's delegation. Two guards hold the tier honest, and both
    # send the pair back to a judge rather than widening it: the certification must still be live,
    # which `test_decided` recomputes from the proof's own digests, and the node's text must not
    # have moved since the bind — a step or a test decided the fact as the node then stated it,
    # and neither was asked about the sentence that replaced it.
    decided = {} if (audit or review) else decided_constraints(home, offset)
    by_test = {} if (audit or review) else test_decided(declared, home, offset)
    def decides(node_id: str) -> tuple[str, list[str]] | None:
        if bound_digest.get(node_id) != nodes[node_id]["digest"]:
            return None
        if node_id in by_test:
            return DECIDED_BY_TEST, [by_test[node_id]]
        if node_id in decided:
            return "step", list(decided[node_id])
        return None

    # One walk over the corpus, read for two questions. The omission guard borrows a judgment
    # only where no record holds an open finding against the pair, and a record it cannot read
    # is one it cannot answer that question over — so an unreadable record is a refusal here,
    # before anything is written, naming the record.
    corpus = judged(home)
    _found, _cleared, unreadable = corpus
    if unreadable:
        for problem in unreadable:
            print(f"cannot run: {RECONCILE_DIR}/{problem}", file=sys.stderr)
        print(f"cannot run: {len(unreadable)} record(s) under {home / RECONCILE_DIR} cannot be "
              f"read, and the omission guard borrows no judgment over a corpus it could not "
              f"finish reading; repair or remove each, then stage again", file=sys.stderr)
        return CANNOT_RUN
    owed_pairs = open_owed(home, corpus)
    # A pair the corpus answers both ways is not owed — a clearance closes a finding, which is the
    # same reading `--owed` reports by — but the omission's reason may not say no record holds a
    # finding against it, because one does. `--owed` states plainly that which judgment is current
    # cannot be settled mechanically, and a reason that claimed otherwise would put that sentence
    # and this one in a committed record together.
    both_ways = {pair for pair in _found if pair in _cleared}
    judged_files: dict[str, list[str]] = {}
    all_current: list[str] = []
    unbound: list[str] = []
    omitted: list[dict] = []
    orphaned: list[dict] = []
    mechanical: list[dict] = []
    answered_by_run: list[str] = []
    for given in files:
        stored = stored_of[given]
        rows = sorted(index.get(stored) or [])
        assigned = []
        held_current = False
        held_mechanical = False
        for node_id, pinned in rows:
            if node_id not in nodes:
                orphaned.append({"node": node_id, "file": given})
                continue
            # An omission borrows an earlier judgment, and a pair has two sides: the file's bytes
            # and the node's. Comparing only the file's let a node whose text moved be omitted as
            # "current" — the pair the drift report was calling `moved` at the same moment — so a
            # reconciliation over it staged no judge, folded a record saying the binding was
            # current, and bound nothing, forever. Both digests, or the pair is owed a reading.
            #
            # An audit is the deliberate re-judgment of exactly the pairs this omission
            # skips: a binding that never drifts is a claim nothing else ever re-examines.
            # A review re-reads what a delivery just stamped, which is the same set; the one
            # pair it may skip is the one a judgment already read, and the branch below is it.
            # A node being certified is read whatever its digest says: the certification rides
            # a fresh reading of the node against the file, and an omission would leave it none.
            if not (audit or review) and pinned == current[stored] \
                    and bound_digest.get(node_id) == nodes[node_id]["digest"] \
                    and (node_id, stored) not in owed_pairs and node_id not in certify_nodes:
                omitted.append({"node": node_id, "file": given,
                                "reason": "the binding computes at the file's content and at the "
                                          "node's text as both stand, and no finding stands open "
                                          "against the pair"
                                          + (" — the corpus answers it both ways, and a clearance "
                                             "closes a finding here as it does in `--owed`"
                                             if (node_id, stored) in both_ways else "")})
                held_current = True
                continue
            # A review omits only what a judgment already read at these bytes. A delivery's bind
            # stamps what it wrote, not what anyone read against the node, so a pair a delivery
            # or a hand stamped goes to the judge; and the delivery's own nodes, named by
            # `--node`, are read on every file whatever the trace says about them. A pair the
            # corpus answers both ways is read too: `judged` records the clearance, and a finding
            # standing beside it is a judgment the clearance does not settle.
            if review and not audit and pinned == current[stored] \
                    and bound_digest.get(node_id) == nodes[node_id]["digest"] \
                    and (node_id, stored) in judged_pairs \
                    and (node_id, stored) not in owed_pairs \
                    and (node_id, stored) not in both_ways \
                    and node_id not in certify_nodes and node_id not in also:
                omitted.append({"node": node_id, "file": given, "reason": CLEARED_BY_JUDGMENT})
                held_current = True
                continue
            # After the omission guard and never before it: a pair nothing has to re-decide needs
            # no run either, and a tier that claimed it would make a caller capture a run to
            # answer a question the last bind already answered over these exact bytes.
            run_decides = decides(node_id)
            if run_decides is not None and node_id not in certify_nodes:
                kind, step_names = run_decides
                mechanical.append({"node": node_id, "file": given, "steps": step_names,
                                   "decided_by": kind})
                held_mechanical = True
                continue
            assigned.append(node_id)
        # Whether a file is judged and whether the trace binds anything to it are two questions.
        # A review hands an untraced file a judge over the plan's nodes, and the record still
        # owes the fact that no binding claims it: a file under `files` that no node accounts
        # for and no `unbound` names is a record the fold refuses to write. A file whose only
        # bindings are orphaned is unbound the same way — nothing standing claims it.
        if not assigned and not held_current and not held_mechanical:
            unbound.append(given)
        if assigned or also:
            judged_files[given] = assigned
        elif held_current:
            all_current.append(given)
        elif held_mechanical:
            # Not unbound and not judged: every pair this file carries is one a run answers, so
            # no judge is spawned for it and the record accounts for it through those nodes.
            answered_by_run.append(given)

    candidates: dict[str, list[str]] = {}
    for given, assigned in judged_files.items():
        for node_id in assigned:
            candidates.setdefault(node_id, []).append(given)

    # Every path a judge needs beside the nodes, resolved here rather than searched for there. A
    # specification root's own layout is not obvious from its root — a projection may or may not
    # exist — and a judge that hunts for one spends a call per delegation to learn what one
    # listing already knows. Only what is on disk is named: a path offered and absent is the same
    # hunt with an extra step. The labels are the shortest thing that identifies each path,
    # because this block is re-read on every turn of every delegation: what each file means is
    # stated where that file is authoritative, and a sentence repeated here would be bought once
    # per turn to say what the file itself says once.
    projections = [(label, spec_root / relative) for label, relative in
                   (("nodes verbatim", "projections/full-text.md"),
                    ("decisions by node", "projections/decisions-by-node.md"),
                    ("decision log", "decision-log.md"))]
    beside = [f"{label}: {path}" for label, path in projections if path.is_file()]
    if not audit:
        beside.append(f"candidate index: {workspace / 'candidates.txt'}")
    beside.append(f"return contract: {RETURN_CONTRACT}")

    packs_dir = workspace / "packs"
    packs_dir.mkdir(parents=True, exist_ok=True)
    manifest_files: dict[str, dict] = {}
    # The node text this staging read, pinned — every node a pack restated, and below every node
    # the mechanical tier holds. A pack header calls this "the digest the bind will stamp", and
    # the bind reads the node fresh, so a node edited between the staging and the fold is one
    # nothing here answered while the trace goes on to assert the new wording.
    staged_nodes: dict[str, str] = {}
    for given, assigned in sorted(judged_files.items()):
        pack = packs_dir / (given.replace("/", "__") + ".md")
        lines = [f"# Node pack for {given} — derived by trace.py --stage from the specification; "
                 f"a reading copy, never a home. Doubt a line, open the source it names.",
                 f"# resolved, nothing here needs searching for — "
                 f"file under judgment: {(target / given).resolve()}",
                 f"# named in a finding's `file` as: {given} — copy this spelling; never "
                 f"compose one"]
        lines += [f"#   {entry}" for entry in beside]
        read_also = [node_id for node_id in also if node_id not in assigned]
        for node_id in assigned + read_also:
            source = spec_root / f"{node_id}.md"
            lines += [f"\n=== {node_id}",
                      f"source: {source}",
                      f"digest: {nodes[node_id]['digest']}",
                      "---",
                      source.read_text(encoding="utf-8").rstrip("\n")]
        pack.write_text("\n".join(lines) + "\n", encoding="utf-8")
        manifest_files[given] = {"nodes": assigned,
                                 "also": read_also,
                                 "pack": str(pack)}
        staged_nodes.update({node_id: nodes[node_id]["digest"]
                             for node_id in assigned + read_also})

    # A pair the mechanical tier holds reaches no pack, and its node is pinned all the same. The
    # staging separated it because a step or a certified test decides the fact as the node then
    # stated it — neither was asked about the sentence that replaces it, so a node edited before
    # the fold is one the run did not answer, exactly as an edited node is one no judge read.
    staged_nodes.update({entry["node"]: nodes[entry["node"]]["digest"] for entry in mechanical})

    # One certification pack per node, beside the file packs: the node's text with its source
    # named, the tests offered as its proof already resolved, and the contract the return is held
    # to. The auditor reads one thing and hunts for nothing.
    for entry in certify_entries:
        node_id = entry["node"]
        source = spec_root / f"{node_id}.md"
        pack = packs_dir / (CERTIFY_PREFIX + node_id.replace("/", "__") + ".md")
        lines = [f"# Certification pack for {node_id} — derived by trace.py --stage from the "
                 f"specification; a reading copy, never a home. Doubt a line, open the source it "
                 f"names.",
                 f"# question: would the proof below fail if this node's fact stopped holding?",
                 f"# proof under judgment: {', '.join(entry['proof_resolved'])}",
                 f"# step that runs it: {entry['step']}",
                 f"# return contract: {CERTIFICATION_CONTRACT}",
                 f"\n=== {node_id}",
                 f"source: {source}",
                 f"digest: {nodes[node_id]['digest']}",
                 "---",
                 source.read_text(encoding="utf-8").rstrip("\n")]
        pack.write_text("\n".join(lines) + "\n", encoding="utf-8")
        entry["pack"] = str(pack)

    # An audit stages no candidate tier, and the omission is the route's own logic rather than a
    # saving taken off it. A candidate exists so a judge can say a fact its own nodes do not hold
    # is held by a node another file carries — an attribution, not an absence. An audit asks one
    # thing of a pair: does this file still carry this node's fact, so that this claim stands?
    # Both answers a candidate separates lead to the same act on that pair — the claim is not
    # carried and the release is what the report hands over — and binding the node that does hold
    # the fact is a delivery's act, which no reconciliation performs. So the tier refines an
    # attribution an audit cannot act on, at the cost of every candidate a judge opens to make it.
    # The reconcile route keeps it: there a misattribution reported as a gap is a false finding,
    # and a false finding blocks a node and costs a fresh delegation to undo.
    if audit:
        candidates = {}
    else:
        lines = [f"# Candidate index — every node this batch's judgments answer for, with the "
                 f"file(s) the trace binds it to. Grep for a fact's own terms; open the node under "
                 f"the specification root before claiming anything about it."]
        for node_id in sorted(candidates):
            lines.append(f"{node_id} — bound in this batch to: "
                         f"{', '.join(sorted(candidates[node_id]))}")
        (workspace / "candidates.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")

    mechanical = sorted(mechanical, key=lambda e: (e["file"], e["node"]))
    manifest = {"slug": slug,
                "audit": audit,
                "review": review,
                "also": also,
                "specification_root": str(spec_root),
                "files": manifest_files,
                "digests": {given: current[stored_of[given]] for given in files},
                "node_digests": staged_nodes,
                "all_current": sorted(all_current),
                "unbound": sorted(unbound),
                "omitted": sorted(omitted, key=lambda e: (e["file"], e["node"])),
                "orphaned": sorted(orphaned, key=lambda e: (e["file"], e["node"])),
                "mechanical": mechanical,
                "answered_by_run": sorted(answered_by_run),
                "certify": [{"node": e["node"], "proof": e["proof"],
                             "proof_resolved": e["proof_resolved"], "step": e["step"],
                             "pack": e["pack"]} for e in certify_entries],
                "candidates": {n: sorted(fs) for n, fs in sorted(candidates.items())}}
    (workspace / MANIFEST_FILE).write_text(json.dumps(manifest, indent=2) + "\n",
                                           encoding="utf-8")
    returns_dir.mkdir(parents=True)

    to_judge = sum(len(a) for a in judged_files.values())
    if audit:
        shape = "staged as an audit — no pair omitted, every standing claim goes to a judge"
    elif review:
        shape = (f"staged by a review — {len(omitted)} pair(s) omitted as cleared by a judgment "
                 f"at these bytes, and {len(also)} plan node(s) read on every file without being "
                 f"bound")
    else:
        shape = (f"{len(omitted)} pair(s) omittable — the binding is current and nothing is "
                 f"owed on them")
    judged_unbound = [given for given in unbound if given in judged_files]
    print(f"staged {slug}: {len(judged_files)} file(s) to judge over {to_judge} node(s); "
          f"{shape}; {len(all_current)} file(s) with nothing left to judge; {len(unbound)} "
          f"file(s) the trace binds nothing to"
          + (f", {len(judged_unbound)} of them judged over the plan's nodes alone"
             if judged_unbound else ""))
    print(f"  manifest and packs at {workspace}; "
          + (f"candidate index at {workspace / 'candidates.txt'}" if not audit else
             "no candidate index — an audit asks whether a claim stands, and both answers a "
             "candidate separates release the same claim"))
    print(f"  save each delegation's return verbatim at "
          f"{returns_dir}/<file path with '/' as '__'>.yaml")
    if orphaned:
        print(f"  {len(orphaned)} binding(s) name a node the specification no longer holds — "
              f"no judge is handed those, no bind repairs them, and --prune is their route:")
        for entry in orphaned:
            print(f"    {entry['node']} — bound to {entry['file']}")
    if mechanical:
        steps = sorted({s for entry in mechanical for s in entry["steps"]})
        print(f"  {len(mechanical)} pair(s) are decided by a run, not by a judge — no judge is "
              f"handed one, and the fold answers each from the run you capture. Run "
              f"{', '.join(f'`{s}`' for s in steps)} into "
              f"{returns_dir}, then pass --run to the fold:")
        for entry in mechanical:
            what = ("a certified test decides it" if entry["decided_by"] == DECIDED_BY_TEST
                    else "a registry step decides the constraint")
            print(f"    {entry['node']} — bound to {entry['file']}: {what} "
                  f"({'steps' if len(entry['steps']) > 1 else 'step'} "
                  f"{', '.join(f'`{s}`' for s in entry['steps'])}"
                  + (", and every one of them has to pass)" if len(entry['steps']) > 1 else ")"))
        print(f"    python3 -B {Path(__file__).resolve().parent / 'run.py'} {returns_dir} "
              f"--run {slug} --cwd {target.resolve()} --timeout-seconds <the registry's bound> "
              + " ".join(f'--step {s}="<the registry\'s command>"' for s in steps))
    if certify_entries:
        print(f"  {len(certify_entries)} certification(s) staged — one coverage-auditor "
              f"delegation each, over the node's pack and its proof; save each return verbatim at "
              f"{returns_dir}/{CERTIFY_PREFIX}<node with '/' as '__'>.yaml:")
        for entry in certify_entries:
            print(f"    {entry['node']} — proof {', '.join(entry['proof'])} (step "
                  f"`{entry['step']}`); pack {entry['pack']}")
    return 0


def return_problems(front, assigned: list[str], given: str) -> list[str]:
    """Every way one delegation's saved return fails its contract or its assignment. The schema
    holds the shape; this holds the relation the schema cannot see — that `read` answers for
    exactly the node set the delegation was handed, since a return short one node reads exactly
    like a complete one and the fold would clear the missing node by silence."""
    if not isinstance(front, dict):
        return ["the return is not a mapping"]
    schema = json.loads(RETURN_CONTRACT.read_text(encoding="utf-8"))
    problems = [f"{'/'.join(str(part) for part in error.path) or 'return'}: {error.message}"
                for error in Draft202012Validator(schema).iter_errors(front)]
    if problems:
        return problems
    answered = [entry["node"] for entry in front["read"]]
    problems += [f"read: {node} appears {answered.count(node)} times; a delegation answers once, "
                 f"and two answers for one node void each other"
                 for node in sorted(set(answered)) if answered.count(node) > 1]
    missing = sorted(set(assigned) - set(answered))
    extra = sorted(set(answered) - set(assigned))
    if missing:
        problems.append(f"read: no entry for {', '.join(missing)}; the return answers for the "
                        f"node set the delegation was handed, whole")
    if extra:
        problems.append(f"read: {', '.join(extra)} is not in this delegation's node set; a "
                        f"candidate is opened to attribute a finding, never answered for in "
                        f"`read`")
    for finding in front.get("findings") or []:
        named = finding.get("file")
        if named is not None and named != given:
            problems.append(f"findings: a finding names {named}, and this delegation read "
                            f"{given}, which is the spelling its pack header hands it; one "
                            f"file per delegation is the shape of this pass")
    return problems


def certification_problems(front, node_id: str, proof: list[str]) -> list[str]:
    """Every way one certification's saved return fails its contract or its ask. The schema holds
    the shape; this holds what the schema cannot see — that the return answers for exactly the node
    it was handed, and cites no test outside the proof the human offered, because the binding pins
    exactly that proof and a test cited from elsewhere would be certified by nobody."""
    if not isinstance(front, dict):
        return ["the return is not a mapping"]
    if not CERTIFICATION_CONTRACT.is_file():
        return [f"{CERTIFICATION_CONTRACT} is missing; nothing can be validated without it"]
    schema = json.loads(CERTIFICATION_CONTRACT.read_text(encoding="utf-8"))
    problems = [f"{'/'.join(str(part) for part in error.path) or 'return'}: {error.message}"
                for error in Draft202012Validator(schema).iter_errors(front)]
    if problems:
        return problems
    answered = [entry["node"] for entry in front["certified"]]
    if answered != [node_id]:
        problems.append(f"certified: the return answers for {', '.join(answered)}; this "
                        f"delegation was handed {node_id} alone")
    for entry in front["certified"]:
        for test in entry.get("tests") or []:
            if test["file"] not in proof:
                problems.append(f"certified: {test['file']} is not among the proof offered "
                                f"({', '.join(proof)}); a certification is of the tests the human "
                                f"named, and the binding pins exactly those")
    return problems


def run_problems(captured: dict, target: Path, steps: set[str],
                 registry: dict | None = None) -> list[str]:
    """Every way one captured run fails to answer for this reconciliation's mechanical tier.

    A run is evidence exactly where it ran: the same command in two trees is two runs, so a run
    whose `cwd` is not this target answers about a tree nobody staged. And the tier is answered
    per step rather than by the run's own outcome — a run that stopped at a failed step never
    attempted the later ones, and a step never attempted decided nothing either way.

    The command is held to the registry's own, because a step name is only worth what the command
    behind it does. `--step lint="echo nothing"` records a step called `lint` that passed, and
    without this the fold would read it as the registry's lint deciding a constraint. Compared as
    argument vectors, the way `bin/run.py` split it, so quoting that changes nothing is nothing."""
    problems = []
    where = captured.get("cwd")
    if not isinstance(where, str) or Path(where).resolve() != target.resolve():
        problems.append(f"the run records cwd {where!r} and this reconciliation is over "
                        f"{target.resolve()}; the same command in two trees is two runs")
    steps_held = captured.get("steps")
    if steps_held is not None and not isinstance(steps_held, list):
        return problems + [f"the run's `steps` is a {type(steps_held).__name__}, not a list; "
                           f"bin/run.py writes one entry per step attempted"]
    attempted = {step["name"] for step in steps_held or []
                 if isinstance(step, dict) and isinstance(step.get("name"), str)}
    missing = sorted(steps - attempted)
    if missing:
        problems.append(f"the run holds no step named {', '.join(missing)}; the mechanical tier "
                        f"is answered by those steps and a run without one answers nothing for it")
    wanted = {c["step"]: c.get("command") for c in (registry or {}).get("commands") or []
              if isinstance(c, dict) and isinstance(c.get("step"), str)}
    for step in captured.get("steps") or []:
        if not isinstance(step, dict) or step.get("name") not in steps:
            continue
        declared_command = wanted.get(step["name"])
        if not isinstance(declared_command, str) or not isinstance(step.get("command"), str):
            continue
        if shlex.split(step["command"]) != shlex.split(declared_command):
            problems.append(
                f"the run's `{step['name']}` step ran {step['command']!r} and the registry "
                f"declares {declared_command!r} for that step; a step name is worth what the "
                f"command behind it does, and this run did something else")
    return problems


def step_outcomes(captured: dict) -> dict[str, dict]:
    """Each step of a captured run by name, so a pair reads the outcome of the step that decides
    it rather than the run's own — the two differ the moment a run stops at a failure."""
    held = captured.get("steps")
    return {step["name"]: step for step in (held if isinstance(held, list) else [])
            if isinstance(step, dict) and isinstance(step.get("name"), str)}


def fold_returns(target: Path, workspace: Path, premise_path: Path, record_out: Path,
                 run_dir: Path | None = None) -> int:
    """Write the reconciliation record from the delegations' saved returns, mechanically.

    Every rule here is a fold over structured answers, applied the same way every time: a node
    conforms exactly where every delegation that read one of its files cleared it; a finding
    naming a node lands on that node wherever its own judge stood; a finding naming none holds
    every node of the file that produced it, marked `collateral` on the nodes nothing contested
    directly; a node whose fact no named file holds any more binds nothing, because a binding
    asserts the file answers for the node and the judge just read that it does not. None of that
    asks for judgment, which is why none of it is applied by a context that could misremember a
    rule between node forty and node eighty.

    What the caller owes is the premise — title, summary, target, one `change` line per named
    file — because that half is the human's assertion and no fold can write it. What the fold
    owes back is refusal by name: a return that does not hold, or one missing for a staged file,
    is a delegation to run again with its prompt fixed, never an answer to repair here."""
    if not target.is_dir():
        print(f"cannot run: {target} is not a directory", file=sys.stderr)
        return CANNOT_RUN
    manifest_path = workspace / MANIFEST_FILE
    if not manifest_path.is_file():
        print(f"cannot run: {manifest_path} does not exist; --stage is what writes it",
              file=sys.stderr)
        return CANNOT_RUN
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not premise_path.is_file():
        print(f"cannot run: {premise_path} does not exist", file=sys.stderr)
        return CANNOT_RUN
    try:
        premise = yaml.safe_load(premise_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as broken:
        print(f"cannot run: {premise_path} does not parse: {broken}", file=sys.stderr)
        return CANNOT_RUN
    if not isinstance(premise, dict):
        print(f"cannot run: {premise_path} is not a mapping", file=sys.stderr)
        return CANNOT_RUN

    home = home_of(target)
    offset = offset_of(target, home)
    problems = [f"premise: `{field}` is missing" for field in
                ("title", "summary", "target", "files") if field not in premise]
    if "target" in premise and isinstance(premise["target"], str) \
            and (home / project.PROJECT_FILE).is_file() \
            and premise["target"] not in target_roots(home):
        problems.append(f"premise: `target` names {premise['target']!r}, which "
                        f"{project.PROJECT_FILE} does not declare as a key under `targets`; "
                        f"a record naming it would bind here and read as unreadable everywhere "
                        f"else that reads `siegard-reconcile/` back")
    named = {}
    if isinstance(premise.get("files"), list):
        for entry in premise["files"]:
            if isinstance(entry, dict) and isinstance(entry.get("path"), str) \
                    and isinstance(entry.get("change"), str):
                named[entry["path"]] = entry["change"]
            else:
                problems.append("premise: every `files` entry carries `path` and `change`")
    every_named = (set(manifest["files"]) | set(manifest["all_current"])
                   | set(manifest["unbound"]) | set(manifest.get("answered_by_run") or []))
    if not problems:
        absent = sorted(every_named - set(named))
        stray = sorted(set(named) - every_named)
        if absent:
            problems.append(f"premise: no `change` line for {', '.join(absent)}; the premise "
                            f"accounts for every staged file")
        if stray:
            problems.append(f"premise: {', '.join(stray)} was never staged; the file set is the "
                            f"staged one, and widening it here reconciles ground nobody scoped")
    if problems:
        for problem in problems:
            print(f"cannot fold: {problem}")
        return 1

    # Every node the staging pinned, held to the text it pinned — the ones a pack restated and
    # the ones the mechanical tier holds alike. The bind reads each node fresh, so a node edited
    # between the staging and the fold is one no judge read and no run answered, while the trace
    # goes on to assert the new wording — and no later `--check` can tell, because the bind
    # stamped the new digest itself. This is the specification-side twin of the guard the run
    # already has over the files, and it covers the pairs the run answers as well as the rest:
    # a tier separated on the node's text as it stood is not answered by a step that ran before
    # the sentence changed.
    spec_root_at = Path(manifest.get("specification_root") or "")
    shifted = []
    for node_id, digest in sorted((manifest.get("node_digests") or {}).items()):
        source = spec_root_at / f"{node_id}.md"
        if not source.is_file() or spec.digest_of(source) != digest:
            shifted.append(node_id)
    if shifted:
        print(f"cannot fold: {', '.join(shifted)} moved in the specification since the staging "
              f"read it, so this fold would stamp a wording neither the judgments nor the run "
              f"answered; the route is a fresh invocation under a new slug, which reads each "
              f"node as it now stands")
        return 1
    # The files' side of the same guard, on every tier. Each judge read a file as the staging
    # pinned it, and the bind stamps what is on disk; a file edited between the two is one no
    # judge read and no run proved, while the trace would go on to assert the new bytes with
    # no `--check` able to tell — the bind stamps the new digest itself.
    moved = sorted(given for given, digest in (manifest.get("digests") or {}).items()
                   if not (target / given).is_file()
                   or spec.digest_of(target / given) != digest)
    if moved:
        print(f"cannot fold: {', '.join(moved)} changed since the staging, so every judgment "
              f"and every run this fold would read answered over content it would not bind; "
              f"the route is a fresh invocation under a new slug, never a bind around the "
              f"answers")
        return 1

    returns_dir = home / RECONCILE_DIR / f"{manifest['slug']}.returns"
    if not returns_dir.is_dir():
        print(f"cannot fold: {returns_dir} does not exist; --stage is what creates it, and the "
              f"returns are saved into it verbatim as each delegation answers", file=sys.stderr)
        return CANNOT_RUN

    expected = {return_name(given): given for given in manifest["files"]}
    certify_expected = {CERTIFY_PREFIX + e["node"].replace("/", "__") + ".yaml": e
                        for e in manifest.get("certify") or []}
    # `run.py`'s own directory lives here too, because the runs a reconciliation captures are
    # evidence of the same kind as the returns and outlive the workspace the same way.
    stray = sorted(p.name for p in returns_dir.iterdir()
                   if p.name not in expected and p.name not in certify_expected
                   and not (p.name == RUN_DIR and p.is_dir()))
    if stray:
        print(f"cannot fold: {returns_dir} holds {', '.join(stray)}, which no staged file "
              f"explains; a return nobody staged is an answer to a question nobody asked")
        return 1

    returns: dict[str, dict] = {}
    rerun: list[str] = []
    for name, given in sorted(expected.items()):
        path = returns_dir / name
        if not path.is_file():
            rerun.append(f"{given}: no return at {path}")
            continue
        try:
            front = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as broken:
            rerun.append(f"{given}: the return does not parse: {broken}")
            continue
        staged_for = manifest["files"][given]
        held = return_problems(front, staged_for["nodes"] + staged_for.get("also", []), given)
        if held:
            rerun += [f"{given}: {problem}" for problem in held]
            continue
        returns[given] = front
    # A certification's return is read by the same rule as a file's: saved verbatim, held to its
    # own contract, and refused by name where it does not hold — the delegation runs again.
    certified_returns: dict[str, dict] = {}
    for name, ask in sorted(certify_expected.items()):
        path = returns_dir / name
        if not path.is_file():
            rerun.append(f"certification of {ask['node']}: no return at {path}")
            continue
        try:
            front = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as broken:
            rerun.append(f"certification of {ask['node']}: the return does not parse: {broken}")
            continue
        held = certification_problems(front, ask["node"], ask["proof"])
        if held:
            rerun += [f"certification of {ask['node']}: {problem}" for problem in held]
            continue
        certified_returns[ask["node"]] = front["certified"][0]
    if rerun:
        for problem in rerun:
            print(f"cannot fold: {problem}")
        print(f"\n{len(rerun)} problem(s); each names a delegation to run again with its prompt "
              f"fixed — an unusable return is never repaired here, and a follow-up question to "
              f"the delegation that already answered is not a fresh judgment.")
        return 1

    # The mechanical tier is answered by a run, and the run is refused before anything is written
    # where it cannot answer: absent while the tier is not, over another tree, missing a step the
    # tier names, or captured over content that has moved since. The last is the one that matters
    # most, and the file-digest guard above is what holds it — a run proved the tree as it stood,
    # and binding what stands now on the strength of it would stamp a claim over bytes the run
    # never saw.
    tier = manifest.get("mechanical") or []
    steps_named = {s for entry in tier for s in entry.get("steps") or []}
    captured: dict | None = None
    if tier:
        if run_dir is None:
            print(f"cannot fold: {len(tier)} pair(s) are decided by a run and none was given; "
                  f"capture {', '.join(sorted(steps_named))} with bin/run.py into "
                  f"{returns_dir} and pass --run <its directory>")
            return 1
        # The run must live under this reconciliation's own returns directory, and that is the
        # half of the content guard the digests cannot supply. `--stage` refuses a slug whose
        # returns directory exists and creates it empty, so anything under it postdates the
        # staging — which closes the interval the digest check leaves open. Without it the digests
        # bound only [stage, fold], and a run captured before the very edit under reconciliation
        # would clear the node while its `how` said the step passed over the tree as it stands.
        try:
            inside = run_dir.resolve().is_relative_to(returns_dir.resolve())
        except OSError:
            inside = False
        if not inside:
            print(f"cannot fold: {run_dir} does not sit under {returns_dir}; a run this fold reads "
                  f"is one this reconciliation captured, and the staging created that directory "
                  f"empty — a run from anywhere else may predate the very edit being reconciled",
                  file=sys.stderr)
            return CANNOT_RUN
        record_json = run_dir / "run.json"
        if not record_json.is_file():
            print(f"cannot fold: {record_json} does not exist; --run names a directory bin/run.py "
                  f"wrote", file=sys.stderr)
            return CANNOT_RUN
        try:
            captured = json.loads(record_json.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as broken:
            print(f"cannot fold: {record_json} does not parse: {broken}", file=sys.stderr)
            return CANNOT_RUN
        if not isinstance(captured, dict):
            print(f"cannot fold: {record_json} holds a {type(captured).__name__}, not a run "
                  f"record; bin/run.py writes a mapping", file=sys.stderr)
            return CANNOT_RUN
        held = run_problems(captured, target, steps_named, registry_of(home, offset))
        if held:
            for problem in held:
                print(f"cannot fold: {problem}")
            return 1
    elif run_dir is not None:
        print(f"cannot fold: --run was given and no pair of this staging is decided by a run; a "
              f"run nothing reads is evidence for a question nobody asked", file=sys.stderr)
        return CANNOT_RUN

    batch_nodes = {node for entry in manifest["files"].values() for node in entry["nodes"]}
    against: dict[str, list[tuple[str, dict]]] = {}
    out_of_scope: list[tuple[str, dict]] = []
    named_mechanical: list[tuple[str, dict]] = []
    tainted: dict[str, list[dict]] = {}
    unstated: list[dict] = []
    landing_nowhere: list[str] = []
    for given, front in returns.items():
        for finding in front.get("findings") or []:
            # `unstated` answers the other question the pair's own conformance never asked: the
            # source states a fact no node holds. Its subject is the specification, its route is
            # the analysis that gives the fact a node, and no rebind reaches it — so it neither
            # lands on a node nor taints one, however its judge filled `node`. Routed on the word
            # rather than on whether a node was named, because a judge naming the node it read
            # the fact beside is naming where it stood, not what the fact belongs to.
            if finding.get("kind") == UNSTATED_FACT:
                unstated.append({"file": given, "where": finding["where"],
                                 "evidence": finding["evidence"], "cost": finding["cost"]})
                continue
            node = finding.get("node")
            if node is None:
                # An unattributed finding holds every node of its file, and a file the trace
                # binds nothing to has none: it would land nowhere, and the record would carry
                # no sign of it. A contradiction names the node it contradicts; over such a
                # file, a fact no node holds is `unstated`, and that is the word owed.
                if not manifest["files"][given]["nodes"]:
                    landing_nowhere.append(
                        f"{given}: a `contradicts` finding naming no node "
                        f"({finding['where']}: {finding['evidence']} — {finding['cost']}) over "
                        f"a file the trace binds nothing to would land on no node and leave the "
                        f"record; a contradiction names the node it contradicts, and over a file "
                        f"the trace binds nothing to a fact no node holds is `unstated`")
                    continue
                tainted.setdefault(given, []).append(finding)
            elif node in batch_nodes:
                against.setdefault(node, []).append((given, finding))
            elif node in {pair["node"] for pair in tier}:
                # A judge may name a node a run decided — it read the file, not that node's text,
                # since a mechanical node reaches no pack. The run is what answers the pair, so
                # the finding does not land on it; what it must not do is vanish behind a sentence
                # saying no file here is bound to the node, which is the opposite of true.
                named_mechanical.append((given, finding))
            else:
                out_of_scope.append((given, finding))

    if landing_nowhere:
        for problem in landing_nowhere:
            print(f"cannot fold: {problem}")
        print(f"\n{len(landing_nowhere)} problem(s); each names a delegation to run again with "
              f"its prompt fixed — a finding that would vanish from the record is never folded "
              f"around, and the judge that filed it is the one that says which word it meant.")
        return 1

    read_of = {(given, entry["node"]): entry
               for given, front in returns.items() for entry in front["read"]}

    entries = []
    for node in sorted(batch_nodes):
        bound_in = sorted(given for given, meta in manifest["files"].items()
                          if node in meta["nodes"])
        holders = [given for given in bound_in
                   if read_of[(given, node)]["held_at"].strip().lower() != NOWHERE]
        found = against.get(node) or []
        taint = [given for given in bound_in if given in tainted]
        if not found and not taint and holders == bound_in:
            how = "\n".join(f"{given}: held at {read_of[(given, node)]['held_at']} — "
                            f"{read_of[(given, node)]['evidence']}" for given in holders)
            entries.append({"node": node, "conforms": True, "how": how,
                            "encoded_at": holders})
            continue
        parts = []
        collateral = False
        if found:
            parts += [f"{given}, {finding['where']}: {finding['evidence']} — {finding['cost']}"
                      for given, finding in found]
        left = [given for given in bound_in if given not in holders]
        if left and not found:
            said = "; ".join(f"{given} read `{read_of[(given, node)]['held_at']}` — "
                             f"{read_of[(given, node)]['evidence']}" for given in left)
            if holders:
                parts.append(f"the fact left part of its ground: still held in "
                             f"{', '.join(holders)}, and {said} — a binding asserts the file "
                             f"answers for the node, so the pair that stopped holding it is "
                             f"released by `--bind ... --replace`, never restamped here")
            else:
                parts.append(f"no named file holds this fact now: {said}")
        if taint:
            parts += [f"{given} returned a finding naming no node ({finding['where']}: "
                      f"{finding['evidence']} — {finding['cost']}), and an unattributed finding "
                      f"holds every node of that file its judge was handed"
                      for given in taint for finding in tainted[given]]
            collateral = not found and holders == bound_in
        entry = {"node": node, "conforms": False, "how": "\n".join(parts),
                 "observed_at": bound_in}
        if collateral:
            entry["collateral"] = True
        entries.append(entry)

    # The mechanical tier's own entries, written from the run and from nothing else. A node here
    # was handed no judge, so there is no reading to fold: what the step's outcome says is the
    # whole answer, and it is said per step because a run that stopped at a failure never
    # attempted what came after it.
    outcomes = step_outcomes(captured) if captured is not None else {}
    run_named = captured.get("run") if captured is not None else None
    by_run: dict[str, list[dict]] = {}
    for pair in tier:
        by_run.setdefault(pair["node"], []).append(pair)
    for node, pairs in sorted(by_run.items()):
        # Every step the registry named for this node, and every one of them has to have passed:
        # a registry naming two is saying each decides a part, so one green beside one red leaves
        # the constraint half answered, which is not answered.
        step_names = list(dict.fromkeys(s for pair in pairs for s in pair.get("steps") or []))
        what = ("a certified test decides this node" if pairs[0]["decided_by"] == DECIDED_BY_TEST
                else "a registry step decides this constraint")
        where = sorted(pair["file"] for pair in pairs)
        ran = [(name, outcomes.get(name, {})) for name in step_names]
        short = [(name, o) for name, o in ran if o.get("outcome") != "passed"]
        said = ", ".join(f"`{name}` {o.get('outcome')}"
                         + (f" (exit {o.get('exit_code')})" if o.get("exit_code") is not None
                            else "")
                         + f" over {o.get('command')}" for name, o in ran)
        if not short:
            entries.append({
                "node": node, "conforms": True,
                "how": f"{what}, and every step the registry named for it passed over the tree as "
                       f"these files stand — {run_named}: {said}. No judge read this pair, and "
                       f"the run is the whole of what answered it",
                "encoded_at": where})
        else:
            entries.append({
                "node": node, "conforms": False,
                "how": f"{what}, and {'a step' if len(short) == 1 else 'steps'} the registry "
                       f"named for it did not pass — {run_named}: {said}. The run is the answer, "
                       f"and what each step printed is in the run's own log"
                       + ("; the constraint is answered only where every step the registry named "
                          "for it passes" if len(step_names) > 1 else ""),
                "observed_at": where})

    # A certification lands on a node only where the auditor answered `covered` and the node's own
    # reading cleared it. Anything else is said in the notes and writes nothing: a certification
    # is a claim about what decides a binding, and a binding the judgment refused has none.
    certification_notes: list[str] = []
    by_node = {entry["node"]: entry for entry in entries}
    for ask in manifest.get("certify") or []:
        node_id = ask["node"]
        answer = certified_returns[node_id]
        entry = by_node.get(node_id)
        if entry is None:
            certification_notes.append(
                f"Certification of {node_id} was asked and the node was judged over no named "
                f"file; nothing here carries it.")
            continue
        if answer["state"] != "covered":
            # Said structurally as well as in prose: `--bind-record` releases a standing
            # certification on this node, which the note below would otherwise only claim. The
            # remainder rides the same entry: whether a test could close what is left is a fact
            # about the node, and `--owed` lists the testable ones as the work a test closes.
            remainder = answer.get("remainder")
            if entry["conforms"]:
                entry["decided_by"] = "reading"
                if remainder is not None:
                    entry["remainder"] = remainder
                    entry["remainder_why"] = answer["remainder_why"]
            said_remainder = "" if remainder is None else (
                f" The remainder is {remainder}: {answer['remainder_why']}.")
            certification_notes.append(
                f"Certification of {node_id} did not hold: the auditor answered `{answer['state']}` "
                f"— {answer.get('why', '')}. The node is decided by reading, and a certification "
                f"standing on it from an earlier reconciliation is released by the bind."
                + said_remainder)
            continue
        if not entry["conforms"]:
            certification_notes.append(
                f"Certification of {node_id} held ({', '.join(t['file'] for t in answer['tests'])} "
                f"would fail if the fact stopped holding) and is not written: the judgment did not "
                f"clear the node, and a test-decided binding rests on a reading that did.")
            continue
        entry["decided_by"] = DECIDED_BY_TEST
        entry["step"] = ask["step"]
        # What is pinned is what the auditor cited, never the whole set the human offered. A file
        # offered and not cited bears on nothing the certification rests on, and pinning it would
        # make an edit to it lapse a certification no reading of it supported.
        entry["proof"] = sorted({test["file"] for test in answer["tests"]})
        certification_notes.append(
            f"Certified {node_id} as decided by step `{ask['step']}`: "
            + "; ".join(f"{t['file']}" + (f" ({t['name']})" if t.get("name") else "")
                        for t in answer["tests"])
            + " would fail if the fact stopped holding.")

    notes = [f"Judged by {len(returns)} delegation(s), one per file; folded mechanically by "
             f"trace.py --fold from the returns under {RECONCILE_DIR}/{manifest['slug']}.returns/."]
    if tier:
        notes.append(
            f"{len(tier)} pair(s) over {len(by_run)} node(s) were decided by {run_named} rather "
            f"than by a judge — a registry step decides the constraint, or a certified test "
            f"decides the node — with step(s) {', '.join(sorted(steps_named))}. No delegation read "
            f"them; the run's own log is the evidence, and it sits beside these returns.")
    notes += certification_notes
    if manifest.get("audit"):
        notes.append("Staged as an audit: the source did not drift — every pair the trace held "
                     "for these files was re-judged deliberately, standing claims included.")
    if manifest.get("review"):
        read_also = manifest.get("also") or []
        notes.append("Staged by a review over files a delivery wrote: every pair a delivery "
                     "or a hand stamped was judged, and a pair was omitted only where a "
                     "reconciliation's judgment had cleared it at these very bytes"
                     + (f"; the plan's node(s) {', '.join(read_also)} were read on every file "
                        f"and answered for, and bound from nowhere here — a binding this record "
                        f"writes is one the trace already held."
                        if read_also else "."))
    if isinstance(premise.get("notes"), str) and premise["notes"].strip():
        notes.insert(0, premise["notes"].strip())
    for given, finding in out_of_scope:
        notes.append(f"A finding in {given} names {finding['node']}, which no file of this set "
                     f"is bound to: {finding['where']}: {finding['evidence']} — "
                     f"{finding['cost']}. It blocks nothing here; it is owed a route of its own.")
    for given, finding in named_mechanical:
        notes.append(f"A finding in {given} names {finding['node']}, which this set is bound to "
                     f"and a run decided rather than a judge: {finding['where']}: "
                     f"{finding['evidence']} — {finding['cost']}. The judge that filed it was "
                     f"handed the file and not that node's text, and the step's own outcome is "
                     f"what answered the pair — so it does not land on the node. It is owed a "
                     f"reading of its own, and a reconciliation that names this file without the "
                     f"node in its mechanical tier is what gives it one.")
    for entry in manifest["orphaned"]:
        notes.append(f"{entry['node']} is bound to {entry['file']} and the specification no "
                     f"longer holds it; no judge was handed it, and --prune is its route.")
    opened_count = sum(len(front.get("candidates_opened") or []) for front in returns.values())
    with_any = sum(1 for front in returns.values() if front.get("candidates_opened"))
    notes.append(f"Candidates: {opened_count} opened across {with_any} of {len(returns)} "
                 f"delegation(s); each return lists its own under `candidates_opened`.")
    if unstated:
        notes.append(f"Unstated: {len(unstated)} fact(s) the source states that no node holds, "
                     f"over {len({e['file'] for e in unstated})} file(s), listed under "
                     f"`unstated`. They block no binding here and no rebind closes them — the "
                     f"route is the analysis that gives each fact a node.")

    front = {"contract_version": RECORD_VERSION,
             "title": premise["title"],
             "summary": premise["summary"],
             "target": premise["target"],
             "files": [{"path": path, "change": named[path]} for path in sorted(every_named)],
             "nodes": entries}
    if unstated:
        front["unstated"] = sorted(unstated, key=lambda e: (e["file"], e["where"]))
    if manifest["unbound"]:
        front["unbound"] = manifest["unbound"]
    if manifest["omitted"]:
        front["pairs_omitted"] = manifest["omitted"]
    front["notes"] = "\n".join(notes)

    schema = json.loads(RECONCILE_CONTRACT.read_text(encoding="utf-8"))
    held = [f"{'/'.join(str(part) for part in error.path) or 'record'}: {error.message}"
            for error in Draft202012Validator(schema).iter_errors(front)]
    if not held:
        held = accounted(front)
    if held:
        for problem in sorted(set(held)):
            print(f"cannot fold: {problem}")
        print(f"\n{len(set(held))} problem(s) in what the fold composed; this is a defect in the "
              f"staging or the premise, and nothing was written.")
        return 1

    if record_out.parent.name != RECONCILE_DIR:
        print(f"cannot run: {record_out} does not sit under {RECONCILE_DIR}/; the record lives "
              f"where the trace it justifies lives", file=sys.stderr)
        return CANNOT_RUN
    if record_out.exists():
        print(f"cannot run: {record_out} already exists; a slug is one reconciliation's name",
              file=sys.stderr)
        return CANNOT_RUN
    text = yaml.safe_dump(front, sort_keys=False, allow_unicode=True, width=100)
    record_out.write_text(
        f"---\n{text}---\n\n## Folded\nThis record was folded by `trace.py --fold` from the "
        f"delegation returns under `{RECONCILE_DIR}/{manifest['slug']}.returns/`, which are the "
        f"evidence behind every entry above.\n", encoding="utf-8")

    cleared = sum(1 for entry in entries if entry["conforms"])
    blocked = [entry for entry in entries if not entry["conforms"]]
    marks = sum(1 for entry in blocked if entry.get("collateral"))
    print(f"folded {record_out.name}: {cleared} node(s) cleared, {len(blocked)} not — "
          f"{marks} of those collateral, blocked only by an unattributed sibling finding — "
          f"{len(manifest['omitted'])} pair(s) omitted as current and unowed")
    print(f"  next: trace.py --reconciliation {record_out}")
    return 0


def unaccounted(record: Path, declared: dict, nodes: dict[str, dict],
                offset: Path) -> list[str]:
    """Every node the trace binds to a file this reconciliation names and the record says nothing
    about. Empty for a record that accounts for all of them, and for any record this does not apply
    to.

    `reconciliation.json` defines the node set as "every specification node the trace binds to a
    named file", and the skill that writes one says it in as many words — "what you keep is every
    node those findings name, and never a subset … reconciling a file against the part of the
    specification that happens to agree with it is the failure this whole route exists to prevent".
    Without this check, nothing holds a record to it: a record naming a file and answering for one
    of the two nodes bound to it would rebind that one and leave the other asserting a link nobody
    re-read, while reading exactly like a complete reconciliation.

    An orphaned binding is excluded. Its node is gone from the specification, no bind can repair it
    and `--prune` is the only thing that clears it, so demanding an answer for it would refuse a
    record over ground the route explicitly hands elsewhere.

    This is the one place this script reads a record as a reconciliation rather than as two field
    names. It is not a second opinion about somebody else's contract: `schemas/reconciliation.json`
    is trace.py's own, and `--reconciliation` is where it is enforced."""
    front = as_reconciliation(record)
    if front is None:
        return []

    named = {entry["path"] for entry in front.get("files") or []
             if isinstance(entry, dict) and isinstance(entry.get("path"), str)}
    if not named:
        return []
    # The record spells its paths from the target source root; the trace spells them from its own
    # directory. Compare in the trace's spelling, the way a bind writes them.
    anchored = named if str(offset) == "." else {(offset / p).as_posix() for p in named}

    # A pair the record declares omitted is not unanswered — it points at the judgment an earlier
    # bind already stamped over these exact bytes. The declaration is form; whether each pair
    # really is current and unowed is `omitted_problems`, checked live at bind time.
    omitted = {(entry["node"], entry["file"]) for entry in front.get("pairs_omitted") or []
               if isinstance(entry, dict)
               and isinstance(entry.get("node"), str) and isinstance(entry.get("file"), str)}
    # Pair by pair, not node by node: a record answering one node over one of its two named
    # files, silent on the other, reads exactly like a complete one at node granularity — and
    # `--bind-record` writes by union, so the silent pair's stale claim would simply stand.
    answered_pairs = {(entry["node"], path) for entry in front.get("nodes") or []
                      if isinstance(entry, dict) and isinstance(entry.get("node"), str)
                      for path in (entry.get("encoded_at") or entry.get("observed_at") or [])
                      if isinstance(path, str)}
    given_of = {(p if str(offset) == "." else (offset / p).as_posix()): p for p in named}
    problems = []
    for entry in declared.get("bindings") or []:
        node_id = entry.get("node")
        if not isinstance(node_id, str) or node_id not in nodes:
            continue
        for held in entry.get("files") or []:
            if not isinstance(held, dict) or held.get("path") not in anchored:
                continue
            given = given_of[held["path"]]
            if (node_id, given) in answered_pairs or (node_id, given) in omitted:
                continue
            problems.append(
                f"{node_id} is bound to {held['path']}, which this record names, and the "
                f"record answers for the pair nowhere; a reconciliation reads every node a named "
                f"file answers to, never the subset that happened to agree — a pair whose "
                f"binding is current and unowed may be omitted, said under `pairs_omitted`")
    return sorted(problems)


def omitted_problems(record: Path, declared: dict, home: Path,
                     offset: Path, nodes: dict[str, dict] | None = None) -> list[str]:
    """Every `pairs_omitted` entry whose claim does not hold at this moment. The record's list is
    a declaration; this is the authority, recomputed at bind time, because an omission is a
    judgment borrowed from an earlier bind and the borrowing only stands while both halves do:
    the binding still computes at the file's content — the pair was judged over these exact
    bytes — and no reconciliation record holds an open finding against it. A pair that fails
    either half was owed a judge, and binding around it would stamp a claim nobody re-read."""
    front = as_reconciliation(record)
    if front is None:
        return []
    listed = front.get("pairs_omitted") or []
    if not listed:
        return []

    bound: dict[tuple[str, str], str] = {}
    judged_pairs: set[tuple[str, str]] = set()
    node_pin: dict[str, str] = {}
    for entry in declared.get("bindings") or []:
        node_pin[entry.get("node")] = entry.get("digest")
        for held in entry.get("files") or []:
            if isinstance(held, dict) and isinstance(held.get("path"), str):
                bound[(entry.get("node"), held["path"])] = held.get("digest")
                if held.get(JUDGED) is True:
                    judged_pairs.add((entry.get("node"), held["path"]))

    owed_pairs = open_owed(home)
    problems = []
    for entry in listed:
        if not isinstance(entry, dict):
            continue
        node_id, given = entry.get("node"), entry.get("file")
        if not isinstance(node_id, str) or not isinstance(given, str):
            continue
        stored = given if str(offset) == "." else (offset / given).as_posix()
        pinned = bound.get((node_id, stored))
        if pinned is None:
            problems.append(f"pairs_omitted: nothing binds {node_id} to {stored}; a pair can "
                            f"only be omitted where a binding holds the judgment being pointed at")
            continue
        source = home / stored
        if not source.is_file() or spec.digest_of(source) != pinned:
            problems.append(f"pairs_omitted: {node_id} over {stored} is stale — the file moved "
                            f"since the binding was stamped, so the judgment the omission points "
                            f"at was over different bytes; the pair was owed a judge")
            continue
        if nodes is not None and node_pin.get(node_id) != (nodes.get(node_id) or {}).get("digest"):
            problems.append(f"pairs_omitted: {node_id} over {stored} is stale on the node's own "
                            f"side — its text moved since the binding was stamped, so the "
                            f"judgment the omission points at was over a different sentence; the "
                            f"pair was owed a judge")
            continue
        if (node_id, stored) in owed_pairs:
            problems.append(f"pairs_omitted: {node_id} over {stored} carries an open finding in "
                            f"the reconciliation corpus; a bind already covered its only symptom "
                            f"once, and omitting it here would do it again")
            continue
        if entry.get("reason") == CLEARED_BY_JUDGMENT and (node_id, stored) not in judged_pairs:
            problems.append(f"pairs_omitted: {node_id} over {stored} was omitted as cleared by a "
                            f"judgment, and the binding no longer says a judgment cleared it — a "
                            f"bind since stamped it from a delivery or by hand; the pair was owed "
                            f"a judge")
    return sorted(problems)


def staged_problems(workspace: Path, target: Path,
                    nodes: dict[str, dict]) -> tuple[list[str], str | None]:
    """Every staged file and every pinned node the workspace's manifest holds at a digest other
    than what stands now — or the reason the manifest could not be read.

    A bind stamps what a judge read, and the manifest is where the staging recorded what that
    was: the digest of each file it handed a judge and of each node it pinned. The fold held
    both at its own moment; between the fold and the bind the interval is open, and this is
    what closes it. A file or a node that moved in it is one the judgment never saw, and a bind
    over it would stamp a claim nobody read."""
    manifest_path = workspace / MANIFEST_FILE
    if not manifest_path.is_file():
        return [], f"{manifest_path} does not exist; --stage is what writes it"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as broken:
        return [], f"{manifest_path} does not parse: {broken}"
    if not isinstance(manifest, dict):
        return [], f"{manifest_path} holds a {type(manifest).__name__}, not a manifest"
    problems = []
    for given, digest in sorted((manifest.get("digests") or {}).items()):
        if not (target / given).is_file() or spec.digest_of(target / given) != digest:
            problems.append(f"{given} changed since the staging read it, so the judgment this "
                            f"record carries was over different bytes; the route is a fresh "
                            f"invocation under a new slug, never a bind around the judgment")
    for node_id, digest in sorted((manifest.get("node_digests") or {}).items()):
        if (nodes.get(node_id) or {}).get("digest") != digest:
            problems.append(f"{node_id} moved in the specification since the staging read it, "
                            f"so the judgment this record carries was over a different "
                            f"sentence; the route is a fresh invocation under a new slug, which "
                            f"reads the node as it now stands")
    return problems, None


def bind_record(target: Path, spec_root: Path, record: Path, replace: bool = False,
                workspace: Path | None = None) -> int:
    """Every binding one implementation record states, written as one act.

    Bound one node at a time, a record pays a full specification validation and a full
    read-and-rewrite of the trace per node. Here they are paid once, and the whole of it is
    refused before anything is written:
    a delivery half bound describes a link nobody made, and the file it would leave behind reads
    exactly like a complete one.

    Refused means over form. What a reconciliation's judgment held back is a different thing and
    is not refused here: those nodes carry no `encoded_at`, the rest are written, and `left_owed()`
    is what keeps the partial act legible.

    Given the staging's workspace, refused also means over time: a staged file or a pinned node
    that moved since the staging read it refuses the record whole, because the bind stamps
    what a judge read and the workspace is the record of what that was. An implementation
    record has no workspace, and without one each file is read fresh."""
    if not target.is_dir():
        print(f"cannot run: {target} is not a directory", file=sys.stderr)
        return CANNOT_RUN
    if not spec_root.is_dir():
        print(f"cannot run: {spec_root} is not a directory", file=sys.stderr)
        return CANNOT_RUN

    pairs, problems = encoded_in(record)
    for problem in problems:
        print(f"cannot run: {problem}", file=sys.stderr)
    if problems:
        return CANNOT_RUN
    if not pairs:
        print(f"nothing to bind: {record} names no node with `encoded_at`; a node the record "
              f"answers only by `how` reached no file, and a bind with none is refused")
        return 0

    nodes, status = sound_specification(spec_root)
    if nodes is None:
        return status

    home = home_of(target)
    certifications = certified_in(record)
    declared_steps = registry_steps(home, offset_of(target, home))
    refusals, folded = [], []
    # A reconciliation's bind stamps what a judgment read, and says so per file: `judged` is what
    # lets a later review borrow that reading instead of buying it twice. An implementation
    # record's bind stamps what a delivery wrote, which nobody has read against the node yet, so
    # its entries carry no `judged` — and replacing an entry by path is what clears one.
    judged_here = as_reconciliation(record) is not None
    if workspace is not None:
        stale_since_staging, cannot = staged_problems(workspace, target, nodes)
        if cannot is not None:
            print(f"cannot run: {cannot}", file=sys.stderr)
            return CANNOT_RUN
        refusals += stale_since_staging
    for node_id, files in pairs:
        if node_id not in nodes:
            refusals.append(f"{spec_root} holds no node {node_id}, which {record.name} says the "
                            f"source encodes")
            continue
        traced, missing = traced_files_of(target, home, files)
        refusals += [f"{node_id}: {problem}" for problem in missing]
        # A certification's proof is pinned the way the files are, read now, and a proof that is
        # not there refuses the record whole: a binding naming a test nobody can open decides
        # nothing.
        certification = None
        if node_id in certifications:
            proof, absent = traced_files_of(target, home, certifications[node_id]["proof"])
            refusals += [f"{node_id}: proof {problem}" for problem in absent]
            # Symmetric with `--stage --certify`, which refuses the same string. A binding naming
            # a step the registry does not declare names one nothing can run, and every later
            # form would read it as decided by a run that can never happen.
            named_step = certifications[node_id]["step"]
            if declared_steps is not None and named_step not in declared_steps:
                refusals.append(
                    f"{node_id}: the record certifies it as decided by the step `{named_step}`, "
                    f"which {project.PROJECT_FILE}'s registry for this target does not declare"
                    + (f"; it declares {', '.join(sorted(declared_steps))}" if declared_steps
                       else " — it declares none"))
            elif not absent:
                certification = {"step": named_step, "proof": proof}
        if not missing and (node_id not in certifications or certification is not None):
            if judged_here:
                traced = [{**entry, JUDGED: True} for entry in traced]
            folded.append((node_id, traced, certification))

    declared, refusal = opened(target, spec_root, home)
    if refusal is not None:
        refusals.append(refusal)
    if declared is not None:
        offset = Path(os.path.relpath(target.resolve(), home.resolve()))
        refusals += unaccounted(record, declared, nodes, offset)
        refusals += omitted_problems(record, declared, home, offset, nodes)
    if refusals:
        for problem in refusals:
            print(f"cannot bind: {problem}")
        print(f"\n{len(refusals)} problem(s); nothing was bound. A record's bindings are one act, "
              f"so a trace holding some of them would say this delivery is linked when it is not.")
        return 1

    withdrawn = released_in(record)
    held = []
    for node_id, traced, certification in folded:
        let_go = None
        if certification is not None:
            fresh = True
        elif node_id in withdrawn:
            # This record asked whether the test still decides the node and the auditor said it
            # does not. Carrying the standing certification would leave the trace deciding by a
            # test a judgment has just refused, and the record's own notes saying otherwise.
            let_go = withdrawn_receipt(declared, node_id)
            fresh = False
        else:
            certification, let_go = carried_certification(declared, node_id, home)
            fresh = False
        count, dropped = fold(declared, node_id, nodes[node_id]["digest"], traced, replace,
                              certification)
        held.append((node_id, count, dropped, certification if fresh else None, let_go))
    if write_trace(target, declared) != 0:
        return 1
    for node_id, count, dropped, fresh_certification, let_go in held:
        print(f"bound {node_id} to {count} file(s)")
        if dropped:
            print(released(node_id, dropped))
        if fresh_certification is not None:
            print(certified(node_id, fresh_certification))
        if let_go:
            print(let_go)
    print(f"{len(held)} binding(s) written at {trace_path(target)}, read from {record.name}")
    let_go_paths = sum(len(dropped) for _, _, dropped, _, _ in held)
    if let_go_paths:
        print(f"{let_go_paths} path(s) released across {sum(1 for _, _, d, _, _ in held if d)} "
              f"node(s); a total is here because one node's receipt is easy to read past in a "
              f"record that bound twenty")
    acted = {entry["path"]: entry["digest"]
             for _, traced, _ in folded for entry in traced}
    stale = stale_after(declared, home, acted, {node_id for node_id, _, _ in folded})
    if stale:
        print(left_stale(stale))
    owed = withheld(record)
    if owed:
        print(left_owed(owed, record))
    return 0


def prune(target: Path) -> int:
    """Drop every binding to a node the specification no longer holds, and nothing else.

    This is the only thing here that deletes, and it exists because one class of drift had no exit
    at all. A node the specification dropped cannot be rebound — `--bind` refuses a node that is
    not there — and a trace is hand-edited by nobody, this script being its one writer. So the
    entry stayed, its finding repeated on every `--check`, and the pile of them is what a real
    drift arriving later disappears into.

    It refuses the two classes it is not for, and the refusal is the point rather than a
    conservatism. A file that moved or vanished is drift with an owner and a remedy: the node is
    still in the specification, still answered by code, and deleting the binding would destroy the
    one record of which node that code answers to while reporting the tree as clean. The narrow
    class is safe for the opposite reason — the node is gone, so the entry links code to nothing,
    and nothing downstream can ask a question of it that an absence does not already answer.

    It reads the specification through the same pipeline `--check` does, and refuses over one that
    does not hold together. Pruning against a specification nobody could read would delete bindings for
    nodes that exist, on the strength of not having been able to see them."""
    if not target.is_dir():
        print(f"cannot run: {target} is not a directory", file=sys.stderr)
        return CANNOT_RUN

    path = trace_path(target)
    declared = load(target)
    if declared is None:
        print(f"no trace file: {path} does not exist; there is nothing to prune")
        return 0

    problems = problems_of(declared)
    if problems:
        for problem in problems:
            print(f"{path}: {problem}")
        return 1

    findings, refusals = drift_of(declared, home_of(target))
    if refusals:
        for refusal in refusals:
            print(refusal)
        print(f"\nnothing was pruned: a specification this cannot read says nothing about which "
              f"bindings it still holds")
        return 1

    stale = sorted({finding[1] for finding in findings if finding[0] == ORPHANED})
    if not stale:
        held = len(declared.get("bindings") or [])
        print(f"nothing to prune: every one of {held} binding(s) names a node the specification "
              f"still holds")
        return 0

    spec_root = home_of(target) / declared["specification"]
    nodes, _ = spec.collect(spec_root, spec.contracts())
    followed = rename_targets(spec_root, stale, nodes)
    by_node = {entry["node"]: entry for entry in declared["bindings"]}
    kept: list[dict] = []
    receipts: list[str] = []
    dropped: list[str] = []
    for entry in declared["bindings"]:
        node_id = entry["node"]
        if node_id not in followed:
            if node_id in stale:
                dropped.append(node_id)
                receipts.append(f"dropped {node_id}: the specification no longer holds it")
            else:
                kept.append(entry)
            continue
        new_id = followed[node_id]
        existing = by_node.get(new_id)
        if existing is None:
            entry["node"] = new_id
            kept.append(entry)
            receipts.append(f"followed rename {node_id} → {new_id} "
                            f"({len(entry['files'])} file(s) kept)")
            continue
        held = {file_entry["path"] for file_entry in existing["files"]}
        joined = [file_entry for file_entry in entry["files"] if file_entry["path"] not in held]
        existing["files"] = sorted(existing["files"] + joined,
                                   key=lambda file_entry: file_entry["path"])
        receipts.append(f"followed rename {node_id} → {new_id} ({len(joined)} file(s) kept, "
                        f"joined to the binding {new_id} already holds)")
    declared["bindings"] = sorted(kept, key=lambda entry: entry["node"])
    if write_trace(target, declared, act="prune") != 0:
        return 1
    for receipt in receipts:
        print(receipt)
    remaining = len(declared["bindings"])
    print(f"\n{len(dropped)} binding(s) pruned and {len(followed)} followed to a renamed node "
          f"at {path}; {remaining} remain."
          + (" What was dropped was a link to a node that is gone — every drift with a node "
             "still in the specification is still here, and still owed a rebind." if dropped
             else ""))
    return 0


def release(target: Path, files: list[str]) -> int:
    """Drop a file the tree no longer holds from every binding that names it, and drop a binding
    left holding nothing.

    A path is read the way the trace stores it — from the trace's own directory, exactly as
    `--check` prints it — and, failing that, from the target source root, the anchor every other
    form reads. The whole call is refused before anything is written: a path the tree still holds
    is reconciled and never released, and a path no binding names has nothing to release."""
    if not target.is_dir():
        print(f"cannot run: {target} is not a directory", file=sys.stderr)
        return CANNOT_RUN

    path = trace_path(target)
    declared = load(target)
    if declared is None:
        print(f"cannot release: {path} does not exist; nothing has been bound, so no binding "
              f"names any of these paths")
        return 1
    problems = problems_of(declared)
    if problems:
        for problem in problems:
            print(f"{path}: {problem}")
        return 1

    home = home_of(target)
    offset = offset_of(target, home)
    bound = {file_entry["path"] for entry in declared["bindings"]
             for file_entry in entry.get("files") or []}
    gone: list[str] = []
    unknown: list[str] = []
    standing: list[str] = []
    for given in files:
        anchored = given if offset == "." else (PurePosixPath(offset) / given).as_posix()
        stored = given if given in bound else anchored if anchored in bound else None
        if stored is None:
            unknown.append(f"{given}: no binding names it — a path is spelled as the trace "
                           f"stores it, from {home}, or from {target}, the target source root; "
                           f"`--encodes` says what a file is bound to")
            continue
        if (home / stored).is_file():
            standing.append(stored)
        elif stored not in gone:
            gone.append(stored)
    for stored in standing:
        print(f"cannot run: {stored} still exists; a file that exists is reconciled, never "
              f"released", file=sys.stderr)
    if standing:
        return CANNOT_RUN
    for said in unknown:
        print(f"cannot release: {said}")
    if unknown:
        return 1

    kept: list[dict] = []
    receipts: list[str] = []
    for entry in declared["bindings"]:
        dropped = sorted(file_entry["path"] for file_entry in entry["files"]
                         if file_entry["path"] in gone)
        if not dropped:
            kept.append(entry)
            continue
        receipts.append(released(entry["node"], dropped, act="--release"))
        remaining = [file_entry for file_entry in entry["files"]
                     if file_entry["path"] not in gone]
        if remaining:
            entry["files"] = remaining
            kept.append(entry)
        else:
            receipts.append(emptied(entry["node"]))
    declared["bindings"] = kept
    if write_trace(target, declared, act="release") != 0:
        return 1
    for receipt in receipts:
        print(receipt)
    print(f"\n{len(gone)} path(s) released at {path}; {len(kept)} binding(s) remain.")
    return 0


def main() -> int:
    args = sys.argv[1:]
    if "--help" in args:
        # The docstring is this script's one home of what it does and how it is called,
        # so `--help` prints that rather than a second copy of it that could drift.
        print(__doc__.strip())
        return 0
    check = "--check" in args
    show_all = "--all" in args
    do_bind = "--bind" in args
    do_record = "--bind-record" in args
    do_prune = "--prune" in args
    do_release = "--release" in args
    do_reconciliation = "--reconciliation" in args
    do_owed = "--owed" in args
    do_encodes = "--encodes" in args
    do_stage = "--stage" in args
    do_fold = "--fold" in args
    replace = "--replace" in args
    do_rank = "--rank" in args
    do_changed = "--changed" in args
    do_convergence = "--convergence" in args
    do_audit = "--audit" in args
    do_review = "--review" in args
    also: list[str] = []
    while "--node" in args:
        at = args.index("--node")
        if at + 1 >= len(args) or args[at + 1].startswith("--"):
            print("cannot run: --node takes a specification node identity", file=sys.stderr)
            return CANNOT_RUN
        also.append(args[at + 1])
        del args[at:at + 2]
    demonstrated: list[Path] = []
    while "--demonstrated" in args:
        at = args.index("--demonstrated")
        if at + 1 >= len(args) or args[at + 1].startswith("--"):
            print("cannot run: --demonstrated takes the path of a proof record", file=sys.stderr)
            return CANNOT_RUN
        demonstrated.append(Path(args[at + 1]))
        del args[at:at + 2]
    captured_run: Path | None = None
    if "--run" in args:
        at = args.index("--run")
        if at + 1 >= len(args) or args[at + 1].startswith("--"):
            print("cannot run: --run takes the directory bin/run.py wrote", file=sys.stderr)
            return CANNOT_RUN
        captured_run = Path(args[at + 1])
        del args[at:at + 2]
        if "--run" in args:
            print("cannot run: --run is given once; one run answers this fold's mechanical tier",
                  file=sys.stderr)
            return CANNOT_RUN
    workspace_given: Path | None = None
    if "--workspace" in args:
        at = args.index("--workspace")
        if at + 1 >= len(args) or args[at + 1].startswith("--"):
            print("cannot run: --workspace takes the directory --stage wrote", file=sys.stderr)
            return CANNOT_RUN
        workspace_given = Path(args[at + 1])
        del args[at:at + 2]
        if "--workspace" in args:
            print("cannot run: --workspace is given once; one staging read what this bind stamps",
                  file=sys.stderr)
            return CANNOT_RUN
    certify: Path | None = None
    if "--certify" in args:
        at = args.index("--certify")
        if at + 1 >= len(args) or args[at + 1].startswith("--"):
            print("cannot run: --certify takes the path of a YAML file listing the "
                  "certifications — node, proof, step", file=sys.stderr)
            return CANNOT_RUN
        certify = Path(args[at + 1])
        del args[at:at + 2]
        if "--certify" in args:
            print("cannot run: --certify is given once; one file lists every certification",
                  file=sys.stderr)
            return CANNOT_RUN
    args = [a for a in args
            if a not in ("--check", "--all", "--bind", "--bind-record", "--replace", "--prune",
                         "--release", "--reconciliation", "--owed", "--encodes", "--stage",
                         "--fold", "--rank", "--changed", "--audit", "--review",
                         "--convergence")]
    named = [name for name, given in (("--check", check), ("--bind", do_bind),
                                      ("--bind-record", do_record),
                                      ("--prune", do_prune),
                                      ("--release", do_release),
                                      ("--reconciliation", do_reconciliation),
                                      ("--owed", do_owed),
                                      ("--encodes", do_encodes),
                                      ("--stage", do_stage),
                                      ("--fold", do_fold),
                                      ("--convergence", do_convergence)) if given]
    if len(named) > 1:
        print(f"cannot run: {' and '.join(named)} are mutually exclusive", file=sys.stderr)
        return CANNOT_RUN
    if replace and not (do_bind or do_record):
        print("cannot run: --replace only applies to --bind and --bind-record", file=sys.stderr)
        return CANNOT_RUN
    if show_all and not (check or do_owed or do_rank or do_convergence):
        print("cannot run: --all only applies to --check, --owed, --rank and --convergence; in "
              "each it is what lists the rows the report holds back", file=sys.stderr)
        return CANNOT_RUN
    if do_rank and not do_encodes:
        print("cannot run: --rank is a mode of --encodes", file=sys.stderr)
        return CANNOT_RUN
    if do_changed and not do_encodes:
        print("cannot run: --changed is a mode of --encodes", file=sys.stderr)
        return CANNOT_RUN
    if do_changed and do_rank:
        print("cannot run: --changed names a file set and --rank reads them all; a ranking over "
              "the files one change touched is a ranking of that change, not of the tree",
              file=sys.stderr)
        return CANNOT_RUN
    if do_audit and not do_stage:
        print("cannot run: --audit is a mode of --stage", file=sys.stderr)
        return CANNOT_RUN
    if do_review and not do_stage:
        print("cannot run: --review is a mode of --stage", file=sys.stderr)
        return CANNOT_RUN
    if do_audit and do_review:
        print("cannot run: --audit and --review are two stagings; a review re-reads files a "
              "delivery wrote, an audit re-reads claims nothing moved", file=sys.stderr)
        return CANNOT_RUN
    if demonstrated and not (do_stage and do_review):
        print("cannot run: --demonstrated is a mode of --stage --review; a proof's claim is "
              "settled by the review that reads the proof, and by nothing else", file=sys.stderr)
        return CANNOT_RUN
    if also and not do_review:
        print("cannot run: --node is a mode of --stage --review; a reconciliation's node set is "
              "the trace's alone", file=sys.stderr)
        return CANNOT_RUN
    if captured_run is not None and not do_fold:
        print("cannot run: --run is a mode of --fold; it names the run that answers the "
              "mechanical tier a staging separated", file=sys.stderr)
        return CANNOT_RUN
    if workspace_given is not None and not do_record:
        print("cannot run: --workspace is a mode of --bind-record; it names the staging whose "
              "digests the bind holds the record to", file=sys.stderr)
        return CANNOT_RUN
    if certify is not None and (not do_stage or do_audit):
        print("cannot run: --certify is a mode of --stage, and never of an audit; an audit "
              "re-examines standing claims over a tree nothing changed, and a certification is a "
              "claim about a test a delivery just wrote", file=sys.stderr)
        return CANNOT_RUN

    if do_reconciliation:
        if len(args) != 1 or args[0].startswith("--"):
            print("cannot run: expected --reconciliation <reconciliation-record>", file=sys.stderr)
            return CANNOT_RUN
        return reconciliation(Path(args[0]))
    if not TRACE_CONTRACT.is_file():
        print(f"cannot run: {TRACE_CONTRACT} is missing; nothing can be validated without it",
              file=sys.stderr)
        return CANNOT_RUN

    if do_record:
        if len(args) != 3:
            print("cannot run: expected --bind-record <target-root> <spec-root> "
                  "<record> [--workspace <workspace-dir>] [--replace]", file=sys.stderr)
            return CANNOT_RUN
        target, spec_root, record = args
        return bind_record(Path(target), Path(spec_root), Path(record), replace, workspace_given)

    if do_prune:
        if len(args) != 1 or args[0].startswith("--"):
            print("cannot run: expected --prune <target-root>", file=sys.stderr)
            return CANNOT_RUN
        return prune(Path(args[0]))

    if do_release:
        if len(args) < 2 or any(a.startswith("--") for a in args):
            print("cannot run: expected --release <target-root> <file> [<file> ...], every file "
                  "spelled as the trace stores it or from the target source root",
                  file=sys.stderr)
            return CANNOT_RUN
        return release(Path(args[0]), args[1:])

    if do_owed:
        if len(args) != 1 or args[0].startswith("--"):
            print("cannot run: expected --owed <target-root> [--all]", file=sys.stderr)
            return CANNOT_RUN
        return owed(Path(args[0]), show_all)

    if do_convergence:
        if len(args) != 3 or any(a.startswith("--") for a in args):
            print("cannot run: expected --convergence <target-root> <spec-root> "
                  "<work-root-parent> [--all]; the last is the directory the initiatives sit in, "
                  "not one initiative", file=sys.stderr)
            return CANNOT_RUN
        return convergence(Path(args[0]), Path(args[1]), Path(args[2]), show_all)

    if do_encodes:
        if do_rank:
            if len(args) != 1 or args[0].startswith("--"):
                print("cannot run: expected --encodes --rank <target-root> [--all]",
                      file=sys.stderr)
                return CANNOT_RUN
            return rank(Path(args[0]), show_all)
        if do_changed:
            if len(args) not in (1, 2) or any(a.startswith("--") for a in args):
                print("cannot run: expected --encodes --changed <target-root> [<ref>]",
                      file=sys.stderr)
                return CANNOT_RUN
            return encodes_changed(Path(args[0]), args[1] if len(args) == 2 else None)
        if len(args) < 2 or any(a.startswith("--") for a in args):
            print("cannot run: expected --encodes <target-root> <file> [<file> ...], every file "
                  "spelled from the target source root", file=sys.stderr)
            return CANNOT_RUN
        return encodes(Path(args[0]), args[1:])

    if do_stage:
        if len(args) < 5 or any(a.startswith("--") for a in args):
            print("cannot run: expected --stage <target-root> <spec-root> <slug> "
                  "<workspace-dir> <file> [<file> ...] [--audit | --review [--node <node> ...]] "
                  "[--certify <file>], every file spelled from the target source root",
                  file=sys.stderr)
            return CANNOT_RUN
        target, spec_root, slug, workspace, *files = args
        return stage(Path(target), Path(spec_root), slug, Path(workspace), files, do_audit,
                     do_review, also, certify, demonstrated)

    if do_fold:
        if len(args) != 4 or any(a.startswith("--") for a in args):
            print("cannot run: expected --fold <target-root> <workspace-dir> <premise-file> "
                  "<record> [--run <run-dir>]", file=sys.stderr)
            return CANNOT_RUN
        target, workspace, premise, record = args
        return fold_returns(Path(target), Path(workspace), Path(premise), Path(record),
                            captured_run)

    if do_bind:
        if len(args) < 4:
            print("cannot run: expected --bind <target-root> <spec-root> <node> "
                  "<file> [<file> ...] [--replace]", file=sys.stderr)
            return CANNOT_RUN
        target, spec_root, node_id, *files = args
        return bind(Path(target), Path(spec_root), node_id, files, replace)

    if len(args) != 1 or args[0].startswith("--"):
        print("cannot run: expected [--check [--all]] <target-root>", file=sys.stderr)
        return CANNOT_RUN

    target = Path(args[0])
    if not target.is_dir():
        print(f"cannot run: {target} is not a directory", file=sys.stderr)
        return CANNOT_RUN

    path = trace_path(target)
    declared = load(target)
    if declared is None:
        print(f"no trace file: {path} does not exist; nothing has been bound yet")
        return 0

    problems = problems_of(declared)
    if problems:
        for problem in problems:
            print(f"{path}: {problem}")
        return 1

    count = len(declared.get("bindings") or [])
    if not check:
        by_test = len(test_decided(declared, home_of(target),
                                   offset_of(target, home_of(target))))
        print(f"trace sound: {count} binding(s)"
              + (f", {by_test} of them decided by a certified test" if by_test else "")
              + f", traced against {declared['specification']}")
        return 0

    home = home_of(target)
    # The report names the file it read, the way the absent case already does. A drift report is
    # a claim about a tree, and the trace is its source; naming it also makes the one redundant
    # invocation visible — a trace is one file per git toplevel, so a second target under the
    # same toplevel re-reads this exact file and prints this exact report.
    print(f"trace: {path} — one file per git toplevel; every target under it reads this same one")
    findings, refusals = drift_of(declared, home,
                                  registry_steps(home, offset_of(target, home)))
    if refusals:
        for refusal in refusals:
            print(refusal)
        return 1

    # What a target declared freely edited is held back from the listing, never from the reading:
    # the finding was computed either way, and `--all` prints it. Suppression is a report's
    # decision about what a reader can act on, so nothing above it knows this happened.
    prefixes = [] if show_all else freely_edited(home)
    listed, held = partitioned(findings, prefixes)

    if listed:
        # Class by class rather than one flat list: the tally is what a reader acts on, and the
        # orphaned count is what says how much of this report no rebind will ever shorten.
        # `code` alone is listed per file (code_report): its remedy is a reconciliation, which
        # is invoked over a file set, so its listing is keyed the way the remedy consumes it.
        for cls in (ORPHANED, MOVED, PROOF):
            for finding in [f for f in listed if f[0] == cls]:
                print(finding[3])
        code_listed = [f for f in listed if f[0] == CODE]
        for line in code_report(code_listed):
            print(line)
        decided = decided_constraints(home, offset_of(target, home))
        on_step = [f for f in code_listed if f[1] in decided]
        if on_step:
            print(step_decided(on_step, decided))
        by_test = test_decided(declared, home, offset_of(target, home))
        on_test = [f for f in code_listed if f[1] in by_test and f[1] not in decided]
        if on_test:
            print(step_decided(on_test, by_test, "a binding a certified test decides"))
        print(f"\n{len(listed)} drift finding(s) over {count} binding(s):")
        for cls in (ORPHANED, MOVED, PROOF, CODE):
            # The suppressed count rides its own class's line rather than sitting under the tally:
            # `0 code` printed above a receipt saying one was held back is a line a reader can
            # finish and walk away from.
            also = f" ({len(held)} suppressed)" if cls == CODE and held else ""
            tally = sum(1 for f in listed if f[0] == cls)
            # The file count rides the code tally because the listing above is keyed by file:
            # `16 code over 2 file(s)` is what says sixteen findings are two acts, not sixteen.
            over = (f" over {len({f[2] for f in code_listed})} file(s)"
                    if cls == CODE and code_listed else "")
            print(f"  {tally} {cls}{over}{also}: {CLASSES[cls]}")
    else:
        print(f"no drift: {count} binding(s) match the specification and the code as both stand "
              f"now" if not held else
              f"no drift to act on: {count} binding(s), and every difference found sits under a "
              f"target this project declares freely edited")
    if held:
        print(suppressed(held, prefixes))
    return 1 if listed else 0


if __name__ == "__main__":
    raise SystemExit(main())
