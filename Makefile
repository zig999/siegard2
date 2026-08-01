# siegard-generator — canonical entry points declared in CLAUDE.md.
#
# Every shipped script lives in src/claude/bin/ and takes its root as an argument: it
# ships, so it cannot default to a path that exists only here. The roots this repository
# validates are therefore named below rather than baked into the tool.
#
# A target that has nothing to check yet must fail loudly rather than succeed
# vacuously. A green run that validated nothing is worse than a named gap.
#
# `check` composes only non-mutating targets. `dist` regenerates, so it cannot
# verify: a check that repairs what it was meant to detect reports success on a
# defect. Verification of the distribution is `dist-check`.

.PHONY: validate foundation knowledge test dist dist-check check

# `foundation/` is the authority this work answers to rather than an artifact the build
# produces, so it has its own entry point and is deliberately absent from `check` —
# CLAUDE.md **Commands** states both. Run it when a specification changes.
foundation:
	@fail=0; \
	python3 scripts/validate_specs.py || fail=1; \
	python3 scripts/check_existence_claims.py || fail=1; \
	exit $$fail

# Every validator runs even when an earlier one fails: a report that names one
# gap and hides the rest is the failure mode this repository is built against.
# Ordered by the precedence in CLAUDE.md: ADRs, then the schema-derived layers.
#
# `scripts/validate_specs.py` is deliberately absent, by a maintainer's decision of
# 2026-07-31: `foundation/` is the authority this work answers to rather than an artifact
# the build produces or verifies. It runs under `make foundation` instead. The line is that
# decision and not a rule derived from what ships — `docs/adr/` and `docs/concepts/` do not
# reach a consumer either, and both are validated here, because each has a contract a
# validator can decide.
validate:
	@fail=0; \
	python3 scripts/validate_adrs.py || fail=1; \
	python3 scripts/check_contract_versions.py || fail=1; \
	python3 src/claude/bin/validate_concepts.py docs/concepts || fail=1; \
	python3 scripts/validate_components.py || fail=1; \
	python3 src/claude/bin/validate_artifacts.py fixtures || fail=1; \
	python3 src/claude/bin/validate_knowledge.py fixtures/*/knowledge || fail=1; \
	python3 src/claude/bin/project_knowledge.py --check fixtures/*/knowledge || fail=1; \
	python3 scripts/measure_ontology.py --check || fail=1; \
	python3 src/claude/bin/verify_judged.py --run fixtures/generation-run/run.json || fail=1; \
	python3 scripts/check_capabilities.py || fail=1; \
	exit $$fail

# `check_capabilities.py` runs last in the chain because it reads the committed
# distribution: foundation/0006 R17 derives each capability's status from whether the
# distribution installs it and whether a fixture exercises it, and both facts are
# only available once `make dist` has produced a manifest to compare against.
#
# `check_contract_versions.py` sits with the schema tier because it validates the contracts
# every validator below it loads. Its polarity is inverted relative to the derived-tree
# checks: it verifies by default and rewrites only under `--update`, which is deliberately
# absent from this target. A lock regenerated to silence a mismatch discards the only record
# that a contract moved.
#
# The knowledge validator is wired above, as foundation/0003 R37 requires. Both derived
# trees are verified rather than regenerated here: `--check` compares and mutates
# nothing, so `validate` stays safe to run on a dirty tree. Regeneration is
# `make knowledge`.
#
# Nothing in `validate` gates on a figure. `measure_ontology.py --check` verifies
# that the recorded R52 measurement matches the fixture, not that any value in it
# clears a threshold: spec 0002 R8 and spec 0001 R25 both forbid the latter.
#
knowledge:
	python3 src/claude/bin/project_knowledge.py fixtures/*/knowledge
	python3 scripts/measure_ontology.py

test:
	python3 -m unittest discover -s tests -t .

# `dist` regenerates dist/.claude/ by copying src/claude/, which holds everything that
# ships and nothing that does not. `dist-check` regenerates into a temporary tree and
# compares, and additionally holds the committed tree to the invariants foundation/0008 states
# about the output itself. Both layers matter: a comparison alone cannot catch a generator
# that is consistently wrong, because it would produce the same defect twice and report
# agreement.
dist:
	python3 scripts/generate_dist.py

dist-check:
	python3 scripts/verify_dist.py

check: validate test dist-check
