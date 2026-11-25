# Changelog

Every version since 3.18.0 is one commit whose subject begins `Ship <version>:`, and this file lists
those subjects, newest first, each with the commit that carries it. The commit's message body
holds what changed and why; `git show <commit>` reads it. A version before 3.18.0 shipped under
another form of subject and is read from `git log`.

The version a consumer runs is the one in `.claude-plugin/plugin.json`. A major changes something
a consumer's own files hold, and the README's "Across a major" section says how to bring them across.

## 5.143.0 — 2026-11-25

Under a grant covering the initiative, `--render` refuses a closing report of `/analyse`, `/implement-task`, `/plan-work`, `/reconcile` or `/survey` that recommends a next step, so the step is handed as the decision the grant answers — or as the person's own choice under `settles_by`, or the body recommends nothing; `--prepare` says so on a `limits:` line (SPEC-006 R11). (`15424da`)

## 5.142.0 — 2026-11-25

Under an armed grant, a `/siegard-status` that recommends a next step is rendered as a decision the grant answers as at a stop — taken where its check decides, judged by the blind door decider within the budget otherwise; without a grant it stays a report. The session rules send status and next-step answers to `/siegard-status` (SPEC-006 R11). (`9feed99`)

## 5.141.1 — 2026-11-25

A routing record never refuses `/plan-work` for want of a target it does not name: in a project declaring several targets the door reads not checked rather than refused, so `/analyse` is no longer taken as derived on a refusal the record produced (SPEC-006 R9, SPEC-011 R14); the `carry:` line says `/analyse` reads the recorded request; the session rules name `/analyse` and `/plan-work` as the routes a grant takes. (`454510c`)

## 5.141.0 — 2026-11-25

A grant may hold the choice of route: `/siegard-grant --routes` lets the framework route a request that names none, `/analyse` or `/plan-work` over a new initiative, as a grant answers a stop's doors, through `handoff.py --prepare --route` and a budget counted apart (SPEC-011 R14, R15); `door.py --check analyse` makes the `/analyse` door one a grant can take; the commit check refuses a judged route under a grant without `routes`. (`b33c3dd`)

## 5.140.1 — 2026-11-25

The session rules drop four clauses the skill listing and the skills already state — the state question, the adoption route row, a review's conformance pass — falling to 8,963 characters; "Six routes" reads "Five routes". (`fb65c07`)

## 5.140.0 — 2026-11-24

The session rules fit what the harness places whole: `hooks/rules.md` falls from 13,562 to 9,621 characters under a pinned 9,800 ceiling, its text reordered with the rules first; the grant's answer carries a `carry:` line saying how each kind of line is carried out (SPEC-011 R4), its commit gate is printed by `grant.py --arm` and placed by the `SessionStart` hook while a grant holds `commits` (R7), and a goal's `not yet` reason says to answer with the route's next step (SPEC-008 R14). (`001d934`)

## 5.139.0 — 2026-11-23

A delivery that stops commits what it wrote as work in progress before its stop line, so the next route opens on a clean tree (SPEC-008 R18, `door.py --check commit --wip`); `/siegard-standard` opens to a session, writing only what a recorded ask names (SPEC-010 R10); and an armed goal's report says when no findings policy is set. (`5e83e43`)

## 5.138.0 — 2026-11-23

A change of the plugin's version ends no grant: a grant holds under every version that reads its record, its words, budget and mark carried over, so an update no longer asks the person to arm it again (SPEC-011 R3). (`471e2cb`)

## 5.137.1 — 2026-11-23

`goal.py --state` reads a `deliver-scope <slug>: prove <task>` commit whose task is named by its bare name, where one task of the scope alone carries it, so a goal no longer stays `not yet` over a proof-only re-delivery it made (SPEC-008 R2). (`9e4e2aa`)

## 5.137.0 — 2026-11-23

A turn that ran a skill ending on a render owes that render: `hooks/after_tool.py` (was `hooks/grant_gate.py`) keeps a turn record of the instant such a skill was invoked, and under `SIEGARD_HANDOFF_STOP=enforce` the `Stop` hook blocks once a route left unrendered, never the form of a message; `handoff-checks.jsonl` lines gain `route` and `rendered`, every `grant-checks.jsonl` line its `mode`, and SPEC-011 R13 holds no rule (SPEC-008 R15, SPEC-011 R12). (`8018d06`)

## 5.136.1 — 2026-11-22

`goal.py --state` reads a task whose proof record is not yet written as answering no criterion, so a stop with an implementation record and no proof keeps its state line and `--render` can read it (SPEC-008 R12). (`5d5b3ce`)

## 5.136.0 — 2026-11-21

`--render` checks a `/reconcile` door over the file set and free slug `trace.py --reconcile-set` prints for its target, reads an invocation opening `/siegard:<skill>` as that skill's entry, and gives a recommended door with no entry the one route door its own words name, so a grant can answer doors a session left unreadable (SPEC-006 R9). (`ff7b3fe`)

## 5.135.0 — 2026-11-21

A choice a handoff leaves to the person names which of SPEC-006 R3's questions it is, in `settles_by` — `contradiction`, `two-readings`, `finding-worth` or `all-excluded` — and `--render` refuses one that names none, so a choice of cost or of route is recommended and, under a grant, reaches it. Under a grant, `--render` notes a recommended door left unchecked for want of a slug (SPEC-011 R9). (`f2c5945`)

## 5.134.0 — 2026-11-21

A grant's `take` or `judge` printed at a render becomes the session's obligation, recorded by a `PostToolUse` hook from the command's own output; a stop that leaves it uncarried is blocked once, and the next stop is allowed (SPEC-011 R12). A stop that hands an unrendered decision naming a door is logged and never blocked (R13). (`905a598`)

## 5.133.4 — 2026-11-21

A handoff that hands one door, with none excluded, is answered `take` by the grant and not `judge`, so the door decider is asked only over a choice between doors, and no budget is spent on a door nothing separates from itself (SPEC-011 R4). (`1aafa3d`)

## 5.133.3 — 2026-11-20

The specification-conformance reviewer files a development tool's defaults, flags and exit codes, and how a test is arranged, in `looked_past` and not as facts the specification does not hold: «The stack is never a node» (SPEC-003 §Rule). (`5853506`)

## 5.133.2 — 2026-11-20

A door `handoff.py` checks with no target named is checked over the target the armed goal names, where the check runs over that goal's own initiative (SPEC-006 R9); a task that implements no node is delivered by a record that carries `stands` and no `nodes`, which the writer holds to the tree alone (SPEC-004 R20, R26). (`aedc207`)

## 5.133.1 — 2026-11-20

The telemetry probe passes over a transcript that holds no conversation, so a session opened and closed with only its metadata no longer makes a readable transcript directory unavailable. (`0a6f83b`)

## 5.133.0 — 2026-11-19

Arming a grant over one that still stands ends it in `grants-ended.jsonl` as `replaced`, says what it held, and arms the new one, so the person needs no `--clear` first; a refused arming leaves the standing grant in place (SPEC-011 R1, R3). (`4b8cccf`)

## 5.132.0 — 2026-11-19

The note `handoff.py --render` prints on standard error under an armed grant fires for any decision whose recommended door carries no `entry`, and names the skeleton's absent doors only where there are some, so a recommended door written beside the skeleton's kept doors is no longer left unreadable to the grant in silence (SPEC-011 R9). (`193fb20`)

## 5.131.0 — 2026-11-19

`handoff.py --render` writes each recommended door's `entry` and `check` as the tree stands, over the slug the record names or the one live initiative, and prints the armed grant's answer over the record on standard error, so a stop's doors reach the grant at the stop (SPEC-006 R9, SPEC-011 R9). (`67c1c53`)

## 5.130.0 — 2026-11-18

`/plan-work` runs the registry's `review:` line once over the tree as it stands before the decomposer cuts, and hands it a red run's name and excerpt; the decomposer turns a test red before the plan green in one task every other task depends on (SPEC-004 R35). (`4014da0`)

## 5.129.0 — 2026-11-18

