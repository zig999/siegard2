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
  - name: reopenings
    type: reopening
    many: true
relationships:
  - target: investigation
    type: composition
    cardinality: "1"
  - target: resolution
    type: composition
    cardinality: "0..*"
operations:
  - open
  - start-investigation
  - resolve
  - cancel
  - reopen
---

## Description

A customer problem submitted to the troubleshooting process.

## Responsibility

Control the investigation from opening to resolution or cancellation, and back to investigation when a resolved case is reopened.

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

=== domain/troubleshooting/case.log
---
entries:
- field: attributes.reopenings
  unstated: The material does not say where a case's reopenings are held or how many a case may have.
  decided: an attribute of the case holding many reopening values
  why: Nothing in the material limits a resolved case to one reopening.
- field: relationships.resolution.cardinality
  unstated: The material does not say what happens to a case's resolution when it is reopened and later resolved again.
  decided: 0..*
  why: A reopened case is resolved again, and keeping each resolution preserves the one the reopening's window counted from.
---

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

=== domain/troubleshooting/reopening
---
type: value-object
attributes:
  - name: reason
    type: string
    required: true
  - name: reopened_at
    type: datetime
    required: true
---

## Description

One return of a resolved case to investigation, made because the customer reported that the problem came back (the material's "reabertura").

## Responsibility

Record why the customer had a resolved case reopened.

=== domain/troubleshooting/reopening.log
---
entries:
- field: type
  unstated: The material names a reopening and says each one records the customer's reason, but not whether the domain tells two reopenings apart by identity.
  decided: value-object
  why: A reopening is never changed after it is recorded, so two with equal reason and time are interchangeable.
- field: attributes.reason.type
  unstated: The material says the reason is the one the customer reports, not what shape it takes.
  decided: string
  why: The reason is the customer's own account, which no closed set of values could hold.
- field: attributes.reopened_at
  unstated: The material does not say that a reopening records when it happened.
  decided: a required datetime reopened_at
  why: The 7-day window can only be checked against the moment the reopening was made.
---

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
  - from: resolved
    trigger: reopen
    to: investigating
rejections:
  - from: open
    trigger: resolve
  - from: investigating
    trigger: start-investigation
  - from: open
    trigger: reopen
  - from: investigating
    trigger: reopen
  - from: resolved
    trigger: start-investigation
  - from: resolved
    trigger: resolve
  - from: resolved
    trigger: cancel
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
- field: rejections
  unstated: The material never says what reopening a case that is open or investigating does.
  decided: The reopen trigger is rejected in the open and investigating states.
  why: The material allows only a resolved case to be reopened.
- field: rejections
  unstated: Once resolved is no longer terminal, the material never says what start-investigation, resolve or cancel do in the resolved state.
  decided: start-investigation, resolve and cancel are rejected in the resolved state.
  why: The material names reopening as the only way a resolved case moves.
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

=== rules/troubleshooting/reopen-within-seven-days
---
type: invariant
statement: A resolved case MUST be reopened only within 7 days of its latest resolution.
expression: reopening.reopened_at <= latest(resolution.resolved_at) + 168 hours
constrains:
  - domain/troubleshooting/case
  - domain/troubleshooting/resolution
---

## Description

Bounds how long after its resolution a customer can have a case reopened.
It does not decide which states accept a reopening; rules/troubleshooting/case-transitions does.

=== rules/troubleshooting/reopen-within-seven-days.log
---
entries:
- field: statement
  unstated: The material says 7 days after the resolution but not which resolution counts once a case has been reopened and resolved more than once.
  decided: The window counts from the case's latest resolution.
  why: The problem the customer reports as returned is the one the latest resolution claimed to solve.
- field: expression
  unstated: The material says until 7 days after the resolution without saying whether the limit is inclusive or how a day is counted.
  decided: reopened_at at most 168 hours after the latest resolution's resolved_at, the bound included
  why: The material's 'até' reads as up to and including, and elapsed hours avoid a dependence on time zones.
---

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
