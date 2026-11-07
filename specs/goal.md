---
id: "SPEC-008"
title: The goal
status: proposed
contract_version: spec/1
---

# The goal

## Scope

This specification fixes what a goal the person arms over `/deliver-scope` ends on, and how that
end is read. It binds `/deliver-scope`, the script that answers a goal's state, the script and the
skill that compose a goal's condition and arm it, the plugin's `Stop` hook — over a stop no armed
goal answers as well, where it holds the message the session stopped on to SPEC-006's check — the
plugin's `SessionStart` line on the version an armed goal began under, and telemetry's count of
the harness's evaluations and of the stops that check read.

A goal is the harness's own mechanism: a condition the person sets once, that the harness
repeats whenever the session tries to stop, and that a model reading the transcript judges met or
not. This specification decides what the condition says, what decides that it is met, and what
ends a run that cannot be carried further without a person — so that a goal always ends, in one
of two states, each read from disk. It also fixes the framework's own goal: the same condition,
armed by the person through the framework, whose end is that script's answer at the session's
stop rather than a model's reading (R14).

Grounds: every `/goal` session of three consumers (`newcatalog`, `productcatalog`,
`productorder`) between 2026-10-13 and 2026-10-25, Siegard 5.18.0–5.28.1, read from their
transcripts on 2026-10-25 — 15 sessions. The harness recorded 467 evaluations judging the
condition not met and 10 judging it met; six sessions never ended met. Read session by session,
each park had one of four causes: a decision this framework reserves to a person — a finding's
worth, a plan's closure, a standing BLOCKING note, `--bind --replace`, a skill closed to the
model — which the condition demanded and the session could not take; an environment the run could
not have, such as a container engine or production data; a condition the evaluator could never
read as met — an order of steps, "follow the standards", an item that did not exist; and a
session that stopped while its subagents were still running. The harness refuses a condition longer than
4,000 characters, and the conditions written by hand restated rules the skills already hold.

### Decided elsewhere, deliberately not restated here

- What stops a run, and what each stop hands the person — `/deliver-scope`'s own file.
- What a handoff opens with and recommends — `specs/handoff.md` (SPEC-006).
- What authorizes a commit — this repository's `CLAUDE.md` and the session rules; how the
  person's authorizing words are recorded so a resumed route reads them — `specs/carried-words.md`
  (SPEC-010). What a stopped run may still commit is R18's.
- What a handoff written as free text is held to, and the functions that decide it —
  `specs/handoff.md` (SPEC-006 R8); R15 decides only when the `Stop` hook runs them and what it
  records.

## Definitions

- **Goal** — a condition the person sets through the harness, repeated by it whenever the
  session tries to stop, until a model reading the transcript judges it met.
- **Goal condition** — the text of a goal.
- **Armed goal** — a goal condition recorded by `goal.py --arm` for the plugin's `Stop` hook to
  answer, instead of the harness's evaluator.
- **Scope** — what a goal carries: an initiative's whole plan, one epic of a live plan, or a set
  of tasks of a live plan.
- **Stop line** — the last line of a stopped run's orchestration log: `stop: <class> — <fact>`.
- **State A** — the scope is delivered, proven, reviewed and measured; the substrate alone is delivered and owes no proof.
- **State B** — the run stopped where only a person moves it, and what it did is committed and
  measured.

## Requirements

### What a goal ends on

