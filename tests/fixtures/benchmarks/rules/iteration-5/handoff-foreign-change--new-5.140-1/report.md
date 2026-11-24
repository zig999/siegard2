```
lending · task 0/1 delivered · phase delivery
```

The late-fee code and its test are written and pass, but not committed: the loan file also holds a change I did not make. May I commit only my two files?
   Pick one:
   - **Recommended** `a`: Commit only the fee file and its test, leaving the loan file exactly as it is. This is a judgment: neither new file reads the loan file's change, and the commit is easy to undo. It would change if that change belongs to this task, or you want it committed first.
   - `b`: You commit the loan file's change or set it aside first; then I commit my two files.
   If none is taken: Nothing is committed; the new files stay untracked and the loan file stays modified.

   ```
   commit only app/lending/fees.py and app/tests/test_fees.py
   ```

Full report: /tmp/an8/w22/.git/siegard/handoff/20261124T225207Z-implement-task.md
