# A red build

Read at step 4 whenever the build run is red, before anything is sent back.

## The excerpt a red run hands you

`--excerpt 40` prints the last forty lines of the step that failed, bounded by the runner. Take
that and go — never a command of your own over the log, which would guess at a reporter's format.
The excerpt is what goes back to a producer and what the report quotes. It is never a diagnosis's
input: the `failure-diagnostician` is handed the run's directory and reads all of it.

## A red build

**A red build is not the end of the invocation and it is not a stop.** Send what the run printed
back to the `task-implementer`, re-entered as `references/delegation.md` says — the source is its
to write — and run again under `<epic>-<slug>-build-2`, then `-3`. Every attempt keeps its
directory and log, so what failed on the way stays readable.

Giving up is a stop: report every run by path and what the last one printed, and write no record.
The validator would refuse a record over a red run anyway.

## A red only a test can answer

**A red only a test can answer is the test-author's, and it is answered before the record.** The
implementer writes no test, so where the fix lies in a test — one the registry requires beside a
file this delivery wrote, or an existing one this delivery's source no longer compiles under — no
return of the implementer turns the build green. «A build red whose fix lies only in files the
project declares as its tests is answered by the delivery's test author, before the implementation
record is written» (SPEC-004 R24).

1. **The implementer names the files the fix lies in**, re-entered with what the run printed.
2. **A script decides which of them are tests:**

   ```
   python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/project.py <project-root> --declared-tests <the target's key> <each path the implementer named>
   ```

3. **Where some paths are declared tests and some are not**, the implementer answers its own
   first and the build runs again; what is left of the red decides whose it is.
4. **Where every path is a declared test**, the implementer keeps its source and, re-entered once
   more, returns the whole mapping over that source; that final reply is what the record will be
   written from. Step 5 runs now, ahead of the record: the test-author is handed the implementer's
   transcript in the record's place, and the run and those paths under `red build`, and writes the
   proof whole, those files with it.
5. **A path the proof of another task names** is answered here only as step 6 answers a test an
   earlier task owns, read from that task's implementation record and this delivery's return —
   «A test the proof of another task names is answered here only where this delivery's files
   include one that task's implementation record names; otherwise the red is a stop»
   (SPEC-004 R24). Otherwise it is the stop below, naming the test and the task whose proof names
   it.
6. **Then the build runs again** under the next name. A red that now names source goes back to the
   implementer, one that names a test to the test-author, each re-entered. Green, the record is
   written over that run, and step 5 has run: go on to step 6 with the proof's return in hand.

## A red no change to this task's own files can answer

**A red no change to this task's own files can answer is a stop of its own, and never a retry.**
Two shapes:

- **Read from the tree:** after the implementer returns, `git status --porcelain --
  <target-source-root>` printing nothing means this delivery changed nothing under the target. The
  red was there before you began.
- **Read from the producer:** the fix lies only in files no record of this task names — another
  task's, or no task's, and not a test the target declares, which the shape above hands the
  test-author — and the implementer says so instead of writing there.

Either way, write no record, report the run by path with the files the fix would touch, and hand
`/plan-work` over this slug as the door; a corrective increment or an ordinary one is the person's
to choose. The orchestrating skill logs it as `outside-task`. Trying the same delivery again pays
for the run again and answers nothing.
