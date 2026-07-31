// Generated from ko.definition.billing.invoice by typescript-node 0.1.0.
// foundation/0004 R7: this file is not hand-edited. Change the knowledge object.

create table invoice (
  number text not null,
  contract_number text not null,
  amount numeric(19, 4) not null,
  state text not null
);