`trace.py --check --reconcile-set` no longer leaves a file "to a delivery" because an undelivered task carrying `stands` implements its node: such a delivery binds nothing, and the file is the reconciliation's (SPEC-004 R34). (`1ac766f`)

## 5.128.0 — 2026-11-18

`/deliver-scope` takes `/reconcile` once per task for a `stands` that does not stand whether `/implement-task` read it out of date before writing or the record writer refused it, and `stop: stands` is kept for a second refusal after that reconciliation (SPEC-008 R8). (`d24cef8`)

## 5.127.0 — 2026-11-17

`/implement-task` hands the test-author the rules of the target's standard whose scope meets the tests `siegard.json` declares, and the artifacts they presuppose, written outside the tree by the new `deliver.py --standard --tests`, never the whole registry (SPEC-007 R8). (`3169e6c`)

## 5.126.0 — 2026-11-17

A review's capture runs `bin/run.py --reuse`: where a passed run of the same steps, in the same directory, saw the tree as it stands outside the framework's records, that run is the capture and nothing executes, instead of the suite running again over the same bytes (SPEC-004 R33). (`a0da155`)

## 5.125.0 — 2026-11-17

Where a build red only a test answers runs the proof ahead of the record, `/implement-task` hands the test-author the implementer's final reply, written outside the tree by the new `deliver.py --implementer-return`, never the implementer's transcript, as SPEC-004 already required. (`0800ffc`)

## 5.124.1 — 2026-11-17

`/siegard-grant` names the `project_root:` line of `project.py --here` as the root where the invocation names none, as every other skill that resolves the root does, so a session no longer hands `grant.py` the whole project report as a path. (`9945c31`)

## 5.124.0 — 2026-11-17

A proof-only re-delivery whose suite is red on its own new test, diagnosed `code`, goes on as the task's re-delivery — a fresh implementer, a new build and both records rewritten — and `deliver.py --red-guard` holds that implementer to the tests already in the tree, putting back any declared test it changed. (`ebddadf`)

## 5.123.0 — 2026-11-17

`trace.py --save-returns` saves a whole wave of judge returns in one call, each found by the pack its subagent's prompt names; `/review-change` and `/reconcile` hand it as the wave's save. (`93b9546`)

## 5.122.0 — 2026-11-17

`/plan-work`, `/deliver-scope` and `/implement-task` hand `spec.py --pack`, `telemetry.py` and `door.py --check commit` as invocations ready to paste, and `spec.py --help` lists `--pack`. (`4fd4027`)

## 5.121.0 — 2026-11-16

`handoff.py --prepare` prints the `--save-report` and `--render` invocations ready to paste after its limits, and its limits name the words a recommending body says the reversing fact after and that the record holds the skeleton's fields alone. (`ec475ae`)

## 5.120.0 — 2026-11-16

The commit that records a stop carries the runs that passed, so the next arming finds no pending change, and the record writer's adoption door names every node the `stands` files extend and is not offered twice over the same files. (`febb263`)

## 5.119.0 — 2026-11-16

`door.py --check commit` holds a commit to the stop line it adds, so the doors a stop hands and a resumed run are no longer refused for one already committed, and a red run a later attempt passed is answered. (`7ee7773`)

## 5.118.0 — 2026-11-16

The commit hook refuses a commit that adds a stop line to an orchestration log and carries anything but the log and the telemetry root, so a stopped run no longer commits its red run or its delivery files with the stop. (`3fad336`)

## 5.117.0 — 2026-11-16

A proof owes the red suite attempts numbered before the run it cites; a red attempt after it belongs to the next invocation's record and no longer stops `deliver.py --outstanding` or the corrective task a red proof-only re-delivery points to. (`b06ce9e`)

## 5.116.0 — 2026-11-16

The plan decomposer keeps an interface and its existing consumers in one task unless the first task leaves the project's suite green on its own, and reads the inventory's risks and their named consumers before cutting. (`67ee898`)

## 5.115.0 — 2026-11-16

The session rules gain one bullet: every message, report and handoff the person reads is written in the language of the person's own messages, after every compaction too. (`db00cc7`)

## 5.114.0 — 2026-11-15

`goal.py --state` gains the `prove` check: a goal reaches state A only once each certification its first review refused with a testable remainder over a task of the scope is answered by a `deliver-scope <slug>: prove <task>` re-delivery of one task whose proof it read (SPEC-008 R2). (`ee4c8b6`)

## 5.113.0 — 2026-11-15

`goal.py --compose` declares untouched no path under the telemetry root, which the measure commits whole, so a recorded ask or a grant's words pending there is committed by the measure rather than forbidden by the condition (SPEC-008 R6). (`37c87eb`)

## 5.112.0 — 2026-11-15

An initiative holds its `closure.md` once `HEAD` holds it, so `grant.py --commit` accepts the closing's own commit under a grant holding `close`, with or without a slug, and a grant naming the initiative ends when that commit lands (SPEC-011 R3, R7). (`2fc70b4`)

## 5.111.0 — 2026-11-15

`deliver.py --standing` reports the standard findings of a target's past reviews whose quoted source still stands, grouped by file and narrowed by `--rule` and `--file`, with those changed, gone or not decidable counted apart (SPEC-007 R7). (`e2533ec`)

## 5.110.0 — 2026-11-15

`deliver.py --recurring` prints the rules of a target's standard its past reviews cite, most cited first, and `/implement-task` hands those lines to the task-implementer and the test-author to check first (SPEC-007 R6). (`2587fe2`)

## 5.109.0 — 2026-11-15

`handoff.py --check` refuses, as composed, free text that hands a decision without a line `--render` writes, and names `--render`; `handoff.py --prepare` prints on standard error the ceilings, what a decision carries and the closed list of words `--render` holds a record to (SPEC-006 R8, R10). (`406a0bb`)

## 5.108.0 — 2026-11-15

Under a grant, a first line `refuses` from `grant.py --commit` stops a commit unless the person's own words in the session name that commit, as R11 already held for a closing; the session rules and `/plan-work`'s closing reference say so (SPEC-011 R7). (`f8d7cad`)

## 5.107.0 — 2026-11-15

While a goal or a grant is armed, the new `hooks/bounds.py` refuses a push, a branch, a history rewrite, a stash and a stage or commit of all that is tracked; in every state it refuses a hand write of `siegard-trace.json`, an initiative's `plan.json` or `delivery.json`, or a captured run; `run.py` records the tree a run left (`siegard-run/3`) and `trace.py --bind-record` refuses a file no run of its task saw (SPEC-010 R8, R9; SPEC-004 R31). (`511c833`)

## 5.106.0 — 2026-11-14

A judged door is taken only under a grant: a goal carries no budget and `--budget` is refused by `goal.py`, the commit hook takes a judged line only where a grant names the initiative or none, and a grant's budget counts for each initiative it covers, `grant.py --decide --slug` naming the stopped one (SPEC-006 R7, R12; SPEC-008 R3, R6, R14; SPEC-011 R2, R5, R6, R10). (`0541ece`)

## 5.105.0 — 2026-11-14

A closing under a grant holding `close` asks `grant.py --close --slug` before its marker and `grant.py --commit` before its commit, and persists the ask copied whole — the grant's words or the person's — never a summary; `/deliver-scope`'s step 5 states its proof-only re-deliveries are inside the ask (SPEC-011 R11, R7). (`399dc7f`)

## 5.104.0 — 2026-11-14

`/siegard-grant` is armed by its flags alone and records the invocation as typed; an invocation with no argument arms nothing and shows the grant armed; each grant carries a mark taken with the instant it was armed, which its `decided:` lines and its budget use (SPEC-011 R1, R2, R5, R10). (`1e37afa`)

## 5.103.0 — 2026-11-14

A goal over an objective in prose runs `/analyse` before the plan unless the invocation says `--no-specify`; composing a goal hands only the line that arms it through the framework; and arming a grant over one a plugin update or a closed initiative already ended replaces it instead of refusing (SPEC-008 R6, SPEC-011 R1, R3). (`f463aca`)

## 5.102.0 — 2026-11-14

