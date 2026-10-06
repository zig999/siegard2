---
name: reconcile
description: Reconciles source that changed without a rebind — whatever wrote it — with the specification the trace says it encodes — reads which nodes a named file set is bound to, holds that source to them through the conformance judgment, records the answer per node, and rebinds only what the judgment cleared. Use when source was edited by hand, resolved in a merge, or rewritten by a delivery while other nodes' bindings still claim it; as an audit over a set the human names, to re-examine standing bindings that never drifted; or as an adoption of source no delivery wrote, binding each node /analyse wrote from it to the files that hold its fact. Not for changing the specification (that is /analyse), not for routing a wrong behavior into a task (that is /plan-work), not for reviewing what a delivered task produced (that is /review-change), and never for writing source.
effort: medium
---

You reconcile source that changed without a rebind — whatever wrote it — with the specification
it is bound to, and you stop. One invocation, one file set.

Every other bind this framework writes comes out of a delivery: an implementation record says which
nodes the source encodes and where, and the bind states exactly that and never a second judgment
about it. This entry point exists because a binding goes stale other ways — a correction typed in
during an incident, a file resolved by hand during a merge, a delivery rewriting a file that other
nodes' bindings still claim, since a bind restamps only the delivering task's own nodes. The file
changes without a rebind, the trace keeps asserting a digest that is not there any more, and it
asserts it silently: `--check` is the only thing that ever says so, and nothing was going to run
it.

What you produce is a rebind and the record that justifies it. **You never write source, and you
never write a specification node.** Where the reconciliation cannot be made for a node — where the
source now states something that node does not hold — you bind that node nothing and hand back
the invocations that could resolve it, without choosing between them. The nodes the judgment did
clear are bound in the same act: the judgment is per node, so the bind is too, and a reading that
succeeded is not discarded because a sibling reading did not.

## Required inputs

A missing input is a stop, not a default:

1. **the file set** — every path this reconciliation covers, listed explicitly, each relative to
   the target source root. Named by the human. **Never discovered**: a reconciliation that chose
   its own scope covers a different set each run, and what it writes is the one claim this
   framework keeps after every plan and delivery root is gone.
2. **the project root** — where `siegard.json` lives. Named by the human; inferred rather than
   named, its absence is a stop.
3. **the target** — which of the project's target source roots these files sit under, by the key
   `siegard.json`'s `targets` names it. Where `targets` declares exactly one key and the
   invocation names none, that key is the target: a set of one holds no choice, so it is
   decided and disclosed in the report, never asked.
4. **the slug** — this reconciliation's own name, under `siegard-reconcile/` at the target's git
   toplevel. A slug already taken is a stop and not a suffix: the record it would overwrite is the
   justification for a binding that is still in the trace.

One optional input: **certifications** — for a node the file set encodes, the test file(s) the
human offers as its proof, spelled from the target source root, and the registry step that runs
them, by the name `commands[].step` gives it. Named by the human, never chosen here: which test
proves a fact is a claim about the project's own suite, and the judgment below decides only
whether the claim holds — the auditor's rule, that the tests would fail if the fact stopped
holding. Where it holds, the bind writes the node as one a test decides, so a later drift on its
files is answered by the step's run rather than by a fresh reading. Absent, nothing is certified
and every binding stays decided by reading, which is every binding's default.

And one mode, named by the human and never inferred: **adoption** — the file set is source no
delivery wrote, and the invocation also names the **candidates**, the nodes `/analyse` wrote from
material read from that source, which its report lists, and optionally the files kept **outside**
the judgment, which no judge reads. «A binding of adopted source rests on a reconciliation record
whose judgment cleared the pair» (SPEC-005 R3), and the candidates are the human's to name, never
discovered here. Without the word, this is an ordinary reconciliation and a file the trace binds
nothing to is reported and goes no further.

Run `python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/project.py <project-root>` once, before anything else.
`specification_root` and `targets` answer only from here: naming one of them in the invocation
instead has no effect, and where the file does not declare one, that is a stop — the report carries
the `/siegard-config` invocation ready to paste, naming the project root and every field missing.
From here on, "the target source root" means `targets[<the target>]`, and "the specification root"
means `specification_root` as resolved.

**No work root, no delivery root, no task, no plan.** This entry point deliberately asks for none
of them, and that is the whole of what it adds: the judgment it runs already existed and was
reachable only through a delivery that a hand edit does not have.

Absent inputs stop once, together: one stop naming everything missing, so the human answers once —
never a question at a time.

## Before anything: the tree

Here the usual rule inverts by half, and the half that inverts is the point. Everywhere else a
pending change is somebody's work in progress; here it is the subject.

