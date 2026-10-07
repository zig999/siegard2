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
