# Full text

Derived by spec.py from the specification files; never edited. Grep here to locate;
open the node file a match names before claiming anything about it.

=== contracts/system/customer-registration
---
type: capability
---

## Description

The system registers customers and keeps each one's record.

=== domain/customers/_context
---
strategic: supporting
---

## Description

The context in which the business registers the people and companies it does business with and keeps each one's identifying record.
The material calls it "cadastro de clientes".

## Responsibility

Hold one record per customer, identified by its document, and say whether that customer is currently active.

=== domain/customers/_context.log
---
entries:
- field: strategic
  unstated: The material does not say whether customer registration is where the business differs, is merely specific to it, or is a solved problem.
  decided: supporting
  why: Registering a customer under a name and a document is specific to this business's documents and not where it competes.
---

=== domain/customers/customer
---
type: aggregate-root
attributes:
  - name: id
    type: customer-id
    required: true
  - name: name
    type: string
    required: true
  - name: document
    type: document
    required: true
  - name: email
    type: string
    required: false
  - name: status
    type: customer-status
    required: true
operations:
  - register
  - activate
  - deactivate
---

## Description

A person or company the business does business with, registered under a name and a document.
Its status says whether the customer is currently active.

## Responsibility

Be the one record the business holds for a customer.

=== domain/customers/customer-id
---
type: value-object
attributes:
  - name: value
    type: string
    required: true
---

## Description

The identity under which a customer is known, distinct from the customer's document.

## Responsibility

Tell one customer from another.

=== domain/customers/customer-id.log
---
entries:
- field: attributes.value.type
  unstated: The material names CustomerId and does not say what shape it takes.
  decided: string
  why: The material gives the identity no structure, and a string admits whatever form the implementation issues.
---

=== domain/customers/customer-status
---
type: enumeration
values:
  - active
  - inactive
---

## Description

The states a customer is seen in.

## Responsibility

Close the set of states a customer may hold.

=== domain/customers/customer.log
---
entries:
- field: attributes.id.required
  unstated: The material lists CustomerId among what a Customer has and does not say it is always present.
  decided: 'true'
  why: An aggregate root is addressed by its identity, so a customer without one cannot be referred to.
- field: attributes.name.type
  unstated: The material names Name and does not say what shape it takes.
  decided: string
  why: The material gives the name no structure of its own, so it is free text.
- field: attributes.name.required
  unstated: The material lists Name among what a Customer has and does not say it is always present.
  decided: 'true'
  why: The material marks only Email as optional, so the attributes it lists without that mark are always present.
- field: attributes.document.required
  unstated: The material lists Document among what a Customer has and does not say it is always present.
  decided: 'true'
  why: The material marks only Email as optional, and a uniqueness rule over the document presumes every customer holds one.
- field: attributes.email.type
  unstated: The material names Email and does not say what shape it takes.
  decided: string
  why: The material gives the email no structure of its own, so it is free text.
- field: attributes.status
  unstated: The material says a customer can be Active or Inactive and does not name the attribute that holds it or say it is always present.
  decided: status, of type customer-status, required
  why: A customer the material says is one of two states always holds exactly one of them.
- field: operations
  unstated: The material asks for customer registration and names two statuses but no operation on a customer.
  decided: register, activate, deactivate
  why: Registration is the act the material asks for, and a status with two values is left by one operation per direction.
---

=== domain/customers/document
---
type: value-object
attributes:
  - name: kind
    type: document-kind
    required: true
  - name: number
    type: string
    required: true
---

## Description

The official document a customer is identified by, which is a CPF for a person or a CNPJ for a company.

## Responsibility

Carry the one document a customer is registered under.

=== domain/customers/document-kind
---
type: enumeration
display: DocumentKind
values:
  - cpf
  - cnpj
---

## Description

The kinds of official document a customer may be registered under.

## Responsibility

Close the set of documents a customer may present.

=== domain/customers/document.log
---
entries:
- field: attributes
  unstated: The material says a Document accepts a CPF or a CNPJ and does not say what a Document holds.
  decided: kind, of type document-kind, required; number, of type string, required
  why: A CPF and a CNPJ are each a numbered document, so one value tells which kind and one carries the number.
---

=== rules/customers/customer-lifecycle
---
type: state-machine
statement: A customer moves between active and inactive only along the declared transitions.
subject: domain/customers/customer
status: domain/customers/customer-status
initial: active
transitions:
  - from: active
    trigger: deactivate
    to: inactive
  - from: inactive
    trigger: activate
    to: active
rejections:
  - from: active
    trigger: activate
  - from: inactive
    trigger: deactivate
---

## Description

Governs which status a customer holds when registered and how it changes afterwards.
It does not decide who may activate or deactivate a customer.

=== rules/customers/customer-lifecycle.log
---
entries:
- field: initial
  unstated: The material does not say which status a customer holds when registered.
  decided: active
  why: Registration is the act of bringing a customer into business, and inactive is the status a customer is later put in.
- field: transitions
  unstated: The material names Active and Inactive and does not say how a customer passes from one to the other.
  decided: active to inactive on deactivate; inactive to active on activate
  why: Neither status is stated as final, so each is left by one trigger named after the status it reaches.
- field: rejections
  unstated: The material does not say what activating an active customer or deactivating an inactive one does.
  decided: rejected in both cases
  why: A trigger reaching the status already held changes nothing the material gives a meaning to.
---

=== rules/customers/document-is-unique
---
type: policy
statement: A customer's document MUST be held by no other customer.
constrains:
  - domain/customers/customer
  - domain/customers/document
consistency: immediate
---

## Description

Governs the uniqueness of a document across every registered customer, whatever the customer's status.
It does not decide whether a document is well-formed.