**The named files must be committed, and so must every proof a certification names, and so must
every candidate node's own file.** `git status --porcelain -- <each named path> <each proof path>
<the specification root>` must print nothing. Not because a pending edit is hard to read, but
because a bind records a digest on both sides: the digest of an uncommitted edit points at content
the next checkout erases, and a node stamped from text nobody committed is a binding to a
specification that may never have existed — the drift that would report afterwards, either way, is
drift nobody caused. Output is a stop that names what is pending — committing or discarding is the
human's decision, never this skill's.

`siegard-trace.json` must be clean for the same reason every other entry point wants its own output
clean: it is what this invocation writes, and a diff only says what this run did when it starts from
a committed state. A target source root not under git control is a stop as well — without git there
is no trace file's history, and the record you write points at a commit that has to exist.

The rest of the repository is not this skill's business. The pathspec is the scope.

## Read the contract

Read `${CLAUDE_PLUGIN_ROOT}/schemas/reconciliation.json`. It is the single home of what a
reconciliation record may and must declare — the fields, which of them a cleared node carries and
which a node the judgment refused carries instead, and one example per outcome. The fold below is
what writes the record against it; what you author is the premise it folds in, and the contract's
`summary` and `files[].change` descriptions are the standard those lines are held to. Do not work
from memory of it, and do not restate it: what you remember is not what the validator will apply.

`${CLAUDE_PLUGIN_ROOT}` is set where this skill runs as an installed plugin. Where it is not, the
plugin root is the directory that holds `schemas/` and `bin/` side by side — in a vendored install,
the `.claude/` directory this skill's tree sits under. Every path below resolves the same way.

## The order

```
situate → stage → judge → capture → fold → bind → report → stop
```

### 1. Situate

- **The specification must hold together before anything is read against it.** Run
  `python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/spec.py <specification-root>`. Anything but a clean pass is
  a stop reported verbatim: this invocation does not repair a specification an earlier one left
  broken, and a judgment against a root that does not hold is a judgment about nothing.
- **The trace must hold together too.** Run
  `python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/trace.py <target-source-root>`. A trace file that does not
  exist is a stop with a plain answer: nothing has ever been bound in this target, so there is no
  link to reconcile, and what the human wants is a delivery — or, for source no delivery wrote, an
  adoption, the one invocation that begins without a trace and writes the first one.
- **The record's own path must be free.** `siegard-reconcile/<slug>.md`, at the target source
  root's git toplevel — the directory `git -C <target-source-root> rev-parse --show-toplevel`
  prints, which is where `siegard.json` and `siegard-trace.json` already sit. A path that exists is
  the stop input 4 describes.

### 2. Stage

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/trace.py --check <target-source-root>
```

This is the reverse lookup for what drifted, and drift is all it reports: the trace is keyed by
node, and what makes a file findable in this output is that the file changed. The `code` class is
listed per file — one line naming the file, the reason, and every binding the change staled, which
is this skill's own shape: a reconciliation is invoked over a file set. Read the findings, and
keep the lines whose path is in the file set.

Then, for the whole file set, into a fresh workspace directory nothing commits (`mktemp -d` is the
ordinary choice — the workspace is a reading copy, and a committed copy of node text would be a
second home for it):

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/trace.py --stage <target-source-root> <specification-root> \
    <slug> <workspace> <each named path> [--audit] [--certify <certifications file>]
