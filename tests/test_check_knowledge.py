"""The checks a per-file schema cannot express, over a base built here rather than expanded.

Three of them were declared owed and unshipped for as long as the ingestion procedure existed:
a lifecycle's transition table is total, no two lifecycles claim one subject, and a reference
crossing a bounded context targets an interface. Each needs to see more than one object, which is
why no boundary validator could ever have carried them.

The base below is written by hand, and that is a change from how this suite used to work. While a
deterministic script expanded a domain model, the input was the model — this repository keeps no
fixtures, and a tree invented here would have been one. There is no expansion now: the analysis
writes by judgment, so a test cannot run it and compare bytes. What is left to assert is the
*checker*, and a checker is asserted against inputs chosen to make it fire.

So every rejection below is paired with the base that passes. A rejection test alone cannot tell a
working check from one that rejects everything.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from . import SHIPPED_ROOT

CHECKER = SHIPPED_ROOT / "bin" / "check_knowledge.py"

ENVELOPE = """contract_version: domain-object/1
generated: {{ by: domain-modeler, at: 2026-08-02T10:00:00Z }}
origin: stated
gaps:
  - {{ kind: authoring, field: question }}
  - {{ kind: authoring, field: description }}
  - {{ kind: authoring, field: out_of_scope }}"""

BASE = {
    "subdomain/sales.md": ("""id: dm.subdomain.sales
type: subdomain
title: Sales
subdomain_type: core""", "Responsibilities"),
    "context/sales.md": ("""id: dm.context.sales
type: context
title: Sales
subdomain: dm.subdomain.sales""", "Responsibilities"),
    "aggregate/sales/proposal.md": ("""id: dm.aggregate.sales.proposal
type: aggregate
title: Proposal
boundary: dm.context.sales
root: dm.definition.sales.proposal""", "Invariants"),
    "definition/sales/proposal.md": ("""id: dm.definition.sales.proposal
type: definition
title: Proposal
boundary: dm.aggregate.sales.proposal
ddd: aggregate-root
attributes:
  - {{ name: number, type: string, max_length: 30, required: true }}
identity:
  attributes:
    - number""", "Invariants"),
    "definition/sales/already-issued.md": ("""id: dm.definition.sales.already-issued
type: definition
title: Already issued
boundary: dm.context.sales
ddd: domain-error
attributes: []""", "Invariants"),
    "lifecycle/sales/proposal.md": ("""id: dm.lifecycle.sales.proposal
type: lifecycle
title: Proposal lifecycle
boundary: dm.context.sales
subject: dm.definition.sales.proposal
states:
  - draft
  - issued
initial: draft
terminal:
  - issued
transitions:
  - {{ from: draft, trigger: issue, to: issued }}
rejections:
  - {{ from: issued, trigger: issue, error: dm.definition.sales.already-issued }}""",
                                     "State semantics"),
}


class Case(unittest.TestCase):
    """A base written fresh per test, so a mutation never leaks into the next one."""

    def setUp(self) -> None:
        self.root = Path(tempfile.mkdtemp()) / "knowledge"
        for relative, (front, section) in BASE.items():
            self.write(relative, front, section)

    def write(self, relative: str, front: str, section: str) -> None:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            "---\n" + front.format() + "\n" + ENVELOPE.format() + "\n---\n\n"
            + f"# Object\n\n## Answer\n\n## {section}\n"
        )

    def edit(self, relative: str, old: str, new: str) -> None:
        path = self.root / relative
        text = path.read_text()
        self.assertIn(old, text, f"{relative} no longer holds the text this test mutates")
        path.write_text(text.replace(old, new, 1))

    def check(self):
        return subprocess.run([sys.executable, "-B", str(CHECKER), str(self.root)],
                              capture_output=True, text=True)

    def assertClean(self) -> None:
        result = self.check()
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def assertReports(self, phrase: str) -> None:
        result = self.check()
        self.assertEqual(1, result.returncode, "the check passed something it should refuse")
        self.assertIn(phrase, result.stdout)


class TheBaseItself(Case):
    def test_it_passes(self) -> None:
        """Paired with every rejection below: a check that refuses everything proves nothing."""
        self.assertClean()

    def test_the_derived_files_are_not_objects(self) -> None:
        """A reader who has just materialized would otherwise be told the index is malformed."""
        for derived in ("index.md", "glossary.md", "context-map.md"):
            (self.root / derived).write_text("# Derived\n\nNo frontmatter here.\n")
        (self.root / "system.md").write_text("---\ncontract_version: knowledge-system/1\n---\n\n# S\n")
        self.assertClean()


class LifecycleTotality(Case):
    """`foundation/0003` R8. An incomplete table is where behaviour is invented silently."""

    def test_an_undecided_pairing_is_reported(self) -> None:
        self.edit("lifecycle/sales/proposal.md", "from: issued, trigger: issue",
                  "from: draft, trigger: cancel")
        self.assertReports("the transition table is not total")

    def test_the_report_names_the_pairings(self) -> None:
        self.edit("lifecycle/sales/proposal.md", "from: issued, trigger: issue",
                  "from: draft, trigger: cancel")
        self.assertReports("issued + issue")

    def test_a_terminal_state_is_checked_like_any_other(self) -> None:
        """Having no outgoing transition is a different statement from having no decision."""
        self.edit("lifecycle/sales/proposal.md",
                  "rejections:\n  - { from: issued, trigger: issue, error: dm.definition.sales.already-issued }",
                  "rejections:\n  - { from: draft, trigger: issue, error: dm.definition.sales.already-issued }")
        self.assertReports("issued + issue")

    def test_the_terminal_shorthand_expands(self) -> None:
        """`from: terminal` stands for every terminal state, and reading it literally would refuse
        a table that is total and written economically."""
        self.edit("lifecycle/sales/proposal.md", "from: issued, trigger: issue",
                  "from: terminal, trigger: issue")
        self.assertClean()

    def test_a_trigger_list_expands(self) -> None:
        self.edit("lifecycle/sales/proposal.md",
                  "transitions:\n  - { from: draft, trigger: issue, to: issued }",
                  "transitions:\n  - { from: draft, trigger: issue, to: issued }\n"
                  "  - { from: draft, trigger: revise, to: draft }")
        self.assertReports("issued + revise")
        self.edit("lifecycle/sales/proposal.md", "trigger: issue, error:",
                  "trigger: [issue, revise], error:")
        self.assertClean()


class OneLifecyclePerSubject(Case):
    """A definition with two state machines has no single state set to generate from."""

    def second(self) -> None:
        front, section = BASE["lifecycle/sales/proposal.md"]
        self.write("lifecycle/sales/proposal-again.md",
                   front.replace("dm.lifecycle.sales.proposal", "dm.lifecycle.sales.proposal-again")
                        .replace("title: Proposal lifecycle", "title: Proposal lifecycle again"),
                   section)

    def test_two_claims_on_one_subject_are_reported(self) -> None:
        self.second()
        self.assertReports("is claimed by 2 lifecycles")

    def test_both_are_named_and_neither_is_chosen(self) -> None:
        self.second()
        result = self.check()
        self.assertIn("dm.lifecycle.sales.proposal,", result.stdout)
        self.assertIn("dm.lifecycle.sales.proposal-again", result.stdout)


class CrossingABoundary(Case):
    """`foundation/0003` R12. What crosses a context is a published contract, never an internal."""

    def other_context(self) -> None:
        self.write("context/billing.md", """id: dm.context.billing
