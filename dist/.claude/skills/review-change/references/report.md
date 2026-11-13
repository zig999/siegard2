# The report

Read at step 6, after `handoff.py --prepare` has printed its skeleton.

Write it through `handoff.py --save-report` and hand the person what `handoff.py --render`
prints, as step 6 states. The report holds every item below, in this order.

1. **The findings as counts before any one of them**, exactly as this prints them:

   ```
   python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/deliver.py --findings <delivery-root>/review/<review-name>.md
   ```

   By pass, the conformance ones by `kind`, the standard ones by the rule cited, the failures by
   `cause`, and by file — with, beside each group, the route item 19 names for findings of that
   shape. The opening carries this grouping's one line: the person reads how many findings go
   where before reading any, and decides over a group where the group is what they would decide
   over. A count is never a verdict, a group is never ranked, and a route named beside a count is
   where a repair would go, not a decision that it goes there.

   Where it prints disagreements the proofs recorded under `contested`, carry every one as it
   printed it — whole, under its task, said as the person's to settle — and never fold, shorten,
   rank or answer one: «A review's report relays, whole and by task, every disagreement the proof
   of a task it reviews recorded under `contested`, as the person's to settle; the review neither
   settles nor ranks it.» (SPEC-004 R29)
2. Every finding, grouped by pass, each with its evidence and what it costs.
3. **Which passes did not run, and which input was missing.** This line is not optional: it
   separates a clean review from a narrow one.
4. Every path the tasks' records name that the file set does not hold, because the target source
   root no longer holds it or it lies outside that root, each said as not read.
5. Every criterion the coverage pass did not find covered, and what is unexercised in each.
6. Every test that pass found bearing on no criterion, and what each asserts: a fact about what
   this plan's criteria reach, handed as a reading and never as a verdict.
7. Every node the tasks implement that no test demonstrates, with the reason the proof gives or
   that it gives none, and the state each certification came back with.
8. The standard: which of its rules were in scope over this file set, and which it leaves to a
   tool.
9. The paths no rule of the standard reaches, from `python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/deliver.py
   --standard <the standard's path> --reach --for <every path of the file set, one --for each>`,
   apart from the rules that do. «A review reports the paths of its file set that no rule of the
   standard reaches, apart from the rules that do.» (SPEC-007 R2) Say it as a fact about the
   registry, never as a finding: the reading was clean over those paths because nothing was read
   against them.
10. **The rules left to a tool.** Name, for each, whether the step that decides it ran, and how
    many rules rest on each step that did; a rule left to a tool that never ran is unanswered.
    - Say what a step that ran and passed settles: that the command exited 0. Whether the command
      was configured to decide the rules resting on it is the registry's to know, never this
      framework's — a linter with no rule loaded for the files it read exits 0 over every one of
      them, and a scanner with no ruleset does the same.
    - The number is what the person can act on: one step carrying twenty rules is worth their
      look.
    - Name the constraints the registry's steps decide and, apart, the ones no step decides: those
      are held by reading alone, and a green run settles nothing about them.
11. Every artifact the registry presupposes and the tree does not hold, with the rules each one
    takes with it: a review reporting two findings over a standard whose substrate is missing has
    reviewed a fraction of it, and this line gives the fraction. The way out is a task declaring
    the artifact in `produces`, planned through `/plan-work`.
12. **The run**: which steps were executed and where each came from — the registry, or the
    invocation — how it ended, how many failures were counted, and where the output sits. Name any step a
    rule expects and the registry declares no command for: that rule was decided by nothing.
13. **The trace**: the drift counts by class over this target as the situate step read them, and
    the route each class takes — `--prune` for the bindings no rebind can repair, `/reconcile` for
    the `code` and `moved` classes on files outside this review, `--release` for a bound file the
    tree no longer holds. Say plainly that this is not a finding and settles nothing about the
    change: it says whether the link back to the specification still describes this tree, which
    no pass asks. Where a suppression receipt came back, say how many were held back and under
    which target, that the rules a reading decides went unread over those files, and offer the
    paths `--all` lists — for this review's file set, or for a `/check-source` over the same list.
14. **What the conformance pass bound, and what it left owed, kept apart.**
    - The nodes restamped over the reviewed files, as the bind's receipt names them, and the nodes
      it did not write, each with the finding that held it — a `collateral` mark said apart from a
      contested one.
    - Where the record and the returns were written.
    - `trace.py --check` over the target reports the drift that remains; `trace.py --owed` reports
      what this pass found and no bind could close, which `--check` cannot see. Neither is a
      verdict on the change, and no route is chosen here for either.
    - Apart from both, every finding the fold placed in the record's `notes` because it names a
      node no reviewed file is bound to; the note ends "owed a route of its own". `--owed` reads a
      record's nodes and its `unstated`, never its notes, so this report is the one place such a
      finding is handed on, with its node, its file and its evidence.
15. What this framework does not review at all, so four passes are never mistaken for every pass.
16. What the passes looked past as another judgment's.
17. Which passes, if any, ran inline instead of in a subagent, and why.
18. The validator's final output, verbatim.
19. **Where the repairs live**, as routes and not as a reading of the findings:
    - source, or a criterion recorded unmet, is answered by `/implement-task` over the same task;
    - a fact stated in source that no node holds is produced by extending the specification
      through `/analyse`, and reaches the task through `/plan-work`;
    - a rule of the standard that seems wrong is changed by whoever owns the registry.

    This skill hands nothing forward as an invocation: which route any finding deserves — or
    whether it deserves one at all — is the decision this pass does not make. Naming where a
    repair would go is not choosing to make it.