- **R1** — A goal's state is a script's answer, read from disk and git alone: its first line is `state A`, `state B` or `not yet`, and every check it ran follows with its output verbatim.
- **R2** — State A holds when every task of the scope holds an implementation record and a proof record, or an implementation record of the substrate alone, which owes no proof; no implementation record of the scope records a criterion unmet; every task of the scope whose records changed since the goal began is named by a review record committed after them; the delivery and the plan check against their sources; the specification is sound; a measure is committed after the last record and the last review; the tree holds no change but those the condition declared untouched; every commit since the goal began names a skill and the slug, or is a reconciliation that touches only the trace and its own record; none of those commits is on a remote; and the plugin runs the version the goal began under.
- **R3** — State B holds when the initiative's orchestration log, changed since the goal began, ends with a stop line whose class is one of `blocking`, `silence`, `rebind`, `producers`, `gave-up`, `infrastructure`, `project-file`, `pending-change`, `specification`, `contradiction`, `budget`, `stands`, `analyse`, `outside-task`, `already-met`, `unclassified`, and the measure, commit and remote conditions of R2 hold; what the tree still holds is reported as left for the person, because a delivery that stopped leaves its files for a person to read. A plugin whose version changed since the goal began is state B on its own, and so is a commit since the goal began that touches the project file or a standard it declares: the rules the goal ran under are no longer the ones that answer, or what only the person authors changed under a goal. A run that took more judged doors since the goal began than the condition's budget is state B on its own: the state command carries the budget the condition was composed with, and counts the `decided:` lines whose criterion is a rung of SPEC-006 R2's ladder that the orchestration log gained since the goal began; a state command carrying no budget counts none.
- **R11** — A commit since the goal began that names no skill and the slug, and is no reconciliation R2 admits, is state B on its own: the route never rewrites history, so that commit stands until a person reads it, and a goal waiting for it to disappear never ends.
- **R12** — A scope that holds every condition of R2 but one — an implementation record of it records a criterion unmet — is state B, each such criterion named beside its task: the record says the source does not satisfy the criterion, and state A would say the scope is delivered.
- **R13** — The answer names every criterion that a review committed since the goal began, naming a task of the scope, left other than covered, beside that review; the list fails no check, because a criterion no suite reaches is a reading for a person, not a state.

### What a stopped run writes

- **R4** — A run a stop ended closes its orchestration log with one stop line: its class names the stop from the list R3 holds, and its fact is the stopping report's own words. Every stop the orchestrating skill's file names carries exactly one class. A stop no other class names carries `unclassified`, and its fact is the whole of what a person reads. A run that resumes an initiative whose log closes on a stop line appends its lines after it and never removes it: the stop stays the record of the run it ended, and the state is read from the line the resumed run ends on.

  Grounds: the 19 stop lines the sales consumers' orchestration logs held on 2026-10-30, read
  against their own facts. Seven carried `gave-up`, and one of those was a delivery that gave up;
  two were a red whose fix lay in files the task does not write — another task's, or none's — two
  a task whose implementer found every criterion already met by source the task never wrote, and
  two framework defects since corrected. Two more carried `unclassified`, outside the list: a
  build red over a tree the delivery had not changed, and a fix that needed another task's file.
  Under a goal, `gave-up` is a judged choice the door decider may answer by trying the same
  delivery again, which a fix outside the task cannot reward; and a class outside the list left
  the goal without state B, though only a person could move the run.

### What a goal carries

- **R5** — A scope restricted to an epic or a set of tasks carries with it every task of the same plan it depends on that holds no record, transitively, and the deliverable set within a scope is a script's answer.
- **R6** — A goal condition names the route, the authorization, the scope and the invocation that answers its state, and states no rule: the rules are those of the plugin version the invocation pins. The condition is composed by a script that checks, before any goal is armed, what the first step of the route would refuse, and it is armed by the person: through the harness by pasting it after `/goal`, which no skill does for them, or through the framework by `goal.py --arm`, which only `/siegard-goal` runs, and only where the person's invocation of it opens with `--arm`: the skill is closed to the model's invocation, so its arguments are the person's own words, and no other component runs `goal.py --arm`. An invocation that opens with `--arm` over a citation composes and does not arm, because the text the person would arm is the one the script wrote, read before an invocation naming that file arms it. An objective in prose is written to a file under the telemetry root and named in the condition by path and digest, so the condition is one line whatever the objective's length; an objective the person cites — text already in the conversation they point at and adopt — is copied whole into that file, never cut to fit the route, and the evaluator reads the state command rather than the objective. Where the person gives them, the condition states the budget of judged doors the run may take and the findings policy, and a policy names only findings a route corrects: conformance findings of kind `contradicts`, which the corrective increment answers.

### How an armed goal ends

