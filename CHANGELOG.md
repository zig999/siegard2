# Changelog

Every version since 3.18.0 is one commit whose subject begins `Ship <version>:`, and this file lists
those subjects, newest first, each with the commit that carries it. The commit's message body
holds what changed and why; `git show <commit>` reads it. A version before 3.18.0 shipped under
another form of subject and is read from `git log`.

The version a consumer runs is the one in `.claude-plugin/plugin.json`. A major changes something
a consumer's own files hold, and the README's "Across a major" section says how to bring them across.

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
