"""Both directions for the three validators that enforced tested contracts untested.

The gap was named plainly: "The validators for ADRs, concepts, and components
remain untested code enforcing tested contracts." A schema being covered says nothing about the
script that loads it — the cross-file checks, the ones a JSON Schema cannot express, are exactly
the part with no coverage, and they are the part with logic in it.

Every case here follows the shape the knowledge suite already uses: copy the real tree, break
exactly one thing, assert the validator names it. The pristine copy is asserted clean first, in
each class, because a rejection test alone cannot distinguish a working check from one that
rejects everything.

`validate_adrs.py` exposes only `main()`, so it is driven through `sys.argv` and its stdout is
captured. That is the real entry point rather than an internal seam, which is the right thing to
pin: `make validate` calls the CLI, and a refactor that broke the CLI while leaving a helper
intact would be a regression this suite should catch.
"""

from __future__ import annotations

import contextlib
import io
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

import validate_adrs
import validate_components
from validate_concepts import validate as validate_concepts

REPO_ROOT = Path(__file__).resolve().parent.parent


def run(module, root: Path) -> tuple[int, str]:
    """Invoke a validator's `main()` against `root`, returning its exit code and output."""
    buffer = io.StringIO()
    argv = sys.argv
    sys.argv = [module.__name__, str(root)]
    try:
        with contextlib.redirect_stdout(buffer):
            code = module.main()
    finally:
        sys.argv = argv
    return code, buffer.getvalue()


class TreeCase(unittest.TestCase):
    """A disposable copy of one real tree, or of a named subset of it.

    `subset` exists for cost, not for convenience. `validate_adrs.py` compares every line of
    every `## Decision` against 215 operative statements, so one run over the full tree costs
    about five seconds; ten mutation tests over it would cost a minute and make `make test`
    something a maintainer avoids running. Each mutation needs one or two documents, so each
    gets exactly those, and one test over the whole tree keeps the full-scale path covered.
    """

    source: Path
    subset: tuple[str, ...] = ()

    def setUp(self) -> None:
        holder = tempfile.TemporaryDirectory()
        self.addCleanup(holder.cleanup)
        self.root = Path(holder.name) / self.source.name
        if self.subset:
            self.root.mkdir(parents=True)
            for name in self.subset:
                shutil.copy(self.source / name, self.root / name)
        else:
            shutil.copytree(self.source, self.root)

    def rewrite(self, rel: str, old: str, new: str) -> None:
        path = self.root / rel
        text = path.read_text()
        self.assertIn(old, text, f"{rel} does not contain {old!r}; the fixture moved")
        path.write_text(text.replace(old, new, 1))

    def assertNames(self, output: str, *needles: str) -> None:
        if not any(all(n in line for n in needles) for line in output.splitlines()):
            self.fail(f"no reported line holds all of {needles}. Output:\n{output}")


