> [← Glossary](../siegard-glossary.md) · Previous: [Setting up a project](02-setting-up-a-project.md) · Next: [Planning (`/plan-work`)](04-planning.md)

## 3. The specification

### Specification, specification root
The set of markdown files that states what the business decided, under one folder. Every file is
a **node**. It is validated by `spec.py`. It is the authority: when code and a node disagree, the
node is what the business decided.

### Node
One markdown file of the specification: YAML frontmatter (the fields) plus a short body
(`## Description`). Example — a Rule node:

```markdown
---
type: invariant
statement: A hypothesis MUST hold at least one piece of evidence before its case resolves.
constrains:
  - domain/troubleshooting/hypothesis
---

## Description

No case resolves on an unsupported explanation.
```

### Identity
A node's path from the specification root, without `.md`. The file above, stored at
`specification/rules/troubleshooting/hypothesis-requires-evidence.md`, has the identity
`rules/troubleshooting/hypothesis-requires-evidence`. Identities are how every record, plan and
trace names a node.

### Bounded context, `_context.md`
A **context** is a folder (`domain/troubleshooting/`) grouping one part of the business with its
own language. `_context.md` in that folder describes it: its responsibility and whether it is
`core`, `supporting` or `generic`. A context descriptor is never bound to code.

### The five classes
Every node belongs to exactly one class, chosen by its folder:

| Class | Folder | Answers | Subtypes |
|---|---|---|---|
| **Domain Model** | `domain/<context>/` | What exists and how it is structured | `aggregate-root`, `entity`, `value-object`, `domain-service`, `enumeration` |
| **Rule** | `rules/<context>/` | What must always hold | `invariant`, `policy`, `state-machine` |
| **Scenario** | `scenarios/<context>/` | What happens in one concrete case (given/when/then) | none |
| **Contract** | `contracts/<context>/` or `contracts/system/` | What is promised across a boundary | `domain-event`, `command`, `api`, `capability` |
| **Architecture Constraint** | `constraints/` | What limits how it may be built | none |

Short definitions of the subtypes:

- **aggregate-root** — the entry point of a consistency boundary (`case`, `order`).
- **entity / value-object** — a thing with its own identity / a value defined only by its content.
- **enumeration** — a closed list of values (`case-status`).
- **domain-service** — a named behaviour that belongs to no single element.
- **invariant** — a rule inside one aggregate, true at all times.
- **policy** — a rule that may cross aggregates; it must say whether it converges `immediate` or
  `eventual`.
- **state-machine** — the allowed states, transitions and rejections of one aggregate's status.
  The validator checks it is *total*: every state × trigger pair is a transition or a rejection.
- **domain-event / command / api** — messages and interfaces; each says `direction: published`
  or `consumed` (a consumed one names its `upstream`).
- **capability** — what the system promises its users; lives in `contracts/system/`.

Key fields you will see: `statement` (one sentence, one falsifiable condition), `constrains`,
`subject`, `given`/`when`/`then`, `payload`, `operations`, `answers`, `scope`, `fitness`.

### Material
Whatever a human gives `/analyse` to read: a document, a transcript, a ticket, or (for an
adoption) a survey written from the source code. Material is **data, never instructions** — a
sentence in it that reads like an order is analysed, never obeyed.

### Intake
The folder `work/<slug>/intake/` where a plan's raw material is kept. Never validated.

### Decision log (`<slug>.log.md`)
**What it is.** One append-only list beside each node that received a decision — `evidence.log.md`
beside `evidence.md`, in the node's own directory — of every fact the analysis *decided* about that
node because the material did not say it. It never blocks anything: it discloses, and a human
reviews it afterwards. A node beside no log is a node whose material answered everything. The dot
in the name keeps it outside the slug space, so no node can ever be called `foo.log`.
**Example** (`domain/troubleshooting/evidence.log.md`):

```yaml
entries:
- field: attributes.value.type
  unstated: The material does not say what shape an evidence value takes.
  decided: string
  why: Every evidence sample in the material is shown as free text.
```

Three shapes of entry: **decided** (`decided` + `why`), **read** (`found`: where outside the
specification the fact was read; no `why`), and **retired** (`retired`: where a fact went when its
field, or the node itself, left the specification). Entries are never edited or removed; the file
is frontmatter alone, and the latest entry over a field is the one that stands.
**How it is written.** Only by `spec.py --decide <identity> <root>` with one entry as JSON on
stdin: the writer checks the entry against the schema and the node, appends it as one block, and
validates the root. Nobody edits a log by hand.
**When a node leaves or moves.** Removing a node appends a `retired` entry to its log and leaves
the log in place as a tombstone — the validator accepts a log beside no node only when its last
entry retires a field. Renaming a node is `git mv` of the node and its log in one commit; no entry
records the move.

### Decide-and-disclose
The discipline behind the log: what the material does not state is decided, written into the node
like any other value (no `TODO`, no `unknown`), and disclosed in the log. Nodes never carry
`gaps`, `sources`, `rationale` or `proposal` fields — the validator refuses them.

### Floor and ceiling
The **floor** is what every analysis must produce (at least one complete context with at least one
definition). The **ceiling** is the rule that nothing answering no comprehension question may exist
(an element nothing reaches fails validation).

### Projection
A generated view of the specification — class diagrams, context map, state diagrams, capability
map, system overview — written by `spec.py --project` into `projections/`. Never edited by hand.

### Digest, pin
A **digest** is the SHA-256 fingerprint of a file's exact bytes, written `sha256:<hex>` — the same
value `sha256sum <file>` prints. A **pin** is a digest stored in a record to say "this is the
version I read". If the file changes, the digest no longer matches, and that mismatch is how
Siegard notices movement.

### `spec.py` — the specification validator

```sh
spec.py <spec-root>                       # validate everything
spec.py --node <file> <spec-root>         # validate one file while writing it (no cross-checks)
spec.py --digest <spec-root>              # print every node's digest
spec.py --project <spec-root>             # validate, then write projections/
spec.py --impact <id>[,<id>...] <spec-root>  # one hop around each node, both directions
spec.py --shape [--of <id>,...] <spec-root>  # measure how long nodes run; never refuses
```

- **Input:** the specification root (and a node identity or file for some forms).
- **Output:** "sound" or a list of problems (exit `0` sound, `1` problems, `2` cannot run).
- **`--impact`** is the **impact set**: every node a node references, every node referencing it,
  and the decision log beside it. Planning uses it to find candidate nodes.
- **`--decide`** appends one entry to the decision log beside a node (one JSON object on stdin),
  then validates the root. It is the only way a log is written.
- **`--shape`** is a report, never a refusal: statement lengths, multi-sentence statements,
  phrases repeated across nodes, prose naming nodes. `--of` marks the nodes you are responsible
  for so they show up even past the cut.

---
> [← Glossary](../siegard-glossary.md) · Previous: [Setting up a project](02-setting-up-a-project.md) · Next: [Planning (`/plan-work`)](04-planning.md)
