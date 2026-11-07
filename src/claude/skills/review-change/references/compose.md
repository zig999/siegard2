# Compose the review

Read at step 4. Write `review/<review-name>.md` under the delivery root, under the name input 6
fixed: the name is this review's identity, and the path is where it lives.

## What the frontmatter carries

- `target` — input 4's key, the root `reviewed` and the standard's path are spelled from, which the
  validator resolves the record at;
- the file set it was computed over, and the tasks it answers;
- one entry per pass;
- the coverage entries and the unpaired tests, where that pass ran;
- the standard's own path and the pin of its text, where that pass ran;
- how many failures were counted, where that pass ran;
- the run's directory whenever one was captured, green or red. A red run is what the failures pass
  read; a green one is the evidence that the change built, and its failures entry says so:
  `missing: run/<review-name> passed; there was no failure to read`;
- the reconciliation record the conformance pass folded, `reconciliation:
  siegard-reconcile/<review-name>.md`. The validator holds it to the pass having run and to this
  review's own file set; over a target holding a trace file, its absence prints a receipt naming
  the review that judged the plan's nodes alone;
- every finding.

The record holds no list of the rules that were in scope. The standard's path and its pin already
determine that set and the validator derives it, so a stored list would be a second answer nobody
could check. Which rules were in scope belongs in the report, for the person.

## Findings and passes

- Stamp each finding's pass yourself: the subagents return findings without one, so a finding
  cannot claim a pass that did not run.
- An entry for a pass that did not run names what was missing. That is what says it did not run,
  and the validator refuses a finding attributed to it.
- Every finding names the file it was observed in, exactly as the file set lists it, and the
  validator holds it there.

## The body

Exactly two headings, in order: `## What it is`, then `## Notes`. One sentence per line; a section
with nothing to say carries the literal line `None.` What the passes looked past, and what this
framework does not review at all, belongs in `## Notes`: a limit only the conversation held is one
the next reader never sees.

## Writing the file

A finding's own prose meets a colon often enough that a plain scalar breaks the moment one appears
in it. Emit the frontmatter with `python3 -c` calling `yaml.safe_dump` rather than typing it by
hand, so a sentence's own colon is never read as a second mapping key; PyYAML is already a declared
dependency of this framework's own tooling.

Check the file on its own as soon as it is composed:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/deliver.py --node <file> <delivery-root>
```
