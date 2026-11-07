# Adoption

Read at step 2 where the person named the mode. The same order runs, with four differences, each
held by the scripts rather than by this prose.

## 1. Stage with `--adopt`, over the ledger

Where `/analyse` wrote a ledger beside survey or intent material — its handoff names it — pass it,
and the files the person keeps out with `--outside`:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/trace.py --stage <target-source-root> <specification-root> \
    <slug> <workspace> --adopt --ledger <ledger.md> [<each named path>] \
    [--outside <path> ...] [--certify <certifications file>]
```

- The file set is the material's areas — on intent material, the files it governs, never its
  tests — or the named subset of them.
- Each file's judge is handed the candidates the ledger landed that file's own facts in: «Every
  fact line of the material lands in a node or is left out with a stated reason» (SPEC-005 R8), so
  the pack is the nodes that file's facts reached and not the whole increment.
- A file no fact names is handed no judge and stays unbound. The candidate index still lists every
  candidate with the files it is read on, for a fact a judge meets that its own pack does not
  settle.
- Where no ledger exists, name every candidate with `--node` instead, and every file's judge reads
  them all.
- No trace is needed either way; a file the trace already binds keeps its own node set beside the
  candidates.
- No candidate is omitted and none is answered by a run: its reading decides whether it is bound
  at all.
- A file the target declares as a test is refused in the set: a test is never adopted source, and
  the refusal hands the `--certify` entry it takes instead — a test offered as a node's proof rides
  the same staging (`references/certify.md`).

## 2. Judge and fold as always

The premise's `summary` says the source is adopted as it stands and did not change. The fold
writes `adopted`, and «An adopted node binds the files whose judgment holds its fact and no
others» (SPEC-005 R4): each cleared candidate's `encoded_at` is the files whose judge read its
fact there. A candidate every judge answered `nowhere`, with nothing found against it, is listed
under `unheld` and claims no file.

## 3. Bind with `--bind-record --workspace`

It writes the trace if this is the target's first.

## 4. Report what an adoption adds

- every candidate under `unheld` — a node the source does not carry, or one the files outside this
  set carry: the analysis's to revisit, or the adoption of those files;
- every `contradicts` against a candidate — a reading of the source the node misstates, the same
  route;
- every `unstated` fact — the source carries it and no node does, the same route again;
- every `restates` — text the comment route removes before this route runs over the file again;
- the target's standing as `trace.py --untraced` prints it: «Adoption is complete when no file is
  unsurveyed and no node is unreached» (SPEC-005 R7), and this is the file half of that count.
