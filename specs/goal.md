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
- **R2** — State A holds when every task of the scope holds an implementation record and a proof record, or an implementation record of the substrate alone, which owes no proof; no implementation record of the scope records a criterion unmet that R12 does not answer; every task of the scope whose records changed since the goal began is named by a review record committed after them; each certification the first review committed since the goal began refused with a testable remainder, over the proof of a task of the scope, is answered by a proof-only re-delivery of one such task committed after that review; the delivery and the plan check against their sources; the specification is sound; a measure is committed after the last record and the last review; the tree holds no change but those the condition declared untouched; every commit since the goal began names a skill and the slug, or is a reconciliation that touches only the trace and its own record; none of those commits is on a remote; and the plugin runs the version the goal began under.
- **R3** — State B holds when the initiative's orchestration log, changed since the goal began, ends with a stop line whose class is one of `blocking`, `silence`, `rebind`, `producers`, `gave-up`, `infrastructure`, `project-file`, `pending-change`, `specification`, `contradiction`, `stands`, `analyse`, `outside-task`, `already-met`, `unclassified`, and the measure, commit and remote conditions of R2 hold; what the tree still holds is reported as left for the person: what a stopped delivery wrote was committed as work in progress before its stop line (R18), and anything else the tree holds is the person's to read. A plugin whose version changed since the goal began is state B on its own, and so is a commit since the goal began that touches the project file or a standard it declares: the rules the goal ran under are no longer the ones that answer, or what only the person authors changed under a goal.
- **R11** — A commit since the goal began that names no skill and the slug, and is no reconciliation R2 admits, is state B on its own: the route never rewrites history, so that commit stands until a person reads it, and a goal waiting for it to disappear never ends.
- **R12** — A scope that holds every condition of R2 but one — an implementation record of it records a criterion unmet — is state B, each such criterion named beside its task: the record says the source does not satisfy the criterion, and state A would say the scope is delivered. A criterion recorded `met: false` is answered, and no longer one recorded unmet, where a review committed since the goal began names the criterion's task and gives the criterion `covered` by a test in a file the task's own proof record names: the implementer writes no test, so a criterion that asks for one is recorded before the test exists, and the test the proof names, in a suite the proof's run passed, is the answer. The answer names each criterion so answered beside the test that answers it. A task whose proof record is not yet written names no file, so no test answers its criteria and they stay recorded unmet.
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
- **R6** — A goal condition names the route, the authorization, the scope and the invocation that answers its state, and states no rule: the rules are those of the plugin version the invocation pins. The condition is composed by a script that checks, before any goal is armed, what the first step of the route would refuse, and it is armed by the person: through the harness by pasting it after `/goal`, which no skill does for them, or through the framework by `goal.py --arm`, which only `/siegard-goal` runs, and only where the person's invocation of it opens with `--arm`: the skill is closed to the model's invocation, so its arguments are the person's own words, and no other component runs `goal.py --arm`. An invocation that opens with `--arm` over a citation composes and does not arm, because the text the person would arm is the one the script wrote, read before an invocation naming that file arms it. An objective in prose is written to a file under the telemetry root and named in the condition by path and digest, so the condition is one line whatever the objective's length; an objective the person cites — text already in the conversation they point at and adopt — is copied whole into that file, never cut to fit the route, and the evaluator reads the state command rather than the objective. A condition over an objective in prose asks to specify it, under R10, unless the person's invocation says `--no-specify`; one over epics or tasks never does. The report that composes a condition without arming it hands the one line that arms it through the framework, and the condition itself, whole, sits in the full report on disk for a person who arms through the harness. Where the person gives one, the condition states the findings policy, and a policy names only findings a route corrects: conformance findings of kind `contradicts`, which the corrective increment answers. A condition carries no budget of judged doors: a judged door is taken only under a grant the person armed (SPEC-011). The condition declares untouched every path the tree holds pending when it is composed, beyond those under the telemetry root, which the measure commits whole: a recorded ask or a grant's words pending there is the measure's to commit, never the person's to keep.

### How an armed goal ends

