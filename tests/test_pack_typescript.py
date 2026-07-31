"""The first target pack: ten templates, two agents, and the constraints `specs/0011` fixes.

A pack is admitted with a fixture (`specs/0012` R13), and this is that fixture. It lives under
`fixtures/` rather than `src/claude/` because `docs/bootstrap.md` D4 records an unresolved conflict
between `specs/0004` R13 and `specs/0008` R23 about where a *production* pack's source belongs. A
fixture pack is not distributed at all, so it does not turn on that decision.

The pack declares all twelve classes of the closed vocabulary — ten deterministic, two judged. That
split is not a convention: `specs/0011` R2 says a template that cannot hold byte identity is not a
weaker template, its class moves to the judged track and an agent produces it. So the track a class
sits on is a claim, and the byte-identity tests below are what back it.
"""

from __future__ import annotations

import ast
import json
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PACK = REPO_ROOT / "fixtures" / "pack-typescript"
sys.path.insert(0, str(PACK / "templates"))

import expand  # noqa: E402
from frontmatter_lib import split_frontmatter  # noqa: E402
from knowledge_graph_lib import load  # noqa: E402

KNOWLEDGE = REPO_ROOT / "fixtures" / "knowledge-two-context" / "knowledge"
VERSION = "0.1.0"

SOURCE_TYPE = {
    "type": "definition", "dto": "definition", "persistence-schema": "definition",
    "migration": "definition", "enum": "lifecycle", "state-machine": "lifecycle",
    "event-schema": "interface", "api-description": "interface",
    "conformance-test": "rule", "documentation": "boundary",
}


