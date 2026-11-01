---
id: "SPEC-006"
title: The handoff
status: proposed
contract_version: spec/1
---

# The handoff

## Scope

This specification fixes the form of the last message a skill's invocation leaves to a person —
its report, or the stop that ends it early — and when that message names one door over the
others. It binds every skill that reports, and the two orchestrating entry points that relay
another skill's report.

It decides what the message opens with, what it may recommend and on what grounds, what it never
recommends, and where a recommendation is recorded so that it can be counted.

Grounds: one consumer session on 2026-10-05 and 2026-10-06, Siegard 5.2.0, read from its
transcript. Its 26 long final messages ran from 1,950 to 24,343 characters, and in 24 of them the
last decision word sat past 78% of the text. The person asked 7 questions right after a report —
the status, what had to be done, the recommendation, whether anything blocked, whether the
initiative was over, what an enumerated "8 deliveries" were, and the detail of a risk handed as
an observation. Of the 10 skill reports that handed doors, 6 handed doors only the person could
choose — the ask, a review of a decided diff — 2 handed doors a fact on disk decided, 2 handed one
door such a fact excluded, and 1 handed two readings of the same evidence. The agent recommended
on 4 doors when asked: the 3 a fact decided held; the 1 over two readings was wrong, and a binder
refused the corrective increment it led to. One `/plan-work` invocation ran only to stop at a
precondition the report before it already held.

Grounds for the form in R1, the excluded door and the judged ladder in R2, R3 as it now reads, and
R6: one consumer,
`newcatalog`, Siegard 5.19.0, four sessions read from their transcripts on 2026-10-13. Of 14
handoffs that handed numbered doors, 8 said in so many words that no door was recommended or that
the session had no preference, and 1 recommended one unasked; the person then asked which door
was recommended 11 times, and answered 6 lists with a bare number. Of the 8, 2 handed a door its
own entry point would have refused beside the one that remained, and 2 handed only doors every one
of which a refusal or a rule excluded. The wording came from the skills' own sentences — "recommend
neither", "no preference", "names none" — rendered into the session's language as written. Asked,
the session recommended anyway, by judgment and unrecorded: of four such recommendations read
across this consumer and the 2026-10-05 one, two held and two were wrong — one reverted two hours
later, one over two readings of one piece of evidence that a binder then refused. The two wrong
ones fell on a decision about cost and on two readings; the ladder takes the first and R3 keeps
the second, with a contradiction and a finding's worth, where the blind decider of SPEC-001 R13
and the reviewers' evidence-only returns already hold.

### Decided elsewhere, deliberately not restated here

- When the plugin's Stop hook runs `--check` over the message a session stops on, what it records,
  and when it blocks — `specs/goal.md` (SPEC-008 R15).
- What each skill reports and in which order — that skill's own file.
- What stops a skill — that skill's own file; a contradiction between scope and specification
  is a stop only a person settles — `specs/minimal-documentation.md` (SPEC-001 R13).
- What a reviewer returns: evidence, never a verdict, a severity or a ranking — the reviewing
  agents' own files.

## Definitions

- **Handoff** — the last message of a skill's invocation, where control returns to a person: its
  report, or a stop that ends the run early. A spawned agent's return is never a handoff.
- **Door** — an act the handoff hands the person, an invocation ready to paste among them.
- **Owed act** — a door without which a named step refuses to run; the handoff names that step.
- **Offered act** — any other door.
- **Criterion** — the closed reason a recommendation is made on: for a derived recommendation one
  of `precondition unmet`, `rule violated`, `already done`, `reading paid twice`; for a judged
  one, a rung of the ladder — `keeps the route`, `serves the stated goal`, `can be undone`,
  `costs less`.
- **Derived recommendation** — one a fact on disk decides.
- **Judged recommendation** — one no fact decides, made by the ladder over a choice of cost or of
  reading the ask.

## Requirements

### What the handoff opens with

