Nothing is committed. I stopped at the last step of `/implement-task task/fees/compute-late-fee`, and the commit is yours to unblock.

`app/lending/loans.py` has an uncommitted change that this invocation did not make. It adds `MAX_RENEWALS = 1` after the `Loan` class. `git status --porcelain -- app` printed nothing before the first write, so the change appeared during the run. The commit covers the whole `app` root, and a root holding a change I did not make is a stop. I did not widen the commit to take the change, and I did not commit only my two files.

What the invocation wrote, still uncommitted and validated:
- `app/lending/fees.py`
- `app/tests/test_fees.py`

`bin/door.py --check commit` accepted the commit, but its two `not decided:` lines are not an acceptance. The file `loans.py` is the reason I stopped.

Which way to go depends on where the `MAX_RENEWALS` change came from, and nothing on disk says. I can't recommend one, so it is your call:
- If it is yours and should stay, commit it yourself or tell me to. Then the commit of `fees.py` and `test_fees.py` can go ahead.
- If it should not be there, put it back as it was. Then I commit the two files.

Once `app` is clean apart from my two files, run `/implement-task task/fees/compute-late-fee` again, or tell me to commit.