class Pack(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.declaration = json.loads((PACK / "pack-declaration.json").read_text())
        cls.graph = load(KNOWLEDGE)
        cls.by_type: dict[str, list[dict]] = {}
        for node in cls.graph.nodes.values():
            if node.is_ko:
                cls.by_type.setdefault(node.kind, []).append(node.data)
        for nodes in cls.by_type.values():
            nodes.sort(key=lambda n: n["id"])

    def sample(self, artifact_class: str) -> dict:
        """The first source object a class can actually expand, skipping any generative gap."""
        for node in self.by_type[SOURCE_TYPE[artifact_class]]:
            try:
                expand.TEMPLATES[artifact_class](node, VERSION)
                return node
            except expand.MissingFact:
                continue
        raise AssertionError(f"no {SOURCE_TYPE[artifact_class]} in the fixture yields {artifact_class}")


class Composition(Pack):
    """specs/0004 R51 and specs/0006 R5."""

    def test_the_declaration_conforms(self) -> None:
        from jsonschema import Draft202012Validator

        schema = json.loads((REPO_ROOT / "src" / "claude" / "schemas" / "pack-declaration.json").read_text())
        self.assertEqual([], list(Draft202012Validator(schema).iter_errors(self.declaration)))

    def test_it_declares_the_whole_closed_vocabulary(self) -> None:
        schema = json.loads((REPO_ROOT / "src" / "claude" / "schemas" / "pack-declaration.json").read_text())
        vocabulary = set(schema["properties"]["produces"]["items"]["properties"]["class"]["enum"])
        self.assertEqual(vocabulary, {entry["class"] for entry in self.declaration["produces"]})

    def test_exactly_one_producer_per_deterministic_class(self) -> None:
        declared = {e["class"] for e in self.declaration["produces"] if e["track"] == "deterministic"}
        self.assertEqual(declared, set(expand.TEMPLATES))

    def test_exactly_one_agent_per_judged_class(self) -> None:
        declared = {e["class"] for e in self.declaration["produces"] if e["track"] == "judged"}
        agents = {p.stem.replace("-producer", "") for p in (PACK / "agents").glob("*.md")}
        self.assertEqual(declared, agents)

    def test_each_agent_produces_one_class_and_says_so(self) -> None:
        for path in sorted((PACK / "agents").glob("*.md")):
            data, body = split_frontmatter(path.read_text())
            self.assertEqual(path.stem, data["name"])
            self.assertIn(path.stem.replace("-producer", ""), body)

    def test_no_agent_has_a_shell(self) -> None:
        for path in sorted((PACK / "agents").glob("*.md")):
            data, _ = split_frontmatter(path.read_text())
            self.assertNotIn("Bash", data["tools"])

    def test_the_declaration_states_nothing_R14_excludes(self) -> None:
        """specs/0004 R14: identity, version, and the classes with track and node types. No more."""
        self.assertEqual(
            {"contract_version", "pack", "version", "framework_contracts", "produces"},
            set(self.declaration),
        )
        for entry in self.declaration["produces"]:
            self.assertEqual({"class", "track", "from"}, set(entry))


class ByteIdentity(Pack):
    """specs/0004 R2 — and specs/0011 R2, which makes the track a claim this backs."""

    def test_every_template_is_byte_identical_across_two_runs(self) -> None:
        for artifact_class, template in sorted(expand.TEMPLATES.items()):
            with self.subTest(artifact_class=artifact_class):
                node = self.sample(artifact_class)
                self.assertEqual(template(node, VERSION), template(node, VERSION))

    def test_every_template_either_produces_output_or_names_the_gap(self) -> None:
        """Coverage is not assumed. A knowledge object short of what a class needs is a
        generative gap (specs/0004 R38), and the template naming it is the correct outcome."""
        produced = gaps = 0
        for artifact_class, template in sorted(expand.TEMPLATES.items()):
            for node in self.by_type[SOURCE_TYPE[artifact_class]]:
                with self.subTest(artifact_class=artifact_class, ko=node["id"]):
                    try:
                        self.assertTrue(template(node, VERSION).strip())
                        produced += 1
                    except expand.MissingFact as gap:
                        self.assertIn(node["id"], str(gap))
                        gaps += 1
        self.assertGreater(produced, 0)

    def test_the_fixture_base_holds_at_least_one_generative_gap(self) -> None:
        """Otherwise the branch above would never run, and R38 would be untested here.

        `ko.rule.sales.proposal-validity` carries no `examples`, so no conformance test can be
        generated from it. specs/0004 R38 blocks the scope rather than inventing one.
        """
        gap = next(n for n in self.by_type["rule"] if "examples" not in n)
        with self.assertRaises(expand.MissingFact):
            expand.conformance_test(gap, VERSION)

    def test_the_pack_version_is_an_input_and_not_a_lookup(self) -> None:
        """specs/0011 R5: a value the knowledge does not hold is supplied by the caller."""
        node = self.sample("type")
        self.assertNotEqual(expand.type_(node, "0.1.0"), expand.type_(node, "0.2.0"))

    def test_every_output_carries_its_source_identifier(self) -> None:
        for artifact_class, template in sorted(expand.TEMPLATES.items()):
            node = self.sample(artifact_class)
            self.assertIn(node["id"], template(node, VERSION))


class ReadsOnlyItsInputs(Pack):
    """specs/0011 R4, read off the module rather than asserted in prose."""

    def module(self) -> ast.Module:
        return ast.parse((PACK / "templates" / "expand.py").read_text())

    def test_it_imports_no_source_of_variation(self) -> None:
        forbidden = {"time", "datetime", "random", "os", "socket", "urllib", "subprocess",
                     "requests", "http", "uuid", "secrets", "pathlib"}
        for node in ast.walk(self.module()):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    self.assertNotIn(alias.name.split(".")[0], forbidden)
            elif isinstance(node, ast.ImportFrom) and node.module:
                self.assertNotIn(node.module.split(".")[0], forbidden)

    def test_it_opens_no_file(self) -> None:
        """R4: no file its inputs did not name — and its inputs name none."""
        for node in ast.walk(self.module()):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                self.assertNotIn(node.func.id, {"open", "input", "eval", "exec"})

    def test_every_template_is_a_pure_function_of_two_arguments(self) -> None:
        for name, template in sorted(expand.TEMPLATES.items()):
            self.assertEqual(2, template.__code__.co_argcount, name)


class MissingFacts(Pack):
    """specs/0011 R10 and specs/0004 R39 — the direction that proves nothing is invented."""

    def test_a_definition_with_no_attributes_fails_naming_the_field(self) -> None:
        node = dict(self.sample("type"))
        node.pop("attributes")
        with self.assertRaises(expand.MissingFact) as caught:
            expand.type_(node, VERSION)
        self.assertIn("attributes", str(caught.exception))

    def test_a_lifecycle_with_no_transitions_fails(self) -> None:
        node = dict(self.sample("state-machine"))
        node.pop("transitions")
        with self.assertRaises(expand.MissingFact):
            expand.state_machine(node, VERSION)

    def test_an_interface_with_no_version_fails(self) -> None:
        node = dict(self.sample("event-schema"))
        node.pop("version")
        with self.assertRaises(expand.MissingFact):
            expand.event_schema(node, VERSION)

    def test_an_attribute_outside_the_primitive_vocabulary_fails(self) -> None:
        node = json.loads(json.dumps(self.sample("type")))
        node["attributes"][0]["type"] = "whatever-the-author-felt-like"
        with self.assertRaises(expand.MissingFact) as caught:
            expand.type_(node, VERSION)
        self.assertIn("primitive vocabulary", str(caught.exception))

    def test_no_template_reads_a_field_with_a_fallback(self) -> None:
        """R10: a default filled in at expansion time is a domain fact authored by the pack."""
        module = ast.parse((PACK / "templates" / "expand.py").read_text())
        for node in ast.walk(module):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "get"
                and len(node.args) > 1
            ):
                self.fail(f"a two-argument .get() supplies a default at line {node.lineno}")

    def test_the_primitive_vocabulary_is_total(self) -> None:
        """A type the knowledge base can hold and this pack cannot express fails at expansion."""
        schema = json.loads((REPO_ROOT / "src" / "claude" / "schemas" / "knowledge-object.json").read_text())
        declared = set(schema["$defs"]["attribute"]["properties"]["type"]["enum"])
        self.assertEqual(declared, set(expand.PRIMITIVE))
        self.assertEqual(declared, set(expand.SQL))


