# Full text

Derived by spec.py from the specification files; never edited. Grep here to locate;
open the node file a match names before claiming anything about it.

=== domain/customer-registry/_context
---
strategic: supporting
---

## Description

The context in which the business records who its customers are — the material's "cadastro de clientes".
It holds the customer, the identity that names one, the fiscal document that distinguishes one, and the two states a customer is seen in.

## Responsibility

Hold one record per customer and keep each customer distinguishable by its fiscal document.

=== domain/customer-registry/_context.log
---
entries:
- field: strategic
  unstated: The material does not say whether customer registration is where the business differs or merely something it needs.
  decided: supporting
  why: Registering who a customer is supports the business's trade without being what it competes on, and the material names nothing a customer record decides beyond who the customer is.
---

=== domain/customer-registry/customer
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

A party the business has registered as a customer.
It is named, carries one fiscal document, may carry an email, and is at any time in one of the states customer-status declares.
What a document may be is document's to decide, and which status changes are allowed is the customer lifecycle rule's.

## Responsibility

Be the one record of a customer, under which its name, document, email and status change together.

=== domain/customer-registry/customer-id
---
type: value-object
attributes:
  - name: value
    type: string
    required: true
---

## Description

The identity under which one customer is held.

## Responsibility

Name exactly one customer.

=== domain/customer-registry/customer-id.log
---
entries:
- field: attributes.value.type
  unstated: The material names CustomerId and gives it no shape.
  decided: string
  why: No format for a customer identity is stated, so a textual value holds whatever the implementation assigns.
---

=== domain/customer-registry/customer-status
---
type: enumeration
values:
  - active
  - inactive
---

## Description

The states a customer is seen in.

## Responsibility

Close the set of states a customer may be in.

=== domain/customer-registry/customer-status.log
---
entries:
- field: type
  unstated: The material says customers can be Active or Inactive and names no element that holds those states.
  decided: enumeration
  why: Two named states and nothing else is a closed set, which only an enumeration declares.
---

=== domain/customer-registry/customer.log
---
entries:
- field: attributes.name.type
  unstated: The material names Name and gives it no shape.
  decided: string
  why: Nothing in the material structures a name beyond text.
- field: attributes.email.type
  unstated: The material names Email as optional and gives it no shape.
  decided: string
  why: The material states no form an email must take, so it is held as text without a value object of its own.
- field: attributes.status.type
  unstated: The material says a customer can be Active or Inactive and names no attribute that holds the state.
  decided: customer-status
  why: A state a customer is seen in has to be held on the customer, and the two named states are a closed set.
- field: attributes.id.required
  unstated: The material lists CustomerId among what a Customer has without saying it must be present.
  decided: 'true'
  why: A customer with no identity is a customer nothing can hold, and the material calls only Email optional.
- field: attributes.name.required
  unstated: The material lists Name among what a Customer has without saying it must be present.
  decided: 'true'
  why: Calling only Email optional in a list of four attributes reads the other three as always present.
- field: attributes.document.required
  unstated: The material lists Document among what a Customer has without saying it must be present.
  decided: 'true'
  why: The uniqueness the material demands of the CPF/CNPJ presupposes every customer holds one, and the material calls only Email optional.
- field: operations
  unstated: The material names no operation on a customer.
  decided: register, activate, deactivate
  why: The material asks for customer registration and names two states, which call for one registering operation and one trigger into each state.
---

=== domain/customer-registry/document
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

The fiscal document a customer is registered under, either a CPF or a CNPJ.
Two documents of the same kind and number are the same document.

## Responsibility

Carry the one fiscal identification by which a customer is told apart from every other.

=== domain/customer-registry/document-kind
---
type: enumeration
values:
  - cpf
  - cnpj
---

## Description

The kinds of fiscal document a customer may be registered under.

## Responsibility

Close the set of document kinds a document accepts.

=== domain/customer-registry/document-kind.log
---
entries:
- field: type
  unstated: The material names CPF and CNPJ as what a Document accepts and names no element that holds those kinds.
  decided: enumeration
  why: Two named kinds a document accepts and nothing else is a closed set, which only an enumeration declares.
---

=== domain/customer-registry/document.log
---
entries:
- field: attributes.kind.type
  unstated: The material says a Document accepts CPF or CNPJ and does not say how a document records which of the two it is.
  decided: document-kind
  why: A document that accepts one of two kinds has to say which kind it holds, and the two kinds are a closed set.
- field: attributes.number.type
  unstated: The material does not say what a document holds beyond being a CPF or a CNPJ.
  decided: string
  why: A CPF and a CNPJ are each a sequence of digits, which text carries without choosing a numeric form.
---

=== rules/customer-registry/customer-lifecycle
---
type: state-machine
statement: A customer moves between active and inactive only along the declared transitions.
subject: domain/customer-registry/customer
status: domain/customer-registry/customer-status
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

A customer is active when registered, is deactivated into inactive, and is activated back into active.
Neither state is final, and a trigger that would leave a customer in the state it already holds is rejected.

=== rules/customer-registry/customer-lifecycle.log
---
entries:
- field: type
  unstated: The material names two states a customer can be in and names no rule governing how a customer moves between them.
  decided: state-machine
  why: Two states on one aggregate with no transition stated leave every status change undecided, and a state machine is the one class that decides them totally.
- field: initial
  unstated: The material does not say which state a customer is in when registered.
  decided: active
  why: A customer registered is a customer the business is trading with, and nothing in the material registers one already inactive.
- field: transitions
  unstated: The material names no trigger that moves a customer between active and inactive.
  decided: active moves to inactive on deactivate, and inactive moves to active on activate
  why: Neither state is named final, so each state leaves by one trigger into the other and no third trigger is needed.
- field: rejections
  unstated: The material does not say what happens when a customer is activated while active or deactivated while inactive.
  decided: both are rejected
  why: A trigger that would leave the customer in the state it already holds changes nothing, and rejecting it keeps every pairing decided.
---

=== rules/customer-registry/document-is-unique
---
type: policy
statement: No two customers hold the same document.
constrains:
  - domain/customer-registry/customer
consistency: immediate
---

## Description

The material's "CPF/CNPJ deve ser único": one fiscal document registers at most one customer.
It holds across every customer, whatever the customer's status, and it says nothing about what a surface answers when a second registration is refused.

=== rules/customer-registry/document-is-unique.log
---
entries:
- field: consistency
  unstated: The material says the CPF/CNPJ must be unique and does not say whether a duplicate is refused at once or resolved later.
  decided: immediate
  why: A must-be-unique with no window stated is a condition that is never allowed to hold false, which only an immediate check gives.
---