The message a session stops on when its goal ends — state A, state B or paused — is held to the handoff check like any stop no goal answers: recorded, and under `enforce` sent back once (SPEC-008 R15). (`e3e0c9b`)

## 5.101.0 — 2026-11-14

A decision that hands two doors or more says how they relate — pick one, a path in order, or each on its own — on a line above the doors; only a door is a bullet, a lone decision is not numbered, and a decision's block may run to 700 characters (SPEC-006 R1, R8). (`6b6d729`)

## 5.100.0 — 2026-11-13

A run that receives a stop asks the grant before it ends: `handoff.py --render` keeps the record, `grant.py --decide --latest <skill> --after <commit>` answers over it and refuses a stale one, and a door a grant takes is counted by the grant's budget and by no goal's (SPEC-011 R9, R10). (`85bf02d`)

## 5.99.1 — 2026-11-13

`/siegard-grant`'s report paragraph lists what an armed grant takes instead of running it into one long sentence. (`aca70e0`)

## 5.99.0 — 2026-11-13

A grant's doors default to all six, `analyse` among them, and `--doors none` leaves them empty; the budget of judged doors stays at zero unless written. `/siegard-grant` and `grant.py` now agree: `--arm` prints what it recorded and refuses empty words, and `--disarm` with nothing armed says so (SPEC-011). (`727d2bb`)

## 5.98.0 — 2026-11-13

A grant holds for the project until the person clears it with `/siegard-grant --clear`, over every live initiative unless `--slug` limits it; `analyse` is a door where the person writes it, and a commit, a closing and the budget read every covered initiative (SPEC-011). (`ee90105`)

## 5.97.0 — 2026-11-13

A grant the person records with `/siegard-grant` lets a stop take a door its own check leaves alone, have the decider choose a door of cost within a budget, commit what the route wrote, and close the initiative once everything is delivered, proven and reviewed; `grant.py` gates each act, and a choice the person reserves stays theirs (SPEC-011). (`ffe8d27`)

## 5.96.0 — 2026-11-13

A red on a test the delivery's own test author wrote, which the diagnosis reads as `test`, is rewritten once by that test author with the diagnosis, instead of stopping the run; a second red on it, or a test left under `contested` because a node still states its condition, is the stop `producers` (SPEC-004 R30). (`f47a1b1`)

## 5.95.0 — 2026-11-13

A criterion an implementation record marks unmet is answered, and no longer fails a goal's `criteria` check, where a review committed since the goal began gives it `covered` by a test in a file the task's own proof names; the answer lists each criterion beside the test (SPEC-008 R12). (`decdbe8`)

## 5.94.0 — 2026-11-12

A review relays every disagreement its proofs recorded: `deliver.py --findings` prints each proof's `contested` entry whole under its task, the review report carries it as the person's to settle, and `/deliver-scope` relays it whole (SPEC-004 R29). (`5abb016`)

## 5.93.0 — 2026-11-12

The drift tally names the bindings its findings sit on: `trace.py --check` ends with `N drift finding(s) on K of M binding(s), P node–file pair(s)`, each class line names the bindings it covers, and the session-start receipt counts `moved` findings over the bindings they sit on. (`a9dfe09`)

## 5.92.0 — 2026-11-12

A refused `stands` names the files the trace already binds: a node bound to a current file is answered by naming it with no door, a node bound only to moved files has the ordinary reconciliation, and an adoption is the door only for a node bound to no file (SPEC-004 R20). (`20a233e`)

## 5.91.0 — 2026-11-12

The ledger lives while its material is in use: committed while a line is open or an adoption still reads it, removed by the commit of the increment that closes it — its message carrying `trace.py --ledger`'s output — or by the adoption's commit; `trace.py --ledger` ends with `ledger: keep` or `ledger: remove` (SPEC-001 R16, SPEC-005 R8, SPEC-008 R10). (`0105644`)

## 5.90.0 — 2026-11-11

A read entry's `found` names its file from the repository's root: `spec.py --decide` rewrites a path spelling out where the repository, or the directory holding it, sits on the machine, and says so (SPEC-001 R9). (`98a245e`)

## 5.89.0 — 2026-11-11

A suite or build red on an earlier task's test whose every owning plan is closed is adopted by the delivery: `deliver.py --test-owner` prints `adopt`, `rewrite` or `re-deliver`, and the test-author rewrites the test whole, keeping every condition its owning proofs state unless a node now says otherwise (SPEC-004 R24, R25). (`c3e636b`)

## 5.88.0 — 2026-11-10

A run's retry number is `bin/run.py`'s: `--next` lands an attempt one past the greatest number its name holds, and `/implement-task` runs setup, build and suite with it (SPEC-004 R28). (`4dbd3cd`)

## 5.87.0 — 2026-11-09

A return that does not parse only because a text field's one-line value holds `: ` is read with that value quoted whole, and the writer names the lines it quoted; a fence, text around the mapping or a key given twice is still refused (SPEC-004 R27). (`d48e6c4`)

## 5.86.1 — 2026-11-09

The second reading a release needs is a step of the `/reconcile` and `/review-change` checklists, run before the bind and never skipped. (`0657f0d`)

## 5.86.0 — 2026-11-09

A pair a reconciliation read `nowhere` is released by the bind where a second reading, blind to the first, also reads it nowhere and the node keeps a current file; `trace.py --stage-release` stages that reading, and `/reconcile` and `/review-change` run it before the bind. Otherwise the release stays the person's (SPEC-005 R10). (`7d9a916`)

## 5.85.0 — 2026-11-09

`/analyse`, `/plan-work`, `/implement-task`, `/review-change` and `/reconcile` commit what their own invocation wrote once their validator passes — one pathspec-scoped commit, `<skill> <slug>: <step>`, never a push — and `/deliver-scope` commits its own log, measure and a stopped delivery's runs (SPEC-010 R7). (`e53a5d8`)

## 5.84.0 — 2026-11-09

`trace.py --stage` names the files the trace binds a node to when it refuses a certification over others; `deliver.py --outstanding` reports a delivered task no review names as never reviewed (SPEC-004 R22); "convém" reads as a word of recommendation. (`0645e43`)

## 5.83.0 — 2026-11-09

A blocking note goes back to the decomposer with the note whole, at most twice, and stands for a person only where the cut keeps the criterion on a sentence the scope states verbatim or the second cut leaves it; a note asking which of a node's values applies, or whether its statement reaches a case it does not name, is `unstated` and decided (SPEC-001 R17). (`55f72ba`)

## 5.82.0 — 2026-11-09

A registry may declare steps whose role is `fix` — a formatter that writes — and a delivery runs them after the install and before every check in its build and suite, so a producer never reformats by hand; a review and a reconciliation never run them, and `deliver.py --standard` prints the review's selection on its own line (SPEC-007 R5). (`086ea23`)

## 5.81.0 — 2026-11-09

A delivery whose implementer finds the task already met writes its implementation record carrying `stands` itself, instead of stopping for a plan; where the trace lacks the bindings, `deliver.py --write-implementation` prints the one door — an adoption `/reconcile` whose candidates are the nodes bound to none of the files, or an ordinary one where a binding moved — and `/deliver-scope` takes it once per task. `/deliver-scope` takes every derived door under the person's own ask, with or without a goal (SPEC-006 R7, SPEC-008 R8). (`69e982d`)

## 5.80.0 — 2026-11-08

A task carrying `stands` holds where its files bind every node it implements between them, each file bound to some node of the task; no one file need bind every node. SPEC-004 R18 and R26 now read as R20 already did, and `deliver.py --write-implementation` refuses a node bound to no `stands` file or a file bound to none of the task's nodes instead of every missing node–file pair. (`eb85957`)

## 5.79.1 — 2026-11-08

`trace.py --carry` over a target nothing has been bound in carries nothing and exits 0, as `--check` does, so a first adoption's `/reconcile` step 2 no longer meets a refusal. (`9d2f4d3`)

## 5.79.0 — 2026-11-08

The specification's ontology is applied in four layers: SPEC-003 makes the order of an operation's refusals its precedence; the class schemas, which both node writers read, state what each class holds and what it does not; `spec.py --shape` reports class signals — an answer in a rule or a constraint, a constraint with no fitness, a refusal condition written again — and refuses none; and the analyse skill reads one table applying the order of homes kind by kind. (`330d0b9`)

