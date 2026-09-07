# Backend conventions — domain-driven design and design patterns

An example of the optional input `/siegard-standard` takes: conventions in a project's own words,
named by path. Nothing here is a rule of the framework. A project adopts this by editing it into
its own words and handing the path to the skill; the skill transcribes what stands here into the
project's registry and writes nothing the document does not say.

Each convention states one condition a file can be held to, why it holds, and which half of a
registry it belongs in: **tool** where a linter, a type checker or an import-boundary check
decides it exactly — the project names the step that does — and **reading** where telling whether
it holds means understanding what the code means. Where a project's tree already configures a
tool for a convention marked reading, the tool wins.

## Layers, ports and adapters

1. Dependencies point inward: adapters depend on the application layer, the application layer on
   the domain, and the domain on neither. — A domain that imports an adapter cannot be tested or
   replaced apart from it. — **tool** (import-boundary check).
2. No two modules import each other, directly or through a chain. — A cycle makes every member
   change together. — **tool**.
3. Every external dependency — database, message broker, HTTP client, clock, identifier generator
   — is reached through an interface named in domain terms and implemented under the adapters
   directory. — The domain names what it needs; which technology answers is a detail it never
   sees. — **reading**.
4. An adapter translates and delegates; it holds no business conditional and no validation of a
   business rule. — A rule in an adapter is a rule the domain does not hold and the tests do not
   reach. — **reading**.
5. An application service loads aggregates, calls their behavior, persists, publishes events and
   authorizes; it holds no invariant. — An invariant in a service is enforced only on the paths
   that service takes. — **reading**.
6. An application service never calls another application service. — Shared behavior descends
   into the domain or ascends into an explicit process; a service calling a service hides a
   transaction boundary. — **tool** (import-boundary check).
7. A domain type appears in no controller or consumer signature and in no serialized response;
   the border carries its own types. — A domain type on the wire couples every client to the
   model's shape. — **tool** (type lint) or **reading** where no lint reaches it.

## The domain model

8. A domain class exposes no public setter; state changes only through methods named for the
   business operation (`confirm`, `cancel`), never `setStatus`. — A setter lets any caller put the
   aggregate into a state no rule admitted. — **tool** (lint on public setters) for the shape,
   **reading** for the names.
9. A domain object cannot exist in an invalid state: its constructor or factory refuses what an
   invariant forbids. — Failure at construction is one place; failure at use is everywhere. —
   **reading**.
