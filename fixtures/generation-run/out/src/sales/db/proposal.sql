// Generated from ko.definition.sales.proposal by typescript-node 0.1.0.
// foundation/0004 R7: this file is not hand-edited. Change the knowledge object.

create table proposal (
  number text not null,
  issued_at timestamptz not null,
  total numeric(19, 4) not null,
  state text not null,
  customer uuid not null,
  items text[] not null
);