- **R14** — A goal the person arms through the framework ends on the state script's answer at the session's stop, never on a model's reading: `state A` or `state B` ends the goal and lets the session stop, `not yet` blocks the stop with the checks that failed, and a fourth consecutive `not yet` whose whole answer repeats the last ends the goal paused. `goal.py --arm` arms it only where `--compose`'s checks pass and the project holds no armed goal, and only `/siegard-goal` runs it, under R6; it records `siegard/goal.json` under the repository's git directory — never in the tree the state reads — holding `contract` (`goal-armed/1`), `project_root`, `slug`, `target`, `scope`, `since`, `version`, `untouched`, `objective` and `objective_sha256` (null without an objective), `condition`, `armed_at`, `session_id` (null until the first stop binds it), `blocks` and `last_state` (the digest of the last `not yet` answer, whole). The plugin's `Stop` hook answers only the session the record is bound to, in a project that declares `siegard.json`, and is silent anywhere else. `state A` or `state B` ends the record and prints one `systemMessage` line carrying the state's first line, the stop line among it under state B; `not yet` prints `{"decision": "block", "reason": …}` whose reason is the state's first line, every failing check with its output verbatim, the line that the stop is answered with the route's next step — never another stop, and no work the route does not name — and the condition repeated; a stop while the session holds background work in flight is allowed and not counted. An ended record — `state A`, `state B`, `paused`, or `disarmed` by `goal.py --disarm` — is appended to `siegard/goals-ended.jsonl` beside it with `ended`, `reason` and `ended_at`. A state the hook cannot compute allows the stop and leaves the goal armed. What the person reads first when the goal ended with nothing delivered is SPEC-006's.

### What a stop no armed goal answers holds

- **R15** — Where no armed goal answers the stop in a project that declares `siegard.json`, the plugin's `Stop` hook reads the event's `last_assistant_message` and the session's turn record, and where `bin/handoff.py`'s own reading says the message hands a decision, or the turn ran a skill whose run ends on a render, appends one line to `siegard/handoff-checks.jsonl` under the repository's git directory — never in the tree the state reads — holding `at`, `session_id`, `characters`, `hands_decision`, `route`, `rendered`, `mode`, `violations` as `handoff.py --check` prints them, `kinds`, `blocked` and `released`. The turn record is what the plugin's `PostToolUse` hook wrote since the session's last allowed stop, from the calls the harness hands it and never from the transcript: the instant of the last `Skill` invocation of a skill whose run ends on `bin/handoff.py --render`, which makes the line's `route`; the line's `rendered` is a record that command keeps under `siegard/handoff/` newer than that instant, a refused render keeping none; an allowed stop clears the record. The mode is the environment variable `SIEGARD_HANDOFF_STOP`, which a project declares in the harness's own settings: `measure` is the default and the reading of every value but `enforce`, and under it the hook never blocks; under `enforce` a stop whose turn ran such a skill and printed no render is blocked once, `{"decision": "block", "reason": …}`, the reason asking for the render and for a recommended door over a stated answer, and the next stop of the same session is allowed whatever its message holds and recorded `released`. The violations of a message's form are recorded and never block. A stop while the session holds background work in flight is not read, a stop R14 answers `not yet` is R14's alone, while a stop on which R14 ends the goal — `state A`, `state B` or paused — is read here once the goal has ended, the line R14 says kept beside whatever this hook answers, and a stop of another session, where the armed goal is bound to one, is read here too — and every failure allows the stop and prints nothing.

### What a session starts on

- **R16** — At a session's start in a project that declares `siegard.json` and holds an armed goal, the plugin's `SessionStart` hook prints one line, to the person and to the session, when the plugin version loaded differs from the armed goal's `version`, and nothing when they are equal or either cannot be read; it never blocks. It also prints one line when the armed goal is bound to a session other than the one starting, naming the goal's slug, when it was armed, and that `goal.py --disarm` ends it.

### What a goal answers without a person