## 5.78.0 — 2026-11-08

The stack is never a node: a language, a runtime version, a package, a tool, a command, an image or a test arrangement belongs to the project's standard, which the person authors. The analyse skill leaves such a line outside the specification and hands it to the person as a rule; the decider returns it as a new `standard` outcome, which plan-work reports without stopping the task. (`7d759b1`)

## 5.77.0 — 2026-11-08

`spec.py --delta` reads what a change did to the specification: the nodes it added, modified and removed, whether a modified node changed in form alone, and the decision-log entries it appended beside each — against the working tree or between two revisions. A reading, so no specification changes. (`9ac3ef9`)

## 5.76.1 — 2026-11-08

The unstated-fact decider writes a boundary in `excludes` and places a behaviour by SPEC-003's order of homes, as the analyse skill already does; an analysis that rewrites a node moves its boundary prose into `excludes`. (`f1a10d6`)

## 5.76.0 — 2026-11-08

A policy may constrain a Contract — a condition an operation meets with no element its subject — and SPEC-003 orders where a behaviour lives: answers, a rule on the element, a policy on the contract, then an architecture constraint for what limits how the solution is built or runs. The analyse guidance applies the order. (`aa1c1d8`)

## 5.75.0 — 2026-11-08

A boundary another node decides is declared in a node's `excludes` — a case and the node that decides it — rather than written into its prose, so the validator resolves the reference; nodes written before keep their prose. SPEC-001 R14 and SPEC-003 state it, the analyse skill writes it, and the binder reads it. (`fb4b70f`)

## 5.74.0 — 2026-11-08

The decomposer reads the plan's impact set in one candidate pack, in windows where one Read cannot hold it, instead of one file per node and log. The decider keeps reading the nodes a fact needs. (`0d896bf`)

## 5.73.1 — 2026-11-08

The binder reads a candidate pack too large for one Read in consecutive windows to its end, searching none in place of reading. (`3a5f88a`)

## 5.73.0 — 2026-11-08

A refusal several operations of an api answer alike is written once, under a YAML anchor, and aliased at its place in each operation's list; the reading is the same data, so a converted contract is carried rather than re-read. SPEC-003 §Contract states it, the analyse guidance shows it, and the agents that read contracts know the alias. (`5ba63ad`)

## 5.72.0 — 2026-11-08

The rule that every constraint is a candidate of every planned scope moves from the plan-work skill into SPEC-003, and the skill quotes it. Nothing a plan does changes. (`2da99a9`)

## 5.71.0 — 2026-11-08

A node whose text changed in form alone no longer owes its files a judgment: `trace.py --carry` restamps every pair whose stamped node text, recovered from git, has the node's present reading, and leaves each other pair with its reason. `/reconcile` runs it before `--check`. SPEC-003 R7 defines the reading; SPEC-005 R13 the carry. (`93a2f72`)

## 5.70.0 — 2026-11-08

The binder reads its candidate set in one file: `spec.py --pack` prints every candidate verbatim under its identity and digest and lists the decision logs by path, plan-work hands that file instead of one path per node and log, and the binder opens a log only for a claim of succession. SPEC-003 R6 names the pack. (`6cf9b5b`)

## 5.69.0 — 2026-11-07

The implement-task skill fits whole inside what a compaction re-attaches: its spawn blocks and their filling rules move to the delegation reference, the order diagram gives way to the checklist, and the task-pin paragraph moves to the records reference. A resumed delivery no longer reads the skill again. (`1c6b8c7`)

## 5.68.0 — 2026-11-07

The deliver-scope skill opens with a progress checklist, fits whole inside what a compaction re-attaches, and keeps its branches in four references; its sentences run shorter, its description names the trigger first, and the door-decider's description takes the form the other agents carry. A resumed run now hands its report through the handoff record. (`2c9c710`)

## 5.67.0 — 2026-11-07

The reconcile skill opens with a progress checklist, fits whole inside what a compaction re-attaches, and keeps its branches in eight references; its sentences run shorter and its description names the trigger first. A resumed reconciliation now hands its report through the handoff record. (`9a02a4c`)

## 5.66.0 — 2026-11-07

The review-change skill opens with a progress checklist, fits whole inside what a compaction re-attaches, and keeps its branches in seven references; it and three of its agents name each concept once and read 6% shorter. A resumed review now hands its report through the handoff record. (`6594b2c`)

## 5.65.0 — 2026-11-07

The plan-work skill opens with a progress checklist, fits whole inside what a compaction re-attaches, and keeps its modes and routes in eight references; it and its four agents name each concept once and read 22% shorter. A resumed planning session now hands its report through the handoff record. (`4997252`)

## 5.64.0 — 2026-11-07

A skill's `## Terms` defines each term by the one sentence `schemas/terms.json` holds for it, verbatim, and a test refuses any other wording; the text metrics read their synonyms from the same file. (`18fad2a`)

## 5.63.0 — 2026-11-07

The shipped instructions name each concept once — "the person", "subagent", `test-author` — across skills, agents, scripts and schemas; `schemas/terms.json` lists the concepts and their variants, and a test holds forbidden variants at zero and every other count to a ratchet. (`9169bc1`)

## 5.62.0 — 2026-11-07

The implement-task skill, its references and its three agents name each concept once, under a `## Terms` section, state each rule with at most one clause of why, and open each description with its trigger; the fifteen files read 23% shorter and 10% cheaper, with a reading quiz showing no meaning lost. (`4b4f069`)

## 5.61.0 — 2026-11-07

The implement-task skill opens with a progress checklist that sends a resumed session back to the skill, and keeps its branches, text unchanged, in eleven `references/` files its steps name (1065 → 496 lines); `handoff.py` reads the doors a report hands from the report reference too, and no citation in the skill or its three agents splits the clause it stands in. (`11b3a0f`)

## 5.60.0 — 2026-11-07

A project root no invocation names is the git toplevel of the session's working directory, read by `project.py --here` and only where it holds `siegard.json` (SPEC-010 R6); every skill that takes the project root quotes the rule in place of a sentence that read both ways, and `siegard.json` is never created under an unnamed root. (`fe7eac0`)

## 5.59.2 — 2026-11-07

No citation in the analyse skill splits the clause it stands in: two quotations move after the instruction they back, words unchanged, and a test holds the skill to it. (`3d618db`)

## 5.59.1 — 2026-11-07

`/plan-work` declares its invocation form in `argument-hint`, and the `/analyse` and `/reconcile` handoffs into it hand the invocation in that form. (`59dbe97`)

## 5.59.0 — 2026-11-07

`spec.py --shape --of` lists a scoped node no log decided anything over at zero, so every node an analysis wrote has a count its report can quote (SPEC-001). (`7484c7e`)

## 5.58.1 — 2026-11-07

The analyse skill states its handoff as four steps and names `schemas/handoff.json` as the shape the record is completed against; the validator's checks read as a list, undefined terms are defined where used, and the skill gains `argument-hint`. (`5bd58ce`)

## 5.58.0 — 2026-11-07

The analyse skill opens with a progress checklist naming each step's command and file, and tells the session to read the skill again where a step's section is no longer in context; the ledger step joins the order line. Deciding by class, reading `--shape` and the ledger's line rules move verbatim into `skills/analyse/references/`, read at the step that needs them. (`09a7fa8`)

## 5.57.0 — 2026-11-07

The ledger is part of the increment it records: the commit that takes the specification an analysis wrote takes the ledger with it, including `/deliver-scope`'s `analyse` commit under a goal that asks to specify (SPEC-001 R16, SPEC-008 R10). (`1322bbd`)

## 5.56.0 — 2026-11-07

Every line of material given to `/analyse` as a file lands in a node, is left out with a reason, or is left open with what remains, in a ledger beside it that records the file's digest (SPEC-001 R16); `trace.py` enumerates the lines of prose material and `--ledger` prints the open lines and the reasons grouped by count. `handoff.py --prepare --ledger` leads the state with the open count and hands `/analyse` back as a door (SPEC-006 R10), and an adoption refuses a ledger over prose or with a line open (SPEC-005 R8). (`5825bf7`)

