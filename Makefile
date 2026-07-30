# Siegard Code — canonical entry points declared in CLAUDE.md.
#
# A target that has nothing to check yet must fail loudly rather than succeed
# vacuously. A green run that validated nothing is worse than a named gap.
#
# `check` composes only non-mutating targets. `dist` regenerates, so it cannot
# verify: a check that repairs what it was meant to detect reports success on a
# defect. Verification of the distribution is `dist-check`.

.PHONY: validate knowledge test dist dist-check check

# Every validator runs even when an earlier one fails: a report that names one
# gap and hides the rest is the failure mode this repository is built against.
# Ordered by the precedence in CLAUDE.md: specifications, then ADRs, then the
# schema-derived layers.
validate:
	@fail=0; \
	python3 scripts/validate_specs.py || fail=1; \
	python3 scripts/validate_adrs.py || fail=1; \
	python3 scripts/validate_concepts.py || fail=1; \
	python3 scripts/validate_components.py || fail=1; \
	python3 scripts/validate_knowledge.py || fail=1; \
	python3 scripts/project_knowledge.py --check || fail=1; \
	python3 scripts/measure_ontology.py --check || fail=1; \
	exit $$fail

# The knowledge validator is wired above, as specs/0003 R37 requires. Both derived
# trees are verified rather than regenerated here: `--check` compares and mutates
# nothing, so `validate` stays safe to run on a dirty tree. Regeneration is
# `make knowledge`.
#
# Nothing in `validate` gates on a figure. `measure_ontology.py --check` verifies
# that the recorded R52 measurement matches the fixture, not that any value in it
# clears a threshold: spec 0002 R8 and spec 0001 R25 both forbid the latter.
knowledge:
	python3 scripts/project_knowledge.py
	python3 scripts/measure_ontology.py

test:
	python3 -m unittest discover -s tests -t .

dist:
	@echo "dist: no generator exists yet — see docs/bootstrap.md, open question 2" >&2
	@exit 1

dist-check:
	@echo "dist-check: no generator exists yet, so there is no committed distribution to compare against — see docs/bootstrap.md, open question 2" >&2
	@exit 1

check: validate test dist-check
