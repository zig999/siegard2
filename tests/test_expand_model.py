"""The expansion step, over the worked example its own producer publishes.

`foundation/0004` R6 puts a property that must hold regardless of model judgment in a script, and
the measured evidence said this one was: classifying 24 constructs cost 75,329 tokens and produced a
mapping 1:1 with the model in every entry, because spec 0003 states that mapping as a closed table.
What used to be an agent is a function here, so the assertions below are of a kind the agent could
not offer — the same input yields the same tree, byte for byte, every run.

The input is `domain-modeler`'s own worked example rather than a fixture. Two reasons. The example
is already held to `domain-model/4` by C02 in `check_component_prose.py`, so it cannot drift out of
conformance without another check firing first; and this repository keeps no fixtures per
`docs/adr/0019-the-repository-keeps-no-fixtures.md`, so a tree invented here would be one.

What is asserted is the contract at each end and the three outcomes between them. What is not
asserted is prose: the expansion writes no sentence, and the two body headings it places are empty
by construction.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

from . import SHIPPED_ROOT, SHIPPED_SCHEMAS

EXPANDER = SHIPPED_ROOT / "bin" / "expand_model.py"
MODELLER = SHIPPED_ROOT / "agents" / "domain-modeler.md"
FENCED = re.compile(r"```json\n(\{.*?\n\})\n```", re.S)
STAMP = ("expand-model", "2026-08-01T18:00:00Z")


def validator(name: str) -> Draft202012Validator:
    return Draft202012Validator(json.loads((SHIPPED_SCHEMAS / name).read_text()))


def frontmatter(path: Path) -> dict:
    return yaml.safe_load(re.match(r"^---\n(.*?)\n---\n", path.read_text(), re.S).group(1))


class Run(unittest.TestCase):
    """One expansion, shared. Each test reads it; none mutates the tree."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.model = json.loads(FENCED.search(MODELLER.read_text()).group(1))
        cls.staged = validator("staged-knowledge-object.json")
        cls.base = validator("knowledge-object.json")
        cls.plan_contract = validator("knowledge-intake-plan.json")
        cls.plan, cls.root, cls.result = cls.expand(cls.model)

    @staticmethod
    def expand(model: dict, intake: str = "ki_4c1e7a90"):
        holder = Path(tempfile.mkdtemp())
        (holder / "model.json").write_text(json.dumps(model))
        result = subprocess.run(
            [sys.executable, "-B", str(EXPANDER), str(holder / "model.json"),
             str(holder / "staging"), intake, *STAMP],
            capture_output=True, text=True,
        )
        plan = json.loads(result.stdout) if result.returncode == 0 else None
        return plan, holder / "staging", result

    def objects(self) -> list[Path]:
        return sorted(self.root.rglob("*.md"))

    @staticmethod
    def expand_into(model: dict, root: Path):
        """A second expansion over an existing tree, which is what re-expansion means."""
        holder = root.parent
        (holder / "again.json").write_text(json.dumps(model))
        return subprocess.run(
            [sys.executable, "-B", str(EXPANDER), str(holder / "again.json"), str(root),
             "ki_4c1e7a90", *STAMP],
            capture_output=True, text=True,
        )

    @staticmethod
    def entry_for(plan: dict, construct: str, identifier: str) -> dict:
        """The entry for one construct, when two constructs share a name.

        The worked example holds an aggregate and a definition both called `Proposal`. Selecting by
        name would pick whichever came first — which is the ambiguity the expansion refuses when a
        *reference* resolves to two, and which a test has no business resolving by luck.
        """
        for entry in plan["entries"]:
            if entry.get("proposed_id") == identifier:
                return entry
        refused = [e for e in plan["entries"]
                   if e["construct"] == construct and e["outcome"] != "classified"]
        assert len(refused) == 1, f"{construct}: {len(refused)} unclassified entries"
        return refused[0]


class TheRun(Run):
    def test_it_exits_zero_and_writes_a_tree(self) -> None:
        self.assertEqual(0, self.result.returncode, self.result.stderr)
        self.assertTrue(self.objects(), "no object was written")

    def test_the_plan_conforms(self) -> None:
        self.assertEqual([], list(self.plan_contract.iter_errors(self.plan)))

    def test_every_construct_in_the_model_has_an_entry(self) -> None:
        """Partial completion is readable only if the count is checkable against the input."""
        kinds = ("contexts", "aggregates", "definitions", "rules",
                 "lifecycles", "interfaces", "processes")
        constructs = sum(len(self.model.get(kind) or []) for kind in kinds)
        constructs += len(self.model.get("excluded") or [])
        self.assertEqual(constructs, len(self.plan["entries"]))

    def test_one_file_per_classified_entry_and_no_other(self) -> None:
        classified = [e for e in self.plan["entries"] if e["outcome"] == "classified"]
        self.assertEqual(len(classified), len(self.objects()))

    def test_an_unclassified_construct_writes_nothing(self) -> None:
        excluded = self.model["excluded"][0]["subject"]
        entry = next(e for e in self.plan["entries"] if e["construct"] == excluded)
        self.assertEqual("unmapped", entry["outcome"])
        self.assertNotIn("proposed_id", entry)