## 5.55.0 — 2026-11-07

A thing the material names only as a question to decide, an option or a proposal is one it names: the entry deciding it says in `unstated` what the material asked or proposed, never that the material names no such thing (SPEC-001 R9). The analyse skill and the decision-log schema's `unstated` description state it. (`42334e0`)

## 5.54.0 — 2026-11-05

A commit that adds to an orchestration log a `decided:` or `recommended:` line out of the form the handoff states, or a judged `decided:` line where no goal armed through the framework names that initiative, is refused by the plugin's new `PreToolUse` hook, `hooks/commit_check.py` (SPEC-006 R12). The door line's form and its eight criteria live once, in `bin/goal.py`. (`391a7d3`)

## 5.53.0 — 2026-11-04

A task carrying `stands`, and a proof-only re-delivery, stop only where a binding of a node the task implements is absent or out of date on its files; another node's binding out of date there is named in the record's notes and left to the review that follows, which reads every reviewed file against every node bound to it (SPEC-004 R25, R26). `deliver.py --write-implementation` refuses a `stands` record over an out-of-date binding of the task's own nodes. (`fdc3ca8`)

## 5.52.0 — 2026-11-03

`/siegard-archive` runs `bin/archive.py`, which holds its criteria: `--check` reports each closed initiative eligible or skipped with the criterion and what answers it, and changes nothing; `--remove` checks again, removes only the pairs that pass, and prints the tag and the commit for the person. A pair holding a file git ignores or does not track is not committed, each delivery is checked against the targets its own records name, and an index never derived is answered by the derivation the report names. (`66a4f6f`)

## 5.51.0 — 2026-11-03

A session writes a project's standard only where the person's own words name the entry — the package or the step, by name — after `bin/ask.py --record` holds those words, and commits that file alone under a message citing the ask's digest; words naming no entry get a question back. `CLAUDE.md`'s execution bound, the session rules and `task-implementer` now state the same route. (`5a05624`)

## 5.50.0 — 2026-11-02

`/siegard-goal` takes the project root from the git toplevel of the session's working directory when the invocation names none, reads its arguments by one table with exactly one scope form, hands an objective to the script on stdin, and hands each outcome — armed, composed, refused, stopped — in one shape, with the lines that follow and end an armed run. (`9792e82`)

## 5.49.0 — 2026-11-02

A review owes no path the target source root no longer holds or never held: a file the delivery deleted, or one outside the target, is named by the record as R16 asks, left out of the review's file set, and said as not read — `deliver.py --review` and `--outstanding` no longer refuse or owe a review over it (SPEC-004 R22). (`7711742`)

## 5.48.0 — 2026-11-01

A goal is armed through the framework only by the person's own invocation of `/siegard-goal` opening with `--arm`: the skill is closed to the model's invocation, so its scope, objective and word to arm are the person's, and a later message asking to arm is answered with the invocation to paste (SPEC-008 R6, R14). Over a citation, `--arm` composes and the person arms after reading the file the script wrote. The skill's report is the report `handoff.py --prepare` prepares, followed by the two ways to arm, each fenced and ready to paste. (`c1c6e49`)

## 5.47.1 — 2026-11-01

The decision-log schema says what a log holds: decisions, facts a planning step read from material outside the specification root, and retirements — not decisions alone. (`2f27c72`)

## 5.47.0 — 2026-11-01

What bounds a goal and a door is counted by a script. `goal.py --compose` pins the budget of judged doors into the state command and the armed record, and `--state` counts the judged `decided:` lines the log gained against it — more is state B (SPEC-008 R3). Another session's stop beside an armed goal is held to the handoff check, and a session starting beside a goal bound elsewhere is told so (R15, R16). A derived door taken outside a goal is recorded as a `decided:` line (SPEC-006 R7). `/adopt-scope` resumes from its own log, commits the declared telemetry root and reports through `handoff.py --prepare`/`--render`, and telemetry counts its log's recommendations. `trace.py --stage --node` records the nodes a person names as written since the bind. Telemetry gains `proofs` (`siegard-telemetry/19`). History in shipped text is restated as standing fact. (`e6a9afb`)

## 5.46.0 — 2026-11-01

The specification states what the skills and the validator already held. SPEC-003 admits what an upstream imposes into a consumed Contract, defines a `capability` as a promise made at the system's boundary — a third party's included, named as an upstream — and states the state-machine and same-context rules `rule.json` and `spec.py` enforced. SPEC-001 defines the decision log per node and says the choice between `/analyse` and the decided-fact route is the person's outside a goal; `spec.py` refuses a root holding nodes and no context. SPEC-004 gains R25, the suite-time route for a red on an earlier task's test; SPEC-005 R5 states the precedence between adoption states; SPEC-007 R3 states that a pin never refuses a record. (`f6dd0b7`)

## 5.45.1 — 2026-11-01

A task declaring `produces` runs the install alone only where `deliver.py --standard --reach` says no rule reaches what it wrote, as the validator already held; `/implement-task`, `phase_steps` and the registry check's printed line now say so. `goal.py` reads a commit naming the skill and the slug followed by a space as on the route, and `--objective-file -` reads the objective from stdin. `/siegard-archive` hands a pathspec-scoped add, every skill but `/deliver-scope` and `/adopt-scope` states it never commits, and the session rules lose a sentence that contradicted the first; a single-value flag named twice is refused by every script that parses one, and `trace.py`'s usage names every form it reads. (`2044676`)

## 5.45.0 — 2026-11-01

A report's short form is held as a decision's opening is (SPEC-006 R11): `bin/handoff.py --render` reads a `body` above a report path whole for the closed list of terms, and a body with no path over its first 450 characters; the list gains the drift classes `moved`, `proof` and `orphaned` and the Portuguese "ato devido" and "leitura devida"; and a body that recommends without the words that open the reversing fact is refused. `trace.py --check --reconcile-set` prints a `free slug:` no reconciliation holds yet, and `/siegard-status` hands the `/reconcile` invocation with it instead of asking the person for a name. (`b4105b2`)

## 5.44.1 — 2026-11-01

The session rules say where the framework's version is read — the marker line that opens them — instead of naming a script that prints none; the handoff and commit rules lose a reason, a layout `--render` already produces and a repeated clause, and the file goes from 12,291 to 11,946 bytes. `tests/test_rules_health.py` holds the file to the rules `CLAUDE.md` now states for it: its size pinned as a ratchet under 200 lines, each bullet opening with its rule in bold, and every script, flag and schema it names shipping. In this repository, the suite runs in parallel under pytest-xdist, and both glossaries gain the armed goal, the handoff record, the door check, the recorded ask, the relay and the progress line. (`410d326`)

## 5.44.0 — 2026-10-31

The state a handoff opens with is a script's line, never the session's: `bin/handoff.py --prepare` writes it from `goal.py --state` or `progress.py` with each next door already checked by `door.py`, `--save-report` writes the full report under the git directory, and `--render` refuses a state that no longer matches its script; eight skills hand their decisions this way (SPEC-006 R10). With no goal armed, the plugin's `Stop` hook holds the message a session stops on to `handoff.py --check` and records it, measuring by default and blocking once under `SIEGARD_HANDOFF_STOP=enforce`, and a session starting under another plugin version than its armed goal is told so (SPEC-008 R15–R17, `siegard-telemetry/18`). `bin/ask.py` records the person's authorizing words so a route resumed after a compaction reads them instead of a summary, and `bin/relay.py` writes text for a sibling project's session behind a confirmation line (SPEC-010). `door.py --check commit` refuses a commit after a stop line or over a red run no record names (SPEC-008 R18). `/siegard-config` installs the status line in `.claude/settings.local.json`, and the line says when it runs from another plugin version (SPEC-009 R5, R6). (`ea876ce`)

## 5.43.0 — 2026-10-31

