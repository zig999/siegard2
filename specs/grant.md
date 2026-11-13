---
id: "SPEC-011"
title: The grant
status: proposed
contract_version: spec/1
---

# The grant

## Scope

This specification fixes what the person's recorded grant lets a session do at a stop without
asking, who can record it, what ends it, and the gates a script holds each act to. It binds
`bin/grant.py`, the one script that records, reads and ends a grant and answers every act it is
asked about, `/siegard-grant`, the one skill that arms it, the plugin's `PreToolUse` commit check
where it reads an orchestration log's `decided:` lines, and the session rules' one line that
sends a stop to the script.

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
  beside the armed goal's: the clauses, the initiative's slug, the person's words under a digest,
  the plugin's version, and `HEAD` at arming.
- **Clause** — one of `doors`, `commits`, `close`, each naming what the grant lets the session do.
- **Taking** — doing the act without asking the person: invoking a door, making a commit, closing
  a plan.

## Requirements

### Who arms it

- **R1** — A grant is armed only by the person's own invocation of `/siegard-grant`, a skill closed
  to the model, whose arguments are the person's words. `bin/grant.py --arm` records the words
  verbatim under their digest and refuses to arm where the project holds an armed grant, where the
  slug names no live initiative, or where no clause is named. No other component runs it.
- **R2** — A grant holds at least one clause: `doors`, a list from `plan-work`, `implement-task`,
  `review-change`, `reconcile` and `deliver-scope`, with a budget of judged doors, a whole number;
  `commits`, which lets a session commit what the route wrote; `close`, the person's reason for
  closing the initiative, in their words, which lets a session close it where R7 holds. Every
  other entry point — `/analyse` among them — is outside `doors` whatever the person writes.

### What ends it

- **R3** — A grant ends when the person disarms it, when the plugin's version is not the one it was
  armed under — the rules a grant took are those of its version — and when the initiative it
  names holds a `closure.md`. An ended grant is appended, with its reason, to the ended log beside
  it, and takes nothing.

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
  carrying the rung it named and the grant's digest among its deciding facts. The budget left is
  the grant's budget less the judged `decided:` lines the initiative's log gained since the grant
  armed, and a judged choice met with it spent is `stop`. «Each door taken is one line of the
  run's orchestration log, `decided: <door> — <criterion> — <deciding fact>`, and a door R3
  reserves is never taken.» (SPEC-006 R7)
- **R6** — The plugin's `PreToolUse` commit check reads an armed grant that names the log's
  initiative as it reads an armed goal, for a judged `decided:` line: a line over a rung of the
  ladder is taken where a goal or a grant names the initiative, and refused where neither does.

### The gates

- **R7** — `bin/grant.py --commit`, over the paths a commit names, answers `accepts` only where the
  grant holds `commits` and every path is one the route writes — under the initiative's delivery
  root, its work root, the telemetry root, `siegard-reconcile/`, the trace, or named by a record
  of the initiative — and none is outside the project, a path of `siegard.json`, a declared
  standard, `CLAUDE.md`, a file that holds credentials, a `closure.md` while the close clause does
  not hold, or a specification file the commit modifies where `HEAD` already holds it, beyond its
  decision log. A path that holds a change no record of the initiative accounts for is `refuses`.
  `bin/grant.py --close` answers `accepts` only where the grant holds `close` and the goal
  computation over the initiative, read from the grant's `HEAD`, finds every task delivered,
  proven and reviewed, no criterion unmet that no covered review answers, and a sound
  specification; the closure's reason is the grant's words, never the session's.
- **R8** — Whatever the clauses say, a grant takes no push, no branch and no history rewrite; no
  edit of a file by the session outside a skill; no action in another project's tree and no command
  the project's registry does not declare; nothing a door's own check refuses; and no choice R3 of
  SPEC-006 reserves to the person.

## Validation required before acceptance

1. Tests hold `grant.py --arm` to R1, R2: a recorded grant carries the words verbatim under a
   digest, a second arming, an unknown slug, no clause and an entry point outside the list are
   each refused, and a plugin version change ends the grant under R3.
2. Tests hold `grant.py --decide` to R4 and R5 over handoff records: a `settles` decision is
   `stop`; one door left after a refusal is `take`; a recommended door that is accepted beside an
   open door is `judge` with the budget left; a spent budget, a door outside the list and an
   unchecked door are `stop`.
3. A test holds the commit check to R6 over a fixture log: a judged line with a grant armed is
   taken, and with neither a goal nor a grant it is refused.
4. Tests hold `grant.py --commit` and `--close` to R7 and R8 over fixture repositories, one refusal
   per bound the requirement names, and one acceptance of a commit that names only paths a record
   of the initiative writes.
5. A test holds `/siegard-grant` closed to the model and the session rules' line to the script.

## Readings

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