class Concepts(TreeCase):
    source = REPO_ROOT / "docs" / "concepts"

    def test_the_real_bundle_is_clean(self) -> None:
        self.assertEqual([], validate_concepts(self.root))

    def test_id_and_filename_must_agree(self) -> None:
        (self.root / "boundary.md").rename(self.root / "frontier.md")
        problems = validate_concepts(self.root)
        self.assertTrue(
            any("frontier.md" in p and "filename must be" in p for p in problems),
            f"expected a filename/id disagreement; got {problems}",
        )

    def test_a_duplicate_id_is_reported(self) -> None:
        shutil.copy(self.root / "boundary.md", self.root / "boundary-copy.md")
        problems = validate_concepts(self.root)
        self.assertTrue(
            any("already used by" in p for p in problems),
            f"expected a duplicate-id report; got {problems}",
        )

    def test_a_link_to_a_removed_concept_is_reported(self) -> None:
        """The bundle's own cross-references, which nothing checked until three of them dangled.

        Three concepts kept linking to two that had been removed, and every validator passed. The
        specification validator had always held specifications to this; the bundle was the asymmetry.
        """
        path = self.root / "boundary.md"
        path.write_text(path.read_text() + "\nSee [a removed concept](gone-from-the-bundle.md).\n")
        problems = validate_concepts(self.root)
        self.assertTrue(
            any("gone-from-the-bundle.md" in p and "resolves to no file" in p for p in problems),
            f"expected a dangling concept link; got {problems}",
        )

    def test_a_link_to_a_present_concept_is_accepted(self) -> None:
        """Otherwise the check above could be passing because it rejects every link."""
        path = self.root / "boundary.md"
        path.write_text(path.read_text() + "\nSee [definition](definition.md).\n")
        self.assertEqual([], validate_concepts(self.root))

    def test_an_absolute_uri_is_not_followed(self) -> None:
        """A link out of the repository is not a cross-reference and is not this check's to resolve."""
        path = self.root / "boundary.md"
        path.write_text(path.read_text() + "\nSee [the harness docs](https://code.claude.com/docs/en/hooks).\n")
        self.assertEqual([], validate_concepts(self.root))

    def test_a_source_that_resolves_to_no_file_is_reported(self) -> None:
        self.rewrite("boundary.md", "resource: foundation/", "resource: foundation/9999-gone-")
        problems = validate_concepts(self.root)
        self.assertTrue(
            any("resolves to no file" in p for p in problems),
            f"expected a dangling-source report; got {problems}",
        )

    def test_an_absolute_source_path_is_reported(self) -> None:
        self.rewrite(
            "boundary.md",
            "resource: foundation/0003-knowledge-ontology-and-notation.md",
            "resource: /etc/passwd",
        )
        problems = validate_concepts(self.root)
        self.assertTrue(
            any("repo-relative path or an absolute URI" in p for p in problems),
            f"expected an absolute-path report; got {problems}",
        )

    def test_a_traversing_source_path_is_reported(self) -> None:
        self.rewrite(
            "boundary.md",
            "resource: foundation/0003-knowledge-ontology-and-notation.md",
            "resource: ../../etc/passwd",
        )
        problems = validate_concepts(self.root)
        self.assertTrue(
            any("repo-relative path or an absolute URI" in p for p in problems),
            f"expected a traversal report; got {problems}",
        )

    def test_a_missing_frontmatter_fence_is_reported(self) -> None:
        (self.root / "boundary.md").write_text("# boundary\n\nno frontmatter at all.\n")
        problems = validate_concepts(self.root)
        self.assertTrue(
            any("frontmatter fence" in p for p in problems),
            f"expected a fence report; got {problems}",
        )

    def test_a_schema_violation_is_reported(self) -> None:
        self.rewrite("boundary.md", "contract_version: concept/1", "contract_version: concept/9")
        problems = validate_concepts(self.root)
        self.assertTrue(
            any("contract_version" in p for p in problems),
            f"expected a schema report; got {problems}",
        )

    def test_the_index_is_not_validated_as_a_concept(self) -> None:
        """`index.md` is reserved; validating it as a concept would demand frontmatter it lacks."""
        self.assertEqual([], validate_concepts(self.root))


ADR_UNDER_TEST = "0010-projection-names-the-graph-derived-artifact.md"


class AdrsFullTree(unittest.TestCase):
    """One run over every ADR, which is the scale `make validate` actually pays."""

    def test_the_real_tree_is_clean(self) -> None:
        code, output = run(validate_adrs, REPO_ROOT / "docs" / "adr")
        self.assertEqual(0, code, output)
        self.assertIn("all ADRs valid", output)


class Adrs(TreeCase):
    source = REPO_ROOT / "docs" / "adr"
    subset = (ADR_UNDER_TEST,)

    def test_the_subset_is_clean_before_any_mutation(self) -> None:
        code, output = run(validate_adrs, self.root)
        self.assertEqual(0, code, output)

    def test_id_and_filename_must_agree(self) -> None:
        target = next(self.root.glob("0010-*.md"))
        target.rename(self.root / f"0099-{target.name.split('-', 1)[1]}")
        code, output = run(validate_adrs, self.root)
        self.assertEqual(1, code, output)
        self.assertNames(output, "0099-", "filename must start with")

    def test_a_missing_required_section_is_reported(self) -> None:
        self.rewrite(ADR_UNDER_TEST, "## Consequences", "## Fallout")
        code, output = run(validate_adrs, self.root)
        self.assertEqual(1, code, output)
        self.assertNames(output, "0010-", "## Consequences")

    def test_a_proposed_adr_needs_its_validation_section(self) -> None:
        self.rewrite(
            ADR_UNDER_TEST,
            "status: accepted",
            "status: proposed",
        )
        code, output = run(validate_adrs, self.root)
        self.assertEqual(1, code, output)
        self.assertNames(output, "0010-", "status is proposed")

    def test_an_unknown_contract_version_is_reported(self) -> None:
        self.rewrite(
            ADR_UNDER_TEST,
            "contract_version: adr/1",
            "contract_version: adr/7",
        )
        code, output = run(validate_adrs, self.root)
        self.assertEqual(1, code, output)
        self.assertNames(output, "0010-", "names no contract")

    def test_a_duplicate_id_is_reported(self) -> None:
        source = next(self.root.glob("0010-*.md"))
        shutil.copy(source, self.root / "0010-a-second-file-with-one-id.md")
        code, output = run(validate_adrs, self.root)
        self.assertEqual(1, code, output)
        self.assertNames(output, "already used by")

    def test_restating_an_operative_rule_is_reported(self) -> None:
        """The non-restatement check, driven by a line lifted out of CLAUDE.md itself."""
        operative = validate_adrs.operative_lines()
        self.assertTrue(operative, "no operative lines were extracted; the check cannot fire")
        _source, line = max(operative, key=lambda pair: len(pair[1]))
        target = self.root / ADR_UNDER_TEST
        text = target.read_text().replace("## Decision", f"## Decision\n\n{line}\n", 1)
        target.write_text(text)
        code, output = run(validate_adrs, self.root)
        self.assertEqual(1, code, output)
        self.assertNames(output, "restates")

    def test_an_unquoted_id_is_explained_rather_than_type_checked(self) -> None:
        self.rewrite(
            ADR_UNDER_TEST, 'id: "0010"', "id: 0010"
        )
        code, output = run(validate_adrs, self.root)
        self.assertEqual(1, code, output)
        self.assertNames(output, "0010-")


