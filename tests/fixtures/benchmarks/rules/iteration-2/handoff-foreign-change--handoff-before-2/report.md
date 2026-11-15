```
lending · task 0/1 delivered · phase delivery
```

Nothing is committed: app/lending holds a loans change this task did not make. How do I commit the late-fee code and test?
   Pick one:
   - **Recommended** `files`: Commit only the late-fee code and its test; the loans change stays uncommitted. A judgment: it keeps a change I cannot attribute untouched, and one revert undoes it. It would change if the loans change belongs to this task.
   - `wait`: You settle the loans change yourself; then I rerun the task's commit.
   - `review`: Excluded: review refuses, no delivery record exists yet.
   - `reconcile`: Re-reads named files; commits nothing here.
   If none is taken: Nothing is committed; all three changes stay as they are.

Full report: /tmp/rh/p/h06/.git/siegard/handoff/20261115T163515Z-implement-task.md
