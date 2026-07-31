// Generated from ko.definition.billing.invoice-not-issued by typescript-node 0.1.0.
// foundation/0004 R7: this file is not hand-edited. Change the knowledge object.

-- up
create table invoice_not_issued (
  invoice_number text not null
);

-- down
drop table invoice_not_issued;
