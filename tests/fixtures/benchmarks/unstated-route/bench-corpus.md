# Bench corpus for the unstated-fact route (decided-fact route)

Source: the 2026-08-14 measurement over the full siegardtest history — 37 blocking events, of
which 10 were the unstated species. The 6 distinct facts below are the ones that received human
decisions there; each carries the value the human actually chose, so a decider run can be scored
against ground truth. Case 7 is a planted contradiction: the correct return is `contradicted`,
never a decision. Cases 8–9 are the read-not-decide half: the fact is stated in the supplied
material, so the correct outcome is `stated` with no log entry.

Protocol: run `unstated-fact-decider` once per case against a fixture specification shaped like
the consumer's (the checkout-service fixture extended as each case needs), handing the fact
alone — never the task text in the "surfaced by" lines, which exists here only for the
scorer's context. Score: outcome correct; for `decided`, the value matches ground truth (cases
1, 4, 5, 6) or is coherent and disclosed (cases 2, 3, where the human's choice was a genuine
shape decision the model may reasonably differ on); the log entry names a resolvable location;
no second fact decided in passing.

## Case 1 — all refusals, or the first (ground truth: all)

Fact: whether a validation over a case reports every refusal it finds or stops at the first.
Human decision (siegardtest, Q1, 2026-08-05): a validation answers with all refusals.
Expected outcome: decided, matching.

## Case 2 — two non-conclusion outcomes over one fallback slot (shape decision)

Fact: how a case declares the resolution taken when no hypothesis is confirmed, given two
distinct non-conclusion outcomes exist.
Human decision (Q3): the case declares two fallbacks, and a rule chooses between them by what
the collection returned — a decision that changed the case's shape.
Expected outcome: decided, coherent and disclosed; matching is not required.

## Case 3 — window idempotency without a ticket reference (shape decision)

Fact: what the repeat-request key does when a diagnose call carries no ticket reference.
Human decision (812d016, 2026-08-10): idempotency by window applies only when a ticket
reference is given; a call with none always starts its own investigation.
Expected outcome: decided, coherent and disclosed; matching is not required.

## Case 4 — content hash derivation (ground truth: the whole file)

Fact: what a published case's content hash is computed over.
Human decision (Q4): the hash covers the whole file.
Expected outcome: decided, matching.

## Case 5 — citation comparison form (ground truth: exact name match)

Fact: how a citation's name is compared against the names a capability's output declares.
Human decision (Q5): exact comparison of names.
Expected outcome: decided, matching.

## Case 6 — requester origin (ground truth: the caller supplies it)

Fact: where a diagnose call's requester identity originates.
Human decision (812d016): the caller supplies it directly in the call's own payload; no
resolution inside the domain.
Expected outcome: decided, matching.

## Case 7 — planted contradiction (must not be decided)

Fact: that an invoice can be amended after issue.
Fixture: `rules/sales/invoice-immutable` states an issued invoice never changes.
Expected outcome: contradicted, naming the rule; any decision is a fail.

## Case 8 — stated in the material (must be read, not decided)

Fact: whether a role, not a person, may be a recipient.
Fixture: the intake material states "publishes as an operational role" for the glossary entry —
the siegardtest Q6 case, resolved there by reading ("leitura confirmada").
Expected outcome: stated, naming where; a log entry is a fail.

## Case 9 — stated in spec prose (promoted, not decided)

Fact: whether citations are by name or by identifier.
Fixture: a node's `## Description` prose states "citations are by name and never by
identifier"; no field states it.
Expected outcome: stated, with edits that give the fact an addressable home; a log entry is a
fail.

## Scoring summary

| case | expected outcome | value scored against |
|---|---|---|
| 1 | decided | all refusals |
| 2 | decided | coherence + disclosure only |
| 3 | decided | coherence + disclosure only |
| 4 | decided | whole file |
| 5 | decided | exact name match |
| 6 | decided | caller supplies |
| 7 | contradicted | no decision made |
| 8 | stated | no log entry |
| 9 | stated | addressable home gained, no log entry |

## Scoring note, 2026-10-07

Case 8 was written before SPEC-001 R13 gained its last sentence — «A fact the supplied material
states is read, not decided, and is recorded as read (R9)». The correct return for a fact found
under `intake/` now carries a log entry recorded as read: `found` beside `field` and `unstated`,
never `decided` and never `why`. Case 8 therefore scores `stated` with a read entry; a decided
entry is the fail. Case 9, found in a node's own prose, still carries no entry. The fixture for
every case is `tests/fixtures/spec-model` extended as the case needs, recorded under `cases/<n>/`;
the latest run is recorded under `iteration-1/<n>/` with its verbatim return and its score.

## Iteration 1 — 2026-10-07, Siegard 5.15.0 candidate, decider on `opus`

Nine fresh-context runs, one per case, each handed the four inputs the decider accepts and
nothing else; returns verbatim and scores under `iteration-1/<n>/`.

| case | expected | outcome | ground truth | tokens |
|---|---|---|---|---|
| 1 | decided | decided | matched (all refusals) | 45,369 |
| 2 | decided | decided | coherence only — different shape (an outcome enumeration) | 43,932 |
| 3 | decided | decided | coherence only — different value (refused, not own investigation) | 38,730 |
| 4 | decided | decided | matched (the whole payload) | 44,342 |
| 5 | decided | decided | matched (exact, case-sensitive); first run over a root short of a citation came back `contradicted`, both kept | 39,162 + 41,697 |
| 6 | decided | decided | **not matched** — credential, never the payload; the person had the caller supply it | 45,079 |
| 7 | contradicted | contradicted | named `rules/sales/invoice-immutable` | 36,015 |
| 8 | stated | stated | read entry over `attributes.recipient_role`, no decided value | 42,521 |
| 9 | stated | stated | promoted to an invariant, no entry | 41,378 |

Every outcome is the expected one, every decided fact landed as an entry `spec.py --decide`
accepted on a copy of its root, and no case decided a second fact. Of the four cases scored
against a person's value, three matched and case 6 did not: the decider chose the opposite of
what the person chose, coherently and disclosed. `tests/test_benchmarks.py` asserts what
SPEC-001 item 3 states — outcome class, resolvable entry, the stop over a contradiction — and
records agreement with a person's value without asserting it, because the requirement is that
the fact be decided and disclosed, not that it be decided as one person did.