- **R8** — In an orchestrating run, under a goal or under the person's own ask alike, a delivery that stopped over a fact no node states is answered by planning's decided-fact route, a task waiting on a re-bind by planning over its slug, and a delivery whose `stands` does not stand — a record carrying it the writer refused, or a planned one `/implement-task` read out of date on a node the task implements before writing — by the reconciliation the refusal names (SPEC-004 R20), each once per task, before the run resumes; a second time over one task is a stop.

  Reading of 2026-11-18, from the `configurator` run of `pendencias-tmforum-do-configurator`:
  three planned `stands` tasks whose files were stamped against an earlier text of the contract
  each implements — moved by the run's own `/analyse` — were read out of date by
  `/implement-task` before any write, as SPEC-004 R26 asks, and never reached the writer; the
  run's door was written for the writer's refusal alone, so it took none and closed on
  `stop: stands`, a class meant for a refusal after the reconciliation. The person ran the
  reconciliation by hand. Replayed with `claude -p` (Sonnet, the run resumed at the task, three
  runs per arm over that state and over a `partymgmt` one): the reconciliation was taken in 1 of
  6 runs under the writer-only wording — the one run that skipped the earlier reading and was
  refused by the writer — and in 5 of 6 under this one; a blind Opus judge scored the route 1.67
  and 4.17 of 5.
- **R9** — Under a goal whose findings policy names a finding's kind, each such finding of the run's review is answered by one corrective increment over the file it names, delivered and reviewed in the same run, once: what that review finds is reported and never corrected again.

- **R10** — Under a goal whose condition asks to specify a prose objective, the orchestrating entry point invokes `/analyse` once, before the plan, over the objective as the person armed it, and the specification root is committed apart, by `/analyse` itself (SPEC-010 R7). That commit takes the ledger the analysis answered beside the objective with it while a line of it is open, and its removal once none is (SPEC-001 R16). A stop of `/analyse` over material that states no fact, or that names nodes and changes none, is nothing to specify, and the plan follows; every other stop of it ends the run. Each of those two stops is printed as one line of its own, `stop: no-fact — <what the material would have to state>` or `stop: no-change — <the nodes it names>`.

### What is counted

- **R7** — Telemetry counts the goal evaluations the harness recorded in each session of its window, those judging the condition met and those judging it not met.
- **R17** — Telemetry reads `siegard/handoff-checks.jsonl` beside the transcript-derived form of the handoffs and counts, over the lines inside its window, the stops checked, those violating, each violation kind, those blocked and those released, and names the longest message checked by session and instant; a log that does not exist is reported unavailable with its path, never as a count of zero, and a line that does not parse is counted apart.

- **R18** — A run whose orchestration log closes on a stop line commits nothing after it but the measure: the telemetry root, the log that carries the stop line, and the captured runs of the initiative that ended `passed`. A captured run that ended other than `passed`, that git does not hold, that no record under the initiative's delivery root names and that no later attempt under the same run name passed, is refused to a commit that reaches that delivery root: a red attempt a record names, or a later attempt answers, is the delivery's own evidence, and one neither answers is a red nothing answered. A delivery that stops commits what its own invocation wrote before its stop line is written, once, as work in progress: pathspec-scoped to those files, under `<skill> <slug>: wip <task>`, its message naming every run among them that ended red, so the next route opens on a clean tree and nothing the stop left is lost; `bin/door.py --check commit --wip` accepts such a red as the stopped delivery's own evidence and lists it. The stop line a commit is held to is the one it adds to the log: a stop line already committed binds the run that wrote it, and the commit of a later invocation of the initiative is not refused for it. Whether a commit breaks either is `bin/door.py --check commit`'s answer, read from the log and the runs as they stand on disk before the commit is made, over the paths the commit names; a commit that names none is read as one of the delivery. Whether the person's words authorize the commit is no file's answer, and the check lists it as not decided.

  Grounds, as the maintainer relayed them on 2026-10-31 and not yet read from a transcript here:
  a session committed a delivery whose orchestration log said the suite was red and that nothing
  of the delivery was committed. The log's stop line was already the record that the run ended;
  nothing read it before the commit.

  Reading of 2026-11-16, from the sales consumers' commits of the preceding 48 hours (213 that touched a delivery root, each rebuilt as its parent tree plus its pending changes and put through the check): a log read by its last line refused 18 commits for a stop line, 1 of them the commit that recorded the stop (R19), 3 of a resumed `/deliver-scope` run that appends its first line after its first commit, 11 of `/implement-task` and `/review-change` run directly after a stop, which write no log line, and 3 corrections the person asked for. A red run no record names refused 2 ordinary deliveries whose red build was followed by a green one; of the 10 red builds in the window, every one had a later green attempt and 5 were named by no record. Reversal: a run that commits after its own committed stop line without a line of its own, or a red whose later green attempt hid a cause nobody wrote down.

