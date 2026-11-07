# Spawning, waiting and re-entering

Read before the first spawn at step 3, and again whenever a run comes back red.

A spawned delegation runs in the background and the harness delivers a notification when it
answers; the session waits for that notification and nothing else — never a `sleep`, a scheduled
wakeup, an agent listing or a message to the delegation, each of which is a turn spent reading
nothing — and reads the return when the notification names it.

A spawned subagent that stalls is never resumed. Its partial work already stands on disk — a
draft implementation, a run directory, a half-written record — and resuming a stalled context
asks it to continue from a state it may no longer hold, where a fresh one asks it to continue
from the one thing that is actually still true: what the tree now shows. Spawn again under the
same task, naming what the prior attempt already left in place and what remains, and let the new
attempt read the tree rather than inherit the old context. Nothing here is lost by this: the
record this step writes is judged against the tree at the end, never against how many attempts it
took to get there.

**A delegation that returned is the opposite case, and a red run is where it comes up.** It holds
the task, the contract slice, the standard and every file it read, all of it consistent with the
tree it just wrote — the state a stalled context is doubted for holding is exactly the state this
one has. So what the run printed goes back to that delegation where the session can reach one
that has returned, rather than to a fresh spawn of the same agent: a fresh spawn is handed the
same block again and reads its way back to where the first one already stood. **What it returns
is the whole mapping, revised — never the part that changed.** Both records are rewritten whole,
so a delta would leave a record assembled out of two answers, which is what an amended record is
refused for.

Where the session cannot reach a delegation that has returned, spawn again, and hand the same
filled block as the first time plus what the run printed and what remains. Either way the runs
keep their own names on disk and the record is judged against the tree at the end, so which of
the two happened changes nothing about the delivery — only what it cost.