- **R14** — A goal the person arms through the framework ends on the state script's answer at the session's stop, never on a model's reading: `state A` or `state B` ends the goal and lets the session stop, `not yet` blocks the stop with the checks that failed, and a fourth consecutive `not yet` whose whole answer repeats the last ends the goal paused. `goal.py --arm` arms it only where `--compose`'s checks pass and the project holds no armed goal, and only `/siegard-goal` runs it, under R6; it records `siegard/goal.json` under the repository's git directory — never in the tree the state reads — holding `contract` (`goal-armed/1`), `project_root`, `slug`, `target`, `scope`, `since`, `version`, `untouched`, `objective` and `objective_sha256` (null without an objective), `budget`, `condition`, `armed_at`, `session_id` (null until the first stop binds it), `blocks` and `last_state` (the digest of the last `not yet` answer, whole). The plugin's `Stop` hook answers only the session the record is bound to, in a project that declares `siegard.json`, and is silent anywhere else. `state A` or `state B` ends the record and prints one `systemMessage` line carrying the state's first line, the stop line among it under state B; `not yet` prints `{"decision": "block", "reason": …}` whose reason is the state's first line, every failing check with its output verbatim, and the condition repeated; a stop while the session holds background work in flight is allowed and not counted. An ended record — `state A`, `state B`, `paused`, or `disarmed` by `goal.py --disarm` — is appended to `siegard/goals-ended.jsonl` beside it with `ended`, `reason` and `ended_at`. A state the hook cannot compute allows the stop and leaves the goal armed. What the person reads first when the goal ended with nothing delivered is SPEC-006's.

### What a stop no armed goal answers holds

- **R15** — Where no armed goal answers the stop in a project that declares `siegard.json`, the plugin's `Stop` hook reads the event's `last_assistant_message` and, where `bin/handoff.py`'s own reading says it hands a decision, appends one line to `siegard/handoff-checks.jsonl` under the repository's git directory — never in the tree the state reads — holding `at`, `session_id`, `characters`, `hands_decision`, `mode`, `violations` as `handoff.py --check` prints them, `kinds`, `blocked` and `released`. The mode is the environment variable `SIEGARD_HANDOFF_STOP`, which a project declares in the harness's own settings: `measure` is the default and the reading of every value but `enforce`, and under it the hook never blocks; under `enforce` a stop whose message violates is blocked once, `{"decision": "block", "reason": …}` with the violations as the reason, and the next stop of the same session is allowed whatever its message holds and recorded `released`. A stop while the session holds background work in flight is not read, a stop R14 answers is R14's alone — a stop of another session, where the armed goal is bound to one, is read here — and every failure allows the stop and prints nothing.

### What a session starts on

- **R16** — At a session's start in a project that declares `siegard.json` and holds an armed goal, the plugin's `SessionStart` hook prints one line, to the person and to the session, when the plugin version loaded differs from the armed goal's `version`, and nothing when they are equal or either cannot be read; it never blocks. It also prints one line when the armed goal is bound to a session other than the one starting, naming the goal's slug, when it was armed, and that `goal.py --disarm` ends it.

### What a goal answers without a person

- **R8** — Under a goal, a delivery that stopped over a fact no node states is answered by planning's decided-fact route, and a task waiting on a re-bind by planning over its slug, each once per task, before the run resumes; a second time over one task is a stop.
- **R9** — Under a goal whose findings policy names a finding's kind, each such finding of the run's review is answered by one corrective increment over the file it names, delivered and reviewed in the same run, once: what that review finds is reported and never corrected again.

- **R10** — Under a goal whose condition asks to specify a prose objective, the orchestrating entry point invokes `/analyse` once, before the plan, over the objective as the person armed it, and commits the specification root apart. That commit takes the ledger the analysis answered beside the objective with it (SPEC-001 R16). A stop of `/analyse` over material that states no fact, or that names nodes and changes none, is nothing to specify, and the plan follows; every other stop of it ends the run. Each of those two stops is printed as one line of its own, `stop: no-fact — <what the material would have to state>` or `stop: no-change — <the nodes it names>`.

### What is counted

