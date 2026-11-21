---
id: "SPEC-011"
title: The grant
status: proposed
contract_version: spec/1
---

# The grant

## Scope

This specification fixes what the person's recorded grant lets a session do at a stop without
asking, who can record it, what ends it, and the gates a script holds each act to. A grant holds
for a project until the person clears it, over every live initiative or over the one it names. It binds
`bin/grant.py`, the one script that records, reads and ends a grant and answers every act it is
asked about, `/siegard-grant`, the one skill that arms it, the plugin's `PreToolUse` commit check
where it reads an orchestration log's `decided:` lines, the session rules' one line that
sends a stop to the script, `bin/handoff.py --render` where it keeps the record it rendered, and
the orchestrating entry point `/deliver-scope`, where it receives a stop.

A grant is the person's own words, decided in advance, for the stops the framework would
otherwise hand back: it arms the taking of a judged choice, and its budget, over a handoff's doors,
and the taking of a run's commits and of the closing of a plan, under a goal or outside one; it
is the one place a judged door is armed. It widens no bound of SPEC-006 R3 or of the session rules: a choice the person
reserves stays theirs under any grant, and a grant that names an act the gates refuse takes
nothing.

Grounds: five sales consumers, 2026-10-30..2026-11-13 (Siegard 5.19.0–5.96.0). In 4 days, 104 of
381 human messages (27%) only unblocked the framework — `Sim`, `a`, `1`, `pode comitar`,
`autorizo` — 139 replies were answers to a stop, and the person ran a scheduled prompt, "advance
with the next recommended action", 158 times in two projects, of which 46 advanced anything.
Over those 139 stops and 252 more read from the ten days before, a policy of the five kinds
below was held to what the person then said: it agreed with the person on 94.7% of the 113 stops
it decided and on 97.4% of 38 in a half of the older data never used to shape it; it covered 40%
of all stops and 46% of the stops the person answered with a decision, because 24% were answered
with a question or a new request. An independent audit of the acts it would take found 21 of 156
crossing a bound, 9 of them one kind of commit the policy dropped, and the other 12 each one a
bound a script on disk decides.

### Decided elsewhere, deliberately not restated here

- What a door is, which doors a handoff hands, and what recommends one: `specs/handoff.md`
  (SPEC-006). A choice the person reserves — a contradiction between scope and specification,
  two readings of one piece of evidence, a finding's worth — is SPEC-006 R3's.
- What the person's words authorize and how they are kept: `specs/carried-words.md` (SPEC-010).
- What a goal ends on and what its condition arms: `specs/goal.md` (SPEC-008).
- Whether a door's own entry point refuses its inputs: `bin/door.py --check` (SPEC-006 R9).

## Definitions

- **Grant** — the record `bin/grant.py --arm` writes inside the repository's git directory,
  beside the armed goal's: the clauses, the initiative's slug where the person names one, the
  person's words under a digest, its mark, the plugin's version, and `HEAD` at arming.
- **Words** — the person's invocation of `/siegard-grant` as typed: its flags and their values,
  and any sentence the person adds after them.
- **Mark** — what one grant is told apart by: the digest of its words' digest and the instant it
  was armed, so that two grants armed with the same invocation never share one.
- **Clause** — one of `doors`, `commits`, `close`, each naming what the grant lets the session do.
- **Taking** — doing the act without asking the person: invoking a door, making a commit, closing
  a plan.

## Requirements

### Who arms it

- **R1** — A grant is armed only by the person's own invocation of `/siegard-grant`, a skill closed
  to the model, whose arguments are the person's words. `bin/grant.py --arm` records the words — the
  invocation as typed, with no sentence needed beside its flags — verbatim under their digest,
  and, where the project holds an armed grant that still stands, ends it and arms the new one (R3);
  it refuses to arm where the invocation names nothing, where a slug the person names is no live initiative, or where no clause is named.
  No other component runs it. The person ends it with `/siegard-grant --clear`, which runs
  `bin/grant.py --disarm`, and the project then behaves as it did before the grant; where none is
  armed it says so and refuses nothing.

