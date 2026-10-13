> [← Glossary](../siegard-glossary.md) · Previous: [The other skills and helper scripts](09-the-other-skills-and-helper-scripts.md) · Next: [Informal words you may meet](11-informal-words-you-may-meet.md)

## 10. The agents

Skills delegate judgment and production to these agents, always by their plugin-scoped name
(`siegard:<name>`). No agent has a shell. Only the two producers can write files.

| Agent | Used by | Does | Writes files? |
|---|---|---|---|
| `codebase-surveyor` | `/plan-work` | Surveys the code; returns inventory nodes | No |
| `backlog-decomposer` | `/plan-work` | Cuts the scope into epics and task skeletons | No |
| `execution-contract-binder` | `/plan-work` | Decides each task's `implements`; returns classified notes | No |
| `unstated-fact-decider` | `/plan-work` | Decides one unstated fact, blind to the task; returns node edits + log entry | No |
| `task-implementer` | `/implement-task` | Writes the source for one task and its implementation record | **Yes** |
| `test-author` | `/implement-task` | Writes the tests and the proof record | **Yes** |
| `failure-diagnostician` | `/implement-task`, `/review-change` | Says why each failure in a captured run failed | No |
| `coverage-auditor` | `/review-change`, `/reconcile` | Pairs criteria with tests; certifies a node's tests | No |
| `specification-conformance-reviewer` | `/review-change`, `/reconcile` | Reads one file against its nodes; returns findings + `read` | No |
| `standard-conformance-reviewer` | `/review-change`, `/check-source` | Reads files against the standard's reading rules | No |

**Delegation** = spawning one of these in a clean context. **Inline** = the fallback when a
session cannot spawn agents: the session applies the agent's file itself, and the report must say
so. `/reconcile` refuses to run inline if the same session wrote any node being judged.

---
> [← Glossary](../siegard-glossary.md) · Previous: [The other skills and helper scripts](09-the-other-skills-and-helper-scripts.md) · Next: [Informal words you may meet](11-informal-words-you-may-meet.md)