class TheContractAtEachEnd(Run):
    def test_every_object_conforms_to_the_staged_contract(self) -> None:
        for path in self.objects():
            with self.subTest(object=path.name):
                self.assertEqual([], list(self.staged.iter_errors(frontmatter(path))))

    def test_no_object_conforms_to_the_base_contract(self) -> None:
        """The boundary promotion guards: the four fields only judgment supplies are absent."""
        for path in self.objects():
            with self.subTest(object=path.name):
                document = dict(frontmatter(path), contract_version="knowledge-object/5")
                self.assertNotEqual([], list(self.base.iter_errors(document)))

    def test_the_base_refuses_the_enrichment_fields_of_every_object(self) -> None:
        """Every staged object is short of the same three, whatever else it is short of."""
        for path in self.objects():
            document = dict(frontmatter(path), contract_version="knowledge-object/5")
            missing = {
                str(error).split("'")[1]
                for error in self.base.iter_errors(document)
                if "is a required property" in str(error)
            }
            with self.subTest(object=path.name):
                self.assertTrue({"question", "description", "out_of_scope"} & missing, missing)

    def test_the_base_also_refuses_an_attribute_the_domain_has_not_finished(self) -> None:
        """The line between the two contracts, one level down from the type's own fields.

        A staged object may carry an attribute whose `max_length` nobody stated, with the gap
        naming it; the base may not. So a `kind: domain` gap on an attribute parameter blocks
        promotion until the domain answers, which is what gives such a gap teeth at the boundary
        rather than letting every incompleteness through. An attribute typed outside the closed
        vocabulary never reaches either contract — that is a refusal, and nothing is written.
        """
        proposal = self.root / "definition" / "sales" / "proposal.md"
        data = frontmatter(proposal)
        self.assertIn("attributes[number].max_length", {g["field"] for g in data["gaps"]})
        self.assertEqual([], list(self.staged.iter_errors(data)))
        missing = {
            str(error).split("'")[1]
            for error in self.base.iter_errors(dict(data, contract_version="knowledge-object/5"))
            if "is a required property" in str(error)
        }
        self.assertIn("max_length", missing)


class TheThreeOutcomes(Run):
    def test_a_missing_fact_is_a_gap_and_the_object_is_written(self) -> None:
        proposal = next(p for p in self.objects() if p.name == "proposal.md"
                        and p.parent.name == "sales" and "definition" in p.parts)
        fields = {gap["field"] for gap in frontmatter(proposal)["gaps"]}
        self.assertIn("attributes[number].max_length", fields,
                      "a string whose length the request never stated is a gap, not a refusal")

    def test_a_wrong_fact_is_a_refusal_and_nothing_is_written(self) -> None:
        model = json.loads(json.dumps(self.model))
        model["definitions"][0]["attributes"][1]["type"] = "Date"  # outside the closed vocabulary
        plan, root, _ = self.expand(model)
        entry = self.entry_for(plan, "Proposal", "ko.definition.sales.proposal")
        self.assertEqual("refused", entry["outcome"])
        self.assertIn("closed primitive vocabulary", entry["reason"])
        self.assertFalse((root / "definition" / "sales" / "proposal.md").exists())

    def test_an_unresolvable_reference_is_a_refusal(self) -> None:
        model = json.loads(json.dumps(self.model))
        model["definitions"][0]["attributes"][3]["target"] = "Nobody"
        plan, _root, _ = self.expand(model)
        entry = self.entry_for(plan, "Proposal", "ko.definition.sales.proposal")
        self.assertEqual("refused", entry["outcome"])
        self.assertIn("matches no element", entry["reason"])

    def test_every_authoring_gap_is_the_same_three_fields(self) -> None:
        """Closed and identical per object: no analysis carries them, and a later pass writes them."""
        for path in self.objects():
            authoring = {g["field"] for g in frontmatter(path)["gaps"] if g["kind"] == "authoring"}
            with self.subTest(object=path.name):
                self.assertEqual({"question", "out_of_scope", "description"}, authoring)

    def test_a_domain_gap_says_what_the_domain_would_have_to_state(self) -> None:
        for path in self.objects():
            for gap in frontmatter(path)["gaps"]:
                if gap["kind"] == "domain":
                    with self.subTest(object=path.name, field=gap["field"]):
                        self.assertTrue(gap.get("why"))


class WhatItSuppliesAndWhatItDoesNot(Run):
    def test_it_writes_no_prose(self) -> None:
        """Both sections are present and empty: the enrichment pass fills them, and a third
        heading is what pre-placing these two prevents."""
        for path in self.objects():
            body = path.read_text().split("\n---\n", 1)[1]
            headings = re.findall(r"^## (.+)$", body, re.MULTILINE)
            with self.subTest(object=path.name):
                self.assertEqual(2, len(headings))
                self.assertEqual("", re.sub(r"^#.*$", "", body, flags=re.MULTILINE).strip())

    def test_origin_is_copied_and_never_decided(self) -> None:
        by_id = {e["proposed_id"]: e for e in self.plan["entries"] if e["outcome"] == "classified"}
        for path in self.objects():
            data = frontmatter(path)
            with self.subTest(object=path.name):
                self.assertEqual(by_id[data["id"]]["origin"], data["origin"])

    def test_the_path_is_computable_from_the_identifier(self) -> None:
        """R33: a path from an id and an id from a path, with no lookup."""
        for path in self.objects():
            data = frontmatter(path)
            expected = Path(data["type"], *data["id"].split(".")[2:]).with_suffix(".md")
            with self.subTest(object=path.name):
                self.assertEqual(expected, path.relative_to(self.root))

    def test_sources_name_the_request_and_not_the_model(self) -> None:
        """The model is an artifact this framework produced, never material the domain supplied."""
        for path in self.objects():
            resources = {source["resource"] for source in frontmatter(path)["sources"]}
            with self.subTest(object=path.name):
                self.assertEqual(set(self.model["request"]["artifacts"]), resources)