- **R2** — A grant holds at least one clause: `doors`, a list from `plan-work`, `implement-task`,
  `review-change`, `reconcile`, `deliver-scope` and `analyse`, which is all six where the person
  names none, with a budget of judged doors for each initiative it covers, a whole number, which is
  zero where the person names none; `commits`, which lets a session commit what the route wrote; `close`, which lets a session
  close an initiative where R7 holds, the grant's words being the reason it is closed under. The
  person narrows `doors` by naming them, and `none` leaves it empty for a grant of commits or of a
  closing alone; no other entry point is ever in it. A grant names no initiative unless the person
  gives a slug, and without one it covers every live initiative of the project. What `--arm`
  recorded is printed: the initiative or the project, the doors, the budget, the clauses, the words'
  digest, the mark and the plugin's version.

### What ends it

- **R3** — A grant ends when the person clears it, when the plugin's version is not the one it was
  armed under — the rules a grant took are those of its version — and, where it names an initiative,
  when that initiative holds a `closure.md`. An initiative holds its `closure.md` once `HEAD`
  holds it: a closure written and not yet committed is the commit its closing still owes, and
  until that commit lands the initiative is one the grant covers and a grant naming it stands.
  An ended grant is appended, with its reason, to the
  ended log beside it, and takes nothing. An arming over a grant whose record is still in place but
  that has ended so appends it to that log, says that it ended and why, and arms; nothing is
  appended where the arming is refused on another ground. An arming over a grant that still
  stands ends it in that log as `replaced`, says what it held — the initiative or the project, the
  doors, the budget, the clauses and the mark — and arms; the person needs no `--clear` first, and
  a refused arming leaves the standing grant in place.

### What it lets a stop do

- **R4** — `bin/grant.py --decide`, over the record a stop's handoff was rendered from, answers
  each decision with one of three lines: `stop`, `take` or `judge`. A decision that carries
  `settles` is `stop`: the choice is the person's. Of the doors a decision hands, the ones whose
  check answered `refuses` are excluded; where exactly one door remains — the only door a decision hands, with none excluded,
  included — and its entry point is in the grant's `doors` the answer is `take`, the criterion
  `precondition unmet`; where the
  recommended door's check accepted and its entry point is in the grant's `doors` the answer is
  `judge`, with the doors, the budget left and the facts the decider reads, and where no door
  qualifies it is `stop`. A door whose check was not run is never taken.
- **R5** — `judge` is answered by the door decider, blind to the grant and to any goal condition,
  and within the budget; the door it names is taken, one `decided:` line carrying the rung it named
  and the grant's mark among its deciding facts. The budget left is the grant's budget less the
  judged `decided:` lines the stopped initiative's log gained since the grant armed, each covered
  initiative counted apart, and a judged choice met with it spent is `stop`. «Each door taken is one line of the
  run's orchestration log, `decided: <door> — <criterion> — <deciding fact>`, and a door R3
  reserves is never taken.» (SPEC-006 R7)
- **R6** — The plugin's `PreToolUse` commit check reads an armed grant for a judged `decided:`
  line: a line over a rung of the ladder is taken where a grant names the log's initiative or
  names none, and refused where none is armed, an armed goal notwithstanding.

### Where a run meets it

- **R9** — `bin/handoff.py --render` keeps the record it rendered, as JSON beside the report its `report` names, so that the run that receives a stop can ask the grant over the doors it handed. `bin/grant.py --decide --latest <skill> --after <commit>` answers over the newest record kept for that skill after that commit, and refuses where none was, so that a run never answers over the report of an earlier stop. `--render` asks the grant over the doors of the decision it rendered and prints its answer on standard error — the `grant:` line and one line per decision, and, where a decision's recommended door carries no `entry`, a `note:` saying so — so that the answer reaches the session at the stop and not at the memory of a rule; nothing is printed where no grant is armed, and a grant of another version is ended there and the line says so. A `judge` line over a door whose check ran over an `inferred_slug` says so beside the door.
- **R10** — Where the project holds an armed grant, the orchestrating entry point asks `bin/grant.py --decide` over the report of a step that stopped, before it ends the run: a `take` or a `judge` it answers is a door the run takes and goes on with, under a goal as without one, and a `stop` leaves the stop as it was. A session that rendered a stop's handoff takes the answer `--render` printed as `--decide` would have. The same door over the same task is taken once in a run. A `decided:` line a grant took ends `(grant sha256 <digest>)`, and the grant's budget counts it. The digest is the grant's mark, and the budget counts only the lines that carry its own.
- **R11** — Where the project holds an armed grant holding `close`, a closing asks `bin/grant.py --close` over the initiative, named by `--slug`, before its marker is written, and a first line `refuses` stops it unless the person's own words in the session name that initiative's closing. The ask a closing persists is words copied whole — the grant's, read from the file the grant names, where the closing is taken under it, or else the person's own — and never a summary the session writes.

