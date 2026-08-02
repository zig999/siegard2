"""Which pass owns which field of a staged knowledge object. One declaration, three consumers.

A staged object is written twice: once by the expansion, from the model, and once by the
enrichment, from judgment. Three separate things need to agree on where the line between them
falls, and each of the three is a place the line could be written down differently.

- the **expansion** writes only the fields on its side, and never the four the enrichment supplies;
- the **enrichment check** rejects a change the enrichment made on the expansion's side, which is
  the only thing enforcing that restriction — a tool grant cannot express "this file, these keys";
- **re-expansion** preserves the enrichment's side while rewriting its own, so a model that changed
  does not silently discard the sentences somebody wrote against it.

Written three times it would be one fact with three chances to drift, and the drift would be
invisible: each of the three would keep working while disagreeing with the others about one field.

The line itself is not arbitrary and was measured. Authoring an object was found to copy `title`,
`ddd`, `statement`, and `examples` from the model byte for byte, and to add exactly a retrieval
question, a summary, a declared out-of-scope, and a body. Everything a model can carry is on the
expansion's side; those four are on the enrichment's; and `gaps` is shared in one direction only —
the enrichment may close an `authoring` gap and may not touch a `domain` one.

Declared dependencies: none beyond the standard library.
"""

from __future__ import annotations

# What only judgment supplies. Closed, and identical for every node type: no analysis carries them,
# which is why the expansion records each as an `authoring` gap rather than guessing.
ENRICHMENT_FIELDS = ("question", "description", "out_of_scope")

# The body belongs to the enrichment too. The expansion places the two headings its node type
# requires and leaves them empty, so a third heading is not something the enrichment can add by
# accident — it would have to write one.
ENRICHMENT_OWNS_BODY = True

# Shared, and in one direction. The enrichment closes an `authoring` gap by writing the field it
# names and removing the entry; a `domain` gap is the domain's to close and no pass of this pipeline
# may remove one.
SHARED_FIELD = "gaps"


def expansion_owns(field: str) -> bool:
    """True where the expansion writes the field and the enrichment may not change it."""
    return field not in ENRICHMENT_FIELDS and field != SHARED_FIELD


def closable(gap: dict) -> bool:
    """True where the enrichment may close this gap.

    `kind: domain` is the domain's, and no capability of this framework closes one — an enrichment
    that removed one would be asserting the domain answered.
    """
    return gap.get("kind") == "authoring"