class Components(TreeCase):
    source = REPO_ROOT / "src" / "claude"

    def test_the_real_tree_is_clean(self) -> None:
        code, output = run(validate_components, self.root)
        self.assertEqual(0, code, output)
        self.assertIn("all components valid", output)

    def test_a_skill_name_must_equal_its_directory(self) -> None:
        self.rewrite("skills/ingest-domain/SKILL.md", "name: ingest-domain", "name: ingest-domains")
        code, output = run(validate_components, self.root)
        self.assertEqual(1, code, output)
        self.assertNames(output, "ingest-domain")

    def test_an_agent_filename_must_equal_its_name(self) -> None:
        (self.root / "agents" / "concept-author.md").rename(self.root / "agents" / "author.md")
        code, output = run(validate_components, self.root)
        self.assertEqual(1, code, output)
        self.assertNames(output, "author.md")

    def test_a_duplicate_agent_name_is_reported(self) -> None:
        nested = self.root / "agents" / "nested"
        nested.mkdir()
        shutil.copy(self.root / "agents" / "concept-author.md", nested / "concept-author.md")
        code, output = run(validate_components, self.root)
        self.assertEqual(1, code, output)
        self.assertNames(output, "concept-author")

    def test_a_skill_directory_without_skill_md_is_reported(self) -> None:
        (self.root / "skills" / "orphan").mkdir()
        (self.root / "skills" / "orphan" / "notes.md").write_text("no entrypoint here\n")
        code, output = run(validate_components, self.root)
        self.assertEqual(1, code, output)
        self.assertNames(output, "orphan")

    def test_an_overlong_skill_body_is_reported(self) -> None:
        path = self.root / "skills" / "ingest-domain" / "SKILL.md"
        path.write_text(path.read_text() + "\nfiller\n" * 600)
        code, output = run(validate_components, self.root)
        self.assertEqual(1, code, output)
        self.assertNames(output, "ingest-domain")

    def test_a_commands_directory_is_rejected_by_name(self) -> None:
        """ADR-0009 merged custom commands into skills; the class is rejected, not empty."""
        (self.root / "commands").mkdir()
        code, output = run(validate_components, self.root)
        self.assertEqual(1, code, output)
        self.assertNames(output, "commands")

    def test_an_unknown_component_class_is_rejected(self) -> None:
        (self.root / "workers").mkdir()
        code, output = run(validate_components, self.root)
        self.assertEqual(1, code, output)
        self.assertNames(output, "workers", "no contract exists")

    def test_a_schema_violation_is_reported(self) -> None:
        self.rewrite("agents/concept-author.md", "tools: Read, Grep, Glob, Write, Edit", "tools: 17")
        code, output = run(validate_components, self.root)
        self.assertEqual(1, code, output)
        self.assertNames(output, "concept-author")

    def test_an_absent_tree_is_reported_and_not_a_failure(self) -> None:
        """The contract precedes the first component by design (ADR-0009)."""
        code, output = run(validate_components, self.root / "does-not-exist")
        self.assertEqual(0, code, output)
        self.assertIn("does not exist yet", output)


if __name__ == "__main__":
    unittest.main()


