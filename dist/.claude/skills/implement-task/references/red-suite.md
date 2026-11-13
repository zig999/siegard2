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
implemented with no proof, the true state. Report the run by path and the tests that failed.

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

Where an earlier step failed instead — a typecheck or a lint reaching the files just written — no
diagnosis is owed: the log names the file, and the red goes back to the producer whose file it is,
as a red build does.

## The five ways out

The diagnosis returns one of the contract's four causes; `test` splits by who owns the failing
test, which you know and it is not told. Every rerun is the same command; `--next` names it,
`<epic>-<slug>-suite-2`, then `-3`.

| cause | owner of the failing test | what happens | waits on a person |
|---|---|---|---|
| `code` | — | the findings go to the `task-implementer`, re-entered; the suite runs again | no |
| `build` | — | the suite's own compile failed; the red goes to the producer whose file the compiler named, re-entered; the suite runs again | no |
| `test` | this delivery | the `test-author`, re-entered once, rewrites it whole; the suite runs again | on a second red |
| `test` | an earlier task | the exit `deliver.py --test-owner` prints: see below | on `re-deliver` |
| `setup` | — | nothing goes to a producer; the suite runs again once | on a second `setup` |

- **`code`.** Where the implementer returns that the fix lies only in files no record of this task
  names, the red is the stop `references/red-build.md` names for a red no change to this task's own
  files can answer.
- **`test`, on a test an earlier task owns.** Its exit is printed, never read from the assertion,
  and only for this cause: a `code` red is the implementer's whoever owns the test. Name each
  failing test as `<file>::<name>`, as the run printed it:

  ```
  python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/deliver.py --test-owner <delivery-root> <task> <file>::<name> [...]
  ```

  - **`adopt`** — every owning plan is closed: «Where every plan whose proof names the test is
    closed, this delivery adopts the test whatever the files share» (SPEC-004 R25).
  - **`rewrite`** — every live owner shares a file with this task, which moved what it bound.
  - **`re-deliver`** — a live owner shares no file. Do not edit that test: stop, and hand the
    proof-only re-delivery `references/redelivery.md` names over each owner listed, ready to paste:
    the task, the assertion the run named, the file this delivery added. It runs once the person
    commits this delivery: its clean-tree stop refuses the pending state.

  On `adopt` and `rewrite`, the `test-author`, re-entered with the run, the diagnosis and each
  owning proof's entry, rewrites the test whole — never trimmed, never narrowed. It joins this
  proof's `tests`, a `--note` names each owner and its plan, and the suite runs again. Returned
  under `contested`, it keeps a condition a node still states: a contradiction only a person
  settles — stop, quote the entry whole, hand `/analyse` over the node.
- **`test`, on a test this delivery wrote.** The specification settled it against the test: the
  `test-author`, re-entered once with the diagnosis whole and its own entry, rewrites it whole as
  above. A second red on it, or a test it leaves under `contested`, is the stop `producers`; the
  report quotes both whole.
- **`setup`.** The harness or its environment did not stand up, so neither code nor test was
  reached. Run the suite again once, changing nothing. A second `setup` in a row is a stop: the
  report quotes both diagnoses and hands the rerun invocation.

## The way out that is forbidden

**A test is never weakened, deleted, narrowed or rewritten to make the suite green.** A test edited
until it passes is one producer overruling the other where nobody would see it. The producer that
owns proofs rewrites a test whole, in the owning task's proof-only re-delivery or in this one, and
the runs on disk show any test that changed between attempts.
