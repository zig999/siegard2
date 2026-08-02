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

.PHONY: validate foundation test dist dist-check check

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
	python3 scripts/validate_concepts.py docs/concepts || fail=1; \
	python3 scripts/validate_components.py || fail=1; \
	python3 scripts/check_component_prose.py || fail=1; \
	python3 scripts/check_capabilities.py || fail=1; \
	exit $$fail

# `check_component_prose.py` sits beside `validate_components.py` and answers a different question.
# That script validates each component against its frontmatter contract and holds the declaration to
# the component; this one holds the component's *prose* to the contracts it declares, and holds the
# agent set to being reachable. Every finding it reports was found by hand first — a field the prose
# named and the contract lacked, an agent no skill invoked — and each was invisible to a check that
# looks at one component at a time against one schema.
#
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
# **The knowledge validator is not wired here, and foundation/0003 R31 requires one.** It ran over
# `fixtures/*/knowledge`, and that tree was removed by a maintainer's decision along with the
# derived-tree checks and the ontology measurement that read it — the `knowledge` target went with
# them. R31 obliges the *distribution* to ship a boundary validator, which is an obligation on
# `src/claude/` rather than on this file; what is missing here is a base for it to run against.
# The gap is named rather than papered over with a target that validates nothing: a green run over
# an empty glob is worse than an absent one.
#
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
