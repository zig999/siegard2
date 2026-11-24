I did not commit. `app/lending/loans.py` holds a change this invocation did not make (3 lines added), and that stops the commit.

What I need from you: say what `app/lending/loans.py` is. It was clean before this invocation's first write and is modified now, so someone or something else touched it. I will not commit it, stash it, revert it or sweep it in with my files, and I will not narrow the commit to my two files while it is pending.

Where the delivery stands:
- `/implement-task task/fees/compute-late-fee` wrote `app/lending/fees.py` and `app/tests/test_fees.py`, and its validator passed.
- Both files are still uncommitted, together with your pending change to `app/lending/loans.py`.
- `bin/door.py --check commit` over the two files I wrote accepts. It does not decide the point above, which is the root holding a change I did not make.

Once `app/lending/loans.py` is settled (committed by you, or reverted), run `/implement-task task/fees/compute-late-fee` again. The tree will be clean at the start and the commit step will go through.
