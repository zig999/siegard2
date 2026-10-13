> [← Glossary](../siegard-glossary.md) · Previous: [Reviewing (`/review-change`)](06-reviewing.md) · Next: [Reconciliation (`/reconcile`)](08-reconciliation.md)

## 7. The trace

### Trace, `siegard-trace.json`
**What it is.** The one long-lived link between the specification and the code. Plans and
delivery records may be archived; the trace stays. For each node it holds the node's digest and the
file(s) holding its fact, each with its digest.
**Who writes it.** Only `trace.py`. Never hand-edit it.
**Example.**

```json
{
  "specification": "specification",
  "bindings": [
    {
      "node": "domain/troubleshooting/case",
      "digest": "sha256:9e85d914…",
      "files": [
        { "path": "backend/src/troubleshooting/case.ts",
          "digest": "sha256:dce326b5…",
          "judged": true }
      ]
    },
    {
      "node": "rules/sales/invoice-immutable",
      "digest": "sha256:…",
      "files": [ { "path": "backend/src/billing/raise.ts", "digest": "sha256:…" } ],
      "decided_by": "test",
      "step": "test",
      "proof": [ { "path": "backend/tests/billing/raise.spec.ts", "digest": "sha256:…" } ]
    }
  ]
}
```

(Paths inside the trace file are relative to the trace file's own folder, the git toplevel.)

### Binding
One entry of the trace: *this node's fact lives in these files*. A **node-file pair** is one node
plus one of its files; most of reconciliation reasons pair by pair.

`judged` on a file means a reconciliation's judgment cleared that pair at that digest. Absent means
it was stamped by a delivery (or by hand) and not re-read since.

### Bind
Writing or extending a binding. Normally done by a skill from a record:

```sh
trace.py --bind-record <target-root> <spec-root> <record>                 # from an implementation record
trace.py --bind-record <target-root> <spec-root> <record> --workspace <dir>  # from a reconciliation record
```

It binds exactly the nodes the record lists with `encoded_at`, and nothing else. By default it
**adds** to what a node already held (the "union"): a file an earlier bind put on the node stays.

`--bind <target-root> <spec-root> <node> <file> ...` is the raw form no record backs; it prints a
warning that the judgment behind the entry lives nowhere.

### Rebind
Binding a node again so the trace's digests match what is on disk now. It happens when a delivery
restamps its task's nodes, or when a reconciliation clears a pair. "Changed without a rebind" is
the core problem: someone edited a file and nobody updated the trace.

### `--replace`
Makes a bind **substitute the whole entry** instead of adding to it — for when a fact genuinely
moved *out* of a file. Every path it stops claiming is printed as a **receipt**. `/reconcile` never
passes it; it hands you the command to run yourself.

### Receipt
The lines a command prints about what it did *not* do or what it dropped (nodes not bound, paths
released, certifications released, drift held back). Carry receipts into the report; they are the
only place a partial action says it was partial.

### Drift, `--check`
**Drift** is any mismatch between the trace and what is on disk now. `--check` recomputes every
digest and reports drift in four **classes**:

| Class | Meaning | Answered by |
|---|---|---|
| `orphaned` | Bound to a node the specification no longer holds | `trace.py --prune` |
| `moved` | The node's text changed since the bind | `/reconcile` over the bound files, or a delivery implementing the node |
| `code` | A bound file changed (or is gone) | `/reconcile` over the file; `--release` if it is gone |
| `proof` | The test that decides a certified binding changed | a new certification |

Real output (from a test fixture):

```
$ trace.py --check backend
domain/troubleshooting/gone-from-the-base: no longer in the specification; the binding is stale
domain/troubleshooting/evidence: bound at sha256:0000…, now sha256:52f0…; the specification moved since this bind
backend/src/troubleshooting/case.ts: the file changed without a rebind — 1 binding(s): domain/troubleshooting/case

3 drift finding(s) over 3 binding(s):
  1 orphaned: …
  1 moved: …
  0 proof: …
  1 code over 1 file(s): …
```

Exit `0` means no drift; `1` means drift (a CI can run it). `--all` also lists the drift held back
by `edits_freely`.

### `--prune`
Drops bindings in the `orphaned` class only — after an `/analyse` removed nodes. If git shows the
node's file was renamed, it follows the rename instead of dropping. Never use it to silence
`code` or `moved` drift.

### `--release`
Drops a file **the tree no longer holds** from every binding naming it. Refuses a file that still
exists (that one is reconciled, never released).

```sh
trace.py --release <target-root> src/legacy/old-handler.ts
```

### `--encodes`
Which nodes each file is bound to — the reverse question `--check` cannot answer for files that did
not drift.

```
$ trace.py --encodes backend src/troubleshooting/case.ts
backend/src/troubleshooting/case.ts: 2 binding(s)
  domain/troubleshooting/case — stale: the file changed without a rebind
  domain/troubleshooting/gone-from-the-base — matches
```

- `--encodes --changed <target-root> [<ref>]` — the same over what git says changed (against
  `HEAD`, or since `<ref>`).
- `--encodes --rank <target-root>` — the **accretion counts**: files by how many bindings they hold,
  nodes by how many files they are bound to. It is where an audit's file set usually comes from.

### `--untraced` and the four file states
Lists every tracked file under a target that no binding names. Each file is in exactly one state:

| State | Meaning |
|---|---|
| **bound** | A binding names it. |
| **holds-nothing** | An adoption judged it and bound none of its candidates to it. |
| **outside** | An adoption deliberately kept it out of the judgment (config, wiring). |
| **unsurveyed** | None of the above — nobody has looked at it yet. |

```
$ trace.py --untraced backend
3 tracked file(s) under backend: 2 bound, 1 no binding names
  0 holds-nothing: judged by an adoption, which bound none of its candidates to it
  0 outside: kept outside an adoption's judgment
  1 unsurveyed: no binding and no adoption names it
```

It refuses nothing: most files of a real system carry no business fact and are never bound.

### `--convergence` and the five node states
Every node of the specification in exactly one state, across the trace and every initiative:

| State | Meaning |
|---|---|
| `current` | Bound, and every digest still matches. |
| `stale` | Bound, and some binding drifted (see `--check`). |
| `planned-unbound` | A task implements it or an epic covers it, but nothing binds it. |
| `declared-uncovered` | An epic looked at it and wrote down why it is not being built. |
| `unreached` | No initiative names it and nothing binds it. |

```sh
trace.py --convergence <target-root> <spec-root> <work-root-parent>
```

A query: always exit `0`, no score.

---
> [← Glossary](../siegard-glossary.md) · Previous: [Reviewing (`/review-change`)](06-reviewing.md) · Next: [Reconciliation (`/reconcile`)](08-reconciliation.md)
