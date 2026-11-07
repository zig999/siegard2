# Closing the plan

Read when the person declares the initiative over.

A work root serves one initiative, and the person says when it is over. The ask, with its why, is
the input, and either missing is a stop. Closing spawns no subagent and touches neither the
specification root nor the target source root.

1. **Resolve** `work_root/<slug>` through `project.py`, as for any invocation.
2. **The root must be under git and clean**, exactly as before any write: the closure diff is its
   own review. A root already holding `closure.md` is already closed: stop.
3. **Persist the ask under `intake/`**, like any scope.
4. **Read what this closure leaves standing**, from disk, before the marker is written — three
   commands, their output quoted whole in the report:

   ```
   python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/deliver.py --findings <delivery-root>/<slug>/review/<the newest review>.md
   python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/trace.py --owed <target-source-root> --plan <work-root>
   python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/plan.py --notes <work-root>
   ```

   The newest review is the last name `ls` lists under `review/`; where the delivery root holds
   none, say "no review". None of the three is a stop, and none is a judgment: they count the
   findings nobody routed, the nodes still owed a test and the notes still standing, so that
   "complete" is read beside them.
5. **Write `closure.md`** at the work root: prose, one sentence per line — the why as the person
   gave it, and the intake file it was read from. It is a marker, never a node.
6. **Derive without the specification root**: `python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/plan.py
   <work-root>`. The derivation is the seal: it still refuses a plan whose structure does not hold,
   and each task's `implements` stands as the record of which nodes the work addressed; its anchors
   drop, and the closure diff shows it.
7. **Report the closure** as step 6 reports — `--prepare`, the full report on disk, what `--render`
   prints — opened with what needs the person, as «A handoff opens with what needs the person»
   (SPEC-006 R1). Right after the opening, give **what this closure leaves standing**: the three
   counts, each with the command that printed it, never a verdict on whether the work was complete.
   Then offer the `/plan-work` invocation that opens the successor initiative's new slug under the
   same work root and project root, where the delivered work returns as inventory through the
   survey. Then stop.
