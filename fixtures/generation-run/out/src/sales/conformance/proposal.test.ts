// Generated from ko.lifecycle.sales.proposal by typescript-node 0.1.0.
// foundation/0004 R7: this file is not hand-edited. Change the knowledge object.

describe("ko.lifecycle.sales.proposal", () => {
  it("rejects accept from draft", () => { expect(() => apply("draft", "accept")).toThrow("ko.definition.sales.proposal-not-issued"); });
  it("rejects expire from draft", () => { expect(() => apply("draft", "expire")).toThrow("ko.definition.sales.proposal-not-issued"); });
  it("rejects issue from issued", () => { expect(() => apply("issued", "issue")).toThrow("ko.definition.sales.proposal-already-issued"); });
  it("rejects issue from terminal", () => { expect(() => apply("terminal", "issue")).toThrow("ko.definition.sales.proposal-terminal"); });
  it("rejects accept from terminal", () => { expect(() => apply("terminal", "accept")).toThrow("ko.definition.sales.proposal-terminal"); });
  it("rejects expire from terminal", () => { expect(() => apply("terminal", "expire")).toThrow("ko.definition.sales.proposal-terminal"); });
  it("rejects cancel from terminal", () => { expect(() => apply("terminal", "cancel")).toThrow("ko.definition.sales.proposal-terminal"); });
});

// declares: ko.lifecycle.sales.proposal