A goal armed through the framework ends on a script's answer: `goal.py --arm` records it on the person's word, the plugin's `Stop` hook answers each stop from `goal.py --state` — `state A` or `state B` ends it, `not yet` blocks with the failing checks, a fourth identical `not yet` ends it paused (SPEC-008 R14). A handoff that hands a decision is rendered by `bin/handoff.py --render` from a record, and a free-text one is held to what is decidable by `--check`; telemetry reports `handoff_form` (SPEC-006 R8, `siegard-telemetry/17`). `bin/door.py --check` decides whether a door's own entry point refuses its inputs before the door is handed (SPEC-006 R9). A go-ahead naming the next step covers the one commit that step needs, and a derived recommendation is taken where the person's message says to proceed. A judge answers the nodes it only read beside a file's bindings by bare identity, a 49–54% cut of saved return characters (SPEC-005 R12). `bin/progress.py` prints a one-line progress for the status line (SPEC-009). Grounds: 251 handoffs and 2,683 subagent runs read from four consumers, 2026-10-27..31. (`00affae`)

## 5.42.0 — 2026-10-31

A release of a pair a reconciliation read `nowhere` drops that pair alone: `trace.py --release <target> <file>... --node <node>` leaves every other file of the node at the stamp it had and refuses a pair no record reads `nowhere`, and a bind hands that invocation ready whether or not another file of the set still holds the fact, where it handed a `--replace` that also dropped every file outside the reconciled set (SPEC-005 R10). (`13def1d`)

## 5.41.0 — 2026-10-31

A reconciliation commit naming its slug with nothing after it stays on a goal's route, and one touching another reconciliation's record leaves it: `goal.py --state` reads R2's "its own record" as the record under the slug the message names, and a commit naming the skill and the slug alone is on the route (SPEC-008 R2, R11). A run that resumes an initiative whose orchestration log closes on a stop line appends after it and never removes it (SPEC-008 R4). (`a2e6540`)

## 5.40.0 — 2026-10-31

A build red whose fix lies only in files the project declares as its tests goes to the test author before the implementation record is written, instead of stopping the delivery: `project.py --declared-tests` says which paths are tests, the implementer keeps its source, the proof is written ahead of the record, and the record is written over the build that then passes (SPEC-004 R24). A rule a step other than the suite decides must hold over a tree without the task's tests, and one requiring a test to exist names the suite step; `deliver.py --standard --against` names the rules this reaches and refuses none (SPEC-007 R4). (`5b52196`)

## 5.39.0 — 2026-10-30

Three stop classes end a goal in state B: `outside-task` — a red no change to the task's own files can answer, a build red over a tree the delivery left unchanged or a fix in another task's files, never a judged retry; `already-met` — the R20 stop where the run does not take the trace's door; and `unclassified` — any stop no other class names (SPEC-008 R3, R4). (`d4f7691`)

## 5.38.0 — 2026-10-30

Only the substrate alone — a task declaring `produces` that wrote nothing a rule of its standard reaches — goes without a proof; /implement-task reads that from `deliver.py --outstanding`, and a substrate task that also wrote a file a rule reaches proves like any other (SPEC-004 R23). `--outstanding` names the substrate alone apart and counts it delivered, so a goal over it reaches state A (SPEC-008 R2). (`eaee176`)

## 5.37.0 — 2026-10-30

A review answers for its tasks as they stood when it was written: `deliver.py` holds only the review `--review` names to its tasks' files and criteria as they stand, and `--outstanding` names a task no review answers as owed one, never a refusal (SPEC-004 R22); a re-delivery writes its record again over the files its task already wrote, `--unrecorded` refusing an unchanged file the replaced record did not name (SPEC-004 R21); /deliver-scope names each review it invokes, the slug or the least free `-N`. (`627b7b3`)

## 5.36.3 — 2026-10-30

The drift hook exits 0 on a machine missing PyYAML or jsonschema, stays silent outside a project that declares `siegard.json`, and inside one says in a single line — as `systemMessage` and as context — that the count was not taken and what to install. (`d3ba462`)

## 5.36.2 — 2026-10-30

A delivery whose implementer finds every criterion already met writes no record and stops, naming the files that hold the fact; /implement-task runs `trace.py --encodes` over them and hands the door it decides — the plan carrying `stands`, or `/reconcile` (SPEC-004 R20). (`1dbcb46`)

## 5.36.1 — 2026-10-29

`met` in an implementation record says whether the written source satisfies the criterion as it reads — demonstrating it is the proof's and the review's — and the criteria description cites the goal's reading of an unmet one (SPEC-008 R12); telemetry counts a commit under an armed goal as `loop`; /deliver-scope runs and commits each proof-only re-delivery before the next. (`8a27dde`)

## 5.36.0 — 2026-10-29

A goal ends in state B on a commit that names no skill and the slug, and state A never stands over a criterion an implementation record says is unmet — the scope is state B with each named — while the criteria this goal's reviews left uncovered are listed beside the state (SPEC-008 R11–R13). (`8ef3d74`)

## 5.35.1 — 2026-10-27

`deliver.py --write-implementation` keeps `files: []` on an implementation carrying `stands`, which its contract requires; every other empty list is still read as absent. (`c68ae9d`)

## 5.35.0 — 2026-10-27

A task writes source, or carries `stands` over files the trace already binds to every node it implements; /plan-work confirms `stands` with `trace.py --encodes` before writing a task, and a proof of what a sibling task writes is that sibling's criterion (SPEC-004 R18, R19). (`a8c117b`)

## 5.34.2 — 2026-10-26

A goal is refused while the trace or `siegard-reconcile/` holds a pending change, and /deliver-scope's precondition holds both, since the route commits them. (`de76fa5`)

## 5.34.1 — 2026-10-26

A goal over a project with no specification root yet is refused naming both ways to create it, and /siegard-goal relays the resolution the script printed. (`799afe2`)

## 5.34.0 — 2026-10-26

/clarify-request carries out an instruction that only reads or plans in the same turn, by reading only; one that acts is still handed over unexecuted. (`ffbc0cb`)

## 5.33.0 — 2026-10-26

/clarify-request cites an earlier message of the conversation, quoted and named as the person's or the assistant's; an assistant's recommendation stays an option, and a continuation summary or a memory settles nothing. (`29c8034`)

## 5.32.0 — 2026-10-26

A goal over a prose objective may ask to specify it: /analyse runs once before the plan and the specification is committed apart, for the person to review after the goal. (`10ba218`)

## 5.31.0 — 2026-10-25

A goal reaches state B where a delivery stopped, re-planned tasks are owed again rather than refused, returns are read as their producers wrote them, and /siegard-goal takes a cited objective. (`f11221f`)

## 5.30.0 — 2026-10-25

Under a goal, a door a fact decides is taken without the person, a judged one only by a door decider blind to the goal and within its budget, and the findings a policy names are corrected once. (`b65004e`)

## 5.29.0 — 2026-10-25

A goal over /deliver-scope ends on `goal.py --state` reading state A or state B from disk, composed by /siegard-goal over an objective, an epic or a set of tasks. (`67e7514`)

## 5.28.1 — 2026-10-23

A delegation that answers by hand-back is read from the `message` the harness confirmed delivered, by `--save-return` and the delivery writers alike. (`52d8fd5`)

## 5.28.0 — 2026-10-20

A drifted pair a human-declared rewrite reproduces byte for byte from its pinned text, with every named step passing, is carried without a judge. (`2b9a8dc`)

## 5.27.0 — 2026-10-20

Telemetry reads the orchestrating context per call and replays each session at every auto-compact window, with the re-authorizations each would owe. (`9460b63`)

## 5.26.0 — 2026-10-19

A live proof names tests its target holds, and a closed one naming a test the tree no longer holds is receipted. (`d05388b`)

## 5.25.0 — 2026-10-19

A reconciliation binds each pair on its own file's judgment, and a file that stopped holding a fact its siblings still hold is a release a person decides. (`58cbb65`)

## 5.24.0 — 2026-10-19

A delivery restamps only the files its record names, and the drift report says so. (`44a1800`)

## 5.23.1 — 2026-10-15

The plugin names its author and the marketplace describes itself. (`cd1f7d6`)

## 5.23.0 — 2026-10-14