class HoldsNoDomainKnowledge(Pack):
    """specs/0011 R13 and R14, and specs/0005 R13 applied where hard-coding is easiest."""

    def literals(self) -> list[str]:
        """Every string the module actually evaluates, excluding docstrings.

        Comments and docstrings are where a rationale lives — the note explaining why `money`
        maps to a string mentions a billing domain, and that is an argument rather than a fact
        about one repository. What R13 and R14 constrain is what the template *carries*, so this
        reads the evaluated strings and nothing else.
        """
        module = ast.parse((PACK / "templates" / "expand.py").read_text())
        docstrings = set()
        for node in ast.walk(module):
            if isinstance(node, (ast.Module, ast.FunctionDef, ast.ClassDef)):
                first = node.body[0] if node.body else None
                if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant):
                    docstrings.add(id(first.value))
        return [
            node.value
            for node in ast.walk(module)
            if isinstance(node, ast.Constant)
            and isinstance(node.value, str)
            and id(node) not in docstrings
        ]

    def test_it_names_no_object_from_the_fixture_base(self) -> None:
        joined = "\n".join(self.literals())
        for node in self.graph.nodes:
            self.assertNotIn(node, joined)

    def test_it_names_no_downstream_specific_value(self) -> None:
        """specs/0011 R14, and specs/0005 R13 applied where hard-coding is easiest."""
        joined = "\n".join(self.literals()).lower()
        for term in ("invoice", "proposal", "customer", "billing", "sales", "order"):
            self.assertNotIn(term, joined)

    def test_it_references_knowledge_by_identifier_and_never_by_path(self) -> None:
        """specs/0011 R8: a path is a fact about how a repository is arranged."""
        source = (PACK / "templates" / "expand.py").read_text()
        for marker in ("knowledge/", "fixtures/", "src/"):
            self.assertNotIn(marker, source)


class ConformanceSuite(Pack):
    """specs/0004 R36 and R3 — what a judged artifact is checked against."""

    def test_it_is_generated_from_rule_examples(self) -> None:
        covered = [node for node in self.by_type["rule"] if node.get("examples")]
        self.assertTrue(covered, "no rule in the fixture carries examples")
        for node in covered:
            output = expand.conformance_test(node, VERSION)
            for example in node["examples"]:
                self.assertIn(example["then"]["outcome"], output)

    def test_it_is_generated_from_lifecycle_totality(self) -> None:
        for node in self.by_type["lifecycle"]:
            output = expand.conformance_test(node, VERSION)
            for rejection in node["rejections"]:
                self.assertIn(rejection["from"], output)

    def test_it_declares_the_knowledge_object_it_covers(self) -> None:
        """specs/0004 R36: a suite must declare the id of the object it covers."""
        covered = [n for n in self.by_type["rule"] if n.get("examples")] + self.by_type["lifecycle"]
        for node in covered:
            self.assertIn(f"// declares: {node['id']}", expand.conformance_test(node, VERSION))


if __name__ == "__main__":
    unittest.main()
