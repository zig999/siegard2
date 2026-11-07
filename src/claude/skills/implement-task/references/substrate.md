# A task that declares `produces`

Read at step 1, step 4 and step 5 when the task declares `produces`.

## At situate: what `produces` drops

**`produces` drops the presupposition half of the registry check, and nothing else.** A task
producing an artifact builds the substrate, so holding it to the substrate's presence would be
circular. The record is held to the claim afterwards: the validator refuses an implementation whose
`files` does not list what the task said it would produce.

## At build: the install alone

**A task declaring `produces` whose written files no rule reaches runs only the install.** Ask:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/deliver.py --standard <registry> --reach --for <each file the implementer wrote>
```

- `reached by no rule: N of N` — run only the step whose role is `install`; where the registry
  declares no install, nothing runs. Every other step decides a rule over a file, and this delivery
  wrote no such file, so a green step here would record a project that builds when nothing was
  checked. The install shows the manifest is well formed and its dependencies resolve.
- Any file a rule reaches — run the whole build phase step 4 runs.

Either way the report names the steps that did not run and why, and the record's `## Notes` carries
the same sentence, so a substrate record never reads as a project that builds. The validator holds
the claim: it refuses a record whose run covered fewer steps than the registry declares, except for
a task that declares `produces` and wrote nothing any rule reaches.

## At prove: no proof owed

**A task delivered as the substrate alone writes no proof record.** «A task delivered as the
substrate alone — it declares `produces`, and nothing it wrote is a file a rule of its standard
reaches — owes no proof.» (SPEC-004 R23) The validator decides which task that is, never your
reading of what the task built:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/deliver.py --outstanding <delivery-root> <work-root> <target-source-root> <specification-root> --scope task/<epic>/<slug>
```

Where it names the task `implemented as the substrate alone, which owes no proof`, steps 5 and 6
do not run: say so in the report and go to step 8. A proof written there would claim that tests
hold up a task where no test could exist. Anywhere else the task proves like any other: «Every other
task owes one, a task that built the substrate and also wrote a file a rule reaches included.»
(SPEC-004 R23)