A moved registry holds no command against an earlier run, and a recommendation an orchestration log wrote is read wherever the log sits. (`deef624`)

## 5.22.0 — 2026-10-14

Where no fact decides between options of cost or of reading the ask, the handoff recommends by judgment and says it is one. (`c0fbd6e`)

## 5.21.0 — 2026-10-14

A choice that is the person's is handed as their own decision, an excluded option is said to be excluded, and an opening with no option on the route says so. (`b3d5699`)

## 5.20.0 — 2026-10-13

A step declared after a record was written is owed by the records written after it. (`e302fc6`)

## 5.19.0 — 2026-10-08

The session rules reach a project that declares siegard.json, and nothing else. (`fe46a6b`)

## 5.18.0 — 2026-10-08

A wave ends on the save's own receipt, a return the fold will refuse is named while the wave is open, a delivery record is a function of its return, and a repeat is the same prompt handed to the same agent type. (`f09685b`)

## 5.17.0 — 2026-10-08

/clarify-request names a mode for calls that change state, applies a data act to the data, writes no stop condition the person did not take, and leaves no fence label in its handoff. (`b112a40`)

## 5.16.0 — 2026-10-08

/clarify-request rewrites a person's request as one validated instruction, asking only the decisions that are theirs. (`4ab80eb`)

## 5.15.0 — 2026-10-07

SPEC-005 names what proves it, a revised decision is counted and named rather than shared, every projection input is shown load-bearing, a reversal has a place for its reading, and the benchmarks SPEC-001 names are repository state with the decided-fact route run once. (`756d96b`)

## 5.14.0 — 2026-10-07

The full text is a projection the metamodel names, a far end is named only where a class holds a distribution, the records pinning no standard reach every report that runs --outstanding, and a finding stops nothing. (`702add9`)

## 5.13.0 — 2026-10-07

The material that states no fact is an absent input, a node the analysis introduced is disclosed by its first entry, and the report counts the fields each node had decided for it. (`66d0d1f`)

## 5.12.0 — 2026-10-07

A record pinning no standard where the project declares one is reported beside the outstanding tasks, and a review says which paths of its file set no rule reaches. (`4d2d8d5`)

## 5.11.0 — 2026-10-07

A delegation is waited for by its notification, the decider is spawned never offered, a session's own commit is bound and counted, a closure says what it leaves standing, a proof task is bound against its neighbours, and a refused certification is pinned at what it was read at. (`2574335`)

## 5.9.0 — 2026-10-06

A confirmation is counted never quoted, a review opens with how many findings go where, the staging cuts the judges into waves, and a state question is answered from disk. (`089578c`)

## 5.7.2 — 2026-10-06

The opening speaks the person's words, and a criterion's name is for the log alone. (`04a0113`)

## 5.7.1 — 2026-10-06

The reconcile set is printed per target from the listed findings, and the opening labels every item and names the recommended door. (`433c204`)

## 5.7.0 — 2026-10-06

A restates finding stands while the text it quoted is in the file, and a judge quotes the line. (`8f9b5d6`)

## 5.6.1 — 2026-10-06

The reconciliation corpus is parsed once per process, through libyaml where the interpreter has it. (`ffd0f46`)

## 5.6.0 — 2026-10-06

The reconcile set is the script's composition, a status hands two readings without choosing, and a criterion is named as written. (`e805453`)

## 5.5.0 — 2026-10-06

A handoff opens with what needs the person, and recommends only what a fact on disk decides. (`75333e4`)

## 5.4.0 — 2026-10-05

A certification is held to its own target's registry, a submodule can be kept outside, and text that only names a control is never a finding. (`bdf4741`)

## 5.3.0 — 2026-10-02

Material read from tests is held to a contract, and an adoption over its ledger judges each governed file against its own facts' nodes. (`dca8d77`)

## 5.2.0 — 2026-10-01

A return is saved from the delegation's transcript, never retyped from its notification. (`c41fe99`)

## 5.1.1 — 2026-10-01

An adopted node's bound files are all named, and two files never share one return. (`656d6c8`)

## 5.1.0 — 2026-10-01

A test the project declares is uncertified, never unsurveyed. (`bbaa02c`)

## 5.0.2 — 2026-10-01

A tombstone log retires every field it filled, and the writer never raises on a log with no final newline. (`63d3ab0`)

## 5.0.1 — 2026-10-01

Telemetry reads a decided field through a list by name. (`58d76dc`)

## 5.0.0 — 2026-10-01

A decision log sits beside the node it discloses. (`c98283a`)

## 4.29.0 — 2026-10-01

/adopt-scope carries one context of adopted source end to end under one ask. (`357f1ce`)

## 4.28.0 — 2026-09-30

A file is stamped against the node text it was read at, and a comment alone is no finding. (`55e7c72`)

## 4.27.0 — 2026-09-30

The survey — an agent reads adopted source and returns its material, a skill hands it to /analyse. (`3850cfb`)

## 4.26.0 — 2026-09-30

An adoption over a ledger hands each file the candidates its own facts landed in. (`eb95088`)

## 4.25.0 — 2026-09-30

Every fact of survey material lands in a node or is left out with a reason — the ledger. (`6fae1e7`)

## 4.24.0 — 2026-09-30

A failure answer is an answer, judges spawn in batches the harness runs, and a question is not a return. (`b03a029`)

## 4.23.0 — 2026-09-30

An element is held where its shape is declared (SPEC-003 §Domain Model). (`2777b2d`)

## 4.22.0 — 2026-09-30

An absent work root is no initiative, an empty findings list is no finding, and a retirement is not a decision. (`0459993`)

## 4.21.4 — 2026-09-30

An adoption certifies a candidate the trace does not hold yet, tested. (`98aaac2`)

## 4.21.3 — 2026-09-30

`restates` is a comment or a docstring, never text the running system emits. (`e03fde7`)

## 4.21.2 — 2026-09-30

`restates` asks whether code anywhere holds the fact, not the judged file. (`6c58614`)

## 4.21.1 — 2026-09-30

`nowhere` with a reason after it is nowhere, and an unheld reading closes an earlier finding. (`3543cdd`)

## 4.21.0 — 2026-09-30

Text restating a node's fact the code holds is `restates`, and blocks no binding. (`195e4d2`)

## 4.20.0 — 2026-09-30

An adoption owes only what it found, and a judge's return quotes in block scalars. (`66aff50`)

## 4.19.0 — 2026-09-29

Source no delivery wrote is adopted — SPEC-005, reconcile/6, --stage --adopt. (`649e445`)

## 4.18.0 — 2026-09-29

Telemetry counts each message once, a context descriptor is never bound, and a retired log location is appended rather than edited. (`48ffba6`)

## 4.17.0 — 2026-09-29

A delivery's tree is held to the records that name it, and telemetry counts compactions. (`78ee6c2`)

## 4.16.2 — 2026-09-28

Element.json says what each body heading holds, in SPEC-002's words. (`e0eb192`)

## 4.16.1 — 2026-09-28

The unstated-fact decider writes a further condition as its own rule, and a body that governs rather than argues. (`5aca2f5`)

## 4.16.0 — 2026-09-28

What an api's operations answer is the contract's `answers`, and a rule states the condition and never the answer. (`2095499`)

## 4.15.2 — 2026-09-28

A cross-context element reference is the target's full identity, in SPEC-002 R4 as in the pattern. (`c11e71c`)

## 4.15.1 — 2026-09-28

`--owed` spells a remainder's files as the proof increment's ask names them. (`e7a7f75`)

## 4.15.0 — 2026-09-28

A node a finite test decides is owed that test wherever its implementation stands, and every surface hands the route that writes it. (`196d837`)

## 4.14.1 — 2026-09-28

A finding's file is spelled as the pack header hands it, a second home is a declaration nothing binds, and a finding on a node outside the set reaches the report. (`91635e0`)

## 4.14.0 — 2026-09-25

Every bind rests on bytes a judge read and every delivery on a node the binder read, and the rules the skills stated in prose are the validator's. (`dd2fa87`)

## 4.13.0 — 2026-09-24

