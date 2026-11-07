# A red build

Read at step 4 whenever the build run is red, before anything is sent back.

## The excerpt a red run hands you

`--excerpt 40` on each of those runs is what a red one hands you: the last forty lines of the
step that failed, printed before the record and bounded by the runner rather than by you. Take
that and go — never a command of your own over the log. A whole failing log is unbounded, and
cutting one down by a pattern that looks like a failure is this framework guessing at a
reporter's format, which it refuses everywhere else and which the runner's own `--help` declines
by name. The excerpt is what goes back to a producer and what the report quotes. It is never a
diagnosis's input: the `failure-diagnostician` is handed the run's directory and reads the whole
of what it holds, which is why the record names the log rather than carrying it.

## A red build

**A red build is not the end of the invocation and it is not a stop.** Send what the run printed
back to the `task-implementer`, re-entered as `references/delegation.md` says — the source is its to write, and
a skill that patched a file to turn a build green would be the writer nobody separated from the
witness — and run again under `<epic>-<slug>-build-2`, then `-3`. Every attempt keeps its directory and its log, because the
runner refuses a name that already exists. That refusal is the whole reason this invocation is
allowed to iterate at all: what failed on the way is readable afterwards by somebody who was not
here.

Giving up is the stop. Report every run by path, what the last one printed, and write no record:
a record over a red run is refused by the validator anyway, and the point of stopping here is that
it was never composed.

**A red only a test can answer is the test author's, and it is answered before the record.** The
implementer writes no test, so where the fix a red names lies in a test — one the registry
requires beside a file this delivery wrote, or an existing one this delivery's source no longer
compiles under — no return of the implementer turns the build green. «A build red whose fix lies
only in files the project declares as its tests is answered by the delivery's test author, before
the implementation record is written» (SPEC-004 R24). Which files the fix lies in is the
implementer's to say, re-entered with what the run printed; which of them are tests is a script's:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/project.py <project-root> --declared-tests <the target's key> <each path the implementer named>
```

Where it calls every path a declared test, the implementer keeps its source, and re-entered once
more it returns the whole mapping over that source; that final reply is what the record will be
written from. Step 5 runs now, ahead of the record: the test author is handed the implementer's
transcript in the record's place, and the run and those paths under `red build`, and it writes
the proof whole, those files with it. A path the proof of another task names is answered here only as step 6 answers a
test an earlier task owns, read from that task's implementation record and this delivery's return:
«A test the proof of another task names is answered here only where this delivery's files include
one that task's implementation record names; otherwise the red is a stop» (SPEC-004 R24) — the stop
below, naming the test and the task whose proof names it. Then the build runs again under the next
name. A red that now names source goes back to the implementer and one that names a test to the
test author, each re-entered; green, the record is written over that run, and step 5 has run —
go on to step 6 with the proof's return in hand. Where some named paths are declared tests and
some are not, the implementer answers its own first and the build runs again: what is left of the
red decides whose it is.

**A red no change to this task's own files can answer is a stop of its own, and never a retry.**
Two shapes, and the first is read from the tree rather than from anyone's account of it: after the
implementer returns, `git status --porcelain -- <target-source-root>` printing nothing means this
delivery changed nothing under the target, so a red build is the tree's own — it was red before
this invocation began, and no return of this task's producer can turn it green. The second is
read from the producer: the fix a diagnosis or the run names lies only in files no record of this
task names — another task's, or no task's, and not a test the target declares, which the shape
above hands the test author — and the implementer says so rather than writing there. Either way, write no record, report the run by path with the files the fix would touch,
and hand `/plan-work` over this slug as the door — a corrective increment or an ordinary one, the
person's to choose. The orchestrating skill logs it as `outside-task`; trying the same delivery
again pays the run again and answers nothing.
