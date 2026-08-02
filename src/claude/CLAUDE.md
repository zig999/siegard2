# Siegard

This repository's domain knowledge is recorded as knowledge objects, governed by the Siegard plugin.
That set is the authority: source, tests, and documentation derive from it. When code and a knowledge
object disagree, the object is what the business decided.

## Entry points

Neither is model-invocable — invoke it by name rather than doing the work ad hoc.

- **`/model-domain`** — turns a request into domain objects, written where they are read, and stops
  there so `git diff` is the review.
- **`/ingest-domain`** — writes into those objects the four fields no analysis carries.

In that order. Running the second over objects nobody reviewed turns every unanswered question into a
blocked entry discovered a step too late.

## Rules that bind every session

- **Do not author or edit a knowledge object by hand.** Use the two entry points. An object written
  outside them skips the boundary validation and the completeness check that make the base
  trustworthy, and nothing downstream can tell it apart from one that passed both.
- **Do not state a domain fact the base does not hold** — in code, a comment, a test, or a prompt. Where
  the base is silent, report the gap. A plausible attribute, an invented state, a default currency: each
  becomes indistinguishable from a fact the business stated.
- **Do not record a status on a knowledge object.** There is no maturity ladder and no approval state:
  what the base holds is current and binds. A fact that is not settled is not recorded — it is reported
  as a gap. Where a fact takes effect on a date or moves through states, that is a typed attribute or a
  `lifecycle` about the domain, not a label on the object. **Which pass has run is not a status
  either**: an object with an open `kind: authoring` gap is one the enrichment has not reached, and a
  field saying so would be a second home for a fact the object already carries.
- **Do not hand-edit a derived file.** `index.md`, `glossary.md`, `context-map.md` and `graph.json`
  restate what the objects already say, and `${CLAUDE_PLUGIN_ROOT}/bin/materialize.py` derives all four.
  Change the objects and run it again.

## Where the rest lives

The eight kinds, the fields each requires, the identifier arithmetic, the authoring order, and
validation at the boundary are carried by `${CLAUDE_PLUGIN_ROOT}/schemas/domain-object.json` and by the
capabilities themselves. Read the contract before touching an object; do not reconstruct its rules from
memory.