- **R1** — A handoff opens with what needs the person, and explains after. The opening holds, in this order, omitting a part that is empty: the state in one line; what this report withdraws from what the same invocation said earlier; each pending decision with its doors, what each door does, and what stays as it is if none is taken; each owed act with its invocation and the step it unblocks, kept apart from every offered one; neither list is ranked, and an order no command printed is a preference. Each item of the opening says what it is for the person, in the session's own plain words — what must be done before a named step runs, what may be done and nothing waits on, what only the person decides, what is suggested and why — and never in a word of this framework's: a reader who has never opened a skill's file reads the opening whole. Where the report recommends a door, the opening says so and why, before any explanation. The report then follows the order the skill's own file states, in the session's language, each framework term explained once where it first appears, and every command output, note and log entry quoted verbatim and untranslated. The opening's form is one block per pending decision and per owed act, in that order, each omitting a line that is empty: the door recommended, with why in one sentence and the fact that would change it, where R2 names one — otherwise that the choice is the person's own decision, and what would settle it; each other door, in the order a command printed it, with what it does and what it leaves as it is; what stays as it is if no door is taken, which for an owed act is the step that refuses to run; and last the invocation ready to paste, the one line where a skill's name appears. A cost or a risk is stated only as a command printed it.

### What a handoff recommends

- **R2** — A recommendation names the door, the criterion, the deciding fact and the reversing fact; without all four, none is named. A derived recommendation's criterion is one of four and no other: `precondition unmet`, the door's own entry point refuses its inputs as the tree stands; `rule violated`, the door breaks a rule this framework states; `already done`, the door's work is already in the tree; `reading paid twice`, the same file read by two judgments, where of two readings over the same files the one owed once is named over the one paid twice — two invocations over different files are each paid once, and their order is a decision about cost. In the handoff the four are carried as sentences in the session's plain words — the door, why it, what on disk says so, what would change it — and the criterion's name is written as it reads here only in the log line R5 states; a label, a field name or the criterion's English name in the prose is the record showing through. A derived recommendation's deciding fact and reversing fact are each a fact on disk, named by path or quoted. A door excluded on one of the four grounds is said to be excluded, beside it and with its fact, and where one door remains it is the door recommended: a handoff that hands an excluded door as though it were open has failed to apply R2. Where no ground excludes a door and the choice left is one of cost or of reading the ask, the recommendation is judged: its criterion is the first rung of this ladder that separates the doors, and no other — `keeps the route`, the door holds to this framework's route, a step done by hand that this framework itself prescribes counting as the route; `serves the stated goal`, the door reaches a goal the ask or its intake states, quoted verbatim, and without the quotation this rung does not apply; `can be undone`, the door can be reversed where the other cannot; `costs less`, by a cost a command printed. Its deciding fact is what the rung read — the step this framework prescribes, the quotation, what reverses the door, or the printed figure — its reversing fact what would move the choice to another door, and the handoff says the recommendation is a judgment. One ladder serves every handoff; a skill applies it and never states another.
- **R3** — No recommendation is made over a scope and a specification that contradict, over two readings of one piece of evidence, or over whether a finding matters or what route it deserves. Each is the person's, and a handoff hands its doors and names none. A finding's worth the person decided in advance, as the findings policy a goal condition states, is applied by its class and never judged. It says so in the person's words: that the choice is the person's own decision, what each door assumes is true, and what on disk or in the person's own answer would settle it — never a bare absence of a recommendation, which reads as an answer withheld.

### What stops

- **R4** — A finding stops nothing. A handoff names a stop only where the skill's own file names one, and names it as a stop. Where a handoff says a step may proceed, it lists the checks it ran and their output verbatim.
- **R6** — Where every door a handoff hands is excluded, by its entry point's refusal or by a rule this framework states, the opening says no door follows this framework's route, names for each door the refusal or the rule as a fact on disk, and recommends none; it names the route that recovers from work done outside the framework where one exists, and says what the person does then is outside this framework's route.

### What a goal takes

- **R7** — Under a goal condition naming the orchestrating route, the orchestrating entry point takes the door a derived recommendation names where that door is an entry point the route invokes, and takes the door a judged choice leaves only as the door decider returned it, blind to the condition and while the condition's budget of judged doors is not spent. Each door taken is one line of the run's orchestration log, `decided: <door> — <criterion> — <deciding fact>`, and a door R3 reserves is never taken. Outside a goal, a session takes a derived recommendation only where the person's own message says to proceed, `bin/door.py --check` accepts the door and every other door is excluded, and the door taken is recorded the same way: one `decided:` line in the orchestration log of the run it continues where one exists, and otherwise in the body of the commit that follows it.

### Where a recommendation is recorded