class Hooks(TreeCase):
    """The hook class, whose contract is its declaration rather than frontmatter."""

    source = REPO_ROOT / "src" / "claude"

    def test_the_real_tree_is_clean(self) -> None:
        code, output = run(validate_components, self.root)
        self.assertEqual(0, code, output)
        self.assertIn("1 hook(s)", output)

    def test_a_declared_hook_with_no_script_is_reported(self) -> None:
        (self.root / "hooks" / "reject-derived-write.py").unlink()
        code, output = run(validate_components, self.root)
        self.assertEqual(1, code, output)
        self.assertNames(output, "reject-derived-write.py", "does not hold")

    def test_an_undeclared_script_is_reported(self) -> None:
        (self.root / "hooks" / "stowaway.py").write_text("#!/usr/bin/env python3\n")
        code, output = run(validate_components, self.root)
        self.assertEqual(1, code, output)
        self.assertNames(output, "stowaway.py", "never be loaded")

    def test_a_missing_declaration_is_reported(self) -> None:
        (self.root / "hooks" / "hooks.declaration.json").unlink()
        code, output = run(validate_components, self.root)
        self.assertEqual(1, code, output)
        self.assertNames(output, "hooks.declaration.json")

    def test_a_default_timeout_is_refused(self) -> None:
        """foundation/0010 R11: 600 is the default the requirement exists to displace."""
        self.rewrite("hooks/hooks.declaration.json", '"timeout": 10', '"timeout": 600')
        code, output = run(validate_components, self.root)
        self.assertEqual(1, code, output)
        self.assertNames(output, "timeout")

    def test_an_event_that_cannot_block_is_refused(self) -> None:
        """foundation/0010 R12: a guarantee bound to an event that cannot deny is one that logs."""
        self.rewrite("hooks/hooks.declaration.json", '"PreToolUse"', '"PostToolUse"')
        code, output = run(validate_components, self.root)
        self.assertEqual(1, code, output)
        self.assertNames(output, "event")

    def test_a_hook_with_no_stated_guarantee_is_refused(self) -> None:
        """foundation/0010 R10 and foundation/0006 R7: one hook, one named guarantee."""
        import json as _json

        path = self.root / "hooks" / "hooks.declaration.json"
        data = _json.loads(path.read_text())
        del data["hooks"][0]["guarantee"]
        path.write_text(_json.dumps(data, indent=2) + "\n")
        code, output = run(validate_components, self.root)
        self.assertEqual(1, code, output)
        self.assertNames(output, "guarantee")


class CapabilityDeclarations(unittest.TestCase):
    """`foundation/0007` R22: one validator over the declaration and the component it declares.

    R21 makes a declaration a separate artifact, which buys a closed harness contract and costs two
    records of one fact. These cover the check that keeps the cost from becoming drift, in the
    direction that matters — each mutation below is a disagreement a reader would not notice.
    """

    import json as _json

    SOURCE = Path(__file__).resolve().parent.parent / "src" / "claude"

    def tree(self) -> Path:
        holder = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, holder)
        root = Path(holder) / "claude"
        shutil.copytree(self.SOURCE, root, ignore=shutil.ignore_patterns("__pycache__"))
        return root

    def problems(self, mutate=None) -> list[str]:
        root = self.tree()
        path = root / validate_components.CAPABILITY_DECLARATION
        if mutate is not None:
            document = self._json.loads(path.read_text())
            mutate(document)
            path.write_text(self._json.dumps(document))
        failures: list[str] = []
        validate_components.check_capability_declarations(root, failures)
        return failures

    def test_the_authored_set_passes_as_committed(self) -> None:
        self.assertEqual([], self.problems())

    def test_a_grant_wider_than_the_component_is_reported(self) -> None:
        """R14: a grant wider than the steps is a defect even when unused."""
        found = self.problems(lambda d: d["declarations"][0]["grant"]["tools"].append("Bash"))
        self.assertEqual(1, len(found))
        self.assertIn("declares grant", found[0])

    def test_a_grant_narrower_than_the_component_is_reported(self) -> None:
        """The other direction: a declaration that misdescribes what actually runs."""
        found = self.problems(lambda d: d["declarations"][0]["grant"]["tools"].pop())
        self.assertIn("declares grant", found[0])

    def test_an_identifier_that_does_not_match_the_component_name_is_reported(self) -> None:
        """The disagreement has to be injected into the component, not the declaration.

        Pointing the declaration at a different component finds one whose name matches its own
        filename, so identity still agrees and only the grant diverges. What this covers is the
        case a rename produces: the component's frontmatter moves and the declaration does not.
        """
        root = self.tree()
        agent = root / "agents" / "impact-analyst.md"
        agent.write_text(agent.read_text().replace("name: impact-analyst", "name: renamed-analyst", 1))
        failures: list[str] = []
        validate_components.check_capability_declarations(root, failures)
        self.assertTrue(failures)
        self.assertIn("must agree", failures[0])

    def test_a_declaration_with_no_component_is_reported(self) -> None:
        found = self.problems(lambda d: d["declarations"][0].update(identifier="not-a-component"))
        self.assertIn("no component answers to it", found[0])

    def test_an_incomplete_declaration_is_reported(self) -> None:
        """R1: a declaration that is incomplete is not a declaration."""
        found = self.problems(lambda d: d["declarations"][0].pop("failure_outcomes"))
        self.assertTrue(found)
        self.assertIn("failure_outcomes", found[0])

    def test_a_duplicate_identifier_is_reported(self) -> None:
        found = self.problems(
            lambda d: d["declarations"].append(dict(d["declarations"][0]))
        )
        self.assertIn("twice", found[0])

    def test_a_missing_set_is_reported(self) -> None:
        root = self.tree()
        (root / validate_components.CAPABILITY_DECLARATION).unlink()
        failures: list[str] = []
        validate_components.check_capability_declarations(root, failures)
        self.assertIn("R1 is unenforceable", failures[0])


