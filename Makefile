# Siegard Code — canonical entry points declared in CLAUDE.md.
#
# A target that has nothing to check yet must fail loudly rather than succeed
# vacuously. A green run that validated nothing is worse than a named gap.
#
# `check` composes only non-mutating targets. `dist` regenerates, so it cannot
# verify: a check that repairs what it was meant to detect reports success on a
# defect. Verification of the distribution is `dist-check`.

.PHONY: validate test dist dist-check check

# Every validator runs even when an earlier one fails: a report that names one
# gap and hides the rest is the failure mode this repository is built against.
validate:
	@fail=0; \
	python3 scripts/validate_concepts.py || fail=1; \
	python3 scripts/validate_adrs.py || fail=1; \
	exit $$fail

test:
	@echo "test: no framework test suite exists yet — see docs/bootstrap.md" >&2
	@exit 1

dist:
	@echo "dist: no generator exists yet — see docs/adr/0002-generated-distribution.md" >&2
	@exit 1

dist-check:
	@echo "dist-check: no generator exists yet, so there is no committed distribution to compare against — see docs/adr/0002-generated-distribution.md" >&2
	@exit 1

check: validate test dist-check