- **R5** — An orchestrating entry point that relays a report carrying a recommendation writes it to the run's orchestration log as one line, `recommended: <door> — <criterion> — <deciding fact>`. A recommendation made where no orchestration log exists is in the report alone, and nothing counts it. The criterion's name says whether the recommendation was derived or judged; the line carries nothing else to say it.

### What a handoff is made from

- **R8** — A handoff that hands a person a decision is rendered by `bin/handoff.py --render` from a record, never composed as free text. The record carries `kind`, `language`, `state` in one line, and `withdraws` where the handoff withdraws what the same invocation said earlier; kind `decision` carries `decisions` — an owed act among them, its door the act and its `if_none` the step that refuses to run — each with its `ask`, either the door `recommended` — its `door`, `why`, `reverses_if` and `reply_word` — or, where R3 or R6 leaves the choice to the person, `settles`, what would settle it, then the `others`, each with its `reply_word` and `what_it_does`, `if_none`, what stays as it is if no door is taken, and optionally the `invocation` ready to paste; and `report`, where one exists, is the path of the full report on disk, which holds the pending items, commit hashes, measurements and command output the opening does not. The rendered handoff holds its state within 200 characters, each decision's block within 600 and the whole message within 1500; carries no term of the closed list `schemas/handoff.json` holds outside the line ready to paste and a state R10 reads from a script; gives every door a reply word no other door in the handoff uses; and is written in the language the record names, whose few fixed words the schema holds and whose prose the script never translates. A status answer or a design conversation is kind `report`, not a stop: `state` and the `report` path, an inline `body`, or both, with no ceiling. A handoff written as free text is held by `bin/handoff.py --check` to what is decidable without the record: no term of that list in its first 450 characters, and, where it hands a decision, a length within 1500 characters and a word of recommendation or of the person's own decision within those 450.

- **R9** — Whether a door's own entry point refuses its inputs as the tree stands is a script's answer, `bin/door.py --check`, read from disk and git alone: its first line is `accepts` or `refuses`, each refusal follows with its fact, and a refusal the entry point's file states that no script decides is listed as not decided, never answered. A door the check refuses is excluded on `precondition unmet`, its deciding fact the `refused:` line; a door it accepts is not thereby recommended.

- **R10** — The state a handoff opens with is a script's line, never the session's. `bin/handoff.py --prepare` prints the record's skeleton for the skill and the inputs it names, with `state` written and `state_from` naming the script it is the line of: the first line `goal.py --state` answers where a goal is armed through the framework, else the segment `progress.py` prints for the initiative named, else the line it prints for the project, else the fixed words the schema holds for a project with nothing live — quoted as the script printed it, cut to the state ceiling, never translated and never read for the closed list of terms. The skeleton's doors are the invocations the skill's own report names ready to paste, each marked with the first line `bin/door.py --check` prints for it and its `refused:` facts, or as not checked where no script decides that door or an input it takes is not named; none is marked recommended, and the report's path lies outside the tree every entry point holds to `git status`. A record of kind `decision` carries `state_from`, and `--render` refuses it where `state` differs from what that script prints when it renders, where its door recommended is one the check refuses, and where a recommendation's `why` or `reverses_if` is empty.

- **R11** — A report's short form is held as an opening is. Where kind `report` carries a `report` path, its `body` is the short form above the full report, and `bin/handoff.py --render` refuses it where it carries a term of the closed list anywhere; where it carries no path, its first 450 characters are held so. A body that recommends carries the fixed words the schema holds for the reversing fact in the record's language, followed by that fact, or `--render` refuses it. A door a report hands is handed whole: where its entry point requires a name the tree decides is free, the script that composes the door prints one, and the report never asks the person for it.

## Validation required before acceptance

1. Every skill whose file states a report cites R1 beside it.
   A test holds `bin/door.py --check` to R9 over fixture repositories: one door accepted and one refused for each cause it decides, and every refusal an entry point's file states that no script decides listed as `not decided`.
2. Telemetry counts the `recommended:` lines of every orchestration log under the delivery
   root — each initiative's own, and one an orchestrating entry point left at the delivery root
   itself, read under the initiative its landing commit names — by criterion, and names each
   line that does not parse, a `recommended:` that does not open its line among them — and the
   log `/adopt-scope` keeps under `siegard-survey/<slug>/`, read under that slug; it computes
   nothing about which door was taken. It counts the `decided:` lines R7 states the
   same way, apart from the `recommended:` ones.
