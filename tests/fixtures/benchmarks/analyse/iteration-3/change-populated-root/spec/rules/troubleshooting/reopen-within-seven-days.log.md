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
