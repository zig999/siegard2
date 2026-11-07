# The project's standard, and the invocation's steps

Read with the inputs, and again at step 1 when the registry is taken in. Two optional inputs, and
between them they decide whether two of the four passes run.

## The project's standard

**The project's standard** is the path to the registry of rules the project set for itself, in
the project's own tree. Its contract is `${CLAUDE_PLUGIN_ROOT}/schemas/standard.json`, and a
consumer holds a registry to it with `deliver.py --standard <file>`; a standard that does not hold
together is a stop, reported verbatim, and fixing it belongs to whoever owns it.

The standard resolves in one order, from the same `project.py` run, and the report says which step
answered:

1. **A naming in the invocation wins here**, unlike the roots.
2. Where the invocation names none, the file answers **for the target**: `project.py` prints one
   `standard:` line for a one-target project, or one `standard <target>:` line per target the file
   declares one for. The line for the target this review names is the answer — never another
   target's line.
3. Where neither answers — no naming, no file, the file not declaring the field, or the field
   declaring no entry for this target — the standard joins the single stop of absent inputs: name
   it, or declare it through `/siegard-config` for this target, and the stop's report carries that
   invocation ready to paste.

Reading the file is no default an absent optional input became: the file is the consumer's own
declaration, read from disk. `null` there declares that the project authored none for this target:
the standard pass does not run, and the record says so in those words — a different absence from
an input the invocation did not name. A naming that overrode a differing file is reported with
both. Below, a standard "named" means resolved by either step.

**The commands are the registry's.** A registry declares how the project is installed, checked
and run, and those steps are what the capture executes. Commands left to the person to retype at
each invocation go untyped, and the registry's tool-decided rules go undecided. Every string stays
the project's: nothing here composes a build or a test command or infers one from what a tree looks
like.

## Steps the invocation names, or a run already captured

Each step is a name and a command, as `${CLAUDE_PLUGIN_ROOT}/bin/run.py` takes them, or the input
is a directory under the delivery root's `run/`.

- Steps given here run after the registry's, under the same capture.
- A name the registry already declares is a stop rather than an override: two commands under one
  step name cannot both be the one a rule's outcome is read against.
- A run named instead of commands is used as it stands, and nothing is executed.

The failures pass runs where any of the three produced a run, and does not where none did. An
absent optional input never becomes a default: a review reported as clean over a pass that never
ran is the failure that rule exists to prevent.

## At step 1: take the registry in

Where a standard is named, take it in and read it before anything is run:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/deliver.py --standard <the project's registry> --against <target-source-root> --specification <specification-root>
```

A registry that does not hold together is a stop, reported verbatim: a review against one reports
a conformance nobody has. The command prints:

- the split — how many rules a reading decides, how many a tool does, and the names of the steps
  those expect;
- every command with its step and its bound, which is everything the capture composes its run
  from;
- against the specification, which constraints each step decides and which no step decides.

Do not open the registry's text here: its rules are the standard pass's subagent to read, and that
pass is handed the path.

**An artifact the registry presupposes and the tree does not hold is not a stop.** A review
reviews what exists, and refusing would withhold the one report that says the project was never
set up. It changes what the review reports: the steps those rules would be decided by cannot
exist, so the failures pass has nothing to run and every rule the absence names goes unanswered,
while the rules a reading decides are still applied. Keep what the command printed and carry it
into the report.

Then note the registry's own path, relative to the target source root, and the SHA-256 of its text
as read now — `sha256sum <target-source-root>/<path>`. Nothing is copied: the record points at the
project's own file, the same way `files[].path` points at code. That pin cites what this review
read when it was written, not a standing guarantee; the registry is free to keep evolving.

The standard is read at step 1 rather than at its own pass for two reasons of order: the capture
runs the commands this registry declares, and the standard pass is handed the registry's own path,
which has to exist before the pass is spawned.
