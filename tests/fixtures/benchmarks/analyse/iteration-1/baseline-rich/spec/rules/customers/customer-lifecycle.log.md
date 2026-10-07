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
