# Full text

Derived by spec.py from the specification files; never edited. Grep here to locate;
open the node file a match names before claiming anything about it.

=== constraints/asynchronous-events
---
statement: Events between contexts travel asynchronously; no context calls another synchronously to publish a fact.
scope: system
---

## Description

Publication is decoupled from consumption across every context pair.

=== contracts/monitoring/alert-raised
---
type: domain-event
direction: published
payload: domain/monitoring/alert
---

## Description

Monitoring tells the world an anomaly was detected.

=== contracts/system/troubleshoot-customer-problem
---
type: capability
---

## Description

The system's promise: a submitted customer problem gets diagnosed and resolved.

=== contracts/troubleshooting/alert-raised
---
type: domain-event
direction: consumed
upstream: contracts/monitoring/alert-raised
payload: domain/monitoring/alert
---

## Description

Troubleshooting depends on monitoring's published alert event.

=== contracts/troubleshooting/case-resolved
---
type: domain-event
direction: published
payload: domain/troubleshooting/case
---

## Description

Troubleshooting tells the world a case was resolved.

=== domain/monitoring/_context
---
strategic: supporting
---

## Description

Watching customer systems and raising alerts.

## Responsibility

Own the language of alerts and their sources.

=== domain/monitoring/alert
---
type: aggregate-root
attributes:
  - name: id
    type: string
    required: true
  - name: raised_at
    type: datetime
    required: true
---

## Description

One anomaly detected on a watched system.

## Responsibility

Carry what was detected until somebody acts on it.

=== domain/troubleshooting/_context
---
strategic: core
---

## Description

Diagnosing customer problems from submission to resolution.

## Responsibility

Own the language of cases, investigations and evidence.

=== domain/troubleshooting/case
---
type: aggregate-root
attributes:
  - name: id
    type: case-id
    required: true
  - name: status
    type: case-status
    required: true
  - name: opened_at
    type: datetime
    required: true
  - name: resolved_at
    type: datetime
relationships:
  - target: investigation
    type: composition
    cardinality: "1"
  - target: resolution
    type: composition
    cardinality: "0..1"
operations:
  - open
  - start-investigation
  - resolve
  - cancel
---

## Description

A customer problem submitted to the troubleshooting process.

## Responsibility

Control the investigation from opening to resolution or cancellation.

=== domain/troubleshooting/case-id
---
type: value-object
attributes:
  - name: value
    type: string
    required: true
---

## Description

The unique identifier of a case.

## Responsibility

None.

=== domain/troubleshooting/case-status
---
type: enumeration
values:
  - open
  - investigating
  - resolved
  - cancelled
---

## Description

The states a case passes through.

## Responsibility

None.

=== domain/troubleshooting/diagnostics
---
type: domain-service
operations:
  - correlate-evidence
---

## Description

Correlation of evidence across hypotheses of one case.

## Responsibility

Decide which hypothesis the collected evidence supports.

=== domain/troubleshooting/evidence
---
type: value-object
attributes:
  - name: kind
    type: evidence-type
    required: true
  - name: value
    type: string
    required: true
  - name: collected_at
    type: datetime
    required: true
---

## Description

One collected fact supporting or refuting a hypothesis.

## Responsibility

None.

=== domain/troubleshooting/evidence-type
---
type: enumeration
values:
  - log
  - metric
  - report
---

## Description

The kinds of evidence an investigation collects.

## Responsibility

None.

=== domain/troubleshooting/evidence.log
---
entries:
- field: attributes.value.type
  unstated: The material does not say what shape an evidence value takes.
  decided: string
  why: Every evidence sample in the material is shown as free text.
---

=== domain/troubleshooting/hypothesis
---
type: entity
aggregate: case
attributes:
  - name: statement
    type: string
    required: true
  - name: evidence
    type: evidence
    many: true
---

## Description

One candidate explanation for the problem under investigation.

## Responsibility

Carry the evidence that confirms or refutes one explanation.

=== domain/troubleshooting/investigation
---
type: entity
aggregate: case
attributes:
  - name: started_at
    type: datetime
    required: true
relationships:
  - target: hypothesis
    type: composition
    cardinality: "0..*"
---

## Description

The diagnostic work performed inside one case.

## Responsibility

Hold the hypotheses raised while diagnosing the case.

=== domain/troubleshooting/resolution
---
type: entity
aggregate: case
attributes:
  - name: summary
    type: string
    required: true
  - name: resolved_at
    type: datetime
    required: true
---

## Description

The outcome that closes a case.

## Responsibility

Record what solved the problem.

=== rules/troubleshooting/alert-opens-case
---
type: policy
statement: An alert unresolved for 24 hours MUST open a case.
constrains:
  - domain/monitoring/alert
  - domain/troubleshooting/case
consistency: eventual
---

## Description

Stale alerts converge into cases; the two contexts need not agree in one transaction.

=== rules/troubleshooting/case-transitions
---
type: state-machine
statement: A case moves only along the declared transitions.
subject: domain/troubleshooting/case
status: domain/troubleshooting/case-status
initial: open
terminal:
  - resolved
  - cancelled
transitions:
  - from: open
    trigger: start-investigation
    to: investigating
  - from: investigating
    trigger: resolve
    to: resolved
  - from: open
    trigger: cancel
    to: cancelled
  - from: investigating
    trigger: cancel
    to: cancelled
rejections:
  - from: open
    trigger: resolve
  - from: investigating
    trigger: start-investigation
---

## Description

The lifecycle of a case, total over its states and triggers.

=== rules/troubleshooting/case-transitions.log
---
entries:
- field: rejections
  unstated: The material never says what resolving an open case does.
  decided: The trigger is rejected in the open state.
  why: Resolution without an investigation contradicts the stated flow.
---

=== rules/troubleshooting/hypothesis-requires-evidence
---
type: invariant
statement: A hypothesis MUST hold at least one piece of evidence before its case resolves.
constrains:
  - domain/troubleshooting/hypothesis
---

## Description

No case resolves on an unsupported explanation.

=== scenarios/system/troubleshoot-from-alert
---
subject: contracts/system/troubleshoot-customer-problem
involves:
  - contracts/monitoring/alert-raised
  - domain/troubleshooting/case
given:
  - monitoring raised an alert that stayed unresolved for 24 hours
when:
  - the alert-opens-case policy fires
then:
  - a case is opened carrying the alert as intake
  - the case resolves through the ordinary investigation flow
---

## Description

End-to-end acceptance of the troubleshooting capability.

=== scenarios/troubleshooting/refuse-resolution-without-evidence
---
subject: rules/troubleshooting/hypothesis-requires-evidence
given:
  - a case under investigation holds one hypothesis with no evidence
when:
  - the operator resolves the case
then:
  - the resolution is refused
  - the case stays investigating
---

## Description

The invariant refusing an unsupported resolution.
