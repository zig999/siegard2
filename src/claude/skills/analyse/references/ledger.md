# The ledger, line by line

Read during step 4b of `/analyse`, whenever the material was given as a file.

## Which lines are owed

Which lines are owed is not yours to choose. On material whose frontmatter declares
`siegard-survey/1` — read from source no delivery wrote — or `siegard-intent/1` — read from the
target's declared tests, each fact beside the source file it governs — they are its fact lines,
the top-level bullets under `## Facts`, `## Answers`, `## Vocabularies` and
`## Upstream artifacts`: «Every fact line of the material lands in a node or is left out with a
stated reason» (SPEC-005 R8). On any other material `trace.py` enumerates them: every line opening
with bold text, every list item at the line's start, every table body row and the first line of
every other paragraph, outside frontmatter, code fences and headings. A context paragraph is
owed an entry too; its answer is `outside`, saying it states no fact.

## The three answers

Read `${CLAUDE_PLUGIN_ROOT}/schemas/ledger.json` and write `ledger.md` beside the material — never
under the specification root — with one entry per line: `at` as `<material file>:<line>`, and
one of three answers.

- `node`, naming the node whose fields now hold the line's fact. A line that lands in several
  nodes takes one entry per node.
- `outside`, saying why no node holds it — implementation knowledge, a fact another context or
  system owns, a behavior the material observed and did not decide, a line that states no fact.
- `open`, saying what of the line remains to answer. A question the material asks and this
  increment does not decide is open, never outside: a later increment of this analysis answers
  it. «A line answered in part lands in the nodes that answer it and is left open for the rest»
  (SPEC-001 R16) — where a line asks several things and the nodes answer some, the entry naming
  the nodes stands beside one `open` entry naming what none of them answers. A node that answers
  part of a line is the one place a ledger can look complete and is not; read each line you land
  against everything it asks before writing `node` alone.

## Digests

A file that declares no Siegard material contract carries its digest under `digests`, keyed as
`material` spells it: «The ledger records the sha256 digest of every such file» (SPEC-001 R16).
`trace.py --ledger` prints the digest it reads where it is missing; the material is edited
between increments only with the ledger answered again, because a changed digest is refused.

## Reading what `--ledger` prints

A refusal names each line with no entry. Each is a line you read and did not answer, and the
answer is one of three: give it the field, rule, scenario or answer it is owed — then rerun step
4 — state why no node holds it, or leave it open saying what remains. Never an entry naming a node
that does not hold the fact: the ledger is what an adoption reads to hand each file's judge — the agent
`/reconcile` sends to read that file — its candidates, and a wrong entry sends a judge to the
wrong node.

Sound, the command prints the lines still open and the reasons lines were left out, grouped and
counted, largest first. Read the largest group before reporting: one reason carrying most of the
material is a reason doing the work an answer should, and each line under it is reread against
it. On survey or intent material it also prints the file set the material read and the
candidates per file; all of it goes into the report and the handoff below. An adoption reads a
ledger only where no line of it is open, so over survey or intent material an open line is one
more increment of this analysis before `/reconcile` can take it.