class ItIsDeterministic(Run):
    def test_two_runs_over_one_model_agree_byte_for_byte(self) -> None:
        """The assertion an agent could not offer, and the reason this is a script."""
        _plan, other, _ = self.expand(self.model)
        first = {p.relative_to(self.root): p.read_text() for p in self.objects()}
        second = {p.relative_to(other): p.read_text() for p in sorted(other.rglob("*.md"))}
        self.assertEqual(first, second)

    def test_the_plan_is_sorted_so_two_runs_compare_directly(self) -> None:
        ids = [e["proposed_id"] for e in self.plan["entries"] if e["outcome"] == "classified"]
        self.assertEqual(sorted(ids), ids)


class ItRefusesRatherThanGuessing(Run):
    def test_a_model_of_another_version_is_refused(self) -> None:
        model = dict(self.model, contract_version="domain-model/3")
        _plan, _root, result = self.expand(model)
        self.assertEqual(1, result.returncode)
        self.assertIn("domain-model/4", result.stderr)

    def test_a_blocked_model_ends_the_run(self) -> None:
        model = dict(self.model, state="blocked", blocking_reason="the request names no domain")
        _plan, _root, result = self.expand(model)
        self.assertEqual(1, result.returncode)
        self.assertIn("blocked", result.stderr)

    def test_an_absent_model_cannot_run(self) -> None:
        result = subprocess.run(
            [sys.executable, "-B", str(EXPANDER), "/definitely/not/here", "/tmp/x",
             "ki_4c1e7a90", *STAMP],
            capture_output=True, text=True,
        )
        self.assertEqual(2, result.returncode)
        self.assertIn("cannot run", result.stderr)

    def test_the_stamp_comes_from_the_caller(self) -> None:
        """A value this script minted could not be reproduced and compared."""
        for path in self.objects():
            with self.subTest(object=path.name):
                self.assertEqual({"by": STAMP[0], "at": STAMP[1]}, frontmatter(path)["generated"])




class Reexpansion(Run):
    """Running the expansion again over a tree an enrichment already touched — §6.5 of the proposal.

    The partition `field_ownership` declares is read here for the third time: the expansion writes
    its own side, the check rejects a change on that side, and this preserves the other. The clause
    that matters is the third — an enrichment written against a design that has since changed is
    stale, and preserving it silently would leave the object inconsistent with nothing recording it.
    """

    def enriched(self, root: Path, relative: str) -> Path:
        """One object, as the enrichment pass would leave it: four fields written, gaps closed."""
        path = root / relative
        data, body = path.read_text().split("\n---\n", 1)
        front = yaml.safe_load(data[4:])
        front["question"] = "What is a proposal?"
        front["description"] = "A priced offer that stops being acceptable after a bounded period."
        front["out_of_scope"] = ["How a proposal is stored."]
        front["gaps"] = [g for g in front["gaps"] if g["kind"] != "authoring"]
        filled = body.replace("## Answer\n", "## Answer\n\nA proposal is a priced offer.\n")
        path.write_text("---\n" + yaml.safe_dump(front, sort_keys=False, allow_unicode=True)
                        + "---\n" + filled)
        return path

    def test_an_unchanged_model_leaves_the_enrichment_alone(self) -> None:
        _plan, root, _ = self.expand(self.model)
        target = self.enriched(root, "definition/sales/proposal.md")
        before = target.read_text()
        self.expand_into(self.model, root)
        self.assertEqual(before, target.read_text())

    def test_a_changed_design_keeps_the_prose_and_reopens_the_gaps(self) -> None:
        _plan, root, _ = self.expand(self.model)
        target = self.enriched(root, "definition/sales/proposal.md")
        moved = json.loads(json.dumps(self.model))
        moved["definitions"][0]["attributes"].append(
            {"name": "currency", "type": "string", "max_length": 3, "required": True})
        self.expand_into(moved, root)
        data = frontmatter(target)
        self.assertEqual("What is a proposal?", data["question"], "the sentence survived")
        self.assertIn("A proposal is a priced offer.", target.read_text(), "the body survived")
        authoring = {g["field"] for g in data["gaps"] if g["kind"] == "authoring"}
        self.assertEqual({"question", "description", "out_of_scope"}, authoring,
                         "what the enrichment closed is owed again, because the design moved")
        self.assertIn("currency", {a["name"] for a in data["attributes"]})

    def test_a_domain_gap_is_never_reopened_because_it_never_closed(self) -> None:
        _plan, root, _ = self.expand(self.model)
        target = self.enriched(root, "definition/sales/proposal.md")
        before = [g for g in frontmatter(target)["gaps"] if g["kind"] == "domain"]
        moved = json.loads(json.dumps(self.model))
        moved["definitions"][0]["ddd"] = "entity"
        self.expand_into(moved, root)
        after = [g for g in frontmatter(target)["gaps"] if g["kind"] == "domain"]
        self.assertEqual(before, after)

    def test_an_object_the_enrichment_never_reached_is_simply_rewritten(self) -> None:
        _plan, root, _ = self.expand(self.model)
        untouched = root / "rule" / "sales" / "proposal-expiration.md"
        before = untouched.read_text()
        self.expand_into(self.model, root)
        self.assertEqual(before, untouched.read_text())