- **R19** — A `git commit` a session runs in a project that declares `siegard.json` is refused by the plugin's `PreToolUse` hook where it adds a stop line to an initiative's orchestration log and carries a path other than an orchestration log, a path under the telemetry root or a captured run of that initiative whose record ended `passed`: the commit that records a stop is the measure alone, and the delivery's files, a red run no record names among them, are never carried by it: R18's work-in-progress commit carried them before the stop line. A run that passed is the evidence the delivery captured and no delivery file, so it rides with the measure and leaves no pending change for the next arming to refuse. A commit that adds no stop line is not read by this requirement.

  Grounds, as read on 2026-11-16 from the inventory session that stopped `token-do-catalogo`: the commit carrying the stop line also carried the red run `...-suite-2`, and R18's check, which the session was told to run before committing, was not run. Replayed over the 213 commits of six consumer repositories that touched a delivery root in the preceding 48 hours, the refusal reads the stop line itself, so it refuses that commit and no other; the wider reading of R18, a log closing on a stop line at the time of any later commit, refused 20 commits more, of which the doors a stop hands (`/implement-task` re-delivery, `/review-change`) and the person's own corrections after a stop were most.

  Reading of 2026-11-16, from the `salese2e` session that stopped `inventory-real-nas-jornadas`: the stop left the setup run, which `passed`, uncommitted under the delivery root; `goal.py --arm` refuses a change pending under that root, so the person's own word to commit was the only way to arm again, 48 minutes later. R18 admits a run that passed to every other commit, so the refusal of R19 over it protected no red. Replayed over R19's tests with a passed run beside the stop, the commit goes ahead; a red run, an unreadable record and a delivery file beside the stop are still refused. Reversal: a run that passed and hid a cause nobody wrote down, committed with a stop.

## Validation required before acceptance

1. Tests hold `goal.py --state` to R2, R3, R11, R12 and R13 over fixture repositories: one
   answering each state, one per condition of R2 failing alone, a foreign commit answering state
   B, a criterion recorded unmet answering state B with the criterion named, a criterion recorded
   unmet that a review gives `covered` by a test in a file the task's own proof names answering state A
   with the test named, one a review gives `covered` by a test in no file the proof names staying
   state B, a criterion a review left uncovered named under state A, a commit naming the skill and the slug with
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
   `measure` and under `enforce` alike; one that hands no decision in a turn that ran no
   rendering skill appends nothing; a turn that ran one appends its line whatever the message
   holds, `route` true and `rendered` as the turn record says; under `enforce` such a turn with
   no render is blocked with a reason asking for the render, and the next stop of the same
   session is allowed and recorded `released`, while one that rendered is allowed; an allowed
   stop clears the turn record and a blocked one keeps it; the `PostToolUse` hook records the
   instant of a `Skill` call to a skill whose run ends on a render and of no other, and a turn
   reads `rendered` where a kept record is newer than that instant and not otherwise; a stop with background work in flight appends
   nothing; a stop an armed goal answers `not yet` appends nothing; a stop on which the armed
   goal ends in `state A`, `state B` or paused is read like one no goal answers — its line
   appended, under `enforce` a route turn left unrendered blocked once with the goal's ending
   line still said and the next stop released — and the goal stays ended either way; a log that
   cannot be written allows the stop with nothing printed.
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
   under the delivery root reading no run; a red run under `--wip` accepted and listed; and the
   authorization listed as not decided.
