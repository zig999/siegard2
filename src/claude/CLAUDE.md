# Siegard

This repository's domain knowledge is recorded as knowledge objects, governed by the Siegard plugin.
That set is the authority: source, tests, and documentation derive from it. When code and a knowledge
object disagree, the object is what the business decided.

## Entry points

Neither is model-invocable — invoke it by name rather than doing the work ad hoc.

- **`/model-domain`** — turns a request into a reviewable domain model, and stops there.
- **`/ingest-domain`** — turns a reviewed model into knowledge objects.

In that order. Running the second over a model nobody reviewed turns every unanswered question into a
blocked entry discovered a step too late.

## Rules that bind every session

- **Do not author or edit a knowledge object by hand.** Use `/ingest-domain`. Objects written outside it
  skip the classification and the boundary validation that make the base trustworthy.
- **Do not state a domain fact the base does not hold** — in code, a comment, a test, or a prompt. Where
  the base is silent, report the gap. A plausible attribute, an invented state, a default currency: each
  becomes indistinguishable from a fact the business stated.
- **Do not record a status on a knowledge object.** There is no maturity ladder and no approval state:
  what the base holds is current and binds. A fact that is not settled is not recorded — it is reported
  as a gap. Where a fact takes effect on a date or moves through states, that is a typed attribute or a
  `lifecycle` about the domain, not a label on the object.
- **Do not hand-edit a derived file.** An index, a glossary, a context map, or a graph restates what the
  objects already say. Change the objects.

## Where the rest lives

The six node types, the fields each requires, the identifier arithmetic, the authoring order, and
validation at the boundary are carried by `${CLAUDE_PLUGIN_ROOT}/schemas/knowledge-object.json` and by
the capabilities themselves. Read the contract before touching an object; do not reconstruct its rules from memory.
