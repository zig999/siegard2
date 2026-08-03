# Generated from ko.rule.billing.invoice-amount by typescript-node 0.1.0 (judged track).
# foundation/0004 R7: this file is not hand-edited. Change the knowledge object.
#
# Recorded rather than observed. foundation/0004 R3 puts this class on the judged track, which means an
# agent produces it — `validator-producer`. No agent ran here, exactly as no agent ran for the
# recorded results in fixtures/knowledge-change-loop/, and the fixture README says so. What this
# file makes testable is the half R3 actually specifies: a judged artifact is verified against a
# conformance suite generated from the knowledge base, and an artifact with no covering suite is
# not accepted output.
#
# Python rather than TypeScript for one reason: the conformance suite has to *execute* against it,
# and a TypeScript file in this repository would be checked by reading. foundation/0004 R5 forbids
# presenting a passing suite as byte identity, and it equally forbids presenting an unread file as
# a passing suite.


def check(given: dict) -> str:
    """Enforce ko.rule.billing.invoice-amount: invoice.amount == invoice.contract_total."""
    amount = given["invoice.amount"]
    contract_total = given["invoice.contract_total"]
    return "allowed" if amount == contract_total else "rejected"
