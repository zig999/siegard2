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

Grounds for the relation R1 and R8 require: two consumers, `configurator` and `salese2e`,
Siegard 5.100.0, read from their transcripts over the 12 hours to 2026-11-14T10:41Z. Of the 11
distinct decision blocks `bin/handoff.py --render` printed, 8 handed steps of one route — `planejar`
beside `conciliar` where the second read "before planning", `analisar` beside `entregar` where the
second read "leaves that one for later" — printed as bullets beside doors that exclude one another,
under a "1." that a lone decision carries. The person answered "1 primeiro", a bare "2", and "qual o
recomendado?" after a block that had printed "Decisão sua". A report the model wrote as free text
listed seven items of five natures — a finding to read, a partial criterion, a decision, a rule to
review, a drift count — as one bullet list; that part is decided in the report's own record, not here.

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

- **R1** — A handoff opens with what needs the person, and explains after. The opening holds, in this order, omitting a part that is empty: what this report withdraws from what the same invocation said earlier; each pending decision with its doors, what each door does, and what stays as it is if none is taken; each owed act with its invocation and the step it unblocks, kept apart from every offered one; neither list is ranked, and an order no command printed is a preference. The state in one line, where a script printed it, follows what the person reads in their own words, above the path of the full report: it is the script's line, quoted as printed, and context for the opening rather than its first words; a count of open lines that leads it stands apart, first, in the person's words; a state the session wrote stays first; and where nothing precedes it, the state opens the message. Each item of the opening says what it is for the person, in the session's own plain words — what must be done before a named step runs, what may be done and nothing waits on, what only the person decides, what is suggested and why — and never in a word of this framework's: a reader who has never opened a skill's file reads the opening whole. Where the report recommends a door, the opening says so and why, before any explanation. The report then follows the order the skill's own file states, in the session's language, each framework term explained once where it first appears, and every command output, note and log entry quoted verbatim and untranslated. The opening's form is one block per pending decision and per owed act, in that order, each omitting a line that is empty: the door recommended, with why in one sentence and the fact that would change it, where R2 names one — otherwise that the choice is the person's own decision, and what would settle it; each other door, in the order a command printed it, with what it does and what it leaves as it is; what stays as it is if no door is taken, which for an owed act is the step that refuses to run; and last the invocation ready to paste, the one line where a skill's name appears. A decision that hands two doors or more says how the doors relate, in one line directly above them: that the person takes one, that the doors are the steps of one path, all taken in the order listed, or that each is taken on its own and any or all may be; the doors of a path are numbered by step. Only a door is a bullet: the person's own choice and what stays as it is if no door is taken are lines of their own. A lone decision is not numbered, since a lone number reads as the first step of a sequence, and several are counted before the first. A cost or a risk is stated only as a command printed it.

### What a handoff recommends

- **R2** — A recommendation names the door, the criterion, the deciding fact and the reversing fact; without all four, none is named. A derived recommendation's criterion is one of four and no other: `precondition unmet`, the door's own entry point refuses its inputs as the tree stands; `rule violated`, the door breaks a rule this framework states; `already done`, the door's work is already in the tree; `reading paid twice`, the same file read by two judgments, where of two readings over the same files the one owed once is named over the one paid twice — two invocations over different files are each paid once, and their order is a decision about cost. In the handoff the four are carried as sentences in the session's plain words — the door, why it, what on disk says so, what would change it — and the criterion's name is written as it reads here only in the log line R5 states; a label, a field name or the criterion's English name in the prose is the record showing through. A derived recommendation's deciding fact and reversing fact are each a fact on disk, named by path or quoted. A door excluded on one of the four grounds is said to be excluded, beside it and with its fact, and where one door remains it is the door recommended: a handoff that hands an excluded door as though it were open has failed to apply R2. Where no ground excludes a door and the choice left is one of cost or of reading the ask, the recommendation is judged: its criterion is the first rung of this ladder that separates the doors, and no other — `keeps the route`, the door holds to this framework's route, a step done by hand that this framework itself prescribes counting as the route; `serves the stated goal`, the door reaches a goal the ask or its intake states, quoted verbatim, and without the quotation this rung does not apply; `can be undone`, the door can be reversed where the other cannot; `costs less`, by a cost a command printed. Its deciding fact is what the rung read — the step this framework prescribes, the quotation, what reverses the door, or the printed figure — its reversing fact what would move the choice to another door, and the handoff says the recommendation is a judgment. One ladder serves every handoff; a skill applies it and never states another.
- **R3** — No recommendation is made over a scope and a specification that contradict, over two readings of one piece of evidence, or over whether a finding matters or what route it deserves. Each is the person's, and a handoff hands its doors and names none. The record names which of the three leaves the choice to the person, in `settles_by` — `contradiction`, `two-readings` or `finding-worth`, or `all-excluded` where R6 holds — and `bin/handoff.py --render` refuses one that names none of the four: a choice of cost, of order or of reading the ask is none of them, and its door is recommended as a judgment. A choice left to the person as `finding-worth` names in `finding` the review record that holds the finding, and `--render` refuses it where that record holds no finding: such a choice is another of the four, or a choice its door is recommended over. The record named holds a finding where its frontmatter carries `findings`, or a reconciliation's `notes` owed a route; a relative path is read from the project root the record's `state_from` names. A finding's worth the person decided in advance, as the findings policy a goal condition states, is applied by its class and never judged. It says so in the person's words: that the choice is the person's own decision, what each door assumes is true, and what on disk or in the person's own answer would settle it — never a bare absence of a recommendation, which reads as an answer withheld.

