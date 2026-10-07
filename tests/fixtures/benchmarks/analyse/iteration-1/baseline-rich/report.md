# baseline-rich — the agent's return, verbatim (paths shortened)

**Start:** 2026-10-07T11:13:24-03:00 · **End:** 2026-10-07T11:16:54-03:00

**Commands that wrote to disk** (all under `runs/baseline-rich/spec/`): Write of `domain/customers/_context.md`, `customer.md`, `customer-id.md`, `document.md`, `document-kind.md`, `customer-status.md`, `rules/customers/customer-lifecycle.md`, `document-is-unique.md`, `contracts/system/customer-registration.md`; `spec.py --decide` over `_context` (strategic), `customer` ×7 (attributes.id.required, attributes.name.type, attributes.name.required, attributes.document.required, attributes.email.type, attributes.status, operations), `customer-id` (attributes.value.type), `document` (attributes), `customer-lifecycle` ×3 (initial, transitions, rejections); `spec.py --project`. No git write.

---

**What needs the person:** nothing blocks. The specification validated and its projections were derived. The review is `git diff` (20 untracked files) over the specification root; the one next step is `/plan-work`, below. Three decisions below are mine to a greater degree than the others and are the ones to read first: the state machine's triggers (`transitions`, `rejections`), the registered customer's initial status (`initial`), and the operations `register`, `activate`, `deactivate` — the material named two statuses and no trigger, so each of these is a value I chose and disclosed, not one I read.

**Nodes written** (empty root; all created): `domain/customers/_context`; `domain/customers/customer` (aggregate-root); `domain/customers/customer-id` (value-object); `domain/customers/document` (value-object); `domain/customers/document-kind` (enumeration: cpf, cnpj); `domain/customers/customer-status` (enumeration: active, inactive); `rules/customers/customer-lifecycle` (state-machine); `rules/customers/document-is-unique` (policy, immediate); `contracts/system/customer-registration` (capability). Not written, by judgment: no scenario, no command or api, no architecture constraint.

**Impact set read:** none — the root was empty.

**Decisions logged:** `_context.strategic` → supporting; `customer.attributes.id.required` → true; `customer.attributes.name.type` → string; `customer.attributes.name.required` → true; `customer.attributes.document.required` → true (only Email is optional, and uniqueness presumes every customer holds one); `customer.attributes.email.type` → string; `customer.attributes.status` → status of type customer-status, required; `customer.operations` → register, activate, deactivate; `customer-id.attributes.value.type` → string; `document.attributes` → kind (document-kind, required), number (string, required); `customer-lifecycle.initial` → active; `.transitions` → active→inactive on deactivate, inactive→active on activate; `.rejections` → both same-state cases rejected.

Facts read, not decided: Customer is the aggregate root; id, name, document, email; Document is a value object accepting CPF or CNPJ; email optional; two statuses; document unique.

**Shape:** lifecycle statement (12w) at the rule p90 with no scenario — left standing. Three `why`s at the log p90 (21w); `operations` carries two halves for one three-valued field — left standing. Everything else zero.

**Cross-check:** the two rules over `customer`; case: an inactive customer and a new registration with the same document — both refuse it; no contradiction, no overlap. **Watch items:** none. **Ledger:** n/a.

**Breach disclaimer:** this step never read the target; the required name and document, string identity, cpf/cnpj enumeration, initial active, same-state rejections and uniqueness across inactive customers may each contradict delivered code.

**Candidates for /reconcile:** the nine nodes above.

**Validator:** `specification sound: 5 element(s), 2 rule(s), 1 contract(s) across 1 context(s); 13 decision(s) disclosed` · **--project:** 6 files incl. `state-customers-customer.mmd`.

**Handoff:** `/plan-work — project root: runs/baseline-rich — scope: <…> — target: <…> — slug: <…>`. Stopped.
