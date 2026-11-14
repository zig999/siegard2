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
otherwise hand back: it arms the same two things a goal condition arms for a judged choice — the
taking, and its budget — over a handoff's doors, a run's commits and the closing of a plan,
outside any goal. It widens no bound of SPEC-006 R3 or of the session rules: a choice the person
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
  and refuses to arm where the project holds an armed grant that still stands, where the
  invocation names nothing, where a slug the person names is no live initiative, or where no clause is named.
  No other component runs it. The person ends it with `/siegard-grant --clear`, which runs
  `bin/grant.py --disarm`, and the project then behaves as it did before the grant; where none is
  armed it says so and refuses nothing.

- **R2** — A grant holds at least one clause: `doors`, a list from `plan-work`, `implement-task`,
  `review-change`, `reconcile`, `deliver-scope` and `analyse`, which is all six where the person
  names none, with a budget of judged doors, a whole number, which is zero where the person names
  none; `commits`, which lets a session commit what the route wrote; `close`, which lets a session
  close an initiative where R7 holds, the grant's words being the reason it is closed under. The
  person narrows `doors` by naming them, and `none` leaves it empty for a grant of commits or of a
  closing alone; no other entry point is ever in it. A grant names no initiative unless the person
  gives a slug, and without one it covers every live initiative of the project. What `--arm`
  recorded is printed: the initiative or the project, the doors, the budget, the clauses, the words'
  digest, the mark and the plugin's version.

### What ends it

- **R3** — A grant ends when the person clears it, when the plugin's version is not the one it was
  armed under — the rules a grant took are those of its version — and, where it names an initiative,
  when that initiative holds a `closure.md`. An ended grant is appended, with its reason, to the
  ended log beside it, and takes nothing. An arming over a grant whose record is still in place but
  that has ended so appends it to that log, says that it ended and why, and arms; nothing is
  appended where the arming is refused on another ground.

### What it lets a stop do

- **R4** — `bin/grant.py --decide`, over the record a stop's handoff was rendered from, answers
  each decision with one of three lines: `stop`, `take` or `judge`. A decision that carries
  `settles` is `stop`: the choice is the person's. Of the doors a decision hands, the ones whose
  check answered `refuses` are excluded; where exactly one door remains and its entry point is in
  the grant's `doors` the answer is `take`, the criterion `precondition unmet`; where the
  recommended door's check accepted and its entry point is in the grant's `doors` the answer is
  `judge`, with the doors, the budget left and the facts the decider reads, and where no door
  qualifies it is `stop`. A door whose check was not run is never taken.
- **R5** — `judge` is answered by the door decider, blind to the grant and within its budget, as a
  goal condition's judged choice is answered; the door it names is taken, one `decided:` line
  carrying the rung it named and the grant's mark among its deciding facts. The budget left is
  the grant's budget less the judged `decided:` lines the logs it covers gained since the grant
  armed, and a judged choice met with it spent is `stop`. «Each door taken is one line of the
  run's orchestration log, `decided: <door> — <criterion> — <deciding fact>`, and a door R3
  reserves is never taken.» (SPEC-006 R7)
- **R6** — The plugin's `PreToolUse` commit check reads an armed grant that names the log's
  initiative, or names none, as it reads an armed goal, for a judged `decided:` line: a line over a
  rung of the ladder is taken where a goal or a grant names the initiative, and refused where
  neither does.

### Where a run meets it

- **R9** — `bin/handoff.py --render` keeps the record it rendered, as JSON beside the report its `report` names, so that the run that receives a stop can ask the grant over the doors it handed. `bin/grant.py --decide --latest <skill> --after <commit>` answers over the newest record kept for that skill after that commit, and refuses where none was, so that a run never answers over the report of an earlier stop.
- **R10** — Where the project holds an armed grant, the orchestrating entry point asks `bin/grant.py --decide` over the report of a step that stopped, before it ends the run: a `take` or a `judge` it answers is a door the run takes and goes on with, under a goal as without one, and a `stop` leaves the stop as it was. The same door over the same task is taken once in a run. A `decided:` line a grant took ends `(grant sha256 <digest>)`; the grant's budget counts it and the goal's budget does not. The digest is the grant's mark, and the budget counts only the lines that carry its own.

### The gates

- **R7** — `bin/grant.py --commit`, over the paths a commit names, answers `accepts` only where the
  grant holds `commits` and every path is one the route writes — under the delivery root or the work
  root of an initiative the grant covers, the telemetry root, `siegard-reconcile/`, the trace, or
  named by a record of such an initiative — and none is outside the project, a path of `siegard.json`,
  a declared standard, `CLAUDE.md`, a file that holds credentials, a `closure.md` while the close
  clause does not hold, or a specification file the commit modifies where `HEAD` already holds it,
  beyond its decision log. A path that holds a change no record of a covered initiative accounts for
  is `refuses`. `bin/grant.py --close`, over one initiative the grant covers, answers `accepts` only
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
   its flags alone arms, and a second arming, an invocation that names nothing, an unknown slug, no clause and an entry point outside the
   list are each refused, a grant without a slug covers every live initiative, a grant that names
   no door holds all six, `none` holds none, `--disarm` returns the project to no grant and with
   none armed says so, and a plugin version change, or a closure of the initiative a grant names,
   ends it under R3; an arming over a grant so ended ends it in the log, says so and arms, and an
   arming refused on another ground leaves it in place.
2. Tests hold `grant.py --decide` to R4 and R5 over handoff records: a `settles` decision is
   `stop`; one door left after a refusal is `take`; a recommended door that is accepted beside an
   open door is `judge` with the budget left; a spent budget, a door outside the list and an
   unchecked door are `stop`.
3. A test holds the commit check to R6 over a fixture log: a judged line with a grant armed is
   taken, and with neither a goal nor a grant it is refused.
4. Tests hold `grant.py --commit` and `--close` to R7 and R8 over fixture repositories, one refusal
   per bound the requirement names, one acceptance of a commit that names only paths a record
   of a covered initiative writes, and a grant without a slug accepting the paths of any live
   initiative and answering `--close` only over the initiative it is asked about.
5. A test holds `/siegard-grant` closed to the model and the session rules' line to the script.
6. For R9 and R10: a test holds `handoff.py --render` to keeping the record beside its report and
   `grant.py --decide --latest` to reading the newest one of a skill; a test holds `goal.py --state`
   to counting a judged line that ends `(grant sha256 …)` under no goal's budget and the grant's
   budget to counting only those that carry its digest; and `/deliver-scope`'s file states the
   requirement in the words above — `tests/test_grant.py`, `tests/test_handoff.py`,
   `tests/test_goal.py` and `tests/test_skill_contract.py` prove each.

## Readings

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