### What stops

- **R4** — A finding stops nothing. A handoff names a stop only where the skill's own file names one, and names it as a stop. Where a handoff says a step may proceed, it lists the checks it ran and their output verbatim.
- **R6** — Where every door a handoff hands is excluded, by its entry point's refusal or by a rule this framework states, the opening says no door follows this framework's route, names for each door the refusal or the rule as a fact on disk, and recommends none; it names the route that recovers from work done outside the framework where one exists, and says what the person does then is outside this framework's route. A door whose check accepts is not excluded: `--render` refuses `all-excluded` beside one, so the choice is recommended — the step the session means, a door as a judgment or a step that is no door with its command in `invocation` — or carries another of the reserved classes; the rule that excludes a door is one `bin/door.py --check` states, and a door it accepts, rechecked as the tree stands and over an initiative the record names, counts as not excluded.

### What a goal takes

- **R7** — The orchestrating entry point takes the door a derived recommendation names where that door is an entry point the route invokes and `bin/door.py --check` accepts it — under a goal condition naming the route and under the person's own ask that invoked the route alike, the same door over the same task once in one run — and takes the door a judged choice leaves only under a grant the person armed, as the door decider returned it, blind to any goal condition and to the grant, while the grant's budget of judged doors for that initiative is not spent (SPEC-011). Each door taken is one line of the run's orchestration log, `decided: <door> — <criterion> — <deciding fact>`, and a door R3 reserves is never taken. Outside a goal, a session takes a derived recommendation only where the person's own message says to proceed, `bin/door.py --check` accepts the door and every other door is excluded, and the door taken is recorded the same way: one `decided:` line in the orchestration log of the run it continues where one exists, and otherwise in the body of the commit that follows it. A request that names no route is no message that says to proceed: its route is taken without the person only under a grant holding `routes`, as SPEC-011 R14 states, and is otherwise recommended and left to the person.

- **R12** — A `git commit` a session runs in a project that declares `siegard.json` is refused by the plugin's `PreToolUse` hook where a line it adds to an orchestration log opens with `decided:` or `recommended:` and is not of the form R5 and R7 state with a criterion R2 names, or opens with `decided:` over a judged criterion while no grant armed through the framework names that log's initiative or names none. A line the commit adds is one the log holds on disk, read past an opening `- ` and its backticks, beyond what the log holds at `HEAD`, and a log `HEAD` does not hold is read whole; the commit reaches a log the index holds changed, a log a path the command names is or holds, and every changed log where the command stages or commits all that is tracked. The refusal names each line and the form it misses, and is said to the session; where the hook cannot read the command, the project or a log, the commit goes ahead.

### Where a recommendation is recorded

- **R5** — An orchestrating entry point that relays a report carrying a recommendation writes it to the run's orchestration log as one line, `recommended: <door> — <criterion> — <deciding fact>`. A recommendation made where no orchestration log exists is in the report alone, and nothing counts it. The criterion's name says whether the recommendation was derived or judged; the line carries nothing else to say it.

### What a handoff is made from

