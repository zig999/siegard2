# Spawning, waiting and re-entering

Read before the first spawn at step 3, and again whenever a run comes back red.

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
