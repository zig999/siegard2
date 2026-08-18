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