type: context
title: Billing
subdomain: dm.subdomain.sales""", "Responsibilities")
        self.write("definition/billing/invoice.md", """id: dm.definition.billing.invoice
type: definition
title: Invoice
boundary: dm.context.billing
ddd: entity
attributes: []
identity:
  attributes:
    - number""", "Invariants")

    def test_a_reference_into_another_context_is_reported(self) -> None:
        self.other_context()
        self.edit("definition/sales/proposal.md", "boundary: dm.aggregate.sales.proposal",
                  "boundary: dm.aggregate.sales.proposal\ndepends_on:\n  - dm.definition.billing.invoice")
        self.assertReports("sits in another")

    def test_the_report_names_where_the_reference_sits(self) -> None:
        self.other_context()
        self.edit("definition/sales/proposal.md", "boundary: dm.aggregate.sales.proposal",
                  "boundary: dm.aggregate.sales.proposal\ndepends_on:\n  - dm.definition.billing.invoice")
        self.assertReports("depends_on[0]")

    def test_an_interface_may_be_crossed_to(self) -> None:
        self.other_context()
        self.write("interface/billing/invoice-issued.md", """id: dm.interface.billing.invoice-issued
type: interface
title: Invoice issued
boundary: dm.context.billing
ddd: integration-event
version: "1"
schema: events/invoice-issued.json
ownership: published""", "Semantics")
        self.edit("definition/sales/proposal.md", "boundary: dm.aggregate.sales.proposal",
                  "boundary: dm.aggregate.sales.proposal\ndepends_on:\n"
                  "  - dm.interface.billing.invoice-issued")
        self.assertClean()

    def test_a_reference_inside_one_context_is_untouched(self) -> None:
        """Through an aggregate to its context: the scope chain is followed, not the id compared."""
        self.edit("definition/sales/proposal.md", "boundary: dm.aggregate.sales.proposal",
                  "boundary: dm.aggregate.sales.proposal\ndepends_on:\n"
                  "  - dm.definition.sales.already-issued")
        self.assertClean()


class TheSealHandlesWhatYamlTypes(Case):
    """A timestamp written unquoted parses as a datetime, and JSON does not serialize one.

    Found by running the pair over a base written the way an analysis writes it rather than the way
    a test quotes it. Every object carries `generated.at`, so the seal failed on the first one — and
    no assertion caught it, because the trees the tests built had quoted the value.
    """

    SEALER = SHIPPED_ROOT / "bin" / "seal_analysis.py"
    OWNERSHIP = SHIPPED_ROOT / "bin" / "check_field_ownership.py"

    def seal(self):
        return subprocess.run(
            [sys.executable, "-B", str(self.SEALER), str(self.root), str(self.root.parent / "seal.json")],
            capture_output=True, text=True)

    def test_a_base_with_unquoted_timestamps_seals(self) -> None:
        self.assertIn("generated: { by: domain-modeler, at: 2026-08-02T10:00:00Z }",
                      (self.root / "context/sales.md").read_text(),
                      "the fixture must carry the unquoted form this exists for")
        result = self.seal()
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_the_ownership_check_reads_what_the_seal_wrote(self) -> None:
        self.assertEqual(0, self.seal().returncode)
        result = subprocess.run(
            [sys.executable, "-B", str(self.OWNERSHIP), str(self.root.parent / "seal.json"), str(self.root)],
            capture_output=True, text=True)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