class TheEnrichmentCheck(Run):
    """The only thing enforcing what the enrichment may touch — §9.1 of the proposal.

    A tool grant names tools, not files, and certainly not keys within a file, so `Edit` restricted
    to four fields is prose until something checks it. This is that something, which is why it lands
    before the pass it checks rather than after.

    It compares against a re-derived expansion rather than a stored baseline. The expansion is a
    function, so what it wrote is recoverable at any time; a recorded copy would be a second
    artifact to keep in step.
    """

    CHECKER = SHIPPED_ROOT / "bin" / "check_enrichment.py"

    def check(self, root: Path, model: dict | None = None):
        holder = root.parent
        (holder / "checked.json").write_text(json.dumps(model or self.model))
        return subprocess.run(
            [sys.executable, "-B", str(self.CHECKER), str(holder / "checked.json"), str(root),
             "ki_4c1e7a90", *STAMP],
            capture_output=True, text=True,
        )

    def edit(self, root: Path, relative: str, change) -> None:
        path = root / relative
        head, body = path.read_text().split("\n---\n", 1)
        data = yaml.safe_load(head[4:])
        body = change(data, body) or body
        path.write_text("---\n" + yaml.safe_dump(data, sort_keys=False, allow_unicode=True)
                        + "---\n" + body)

    def test_an_untouched_tree_passes(self) -> None:
        _plan, root, _ = self.expand(self.model)
        result = self.check(root)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_a_legitimate_enrichment_passes(self) -> None:
        """The four fields and the body, with the authoring gaps closed."""
        _plan, root, _ = self.expand(self.model)

        def enrich(data, body):
            data["question"] = "What is a proposal?"
            data["description"] = "A priced offer."
            data["out_of_scope"] = ["How a proposal is stored."]
            data["gaps"] = [g for g in data["gaps"] if g["kind"] != "authoring"]
            return body.replace("## Answer\n", "## Answer\n\nA proposal is a priced offer.\n")

        self.edit(root, "definition/sales/proposal.md", enrich)
        result = self.check(root)
        self.assertEqual(0, result.returncode, result.stdout)

    def test_a_change_on_the_expansion_side_is_reported(self) -> None:
        _plan, root, _ = self.expand(self.model)
        self.edit(root, "definition/sales/proposal.md",
                  lambda data, body: data.__setitem__("ddd", "entity"))
        result = self.check(root)
        self.assertEqual(1, result.returncode)
        self.assertIn("`ddd` differs", result.stdout)

    def test_removing_a_domain_gap_is_reported(self) -> None:
        """Only whoever knows the domain closes one, and no pass of this pipeline may."""
        _plan, root, _ = self.expand(self.model)
        self.edit(root, "definition/sales/proposal.md",
                  lambda data, body: data.__setitem__(
                      "gaps", [g for g in data["gaps"] if g["kind"] != "domain"]))
        result = self.check(root)
        self.assertEqual(1, result.returncode)
        self.assertIn("kind: domain", result.stdout)

    def test_writing_a_field_without_closing_its_gap_is_reported(self) -> None:
        """Closing the gap is what records that the field was filled."""
        _plan, root, _ = self.expand(self.model)
        self.edit(root, "definition/sales/proposal.md",
                  lambda data, body: data.__setitem__("question", "What is a proposal?"))
        result = self.check(root)
        self.assertEqual(1, result.returncode)
        self.assertIn("is still open", result.stdout)

    def test_a_third_heading_is_reported(self) -> None:
        _plan, root, _ = self.expand(self.model)
        self.edit(root, "definition/sales/proposal.md",
                  lambda data, body: body + "\n## Rationale\n\nBecause.\n")
        result = self.check(root)
        self.assertEqual(1, result.returncode)
        self.assertIn("body headings changed", result.stdout)

    def test_an_object_the_expansion_never_wrote_is_reported(self) -> None:
        """The enrichment writes into the objects it was given and creates none."""
        _plan, root, _ = self.expand(self.model)
        stray = root / "definition" / "sales" / "invented.md"
        stray.write_text("---\nid: ko.definition.sales.invented\n---\n\n# Invented\n")
        result = self.check(root)
        self.assertEqual(1, result.returncode)
        self.assertIn("nothing in the model expands to it", result.stdout)

    def test_a_deleted_object_is_reported(self) -> None:
        _plan, root, _ = self.expand(self.model)
        (root / "rule" / "sales" / "proposal-expiration.md").unlink()
        result = self.check(root)
        self.assertEqual(1, result.returncode)
        self.assertIn("it is gone", result.stdout)

    def test_an_absent_tree_cannot_run(self) -> None:
        _plan, root, _ = self.expand(self.model)
        holder = root.parent
        (holder / "checked.json").write_text(json.dumps(self.model))
        result = subprocess.run(
            [sys.executable, "-B", str(self.CHECKER), str(holder / "checked.json"),
             "/definitely/not/here", "ki_4c1e7a90", *STAMP],
            capture_output=True, text=True,
        )
        self.assertEqual(2, result.returncode)
        self.assertIn("cannot run", result.stderr)