- **R8** — A handoff that hands a person a decision is rendered by `bin/handoff.py --render` from a record, never composed as free text. The record carries `kind`, `language`, `state` in one line, and `withdraws` where the handoff withdraws what the same invocation said earlier; kind `decision` carries `decisions` — an owed act among them, its door the act and its `if_none` the step that refuses to run — each with its `ask`, either the door `recommended` — its `door`, `why`, `reverses_if` and `reply_word` — or, where R3 or R6 leaves the choice to the person, `settles`, what would settle it, with `settles_by`, which of R3's questions or R6 leaves it, then the `others`, each with its `reply_word` and `what_it_does`, `if_none`, what stays as it is if no door is taken, and optionally the `invocation` ready to paste; a decision that hands two doors or more also carries `relation` — `one-of`, the person takes one; `in-order`, the doors are the steps of one path, all taken in the order listed and the recommended door first; or `independent`, each taken on its own — which `--render` writes as the words the schema holds for it, in the record's language, on the line directly above the doors, and without which it refuses the record, saying what each value means; and `report`, where one exists, is the path of the full report on disk, which holds the pending items, commit hashes, measurements and command output the opening does not. The rendered handoff holds its state within 200 characters, each decision's block within 700 and the whole message within 1500; carries no term of the closed list `schemas/handoff.json` holds outside the line ready to paste and a state R10 reads from a script; gives every door a reply word no other door in the handoff uses; and is written in the language the record names, whose few fixed words the schema holds and whose prose the script never translates. A status answer or a design conversation is kind `report`, not a stop: `state` and the `report` path, an inline `body`, or both, with no ceiling. A handoff written as free text is held by `bin/handoff.py --check` to what is decidable without the record: no term of that list in its first 450 characters, and, where it hands a decision, a length within 1500 characters and a word of recommendation or of the person's own decision within those 450. Where text given to `--check` hands a decision and carries no line `--render` writes for one — the line that opens with the words the schema holds for what stays if no door is taken — `--check` refuses it as composed and names `--render`: a handoff that hands a decision is rendered, never checked into shape.

- **R9** — Whether a door's own entry point refuses its inputs as the tree stands is a script's answer, `bin/door.py --check`, read from disk and git alone: its first line is `accepts` or `refuses`, each refusal follows with its fact, and a refusal the entry point's file states that no script decides is listed as not decided, never answered. A door the check refuses is excluded on `precondition unmet`, its deciding fact the `refused:` line; a door it accepts is not thereby recommended. `--render` writes the `entry` and the `check` of the door a record recommends, from the entry the door carries or the one its invocation opens with, and a door of `others` that carries an `entry` and no `check` gets its check; the check is run as the tree stands when the record renders, so a door it refuses is refused as recommended whatever check the record carried. A door that takes a slug is checked over the slug the record's `state_from` or its invocation names, else the armed goal's where the state is the goal's and the goal is the project's, else the one live initiative of the project, and a check run over the latter carries it as `inferred_slug`; a `/reconcile` invocation's slug names a reconciliation and is not read as an initiative — save in a routing record `--prepare --route` wrote (SPEC-011 R14), whose doors are never checked over an initiative it does not name, nor refused for want of a target it does not name: such a door is not checked; where the project holds none or several, the door is not checked. A door that takes a target and is checked with none named is checked over the target the armed goal names, where the check runs over that goal's own initiative; where no goal is armed, or the check runs over another initiative, a project that declares several targets refuses the door for want of one. An `/analyse` door is checked over the specification root alone, which git must hold clean, with no target and no slug. A `/reconcile` door is checked over the file set and the free slug `bin/trace.py --check <target-root> --reconcile-set` prints for its target — the one named, the armed goal's, or the project's one target, and not checked where several are declared and none is named — and an empty set refuses it; a certification and a rewrite are the person's to name, so the check is of the reconciliation that reads alone. An invocation opening with `/siegard:<skill>` names that skill's entry, and a recommended door that carries no `entry`, with no invocation opening with one, takes the one door of the route its own words name, where they name exactly one. Where a grant covering the record's initiative stands, `--render` refuses a recommended door that carries no `entry` in a decision that carries no `invocation`: the entry is the skill the door invokes, whatever it is, and a step that is no door carries the command line that runs it in `invocation`, never prose; a grant holding no door refuses nothing. Under such a grant, an `/implement-task` door whose own invocation names no task, while more than one is deliverable, is not checked rather than refused.