- **R7** — Telemetry counts the goal evaluations the harness recorded in each session of its window, those judging the condition met and those judging it not met.
- **R17** — Telemetry reads `siegard/handoff-checks.jsonl` beside the transcript-derived form of the handoffs and counts, over the lines inside its window, the stops checked, those violating, each violation kind, those blocked and those released, and names the longest message checked by session and instant; a log that does not exist is reported unavailable with its path, never as a count of zero, and a line that does not parse is counted apart.

- **R18** — A run whose orchestration log closes on a stop line commits nothing after it but the measure: the telemetry root, and the log that carries the stop line. A captured run that ended other than `passed`, that git does not hold, and that no record under the initiative's delivery root names, is refused to a commit that reaches that delivery root: a red attempt a record names is the delivery's own evidence, and one no record names is a red nothing answered. Whether a commit breaks either is `bin/door.py --check commit`'s answer, read from the log and the runs as they stand on disk before the commit is made, over the paths the commit names; a commit that names none is read as one of the delivery. Whether the person's words authorize the commit is no file's answer, and the check lists it as not decided.

  Grounds, as the maintainer relayed them on 2026-10-31 and not yet read from a transcript here:
  a session committed a delivery whose orchestration log said the suite was red and that nothing
  of the delivery was committed. The log's stop line was already the record that the run ended;
  nothing read it before the commit.

## Validation required before acceptance

1. Tests hold `goal.py --state` to R2, R3, R11, R12 and R13 over fixture repositories: one
   answering each state, one per condition of R2 failing alone, a foreign commit answering state
   B, a criterion recorded unmet answering state B with the criterion named, a criterion a
   review left uncovered named under state A, a commit naming the skill and the slug with
   nothing after them and a reconciliation naming its slug alone both on the route, a
   reconciliation touching another reconciliation's record off it, and a run resumed after a
   stop line answering from the line it ends on.
2. A test holds the stop list of `/deliver-scope`'s file to R3's classes, one class per stop.
3. A test holds `deliver.py --outstanding --scope` to R5: an epic, a task set, a dependency
   outside the scope, and an id the plan does not hold.
4. A consumer goal composed under this specification is read for the evaluations telemetry
   counts (R7). The baseline is the grounds' 467 judged not met over 15 goals; a goal composed by
   `goal.py --compose` that the harness judged not met more than once while `--state` answered
   `state A` or `state B` is a defect in what the condition says, never grounds to widen it.
5. Tests hold `goal.py --arm` and `--disarm` to R14 over the fixture repositories: an arming
   refused where `--compose`'s checks refuse, writing nothing; a second arming in the same project
   refused; a disarming that ends the record into the ended log.
6. Tests hold the `Stop` hook to R14 by running it as the harness does, an event on stdin: silent
   in a project without `siegard.json`; silent with no armed goal; silent for another session's
   stop; `state A` ending the goal and allowing the stop; `state B` ending it with a
   `systemMessage` carrying the stop line; `not yet` blocking with the failing checks first and
   counting; the fourth identical `not yet` allowing the stop and ending the goal `paused`; a stop
   with background work in flight allowed and uncounted; a malformed event exiting 0 with nothing
   printed; and `hooks.json` declaring the hook on `Stop`.
7. Tests hold the `Stop` hook to R15 by running it as the harness does: with no goal armed, a
   message handing a decision and violating appends one line and allows the stop under
   `measure`; one that hands no decision appends nothing; under `enforce` the first violating
   stop is blocked with the violations as the reason and the next stop of the same session is
   allowed and recorded `released`; a stop with background work in flight appends nothing; a
   project holding an armed goal appends nothing; a log that cannot be written allows the stop
   with nothing printed.
8. Tests hold the `SessionStart` hook to R16: one line on both channels where the armed goal's
   `version` differs from the plugin's; nothing where they agree, where no goal is armed, or
   where the record does not parse.
9. A test holds telemetry to R17 over a fixture log: lines inside and outside the window, a line
   that does not parse, every violation kind, a block and its release, and a project with no log
   reported unavailable.
10. Tests hold `door.py --check commit` to R18 over the fixture repositories: a log closing on a
   stop line refusing a commit naming no path and one naming the delivery, and accepting one
   naming only the telemetry root and the log; a red run uncommitted and named by no record
   refused; the same run named by a record, or committed, accepted; a commit naming no path
   under the delivery root reading no run; and the authorization listed as not decided.
