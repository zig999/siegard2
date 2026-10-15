# Contributing

This repository authors the Siegard framework. It is not the framework: the framework is what an
assembly of `src/claude/` produces, and it builds no business application. Issues and pull
requests are welcome. Open an issue first for a change that alters a specification, a schema or a
contract version; a typo, a comment or a test for behavior already specified can go straight to a
pull request.

## Where a change goes

- **Edit `src/claude/`, never `dist/.claude/`.** `dist/.claude/` is a byte-for-byte copy and
  `tests/test_distribution.py` refuses a file that differs from its source. Assemble it with the
  two copies in the README's "For maintainers" section, then commit source and copy together:

  ```sh
  rsync -a --delete --exclude '__pycache__' src/claude/ dist/.claude/
  cp src/consumer/* dist/
  ```

- **Authority runs in one order:** a specification in `specs/`, then a schema in `schemas/`, then
  code and tests, then documentation. Where two disagree the earlier wins, and the change that
  resolves it updates both. Where nothing states a requirement, the specification gains the
  statement.
- **One name per concept** across specs, schemas, code and tests, and one authoritative
  definition per concept.
- **What ships is timeless.** Nothing under `src/` states what the framework was, what it replaced
  or what incident produced a rule. The evidence for a change belongs in the commit message.
- **A distributed artifact that cites a specification requirement** carries, in `«…»` beside the
  citation, a sentence of that requirement verbatim; `tests/test_spec_citations.py` keeps the two
  from drifting.

## `CLAUDE.md` is the maintainer's

`CLAUDE.md` holds the rules this repository is worked under, and only the maintainer changes it. A
contributor, human or agent, who thinks it should carry a rule proposes it: the exact text, where
it goes and what it displaces, in an issue. Everything else here is ordinary work.

## Language

Every committed artifact is English (en-US): source, specifications, schemas, tests, fixtures and
commit messages. Explanatory material — a README, a glossary, a guide — may be written in another
language beside its English original as `<name>.<locale>.md`; it states no requirement, and the
English document governs. Identifiers the framework defines are never translated.

## Tests

```sh
python3 -m pytest
```

The suite takes about five minutes and must be green before a change lands. A test anchored on
words a change rewrote is re-anchored on the new words, never loosened. Install the dependencies
first: PyYAML and jsonschema, plus pytest.

## A change that ships

A change that alters what ships — anything under `src/` — is a release:

1. Bump the version in `src/claude/.claude-plugin/plugin.json` and in the marker line of
   `src/claude/hooks/rules.md`; the suite refuses a mismatch.
2. Assemble `dist/` as above and run the suite.
3. Commit with a subject of the form `Ship <version>: <what changed>`, and say in the body what
   changed and why, citing any measurement the change rests on.

A major is a version whose contract a persisted record no longer satisfies; it ships with the
rewrite a consumer runs once, under `tools/`.

## Licensing

Contributions are made under the repository's MIT license.