- **R10** — The state a handoff carries is a script's line, never the session's. `bin/handoff.py --prepare` prints the record's skeleton for the skill and the inputs it names, with `state` written and `state_from` naming the script it is the line of: the first line `goal.py --state` answers where a goal is armed through the framework, else the segment `progress.py` prints for the initiative named, else the line it prints for the project, else the fixed words the schema holds for a project with nothing live — quoted as the script printed it, cut to the state ceiling, never translated and never read for the closed list of terms. Beside the skeleton, on standard error, it prints the limits `--render` holds a record to — the ceilings of the state, of each decision's block and of the message, what a decision carries, the words in the record's language a body that recommends says the reversing fact after, that the record holds the skeleton's fields and no other, and the closed list's terms, phrases and pattern names — so that a record is filled to them rather than refused into them — and after them the two invocations that follow, ready to paste: `--save-report` over the skeleton's report path, the report read from standard input, and `--render` over the filled record. The skeleton's doors are the invocations the skill's own report names ready to paste, each marked with the first line `bin/door.py --check` prints for it and its `refused:` facts, or as not checked where no script decides that door or an input it takes is not named; none is marked recommended, and the report's path lies outside the tree every entry point holds to `git status`. Where the skill names a material ledger that leaves lines open, the count of open lines leads the state, before the script's line, and the skill's own invocation is a door beside the others. `--prepare --route`, over a project, a slug no initiative holds and the request `ask.py --record` copied, prints a routing record's skeleton instead, for a request that names no route (SPEC-011 R14): its doors are `/analyse` and `/plan-work`, each so checked, and it refuses a slug an initiative holds and an ask that is no recorded file. A record of kind `decision` carries `state_from`, and `--render` refuses it where `state` differs from what that script prints when it renders, where its door recommended is one the check refuses, and where a recommendation's `why` or `reverses_if` is empty.

- **R11** — A report's short form is held as an opening is. Where kind `report` carries a `report` path, its `body` is the short form above the full report, and `bin/handoff.py --render` refuses it where it carries a term of the closed list anywhere; where it carries no path, its first 450 characters are held so. A body that recommends carries the fixed words the schema holds for the reversing fact in the record's language, followed by that fact, or `--render` refuses it. A door a report hands is handed whole: where its entry point requires a name the tree decides is free, the script that composes the door prints one, and the report never asks the person for it. Where a grant covering the record's initiative stands and the close recommends an invocation, the status is rendered kind `decision`, so the grant answers it as it answers a stop (SPEC-011 R9): its recommended door is that invocation and its others the doors the status hands; a close that recommends none is kind `report`. `--prepare --skill siegard-status` hands its doors only where such a grant stands, and prints kind `report` where none does. The record's initiative is the one its `state_from` names, else the armed goal's where the state is the goal's, else the one live initiative. Where a grant covering the record's initiative stands, `--render` refuses kind `report` from a skill whose report hands doors when its body recommends, so the step is handed as a decision the grant answers: the skeleton's decision with its door recommended, a choice left to the person under `settles` and `settles_by`, or a body that recommends nothing; `--prepare` says so on a `limits:` line where such a grant stands.

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
   The same test holds `--prepare` given a material ledger that leaves lines open: its state
   opens with their count, the skill's own invocation is among the doors, and `--render`
   refuses the record once the count it opened with has changed.
   The same test holds `--prepare` printing on standard error each ceiling, what a decision
   carries and every term, phrase and pattern name of the closed list, with standard output the
   skeleton alone; and `--check` refusing, as composed, free text that hands a decision without
   the line `--render` writes for what stays, while accepting a message `--render` printed.
6. The closed list holds a framework word that is also plain English — `stands`, `nowhere`,
   `owed`, `offered` — as a term only backticked or inside a framework phrase in English prose,
   and as a whole word in prose of any other language; a test holds both halves, and the
   Portuguese fixture that carried those words still carries them.

7. A test holds `bin/handoff.py --render` to R11: a report body above a path that carries a
   term of the closed list past its first 450 characters is refused, a body with no path that
   carries one only past them renders, and a body that recommends without the reversing words
   of its language is refused; and a test holds `bin/trace.py --check --reconcile-set` printing a
   `free slug:` line that names no record or returns directory under `siegard-reconcile/`.
   A test holds `--prepare --skill siegard-status` to kind `report` with no `decisions` where no
   grant stands, and to its doors where one does; and `--render` of a status decision under a
   grant to printing the grant's answer.
   A test holds `--render` refusing, under a standing grant, a report of a skill whose report
   hands doors that recommends, the refusal naming `--prepare` and `settles_by`, and `--prepare`
   printing its `limits:` line; the same report rendering with no grant, under a grant naming
   another initiative, and with no `state_from`, a report recommending nothing rendering under a grant, a report of a
   skill handing no door rendering under a grant, and the step handed as a choice left to the
   person under `settles_by` rendering with the grant's `stop`.

8. A test holds the `PreToolUse` hook to R12 over fixture repositories: a commit adding a
   `decided:` or `recommended:` line that does not parse is refused with the line named; one
   adding a judged `decided:` line is refused where no goal is armed and where the goal armed
   names another initiative, and goes ahead where it names that log's; a derived `decided:` line
   and a log line opening with neither word go ahead; a line already at `HEAD` is never read; a
   log the commit does not reach is never read; and a project without `siegard.json`, a command
   that is no commit, a tool other than Bash and an event record that does not parse are all
   allowed in silence.