class Promotion(Run):
    """The boundary between staging and the base — §6.4 of the proposal.

    It is a contract change rather than a directory change: the staged contract does not require the
    three fields only judgment supplies and the base's does, so the move is where that difference is
    checked. Validating before writing is what makes the two contracts worth having.
    """

    PROMOTER = SHIPPED_ROOT / "bin" / "promote_staged.py"

    def promote(self, staging: Path, knowledge: Path, *flags: str):
        return subprocess.run(
            [sys.executable, "-B", str(self.PROMOTER), str(staging), str(knowledge), *flags],
            capture_output=True, text=True,
        )

    def answered(self) -> dict:
        """The model as it stands once the domain has answered every open parameter.

        Closing a `kind: domain` gap means *stating the fact*, not deleting the entry — the base
        refuses an attribute whose primitive parameter is missing whatever the gaps say, which is
        what gives such a gap teeth at this boundary. So the complete case is built by supplying the
        values and re-expanding, which is the path a consumer actually takes.
        """
        model = json.loads(json.dumps(self.model))
        attributes = model["definitions"][0]["attributes"]
        attributes[0]["max_length"] = 32
        attributes[3]["binding"] = "by-identity"
        model["definitions"][1]["attributes"][0]["max_length"] = 120
        # R7, restored: a rule declares `expression` or `examples`, and the worked example states
        # neither. Deleting the gap without supplying one is the same pretence as deleting an
        # attribute's gap without stating its length, and the contract catches both.
        model["rules"][0]["expression"] = "proposal.issued_at + validity_period < now"
        return model

    def enrich_all(self, root: Path, close_domain: bool = False) -> None:
        """Every object as the enrichment pass would leave it."""
        for path in sorted(root.rglob("*.md")):
            head, body = path.read_text().split("\n---\n", 1)
            data = yaml.safe_load(head[4:])
            data["question"] = f"What is {data['title']}?"
            data["description"] = f"{data['title']}, in one sentence."
            data["out_of_scope"] = ["What another object answers."]
            keep = [] if close_domain else [g for g in data.get("gaps", []) if g["kind"] == "domain"]
            if keep:
                data["gaps"] = keep
            else:
                data.pop("gaps", None)
            path.write_text("---\n" + yaml.safe_dump(data, sort_keys=False, allow_unicode=True)
                            + "---\n" + body)

    def test_an_unenriched_tree_is_refused_and_nothing_moves(self) -> None:
        _plan, staging, _ = self.expand(self.model)
        knowledge = staging.parent / "knowledge"
        result = self.promote(staging, knowledge)
        self.assertEqual(1, result.returncode)
        self.assertIn("nothing was promoted", result.stdout)
        self.assertFalse(knowledge.exists())
        self.assertTrue(list(staging.rglob("*.md")), "the staging tree is intact")

    def test_an_open_domain_gap_is_refused_by_default(self) -> None:
        """A gap the domain has not closed is a fact the base would be asserting it has."""
        _plan, staging, _ = self.expand(self.model)
        self.enrich_all(staging)
        result = self.promote(staging, staging.parent / "knowledge")
        self.assertEqual(1, result.returncode)
        self.assertIn("is open", result.stdout)
        self.assertIn("--with-open-domain-gaps", result.stdout)

    def test_it_promotes_when_the_caller_takes_the_decision(self) -> None:
        """The flag waives the *gap*, never the contract.

        So the case it covers is an object the base accepts while the domain still owes something:
        `identity` absent on an aggregate root, which the type's alternation excuses because the gap
        names it. An attribute missing the parameter its primitive requires is a different thing —
        the contract refuses it, and no flag here reaches that.
        """
        model = self.answered()
        del model["definitions"][0]["identity"]
        _plan, staging, _ = self.expand(model)
        self.enrich_all(staging)
        knowledge = staging.parent / "knowledge"
        result = self.promote(staging, knowledge, "--with-open-domain-gaps")
        self.assertEqual(0, result.returncode, result.stdout)
        self.assertIn("open domain gap", result.stdout, "the decision is recorded, not defaulted")
        self.assertTrue(list(knowledge.rglob("*.md")))

    def test_a_complete_tree_promotes_cleanly(self) -> None:
        _plan, staging, _ = self.expand(self.answered())
        self.enrich_all(staging, close_domain=True)
        knowledge = staging.parent / "knowledge"
        result = self.promote(staging, knowledge)
        self.assertEqual(0, result.returncode, result.stdout)
        for path in sorted(knowledge.rglob("*.md")):
            with self.subTest(object=path.name):
                self.assertEqual([], list(self.base.iter_errors(frontmatter(path))))

    def test_the_contract_line_is_rewritten_and_nothing_else_is(self) -> None:
        _plan, staging, _ = self.expand(self.answered())
        self.enrich_all(staging, close_domain=True)
        before = {p.relative_to(staging): p.read_text() for p in sorted(staging.rglob("*.md"))}
        knowledge = staging.parent / "knowledge"
        self.promote(staging, knowledge)
        for relative, text in before.items():
            with self.subTest(object=relative.name):
                self.assertEqual(
                    text.replace("staged-knowledge-object/2", "knowledge-object/5", 1),
                    (knowledge / relative).read_text(),
                )

    def test_the_staging_tree_is_emptied(self) -> None:
        _plan, staging, _ = self.expand(self.answered())
        self.enrich_all(staging, close_domain=True)
        self.promote(staging, staging.parent / "knowledge")
        self.assertEqual([], list(staging.rglob("*.md")))

    def test_one_refusal_stops_the_whole_run(self) -> None:
        """A partial promotion leaves edges resolving to whichever half the reader looked at."""
        _plan, staging, _ = self.expand(self.answered())
        self.enrich_all(staging, close_domain=True)
        broken = next(p for p in staging.rglob("*.md"))
        head, body = broken.read_text().split("\n---\n", 1)
        data = yaml.safe_load(head[4:])
        del data["question"]
        broken.write_text("---\n" + yaml.safe_dump(data, sort_keys=False) + "---\n" + body)
        knowledge = staging.parent / "knowledge"
        result = self.promote(staging, knowledge)
        self.assertEqual(1, result.returncode)
        self.assertFalse(knowledge.exists(), "no object moved while one was refused")

    def test_an_empty_staging_tree_cannot_run(self) -> None:
        holder = Path(tempfile.mkdtemp())
        (holder / "staging").mkdir()
        result = self.promote(holder / "staging", holder / "knowledge")
        self.assertEqual(2, result.returncode)
        self.assertIn("cannot run", result.stderr)