A compound criterion is caught before the task exists, and a refused certification's remainder has a route that writes the test. (`8ae9c8c`)

## 4.12.0 — 2026-09-24

A decision the framework made is followed to the field it filled, and a session's cost is attributed to the skill it ran. (`9f0a282`)

## 4.11.0 — 2026-09-23

A certification is carried whole and never lost in silence, and the review composes its certifications from the proofs' own claims. (`fcc4771`)

## 4.10.0 — 2026-09-23

Every node of the specification in one state, read once across the trace and every initiative. (`aeabb8d`)

## 4.9.3 — 2026-09-23

--unplanned reads the initiatives /siegard-archive removed, from git. (`7815e84`)

## 4.9.2 — 2026-09-23

A review written before `unpaired` existed is receipted, never refused. (`8594be9`)

## 4.9.1 — 2026-09-23

SPEC-004 states the coverage audit's reading of a test no criterion derives. (`ac05d52`)

## 4.9.0 — 2026-09-22

The drift a project carries reaches the session that starts over it, and the coverage pass answers in both directions. (`306ce0c`)

## 4.8.0 — 2026-09-12

Telemetry counts an agent's own spawns, and a corrective delivery answers the sibling test it moved. (`b5ad8ac`)

## 4.7.0 — 2026-09-11

A spawned subagent is named by its plugin-scoped identity. (`dd1395c`)

## 4.6.0 — 2026-09-10

A fact read from a plan's intake is recorded in the decision log as read. (`1a04b82`)

## 4.5.0 — 2026-09-10

A corrective increment's criteria carry the domain's condition, and a chain of silences under one skeleton is seen while it happens. (`e17e27b`)

## 4.4.0 — 2026-09-10

Tests are owed to obligations, and a finite test decides a node before a reading does. (`2e7187c`)

## 4.3.0 — 2026-09-10

The plugin's hooks place the consumer rules; nothing is copied to the root. (`2c2c46c`)

## 4.2.0 — 2026-09-09

The consumer rules carry only what binds a session outside a skill. (`13119c6`)

## 4.1.0 — 2026-09-09

A refused certification says whether a test could close the rest. (`28dcc49`)

## 4.0.0 — 2026-09-09

A delivery record names its own target. (`7b9b435`)

## 3.58.0 — 2026-09-09

Every citation of a specification carries its sentence verbatim. (`f91cb34`)

## 3.57.0 — 2026-09-09

One condition is one sentence, and the validator says so. (`4abb0f6`)

## 3.56.0 — 2026-09-08

The prose a specification writes about itself, measured where it is written. (`eb4945b`)

## 3.54.0 — 2026-09-08

A run answers the node as it stood, and a word answers for its senses. (`ecd2290`)

## 3.53.0 — 2026-09-08

The contracts a human authors answer for themselves. (`d2ebe81`)

## 3.52.1 — 2026-09-08

A constraint several steps decide needs every one of them. (`aa9e855`)

## 3.52.0 — 2026-09-08

A delivery's own proof may claim the node its test decides. (`67691fd`)

## 3.51.1 — 2026-09-08

The revalidation of phases 0, 1 and 2. (`76dfa8d`)

## 3.51.0 — 2026-09-08

A run answers the pairs a reading would only re-decide. (`b534f48`)

## 3.50.1 — 2026-09-08

The review of phases 0 and 1, and what it found. (`f91bb33`)

## 3.50.0 — 2026-09-08

A reconciliation may certify the test that decides a node. (`774262d`)

## 3.49.0 — 2026-09-08

The trace names the pairs a registry step decides. (`be1fcf9`)

## 3.48.2 — 2026-09-08

Returning agents write quoted source as a YAML block scalar. (`1e18398`)

## 3.48.1 — 2026-09-07

--fold refuses the same unresolvable target one step earlier. (`a4ab84c`)

## 3.48.0 — 2026-09-07

--reconciliation holds a record's target to the project file. (`70b7578`)

## 3.47.1 — 2026-09-07

Conventions may be handed to /siegard-standard by path. (`4969fab`)

## 3.47.0 — 2026-09-07

The overview says how much each aggregate holds. (`1f71f21`)

## 3.46.0 — 2026-09-07

The context map reads whose model crosses a boundary. (`0645027`)

## 3.45.0 — 2026-09-07

A registry names the step that decides a constraint. (`19411ff`)

## 3.44.1 — 2026-09-05

The orchestration log is kept, and a judged file is still unbound. (`6182f90`)

## 3.44.0 — 2026-09-03

A fresh worktree derives its includes and names its own prepare step. (`2180d29`)

## 3.43.0 — 2026-09-02

A status reports the reading that never ran, and hands a door that runs. (`9e38829`)

## 3.42.1 — 2026-09-02

The pack's resolved-path block is labels, not sentences. (`9382377`)

## 3.42.0 — 2026-09-02

The conformance judge is handed the contract that judges it, and only that one. (`997c4eb`)

## 3.41.1 — 2026-09-02

One name for the specification, and two statements that could not be acted on. (`7ab0750`)

## 3.41.0 — 2026-09-02

The runner hands over the tail of what failed, bounded by itself. (`d4fbff4`)

## 3.40.0 — 2026-09-02

A delegation that returned is re-entered, not replaced. (`268edfc`)

## 3.39.1 — 2026-09-02

A file already read whole is one the producer is holding. (`e220a99`)

## 3.39.0 — 2026-09-02

A delegation is a filled form, and a red compile inside the suite has a way out. (`8387ab3`)

## 3.38.1 — 2026-09-02

An architecture constraint is a candidate before any grep runs. (`9839f4c`)

## 3.38.0 — 2026-09-02

A plan's impact set is read rather than assembled, and every judge is handed the fields it writes. (`722390a`)

## 3.37.0 — 2026-09-01

A review judges every node the trace binds to the files it reads, and restamps what cleared. (`e484802`)

## 3.36.0 — 2026-09-01

Siegard-reconcile/3 — a finding says which question it answers. (`c15a3a0`)

## 3.35.0 — 2026-09-01

An audit stages no candidate tier. (`26b129a`)

## 3.34.0 — 2026-09-01

A reconcile prompt carries paths, not the text behind them. (`2182651`)

## 3.33.0 — 2026-09-01

Contracts print their own slices, and a review reads only its own half. (`49fe7b4`)

## 3.32.0 — 2026-09-01

The audit route — standing bindings gain their one re-examination. (`c16a34d`)

## 3.31.1 — 2026-09-01

Every decision-log reader starts at the grouped projection. (`3ab7567`)

## 3.31.0 — 2026-09-01

The reconcile locate and fold run as scripts, and the conformance judge moves to sonnet. (`4994afa`)

## 3.30.0 — 2026-08-31

Comments drain with every edit, and a rules update names the restart it needs. (`fc0ec32`)

## 3.29.0 — 2026-08-31

The consumer rules said directively, a fifth shorter. (`8a2d3ef`)

## 3.28.0 — 2026-08-31

The distribution states what is, never what changed. (`a12f4c8`)

## 3.27.0 — 2026-08-31

Source carries no comments, and a fact is held by code, never by prose. (`76017ca`)

## 3.26.0 — 2026-08-31

What a reconciliation found and no bind could close, read back. (`c44f5ca`)

## 3.25.0 — 2026-08-30

Every agent runs on a pinned model, by the criterion effort already used. (`9d79cb7`)

## 3.24.0 — 2026-08-29

A marketplace to install from, and a rules file that reports its own age. (`af57fe7`)

## 3.23.0 — 2026-08-27

/deliver-scope carries a stated scope end to end. (`942daeb`)

## 3.22.0 — 2026-08-27

Five answers to the servicedeskn1 telemetry report. (`6d24e1b`)

## 3.21.0 — 2026-08-25

/siegard-telemetry counts how the work happened, from disk. (`8a64a24`)

## 3.20.0 — 2026-08-25

A standard per target in siegard.json. (`a0284b6`)

## 3.19.0 — 2026-08-21

A reconciliation binds what its judgment cleared. (`661af89`)

## 3.18.0 — 2026-08-21

The audit remediation and the second telemetry round. (`eda12f7`)