```

This is the locate step, run by the one reader that cannot miss a binding. It computes every node
each named file is bound to, writes the node set per file into the workspace's manifest, writes
one **node pack** per file — the full text of every node that file's judge must read, each entry
naming its source path and digest — writes the **candidate index** for the whole batch, separates
out every pair whose re-judgment would buy nothing (see the fold step for what lands where), and
creates `siegard-reconcile/<slug>.returns/` empty, beside the record's own reserved path. Run it;
never infer any of it, and never reconstruct a node set by reading `siegard-trace.json` yourself.
A node missed in a hand reading is a judge handed an incomplete node set, and the record that
comes back reads exactly like a complete one.

**Two anchors meet here, and only one of them belongs in what anyone writes.** The git toplevel
is the anchor of what `trace.py` *prints* — a `--check` finding, an entry of the trace file — and
nothing else. Everything written — the file set the human gave you, every path in the premise,
and the `file` every finding names — is spelled from the target source root, the anchor every
other record in this framework uses; the pack header hands the judge that spelling verbatim, and
the judge copies it. `--stage` takes the human's own spelling and refuses the other one naming
the correction, which is the cheap failure; the expensive one is converting the human's paths
the other way to match the drift report you just read. **What is judged is every node the trace binds to the set, and never a chosen subset** —
which nodes a file answers to is what the trace holds, and reconciling a file against the part of
the specification that happens to agree with it is the failure this whole route exists to prevent.
The one subtraction is `--stage`'s own, mechanical and rechecked at bind time: a pair whose
binding computes at the file's content as it stands, with no open finding against it in the
corpus, was judged over these exact bytes already, and re-judging it buys a second reading of
text that did not move.

**Where the human's ask is an audit, pass `--audit` and omit nothing.** An audit is this same
invocation over a set whose bindings did not drift: a binding over-broad from the day it was
written never drifts, so nothing keyed by change ever re-examines it, and the human's ask to
re-examine standing claims is the one trigger there is. The staging then hands every pair to a
judge, the premise's `summary` says the source did not change and the claims are what is being
re-read, and everything downstream runs unmodified — a claim confirmed is restamped with the
record justifying it, a fact held nowhere blocks its node and the report hands the
`--bind ... --replace` release ready to paste, and a finding nobody acts on stays in the corpus
where `--owed` repeats it. `trace.py --encodes --rank <target-source-root>` is where an audit's
candidate set comes from — the two accretion counts, as facts; the file set is still the human's
to name. An audit is never chosen by this skill: invoked without the word, a reconciliation
omits what the guard allows, and that is the default for a reason — re-judging unchanged pairs
is bought deliberately or not at all.

Four states the staging separates, and they do not all continue:

- **A file with nodes in the manifest.** This is the subject. Its judge is spawned below.
- **A file the trace binds nothing to.** Reported, never guessed. Deciding which node an untraced
  file answers to is a delivery's judgment or an analysis's, and inventing one here would write
  this framework's most durable claim out of its thinnest evidence. The manifest holds it under
  `unbound`, the fold carries it into the record, and it goes no further — except on an
  adoption, where the analysis's candidates are what its judge reads it against.
- **A file whose every pair the staging omitted.** Nothing left to judge: each of its bindings
  was stamped over the content on disk now and nothing is owed against any of them. It stays in
  the file set and in the premise, and the record accounts for it under `pairs_omitted`.
- **A node reported under the orphaned class.** Stop for that node, and say so plainly: the
  specification no longer holds it, no bind can repair the entry, and the route is
  `trace.py --prune` followed by whatever put the fact somewhere else. `--stage` hands no judge
  such a node and names each one; do not bind around it, and do not prune it from here — this
  invocation's writes are its own record and its own bindings.

**A pair a run decides is handed no judge, and the staging separates it under `mechanical`.**
Two kinds land there and both are answered the same way: a constraint some step of the project's
registry `decides`, and a node a certified test decides. A reading of either would re-decide
mechanically what a run settles exactly — at a model's recall, and at the price of the whole
file's delegation. Two guards send such a pair back to a judge instead, and neither is yours to
override: a certification whose test's text moved is no longer live, and a node whose own text
moved was decided by a step or a test that was never asked about the sentence which replaced it.
A pair that is current and owes nothing is omitted before either tier reaches it — nothing has to
re-decide it, so it needs no run either.

**Where the human offered certifications, write them into a small YAML file in the workspace and
pass it as `--certify`** — a list, each entry the node, its `proof` paths and its `step`, exactly
as the human stated them. The staging refuses, before writing anything, a node none of the named
files encodes, a proof that is not there, and a step the registry does not declare; a refusal is
the human's to answer, never a default. It never omits a pair of a node being certified — the
certification rides a fresh reading of the node against its file — and it writes one
**certification pack** per node beside the file packs: the node's text with its source named, the
proof resolved to absolute paths, the step, and the return contract's path. The pack is the whole
of what the auditor is handed.

**A node written since the bind is in none of that.** The trace is what this step reads, and a node
no delivery ever encoded has no entry in it — which is the ordinary state of every node `/analyse`
wrote after the source it governs was written, and that alternation is the rhythm this framework
expects rather than an exception to it. Such a node cannot be cleared here and cannot be bound here:
it was never delivered, and binding it is a delivery's act. What it can be is a **candidate**. Where
the human names nodes written since this source was last bound — `/analyse` ends by listing exactly
those identities — they join the candidate tier the judgment is passed, so a fact one of them now
holds is attributed to it instead of reported as held by nothing. Named, never discovered, and by
the same person who named the file set: a reconciliation that went looking for its own candidates
chose part of its own scope after all.

Where a node also drifted on the specification side, the judgment below reads it as it now stands,
and the record says so in `notes`. Both sides having moved is not a special case; it is two facts,
and the bind restamps both.

### 3. Judge

Spawn one `siegard:specification-conformance-reviewer` subagent per file the manifest holds nodes for,
together rather than one after another — in batches no larger than the harness runs at once,
where it caps concurrent delegations; a launch the harness refused ran no judge and is dispatched
again in the next batch, never counted or answered for — its judgment lives at
`${CLAUDE_PLUGIN_ROOT}/agents/specification-conformance-reviewer.md`. Each delegation is passed:
a file set of exactly its one file — the resolved path its pack header names, the spelling a
finding echoes being the header's own; as the node set, its node pack's path from the manifest —
the pack is the set, whole, each node's text with its source named; as candidates, the path to
the workspace's candidate index — together with the identities of any node the human named as
written since the bind — which it may consult where its file states a fact its own nodes do not
settle: a fact one file states can be governed by a node another file carries, and a judge who
cannot open that node reports an absence where the true finding is a misattribution; the
specification root; and the path to
`${CLAUDE_PLUGIN_ROOT}/schemas/conformance-return.json`, which is both where a finding's own
shape lives and the contract the whole return is held to by the fold below. One contract, handed
once: a second one pasted beside it would be a shape the fold never applies.

**On an audit, no candidate tier is passed, and the staging writes none.** The manifest carries an
empty `candidates` and the workspace holds no index, so there is nothing to hand over and nothing
to compose. A candidate exists for one purpose — letting a judge say that a fact its own nodes do
not hold is held by a node another file carries — and an audit asks a narrower question than the
one that serves: does this file still carry this node's fact, so that this claim stands? Both
answers a candidate separates end at the same act on that pair, because the claim is not carried
either way and the release is what the report hands over; binding the node that does hold the fact
is a delivery's act, which no reconciliation performs. What the tier would buy on an audit is a
better sentence about a pair whose outcome it cannot change, paid for with every candidate node a
judge opens to write it. The ordinary route keeps the tier for the opposite reason: there a
misattribution reported as a gap is a false finding, a false finding blocks its node, and undoing
one costs a fresh delegation over the whole file.

**Two rules about the paths in those prompts, and both are about what a prompt costs.**

- **The candidate index goes as its path and never as its contents.** One index serves the whole
  batch — every node the staging assigned, with the files each is bound to — and a judge opens it
  on demand, in its own context, where the reading is paid once by whoever needs it. Writing that
  list into a prompt instead pays for it again per delegation, in this context, where nothing
  reuses it: a batch's index is the same text every time, so N prompts carrying it inline is that
  text written N times to say what one path already says. The same holds for the node pack: its
  path, never its text.
- **Every path a delegation receives is absolute and already resolved.** Never a path relative to
  a root the delegation is told to prepend, and never a root plus an instruction to compose the
  rest — a target source root whose own internal layout is not obvious (a nested `src/`, a
  monorepo alias, a generated directory) turns that composition into the delegation's guess, and a
  guess that misses returns a refusal instead of a judgment. The refusal costs the whole
  delegation and buys nothing: it is the one failure that a resolved path makes impossible.

**A judgment answers two questions, and `kind` is which one a finding answers.** Whether the
source still states what a node holds is one; whether it states a fact **no** node holds is the
other, and a record that folded both into one boolean per node made the second land on whichever
node shared the file with it. `contradicts` is the pair's: a node governs the fact and the source
disagrees with it or became a second home for it, so the node does not bind and a rebind is what
closes it. `unstated` is the specification's: no node holds the fact at all, the route is
`/analyse`, **no rebind can ever close it**, and so it blocks no binding a node's own reading
cleared. The fold routes on the word and lands the second class under the record's own `unstated`,
keyed by file rather than by node — a fact no node holds has no node to be about. A third word
answers a third question: `restates` is a comment or a docstring saying a node's fact while
code holds it too, in that file or in another — never text the running system emits, such as a
tool description or an error message, which is behavior. The pair conforms and binds where the
code is;
the fold lands the finding under the record's own `restates`, and what it owes is the text's
removal, then this route over the file. `trace.py --owed` reports all three apart from what a
bind is owed, and the report hands each its route.

**Save each return verbatim the moment it arrives**, at
`siegard-reconcile/<slug>.returns/<the file's path with every '/' as '__'>.yaml` — a copy and
nothing else. Never reshape one, never trim one, never repair one: the returns are the evidence
the record is folded from and they outlive this session, and a return adjusted by the hand that
saved it carries a judgment the delegation never made. The copy is the script's, from the
delegation's transcript — the output file the harness names for the spawned agent:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/trace.py --save-return <target-root> <workspace> <file> <transcript>
```

`<file>` is the staged file's path as the manifest lists it, or the node identity of a
certification. Never retype a return from the notification that relays it: that text is
re-rendered for display, and an escaped character it carries parses as part of a scalar. A
refusal says why: a delegation whose transcript ends in a tool call has not answered yet and is
waited for, and only one whose transcript cannot be read is saved by hand, under the same
discipline.

**A certification is the coverage auditor's, and it is one more delegation per node.** For each
entry the manifest holds under `certify`, spawn a `siegard:coverage-auditor` subagent — its judgment
lives at `${CLAUDE_PLUGIN_ROOT}/agents/coverage-auditor.md` — handing it the certification
pack's path and the target source root, and nothing else: the pack names the node, the proof and
the contract. Its rule is the whole test of a test — the named tests would fail if the node's
fact stopped holding — and it is the same rule it applies to a task's criterion in a review. Save
its return verbatim at `siegard-reconcile/<slug>.returns/certify__<node with every '/' as
'__'>.yaml`, under the same discipline as every other return. The conformance judge for the
node's file runs as well, unchanged: certification rides a reading that cleared the node, and the
fold writes it on no other. Where the auditor answers short of `covered`, its return also says
whether the **remainder** — what the offered tests leave unexercised — is one a test could
assert, with the assertion named, or one no finite test closes; the fold carries that onto the
node's entry, and `trace.py --owed` lists the testable ones as the work a test closes.

**Verbatim is literal, and the fold enforces it against four keys.** `conformance-return.json`
admits `findings`, `read`, `looked_past` and `candidates_opened`, and nothing else at any depth.
A fifth key — a `notes` holding a delegation's closing paragraph, a summary line written for a
human, anything the four do not have a home for — refuses that return at `--fold`, and the fold
refuses whole: every saved return is re-read and re-written before it runs at all, which is the
whole batch's transcription paid twice for one field nobody needed. What a delegation says outside
those keys belongs in your report to the human, never in the file the fold reads. Where a return
arrives shaped for a reader rather than for the contract, the fix is still a copy: save what came
back, and say the rest in the report.

One judge per file rather than one over the set, because a judgment over the set saturates: a
single context holding every node and every file at once answers hundreds of node-file pairs in
one reading and claims clean over pairs it never weighed. A judge holding one file and its own
nodes reads less and misses less. No delegation reads another's
return, and the pass is the union of what they return: a finding keeps the file its judge read,
and a node is cleared exactly where no delegation that read one of its files found against it.

**A delegation answers once.** Where a return is unusable — a field missing, a node it never
accounted for — the prompt was wrong, and the correction is a fresh delegation with the prompt
fixed, never a follow-up question to the one that already answered. A resumed judge holds its first
reading and the new question at once, and what comes back is neither its first answer nor an
independent second one. So two divergent answers from one delegation are
not a union to fold — union is what holds *between* delegations, each of which read something the
others did not. They void each other, the file is judged again from a clean context, and `notes`
says that happened. A score folded out of a judge that answered twice is a floor, not a measurement,
and a record cannot say which it is.

One agent serves both routes, deliberately: what belongs in the file set and the node set is the
caller's rule and never its own — in a review that rule is the change, with the trace's nodes and
the plan's read together over each file it wrote; here it is the trace alone, one file at a time. Duplicating the judgment into a second agent that reads it differently
is how two passes end up disagreeing about what conformance means. Two things this route needs are
in the agent's own contract rather than in this sentence: the candidate tier it may open to
attribute a fact, and the per-node `read` it returns — `held_at` and its quoted evidence — which
is what a cleared node's `how` is written from. Never write a `how` from your own reading of the
file; that is the judgment this step delegated.

**Do not read the files yourself and decide.** The premise the human handed you is that the source
is correct; the question this step answers is a different one — whether the specification still
states what the source now says — and answering it from the same context that accepted the premise
is answering it from the premise.

Delegating means spawning the subagents by their plugin-scoped names — `siegard:<agent-name>` —
never the bare form, which a consumer's own `.claude/agents/` can shadow. Only where the session
cannot spawn subagents, read the agent's file under the plugin root's
`agents/` directory and apply its discipline in place, file by file in the same shape — the file
stays the single home of that judgment — and the report must say the pass ran inline.

**And not even then, where this session wrote any node the judgment will read** — its own set or
its candidates. A context that authored a node and then reads the source against it is grading its
own writing, which is the whole of what delegating this judgment prevents; run inline, it produces a
record saying `conforms` in the voice of a judgment nobody independent made, and that record is what
a bind rests on for as long as the code lives. The stop is to report and wait. Say why the spawn
failed, too: a spend limit or a rate limit passes, and what the human does then is run it again
rather than accept less.

### 3b. Capture the run the mechanical tier is answered by

Where the staging separated nothing under `mechanical`, skip this step and say so in the report.

Where it did, run the step(s) it named, once, into the returns directory beside the record —
which is where the reconciliation's evidence already lives and outlives the workspace:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/run.py siegard-reconcile/<slug>.returns \
    --run <slug> --cwd <target-source-root> --timeout-seconds <the registry's bound> \
    --step <name>="<the registry's command>" [--step ...]
```