9. A test holds `/deliver-scope` to R7 over its text: a derived door taken under the ask that
   invoked the run, with or without a goal, where `bin/door.py --check` accepts it and no
   `decided:` line of the run took it over the same task; a judged door left to a goal; and the
   three questions R3 reserves never taken — `tests/test_deliver_scope.py` proves each.

10. A test holds `bin/handoff.py --render` to the relation R1 and R8 state, over a record of each
    value in each language and with the person's own choice as with a recommendation: the words
    for the value stand alone on the line directly above the first door, once, and no other value's
    words appear in the block; the doors of a path carry their step and the recommended door is the
    first; a decision of two doors or more with no relation, or one that is none of the three, is
    refused once, saying what each value means; one door needs none; only a door is a bullet, so
    the person's own choice and what stays as it is are lines of their own; a lone decision is
    unnumbered and several are counted before the first; every record fixture is swept for the
    same, so the next one is held without anyone adding it; `--prepare` writes an empty relation
    where the skeleton hands two doors and none where it hands one, and the skeleton refuses on
    that field alone once everything else is filled — `tests/test_handoff.py` proves each.
11. A test holds `bin/handoff.py --render` to R9's writing of the check, over fixture repositories: a
    recommended door that lost its entry takes its invocation's and is checked, a door with no
    entry and no invocation is kept as it came, a carried `accepts` the tree no longer supports is
    refused as recommended, a door of `others` without a check gets one, a door that takes a slug
    is checked over the one live initiative and says so in `inferred_slug`, never over a slug the
    record named, and with two live initiatives it stays not checked; a `/reconcile` door is checked
    over the set and slug its trace prints, refused over an empty set and not checked with several
    targets and none named; an invocation naming the plugin gives the recommended door its entry,
    and a door naming exactly one door of the route in its words takes it — `tests/test_handoff.py`.
12. A test holds `bin/handoff.py --render` to R3's class: a choice left to the person with no
    `settles_by` or with a value none of the four is refused once, naming each value and telling
    the session to recommend its door as a judgment; each of the four renders, `finding-worth` only
    naming in `finding` a review record that holds a finding, refused naming none, a file that is
    not one or a record with no finding, its refusal naming the other classes before the
    recommendation, and the record it names shown in the rendered block; a recommendation
    carrying `settles_by` is refused — `tests/test_handoff.py`.

## Readings

- 2026-11-16 — grounds for R10's next invocations and the two limits beside them. From the sales
  consumer transcripts, 2026-11-13 to 2026-11-16, sessions ran `handoff.py --help` 63 times (about
  313k characters), 27 of them on the call after `--prepare`, reading for how `--save-report` and
  `--render` take their input; `--render` was refused about 30 times, 6 of them for a body that
  recommends without the reversing words. A `claude -p` A/B over the step-6 report of a real
  productorder review (`temp/20261116-goal15/`, four runs per arm, Sonnet): with the invocations
  printed after the limits, no run read `--help` or the schema (against 10 reads over four runs
  without them), at 8% less cost per run; two of the four were then refused once, for a field the
  skeleton does not hold and for the missing reversal words, which the limits now name.
  Reversal: `--help` reads after `--prepare` persisting in consumer transcripts under a release that
  prints them.
  Re-measured 2026-11-17 over the code 5.121.0 shipped (both limits included), same review, four
  runs per arm against 5.120.0: handoff `--help` and schema reads 12 -> 2, `--render` refusals 0 and
  0, every run rendered; mean cost $0.416 against $0.415. The 8% saving above did not reproduce —
  the cost of this step is dominated by how far the session reads the review to compose the
  report (11 to 21 turns in both arms), and the change's measured effect is the lookups alone.

- 2026-11-15 — grounds for R8's refusal of a composed decision by `--check`, and for R10's limits
  beside the skeleton. In the session-rules benchmark (`tests/fixtures/benchmarks/rules/`,
  iterations 2 and 3, `4a41a4d`), over eight runs of `handoff-which-door` under the 5.108.0 rules,
  two runs wrote the decision as free text, held it to `handoff.py --check` until it passed and
  never ran `--render`; `--check` accepted it, as R8 then had it hold free text to what is
  decidable without the record. A rewrite of the rules' report and handoff bullets had no such run
  in eight, and was declined: the bypass is the script's to close. Across the 22 runs of
  iterations 2 and 3, `--render` was refused 15 times; the causes the runs gave were a block over
  700 characters, a framework word (`slug`, `door`, a file name), a blank `relation` and a missing
  recommendation or `settles` — limits the schema holds and the skeleton did not show. From every
  consumer transcript, 2026-11-01 to 2026-11-15: 97 of 434 `--render` and `--check` calls were
  refused (22%); of the refusals whose message could be read, about as many fell on the block
  ceiling as on a framework word and on a report path naming no file, a dozen each.
  Reversal: a composed decision recurring after `--check` refuses it, or `--render` refusals not
  falling once the limits print, reopens R8's text in the session rules.

