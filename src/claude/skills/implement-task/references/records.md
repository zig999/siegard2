# Writing the two records

Read at step 4 before the implementation record is written, and at step 6 before the proof is.

## What the writer reads

- **`--from <the subagent's transcript>`** is the output file the harness names for the spawned
  subagent. The return is its final reply — or the `message` of a hand-back the harness confirmed
  delivered — read verbatim, never retyped from the notification that relays it.
- **`--from-text <file>`** names a file holding the mapping, where the step ran inline.

## What the writer stamps

Each record is a function of the return, the task file, the standard and the run. The writer
stamps, on both records:

- `target` — input 3's key, the root every path in the record is spelled from;
- the registry's own path and the pin of its text as read now, where a standard was named — omit
  `--standard` and `--standard-file` where none was;
- the run that passed — the build run on the implementation, the suite run on the proof; omit
  `--run` where nothing ran.

On the implementation it also stamps the pin of the task file on `task`; you never type it. It
equals `sha256sum <work-root>/task/<epic>/<slug>.md`, and covers the task and not the plan's index,
so adding an unrelated task stales no record. On the proof it stamps the SHA-256 of
`implementation/<epic>/<slug>.md` as it stands on disk on `implementation` — `sha256sum <that file>`
by hand — so rewriting the implementation and leaving the proof makes the validator refuse the pair.
The proof carries its own standard pin because the rules about how a project writes its tests reach
files no implementation lists.

A return carrying any stamped key is refused naming the key: the producer answers for what it
decided, and the writer stamps what you know. Every dependency the implementer added is in its
return under `installed`, carried through as returned.

## What the body holds

Exactly two headings, in order: `## What it is` from each `--what` line, defaulting to the return's
`summary`; `## Notes` from each `--note` line, defaulting to the literal line `None.` One sentence
per line. A `--note` carries what a reader is owed and no field holds:

- on an implementation that built the substrate, the sentence `references/substrate.md` names —
  which steps did not run and why;
- on a proof, every sentence this skill and its references say its `## Notes` names — the task
  whose delivery falsified an assertion, the record that left a remainder, the owning task, the
  assertion and the file this delivery moved — and, where earlier suite runs failed before one
  passed, each red run by path with the `cause` its diagnosis returned, one sentence per run. The
  writer refuses a proof whose notes name none of the red runs, naming them.

## Refusals and rewrites

The writer validates the record as `--node` does before writing it and writes nothing while it finds
a problem. A refusal is a composition error at the file that made it: correct it in the invocation
or send it back to the producer, never around it. The writer prints the path written and the
file's pin.

A record rewritten whole goes through `--replace`. A proof rewritten whole — the proof-only
re-delivery, or the restamp `references/finish.md` names — goes through `--write-proof --replace`,
with every `--note` line given again.

A disagreement the test-author recorded under `contested` is not settled here. It stays recorded:
the two producers exist so that one cannot overrule the other.