class TheGapFieldCheck(Run):
    """The check `docs/adr/0021-an-object-carries-its-own-gaps.md` recorded as owed.

    A gap excuses an object from a field its node type requires, so the excuse is only as good as
    the field name. The schema cannot check it — the requirement a gap excuses is a conditional
    elsewhere in the same document — and without this, `{kind: domain, field: colour}` excuses an
    object from declaring `attributes`.

    It found a defect the moment it ran, in this repository rather than in a consumer's: the gap
    alternation had been applied over the rule's `expression`-or-`examples` alternation and
    overwritten it, so `foundation/0003` R7 had stopped being enforced by the contract. The two
    alternations now nest, and `test_a_rule_short_of_both_is_still_refused` holds the restored rule.
    """

    CHECKER = SHIPPED_ROOT / "bin" / "check_gap_fields.py"

    def check(self, root: Path):
        return subprocess.run(
            [sys.executable, "-B", str(self.CHECKER), str(root)], capture_output=True, text=True)

    def with_gap(self, root: Path, gap: dict) -> None:
        path = root / "definition" / "sales" / "proposal.md"
        head, body = path.read_text().split("\n---\n", 1)
        data = yaml.safe_load(head[4:])
        data.setdefault("gaps", []).append(gap)
        path.write_text("---\n" + yaml.safe_dump(data, sort_keys=False, allow_unicode=True)
                        + "---\n" + body)

    def test_a_freshly_expanded_tree_passes(self) -> None:
        _plan, root, _ = self.expand(self.model)
        result = self.check(root)
        self.assertEqual(0, result.returncode, result.stdout)

    def test_a_gap_naming_a_field_the_type_does_not_require_is_reported(self) -> None:
        _plan, root, _ = self.expand(self.model)
        self.with_gap(root, {"kind": "domain", "field": "colour", "why": "nobody stated it"})
        result = self.check(root)
        self.assertEqual(1, result.returncode)
        self.assertIn("a definition does not\nrequire".replace("\n", " "), " ".join(result.stdout.split()))

    def test_a_parameter_of_an_attribute_the_object_lacks_is_reported(self) -> None:
        """`attributes[x].y` is nameable only where the object carries `x`."""
        _plan, root, _ = self.expand(self.model)
        self.with_gap(root, {"kind": "domain", "field": "attributes[nobody].max_length",
                             "why": "nobody stated it"})
        self.assertEqual(1, self.check(root).returncode)

    def test_a_gap_beside_the_fact_it_names_is_reported(self) -> None:
        """A gap records a fact that is missing; one beside the fact keeps an object out for nothing."""
        _plan, root, _ = self.expand(self.model)
        self.with_gap(root, {"kind": "domain", "field": "boundary", "why": "nobody stated it"})
        result = self.check(root)
        self.assertEqual(1, result.returncode)
        self.assertIn("which this object declares", result.stdout)

    def test_an_authoring_gap_outside_the_closed_set_is_reported(self) -> None:
        _plan, root, _ = self.expand(self.model)
        self.with_gap(root, {"kind": "authoring", "field": "aliases"})
        result = self.check(root)
        self.assertEqual(1, result.returncode)
        self.assertIn("no pass of this framework writes", result.stdout)

    def test_a_gap_on_either_side_of_a_nested_alternation_is_accepted(self) -> None:
        """A rule short of both `expression` and `examples` may name either as its gap."""
        _plan, root, _ = self.expand(self.model)
        path = root / "rule" / "sales" / "proposal-expiration.md"
        self.assertIn("expression", {g["field"] for g in frontmatter(path).get("gaps", [])},
                      "the expansion names one of the two the rule lacks")
        self.assertEqual(0, self.check(root).returncode)

    def test_a_rule_short_of_both_is_still_refused_without_a_gap(self) -> None:
        """R7, restored: the gap alternation had overwritten it, and nothing noticed until now."""
        rule = {
            "contract_version": "knowledge-object/5", "id": "ko.rule.sales.x", "type": "rule",
            "title": "X", "description": "d", "question": "q?", "boundary": "ko.boundary.sales",
            "ddd": "invariant", "origin": "stated", "statement": "A MUST b.",
            "generated": {"by": "a", "at": "2026-08-01T09:00:00Z"}, "out_of_scope": ["y"],
        }
        self.assertNotEqual([], list(self.base.iter_errors(rule)))
        self.assertEqual([], list(self.base.iter_errors(dict(rule, expression="a > b"))))
        self.assertEqual([], list(self.base.iter_errors(
            dict(rule, gaps=[{"kind": "domain", "field": "expression", "why": "no criterion"}]))))

    def test_an_empty_root_cannot_run(self) -> None:
        holder = Path(tempfile.mkdtemp())
        (holder / "empty").mkdir()
        result = self.check(holder / "empty")
        self.assertEqual(2, result.returncode)
        self.assertIn("cannot run", result.stderr)




