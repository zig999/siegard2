# Writing the two records

Read at step 4 before the implementation record is written, and at step 6 before the proof is.

## The implementation record

`<the delegation's transcript>` is the output file the harness names for the spawned agent: the
return is read from its final reply — or from the `message` of a hand-back the harness confirmed
delivered — verbatim, never retyped from the notification that relays it. Where the step ran inline, the mapping is in a file and `--from-text <file>` names it. The
record is a function of that return, the task file, the standard and the run: the writer stamps
`target` — input 3's key, the root every path in the record is spelled from, which the
validator resolves the record at and never the one an invocation happened to name — the pin of
the task file on `task`, the registry's own path and the pin of its text as read now, and the
build run that passed. Omit `--standard` and `--standard-file` where no standard was named, and
`--run` where nothing ran. A return carrying any of those keys is refused naming the key: the
producer answers for what it decided, and what the invocation knows is stamped here. Every
dependency the agent added is in its return under `installed`, and the writer carries it
through as returned.

The body is the writer's as well, exactly two headings in order: `## What it is` from each
`--what` line, defaulting to the return's `summary`; `## Notes` from each `--note` line,
defaulting to the literal line `None.` One sentence per line. `--note` carries what a reader
meeting the record is owed and no field holds: where this delivery built the substrate, the
sentence `references/substrate.md` names — which steps did not run and why — so the record
does not read as a project that builds. The writer validates the record as `--node` validates
one before writing it and writes nothing while it finds a problem; a refusal is a composition
error at the file that made it, corrected in the invocation or sent back to the producer, never
worked around. It prints the path written and the pin of the file.

## The proof record

The same `target`, and — where a standard was named — the same stamps: the registry's own path,
the pin of its text as read now, and the suite run that passed on this record too, exactly as
the implementation carries its own — the rules about how a project writes its tests reach files
no implementation ever lists, so a departure from one is the proof's to disclose and resolves
against the pin the proof itself carries. The writer reads `implementation/<epic>/<slug>.md`
from disk and stamps its SHA-256 on `implementation` — `sha256sum <that file>` by hand — which
says which version of that record these tests were written against, and is what makes a
re-delivery honest: rewrite the implementation later and leave the proof alone, and the
validator refuses the pair instead of letting tests stand that claim to prove criteria the
source now satisfies some other way.

A disagreement the author recorded is not settled here. It stays recorded: this invocation holds
two producers precisely so that one cannot overrule the other, and resolving it now would discard
the signal.

What `--note` carries on a proof is every sentence this skill and its references say its `## Notes` names — the task whose delivery falsified an assertion, the record that left a remainder, the
owning task, the assertion and the file this delivery moved — and, where earlier suite attempts
failed before this one passed, each red run by path with the cause its diagnosis returned, one
sentence per run. The diagnosis otherwise lives only in the conversation, and a reader meeting
three run directories beside one proof deserves the sentence that says why; the writer refuses a
proof whose notes name none of them, naming the runs, so a red attempt is never left unnamed by
oversight. A proof rewritten whole — the proof-only re-delivery, or the restamp step 7 names —
goes through `--write-proof --replace`, with every `--note` line given again.
