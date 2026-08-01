---
id: "0006"
title: Make a capability describe itself well enough to be chosen without being read
status: accepted
contract_version: spec/1
---

# Capability contracts

## Scope

What a capability declares about itself, in a form a consumer can act on without reading the
implementation: its identity, its inputs and outputs, what it decides deterministically, its grant, and
its failure outcomes.

Not here: which classes exist (`foundation/0005`).

## Requirements

### The declaration

- **R1** — Every capability carries a declaration holding the parts required of its class. A capability
  whose declaration is absent or incomplete is not installed.
- **R2** — A declaration is machine-readable where a consumer branches on it, and prose where a reader
  needs to understand it.
- **R3** — A capability's identifier is stable across versions of its behavior. A change in what a
  capability does is a contract version change, not a rename.
- **R4** — An objective states what the capability is for and when to choose it, with the deciding case
  first. It does not describe how the capability works.

### Inputs and outputs

- **R5** — Every input is named, and every input is either required or has a stated default. A capability
  that behaves differently when an input is absent states that behavior in its own declaration.
- **R6** — A missing or contradictory required input is a declared failure outcome, never an
  improvisation and never a substituted default.
- **R7** — Every output another capability consumes declares its contract version. An output carrying
  control flow or persisted state names the versioned schema it satisfies.
- **R8** — A capability declares the artifacts it reads without being given them, so that a reader can
  tell what it depends on without executing it.
- **R9** — A capability declares, as a named input with its contract version, every artifact that must
  exist before it can run. The declaration is therefore sufficient to derive the order two capabilities
  run in without executing either. A capability with an undeclared prerequisite is incomplete under R1
  and is not installed. A capability that genuinely has no prerequisite declares none.
- **R10** — Where more than one declared input can satisfy a capability, the declaration states that the
  alternatives are alternatives, and names each.
- **R11** — A capability that needs knowledge in scope declares what it needs, in terms of the ontology
  rather than of file paths.

### The determinism split

- **R12** — Every declaration separates what the capability decides deterministically from what it
  decides by judgment. A capability that declares neither is not describable.
- **R13** — A property declared deterministic is decided by a script or a hook. Declaring a property
  deterministic while a prompt decides it is a defect in the declaration.
- **R14** — A capability declares which of its outputs an assertion binds, and names each one. Where no
  assertion covers an output, the declaration says so.
- **R15** — A declaration never promises byte identity for an output a model produced. It may promise
  that the inputs, the contract, and the recorded outcome are reproducible.

### Grant and failure

- **R16** — A capability's grant lists only what its declared steps require. The absence of a statement
  is not a grant, and a grant wider than the steps is a defect even when unused.
- **R17** — Every failure outcome is a named, closed value a consumer can branch on, accompanied by a
  reason a caller can act on without re-running the capability.
- **R18** — A capability does not report success on partial completion. Where it completed part of its
  work, it reports the failure and what was written.

### What a declaration may not hold

- **R19** — A declaration does not restate a rule a specification, a schema, or a validator already
  holds. It cites it.
- **R20** — A declaration does not carry a business rule of any downstream system, and does not name a
  single repository's paths, services, or conventions.
- **R21** — A declaration does not encode a numeric threshold that has not been calibrated from executed
  runs and recorded with the evidence that calibrated it. A value the caller supplies per run is not a
  framework threshold; a value the framework ships is.
- **R22** — A report naming a numeric value states which of the two it is: supplied by the caller for
  this run, or shipped by the framework and calibrated.

### Where a declaration lives

- **R23** — A declaration is a separate authored artifact that references the frontmatter contract of its
  class. It does not extend one.
- **R24** — A declaration and the component it declares are checked by one validator, which rejects an
  incomplete declaration and a disagreement on any field both carry.
- **R25** — A declaration is authored under the framework source and is not itself installed. What a
  consumer reads instead is a catalog derived from the declaration set.