11. Tests hold `/siegard-goal` to R6: its file closed to the model's invocation, arming only
   where the invocation opens with `--arm` and never over a citation, a root the invocation does
   not name read as the git toplevel of the session's working directory, and an objective handed
   to the script on stdin; no other shipped skill and not the session rules running
   `goal.py --arm`; and the handoff it renders, followed by the line it hands to paste,
   passing `handoff.py --check`. Tests hold `goal.py --compose` to specifying an objective in
   prose by default: its condition carries the sentence that asks to specify without any flag,
   `--no-specify` leaves it out, `--specify` changes nothing, the two together are refused, and
   either over a scope of epics or tasks is refused, and to declaring untouched no path
   under the telemetry root.
12. Tests hold `/deliver-scope` to R8 over its text: the re-bind, the decided-fact route and the
   reconciliation a `stands` refusal names, by `/implement-task` before writing or by the record
   writer, each taken in a run with or without a goal, each under
   its commit message, once per task, a second time over one task a stop —
   `tests/test_deliver_scope.py` proves each.
13. Tests hold `goal.py --state` to R2's proof clause: a certification the first review left
   with a testable remainder over the proof of a task of the scope is `not yet` under `prove`
   until a `deliver-scope <slug>: prove <task>` commit of one such task follows the review — the
   task named by its id, or by its bare name where one task of the scope alone carries it, a bare
   name none carries answering nothing — and a remainder over a proof no task of the scope holds
   owes nothing — `tests/test_goal.py`.
14. Tests hold the commit hook to R19 over fixture repositories: a commit adding a stop line and
   carrying a run directory refused, and the same with a commit of all that is tracked; a commit
   of the log alone, of the log and the measure, and of a log whose added line names no stop
   class going ahead; a commit after the stop adding no stop line going ahead; a staged file the
   commit's pathspec leaves out not counted; and a project without `siegard.json`, or a log that
   cannot be read, going ahead.

## Readings

- 2026-11-24 — grounds for R14's answer line in a `not yet`'s reason. The session rules told a
  session how to answer a `not yet`, but they had grown past the 10,000 characters Claude Code
  places whole from a hook, and since 2026-10-31 that line reached no session. The block reason is
  read at the one moment the rule binds, by the one session it binds, so it carries the line and
  the session rules keep only that arming and disarming are the person's. Reversal: a session that
  answers a `not yet` with another stop or with work the route does not name while the reason
  carried the line.
- 2026-11-23 — grounds for R18's work-in-progress commit, the maintainer's bound changed to state
  it the same day. Read from a week of the sales consumers' transcripts (2026-11-16 to
  2026-11-23): about 11 times, in five projects, a stopped delivery left what it wrote in the
  tree, every next route refused the pending change, and about 20 stops asked the person to keep
  or discard it. The person's answers were "pode comitar", "1", "segue o sugerido", "pode mover o
  run" and "pode fazer o deliver scope" — never a discard by choice. One delivery's code was
  discarded with `git restore` and `git clean` so that a goal could be armed again
  (configurator, 2026-11-23), and one session moved a stopped delivery's files to `/tmp`
  (salese2e, 2026-11-16). The one work-in-progress commit the person chose (`f767b55`,
  productorder, 2026-11-22, carrying an implementation record, three specs and a red suite run)
  was followed by fourteen deliveries of the same run without a refusal. The commit precedes the
  stop line, so R18's after-the-stop clause and R19's measure-alone refusal are unchanged; its
  subject names the skill and the slug, which the state's `commits` check reads as on the route,
  and `wip` in it says the delivery is not delivered, which is what R18 was written to keep
  apart. Reversal: a work-in-progress commit that no later delivery of its task builds on within
  a week, or one a person reverts.

