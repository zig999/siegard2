---
name: siegard-progress
description: Reads one live initiative's plan and delivery records from disk and reports every task it maps as one row of a table — a status column and a detail column stating why — so a person running this repeatedly, for example from /loop every few minutes, can watch a single initiative's progress without reading a prose report scoped to the whole project. Infers the initiative when exactly one is live under work_root; stops and lists the live slugs when more than one exists. It writes nothing and decides nothing — every table is recomputed from the plan graph and the delivery records at the moment of asking, never remembered. Use when a human wants a compact, repeatable read of one initiative's tasks — what is done, what is blocked, what is waiting, and on what. Not for the project's specification soundness, trace drift, or git state — that is /siegard-status, over the whole project.
effort: low
---

You answer one question — inside a single live initiative, what is the status of every task it
maps — as a table, and you stop. Everything you state is derived from disk at the moment of
asking, the same discipline `/siegard-status` holds over the whole project: this framework
stores no status anywhere, on purpose, so the only honest report is the one recomputed by the
commands below.

## Required inputs

A missing input is a stop, not a default:

1. **the project root** — where `siegard.json` lives. Named by the human; inferred rather than
   named, its absence is a stop.
2. **the initiative** — the live one under `work_root` whose tasks this table covers. Inferred
   when `work_root` holds exactly one directory without a `closure.md`; where it holds more than
   one, that is a stop — list every live slug and ask which one this run watches.

Run `python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/project.py <project-root>` once, before anything
else — the one reader of `siegard.json`, held to `${CLAUDE_PLUGIN_ROOT}/schemas/project.json`.
`work_root`, `delivery_root`, `targets` and `specification_root` answer only from here; where the
file is missing or a field is absent, that absence *is* the status: report it with the
`/siegard-config` invocation ready to paste, and stop.

`${CLAUDE_PLUGIN_ROOT}` is set where this skill runs as an installed plugin. Where it is not,
the plugin root is the directory that holds `schemas/` and `bin/` side by side — in a vendored
install, the `.claude/` directory this skill's tree sits under.

## The order

Everything below is read-only.

1. **List `work_root`.** A directory holding `closure.md` is closed history and never a
   candidate. Zero live directories is a stop — there is nothing to report. Exactly one live
   directory is the initiative. More than one is a stop: name every live slug and ask which one
   this run watches.
2. **Confirm the plan holds together and is current.**
   `python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/plan.py --check <work-root>/<slug> <specification-root>`.
   Where this reports a problem, or reports the derived plan `STALE`, that report *is* the
   status — quote it verbatim and stop. A table built over a plan the framework itself will not
   certify would present rows nothing has actually checked.
3. **Read every task the plan maps.** `<work-root>/<slug>/plan.json`, held to
   `${CLAUDE_PLUGIN_ROOT}/schemas/plan.json` — every entry with `"kind": "task"` is one row
   waiting for a status. Its `id` already carries its epic (`task/<epic>/<name>`), and the
   `epic` field names it directly; the array's own order groups by epic for free, since ids
   sort that way.
4. **Ask the delivery what is not yet whole, once per target.** `targets` may declare more than
   one key; a status that read one of them would answer for a target nobody asked about. For
   every key `project.py` printed:
   `python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/deliver.py --outstanding <delivery-root>/<slug> <work-root>/<slug> <target-source-root> <specification-root>`.
   This names, one line per task, every task without both an implementation record and a proof
   record, and why. A task `plan.json` lists that this command never names is done — implemented,
   and its own proof stands; the command falls silent about it by design, so its absence from the
   output is itself the fact.

## Deriving each row

For every task `plan.json` holds, sorted in `plan.json`'s own order:

- **Not named anywhere in the target's `--outstanding` output → `done`.** Detail: "implemented
  and proven" — stated once here, since the command that would have said otherwise said nothing.
- **Named with `implemented, and no proof record holds it up` → `implemented, unproven`.**
  Detail: that clause, verbatim.
- **Named with `no record` and a standing `BLOCKING, from the specification —` entry →
  `blocked`.** Detail: the joined reason clause verbatim; quote every
  `BLOCKING, from the specification —` entry whole beneath the table, keyed to its task — only a
  person settles these, so the words themselves belong in the report, not just a count.
- **Named with `no record`, no `BLOCKING` entry, and `waits on` another task or "produces the
  substrate every other delivery waits on" → `waiting`.** Detail: the joined reason clause
  verbatim.
- **Named with `no record` and neither of the above → `ready`.** It sits in this run's
  `deliverable now` set. Detail: "deliverable now".

Where a task also carries `UNDERDETERMINED, from the specification —` entries, they bar nothing
and never change the status; quote them the same way as BLOCKING entries, beneath the table, so
whoever writes the task's tests still receives them whole.

Where `targets` declares more than one key, repeat this whole derivation and table once per
target — the substrate-wait detail is target-specific — each one headed with the target's own
name.

## The report

One table per target (one table total where `targets` names exactly one), in this order:

- a header naming the project root, the initiative slug, and — where more than one target
  exists — which target the table answers over;
- the table itself, columns in this exact order: `Task | Epic | Status | Detail`;
- directly beneath, every BLOCKING and UNDERDETERMINED entry any row's Detail referred to,
  quoted whole and keyed to its task id;
- nothing else. No specification soundness, no trace drift, no git state, no session recap —
  `/siegard-status` already answers those, over the whole project, and restating them here would
  be a second home for an answer that already has one.

## What you never do

- Report a percentage, a "nearly done," a health grade, or any figure no command printed.
- Build a table over a plan `--check` reports as stale or with a problem — quote the problem and
  stop instead of guessing at rows.
- Write, edit, bind, prune or derive anything; every command above is a read.
- Answer from memory of an earlier run, this conversation, or auto memory without disk
  confirming it now — a table this skill exists to run repeatedly is exactly the one a stale
  memory would corrupt silently.
- Choose the next task, settle a BLOCKING note, or judge which target matters more — the table
  hands rows and takes none of them.
