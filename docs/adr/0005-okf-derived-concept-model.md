---
id: 0005
title: Base the knowledge layer on OKF concepts, as a constrained superset
status: accepted
---

# Base the knowledge layer on OKF concepts, as a constrained superset

## Context

Siegard's vocabulary lived in a single file, docs/glossary.md, removed by this change, with one `##`
heading per term. That shape has three problems: a term is not individually addressable, so nothing can
cite one as evidence with a stable path; the file carries no provenance, so there is no record of who
wrote a definition or what it derives from; and it is not machine-consumable, which contradicts the
framework's own requirement that knowledge passed to agents be readable without human interpretation.

Google Cloud published the Open Knowledge Format (OKF) in June 2026 — a specification for exactly this
problem: organizational knowledge as a directory of markdown files with YAML frontmatter, one concept
per file, aimed at giving AI agents curated context. It reached v0.2 within roughly a month, superseding
v0.1.

Adopting OKF wholesale was not available. `.claude/rules/claude-code-authoring.md` forbids adding
vendor-neutral abstractions without an accepted requirement, and `CLAUDE.md` puts support for other
agent harnesses out of scope. Vendor neutrality is OKF's headline property. OKF also provides far weaker
guarantees than Siegard requires: exactly one required field (`type`), an explicitly unregistered type
vocabulary, and no shipped schema or validator.

## Decision

Adopt OKF's **concepts**, not its portability goal. The knowledge layer becomes a concept bundle at
`docs/concepts/`: one concept per file, markdown body, YAML frontmatter governed by
`schemas/concept.v1.json`, validated by `scripts/validate_concepts.py` via `make validate`.

Taken from OKF, semantics preserved:

- one concept per file, plain markdown, readable with `cat`;
- `type`, `title`, `description`, `tags`, `resource` field names and meanings;
- the provenance model — `generated: { by, at }`, `sources`, `verified` — which Siegard previously
  described abstractly and now carries as structured fields;
- `stale_after` for content that should be re-verified after a date;
- reserved `index.md` for progressive disclosure, with `okf_version` declared at the bundle root;
- unknown-field preservation, so a producer may add fields a consumer does not know.

Changed, because Siegard requires more than OKF does:

- `type` is a **closed enum**. OKF states type values are not registered centrally; Siegard's own
  contract rules require a consumer to branch on a known value, so the vocabulary is closed and grows
  only when a second type actually exists. It currently holds one value, `term`.
- `id` is **required and stable**, and the filename must match it. OKF has no identifier field.
- `contract_version` is **required**, so a consumer rejects an artifact it was not built to read rather
  than inferring version from shape.
- `generated` is **required**. OKF leaves it optional; provenance is not optional here.
- A **validator ships**, and the schema is the single authority it reads. OKF deliberately provides
  neither.

The result is a strict superset on every field except one: an OKF consumer can read a Siegard bundle,
and a Siegard bundle imposes requirements OKF does not.

## Known divergence

`status` is the one field where Siegard is not OKF-compatible. OKF defines `draft | stable |
deprecated`. Siegard uses `proposed | accepted | superseded`, the vocabulary already established in
`docs/adr/README.md` and defined in `docs/concepts/accepted.md`.

Importing OKF's values would put two lifecycle vocabularies in one repository, which the
single-authority rule in `CLAUDE.md` forbids. Keeping Siegard's values means an OKF consumer reading
`status: accepted` sees a value outside the spec's vocabulary. That is a real, narrow incompatibility,
recorded here rather than glossed: one optional field, with a documented mapping if interoperability is
ever needed — `proposed` → `draft`, `accepted` → `stable`, `superseded` → `deprecated`.

## Consequences

- Each term is individually addressable, so a rule or an ADR can cite one by path.
- Provenance is now mechanical rather than implied: every concept records its author, time, and sources.
- `schemas/` and `scripts/` exist for the first time, and `make validate` performs a real deterministic
  check instead of naming a gap. This is the first place the framework enforces a contract rather than
  describing one.
- OKF is explicitly unfinished and has already broken compatibility once. Siegard tracks a pinned
  version (`okf_version: "0.2"`) and treats a spec update as a change to evaluate under
  `.claude/rules/compatibility.md`, not as something to follow automatically.
- Cost accepted: authoring a concept now requires frontmatter that a plain glossary entry did not. The
  validator makes the cost visible immediately rather than at review time.

## Why this is accepted rather than proposed

Unlike ADR-0001 through ADR-0003, this decision presupposes no unbuilt component, and it is exercised
in the same change that records it: ten concepts converted, a schema enforcing them, and a validator
proven to reject a bad `type`, a missing `generated`, a wrong `contract_version`, a `superseded` concept
without `superseded_by`, a duplicate `id`, and a filename that disagrees with its `id`.
