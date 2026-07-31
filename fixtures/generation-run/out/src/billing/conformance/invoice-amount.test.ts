// Generated from ko.rule.billing.invoice-amount by typescript-node 0.1.0.
// specs/0004 R7: this file is not hand-edited. Change the knowledge object.

describe("ko.rule.billing.invoice-amount", () => {
  it("allowed when invoice.amount=1200.00, invoice.contract_total=1200.00", () => { expect(checkInvoiceAmount('invoice.amount: 1200.00, invoice.contract_total: 1200.00')).toBe("allowed"); });
  it("rejected when invoice.amount=1300.00, invoice.contract_total=1200.00", () => { expect(checkInvoiceAmount('invoice.amount: 1300.00, invoice.contract_total: 1200.00')).toBe("rejected"); });
});

// declares: ko.rule.billing.invoice-amount
