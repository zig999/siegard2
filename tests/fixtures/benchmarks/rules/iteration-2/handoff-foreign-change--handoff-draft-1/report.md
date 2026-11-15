```
lending · task 0/1 delivered · phase delivery
```

2 questions, each answered on its own:

1. The loans file in app/lending has 3 added lines this task did not write, so the late-fee work is not committed yet: what should happen to that change?
   **Your decision**: Only you know whose that change is: 'aside' assumes it is separate work you handle; 'two' assumes it can stay uncommitted while the late-fee files go in alone.
   Pick one:
   - `aside`: You commit, move out or discard the loans change yourself, then tell me; I then commit app for this task.
   - `two`: I commit only the late-fee code and its test; the loans change stays as it is, uncommitted.
   If none is taken: Nothing is committed; the late-fee code, its test and the loans change all stay uncommitted.

2. After the late-fee commit, which step comes next?
   **Your decision**: This waits on the commit above; the review assumes this task's delivery record is on disk, and the check found none yet.
   Pick one:
   - `reconcile`: Re-reads the named files against the specification and rebinds what it clears; no script checked it here.
   - `review`: Excluded as things stand: the delivery check exits 2 and there is no implementation record for lending yet.
   If none is taken: The task stays at 0/1 delivered until the commit lands.

Full report: /tmp/rh/p/h07/.git/siegard/handoff/20261115T163515Z-implement-task.md
