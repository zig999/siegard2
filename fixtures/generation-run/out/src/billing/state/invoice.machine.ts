// Generated from ko.lifecycle.billing.invoice by typescript-node 0.1.0.
// foundation/0004 R7: this file is not hand-edited. Change the knowledge object.

export const InvoiceTransitions = [
  { from: "draft", trigger: "issue", to: "issued" },
  { from: "issued", trigger: "pay", to: "paid" },
] as const;

export const InvoiceRejections = [
  { from: "draft", trigger: "pay", error: "ko.definition.billing.invoice-not-issued" },
  { from: "issued", trigger: "issue", error: "ko.definition.billing.invoice-already-issued" },
  { from: "terminal", trigger: "issue", error: "ko.definition.billing.invoice-terminal" },
  { from: "terminal", trigger: "pay", error: "ko.definition.billing.invoice-terminal" },
] as const;
