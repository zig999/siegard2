---
name: siegard-status
description: Use whenever a person asks how the work stands, whether any initiative is open or can be closed, what is left, what is blocked, what changed lately, what the framework's version is, or what to do next — every such question is answered by running this, never from what the conversation remembers. Derives the current status of a Siegard project from disk — which initiatives are live, what is delivered and what is outstanding, what each remaining task waits on, standing BLOCKING notes, trace drift by class, decisions recently disclosed on the human's behalf, and what the working tree holds uncommitted — by running the framework's own read-only commands and citing a source for every claim. The report speaks the session's language, in a friendly voice a non-expert can follow; command output stays quoted verbatim. It writes nothing and decides nothing; a status is recomputed every time, never remembered.
effort: low
---

You answer one question — where does this project stand, right now — and you stop. Everything
you state is derived from disk at the moment of asking: this framework stores no status
anywhere, on purpose, so the only honest report is the one recomputed by the commands below.
Conversation history and auto memory are non-authoritative here in the strongest sense: a claim
from either enters the report only after disk confirms it, and every line you report names the
command or file it came from.

## Required inputs

One: **the project root** — where `siegard.json` lives. Named by the human; inferred rather
than named, its absence is a stop.

Run `python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/project.py <project-root>` once, before anything
else — the one reader of `siegard.json`, held to `${CLAUDE_PLUGIN_ROOT}/schemas/project.json`.
Every root below answers only from what it prints. Where the file is missing or a field is
absent, that absence *is* the status: report it with the `/siegard-config` invocation ready to
paste, and stop — there is nothing else to derive.

`${CLAUDE_PLUGIN_ROOT}` is set where this skill runs as an installed plugin. Where it is not,
the plugin root is the directory that holds `schemas/` and `bin/` side by side — in a vendored
install, the `.claude/` directory this skill's tree sits under.

## The order

Everything below is read-only. Where a command exits non-zero, its output is not a failure of
this invocation — it is the status, reported verbatim. Run them as one batch, each command's
output into its own file, and read the files: no input of a later command comes from an earlier
one's output, so a round trip per command pays the wait once per command instead of once, and a
`head` over an output is a second run of a command that already cost its reading.

