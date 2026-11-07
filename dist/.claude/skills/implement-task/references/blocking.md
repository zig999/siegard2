# A BLOCKING note

Read at step 1 when the task's `## Notes` carries an entry opening
`BLOCKING, from the specification —`.

The entry is a stop, whether or not you agree with it: what the class means is the binder's,
defined in `agents/execution-contract-binder.md`, and never re-derived here. A note you disagree
with is still a stop, and the disagreement goes in the report. Writing source past it would encode
a contradiction as though the business had decided it.

1. **Quote the entries whole from the task file**, which holds them — not from `--outstanding`,
   which read the same file.
2. **End the report with two doors**, each filled with everything you know: a `/plan-work`
   invocation, with the note quoted as the conflict the scope must settle, and an `/analyse`
   invocation, with the note quoted as the statement the specification must amend.
3. **Hand the choice as the person's own decision**: say what each door assumes is true and what
   would settle it, as `references/report.md` states for a stop over a BLOCKING note.

Either settlement re-runs the task through `/plan-work`'s implement-against step, which removes
the note; the record is written only then, never past the note. `deliver.py` holds the same stop:
it refuses a record over a task whose `## Notes` still carries the entry, quoting it and naming
both doors, and `--outstanding` lists which tasks carry one.