class TheOneTypeThatCarriesNoDdd(Run):
    """A `lifecycle`, which the worked example does not hold — and that absence hid a live defect.

    The ontology maps a state machine to the node type itself rather than to a `ddd` value beside
    it, so `knowledge-object` rejects `ddd` on a lifecycle. `knowledge-intake-plan` required one of
    every classified entry until `/5`, which meant a classification had to invent a value the
    boundary would then refuse — the reference run recorded exactly that, `ddd: "lifecycle"`, in the
    producer's own notes as a conflict it could not resolve.

    Nothing here caught it because no test model held a lifecycle. This one does.
    """

    def with_lifecycle(self) -> dict:
        model = json.loads(json.dumps(self.model))
        model["lifecycles"] = [{
            "id": "dm.lifecycle.sales.proposal", "subject": "Proposal", "context": "Sales",
            "states": ["draft", "issued"], "initial": "draft",
            "transitions": [{"from": "draft", "trigger": "issue", "to": "issued"}],
            "origin": "stated",
        }]
        return model

    def test_the_entry_carries_no_ddd(self) -> None:
        plan, _root, _ = self.expand(self.with_lifecycle())
        entry = next(e for e in plan["entries"] if e.get("node_type") == "lifecycle")
        self.assertNotIn("ddd", entry)

    def test_the_plan_conforms_with_a_lifecycle_in_it(self) -> None:
        plan, _root, _ = self.expand(self.with_lifecycle())
        self.assertEqual([], list(self.plan_contract.iter_errors(plan)))

    def test_the_object_conforms_and_carries_no_ddd(self) -> None:
        _plan, root, _ = self.expand(self.with_lifecycle())
        data = frontmatter(root / "lifecycle" / "sales" / "proposal.md")
        self.assertNotIn("ddd", data)
        self.assertEqual([], list(self.staged.iter_errors(data)))

    def test_every_other_type_still_requires_one(self) -> None:
        """The conditional narrows to one node type and leaves the rest as they were."""
        plan, _root, _ = self.expand(self.with_lifecycle())
        for entry in plan["entries"]:
            if entry["outcome"] == "classified" and entry["node_type"] != "lifecycle":
                with self.subTest(construct=entry["construct"]):
                    self.assertIn("ddd", entry)

    def test_its_subject_and_states_survive_the_expansion(self) -> None:
        _plan, root, _ = self.expand(self.with_lifecycle())
        data = frontmatter(root / "lifecycle" / "sales" / "proposal.md")
        self.assertEqual("ko.definition.sales.proposal", data["subject"])
        self.assertEqual(["draft", "issued"], data["states"])
        self.assertIn("rejections", {gap["field"] for gap in data["gaps"]},
                      "totality is required and the model states no rejection")




