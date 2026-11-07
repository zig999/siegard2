---
entries:
- field: rejections
  unstated: The material never says what resolving an open case does.
  decided: The trigger is rejected in the open state.
  why: Resolution without an investigation contradicts the stated flow.
- field: rejections.resolved.cancel
  unstated: The material says a resolved case can be reopened but not whether a resolved case can still be cancelled.
  decided: The cancel trigger is rejected in the resolved state.
  why: Cancelling abandons a problem never solved, and a resolved case has already been solved.
- field: rejections.resolved.resolve
  unstated: The material does not say what resolving an already resolved case does.
  decided: The resolve trigger is rejected in the resolved state.
  why: A resolved case returns to resolution only through a reopened investigation.
- field: rejections.resolved.start-investigation
  unstated: The material names reopening as the only way back to investigation and says nothing of starting one on a resolved case.
  decided: The start-investigation trigger is rejected in the resolved state.
  why: The material routes a resolved case back to investigation through reopening alone.
- field: rejections.open.reopen
  unstated: The material speaks of reopening only a resolved case and is silent on an open case.
  decided: The reopen trigger is rejected in the open state.
  why: The material makes reopening something that happens to a resolved case.
- field: rejections.investigating.reopen
  unstated: The material speaks of reopening only a resolved case and is silent on a case under investigation.
  decided: The reopen trigger is rejected in the investigating state.
  why: A case under investigation is already where reopening would send it.
---
