# Specification overview

Derived by spec.py from the specification files; never edited.

## Contexts

| context | strategic | elements | rules | contracts | scenarios |
|---|---|---|---|---|---|
| monitoring | supporting | 1 | 0 | 1 | 0 |
| troubleshooting | core | 9 | 3 | 2 | 1 |

## Aggregates

- monitoring/alert — 0 entity(ies) inside, 2 attribute(s) on the root
- troubleshooting/case — 3 entity(ies) inside, 4 attribute(s) on the root

## Capabilities

- troubleshoot-customer-problem — orchestrates monitoring, troubleshooting

## Constraints

- asynchronous-events (system)

2 decision(s) disclosed in the decision logs.
