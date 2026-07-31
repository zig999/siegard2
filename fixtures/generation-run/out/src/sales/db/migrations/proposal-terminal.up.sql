// Generated from ko.definition.sales.proposal-terminal by typescript-node 0.1.0.
// specs/0004 R7: this file is not hand-edited. Change the knowledge object.

-- up
create table proposal_terminal (
  proposal_number text not null,
  state text not null
);

-- down
drop table proposal_terminal;
