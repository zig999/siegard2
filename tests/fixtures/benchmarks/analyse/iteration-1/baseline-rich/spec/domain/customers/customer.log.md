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
