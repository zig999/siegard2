# A red suite

Read at step 6 whenever the suite run is red, before anything is sent back or rerun.

## Contents

- What a red suite leaves standing
- The diagnosis
- The five ways out
- The way out that is forbidden

## What a red suite leaves standing

**A red suite is a stop until a way out applies, and which way out applies is diagnosed, never
guessed.** Nothing further is written: the implementation record stands, because its own run
passed, and no proof record is written, so `deliver.py --outstanding` reports the task as
implemented with no proof — the true state. Report the run by path and the tests that failed.

## The diagnosis

Where the step that failed is the one whose role is `suite`, spawn a
`siegard:failure-diagnostician` subagent — its judgment lives at
`${CLAUDE_PLUGIN_ROOT}/agents/failure-diagnostician.md` — and hand it this, filled:

```
run:                   <absolute path of the run's directory under the delivery root>
target source root:    <absolute path>
nodes:                 <the identity of each specification node the task implements, with the
                        absolute path of the specification root>
finding slice:         <the --contract finding output, pasted whole>
file set:              <every path the implementation record's `files` and the tests just
                        written name>
```

Spawn it on every red of that step, never reading the log yourself in its place: probing a red
with commands of your own composes commands the registry never declared.

Where an earlier step of the run failed instead — a typecheck or a lint reaching the files just
written — no diagnosis is owed: the log names the file, and the red goes back to the producer whose
file it is, exactly as a red build does.

## The five ways out

The diagnosis returns one of the contract's four causes. `test` splits in two by who owns the
failing test, which the diagnosis is not told and you know: a test the test-author just wrote for
this proof is this delivery's; any other test belongs to an earlier task. Every rerun takes the
next free name — `<epic>-<slug>-suite-2`, then `-3` — and every earlier run keeps its own.

| cause | owner of the failing test | what happens | waits on a person |
|---|---|---|---|
| `code` | — | the findings go to the `task-implementer`, re-entered; the suite runs again | no |
| `build` | — | the suite's own compile failed; the red goes to the producer whose file the compiler named, re-entered; the suite runs again | no |
| `test` | this delivery | stop: the two producers disagree | yes |
| `test` | an earlier task | read the two implementation records: see below | where no file is shared |
| `setup` | — | nothing goes to a producer; the suite runs again once | on a second `setup` |

- **`code`.** Where the implementer returns that the fix lies only in files no record of this task
  names, the red is the stop `references/red-build.md` names for a red no change to this task's own
  files can answer.
- **`test`, on a test this delivery wrote.** The proof asserts what the criterion requires and the
  implementation does not satisfy it; only a person settles that. The report quotes the diagnosis's
  evidence and correction whole, never a summary — even where it looks mechanical.
- **`test`, on a test an earlier task owns.** This delivery's legitimate files broke it, and which
  of two shapes it took is read from the two implementation records, never from the assertion's
  wording: does this delivery's `files` name a path the owning task's `files` names too? — «A suite
  red on a test the proof of an earlier task names is answered by this delivery only where its
  files include one that task's implementation record names» (SPEC-004 R25).
  - **Where none is**, the old assertion claimed more than its task's criteria establish —
    totality over ground the two tasks share — and this delivery falsified the excess. Do not edit
    that test. Stop, and hand the proof-only re-delivery `references/redelivery.md` names, over the
    owning task, ready to paste: the owning task by identifier, the assertion the run named, and
    the file this delivery added. Say that it runs only after the person commits this delivery,
    because its own clean-tree stop refuses the pending state.
  - **Where one is**, this delivery rewrote a file the owning task bound, so that task's
    implementation no longer stands and the proof-only re-delivery would refuse. The test is this
    delivery's: the `test-author`, re-entered, rewrites it whole — never trimmed, never narrowed —
    against the nodes as they stand now; it joins this proof's `tests`; the proof's `## Notes`
    names the owning task, the assertion the run named and the file this delivery moved; and the
    suite runs again. The owning task's records stay as they are.
- **`setup`.** The harness or its environment did not stand up, so neither code nor test was
  reached. Run the suite again once, changing nothing. A second consecutive red the diagnosis reads
  as `setup` is a stop: the report quotes both diagnoses and hands the rerun invocation.

## The way out that is forbidden

**A test is never weakened, deleted, narrowed or rewritten to make the suite green.** A test edited
until it passes is one producer overruling the other where nobody would see it. Where a test an
earlier task owns must change, the producer that owns proofs rewrites it whole — in the owning
task's own proof-only re-delivery, or in this one where this delivery moved what that task bound —
and the runs on disk show any test that changed between attempts.
