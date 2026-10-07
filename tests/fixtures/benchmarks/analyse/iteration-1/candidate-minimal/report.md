# candidate-minimal — the agent's return, verbatim

Note on the plugin root: the arm symlink was broken (`../../../../src/claude`); the skill, rules and `bin/project.py` were read from the evident target `/home/siegfriedneto/projects/siegard2/src/claude` and nothing under the workspace was changed.

**Start:** 2026-10-07T11:13:25-03:00
**End:** 2026-10-07T11:14:25-03:00

**Commands that wrote to disk:** none.

---

**/analyse stopped: the material is an absent input.**

The material supplied is one line: `Crie uma tela de cadastro de clientes.` It names a screen and states no fact of the domain. «Material that states no fact any of the five classes admits is an absent input, never a specification to decide» (SPEC-001 R15). This is a stop over an input, taken before the specification root's tree was checked and before any write: no node, no log, no projection was produced, and nothing under `runs/candidate-minimal/spec` was touched.

Of the two required inputs, the project root is present and sound — `bin/project.py` answers `specification_root: runs/candidate-minimal/spec`. The material is the one input missing, so this is the single stop.

For the analysis to proceed, the material would have to state, for each class it would otherwise have had to decide alone:

- **Domain Model** — what a "customer" is in this business: the terms that denote it and the things it holds, with the meaning the business gives each; which of those things identify a customer as opposed to merely describing it; which have a closed set of possible values, and what that set is.
- **Rule** — the conditions that must hold for a customer to be registered, kept or refused: what is required, what may never occur, what must be unique, and what happens to a registration over its life if it has states.
- **Scenario** — at least one concrete case: a particular customer being registered, what is true before, what is done, and what is true after — or what is refused and under which condition.
- **Contract** — what crosses a boundary when a customer is registered: what the system records or announces once a registration has happened, what it answers to the person or system that requested it, and whether any upstream system supplies or receives part of it.
- **Architecture Constraint** — any limit the business places on how the solution may be built, if there is one; none is required.

Nothing about what a customer registration screen shows or how it is laid out is a fact of the domain — a control's label, a layout, a field's placement are the implementation's, and no class admits them. What changes what a person can learn or do is a fact, and that is what the material must state.

Supplying the material is a new invocation:

```
/analyse — the material: <a document, transcript or file stating the facts above> — the project root: runs/candidate-minimal
```