- 2026-11-09 — grounds for R7's derived doors under the person's ask, read from the orchestration
  logs and transcripts of five sales consumers between 2026-11-07 and 2026-11-09 (Siegard 5.47.1
  to 5.79.1): no goal was armed in any `/deliver-scope` run of the window, and a run that met a
  stop handing a door the trace or a script decided ended there and waited for the person; where
  the transcripts show the answer, it was "siga", "Sim", "1" or "Pq parou?". R7 took a derived door
  only under a goal, and outside one only where a later message of the person said to proceed;
  the ask that invoked the route already names it, as the generator's `CLAUDE.md` reads a message
  that names the route. A judged door stays under a goal alone: the 2026-11-05 reading above is a session
  spending a delegation the person wrote in prose on skipping a step.

- 2026-11-05 — grounds for R12, read from the four sales consumers' transcripts and trees over
  2026-11-01T23:00Z..2026-11-05T23:46Z (Siegard 5.47.1–5.53.0): 416 commits, and
  `bin/door.py --check commit`, which the session rules ask before every commit of a delivery,
  ran in none; `bin/ask.py --record` ran 5 times and `bin/handoff.py --render` 8 times over 413
  handoffs. Of 16 `decided:` and `recommended:` lines the window's orchestration logs gained,
  telemetry parsed 1. In `salese2e`'s `incorporar-partymgmt-jornadas` (session `ffe58671`), after
  the person wrote that the session could decide "nas próximas cinco paradas", the session wrote
  three lines `decided: … (delegated decision N of the second 5)` with no goal armed, the third
  stopping before the proof-only rounds on cost — which `/deliver-scope` states is inside the
  ask — and later answered the person that the stop was its own and its reason weak. None of the
  three carried a criterion R2 names, so `goal.py`'s budget would not have counted them under a
  goal either. A rule only a session applies was not applied; the hook applies it at the one act
  every run performs.

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
- 2026-11-21 — grounds for R3's `settles_by`, read from the `configurator`, `inventory` and
  `productorder` sessions under `sales/`, 2026-11-19 13:37Z to 2026-11-21. Of 95 stops the person
  answered with a go-ahead or a "what now?", 76 found a grant of the plugin's version armed; the 48
  of them whose message named a door were replayed under 5.134.0 with a stop that named a door
  unrendered blocked once, each resumed from its own session transcript cut before its last
  message, in a clone at the commit before it, under the grant live at the time. The grant
  answered `take` or `judge` in 5, and `stop` in 25: 19 of them over a `settles` the session
  wrote. Read one by one, about 6 of the 19 were R3's — a node the code contradicts, a deviation
  from a standard the person had not authorized — about 3 were the replay's own (a clone's local
  branch behind its origin), and about 10 were choices of cost or of route: whether writing the
  missing tests now is worth it, to plan or to reconcile first, to deliver again or plan a
  correction, whether to deliver a task already planned. Estimator: the `grant:` and `decision`
  lines `--render` printed in each replay's stream; one run per stop; the reading of the 19 is a
  maintainer's. Replayed again under 5.135.0, two runs per stop: `--render` refused
  `settles` without its class 11 times and the session then recommended; the grant answered
  `take` or `judge`, carried out, in 14 of 96 runs against 5 of 48, at the same cost per run
  ($0.88); none of the six stops read as R3's was taken in either run. What still stopped was a
  recommended door that is no skill of the grant's (10 runs: moving a local branch, running a
  kit, writing a change request), a `/reconcile` door no script checks (5), and `settles` under
  one of the four (15). Reversal: a week of consumer records in which `settles_by` names a class that a
  reading of the decision finds wrong in more than one of four says the class is not what holds
  the session, and the field is weighed for removal.