class TheMaterializer(Run):
    """The derived files six shipped documents told a consumer never to hand-edit, and nothing wrote.

    A rule about a file that does not exist is a rule a reader cannot follow. `knowledge-graph/2` had
    no producer either, so a contract sat in the distribution describing an artifact nobody could
    make. Both are closed here.

    Everything asserted below is a property of a derivation rather than of a judgement: the graph is
    the objects' declared relationships and nothing inferred, the ordering is fixed so two runs
    agree byte for byte, and a defect is reported rather than repaired.
    """

    MATERIALIZER = SHIPPED_ROOT / "bin" / "materialize.py"
    PROMOTER = SHIPPED_ROOT / "bin" / "promote_staged.py"

    def promoted_base(self, model: dict | None = None) -> Path:
        """A promoted knowledge base, which is what this reads."""
        _plan, staging, _ = self.expand(model or self.complete_model())
        for path in sorted(staging.rglob("*.md")):
            head, body = path.read_text().split("\n---\n", 1)
            data = yaml.safe_load(head[4:])
            data["question"] = f"What is {data['title']}?"
            data["description"] = f"{data['title']}."
            data["out_of_scope"] = ["What another object answers."]
            data.pop("gaps", None)
            path.write_text("---\n" + yaml.safe_dump(data, sort_keys=False, allow_unicode=True)
                            + "---\n" + body)
        knowledge = staging.parent / "knowledge"
        subprocess.run([sys.executable, "-B", str(self.PROMOTER), str(staging), str(knowledge)],
                       capture_output=True, text=True, check=True)
        return knowledge

    def complete_model(self) -> dict:
        model = json.loads(json.dumps(self.model))
        model["definitions"][0]["attributes"][0]["max_length"] = 32
        model["definitions"][0]["attributes"][3]["binding"] = "by-identity"
        model["definitions"][1]["attributes"][0]["max_length"] = 120
        model["rules"][0]["expression"] = "issued_at + validity < now"
        return model

    def materialize(self, root: Path, *flags: str):
        return subprocess.run(
            [sys.executable, "-B", str(self.MATERIALIZER), str(root), *flags],
            capture_output=True, text=True)

    def test_it_writes_the_four_derived_files(self) -> None:
        root = self.promoted_base()
        result = self.materialize(root)
        self.assertEqual(0, result.returncode, result.stdout)
        for name in ("graph.json", "index.md", "glossary.md", "context-map.md"):
            with self.subTest(file=name):
                self.assertTrue((root / name).is_file())

    def test_the_graph_conforms_to_its_contract(self) -> None:
        root = self.promoted_base()
        self.materialize(root)
        contract = validator("knowledge-graph.json")
        self.assertEqual([], list(contract.iter_errors(json.loads((root / "graph.json").read_text()))))

    def test_every_edge_is_declared_and_none_inferred(self) -> None:
        """A relationship stated only in prose is not an edge: two readings give two graphs."""
        root = self.promoted_base()
        self.materialize(root)
        graph = json.loads((root / "graph.json").read_text())
        for edge in graph["edges"]:
            with self.subTest(edge=edge["locator"]):
                self.assertIn(edge["kind"], graph["edge_kinds"])
                source = next(p for p in root.rglob("*.md")
                              if p.name not in ("index.md", "glossary.md", "context-map.md")
                              and frontmatter(p).get("id") == edge["source"])
                self.assertIn(edge["target"], source.read_text())

    def test_two_runs_agree_byte_for_byte(self) -> None:
        root = self.promoted_base()
        self.materialize(root)
        first = {n: (root / n).read_text() for n in ("graph.json", "index.md", "glossary.md")}
        self.materialize(root)
        self.assertEqual(first, {n: (root / n).read_text() for n in first})

    def test_check_reports_a_stale_derived_file_and_writes_nothing(self) -> None:
        root = self.promoted_base()
        self.materialize(root)
        (root / "index.md").write_text("# Edited by hand\n")
        result = self.materialize(root, "--check")
        self.assertEqual(1, result.returncode)
        self.assertIn("index.md", result.stdout)
        self.assertEqual("# Edited by hand\n", (root / "index.md").read_text())

    def test_an_unresolvable_edge_is_reported_and_not_repaired(self) -> None:
        root = self.promoted_base()
        target = root / "definition" / "sales" / "proposal.md"
        head, body = target.read_text().split("\n---\n", 1)
        data = yaml.safe_load(head[4:])
        data["depends_on"] = ["ko.definition.sales.nobody"]
        target.write_text("---\n" + yaml.safe_dump(data, sort_keys=False) + "---\n" + body)
        result = self.materialize(root)
        self.assertEqual(1, result.returncode)
        self.assertIn("which the base does not hold", result.stdout)
        self.assertTrue((root / "graph.json").is_file(),
                        "the graph is still written, so a reader sees the shape the defect sits in")
        self.assertIn("ko.definition.sales.nobody", (root / "definition" / "sales" / "proposal.md").read_text())

    def test_the_glossary_is_the_set_of_definitions(self) -> None:
        """The ubiquitous language is where the ontology says it is, not a separate list."""
        root = self.promoted_base()
        self.materialize(root)
        glossary = (root / "glossary.md").read_text()
        self.assertIn("Proposal", glossary)
        self.assertIn("Customer", glossary)
        self.assertNotIn("Proposal expiration", glossary, "a rule is not a term")

    def test_a_derived_file_is_never_read_back_as_an_object(self) -> None:
        root = self.promoted_base()
        self.materialize(root)
        self.materialize(root)
        graph = json.loads((root / "graph.json").read_text())
        self.assertFalse([n for n in graph["nodes"] if "index" in n["id"] or "glossary" in n["id"]])

    def test_an_empty_base_cannot_run(self) -> None:
        holder = Path(tempfile.mkdtemp())
        (holder / "knowledge").mkdir()
        result = self.materialize(holder / "knowledge")
        self.assertEqual(2, result.returncode)
        self.assertIn("cannot run", result.stderr)


if __name__ == "__main__":
    unittest.main()