Every string is the project's. The step names come from the staging; each command and its bound
come from the registry's own `commands[]`, read from what `deliver.py --standard` printed — never
composed here, never inferred from what the tree looks like. The staging prints this invocation
with the names filled in; the commands are yours to paste from the registry.

**A red step is a result, not a stop.** The fold reads the run per step and writes what it says:
a step that passed clears its nodes, a step that failed binds nothing and the finding routes like
any other. Do not re-run to get a green, and do not repair the tree and run again under the same
name — `bin/run.py` refuses a name it already holds, and a second attempt is a second name, which
is what keeps both readable.

### 4. Fold

Write the premise — the one part of the record that is the human's and no fold can compose. A
small YAML file in the workspace, carrying `title`, `summary` (what changed and why the human
states it is correct, as theirs — never restated as a finding of yours), `target`, and one
`files` entry per named file with its `change` line: what the file now does differently, not what
was typed into it. Then:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/trace.py --fold <target-source-root> <workspace> \
    <the premise> siegard-reconcile/<slug>.md \
    [--run siegard-reconcile/<slug>.returns/run/<slug>]
```

`--run` is owed exactly where the staging separated a mechanical tier, and refused where it did
not — a run nothing reads is evidence for a question nobody asked. The fold refuses it over
another tree, missing a step the tier names, or captured over content that has moved since the
staging: the run proved the tree as it stood, and binding what stands now on the strength of it
would stamp a claim over bytes the run never saw. That last refusal is the same stop the omission
guard has at bind time, and the route is the same — a fresh invocation under a new slug.

The fold writes the record, whatever the judgment returned — a reconciliation that stopped is the
record worth keeping most, because without it the next invocation rediscovers the same divergence
from scratch and calls it new. Every rule it applies is mechanical and lives in the fold and its
tests, not here: which answer a node folds to when more than one judge read it, where a finding
naming a node lands, what a finding naming none holds, which nodes are marked `collateral`, and
how every named file is accounted for. **Never apply those rules by hand, and never edit what the
fold wrote** — a record adjusted after the fold carries a judgment the returns behind it do not,
and the returns are what a later reader checks it against.

Where the fold refuses, read the refusal as two kinds. A refusal naming a delegation — a return
missing, a node unanswered, a shape the contract does not hold — is a fresh delegation with the
prompt fixed, run again from the judge step, never a follow-up question to the one that already
answered and never a hand-edit of what it returned. A refusal about the premise is yours to fix
here. Then hold the record to its contract:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/trace.py --reconciliation <the record>
```