- 2026-11-21 (declined) — refusing at `--render` a `report` whose prose hands a decision, read by
  `hands_a_decision` as `--check` reads free text. Over the 158 `report` records kept under
  `.git/siegard/handoff/` in the three consumers, 83 read as handing a decision, every one by a
  word of recommendation or of the person's own decision and none by a question or an invocation;
  of the 7 replays above that rendered a report, 4 handed a choice in words no narrower reading
  catches. A refusal that would fire on half of the reports is not a check. Reversal: a reading
  that separates a report offering a choice from one stating a recommendation it already took,
  on the kept reports, with fewer than one in ten refused wrongly.
- 2026-11-21 (last) — grounds for R9's `/reconcile` check and its entry read from an invocation
  naming the plugin or from the door's own words. Of the 96 runs replayed under 5.135.0 (above),
  the records `--render` kept were asked of the grant again under this code, with no model run:
  of 55 decisions, 13 had been answered `take` or `judge` and 21 now are. The 8 that moved were a
  `/reconcile` door checked over its set (4), an invocation opening `/siegard:plan-work` (2), and a
  recommended door whose words named one door of the route (2); none was one of the six stops read
  as R3's. What the static reading does not measure is whether the session then carries the
  answer out, which the gate of SPEC-011 R12 held at 13 of 14. A `/reconcile` door is now checked
  over the whole set of its target, which may be wider than the files a session meant: the skill
  reads that set whole either way. Reversal: a `/reconcile` taken under a grant that the person
  reverts in more than one of ten returns the door to `not checked`.
- 2026-11-25 — grounds for R11's status under a grant. Read from the sales transcripts and
  `handoff-checks.jsonl` of 2026-11-24 (local day; configurator, inventory, salese2e,
  productorder): 49 stops, 21 rendered. Of the 28 unrendered, 4 were turns of a skill that ends
  on a render, each blocked under `enforce` and rendered at the next stop; 24 were turns of no
  skill — status and next-step answers — which SPEC-008 R15 measures and never blocks. In about 8
  of them the stop handed a door the armed grant could have answered (`/plan-work`,
  `/implement-task`, `/reconcile`, a review, a choice of cost), and the person spent a turn on
  "sim", "segue" or "siga". Two causes: the four sessions ran 5.139.0 and 5.137.0, whose session
  rules reached the model as a 2 KB preview, so the rule to render never arrived; and a status
  answer, even rendered, was kind `report`, which no grant answers — `/siegard-status` rendered at
  23:29 in configurator recommending `/plan-work`, and the person still answered "sim" two turns
  later. Asked whether a next-step question under a grant should inform or proceed, the
  maintainer answered that it follows the recommendation; under CLAUDE.md a judged one is taken
  only as the blind door decider returns it, so the status hands the doors it weighed and the
  grant answers them as at a stop. Without a grant nothing changes: `--prepare` prints kind
  `report`, as the skill already required. Reversal: a status taken under a grant that the
  person reverts, or answers by naming another door, in more than one of ten.