11. Tests hold `/siegard-goal` to R6: its file closed to the model's invocation, arming only
   where the invocation opens with `--arm` and never over a citation, a root the invocation does
   not name read as the git toplevel of the session's working directory, and an objective handed
   to the script on stdin; no other shipped skill and not the session rules running
   `goal.py --arm`; and the handoff it renders, followed by the two lines it hands to paste,
   passing `handoff.py --check`.

## Readings

- 2026-11-01 — grounds for R6's arming by invocation, read from every consumer transcript on
  that date: `/siegard-goal` ran 129 times, 109 typed by the person and 20 invoked by the model,
  each of those on a message asking for a goal; in at least two of them the objective the skill
  received was the model's own wording — a scope it drafted from "what is still left", and a
  citation it chose — though the skill takes the objective only as the person's words, verbatim.
  `goal.py --arm` ran once, on "arme o goal pelo framework"; one message, "pode armar o novo
  goal", named no route between the harness and the framework. The word to arm was a reading of
  a message; an argument the person typed into a skill the model cannot invoke is not. The same
  reading found the skill's report filling a decision record where `handoff.py --prepare` had
  prepared a report, which holds no line to paste: the two lines follow the rendered handoff
  instead, inside fences, which `--check` reads as no prose. Reversal: a person asking a session
  to compose a goal and the session handing back the invocation to paste, measured as friction
  the person names, reopens model invocation for composing alone, with `--arm` still the
  person's argument.
- 2026-10-31 — grounds for R15–R17, read before any of them had run in a consumer. SPEC-006's
  baseline of the same date read 251 handoffs over four consumers: 62% over 1500 characters, 33%
  carrying a framework term in their first 450, 42% with no word of recommendation or decision;
  R8 moves the opening into a rendered record, and telemetry measures it only after the fact,
  from transcripts, when a person runs it. The `Stop` hook reads the message as it is handed, so
  the count accrues at every stop rather than at every telemetry run. Measured live the same day
  with `claude -p --plugin-dir dist/.claude`, CLI 2.1.316: the harness honoured a plugin `Stop`
  hook's `{"decision": "block", "reason": …}` — the session received the reason as hook feedback
  and resumed work — and a stop allowed with a `systemMessage` reached the session as an
  informational event; `last_assistant_message` on `Stop` is the harness's published hooks
  reference as read on this date, and `background_tasks` was not exercised. The mode is an
  environment variable rather than a key of `siegard.json` because `schemas/project.json` admits
  no property it does not list and the project file holds what entry points resolve — roots, the
  standard, the tests — while the mode is a harness setting the harness's own `env` already
  declares per project. The check is `goal_stop.py`'s path where no goal is armed rather than a
  second `Stop` hook, because the harness runs a stop's hooks in parallel: a second hook reading
  whether a goal is armed could read it in the instant the first ends it, and block the stop the
  armed goal just released. R16 reads only the armed goal: no delivery record — implementation,
  proof or review — carries the plugin version it was written under, and the armed goal's
  `version` is the one persisted record of the version an initiative runs under. Reversal for
  the default: a week of `siegard/handoff-checks.jsonl` under `measure` across the consumers,
  read with R17's counts, where the share of checked stops violating has not fallen and a person
  reading the violating lines — the far end named first — judges at most one in ten a false
  positive, switches the default to `enforce`; a false-positive share above that narrows what
  `--check` decides before anything is enforced. The figure is this reading's, for a person to
  apply, and no script applies it. Reversal for R16: a version line at a start whose next stop
  answered other than state B is a defect in the line, and it is withdrawn until the state and
  the line read the version the same way.