Anything but a clean pass is a stop, reported verbatim: the fold validates what it writes, so a
record this refuses is a defect in the staging, the premise or the fold itself, not in any
judgment.

### 5. Bind

**Whatever the judgment cleared, and never anything else:**

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/trace.py --bind-record <target-source-root> <specification-root> <the record> --workspace <workspace>
```

The record is read the same way an implementation record is, and the whole of it is refused before
anything is written — refused over form, meaning a node this specification does not hold or a file
that is not there, which is defect in what you wrote and never the judgment's answer. `--workspace`
names the staging's own: the bind refuses a file or a node that moved since the staging read it,
because it stamps what the judges read and the workspace is where the staging recorded what that
was. What lands is
the union: a file an earlier bind put on a node and this record does not name stays bound, because
two things landing one node in two files is not one of them undoing the other's work.

**This skill never passes `--replace`.** Where the human says a fact moved out of a file rather than
into an additional one, the report hands that invocation ready to paste and stops: `--replace`
substitutes the whole entry, its receipt of what stopped being claimed is the only signal there is,
and a receipt nobody was there to read is the silent loss the union default exists to end.

**Where a node carries a finding, that node is not bound, and the nodes that cleared still are.**
The join is already structural and needs nothing from you: a node the judgment refused carries no
`encoded_at`, and this form reads only nodes that do — so the invocation above writes exactly the
cleared set however anyone runs it. Run it whether the judgment cleared everything or not, and run
it once.

The bind also recomputes every `pairs_omitted` claim at this moment, both halves — the binding
still computes at the file's content, and the corpus holds nothing open against the pair — and a
claim that stopped holding refuses the record whole: a file that moved between staging and
binding broke the committed-tree premise this whole invocation rests on, and the route is a fresh
invocation under a new slug, never a bind around the pair.

What that is not is a claim that the set is reconciled. A cleared node's binding rests on the
judgment that cleared it and on nothing else in the record; a node with a finding against it stays
exactly as it stood.

**What `--check` says about that node afterwards is a different question, and often the answer is
nothing.** Drift is computed from the bindings: where the pair was bound before, its old digest
still reports and the drift report is honest about it; where it was not — a node the judgment
opened as a candidate, bound to a sibling file and not to this one — there is no digest to
disagree with, and there never will be. A later bind that stamps the very content the finding was
read in removes the only digest that did. `trace.py --owed <target-source-root>`
is what reads the records back and says which of the three states each finding is in; the count
`--check` reports is not that number. Holding the cleared bindings back would
not have made that clearer — it would have left forty findings looking equally unexamined instead of
two — and it would have thrown away every reading that succeeded, so the next invocation re-judges
files whose text nobody touched.

**Read the bind's receipt and carry it into the report.** It names the nodes it did not write,
which is the one place the partial shape of the act is stated at the moment it happens. It names
what it certified, too — each node now decided by a test, with the step and the proof it pinned —
and any certification an earlier bind held that this one released because the proof's text
changed. The fold already said which certifications did not hold and why, in the record's
`notes`; the bind says which ones landed.

### 6. Report

Open as «A handoff opens with what needs the person, and explains after» (SPEC-006 R1)
states; what follows is the report that opening sits above.

Say, in this order and in prose: the file set as given; what the staging held for each file, by
state — judged, nothing left to judge, unbound — and how many pairs it omitted as current and
unowed; the shape the judgment ran in — how many delegations, one per file; what the judgment
answered per node, with its evidence; which pairs a run answered instead of a judge, with the
step and the run's own outcome per step; where the record, the returns and the run were written;
what was bound and what was not; which nodes are decided by a test from here and which
certifications did not hold, in the auditor's own words — and for each of those whether the
remainder is testable, with the assertion the auditor named beside it and the file's own count of
bindings a reading decides, because a node a test closes frees a judge only once every binding on
its file is decided by a step or a test — and the route that closes them, as one invocation: a
proof increment, `/deliver-scope` with an ask naming the proof increment and, per testable
remainder, the node, the assertion verbatim, this record's path and the files the node is bound
to, all read from the record you just folded, under a new slug. `/plan-work` plans one task per
fact, `/implement-task` writes the proof alone, and the review that reads it certifies the node —
«A finite test is preferred to a reading, and to a registry step's decision, wherever one exists»
(SPEC-004 R10), so every testable remainder is handed on, never only the ones that look cheap.
Which to take is the human's: they paste the invocation whole, or trimmed to the facts they want.
And the next invocation where there is one.

Where a node the judgment did not clear carries `collateral`, say so apart from the contested
ones: nothing was found against that node's own substance — it shares a file with a finding that
named no node, and the conservative default holds every node of that file. Its route rides the
finding's own: route the finding, and the re-invocation that follows re-judges the file and
re-clears the node with it. A reader who cannot tell collateral from contested reads four open
questions where there is one.

Where the judgment cleared everything, there is no next invocation. The trace now describes the tree
as it stands, and `trace.py --check` over the target is what a reader confirms that with.

Where it cleared part of the set, say both halves and keep them apart: the nodes now bound, and the
nodes still owed exactly as the bind's receipt names them. Two confirmations, and naming only the
first is what leaves a reader believing a partial reconciliation was a whole one. `trace.py --check`
over the target reports the drift that remains — a reader who sees two findings where the report
opened with forty is reading the progress, not a clean tree. `trace.py --owed` over the same target
reports what this judgment found and no bind could close, which is the half `--check` cannot see:
a node bound to no file here has no digest to drift, so its finding lives in the record alone.

**Then say what the next invocation's file set is, and make it the remainder.** It is the files
whose nodes are still owed — never the whole set again. The nodes that cleared are bound, their
files are committed and nothing here rewrites source, so re-judging them buys a second reading of
text that did not move and pays one delegation per file for it. Two things go in with the remainder,
and both come from `--check` rather than from your memory of this run: any file the run about to
follow leaves reporting `moved`, because an `/analyse` that shifts a node re-opens every file bound
to it including one that cleared here, and any file whose nodes the remainder shares — the binding
form refuses a record that names a file and answers for only some of the nodes bound to it. Name
them; the file set is still the human's to state. A bound file `--check` reports as no longer
existing goes in no file set: this skill reads files, and there is nothing to read — `trace.py
--release <target-source-root> <path>` is what answers it, and the report names that invocation
beside the remainder.

Where it did not, there are two readings and **you choose neither.** The source may be right and the
specification behind it, or the node may be right and the source wrong — that is a person's to
settle, and a reviewer that settles it is a decision wearing a finding's clothes. Hand both, and say
which finding each one answers: two readings of one piece of evidence are a door nobody
recommends — «Each is the person's, and a handoff hands its doors and names none» (SPEC-006 R3).

The first, where the fact the source now states belongs in the specification — the `/analyse`
invocation ready to paste, naming the material (the finding's evidence, the file it was read in, and
the nodes located above) and the project root. After it runs, this skill is invoked again over the
remainder under a new slug: the node has moved, the judgment reads it as it now stands, and the bind
stamps both sides.

The second, where the node is right and the behavior is not — the `/plan-work` invocation ready to
paste for a corrective increment, naming the scope (the one wrong behavior, as the finding states
it), the project root, the target, and the initiative's slug. That route ends in a delivery, which
binds on its own and leaves this reconciliation with nothing to do.

The third, where the node and the behavior agree and what the finding names is the file's own
prose — a comment breaking the consumer rules' comment rule. Neither door above fits it: there is
no fact to decide into the specification and no behavior to correct, and routing it through either
prices a line of prose like a defect. The consumer rules' comment route is the answer — the human
removes the prose, never refreshes it, and this skill invoked again over that file under a new slug
is what re-judges and rebinds. The prose removed is every comment the file carries, directives the
toolchain reads excepted, never only the ones cited: a judge names what it read, it does not list
every comment, so a file stripped of the cited ones hands the next judge the rest. Hand that
invocation ready to paste, and say which findings it answers. Over these findings the comment
route is recommended, as «A recommendation names the door, the criterion, the deciding fact and
the reversing fact» (SPEC-006 R2) states: the criterion is `rule violated`, since either door
above would route prose as a fact or a behavior; the deciding fact is the judge's return naming
prose and no contradicted node, quoted; the reversing fact is a return naming a fact or a
behavior, which puts the finding back between the two readings above.

The fourth, where the fold placed a finding in the record's `notes` because it names a node no
file of this set is bound to — the note ends "owed a route of its own". It blocked nothing here,
and `trace.py --owed` reads a record's nodes and its `unstated`, never its notes, so this report
is the one place the finding is handed on: name it apart, with the node, the file and the
evidence, and hand it the same two doors as a finding on a node — `/analyse` where the fact
belongs in the specification, `/plan-work` where the node is right and the behavior is not —
or, where the finding says the file holds the node's fact and nothing binds it, this skill
invoked again over that file under a new slug, which is what hands a judge that node's text.
Where the note says so, that door is recommended as R2 states: the criterion is `already done`,
since the fact is already in the file and only the binding is owed; the deciding fact is the note,
quoted; the reversing fact is a note saying the file contradicts the node, which leaves the two
readings and recommends neither.
A finding left in the notes and not in the report is a finding nobody will act on.

## Adoption

The same order, with four differences, each held by the scripts rather than by this prose.

- **Stage with `--adopt`, over the ledger.** Where `/analyse` wrote a ledger beside survey or
  intent material — its handoff names it — pass it, and the files the human keeps out with
  `--outside`:

  ```
  python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/trace.py --stage <target-source-root> <specification-root> \
      <slug> <workspace> --adopt --ledger <ledger.md> [<each named path>] \
      [--outside <path> ...] [--certify <certifications file>]
  ```

  The file set is the material's areas — on intent material, the files it governs, never its
  tests — or the named subset of them; each file's judge is handed
  the candidates the ledger landed that file's own facts in — «Every fact line of the material
  lands in a node or is left out with a stated reason» (SPEC-005 R8), so the pack is the nodes
  that file's facts reached and not the whole increment. A file no fact names is handed no judge
  and stays unbound. The candidate index still lists every candidate with the files it is read
  on, for a fact a judge meets that its own pack does not settle. Where no ledger exists, name
  every candidate with `--node` instead, and every file's judge reads them all. No trace is
  needed either way; a file the trace already binds keeps its own node set beside the
  candidates. No candidate is omitted and none is answered by a run, because its reading is what
  decides whether it is bound at all. A file the target declares as a test is refused in the
  set: a test is never adopted source, and the refusal hands the `--certify` entry it takes
  instead — a test offered as a node's proof rides the same staging.
- **Judge and fold as always.** The premise's `summary` says the source is adopted as it stands
  and did not change. The fold writes `adopted`, and «An adopted node binds the files whose
  judgment holds its fact and no others» (SPEC-005 R4): each cleared candidate's `encoded_at` is
  the files whose judge read its fact there. A candidate every judge answered `nowhere`, with
  nothing found against it, is listed under `unheld` and claims no file.
- **Bind with `--bind-record --workspace`,** which writes the trace if this is the target's first.
- **Report** what an adoption adds: every candidate under `unheld` — a node the source does not
  carry, or one the files outside this set carry: the analysis's to revisit, or the adoption of
  those files; every
  `contradicts` against a candidate — a reading of the source the node misstates, the same route;
  every `unstated` fact — the source carries it and no node does, the same route again; every
  `restates` — text the comment route removes before this route runs over the file again; and the
  target's standing as `trace.py --untraced` prints it, because «Adoption is complete when no file
  is unsurveyed and no node is unreached» (SPEC-005 R7) and this is the file half of that count.

## What this never does

- **It never writes source and never writes a specification node.** Both have entry points, and a
  reconciliation that repaired what it found would be a third one nobody validated.
- **It never decides that a file is correct.** The human asserts that; this skill records the
  assertion as theirs and asks a different question.
- **It never certifies a test itself.** Which test a human offers is theirs; whether it would
  fail if the fact stopped holding is the auditor's; the fold writes `decided_by: test` from the
  auditor's `covered` and from nothing else. A node's type says nothing about it either way.
- **It never decides that a node is testable.** Whether the remainder a refused certification
  leaves is one a test could assert is the auditor's, read from the fact as the node states it;
  the record carries it, and what closes it is a test the human writes and offers again. A node
  whose type looks testable and whose fact is not is exactly the case the auditor is there for.
- **It is not a review.** It reads one file set against the nodes the trace already links to it. It
  says nothing about coverage, about the project's standard, or about whether anything was proven —
  those are `/review-change`'s, over a delivery, and a reconciliation that reported them would be
  reviewing a change nobody delivered.