3. A consumer initiative run under this specification is read for three things. Each handoff
   that hands a door R2 excludes and carries no recommendation is a failure to apply R2, never
   grounds to withdraw it. For each `recommended:` line a person reads its `next_commit` and
   says whether that door was taken; judged recommendations read as not taken outnumbering
   those read as taken narrows R2 back to derived recommendations alone. And telemetry's
      `handoffs.questions` — every human turn in the window holding a `?`, a continuation summary
   excepted and a paste counted as typed — is reported beside each reading against its baseline
   in its own unit, and reverses nothing: 17 in 56 human turns over the eternal session
   `0775f0fa` (2026-10-05T15:26:28Z..2026-10-06T13:54:56Z, Siegard 5.2.0); 15 in 62 over
   `newcatalog`'s 2026-10-13T11:30:19Z..15:18:41Z, the window of its
   `siegard/telemetry/20261013T151841Z.json`, and 52 in 226 over
   2026-10-10T00:00Z..2026-10-13T15:18:41Z — each `telemetry.read_session` summed over that
   consumer's transcripts. The readings the grounds state — 7 clarifying questions right after
   26 reports on 2026-10-05, 11 asking for the recommendation after 14 handoffs that handed
   doors on 2026-10-13 — are a person's, read from the transcript; a later reading in that unit
   is compared to them, never to the count.
4. Telemetry reads every assistant message that precedes a human turn in its window with the
   functions `bin/handoff.py --check` runs — one definition — and counts how many there are, how
   many hand a decision, how many of those exceed the message ceiling, how many carry a term of
   the closed list in their first 450 characters, how many carry a word of recommendation, and
   the median position of the first decision word as a share of the text; it names the longest
   message and the one whose first decision word sits latest, by session and instant, so a reader
   can open them, and refuses nothing. Each reading is set beside the baseline of 2026-10-31
   below, in its own unit; a later reading where the four proportions have not moved toward the
   ceiling under R8 is grounds to read why the record is not being filled, never to raise the
   ceiling.
5. A test holds `bin/handoff.py --prepare` to R10 over fixture repositories: the state is the
   goal's first line where a goal is armed, the initiative's progress segment where a slug is
   named, the project's line where none is, and the fixed words where nothing is live; a door
   the check accepts and one it refuses are each marked with that answer and the refused fact,
   a door no script decides is marked not checked, and none is marked recommended; the skeleton
   fails the schema only on the fields the model fills. The same test holds `--render` refusing
   a decision record without `state_from`, one whose state differs from what the script prints
   now, one recommending a door the check refuses, and one whose `why` or `reverses_if` is
   empty; and every skill named in `bin/handoff.py`'s use — `deliver-scope`, `adopt-scope`, `plan-work`,
   `implement-task`, `review-change`, `reconcile`, `analyse`, `siegard-goal`, `siegard-status` —
   names `--prepare` and `--render` beside its report and cites R10.
6. The closed list holds a framework word that is also plain English — `stands`, `nowhere`,
   `owed`, `offered` — as a term only backticked or inside a framework phrase in English prose,
   and as a whole word in prose of any other language; a test holds both halves, and the
   Portuguese fixture that carried those words still carries them.

7. A test holds `bin/handoff.py --render` to R11: a report body above a path that carries a
   term of the closed list past its first 450 characters is refused, a body with no path that
   carries one only past them renders, and a body that recommends without the reversing words
   of its language is refused; and a test holds `bin/trace.py --check --reconcile-set` printing a
   `free slug:` line that names no record or returns directory under `siegard-reconcile/`.

## Readings

- 2026-11-01 — grounds for R11: the first `/siegard-status` short form rendered under 5.44.0 in
  `salese2e` passed `--render` while carrying "slug", the drift class names "moved", "proof"
  and "code", and "a leitura devida" — `owed` translated — and closed on "falta apenas você
  escolher o slug" with no fact that would change the suggestion. `--render` read the state and
  the decisions' prose for the list but never the body, the list held the class names nowhere,
  and the status skill left the slug a slot for the person. `code` stays off the list: it is also
  the plain word in "Claude Code".