- 2026-11-23 — grounds for validation 13's bare name. `references/prove.md` of `/deliver-scope`
  says to commit `deliver-scope <slug>: prove <task>`, and `goal.py` read only `<epic>/<task>`
  there. inventory's `party-ref-published` committed `prove
  characteristic-received-with-null-value-held-without-a-value` (`9763282`), the task's own name
  as the reference wrote it, and the goal stayed `not yet — failing: prove` over a re-delivery it
  had made; the session asked the person seven times, over 15 hours, whether to add an empty
  commit carrying the epic. A task's name is unique within an epic, not across a plan, so the
  bare name answers only where one task of the scope carries it. Reversal: two tasks of one scope
  sharing a name and a run proving one of them under it, which reads as no answer and names the
  id form in the stop.

- 2026-11-23 — grounds for R15's turn record and for what `enforce` blocks. Read from the
  inventory, productorder and configurator transcripts and their `handoff-checks.jsonl` under
  5.136.0/5.136.1. A week of lines under `measure` held 456 stops checked and 340 violating; 40
  of the 340 — the 10 longest, then 30 drawn with seed 22 — were read by a session the person
  delegated to and the person confirmed it: 6 handed no decision, 19 a vague or buried one, 15 a
  clear one. The 6 are 15%, over the one in ten the earlier reading set, so a block on the
  message's form stays off. Of the 6, 4 answered the person's own question in free conversation,
  where no skill ran and no render applies, and 2 closed a route without a choice (a goal ended
  state A; a review recorded). Which signal of `bin/handoff.py`'s reading fired was counted over
  the 40: a decision word anywhere fired on 38, and no signal of the words separated the two
  route closings from the route stops whose decision was buried. The turn record is what
  separates them without the words: a turn that ran a skill whose run ends on a render owes that
  render, whatever its message holds. Replayed with `tools/replay_stops.py` over 24 stops the
  person answered with a go-ahead or a "what now?" (live grant, one run each): the block asking
  for a render or a rewrite rendered 4 of 24 and the sessions rewrote instead; the block asking
  for the render alone rendered 19 of 24 and its message carried a recommendation in 6, the
  others handed as the person's own; over the 14 of those whose render handed a decision, the
  same block without naming `settles` rendered 14 of 14, carried a recommendation in 9 against
  3, handed 7 as the person's own against 12, and the grant took 2 against 1. Estimator: the
  grant's lines in each run's stream, the intercept log and the clone's check log; $0.75–$0.95 a
  run. Reversal for the default: a week of lines under `measure`, the far end named first, read
  for those with `route` true and `rendered` false; where a person judges at most one in ten a
  turn that owed no render, the default becomes `enforce`; above it, the set of skills read as a
  route narrows first. This replaces the 2026-10-31 reversal, which read the violating lines.

- 2026-11-15 — grounds for R2's proof clause: `/deliver-scope`'s step 5 «runs once per run», and
  runs skipped it with reasons the step does not state. Read from the sales consumers' git and
  orchestration logs since the step's present form (5.68.0): of the first reviews of a run that
  left a testable remainder over a task of its own, eleven were followed by proof-only
  re-deliveries, one began its re-delivery and stopped, and five did not run the step — productcatalog `remover-tmf679-qualificacao-oferta` ("not
  run" by a `decided:` line, cost given as the reason in the report), inventory
  `product-inventory` (skipped "por custo" until the person answered "1"), `salese2e`
  `prontidao-em-duas-ondas` (a drift elsewhere), `configurator-no-e2e-etapas` (tests "no task of
  this run owns") and `troca-origem-tmf679-productorder` (a stop line). Two of those ended their
  goal in state A, which the state could not see. Replayed over every goal ended in state A, the
  clause fails exactly those two. A certification names under `read_at` the proof files it read,
  and the step's run in `salese2e` `perfis-de-acesso-do-bff` answered five certifications with two
  re-deliveries, one task per certification, so one re-delivery among the tasks a certification
  read closes it. A run without a goal is not read by the state, and keeps the step's text alone.
  Reversal: a goal held at `not yet` on `prove` whose re-delivery the step's own text would not
  owe.

- 2026-11-15 — grounds for leaving the telemetry root out of what a condition declares untouched,
  read from `goals-ended.jsonl` and git of five sales consumers (Siegard 5.89.0 to 5.106.0). The
  condition declared untouched every pending path, so the asks `ask.py --record` writes and a
  grant's words — which `ask.py`, `/siegard-grant` and R18 each say the measure commits with the
  telemetry root — were also "never edit, commit or discard". Of the 29 pairs of a goal and a
  telemetry file it declared untouched, four measures committed six against the condition
  (configurator `cb3097c`, `7fc90b4`; partymgmt `a61f6c8`, which the session reported as its own
  mistake; productorder `0df5ef7`), the person committed five such files by hand afterwards
  (configurator `b2049d8`, productorder `f51b502`), and nine stay untracked on this date
  (configurator 3, `salese2e` 5, productcatalog 1), each declared untouched again by the next goal. `state` saw none of it: a path committed leaves no pending change for `tree` to
  read. Leaving the measure only its own report instead was weighed and set aside: it contradicts
  three shipped statements, and the asks would never be committed. Reversal: a file the person
  placed under the telemetry root by hand, committed by a measure against their wish.

- 2026-11-14 — grounds for specifying a prose objective by default, read from
  `goals-ended.jsonl` of every sales consumer (Siegard 5.43.0 to 5.100.0): of 27 goals armed over
  an objective in prose, 19 asked to specify. Of the 8 that did not, 2 ended within about two
  minutes on a contradiction between the objective and the specification — `configurator`
  2026-11-13 19:10 and 23:01 — and were armed again with `--specify` over the same objective; the
  other 6 would now run `/analyse` they did not ask for, which the person accepted when asked.
  Grounds for handing one line where a goal is composed: the line after `/goal` a composing
  report handed was last pasted on 2026-11-01, and every goal armed since went through
  `/siegard-goal --arm`. Reversal: a goal stopped by an `/analyse` that wrote a fact the person
  then reverts, more often than a contradiction stop, narrows the default back to the flag.

- 2026-11-13 — grounds for R12's second sentence, read from the git history of `configurator`,
  `productorder`, `salese2e`, `partymgmt` and `productcatalog`: 146 distinct criteria were
  recorded `met: false` across their implementation records. The first review naming the task
  after the record gave 54 of them `covered`, and 48 of those by a test in a file the task's own
  proof names; the other 6 were covered by tests of no such file, among them three criteria of the
  form "in a pnpm e2e run … the journey passes", which no suite the proof ran decides. Read by
  their text, 45 of the 48 are criteria about a test or a suite ("a unit test fails when X is
  removed", "the route sweep passes") and 3 are two migration outcomes and one refusal that a test
  of the same task holds; none of them was a source that failed the criterion. In `salese2e`,
  `configurator-no-e2e-etapas` ended state B over 5 such criteria in 3 tasks while its review
  gave all 5 `covered`; the person's re-delivery of the 3 tasks wrote the same records again with
  `met: true`, each `how` citing the test, at the cost of 3 full deliveries. The estimator reads
  each record's front matter at the first commit holding the entry and the review's `coverage` at
  the first review commit after it; the proof is read at the repository's `HEAD`, which may
  postdate the review. A review and a proof quote a parametrized test under different names, so
  the answer matches on the file: matching on the name as well cleared 38 of the 48. Reversal: a
  criterion answered here that a later review, run or person finds the source did not satisfy
  returns R12 to the record alone.

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
- 2026-11-14 — grounds for reading the stop on which a goal ends, under R15: the one goal of
  the 12 hours to 2026-11-14T10:41Z that ended in `state A`, in `configurator` (Siegard 5.100.0),
  closed on a 3,670-character message the session wrote in English to a person writing in
  Portuguese, without `bin/handoff.py`, saying so itself. Run over it afterwards, `handoff.py
  --check` names three violations — a term of the closed list in the opening, the length, and the
  first decision word at character 2,484 — and none was recorded, because R15 left every stop R14
  answered to R14, the one that ends the goal among them. That stop answers nothing R14 still
  needs: the goal is over and control returns to the person on it.

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
  the default (superseded by the 2026-11-23 reading, which reads the turn record instead): a
  week of `siegard/handoff-checks.jsonl` under `measure` across the consumers,
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
