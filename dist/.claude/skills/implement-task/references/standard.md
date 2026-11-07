# The project's standard

Read with the inputs, and again at step 1 when the registry check runs.

## Resolving the optional standard

**The project's standard** is the path to the registry of rules the project set for itself, in the
project's own tree. Named, the source is written to follow it; not named, the only convention you
follow is what the inventory evidenced, and the report says so. The framework ships no rule:
`${CLAUDE_PLUGIN_ROOT}/schemas/standard.json` is the contract a project's own file answers to.

It resolves in this order, from the same `project.py` run the inputs name, and the report says
which step answered:

1. **A naming in the invocation wins**, unlike the roots.
2. Otherwise the file's `standard` answers **for the target**. `project.py` prints one
   `standard:` line for a one-target project, or one `standard <target>:` line per target the file
   declares one for; the line for this invocation's target is the answer, never another target's.
   `null` there declares that the target has none: take the narrow path without asking again.
3. Where neither answers — no naming, no file, no field, or no entry for this target — the
   standard joins the single stop of absent inputs, and the report carries the `/siegard-config`
   invocation that declares it for this target, ready to paste.

A file that does not hold together is a stop reported verbatim. A naming that overrode a differing
file is reported with both. Below, a standard "named" means resolved by either step.

## The refusals of the first form

`deliver.py --standard … --against` refuses twice:

- **A registry that does not hold together.** It answers to nothing, and fixing it is its owner's.
- **An artifact the registry presupposes and the tree does not hold.** A rule is a condition over a
  file that exists, so a registry whose substrate is absent holds nothing to account. The output
  names the way out: a task declaring the artifact in `produces`, planned through `/plan-work` and
  delivered first.

## The registry's pin, and what is read from it

Note the registry's path relative to the target source root, and its absolute path. The writer each
record goes through stamps the SHA-256 of its text as read when the record is written —
`sha256sum <target-source-root>/<path>` by hand. Nothing is copied: the record points at the
project's own file and stays held to the text it read, whatever the file says later.

What the check printed is everything you read from the registry: each step with its command and
bound, which step installs and which proves, and the packages it authorizes by name. Do not open
the registry's text yourself: its rules are the producers' to read, and each is handed the path at
steps 3 and 5.
