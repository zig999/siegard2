// Generated from ko.lifecycle.sales.proposal by typescript-node 0.1.0.
// foundation/0004 R7: this file is not hand-edited. Change the knowledge object.

export const ProposalTransitions = [
  { from: "draft", trigger: "issue", to: "issued" },
  { from: "issued", trigger: "accept", to: "accepted" },
  { from: "issued", trigger: "expire", to: "expired" },
  { from: "draft", trigger: "cancel", to: "cancelled" },
  { from: "issued", trigger: "cancel", to: "cancelled" },
] as const;

export const ProposalRejections = [
  { from: "draft", trigger: "accept", error: "ko.definition.sales.proposal-not-issued" },
  { from: "draft", trigger: "expire", error: "ko.definition.sales.proposal-not-issued" },
  { from: "issued", trigger: "issue", error: "ko.definition.sales.proposal-already-issued" },
  { from: "terminal", trigger: "issue", error: "ko.definition.sales.proposal-terminal" },
  { from: "terminal", trigger: "accept", error: "ko.definition.sales.proposal-terminal" },
  { from: "terminal", trigger: "expire", error: "ko.definition.sales.proposal-terminal" },
  { from: "terminal", trigger: "cancel", error: "ko.definition.sales.proposal-terminal" },
] as const;
