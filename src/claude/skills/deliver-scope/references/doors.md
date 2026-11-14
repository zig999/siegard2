# The doors this run takes

Read at step 3 where a delivery stopped, before `references/stops.md`.

The ask that invoked this run is the go-ahead, with or without a goal: «The orchestrating entry
point takes the door a derived recommendation names where that door is an entry point the route
invokes and `bin/door.py --check` accepts it» (SPEC-006 R7). Take one the report recommends as
derived or a bullet below names, whose entry point is `/plan-work`, `/implement-task`,
`/review-change` or `/reconcile`, that `door.py --check` accepts, and that no `decided:` line of
this run took over the same task. A judged door is taken only under a grant: «takes the door a
judged choice leaves only under a grant the person armed» (SPEC-006 R7); an armed goal arms none,
and the three reserved questions are never taken. With a grant armed, run `bin/grant.py --decide
<project-root> --latest <the stopping skill> --after <the log commit before it ran> --slug
<slug>` first: `take:` prints a derived door's `decided:` line, `judge:` a judged door (below),
`stop:` or no answer leaves the stop; the same-task rule binds them.

Write `decided: <door> — <criterion> — <deciding fact>` to the log, copied from the report, and
commit the log. Invoke the door as handed — it commits what it wrote — and resume step 3:

- **A record carrying `stands` the writer refused**: `/reconcile` as `/implement-task` handed it
  from the writer's `door:` line; its premise's `said` is the ask this log quotes. Commit the runs
  the stopped delivery captured under `run/`, each `passed`, before invoking it, as
  `deliver-scope <slug>: runs <task>`. A second refusal ends the run.
- **A task waiting on a re-bind**: `/plan-work` over the slug, as `--outstanding` names it.
- **A fact no node states**: the decided-fact `/plan-work` handed beside `/analyse`. A fact
  returned as contradicted ends the run.
- **Any other derived door** to `/plan-work`, `/implement-task` or `/review-change`: as handed.

## A judged door, under a grant

`judge:` lists the doors and the budget this initiative has left.

1. Spawn a `siegard:door-decider` subagent, its judgment at
   `${CLAUDE_PLUGIN_ROOT}/agents/door-decider.md`, handing it four things: the doors `judge:`
   listed, each with what it does and what it leaves; the facts each rests on, by path, the runs
   and the diagnoses among them; the ask's scope, quoted; and the budget left. Never the
   conversation, the attempts' story, the grant, or what ends a goal.
2. Save its return as the subagent's own reply.
3. `chosen` or `excluded` naming a door: take it, its `decided:` line carrying the rung it named
   and ending `(grant sha256 <mark>)` as `judge:` printed. Anything else — `reserved`, `none`, or
   the door that ends the run — is the stop it was.
