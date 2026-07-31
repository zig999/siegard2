# One generation, end to end

Fifty-nine artifacts produced from `fixtures/knowledge-two-context/` through
`fixtures/pack-typescript/`, with the manifest that records them and the tree they went into.

`out/` is committed because `specs/0004` R34 verifies by regenerating into a temporary tree and
diffing against the committed one. There is nothing to diff against otherwise, and R7 makes the
files there not hand-edited — a `PreToolUse` hook does not yet cover them, so that rule holds by the
verification catching it rather than by prevention.

## What it holds

| Path | What it is |
|---|---|
| `run.json` | the roots and every identifier, stated rather than minted |
| `generation-manifest.json` | **derived.** What was produced, with a hash and a pack version each |
| `out/` | **derived.** 59 files of TypeScript, SQL, and markdown |

## What it is evidence for

- **A plan executes and the manifest records it** (R30). Every artifact traces to a knowledge object
  in the scope, carries the pack version that produced it, and matches the hash the manifest holds.
- **Regenerate-and-diff mutates nothing** (R34), and a difference is attributed rather than merely
  reported (R35). A hand edit, a deletion, and a change in knowledge each produce a different
  finding, because the three call for opposite actions and a diff saying "differs" leaves the reader
  to guess.
- **A blocked plan writes nothing** (R25). A placement collision raises before the first file, and a
  test asserts the target directory does not exist afterwards.
- **The two indexes are derived** (R42, R44). Produced source binds through the manifest;
  hand-authored source binds through a `siegard:binds` declaration it carries. Neither is committed,
  because a committed one would be the hand-maintained mapping R44 forbids.
- **The deterministic share is measured** (R6): 59 of 61 plan entries. The two judged ones are
  `validator` and `orchestration`.

## What it is not evidence for

- **The judged track never ran.** No agent produced a `validator` or an `orchestration`, so R3 — a
  judged artifact verified against a generated conformance suite — is stated and untested. The
  conformance tests for those rules exist in `out/`; the thing they would check does not.
- **The produced code was never compiled or run.** It is TypeScript and SQL by shape. Nothing here
  claims it type-checks, and `specs/0004` R3's behavioural conformance is a different claim from the
  byte identity this fixture holds.
- **`specs/0004` R7's extension point is unexercised.** The rule is stated in every produced file's
  header and the binding index reads a `siegard:binds` marker, but no fixture extends a produced
  artifact through a declared extension point.
- **One knowledge base, one pack.** `specs/0012` R13 wants a pack shown to serve any repository on
  its stack, and this shows one.
