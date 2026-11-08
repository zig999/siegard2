# Where a behaviour lives, by kind of fact

Read before writing a rule, a contract's `answers` or a constraint. The order is fixed —
«A fact takes the first of these homes that holds it» (SPEC-003 §Rule): what an operation answers,
then a rule on the element, then a `policy` on the contract, then an architecture constraint; and
«The stack is never a node» (SPEC-003 §Rule). This table applies that order to the kinds of fact
that most often land in the wrong home. It decides nothing the specification does not.

| Kind of fact | How you recognise it | Home | Not here |
|---|---|---|---|
| What an operation answers | a status, an error value, a body, a header sent back | the api's `answers` | a rule, a constraint |
| Which refusal is answered first | "before any other refusal", "the first broken rule" | the order of the operation's `refusals` | a rule, a constraint |
| Who may do what | a right, a role, an owner, "only X may" | a rule — on the element, or a `policy` on the contract — and the refusal names it by `rule` | a `when` repeated per operation |
| A condition the surface alone refuses | an identity nothing is held at, a dependency unavailable, a request the operation cannot read | `when` in that operation's refusal, written once under an anchor where several operations share it | a constraint restating the `when` |
| The shape of an error | the members of the error body, how a reason and a message differ | the value object the answers name | a constraint |
| How a list is read | filters, sorting, paging, the count headers | the api's `answers`, or a `policy` on the contract for what the filters mean | a constraint per parameter |
| What an event carries | the envelope, the members, the type | the event contract's `payload` | a constraint |
| When an operation notifies | "a deletion notifies each removed version" | a `policy` on the contract | a constraint |
| How events are delivered | outbox, retry, retention, at-least-once | an architecture constraint | the event contract |
| How a status may change | lifecycle, transitions, what a status allows | the aggregate's `state-machine` and `invariant`s | a constraint |
| How a credential is checked | issuer, keys, signature, audience, expiry | an architecture constraint; the refusal it causes is in `answers` | the same condition in each operation's `when` |
| How long something may take | "within three seconds", a timeout, a deadline | an architecture constraint (timing) | a rule |
| How the processes behave while running | stop signals, exit status, readiness, configuration precedence | an architecture constraint, with its `fitness` | the standard |
| The stack | a language, a runtime version, a package, a tool, a command, an image, a test arrangement | the project's standard, which the person authors — the line is `outside` in the ledger | any node |

The order of an operation's refusals is its precedence — «that order is the operation's precedence
— never a rule's or a constraint's to state» (SPEC-003 §Contract) — so a rule or a constraint that
says which refusal comes first restates the list, and the list is what changes.
