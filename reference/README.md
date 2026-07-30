# Reference material

Historical design input, under version control for traceability. **Nothing in this directory is
normative.**

The nine SIGARD v0.1 documents here are the origin of this framework. Each one carries
`Status: Normative Draft` in its own text. That label describes what the draft aspired to be; it is not
a status this repository recognizes. `CLAUDE.md` admits three normative sources — accepted
specifications in `specs/`, accepted ADRs in `docs/adr/`, and the schemas and concepts derived from them
— and this directory is none of them.

What replaced them:

- `specs/0001-knowledge-object-driven-development.md` is the design authority, and its **Provenance**
  section records the three defects in this draft that forced a rewrite rather than an edit.
- `docs/concepts/` holds the vocabulary that survived, one concept per file, each naming the document
  here it derives from. A concept absent from that bundle did not survive.

Cite a document here as provenance for a decision, never as authority for a rule. No rule scopes to this
directory, nothing derives from it, and no validator reads it.
