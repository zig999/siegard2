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