10. A value object is immutable (`readonly`, frozen, or the stack's equivalent) and compares by
    value. — Two equal values are interchangeable, and a mutable one is not a value. — **tool**
    (type checker or lint).
11. A public domain signature uses a value object or an enumeration for a concept with a
    constraint — an email, a document number, money, a percentage, a period — never a bare
    primitive. — Every caller of a primitive re-learns what it means and what it admits. —
    **reading**.
12. The domain performs no I/O: no HTTP, SQL, queue, file system, system clock or environment
    read. What comes from outside arrives as a parameter or through a port. — A domain that reads
    the clock cannot be tested at a chosen instant. — **tool** (import-boundary and forbidden-API
    check).

## Persistence and reads

13. One repository per aggregate root, named for it, speaking in collection terms (`add`,
    `ofId`, `findBy<business criterion>`); no repository per table, and no query type of the
    persistence library crosses the repository interface. — A repository per table dissolves the
    consistency boundary the aggregate draws. — **reading**.
14. A listing, a report or a screen reads through a dedicated query path and never hydrates an
    aggregate to discard it. — Loading a boundary to read one column pays for every invariant it
    will not check. — **reading**.

## Failures

15. A business failure is a typed return value; an exception is for the unexpected and for a
    violated internal invariant. — A refusal thrown is a refusal no signature announces. —
    **reading**.
16. The mapping from business failure to transport status lives in one place, and its
    exhaustiveness is decided by the compiler. — A failure the mapping omits reaches the client as
    an accident. — **tool** (type checker).

## Design patterns

17. A class is named for its role in the domain, never for the pattern it implements —
    `PriceCalculator`, not `PricingStrategyImpl` — except where the pattern is the concept itself
    (`OrderRepository`, `EventPublisher`). — A pattern's name says how; a reader wants what. —
    **reading**.
18. An interface exists only with two implementations already in the tree, or one implementation
    and a test double that exercises the interface; one with neither is removed. — An abstraction
    over one thing is an indirection with a name. — **reading**.
19. A design pattern enters for a variation that already exists in the code, never for one
    imagined; the trigger and what the pattern costs are stated in the implementation record's
    inferences. — A pattern without a trigger is structure nobody can remove because nobody knows
    what it was for. — **reading**.
20. The same pattern is not applied uniformly across modules; a module whose context the
    specification classifies as supporting or generic may be a controller writing SQL. — Structure
    where no invariant lives is cost without a rule to pay for it. — **reading**; the registry
    scopes rules 1–16 to the directories of core contexts.

### Pattern triggers

What rule 19 holds a pattern to, per pattern: the variation that authorizes it, and the shape
that says it was applied without one. The reading that judges rule 19 reads this table; a pattern
absent from it is judged by the same question — what already varies, and what does the pattern
cost.

| pattern | trigger that authorizes it | sign of misuse |
|---|---|---|
| Factory / Factory Method | constructing the aggregate has an invariant or more than one step | a factory that only calls the constructor |
| Builder | an object with many valid combinations and partial construction | a builder for two required fields |
| Strategy / Policy | two or more variants **already present**, chosen at runtime | an interface with one implementation; an enumeration of one case |
| Specification | a selection or validation criterion reused in two or more places and testable alone | a wrapper over one `where` used once |
| Repository | one aggregate root with its own lifecycle | a repository per table; a generic repository leaking the ORM's query type |
| Unit of Work | one use case, one aggregate, one transaction | a unit of work committing several aggregates together |
| Ports & Adapters | an external dependency that is replaceable or must be stood in for under test | a port for code that will never have a second implementation nor a test |
| Domain Event | another aggregate or context reacts to the fact | an event nobody consumes |
| Transactional Outbox | a service writes and must publish from the same operation | an in-memory queue; a publish inside the transaction |
| Saga / Process | a business transaction spanning two or more aggregates or services, with compensation | a saga over a single aggregate |
| CQRS | reads and writes diverge in model or in load | the same model in two packages, called CQRS |
| Event Sourcing | history, audit or replay is a stated requirement | CRUD paying the operational cost of an event store |
| Anticorruption Layer | an external or legacy model that cannot be changed | a layer over the project's own context that was only a mapping |
| Decorator / Chain | cross-cutting behaviors composed at runtime | five layers for one log line |
| Observer / internal Pub-Sub | a reaction that is decoupled and optional | an essential coupling hidden behind an event, so the flow cannot be read |
| Singleton | a genuinely unique resource with no mutable state | mutable global state; a test that cannot isolate it |

## Tests

21. A domain test runs without a stand-in for any infrastructure; a domain test that needs one is
    reported against the domain, never repaired in the test. — The stand-in is the evidence that
    the domain reached outside. — **reading**.
22. Every adapter has one contract test against the real technology — a container or an instance
    — verifying the port it implements. — An adapter tested only against a stand-in is proven
    against nothing it will meet. — **reading**.
23. A use-case test runs with in-memory adapters and covers the authorization, the transaction
    boundary and the events published. — Those are the three things the use case owns. —
    **reading**.
24. Every invariant of an aggregate has a test that violates it and expects the refusal. — An
    invariant without a violating test is a sentence. — **reading**.

## Not this registry's — Architecture Constraints for `/analyse`

The standard's contract excludes any rule stating an integration or architecture strategy that
constrains the solution as a whole. The following are written into the specification as
Architecture Constraints with `scope: system`, and a step of the registry then names each one it
decides in `commands[].decides`, so the check runs with the suite and the constraint keeps one home.

- One transaction persists one aggregate; a rule that reaches across aggregates converges
  eventually through a domain event.
- Every aggregate root carries a version, and a write on a stale version is refused, never
  overwritten.
- No network call happens inside an open database transaction; the order is transaction, commit,
  then effect.
- An event published from a write is written to a transactional outbox in the same transaction,
  never published directly from the write path.
- Every message consumer and every command with an effect is idempotent under redelivery and
  reordering; a command carries a client-supplied idempotency key.
- A business transaction spanning aggregates or services is an explicit process with a named
  compensation for every step that produces an effect.
- Reads may bypass the domain through a dedicated query path.
- Separate read and write models exist only where a declared divergence in model, load or
  consumer justifies them; an event store exists only where history or replay is a stated
  requirement.
