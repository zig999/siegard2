# Siegard Code — canonical entry points declared in CLAUDE.md.
#
# A target that has nothing to check yet must fail loudly rather than succeed
# vacuously. A green run that validated nothing is worse than a named gap.

.PHONY: validate test dist check

validate:
	python3 scripts/validate_concepts.py

test:
	@echo "test: no framework test suite exists yet — see docs/bootstrap.md" >&2
	@exit 1

dist:
	@echo "dist: no generator exists yet — see docs/adr/0002-generated-distribution.md" >&2
	@exit 1

check: validate test dist
