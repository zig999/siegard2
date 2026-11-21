#!/usr/bin/env python3
"""Bench hook: appends every Skill and Agent call to the log named by its argument and denies it,
so a benchmark reads a session's first act without running what it invokes."""
import json
import sys
from datetime import datetime, timezone

event = json.loads(sys.stdin.read() or "{}")
tool = event.get("tool_name")
given = event.get("tool_input") or {}
with open(sys.argv[1], "a", encoding="utf-8") as log:
    log.write(json.dumps({"at": datetime.now(timezone.utc).isoformat(), "tool": tool,
                          "skill": given.get("skill"), "agent": given.get("subagent_type"),
                          "args": str(given.get("args") or given.get("prompt") or "")[:400]})
              + "\n")
print(json.dumps({"hookSpecificOutput": {
    "hookEventName": "PreToolUse", "permissionDecision": "deny",
    "permissionDecisionReason": "Recorded by the benchmark. The call is not run in this "
                                "benchmark; end the session now."}}))