- 2026-11-25 — grounds for R11's refusal of a recommending report under a grant. Read from the
  handoff records the seven sales projects kept since 2026-11-20, every one under a standing
  grant: of 11 kind `report` records of skills whose report hands doors (implement-task,
  plan-work, analyse; `/siegard-status` excluded), 3 recommend a next step in their body and
  `--render` accepted all three — configurator 11-24 23:35 `/plan-work` ("Sugiro tratar o vínculo
  parado…", the person answered "próximo passo?"), configurator 11-25 00:13 `/implement-task`
  ("Sugiro revisar essa entrega…", minutes after the person wrote "pode seguir a recomendação e
  fazer em sequência, sem parar nos handoffs"), inventory 11-23 20:22 `/plan-work` ("Sugiro
  encerrar a fase 2…"). The skeleton had printed kind `decision` with its doors each time; the
  session rewrote it as a report, which no grant answers. The other 8 recommend nothing and still
  render. A grant reading the report's prose was weighed and refused: a report carries no
  `settles_by`, and productorder 11-25 01:19 holds a recommendation and a finding's worth in one
  body. Text in the skills alone was refused for want of a mechanical hold: the skeleton already
  handed the decision. Measured by `temp/goal-melhoria/20261124-2334/c1/measure.py`. Reversal: a
  report refused for a recommendation it did not make, seen in a consumer, or a reserved question
  a grant took after the refusal.
- 2026-11-25 — grounds for R3's `finding`. Read from the decision records the sales projects kept
  since 2026-11-20: 10 decisions left to the person as `finding-worth`, none over a finding a
  review recorded — configurator 11-24 18:40 "when to resume" after a usage limit, 19:36 "nothing
  needs you now"; inventory 16:51 "review now or wait", 19:26 "a full re-delivery or reread the
  files first" (the person pasted the rendered choices back as "these decisions are options");
  productorder 11-22 21:51 "split into several tasks"; salese2e 01:04 and 01:06 the plan's order,
  10:45 a stopped delivery's files; and productorder 11-23 22:04 and 22:16, a conformance kit
  against the specification, a reserved question of another class. `--render` accepted all ten
  (`temp/goal-melhoria/20261124-2334/c3/measure.py`); the schema and `--prepare` already said a
  choice of cost, of order or of reading the ask is none of the four. Refusing `finding-worth`
  where the initiative holds no review with findings was weighed and refused: it would have held 5
  of the 10, the other five initiatives holding reviews their choices were not about. Reversal:
  `finding-worth` choices naming a review the choice is not about, in most of the consumer records
  after the release.
- 2026-11-25 — grounds for R1's place of the state line. Of the handoff records the sales projects
  kept since 2026-11-20 for a person writing pt-BR, 116 of 116 rendered whose state a script
  printed opened with that line, fenced — 133 of 138 such records hold it in English with this framework's terms
  ("task 1/3 delivered · phase delivery · last: stop: outside-task — …", "state B — …: the scope
  is delivered, reviewed and measured") — before the question the person was asked. R10's grounds
  of 2026-10-31 are who writes the state, a script rather than the session; where it sits was
  never their point. The line now follows the decisions and the body, above the report's path
  (116 → 10: the ten left are reports holding a state and a path alone);
  `--check` and the Stop hooks read no fenced line and are unmoved. Translating the line was
  weighed and refused (R10 quotes it as printed, and mechanisms read it), as was a label in the
  person's language before it (the first line read stays English). Measured by
  `temp/goal-melhoria/20261124-2334/c5/measure.py`. Reversal: a person asking for the state the
  handoff used to open with, in consumer transcripts after the release.
- 2026-11-25 — grounds for R9's goal step. Under a goal with two initiatives live, a door taking a
  slug that the record did not name was re-checked over `state_from` (a goal's state names none),
  then the invocation, then the one live initiative (none), and stayed `not checked`, so the grant
  stopped on it — though R11 already reads the record's initiative as the armed goal's. Of 20
  decision records the sales projects kept since 2026-11-20 under a goal state, 2 left `/plan-work`
  so (configurator 11-20 18:12, productorder 11-24 17:34), with the goal of each instant rebuilt
  from `goals-ended.jsonl` (`temp/goal-melhoria/20261124-2334/c7/measure.py`); the note asking for
  the slug was printed and not followed. The goal's initiative, named by the person who armed it,
  is checked as named, never marked inferred, and after the invocation, so an invocation naming
  another initiative still stops a grant. Reversal: a goal-state door checked over the goal's
  initiative where the person meant another, read from `grant-checks.jsonl`.
- 2026-11-25 — grounds for R6's accepted door. Three decisions configurator kept on 2026-11-24
  (11:08, 11:24, 12:23) left the choice to the person as `all-excluded` while `/reconcile` beside it
  carried a check that accepted ("Reconciliar os arquivos cujo vínculo ficou desatualizado; pode
  esperar a revisão"), the step the session meant being to go on delivering; `--render` accepted all
  three (`temp/goal-melhoria/20261124-2334/c9/measure.py`), and none of the accepted doors cited a
  rule. Letting the grant pass over the label was weighed and refused (the framework would relabel a
  choice it marked reserved). Reversal: an `all-excluded` beside an accepted door that the person
  confirms a rule excluded.
- 2026-11-25 — grounds for R9's refusal of an unentered recommendation under a grant. Six decisions
  productorder kept under its standing grant (11-23 22:59 to 11-24 14:25) recommended a door only in
  words — "Entrega de novo a tarefa…", "Replaneja juntando as cinco correções…", "Seguir com a
  próxima entrega…" — with no `entry` and no `invocation`, so the grant stopped ("no recommended door
  is in the grant's doors"); the note and the `limits:` line asked for "the `entry` its skeleton door
  holds", which in four of the six the skeleton did not hold (`/implement-task`'s report hands
  `/review-change` alone). A blind decider required the refusal narrow (no `entry` and no
  `invocation`), the entry asked for as the skill the door invokes rather than one the grant holds,
  and an unnamed task among several read as not checked, so a forced entry never leaves one other
  door for the grant to take. Inferring the door from the words was weighed and refused. Measured by
  `temp/goal-melhoria/20261124-2334/c8/measure.py`. Reversal: a recommendation that is no door
  refused for want of an entry, seen in a consumer, or an entry written on a door the session did not
  mean.