class ExistenceClaims(unittest.TestCase):
    """A foundation document may say a tree is empty only while it is.

    Six specifications drifted the same way — each opened Provenance with an existence claim about
    this repository and kept it after the thing was built. Every document still validated, because
    nothing compared prose against the filesystem. These cover the check that closes it, including
    that it can fail: a check over prose is worth exactly what its negative case proves.
    """

    import check_existence_claims as _ce

    FOUNDATION = Path(__file__).resolve().parent.parent / "foundation"

    def test_every_claim_in_foundation_holds(self) -> None:
        problems: list[str] = []
        for path in sorted(self.FOUNDATION.glob("*.md")):
            problems.extend(self._ce.problems_for(path, path.read_text()))
        self.assertEqual([], problems, "\n".join(["", *problems]))

    def test_a_reintroduced_claim_is_reported(self) -> None:
        """The exact drift that happened: 'No hook exists' while one ships."""
        problems = self._ce.problems_for(
            self.FOUNDATION / "0010-hook-system.md", "No hook exists, and none is planned.\n"
        )
        self.assertEqual(1, len(problems))
        self.assertIn("claims 'hook' is absent", problems[0])

    def test_a_claim_is_matched_wherever_it_sits(self) -> None:
        """Moving the sentence out of Provenance does not exempt it."""
        body = "## Requirements\n\n- **R1** — Because no pack exists, nothing binds.\n"
        self.assertTrue(self._ce.problems_for(self.FOUNDATION / "0012-target-pack-model.md", body))

    def test_a_claim_of_existence_is_not_checked(self) -> None:
        """Naming a mechanism a requirement needs is how one is written before it arrives."""
        body = "A validator in scripts/ rejects an incomplete declaration.\n"
        self.assertEqual([], self._ce.problems_for(self.FOUNDATION / "0007-capability-contracts.md", body))

    def test_every_subject_names_evidence_that_resolves(self) -> None:
        """A row whose predicate can never be true would make its phrases unreachable."""
        for subject, spec in self._ce.SUBJECTS.items():
            with self.subTest(subject=subject):
                self.assertTrue(spec["evidence"](), f"{subject}: predicate matches nothing")


class DeclaredHooks(unittest.TestCase):
    """A declared hook must be one the hook declaration installs.

    A hook has no frontmatter, so `hooks.declaration.json` is its second record and the agreement
    half of R22 compares against that instead. Without this, a declaration could describe a
    guarantee nothing ever fires.
    """

    SOURCE = Path(__file__).resolve().parent.parent / "src" / "claude"

    def test_the_declared_hook_is_installed(self) -> None:
        failures: list[str] = []
        validate_components.declared_hook(self.SOURCE, "reject-derived-write", "rel", failures)
        self.assertEqual([], failures)

    def test_a_hook_nothing_installs_is_reported(self) -> None:
        failures: list[str] = []
        validate_components.declared_hook(self.SOURCE, "imaginary-hook", "rel", failures)
        self.assertEqual(1, len(failures))
        self.assertIn("does not install", failures[0])
