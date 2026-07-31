# A capability retired

`foundation/0006` R14 fixes the lifecycle vocabulary, R15 forbids skipping `deprecated`, and R16 makes
retiring a consumed capability owe the migration `.claude/rules/compatibility.md` demands and a test
that fails against the old behavior.

## Why a fixture and not a real retirement

Nothing in the framework has needed to go yet. Retiring something to demonstrate retirement would
manufacture the evidence rather than produce it — the same objection this repository makes to a
threshold asserted before there is anything to calibrate against.

What a fixture can make real is the mechanism, and it does:

- `scripts/check_capabilities.py` checks the sequence. A capability moving from `active` straight to
  `retired` is reported, and R15's "breaking change made silently" is silent precisely because
  nothing compares two releases until something does.
- A deprecation naming no replacement is reported, and so is a retirement recording no migration.
- The migration is a function and the test asserts the **old** behavior no longer satisfies the new
  consumer. That is R16's own clause, and it is the one a recorded history cannot satisfy: a
  migration returning its input unchanged would pass a test that only checked the new shape works.

## What it is not evidence for

- **No capability actually went through this.** The four capability classes the distribution ships
  are all `active`, and `check_capabilities.py` derives that from facts rather than from labels.
- **No release record exists.** `foundation/0013` governs how a consumer learns what changed between two
  versions, and this fixture records three versions of one capability rather than a release.
- **`docs/` carries no changelog.** `.claude/rules/compatibility.md` requires release documentation
  updated on a breaking change, and that requirement is stated and unmet.