- 2026-10-31 — grounds for R14, and R6's amendment, read from the transcripts of four consumer
  projects over the four days before it: the harness's `/goal` evaluator judged a stop
  not met 119 times, 95 of them after `goal.py --state` had already printed `state B` in the same
  session — a terminal state R3 defines — and every one of those 95 was answered by another stop
  and no work. Eight goals were paused by the harness after nine consecutive blocks and needed the
  person to send a message to go on. Validation item 4 already named this a defect in what the
  condition says; no wording of the condition removed it, because the evaluator is a reading and
  R1 makes the answer a script's. R14 takes the reading out for a goal armed through the
  framework: the stop is answered by `--state`'s own computation, and a loop the harness would cut
  at nine is ended at four and said. The record lives in the git directory because the measure
  commits the telemetry root whole and the `tree` check reads everything else. The harness
  `/goal` path stays the person's alternative. Read without a live run: the hook's protocol —
  `decision: "block"` with `reason`, `systemMessage`, `session_id`, `cwd`, `background_tasks` on
  `Stop`, and a cap of eight consecutive continuations reset by a tool call — is the harness's
  published hooks reference as read on this date, not yet observed from a consumer session.
  Reversal: the hook releasing a stop at `state B` while a run could have delivered without a
  person — a state B whose stop class R8 or R9 answers by itself under the armed condition — is a
  release that ended a goal early, and the hook gains the route that answers that class before it
  ends; a paused end the person resumes by re-arming, with the run then reaching `state A` without
  a change the person made, narrows the pause bound.

- 2026-10-31 — read from `salese2e`'s transcript and repository under Siegard 5.40.0, over the
  goal `prova-recusas-registro-pedidos` (armed 15:14Z, `--since 65a7394`). R11 as `goal.py` read
  it: the goal ended state B on `commits` alone, over `d041459 reconcile
  adocao-precedencia-endereco-pedidos`, which touches `siegard-trace.json` and its own record and
  nothing else — a reconciliation R2 admits, under the message form the consumer rules state,
  "naming the skill and the slug". The script demanded a colon after the slug, which no artifact
  states; 4 of the 36 reconciliation commits in the sales consumers carry none. Run over the
  commit the goal ended on, the corrected script answers `commits: pass`, and the goal would
  have ended state A at its first review. The script now reads "its own record" as R2 writes it:
  the record under the slug the message names. Of those 36 commits, none touches another
  reconciliation's record. Grounds for R4's last sentence: each of this initiative's 4 resumes
  removed the stop line that ended the run before it, with `sed -i '/^stop:/d'`, and 7 stop lines
  were removed outright across `salese2e`, `productorder` and `productcatalog` — the 19 stop
  lines R4's grounds read were a count after those removals. The orchestrating skill's file said
  nothing is appended after the stop line and said nothing of a resume; the state was read from
  the last line, so appending after it already sufficed. Reversal: a stop line removed under the
  version that states this is a removal no prose prevents, and the state script gains the check
  that reports it.

- 2026-10-28 — grounds for R11–R13, read from `salese2e`'s transcript and repository under
  Siegard 5.35.1. R11: the person committed `aa7b89c` from another session inside the first
  goal's window; `commits` failed for good, neither state could be reached, the harness judged
  the condition not met 12 times in 67 seconds and paused the goal after 9 consecutive blocks, and
  the person cleared it by hand. R12: the walking-skeleton delivery held 7 criteria recorded unmet
  in two implementation records — six of `fictitious-module-entry`, each needing a repository no
  task writes — and R2 as it then stood would have answered state A over them. R13: the second goal
  ended state A over a review leaving one criterion partial, and the walking-skeleton review left
  59 criteria uncovered or partial, the exit criterion of the phase among them, with no line of the
  state's answer saying so. Reversal for R12: a run that ends state B on criteria recorded unmet
  which a later delivery of the same task meets without a person is a route the goal should take
  itself, and narrows R12 to what that route cannot answer.

- 2026-10-26 — grounds for R10, read before it had run: `/analyse`-origin decisions were revised
  31 of 162 times (19%, eternal, read 2026-10-07), and the person's review before a
  specification commit took a median 1.7 minutes over 108 consumer transcripts (2026-10-06) — the
  gate R10 removes was mostly nominal. Its reversal: decisions landed by a goal's `analyse`
  commit revised at a higher rate than `/analyse`'s outside a goal narrow the goal back to a
  closed specification.

- 2026-10-25 — not yet read: no goal has been composed under this specification.
