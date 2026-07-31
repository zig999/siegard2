// Generated from ko.rule.sales.proposal-expiration by typescript-node 0.1.0.
// foundation/0004 R7: this file is not hand-edited. Change the knowledge object.

describe("ko.rule.sales.proposal-expiration", () => {
  it("allowed when proposal.issued_at=2026-07-01T09:00:00Z", () => { expect(checkProposalExpiration('proposal.issued_at: 2026-07-01T09:00:00Z')).toBe("allowed"); });
  it("rejected when proposal.issued_at=2026-07-01T09:00:00Z", () => { expect(checkProposalExpiration('proposal.issued_at: 2026-07-01T09:00:00Z')).toBe("rejected"); });
});

// declares: ko.rule.sales.proposal-expiration
