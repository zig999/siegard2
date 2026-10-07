# candidate-rich — the agent's return, verbatim (paths shortened)

**Start:** 2026-10-07T11:15:54-03:00 · **End:** 2026-10-07T11:20:08-03:00

**Commands that wrote to disk** (`ROOT` = `runs/candidate-rich/spec`): Write of `domain/customer-registry/_context.md`, `customer.md`, `customer-id.md`, `document.md`, `document-kind.md`, `customer-status.md`, `rules/customer-registry/document-is-unique.md`, `customer-lifecycle.md`; `spec.py --decide` over `_context` (1), `document-kind` (1), `customer-status` (1), `customer-id` (1), `document` (2), `customer` (7), `document-is-unique` (1), `customer-lifecycle` (4); `spec.py --project` (6 files); Edit `document-is-unique.md` (removed `expression`); `spec.py --project` again.

---

**What needs you.** Nothing stops. One review is owed, and one watch item has no deciding fact on disk, so no door is recommended:

- The review is `git diff` over ROOT — eight nodes and eight logs, all new, 18 decided fields of 56 declared. The two nodes the material barely described are `domain/customer-registry/customer` (7 of 19 fields decided) and `rules/customer-registry/customer-lifecycle` (4 of 15, a node the material does not name). Open those logs first.
- Watch item (not logged — no case both nodes decide differently): the material says "CPF/CNPJ deve ser único" with no qualification, and `document-is-unique` holds across every customer whatever its status, so an inactive customer's document still blocks a new registration under it. The material is silent on whether deactivation should free the document. Disagreeing is an ordinary change to that rule's `statement`.
- One finding kept out, for you to supply as material if it is a fact: the material asks for "cadastro de clientes" but states no boundary this context crosses and no promise to a named user, so no Contract was written — no command, no api, no capability. The uniqueness refusal therefore has no `answers` home yet.

**Nodes written** (created), each with how many declared fields this invocation decided, as `--shape --of` printed:
- `domain/customer-registry/_context` — 1 decided / 1 declared
- `domain/customer-registry/customer` — 7 decided / 19 declared
- `domain/customer-registry/customer-id` — 1 decided / 4 declared
- `domain/customer-registry/document` — 2 decided / 7 declared
- `domain/customer-registry/document-kind` — 1 decided / 3 declared (node the material does not name)
- `domain/customer-registry/customer-status` — 1 decided / 3 declared (node the material does not name)
- `rules/customer-registry/document-is-unique` — 1 decided / 4 declared
- `rules/customer-registry/customer-lifecycle` — 4 decided / 15 declared (node the material does not name)

**Impact set read:** none (empty root). For the cross-check, `--impact` over the two rules closed 6 nodes, one hop.

**Decisions logged:** `_context.strategic` → supporting; `document-kind.type` → enumeration (two named kinds and nothing else is a closed set); `customer-status.type` → enumeration; `customer-id.attributes.value.type` → string; `document.attributes.kind.type` → document-kind; `document.attributes.number.type` → string; `customer.attributes.name.type` → string; `.email.type` → string; `.status.type` → customer-status; `.id.required` → true; `.name.required` → true; `.document.required` → true; `customer.operations` → register, activate, deactivate; `document-is-unique.consistency` → immediate; `customer-lifecycle.type` → state-machine (two states on one aggregate with no transition stated leave every status change undecided); `.initial` → active; `.transitions` → active→inactive on deactivate, inactive→active on activate; `.rejections` → both self-transitions rejected.

**Shape:** fixed — `document-is-unique`'s `expression` outgrew its `statement` and was removed. Left standing — lifecycle statement 12w at the rule p90 with no scenario; two `why`s at the log p90 (29w, 26w), each one claim. Zero shared phrases, zero sibling-naming prose, zero unresolved names, zero multiply-decided fields.

**Watch items:** the one above. No contradiction, no overlap. **Ledger:** n/a.

**Breach disclaimer:** this invocation never read the target; the eight nodes' obligations may contradict delivered code.

**Candidates for /reconcile:** the eight nodes above.

**Validator:** `specification sound: 5 element(s), 2 rule(s) across 1 context(s); 18 decision(s) disclosed` · **--project:** 6 files incl. `state-customer-registry-customer.mmd`.

**Handoff:** `/plan-work — the project root: runs/candidate-rich — the scope: <SCOPE> — the target: <TARGET> — the slug: <INITIATIVE-SLUG>`. Stopped.
