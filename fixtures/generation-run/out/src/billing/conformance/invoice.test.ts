// Generated from ko.lifecycle.billing.invoice by typescript-node 0.1.0.
// foundation/0004 R7: this file is not hand-edited. Change the knowledge object.

describe("ko.lifecycle.billing.invoice", () => {
  it("rejects pay from draft", () => { expect(() => apply("draft", "pay")).toThrow("ko.definition.billing.invoice-not-issued"); });
  it("rejects issue from issued", () => { expect(() => apply("issued", "issue")).toThrow("ko.definition.billing.invoice-already-issued"); });
  it("rejects issue from terminal", () => { expect(() => apply("terminal", "issue")).toThrow("ko.definition.billing.invoice-terminal"); });
  it("rejects pay from terminal", () => { expect(() => apply("terminal", "pay")).toThrow("ko.definition.billing.invoice-terminal"); });
});

// declares: ko.lifecycle.billing.invoice
