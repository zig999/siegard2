# Certification

Read at step 2 where the person offered certifications, and again at step 3 for each entry the
manifest holds under `certify`. The auditor's judgment lives at
`${CLAUDE_PLUGIN_ROOT}/agents/coverage-auditor.md`.

## The input

For a node the file set encodes, the person names the test file(s) offered as its proof, spelled
from the target source root, and the registry step that runs them, by the name `commands[].step`
gives it. Named by the person, never chosen here: which test proves a fact is a claim about the
project's own suite, and the judgment decides only whether the claim holds — that the tests would
fail if the fact stopped holding. Where it holds, the bind writes the node as one a test decides,
so a later drift on its files is answered by the step's run rather than by a fresh reading.

## Staging it

**Write the certifications into a small YAML file in the workspace and pass it as `--certify`** —
a list, each entry the node, its `proof` paths and its `step`, exactly as the person stated them.

- The staging refuses, before writing anything, a node none of the named files encodes, a proof
  that is not there, and a step the registry does not declare. A refusal is the person's to
  answer, never a default.
- It never omits a pair of a node being certified: the certification rides a fresh reading of the
  node against its file.
- It writes one **certification pack** per node beside the file packs: the node's text with its
  source named, the proof resolved to absolute paths, the step, and the return contract's path.
  The pack is the whole of what the auditor is handed.

## The auditor

**A certification is the coverage auditor's, and it is one more subagent per node.**

- For each entry under `certify`, spawn a `siegard:coverage-auditor` subagent, handing it the
  certification pack's path and the target source root, and nothing else.
- Its rule is the whole test of a test: the named tests would fail if the node's fact stopped
  holding — the same rule it applies to a task's criterion in a review.
- Save its return verbatim at `siegard-reconcile/<slug>.returns/certify__<node with every '/' as
  '__'>.yaml`, under the same discipline as every other return (`references/judge.md`).
- The conformance judge for the node's file runs as well, unchanged: the fold writes a
  certification on no reading but one that cleared the node.
- Where the auditor answers short of `covered`, its return also says whether the **remainder** —
  what the offered tests leave unexercised — is one a test could assert, with the assertion named,
  or one no finite test closes. The fold carries that onto the node's entry, and `trace.py --owed`
  lists the testable ones as the work a test closes.

The fold writes `decided_by: test` from the auditor's `covered` and from nothing else; a node's
type says nothing about it either way.