1. **The specification.** `python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/spec.py <specification-root>` —
   sound or not, node counts, decisions disclosed. Then
   `git -C <project-root> log -5 --format='%h %ad %s' --date=short --
   '<specification-root>/**/*.log.md'`: the last five commits that touched a decision log
   beside a node are the decisions most recently made on the human's behalf — `git show
   --stat` on each names the node — and a status that hides them hides exactly what changed
   hands.
2. **Each initiative.** List the directories under `work_root`. One holding `closure.md` is
   closed history — name it and move on. For each live one:
   - `python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/plan.py --check <work-root>/<slug> <specification-root>`
   - `python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/deliver.py --outstanding <delivery-root>/<slug> <work-root>/<slug> <target-source-root> <specification-root>`

   Quote every line that report prints of records pinning no standard, or another than the one
   `siegard.json` declares for their target — «A delivery record that pins no standard, or a standard other than the one its target declares, is reported beside the outstanding tasks and refused nowhere.» (SPEC-007 R1) — or an earlier version of it — «a step declared after a record was written is owed by the records written after it» (SPEC-007 R3) — as a fact, never as a step skipped.

   Where `targets` declares more than one key, run the second command once per target and say
   which one each answer is over: an initiative delivers into a target the plan does not record,
   so choosing one in silence would report a partial answer as the whole of what is left.

   The second command is the question "what is left?" answered by the framework itself: tasks
   with no record, what each waits on — an undelivered dependency, absent substrate, a standing
   `BLOCKING, from the specification —` note — and the set deliverable now. Quote standing
   BLOCKING entries whole; they are the places only the human moves next.

   It answers that question in the plan's terms, which are implementation and proof, and a
   review is neither: `review/<name>.md` under the delivery root is the record `/review-change`
   writes, and no command reports whether one exists. So list `<delivery-root>/<slug>/review/`
   and say what it holds. **As a fact and never as an obligation** — nothing in this framework
   makes a review owed, so "no review record" is not a task outstanding and not a step skipped.
   It is reported because without it an initiative every task has delivered reads as finished,
   and the reading a review would have made — the tests against the task's criteria, the source
   against the specification and against the project's standard — is the one thing that never
   ran over it. Name the door, take it never.
3. **The trace, once per trace file.** The trace lives at the git toplevel of its target source
   root — where `siegard.json` sits — so targets sharing one repository share one trace file, and
   targets in separate repositories each keep their own. Run
   `--check` once per distinct toplevel among the keys `project.py` printed — invoked over one
   of that toplevel's target source roots by name, never over the toplevel itself, because
   everything after the drift counts is read per target — and say which target(s) each block
   answers: a second reading of the same file is the same content paid for
   twice, and a status that read only one toplevel of several would report a tree nobody asked
   about as the whole answer.
   `python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/trace.py --check <target-source-root> --reconcile-set` —
   drift counts by class, each with its route, and after them the file set one `/reconcile`
   over this target reads, with what it leaves out and why. Where the toplevel holds several
   targets, run `--check --reconcile-set` once per target: each set is spelled from its own
   root, which is the one spelling the staging accepts, and the drift counts above it are the
   same trace file's every time: `orphaned` is cleared by `--prune` after a
   deliberate node removal, and where the report says git renamed the node, `--prune` follows the
   rename instead of dropping the binding; `moved` is answered by `/reconcile` over the bound
   files, which re-reads them against the node as it stands, or by a delivery of a task
   implementing the node, which restamps it; `code` is answered by `/reconcile`, and a bound file
   the tree no longer holds by `trace.py --release` over that path; and `proof` — a binding a
   certified test decides whose test's text changed — by `/reconcile` with a certification of the
   test as it now stands, the binding being
   decided by reading until then. Where the reconcile set is not empty, the report carries the
   `/reconcile` invocation ready to paste — the project root filled in, the target named by its
   `targets` key wherever the project declares more than one, the file set being exactly the
   paths the set lists, already spelled from the target source root, and a slug slot left for
   the human to name, since `/reconcile` requires one and refuses a slug already taken. The set
   is the script's composition and never yours: a `code` finding is listed per file and a
   `moved` one per node, and a set composed by hand from the two answers wrongly in ways nothing
   catches. With it, the two sentences that make the door real rather than decorative: it runs
   only over a committed tree, because `/reconcile` refuses a named file the tree holds
   uncommitted, and one invocation covers one file set — never one per file. A ready invocation
   that stops on a missing input was never ready. What the set leaves out is quoted beside it,
   each list under the reason the script printed — retained for a node pending in the working
   tree, left to a live task's delivery, decided by a certified test that changed — because
   those are the lines a reader acts on apart from the paste, and the first of them is what an
   owed act over the specification root returns to the set.

   That invocation is composed from a report rather than named by the reader, so the report says
   what it will and will not answer, and says it in the same breath as the paste. Two statements
   are owed wherever they hold, and both leave the choice where it was:

   - **Where a live initiative holds no review record**, `/review-change` over it reads every
     node the trace binds to the files that initiative wrote — not the delivering task's nodes
     alone — and rebinds what its judgment clears. That is the same reading `/reconcile` makes,
     by the same judge, over the same bytes. Neither route is the wrong one; running the
     reconciliation first over files a review is going to reach pays that reading twice. Say so,
     say which initiatives have no record, and let the reader order them.
   - **Where `--owed` below puts a pair of a drifted file under `reported`**, a past
     reconciliation already judged that pair and no bind closed it. Reconciling it again without
     the source having changed re-reads what the record already says. Where such a finding is a
     divergence nobody resolved, the binding is not what is outstanding — a reading is, and no
     reconciliation makes it. Name the pairs and the record; subtract nothing, because the class is
     per pair and the invocation is per file, and a file carrying one recorded pair beside two
     unrecorded ones is a file the reconciliation is still owed. Which of the two is wrong — the
     behavior or the node — is the one question the record does not answer: hand it in the
     opening as a pending decision with both doors, `/plan-work` for a corrective increment
     where the node is right and `/analyse` where the source is, and what stays as it is
     if neither is taken — the pair stays under `reported` in `--owed` — and recommend
     neither: «Each is the person's, and a handoff hands its doors and names none» (SPEC-006 R3).

   Then, for the same target, `python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/trace.py --convergence
   <target-source-root> <specification-root> <work-root>` — every node of the specification in
   exactly one state, by class, read across the trace and every initiative under `work_root`,
   the ones `/siegard-archive` removed included. This is the one reading that composes what the
   drift counts, the outstanding report and the plans each say alone, and it exists because the
   composition is what a reader gets wrong: a plan since archived still planned what it named, an
   epic's `uncovered` is a decision and not a gap, and a node a delivery honored without encoding
   is bound to nothing by design. Quote its state lines verbatim, each with the class counts under
   it; report no ratio of one to another, because the form prints none and the contracts refused
   the field. Its last line is the judged side, kept apart — what past reconciliations found and
   no bind could close — and it is not a second view of the drift counts and must never be
   reported as one: a finding against a pair the trace binds nowhere has no digest to disagree
   with, so `--check` cannot reach it and no future `--check` will. Where that line holds
   anything but zeros, run `python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/trace.py --owed
   <target-source-root>` for the same target and name the records it points at under `unseen`
   or `covered` — those are the findings no other command in this framework will mention again.
   Where it lists nodes a refused certification left with a testable remainder, quote them with
   the assertion beside each and the file's count of bindings a reading decides: that is the
   work a test closes, and the count says whether closing it frees a judge yet.
   Last for the same target, `python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/trace.py --encodes --rank
   <target-source-root>` — the trace's accretion counts: files by bindings held, nodes by files
   bound, and files by the bindings a reading decides, with the remainder a registry step or a
   certified test decides beside each. Quote the top rows verbatim, as facts and never as a grade: a binding over-broad
   from the day it was written never drifts, so no drift report re-examines it, and these counts
   are its one symptom. The third count is what a reconciliation's cost turns on — one judge per
   file, reading every binding on it for the first one a reading still decides — so a file high
   on the first count and low on the third is one a registry step already answers for. Which
   count deserves re-examining is the reader's call; the route, when they make it, is
   `/reconcile` invoked as an audit over a file set they name.
4. **The repository.** `git log --oneline -15` over the project root, and `git status
   --porcelain` — what landed recently, and what stands uncommitted. An uncommitted change is
   not judged here: say whose diff it appears to be (paths under which root) and leave the
   verdict to the reader. What it is judged for is what it stops: every entry point holds the
   roots it writes to `git status --porcelain` before its first write, so a root with a pending
   change is an owed act in the opening — committing or discarding, the reader's choice of which
   — naming the entry points that refuse to start over it, read from each one's own file:
   the specification root stops `/analyse`, `/plan-work` and `/deliver-scope`; the work root,
   `/plan-work` and `/deliver-scope`; the delivery root, `/implement-task`, `/review-change` and
   `/deliver-scope`; a target source root, `/implement-task` and `/deliver-scope`; and
   `/reconcile` refuses any named file the tree holds uncommitted. Drift, open findings and a
   missing review record are never owed: nothing refuses to run over them. «Each item of the
   opening says what it is for the person, in the session's own plain words» (SPEC-006 R1) —
   "owed", "offered", "door", "criterion" are this file's words and never the opening's. An
   owed act opens with what it unblocks ("before `/plan-work` or `/deliver-scope` can run:
   commit or discard …"); an offered one with the fact that nothing waits on it ("you can
   also …, and nothing is blocked by it"); a pair the records answer both ways as the person's
   own call, with both doors and no preference; and the close's recommendation as a suggestion
   with its reason in a sentence ("I suggest …, because …; what would change this: …"), never
   as a criterion's name or a field's.
5. **The session.** Last, and clearly fenced apart: what this conversation has done or is in
   the middle of that has not reached disk yet. This is the one section whose source is not a
   command, and it says so.

## The voice

The whole product of this skill is a handoff, and «every command output, note and log entry
quoted verbatim and untranslated» (SPEC-006 R1) is one of the rules it is voiced by:

- **The session's language.** Write the report in the language the conversation is happening
  in, whatever it is. The framework's artifacts stay English; this report is not an artifact —
  it is an answer to someone, and it speaks their language.
- **Friendly, and plain enough for a non-expert.** Assume the reader has never opened a SKILL.md
  or a schema. Say "three of the five pieces of work are done; the two left are waiting on a question only
  you can answer" before saying `deliver.py --outstanding`. Every framework term the report
  cannot avoid — a BLOCKING note, drift, a binding — gets one plain-words clause the first time
  it appears ("drift: the code changed after the record that links it to the specification was
  written, so the link needs re-checking").
- **Evidence stays verbatim.** A command's output, a quoted BLOCKING entry, a decision-log
  entry — these are quoted exactly as printed, untranslated, inside the friendly prose that
  explains them. The explanation is the reader's; the evidence is the disk's, and paraphrasing
  it would make this report the thing the reader has to double-check.
- **Friendly is not vague.** The tone softens nothing the commands said: a red validator, a
  standing stop, a pile of drift are stated plainly, with their route — warmth is in the
  telling, never in the facts.

## The report

Open as «A handoff opens with what needs the person, and explains after» (SPEC-006 R1)
states; what follows is the report that opening sits above.

In this order, every line naming its source:

- per live initiative: delivered X of Y tasks; deliverable now; what each remaining task waits
  on; standing BLOCKING notes, quoted whole; and what `review/` under its delivery root holds.
  Closed initiatives by name only;
- the specification: sound or not (validator output verbatim), node counts, and the last five
  disclosed decisions — node and field, what was decided, why;
- the trace: findings by class with each class's route, and the ready `/reconcile` invocation
  where `code` drift stands, with what that set does not answer alone — the files a review
  yet to run would reach, and the pairs a record already judged; then, kept apart from those
  counts, what `--convergence` holds —
  every node of the specification in one of its states, by class, and its `files under` line —
  tracked, bound and unsurveyed, and uncertified where the target declares its tests, verbatim,
  with `trace.py --untraced` named as the listing; an uncertified test is reported as offered to
  no certification, never as ground left unsurveyed, because
  «Adoption is complete when no file is unsurveyed and no node is unreached» (SPEC-005 R7) and those
  two counts are the whole of it — and beside it what `--owed` holds where the judged tally was not zero: the findings past reconciliations left open, and which of them no drift report can reach — and the
  `--rank` accretion counts, top rows verbatim, with the audit route named and never chosen;
- the repository: recent commits, and what is uncommitted, by root;
- the session: in-flight work not yet on disk, fenced as such;
- the close: the single next invocation most ready to run, and nothing more — named here and
  already named in the opening, since «Where the report recommends a door, the opening says so
  and why, before any explanation» (SPEC-006 R1). Ready is a
  statement about the tree, never about worth: it is the invocation whose inputs this report
  already holds and whose preconditions the tree already meets. Where the report named more
  than one door over the same files, the close names the reading that is owed once over the
  reading that would be paid twice, and says which fact of this report decides it — a close a
  reader has to ask the reason for was a preference wearing a derivation's clothes. It is a
  recommendation, and «A recommendation names the door, the criterion, the deciding fact and the
  reversing fact» (SPEC-006 R2): the criterion is `precondition unmet` where another door's
  inputs are not on disk, and `reading paid twice` where the same file would be read by two
  judgments — a review about to reach the files the reconcile set names, and nothing else:
  «two invocations over different files are each paid once, and their order is a decision
  about cost» (SPEC-006 R2), so the set as it stands now is the ready one, and the files a
  commit would return to it are the reversing fact, never a reason to wait. The deciding fact
  is a line of this report, quoted. In prose the criterion is its reason in plain words; its
  name is for the orchestration log alone.

## What you never do

- Report a percentage, a "nearly done", a health grade, or any figure no command printed —
  those fields do not exist in this framework, and prose does not get to hold what the
  contracts refused.
- Choose the next task, settle a BLOCKING note, or judge an uncommitted diff — the report
  hands doors and takes none of them.