### The gates

- **R7** — `bin/grant.py --commit`, over the paths a commit names, answers `accepts` only where the
  grant holds `commits` and every path is one the route writes — under the delivery root or the work
  root of an initiative the grant covers, the telemetry root, `siegard-reconcile/`, the trace, or
  named by a record of such an initiative — and none is outside the project, a path of `siegard.json`,
  a declared standard, `CLAUDE.md`, a file that holds credentials, a `closure.md` while the close
  clause does not hold, or a specification file the commit modifies where `HEAD` already holds it,
  beyond its decision log. A path that holds a change no record of a covered initiative accounts for
  is `refuses`. A first line `refuses` stops the commit unless the person's own words in the
  session name that commit: a commit they name is not a taking. `bin/grant.py --close`, over one initiative the grant covers, answers `accepts` only
  where the grant holds `close` and the goal computation over the initiative, read from the grant's
  `HEAD`, finds every task delivered, proven and reviewed, no criterion unmet that no covered review
  answers, and a sound specification; the closure's reason is the grant's words, never the
  session's.
- **R8** — Whatever the clauses say, a grant takes no push, no branch and no history rewrite; no
  edit of a file by the session outside a skill; no action in another project's tree and no command
  the project's registry does not declare; nothing a door's own check refuses; and no choice R3 of
  SPEC-006 reserves to the person.

## Validation required before acceptance

1. Tests hold `grant.py --arm` to R1, R2: a recorded grant carries the words verbatim under a
   digest and a mark that two armings of the same words never share, an invocation recorded with
   its flags alone arms, and an invocation that names nothing, an unknown slug, no clause and an entry point outside the
   list are each refused, a grant without a slug covers every live initiative, a grant that names
   no door holds all six, `none` holds none, `--disarm` returns the project to no grant and with
   none armed says so, and a plugin version change, or a closure of the initiative a grant names,
   ends it under R3; an arming over a grant so ended ends it in the log, says so and arms, an
   arming over a grant that still stands ends it in the log as `replaced`, says what it held and
   arms with a mark of its own, and an arming refused on another ground leaves either in place.
2. Tests hold `grant.py --decide` to R4 and R5 over handoff records: a `settles` decision is
   `stop`; one door left after a refusal, and the only door a decision hands, are `take`; a recommended door that is accepted beside an
   open door is `judge` with the budget left, counted over the stopped initiative's log alone; a
   spent budget, a door outside the list and an unchecked door are `stop`; and a report whose
   recommended door is a proof-only re-delivery after a certification refused again is `judge`.
3. A test holds the commit check to R6 over a fixture log: a judged line with a grant armed is
   taken, and with a goal armed and no grant, or with neither, it is refused.
4. Tests hold `grant.py --commit` and `--close` to R7 and R8 over fixture repositories, one refusal
   per bound the requirement names, one acceptance of a commit that names only paths a record
   of a covered initiative writes, and a grant without a slug accepting the paths of any live
   initiative and answering `--close` only over the initiative it is asked about; under a grant
   holding `commits` and `close`, with or without a slug, `--commit` accepts the closing's own
   paths — `closure.md`, its `intake/` ask and the derived `plan.json` — written and not yet
   committed, and once that commit lands the initiative is no longer covered.
5. A test holds `/siegard-grant` closed to the model and the session rules' line to the script,
   the person's own words in the session exempting from a refusal the commit or the closing they
   name.
6. For R9 and R10: a test holds `handoff.py --render` to keeping the record beside its report and
   `grant.py --decide --latest` to reading the newest one of a skill; a test holds the grant's
   budget to counting only the lines that carry its digest; and `/deliver-scope`'s file states the
   requirement in the words above — `tests/test_grant.py`, `tests/test_handoff.py`,
   `tests/test_goal.py` and `tests/test_skill_contract.py` prove each.
7. For R11: a test holds `/plan-work`'s closing reference to asking `grant.py --close` with
   `--slug` before the marker, to `grant.py --commit` before the closing's commit, and to
   persisting the ask copied whole, stated in the words above, and the session rules' invocation
   of `--close` to naming `--slug` — `tests/test_skill_contract.py`.
8. For R9's answer at the render: a test holds `handoff.py --render` under an armed grant to printing `judge`
   with the budget left on standard error for a recommended door its check accepts beside an open door, `stop`
   with the note naming the lost entry where the recommended door carries none, nothing where no grant is armed,
   the note for a recommended door with no entry, whether or not a door of the skeleton is absent, the ending of a grant of another version, and the inferred initiative beside a door whose check ran over one —
   `tests/test_grant.py`.