- 2026-10-31 — grounds for R10 and the narrowed list: the handoffs read for the R8 baseline
  wrote their state line in the session's own words, and it was wrong more than once — "no next
  phase" where one existed, "nothing pending" where disk held pending work, a success mark set
  before the check that would have shown it — and recommended doors their own entry point
  refused. R8's record existed, but no skill produced it: only the session rules asked for it, so
  a session that wrote free text changed nothing. R10 moves the state and the doors' marks into
  the skeleton a script writes, and every skill that reports runs it. The same reading found
  `stands`, `nowhere`, `owed` and `offered` hit as framework terms in English prose where they
  were plain English; the list keeps them as terms backticked, inside a framework phrase, or in
  prose of another language, where a word of English in a session that is not English is the
  framework showing through. The four figures of the 2026-10-31 baseline were read under the
  wider list; a later reading under this one is compared to them knowing that.

- 2026-10-31 — baseline for R8: 251 handoffs read from the session transcripts of four consumers
  under Siegard 5.34–5.42, over four days. 62% were longer than 1500 characters; 33% carried a
  framework term — state A/B, stands, nowhere, binder, decisor, juiz, pathspec, rebind,
  `--replace`, a `*.py` script name, unstated, substrate — inside their first 450 characters; the
  median first decision word sat at 39% of the text; 42% carried no word of recommendation or
  decision at all. Some mixed English into a Portuguese session, which no script decides; the same
  pending-items block repeated across consecutive handoffs, and commit hashes and measurement
  lines padded the body. R1 and R2 held these by prompt alone through three measured rounds; R8
  moves the opening into a record a script renders, and Validation item 4 is the measurement.

- 2026-10-25 — grounds for R7: every human turn of 15 `/goal` sessions of `newcatalog`,
  `productcatalog` and `productorder` (2026-10-13..25), one coder
  (`temp/20261025-goal-autonomy/decisions.md` in the generator): where a handed choice carried a
  recommendation, the person took it — derived 42/42, judged 49/56; of the 6 judged not taken,
  3 were a closure, a push and a standard deviation, which no goal takes. The sessions took 19
  reserved decisions themselves, 3 reversing their own refusal minutes earlier — the judgment R7
  hands a decider blind to the condition.

- 2026-10-07 — not yet read: no initiative has run end to end through `/deliver-scope` or
  `/adopt-scope` under 5.5.0 or later, so no orchestration log holds a `recommended:` line. The
  numerator is `telemetry.py`'s `recommendations` count by criterion; the denominator — handoffs
  that hand doors — is read from the transcript until telemetry counts it. Verdict pending.
- 2026-10-08 — read over two `/deliver-scope` runs in the eternal consumer, `entity-edit-backend`
  and `entity-edit-frontend` (sources: the two `siegard-delivery/*/orchestration.md` and sessions
  `2c28fd42`, `d4d868ba`): five handoffs handed doors, zero `recommended:` lines. By the letter of
  Validation item 3 that is 0/5, below two per ten; the reversal is not taken, because all five
  handed doors R3 names — the ask or its scope, a contradiction, a finding's worth, a decision
  about cost or standard — so R2 applied to none and stands unexercised. Verdict pending; the
  criterion that reverses it is a handoff handing a door R2 decides — precondition unmet, rule
  violated, already done, reading paid twice — with no `recommended:` line.
- 2026-10-13 — read over `newcatalog`'s four sessions under 5.19.0 (grounds above): 14 handoffs
  handed doors, 0 `recommended:` lines; none of the 14 was relayed by an orchestrating entry
  point, so R5 counted nothing by design. 2 handed a door R2 excludes with no recommendation —
  the failure the last sentence of R2 now names — and the reversal of item 3 is not taken over
  them, because R2 not applied is not R2 failing. Verdict pending.
- 2026-10-14 — the 22 orchestration logs of three consumers held no line opening
  `recommended:`. One recommendation was written: `newcatalog`'s
  `siegard/delivery/orchestration.md` line 92, appended to the end of a step's sentence, in a log
  at the delivery root itself that three initiatives shared — telemetry read only logs at an
  initiative's root, and skipped a line not opening with the word. Both are now read, and the
  line is named as one that does not parse. The criterion's name was not what kept lines from
  being written: the orchestrator runs in the session that wrote the report, and wrote a valid
  one. Open: `/adopt-scope` writes its log at `siegard-survey/<slug>/`, which telemetry does not
  read; R5 binds it, and under the reading that constrains more its lines are owed a count.
- 2026-11-01 — the open item above is closed: telemetry reads `siegard-survey/*/orchestration.md`
  beside the delivery root's logs, and `/adopt-scope` hands its report through `--prepare` and
  `--render` (R10, validation 5).
