# A red suite

Read at step 6 whenever the suite run is red, before anything is sent back or rerun.

**A red suite is a stop, and which way out applies is diagnosed, never guessed.** Nothing further
is written — the implementation record stands, because its own run passed, and no proof record is
composed, so `deliver.py --outstanding` reports the task as implemented with no proof holding it
up, which is true and is the state a person should meet. Report the run by path and the tests
that failed.

Where the step that failed is the one whose role is `suite`, spawn a `siegard:failure-diagnostician`
subagent — its judgment lives at `${CLAUDE_PLUGIN_ROOT}/agents/failure-diagnostician.md` — and
hand it this, filled:

```
run:                   <absolute path of the run's directory under the delivery root>
target source root:    <absolute path>
nodes:                 <the identity of each specification node the task implements, with the
                        absolute path of the specification root>
finding slice:         <the --contract finding output, pasted whole>
file set:              <every path the implementation record's `files` and the tests just
                        written name>
```

Always, on every red of that step, and never your own reading of the log in its place: a session
probing flakiness with commands of its own is composing commands the registry never declared,
which this skill forbids under *What you never do*, and the diagnosis is the licit form of the same question. Where
an earlier step of this run failed instead — a typecheck or a lint reaching the files just
written — no diagnosis is owed: the log names the file, and that red goes back to the producer
whose file it is, exactly as a red build does.

**The `cause` the diagnosis returns is one of the contract's four, and it opens five ways out.**
Four of the five it settles on its own. The fifth it does not: where the cause is `test`, which
of that cause's two exits applies turns on who owns the failing test, and the diagnosis returns
the file the run named without being told what this delivery wrote. This invocation knows —
the tests step 5 just wrote are in the proof it is about to compose, and everything else is
somebody else's. A file in that set takes the first `test` exit; any other file takes the second.

`code` — the source is wrong: the fix goes back to the `task-implementer` with the findings, that
delegation re-entered rather than respawned, and the suite runs again under
`<epic>-<slug>-suite-2`, with the first run keeping its name. Where the implementer returns that
the fix lies only in files no record of this task names, the red is the stop step 4 names for a
red no change to this task's own files can answer. `build` — nothing ran, because a
compile the suite step performed itself failed, and every failure the output lists after it
describes a binary nobody built. No registry owes a step that compiles
before the suite, so this is the same red as a typecheck step's, arriving one step later instead
of never: it goes back to the producer whose file the compiler named — the `task-implementer` for
source and the `test-author` for a test, that delegation re-entered too — and the suite runs
again under the next name. Nothing here waits on a person. `test`, on a test this delivery
wrote — the two producers disagree and that disagreement is what the red is: the proof asserts
what the criterion requires and the implementation does not satisfy it, and only a person
settles that. The report quotes the diagnosis's evidence and correction in full, whole findings
and not a summary of them — a diagnosis obvious enough to look mechanical is still a person's
call to make, and the report's business is to make that call fast, not to make it for them.
`test`, on a test an earlier task owns — what broke it is not a regression but
this delivery's own legitimate files, and which of two shapes it took is read from the two
implementation records, never from the assertion's wording: whether a path this delivery's
`files` names is one the owning task's `files` names too — «A suite red on a test the proof of an
earlier task names is answered by this delivery only where its files include one that task's
implementation record names» (SPEC-004 R25). **Where none is**, the old assertion
claimed more than its task's criteria establish, totality over ground the two tasks share, and
this delivery falsified the excess beside it. That test is not edited from here, whatever the
temptation: the way out is the proof-only re-delivery `references/redelivery.md` names, over the
task that owns the test, and it is the human's to invoke. The report hands that invocation ready
to paste — the owning task by identifier, the assertion the run named, the file this delivery
added — and says plainly that it runs only after the human commits this delivery's pending
state, because that invocation's own clean-tree stop refuses a tree still carrying it. **Where
one is**, this delivery rewrote a file the owning task bound — the shape a corrective increment
takes, cut over that very file — and the assertion states what the file did before the
specification moved. The owning task's implementation no longer stands as its record describes,
so the proof-only re-delivery is not open to it: its own `--check --all` would refuse before a
line was written, and an invocation handed toward that refusal costs a round trip and answers
nothing. The test is this delivery's to answer. The `test-author` is re-entered and rewrites it
whole — never trimmed, never narrowed — against the nodes as they stand now; it joins this
proof's `tests`; the record's `## Notes` names the owning task, the assertion the run named and
the file this delivery moved; and the suite runs again under the next name. The owning task's
own records are left as they are: each describes the tree it was written against, which is what
a record is, and what the file asserts now is this proof's to say. And `setup` — neither the code nor the test
was reached, because the harness or the environment it needs did not stand up: that is not this
delivery's defect and not its to fix, so nothing is sent to any producer. Run the suite again,
once, under the next name. A second consecutive red the diagnosis reads the same way is a stop:
infrastructure failing twice is a fact for a person, and the report quotes both diagnoses and
hands the rerun invocation ready. That exit licenses exactly one thing — the same suite,
again — and the run is what decides; a fix routed through it would be a fix nobody diagnosed.

**One more way out exists, it is forbidden, and it is the one that is easy.** A test is never
weakened, deleted, narrowed or rewritten to make the suite green. This invocation holds two
producers precisely so that one cannot overrule the other, and a test edited until it passes is
exactly that overruling, performed where nobody would see it. The `test` exits over a test an
earlier task owns exist precisely so this one never looks necessary: whichever shape applies, the
assertion is rewritten whole by the producer class that owns proofs — in its own invocation where
the owning implementation stands, in this one where this delivery moved what that task bound —
and never trimmed to unblock a run. What makes the rule enforceable
rather than pious is that the runs are on disk: four attempts leave four logs, and a test that
changed between them is in the diff beside them.
