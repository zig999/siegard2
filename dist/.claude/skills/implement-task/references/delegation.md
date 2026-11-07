# Spawning, waiting and re-entering

Read before the first spawn at step 3, again at step 5 for its block, and again whenever a run
comes back red.

## Contents

- What step 3 hands the task-implementer
- What step 5 hands the test-author
- Waiting, stalls and re-entry

## What step 3 hands the task-implementer

```
task file:             <absolute path of work-root/task/<epic>/<slug>.md>
specification root:    <absolute path>
target source root:    <absolute path>
inventory:             <absolute path of each inventory node whose area reaches where this
                        task lands, one per line>
implementation slice:  <the --contract implementation output above, pasted whole>
standard:              <absolute path — omit this line where none was named>
authorized packages:   <each package the registry authorizes, by name — omit where it
                        authorizes none, or where no standard was named>
produces:              <each path the task's `produces` declares — omit where it declares none>
reference:             <each path the task's `reference` declares, resolved against the work
                        root — omit where it declares none>
earlier record:        <absolute path of the implementation record this re-delivery replaces —
                        omit on a first delivery>

You write no file under the delivery root: return the record's content as text.
```

Every path is absolute, because a path resolves only where the subagent's read scope reaches it.
The slice is pasted, not cited. Two lines carry a rule of their own:

- **Pass no reference the task did not name.** A subagent sent looking through `intake/` reads the
  scope, which this route keeps out of the writing. A `reference` path that resolves to nothing is
  a stop, named.
- **`authorized packages` is the whole list or an absent line**, never a selection: it is what a
  person approved, and narrowing it would be you deciding a manifest.

**Every path the returned record names is relative to the target source root**, the directory the
registry's commands run from, never to the repository around it: `produces` is matched to `files`
by spelling, and a registry scope reaches a file only under that anchor.

## What step 5 hands the test-author

```
task file:             <absolute path of work-root/task/<epic>/<slug>.md>
implementation record: <absolute path of the record step 4 wrote — or, where step 4 runs this
                        step ahead of the record, the implementer's transcript, whose final
                        reply the record will be written from>
red build:             <the build run's absolute path and each path its fix lies in — omit
                        unless step 4 runs this step ahead of the record>
target source root:    <absolute path>
proof slice:           <the --contract proof output above, pasted whole>
nodes:                 <the identity of each specification node the task implements, with the
                        absolute path of the specification root — omit where the task implements none>
standard:              <absolute path — omit this line where none was named>
underdetermined:       <every `UNDERDETERMINED, from the specification —` entry of the task's
                        `## Notes`, quoted whole — omit where the task carries none>
remainder:             <the node's identity, the assertion an auditor named as what would close
                        its certification, verbatim, and the proof file(s) the record named —
                        omit unless this is the proof-only re-delivery over a refused
                        certification, or a task carrying `stands`, where each criterion is
                        the assertion and the files are the task's `stands`>
reproduction:          <how the failure is observed — omit unless the task's criteria name a
                        failure that must stop happening>

You write no file under the delivery root: return the record's content as text.
```

`--outstanding` already quoted the `underdetermined` entries by their opening, so an entry it
printed and your collection lacks is your collection wrong. Quote them from the task file all the
same, which is what holds them.

## Waiting, stalls and re-entry

- **Wait for the notification.** A spawned subagent runs in the background, and the harness
  delivers a notification when it answers. You wait for that notification and nothing else —
  never a `sleep`, a scheduled wakeup, an agent listing or a message to the subagent — and read
  the return when the notification names it.
- **A subagent that stalls is never resumed.** Its partial work already stands on disk, and a
  stalled context may no longer hold a state the tree does. Spawn it again under the same task,
  naming what the prior attempt left in place and what remains, and let the new attempt read the
  tree.
- **A subagent that returned is re-entered on a red run.** It holds the task, the slice, the
  standard and every file it read, consistent with the tree it just wrote. Send what the run
  printed back to that same subagent where you can reach it, rather than spawning a fresh one that
  would read its way back to the same place. **It returns the whole mapping, revised — never the
  part that changed**: each record is written whole from one return.
- **Where you cannot reach a subagent that returned**, spawn it again and hand it the same filled
  block as the first time, plus what the run printed and what remains.

Either way every run keeps its name on disk and each record is judged against the tree at the end,
so which of these happened changes only what the delivery cost.
