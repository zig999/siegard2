fact: how a citation's name is compared against the names a capability's output declares
outcome: decided
edits:
  - path: rules/troubleshooting/citation-names-declared-output.md
    text: |
      ---
      type: invariant
      statement: A citation's name MUST equal, character for character and with case significant, one of the output_names declared by the diagnostic capability it references.
      constrains:
        - domain/troubleshooting/citation
      ---

      ## Description

      How a citation's name resolves to one output of the diagnostic capability it references: by exact, case-sensitive equality with a declared output name, with no trimming, case folding or other normalisation. Which outputs a capability declares is the diagnostic capability's; what evidence carries a citation is the evidence's.
log:
  node: rules/troubleshooting/citation-names-declared-output
  field: type
  unstated: No node and no material names a rule fixing how a citation's name is compared against the output names a diagnostic capability declares.
  decided: invariant
  why: Output names are identifiers the capability declares, so a citation resolves only to a name spelled exactly as declared, and any normalisation would let distinct declared names collide or let a citation name an output no capability declares.
noticed: No node states whether the output_names a single diagnostic capability declares must be unique within it.
