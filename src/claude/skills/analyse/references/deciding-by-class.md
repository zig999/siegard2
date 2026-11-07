# Deciding, class by class

Read during step 2 of `/analyse`, before the first node is decided. The schema says what each
class may declare; this is the judgment that decides what goes in it:

- **Language first.** The material's recurring nouns, with the meanings the material gives
  them, are the candidate Domain Model elements. A term whose meaning shifts between parts of
  the material is the strongest boundary signal you will get: two meanings, two contexts.
  «There is no alias mechanism» (SPEC-001 R3) in this model — where the material uses two words
  for one thing, the analysis picks the one that best carries the term as the element's name,
  and the other does not surface as a second entry. `display` exists only to correct a slug's
  derived PascalCase where it would miscase an acronym, never to record a synonym. A phrase you
  find yourself writing again in a second node is the same signal in reverse: name the thing it
  denotes and reference the name, because a definition restated is a definition kept in as many
  places as it appears. «Every specification is written in
  English (en-US), whatever language the material is in» (SPEC-001 R12) — every name this analysis
  writes is English: an
  identifier, a rule's `statement`, a scenario's `given`/`when`/`then`, a log entry —
  translate the term to its closest English equivalent before it becomes one of these. The
  material's own word may still appear in a `## Description`, where it helps a reader map the
  name back to the source; it is prose there, never the identity.
- **A context is a linguistic boundary.** Not a team, not a deployment unit, not a module. Draw
  one where the language changes or where somebody else's model gets translated at the edge.
  In a first pass, fewer and larger contexts beat many thin ones.
- **Identity decides an element's subtype.** Ask whether the domain cares *which one* it is or
  only *what it holds*. Most things a first pass calls entities are value objects: where two
  instances with equal attributes are interchangeable, the thing is replaced, not modified.
  An enumeration is a closed, named set of states or kinds; a service is a named behavior
  with no state of its own.
- **An aggregate is a consistency boundary, not an object graph.** Group only what must change
  together in one transaction; the default size is small. `composition` holds an entity inside
  its root's aggregate and never crosses it; `reference` is how an element points at another
  aggregate's root, always by identity, never by containment.
- **A set of conditions several rules decide is an enumeration they constrain.** Where you find
  yourself enumerating the same conditions inside a second `statement` — the readings a
  separately-issued read passes through, the ways a collection can end, the states a submission
  is seen in — that set is an element, and each rule then names its value rather than restating
  the list. `constrains` admits it: an enumeration a rule names is reachable by that naming
  alone, so this needs no field that does not exist. What it buys is not brevity. A rule stating
  a value of a declared set is a rule whose coverage of that set is visible; a rule restating the
  set in prose leaves the condition it forgot indistinguishable from the condition it decided to
  say nothing about, and there is no reading of prose that recovers the difference.
- **One rule, one falsifiable statement.** An invariant holds inside one aggregate,
  immediately. A policy may cross an aggregate or a context and must then declare
  `consistency` — `eventual`, because an immediate demand across a boundary is the boundary
  redrawn, not a rule. Where the material says what is observable before an eventual policy
  converges, that is a scenario anchored to the policy — never a field of it, and never
  invented where the material is silent. A state machine anchors to one aggregate root and its status
  enumeration; decide every transition and rejection so the pairing is total over every
  non-terminal state and every mentioned trigger. Where the material does not say what a
  trigger does in some state, that silence is exactly the kind of unstated fact this step
  exists to close: decide it — a transition or a rejection — and log it, never leave it for
  the validator's totality check to name as a defect. That check verifies the pairing is
  total; deciding it completely, so the check has something true to verify, is yours.
- **A scenario is one concrete case.** It anchors to exactly one Domain Model element, Rule, or
  Contract, with `given`/`when`/`then`. A rule the material illustrates with a worked example
  deserves one; a rule stated only in the abstract does not need an invented case to match it.
- **A contract is what crosses a boundary.** One kind records a fact that already happened,
  named in the past tense. A `command` requests something that may be refused — name the value
  object its refusal surfaces where the material states one. An `api` is a
  synchronous interface; where the material states what an operation answers — accepted or
  refused — that answer lands in the api's `answers`, and the condition a refusal answers stays
  the Rule's, named there by identity: «A Rule states the condition and never the answer»
  (SPEC-003 §Contract), so a status or an error value never enters a rule's statement. A
  `capability` is «a promise made at the system's boundary» (SPEC-003 §Contract) — this
  system's to its users, or a third party's this system consumes — and lives only under
  `contracts/system/`. `direction` (`published` | `consumed`) is required on the first
  three; a consumed contract names the published one it depends on, in another context, and «A
  third-party system is a `capability` named by what it supplies, never by the vendor»
  (SPEC-003 §Contract): the contract consuming it names that capability as its `upstream`. A consumed contract's payload says how the boundary is crossed: the upstream's
  own element adopts that model, an element of the consuming context translates it, and the
  context map reads the difference from the payload alone — declare it nowhere else.
- **An architecture constraint limits the solution, never the domain.** An integration
  strategy, a storage choice, an anti-corruption layer — state its `scope` (`system` or one
  context) and, where a mechanical check exists, its `fitness`.
- **What never enters the specification:** persistence, UI, stack, performance — implementation
  knowledge is not domain knowledge, whichever class would otherwise hold it. Of what an
  interface shows, «text that only names a control — a button, column, tab or menu label, an
  accessible name, a placeholder — and a client's tuning of its own requests — a cache lifetime, a
  retry count — are what the implementation chose and never a fact of the domain» (SPEC-005 R2);
  what changes what a person can learn or do is a fact. Nor a technical
  artifact — a DTO, a repository, a table, a topic: it emerges from implementation, and no
  class admits it.
- **The line is who chose the artifact, and there is one place it falls the other way.** The rule
  above holds because an artifact this system's own implementation picked is a decision the
  implementation is free to unpick, so a node stating it would freeze a choice the business never
  made. An artifact an **upstream** system imposes is not that: the object a consumed api is read
  from, the column a value is carried in, the coded values that column holds, the topic a
  subscribed event arrives on. Nothing downstream chose those and nothing downstream can change
  them — they are what the outside world is, and they are as much a fact about it as the payload
  of an event. So «a Contract whose `direction` is `consumed` may name them, and only such a
  contract may» (SPEC-003 §Contract): it is the class whose whole subject is a boundary this system does not own.
  Leaving them out does not keep them out of the system — it sends them into the code as facts no
  node holds, which is the finding a conformance pass reports as the most expensive one there is,
  and which is then discovered file by file forever. A published surface is the opposite case and
  keeps the rule: this system chose its own route, its own column, its own table, and those stay
  out. What its operations answer is the one thing it chose that does not:
  «An answer is what a caller of the boundary reads, so it is the Contract's, published or
  consumed» (SPEC-003 §Contract), and it lands in `answers` — never in a rule, and never in a
  constraint per operation. That includes what the operation answers when it cannot be carried
  out at all — «A failure answer is an answer» (SPEC-003 §Contract): the internal failure and the
  unavailable dependency the material shows the caller receiving are answers under `when`, and
  leaving them out sends them into the code as facts no node holds.
