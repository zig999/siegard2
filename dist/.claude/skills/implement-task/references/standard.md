# The project's standard

Read with the inputs, and again at step 1 when the registry check runs.

## Resolving the optional standard

One optional input: **the project's standard** — the path to the registry of rules the project set
for itself, in the project's own tree. Named, the source is written to follow it; not named, the
only convention this invocation follows is what the inventory evidenced, and the report says so.
The framework ships no rule and never owns the registry: `${CLAUDE_PLUGIN_ROOT}/schemas/standard.json`
is the contract a project's own file answers to.

The standard resolves in one order, from the same `project.py` run the inputs name, and the report says
which step answered. Unlike the roots, **a naming in the invocation wins here**. Where the
invocation names none, the file's `standard` answers **for the target**: a standard governs one
target, so `project.py` prints either one `standard:` line for a one-target project or one
`standard <target>:` line per target the file declares one for, and the line for the target this
invocation names is the answer — never another target's line. `null` there declares deliberately
that it has none for this target — the narrow path, chosen rather than forgotten, taken without
asking again. Where neither answers — no naming, no file, the file not declaring the field, or
the field declaring no entry for this target — the standard joins the single stop of absent
inputs: name it, or declare it through `/siegard-config` for this target, and the stop's report
carries that invocation ready to paste. A file that does not hold together is a stop reported
verbatim; a naming that overrode a differing file is reported with both. Below, a standard
"named" means resolved by either step.

## The refusals of the first form

The first form carries two refusals. A registry that does not hold together answers to nothing, and
fixing it belongs to whoever owns it. An artifact the registry presupposes and the tree does not
hold is the same refusal one step earlier: a rule is a condition over a file that exists and can
never ask for one, so a registry whose substrate is absent is a registry nothing can be held to —
its tool-decided rules have no step to run as, and its read-decided rules are read against files
written to answer a set of rules that was never in force. Written anyway, the absence is found once
per file in a review, after the files exist, instead of once here, before the first of them. The
way out is named in the output: a task declaring the artifact in `produces`, planned through
`/plan-work` and delivered first.

## The registry's pin, and what is read from it

Then note the registry's own path, relative to the target source root, and its absolute path:
the writer each record goes through stamps the SHA-256 of its text as read when the record is
written, `sha256sum <target-source-root>/<path>` by hand. Nothing is copied: the record points at the
project's own file, the same way `files[].path` already points at code without a second copy of
it. That pin is a citation of what this record read when it was written, not a standing guarantee
— the project's registry is free to keep evolving, and this record stays held to the text it
actually read rather than to whatever the file says later.

What the command printed is also everything this invocation reads *from* the registry: each step
with its command and its bound, which step installs and which proves, and the packages it
authorizes, by name. Do not open the registry's text here — the rules it declares are its two
producers' to read, each is handed the path at steps 3 and 5, and a registry read twice is the same registry
at twice the cost.