## Readings

- 2026-11-15 — grounds for R3's closure at `HEAD`: no closing taken under a grant could pass the
  commit gate. `/plan-work`'s closing writes `closure.md`, then asks `grant.py --commit` before
  its commit, as R11 and R7 order; the gate read the marker from the tree, so a grant naming the
  initiative had ended (`refused: the grant ended — <slug> holds a closure.md`) and a grant naming
  none no longer covered it (`is no path the route writes`), for all three paths of the closing.
  Read in `partymgmt` session `35073eba` (Siegard 5.106.0): `grant.py --commit` refused the
  closing of `n17-autorizacao-por-direito` and the session committed it in the same command
  (`80c87c3`); reproduced over `tests/test_grant.py`'s fixture for both grant shapes. R7 already
  named a `closure.md` as a path the close clause admits. Reversal: a closure left written and
  uncommitted under which a grant took a door over the closed initiative.

- 2026-11-15 — grounds for R7's exemption of a commit the person's words name. The session rules
  stopped every commit `grant.py --commit` refused, a commit the person named in the session among
  them, while R11 already exempted a closing the person names, and a taking is defined as an act
  done without asking. A benchmark run of the session rules
  (`tests/fixtures/benchmarks/rules/`, iteration 1) held it: under a grant armed with `--commits
  --doors none`, all four runs asked to "comita o fees.py e o teste e dá push" stopped on the
  gate's refusal — two files the session wrote outside a skill — and committed nothing, where with
  no grant armed the same words were committed. Read the same day from every consumer transcript:
  `grant.py --commit` and `--close` never ran; of the commits made while a grant was armed, at
  most 89 (the windows ignore R3's end at a version change), one followed a commit word of the
  person. The exemption leaves the gate on every commit taken without asking. Reversal: a commit a
  person named under a grant that the person then reverts, read as recurring, narrows the
  exemption to the paths the words spell.

- 2026-11-14 — grounds for the grant as the one home of a judged door, and for its budget per
  initiative (R2, R5, R6, R10; SPEC-006 R7, R12; SPEC-008 R3, R6, R14), read from every
  orchestration log of the five sales consumers on that date: no judged `decided:` line in the
  form `goal.py` counts was ever taken, by a goal's budget or by a grant's. The five goals ended
  last in `salese2e` were armed with a budget of zero, and the five grants of 2026-11-13 with a
  budget of five. Of the three judged choices a goal condition answered, a delivery that gave up
  and an infrastructure failure read twice handed a retry no door reaches — the delivery's files
  stay in the tree, which `/implement-task`'s tree check and `door.py --check` refuse, and a rerun
  of a capture is no entry point — and a certification refused again hands a proof-only
  re-delivery, which `--decide` answers as `judge` where the report recommends it. Two judges of
  one choice, each with its own budget, left unstated which answered when both were armed. The
  person asked, the same day, that the budget hold for each initiative. Reversal: a person naming
  as friction arming a grant beside a goal for its judged doors returns a budget to the goal's
  invocation, as a grant it arms over the goal's initiative.
- 2026-11-14 — grounds for R11, read from the `salese2e` session `8ba20ddc` (Siegard 5.104.0),
  which ran under a grant holding `close` with no slug, armed at 13:49Z, and under a harness goal
  the person typed: it closed `intervalo-de-reconciliacao-do-configurator` (`5c2a20b`) and
  `corrigir-limites-do-combo-no-dataset-base` (`50fca30`) and committed a review (`0a22325`)
  without running `grant.py --close` or `--commit` once. Each `closure.md` gave as its reason a
  sentence the session wrote — "the user asked in the goal armed on 2026-11-14 for every open
  initiative to be closed once in that state" — read from an `intake/` file the session wrote the
  same way. The rule lived in the session rules alone, and the reference the closing reads at the
  moment it closes did not name the grant. The session rules' own line named `--close
  <project-root>` with no `--slug`, which a grant naming no initiative refuses. Both closings
  would have been accepted: every task was delivered, proven and reviewed. Reversal: closings
  taken under a grant refused by `--close` and closed anyway by a person's later word, read as
  outnumbering those that held, narrows R11's stop to a report.

- 2026-11-14 — grounds for the invocation as the words and for the mark: the five grants armed
  in `configurator`, `productorder` and `salese2e` on 2026-11-13 (Siegard 5.97.0–5.100.0) carry
  the same pasted paragraph and the same clauses — `--budget 5 --commits --close`, all six doors.
  The paragraph restated the flags in Portuguese, its last sentence restated R3 and SPEC-006 R3,
  and its closing reason, "because the work will be done", named no initiative. The flags were
  already the person's words, typed into a skill closed to the model, and are now what is
  recorded. Five identical invocations recorded under one digest could not say which grant took
  which door, which the reversal R5 reads needs, so each grant is marked with the instant it was
  armed. An invocation with no argument would have armed all six doors with no budget, and is
  refused.

- 2026-11-19 — grounds for arming over a grant that still stands: the person asked that an arming
  replace the standing grant, as the person's own invocation is the one act that can arm and
  nothing a `--clear` first protected was anyone's but the person's. The standing grant is kept in
  `grants-ended.jsonl` as `replaced`, so what it held stays readable; its budget does not carry,
  the new grant's mark and `HEAD` being its own, which a `--clear` and an arming already did.
  Reversal: a reading of the sessions that finds replaced grants re-armed within a stop of what
  they held, a narrowing the person did not mean.

- 2026-11-14 — grounds for arming over a grant R3 has ended: in `configurator` and `salese2e`
  (Siegard 5.100.0), the person armed a grant right after updating from 5.99.1; both were refused
  as "armed already" over a 5.99.1 grant R3 had already ended, with the same doors, budget and
  clauses, and each project took a `--clear` and a second arming, three invocations where one
  sufficed. The record stayed in place because only `--decide`, `--commit`, `--close` and `--read`
  ended it, and none had run since the update.

- 2026-11-13 (run) — the person armed a grant and a goal in two projects and found the grant
  moved nothing in the goal: the goal ends at a stop before any session can ask the script, and
  its own judged budget was zero. R9 and R10 put the ask where the stop is received. The record a
  stop's report was rendered from was never kept — only the report in prose — so R9 keeps it. A
  judged door a grant takes under a goal is the person's, armed as the grant was, and counts
  against the grant's budget alone. The doors a run takes under a grant are held by tests over
  the scripts; the orchestrating entry point's reading of its own file was read by an agent over
  a fixture, not by a consumer's run. Reversal: a goal that continued past a stop the person
  then reverts, or a loop over one task, narrows R10 to `take`.

- 2026-11-13 (last) — the person asked that `doors` default to every entry point, `analyse`
  among them, and kept the budget at zero. A grant that names no door then takes the doors its
  checks leave alone and the commits it holds, and a choice between open doors stops until the
  person writes `--budget n`. Three runs of the skill, each followed by an agent against a clone
  of a consumer, found its text and the script disagreeing — a target picked in silence where
  the skill said a project with several stops, an `--arm` that printed two lines where the report
  quotes the clauses, a `--disarm` that answered `cannot run` where no grant was armed — and the
  requirements above state what each does. Reversal: a default `analyse` whose specification the
  person reverts more than once in ten narrows the default to the five the policy measured.

- 2026-11-13 (later) — the person asked that a grant hold for the project until cleared, that
  every entry point benefit, and that `/siegard-grant` clear it. R1–R3 and R7 follow: the slug is
  optional and the grant ends on a clearing. `analyse` is a door only where the person writes it:
  it is outside the policy that was measured, whose audit found the changes it may make to an
  existing node, which no script decides, in 3 of 156 acts, and the specification it writes is
  disclosed and read afterwards, as under a goal that asks to specify. A grant held by a running
  `/deliver-scope` under a goal, which ends at a stop before a session can ask the script, is not
  decided here: the run reaches the grant where its handoff is relayed, and a run a goal ends is
  resumed from the next invocation. Reversal: a door taken over `analyse` that the person reverts
  narrows `doors` to the entry points the measured policy held.

- 2026-11-13 — grounds for R2, R4 and R7, read from five sales consumers' transcripts, 391 stop
  replies labelled by sonnet agents, 101 of them again against SPEC-006's ladder, and 156 acts
  audited. A policy of five kinds — a recommended door, the one door a stop offers, a commit of the
  route's own files, a closing at state A, a door the ladder singles out — covered 144 of 325
  stops (44.3%) and agreed with the person on 119 of 125 decided (95.2%); with the audited
  crossings made stops, 131 (40.3%), 46% of the stops answered with a decision. A sixth kind, the
  commit of files already pending, was dropped: the audit found a file the person edited, or one
  pending before the session, in 9 of its 13 acts. A proposed discriminator, a node newer than
  the file that contradicts it, covered 17 of 248 contradictions and missed the one that
  motivated it, so a contradiction stays R3's. The measured agreement is of the recommendation the
  stopping skill named; R5 hands a judged choice to the door decider instead, and the
  agreement of its choices is not yet read. Estimator: front matter and replies read by
  agents from each project's session transcripts; the older ten days run an earlier plugin.
  Reversal: a door taken under a grant that the person reverts in more than one of ten, or a
  later audit that finds an act crossing a bound R7 or R8 names, narrows `doors` to the door R4
  takes without the decider.

- 2026-11-19 — grounds for R9's answer at the render and for SPEC-006 R9's writing of the check,
  read from the `configurator` and `inventory` sessions of the 24 hours before, with `productorder`
  holding no decision. Ten decisions of five stops each were rendered; no session ran
  `grant.py --decide` though the session rules' line stood in every context, and the budget stayed
  at zero in all three consumers. Replayed over the records kept beside the reports and then run
  for real over clones at the commit before each stop, with a grant of the plugin's version, all
  five candidates answered `stop`: seven of the eight recommended doors carried no `entry`, which
  `--prepare` writes only on the doors it places under `others`, and a `/plan-work` door after
  `/analyse` was `not checked` because the skeleton was prepared before the plan's slug was named.
  With the entry carried and the check run at the render, two of five answered `judge`, and four of
  five with the one live initiative taken for the slug where the record named none; an
  invocation's `--slug` alone resolved one in eleven of the recommended doors kept in the three
  consumers. The fifth stayed `stop`: a `/reconcile` door is checked over a file set the record
  does not carry, which `trace.py --reconcile-set` prints at 59 files in one of the clones, and
  `door.py --check reconcile` leaves its certifications as `not decided`, so that door is not made
  checkable here. A decision handing one door, with none excluded, is answered `judge` by the code
  where R4's words read `take`; the two are reconciled on 2026-11-21 below. The `inventory` grant
  had been armed under 5.124.0 and the plugin ran 5.125.0, so every stop of the day found a grant
  R3 had ended and nothing had asked it. Reversal: a check run over an inferred initiative that a
  reading of the next commit finds was the wrong one narrows the fallback to the slug the record
  or its invocation names.
- 2026-11-19 (later) — the note R9 prints was first written to fire only where a door of the skill's
  report was absent from the record. Read over the ten records of the day, the configurator's
  23:01 stop and the inventory's 15:05 stop kept every skeleton door under `others` and wrote the
  recommended door beside them with no entry, so no door was absent, no note printed, and the
  recommended door stayed unreadable. The note now fires for any decision whose recommended door
  carries no entry, and names the skeleton's absent doors only where there are some. A recommended
  door that is free text by design, 6 of the 18 kept, is noted too; the note is on standard
  error and only where a grant is armed. Reversal: a reading of the sessions that finds the
  note ignored as noise on free-text doors narrows it to the doors the skeleton handed.
- 2026-11-21 — grounds for R4's lone door, read from every transcript of the `configurator`,
  `inventory` and `productorder` sessions under `sales/` and the handoff records kept beside their
  reports. Seven `judge` lines had been printed in the grants' life, and the door decider was spawned
  after none; five listed one door, and only two (configurator 11:33, inventory 20:17 UTC) were a
  choice. The code answered `judge` over a lone door with none excluded where R4 reads `take`, so a
  decider and a unit of budget were asked for a choice the decider's own definition calls never a
  judgment; the code now follows R4. The line it writes states the fact as it is — the handoff
  hands no other door and its own check accepted — and the criterion stays R4's, `precondition
  unmet`, with no other door left to refuse; being derived, it is not counted by the budget. The two real choices were replayed through the door decider, blind, over clones at the
  commit before each stop: both returned `planejar` (`/plan-work`) on the rung `keeps the route`,
  the door the person then took; the configurator's stopped report carried the stopping step's own
  recommendation, so that agreement is partly circular. Estimator: `judge:` lines read from tool
  results in the session transcripts, spawns from `door-decider` in the Agent inputs; one replay per
  stop. Whether the remaining `judge` is answered is open, and a check holding a stop with an
  unanswered `judge` over two or more doors is not built: two stops in seven days. Reversal: a lone
  door taken under this reading that the person reverts in more than one of ten returns it to the
  stop.
