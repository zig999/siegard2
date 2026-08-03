// Generated from ko.definition.sales.proposal-expired by typescript-node 0.1.0.
// specs/0004 R7: this file is not hand-edited. Change the knowledge object.

-- up
create table proposal_expired (
  proposal_number text not null,
  expired_at timestamptz not null
);

-- down
drop table proposal_expired;
