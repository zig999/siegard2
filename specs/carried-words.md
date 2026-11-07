---
id: "SPEC-010"
title: The person's words, carried
status: proposed
contract_version: spec/1
---

# The person's words, carried

## Scope

This specification fixes how the person's own words cross two boundaries a session cannot carry
them over by itself: a compaction, after which the session holds a summary of what was said
rather than what was said; and a sibling project, whose session is another context the words must
be handed to. It binds `bin/ask.py`, `bin/relay.py`, and the session rules that read what they
write. And it fixes the one choice the person makes before saying anything: the project a skill
runs over, named in the invocation or chosen by opening the session in it. That binds
`bin/project.py --here` and every shipped skill that takes the project root as an input.

Grounds for R6, read from consumer transcripts on 2026-11-07: of the invocations of the skills
that take a project root, `/siegard-status` ran 24 times and `/siegard-progress` 6 times with no
argument at all, and `/deliver-scope`, `/siegard-telemetry`, `/siegard-standard` and
`/siegard-config` were invoked in prose naming no root; every `/siegard-status` read ran
`project.py` over the working directory without asking. The skills' own text said "named by the
human; inferred rather than named, its absence is a stop", which reads both ways, while
`/siegard-goal` already stated the working directory's git toplevel as the root none names.

Grounds, as the maintainer relayed them on 2026-10-31 and not yet read from transcripts here:
commit authorizations were asked for again and again — after a compaction, because the session
rules make a resumed route re-authorize and "a summary of an earlier context is not an
authorization", and once right after the person had written "comits estão autorizados"; the
operator wrote standing authorizations by hand into long pasted prompts. Separately, the operator
relayed prompts between sibling projects' sessions by copy and paste 11 times, once into the wrong
project, and a ready command saved under `/tmp` was gone when it was needed.

### Decided elsewhere, deliberately not restated here

- What authorizes a commit, and which commit a word covers — the session rules
  (`src/claude/hooks/rules.md`) and this repository's `CLAUDE.md`.
- An objective a goal carries by path and digest — `specs/goal.md` (SPEC-008 R6), whose file
  form this one follows.
- What a run that stopped may still commit — `specs/goal.md` (SPEC-008 R18).

## Definitions

- **Ask** — the person's own words, given in a session, that authorize what the session does next.
- **Recorded ask** — an ask written by `ask.py --record` to `ask-<stamp>.md` under the telemetry
  root.
- **Sibling project** — another project that declares its own `siegard.json`, worked in a session
  of its own.
- **Relay file** — text for a sibling project's session, written by `relay.py` to
  `relay-<stamp>-<sibling>.md` under the origin project's telemetry root.
- **Stamp** — the UTC instant a file was written, `YYYYMMDDTHHMMSSZ`.

## Requirements

### An ask across a compaction

- **R1** — An ask is recorded by `bin/ask.py --record` to `ask-<stamp>.md` under the telemetry root, its bytes the person's own words copied whole and never edited, and is named by its path and its sha256 digest, which the script prints. A recorded ask is never overwritten: a path already taken is refused, and an empty text is refused.
- **R2** — `bin/ask.py --read` prints the newest recorded ask, or the one named by path, verbatim beneath its path and digest, and refuses a digest named beside it that the file no longer holds. A path outside the telemetry root, or not named `ask-<stamp>.md`, is no recorded ask and is refused.
- **R3** — A route resumed after a compaction reads its authorization from a recorded ask, printed by `ask.py --read`, in place of a summary of an earlier context: a recorded ask is the person's words, and a summary is the session's. What an ask authorizes is read from its words under the session rules, and recording it widens nothing.

### A relay to a sibling project

- **R4** — Text for a sibling project's session is written by `bin/relay.py` to `relay-<stamp>-<sibling>.md` under the origin project's telemetry root, and never into the sibling's repository. Its first line is the invocation the receiving session runs to confirm it; then, each on a line of its own, the sibling's root, the plugin version the receiving session must run — read from the plugin manifest `project.py` reads — the origin's root and the text's digest; then a blank line and the text verbatim. A sibling that declares no `siegard.json`, or that resolves to the origin project itself, is refused and nothing is written.
- **R5** — `bin/relay.py --confirm` prints the relay's text only where the session running it is in the sibling's project, as `project.py` resolves the working directory, runs the plugin version the relay names, and holds the text the relay's digest names. Any one of these failing is a refusal, and the text is withheld.

### The project an invocation runs over

- **R6** — A skill runs over the project root its invocation names. Where the invocation names none, the project root is the git toplevel of the session's working directory, as `bin/project.py --here` resolves it, and only where that toplevel holds `siegard.json`. An unnamed root that holds none is a stop, and `siegard.json` is never created under a root the invocation did not name.

## Validation required before acceptance

1. Tests hold `ask.py` to R1 and R2 over a fixture project: an ask recorded byte for byte and its
   digest printed; an empty text refused; the newest ask read verbatim; a named ask read; a digest
   that no longer matches refused with nothing of the text printed; a path outside the telemetry
   root refused; a project declaring no telemetry root refused.
2. Tests hold `relay.py` to R4 and R5 over two fixture projects: the relay file written under the
   origin's telemetry root with its header and the text verbatim, and nothing written in the
   sibling; a sibling without `siegard.json` refused; `--to` equal to `--from` refused;
   `--confirm` printing the text from the sibling's working directory and refusing it from the
   origin's, under another version, and over a text changed since it was written.
3. A consumer session resumed after a compaction under this specification is read for the
   commit authorizations the person was asked for again; each one asked while a recorded ask
   covered the commit is a defect in what reads the ask, never grounds to widen what it covers.
4. Tests hold `project.py --here` to R6 over fixture trees: run from a subdirectory of a project
   that declares `siegard.json`, it prints the toplevel as `project_root:` and then every field;
   from a tree whose toplevel holds no `siegard.json`, it refuses and prints no field; combined
   with a named root, it refuses. A test holds every shipped skill that lists the project root as
   a required input to quote R6 in that input.

## Readings

- 2026-10-31 — not yet read: no session has recorded an ask or relayed a text under this
  specification.
