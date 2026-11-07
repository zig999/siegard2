---
name: siegard-goal
description: Use when a person wants one scope — an objective in prose, an epic, or a set of tasks of a live plan — carried end to end with nobody asked anything along the way. Checks everything /deliver-scope would refuse before its first step, then either arms the goal through the framework (the invocation opens with --arm) or composes its condition and hands two ready lines to paste — one that arms it through the framework, one after /goal. The goal ends when a script reads state A (delivered, proven, reviewed, measured) or state B (stopped where only a person moves it) from disk, so it always ends. Writes only the objective, verbatim, and the armed record. Closed to the model, so every argument is the person's own words. Not for delivering anything now (that is /deliver-scope), and not for watching a run (that is /siegard-progress).
argument-hint: "[--arm] [<project-root>] (epic/<name> | task/<epic>/<name> ... | <objective in prose> | --objective-file <path>) [--slug <slug>] [--target <key>] [--budget <n>] [--correct contradicts] [--specify]"
disable-model-invocation: true
effort: low
---

You turn one scope into one goal and stop. The goal's condition is short on purpose — «A goal
condition names the route, the authorization, the scope and the invocation that answers its state,
and states no rule: the rules are those of the plugin version the invocation pins.» (SPEC-008 R6)
— so every rule the run follows lives in the skills of that version, and one command decides when
the goal is over. `bin/goal.py` does every check and writes every file; this skill reads the
invocation, hands the script exactly what the person said, and reports what the script printed.

This skill is closed to the model's invocation: only the person types it, so every argument it
receives is the person's own words — the scope, the objective and the word to arm. That is the
gate R6 places here, and no other component runs `goal.py --arm`.

`${CLAUDE_PLUGIN_ROOT}` is set where this skill runs as an installed plugin. Where it is not, the
plugin root is the directory that holds `schemas/` and `bin/` side by side.

## Reading the invocation

Read the arguments once, in this order, and decide nothing they do not say:

| What | How it is recognised | If absent |
|---|---|---|
| **To arm** | `--arm` as the first argument, and only there | compose, do not arm |
| **Project root** | the next argument, where it is a path to a directory holding `siegard.json` | the git toplevel of the session's working directory, disclosed |
| **Scope ids** | each `epic/<name>` or `task/<epic>/<name>`, bare or after `--scope` | — |
| **Objective file** | `--objective-file <path>` | — |
| **Objective** | the remaining text, whole and in order, once every flag and id is taken out | — |
| **Slug** | `--slug <slug>` | decided, below, and disclosed |
| **Target** | `--target <key>` | the one key `targets` declares, disclosed; more than one is a stop |
| **Budget** | `--budget <n>`, a whole number | none: a choice no fact decides ends the run |
| **Findings policy** | `--correct contradicts` — the one kind a route corrects | none: every finding is reported, none corrected |
| **To specify** | `--specify`, over an objective only | none |

**To arm** is the invocation's first argument, `--arm`, and nothing else: the word in any other
place — inside an objective, after the scope, in a later message — arms nothing. A later message
asking to arm is answered with the invocation to paste that the composing report handed, never by
running `goal.py --arm`.

**The project root** where none is named is what `python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/project.py
--here` prints as `project_root:` — «Where the invocation names none, the project root is the git
toplevel of the session's working directory, as `bin/project.py --here` resolves it, and only
where that toplevel holds `siegard.json`» (SPEC-010 R6). The person opened the session there and
typed the invocation in it, so the directory is their choice as much as any argument. A toplevel
holding no `siegard.json` is a stop: `--here` refuses it.
Every line this skill hands to paste names the root explicitly, so it arms the same project from
any directory.

**The scope is exactly one** of: scope ids; an objective file; an objective. Ids beside prose, an
objective file beside prose, or no scope at all is a stop that quotes what was received and gives
the three forms. An objective is the person's own words and is handed to the script verbatim —
never summarized, translated, completed or corrected — because the ask `/deliver-scope` requires is
the person's, and a paraphrase is an ask nobody made.

**A citation** is an objective whose text points at words already in this conversation instead of
stating what the system must do — "parts 2 and 3 above", "the scope you wrote". Pointing is the
person's act: the text pointed at becomes the objective, copied character for character as the
conversation holds it. A pointer that does not name one span without doubt is a stop that quotes
each candidate. Text that both points and states is a stop that asks which one is the objective.
Where the span holds a part this route does not carry — a fact the specification does not state
yet, which `/analyse` takes before any goal; an edit to the project's standard or to
`siegard.json`, the person's own files — the copy is never cut to fit: it is a stop naming each such
part and what carries it instead.

**The slug**, where none is named: for scope ids, the one initiative under `work_root` without
`closure.md` whose `plan.json` — contract `${CLAUDE_PLUGIN_ROOT}/schemas/plan.json` — holds every id;
none or more than one is a stop naming what was found. For an objective or a citation, a new
kebab-case slug of at most five words from the objective's own terms, naming no directory under
`work_root`; an objective cannot reuse a live initiative's slug, and the stop says to name its
epics instead.

**Where an objective changes a fact of the business** — a status, a refusal, what the system tells
someone, who may see what — and `--specify` is absent, the report says the goal will stop at the
first fact the specification does not hold, and that `--specify` is the person's to add. It is
never added for them.

Then run `python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/project.py <project-root>` once. Every root answers
from there; a field the file does not declare is a stop, and the report carries the
`/siegard-config` invocation ready to paste — that skill is closed to model invocation, so the
paste is the person's.

## Running the script

Run from the project root. An objective or a citation always travels on stdin, under a heredoc
delimiter its text does not contain, so no quote, newline or character in it is altered by a shell:

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/goal.py <--arm|--compose> <project-root> --slug <slug> [--target <key>] [--budget <n>] [--correct contradicts] [--specify] --scope <id> [--scope <id>]...
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/goal.py <--arm|--compose> <project-root> --slug <slug> [--target <key>] [--budget <n>] [--correct contradicts] [--specify] --objective-file <path>
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/goal.py <--arm|--compose> <project-root> --slug <slug> [--target <key>] [--budget <n>] [--correct contradicts] [--specify] --objective-file - <<'OBJECTIVE'
… the objective or the citation, verbatim …
OBJECTIVE
```

- **`--arm`** where the invocation opens with it and the scope is no citation. The script runs
  every check composing runs, refuses a project already holding an armed goal, and records the
  condition for the plugin's `Stop` hook: «A goal the person arms through the framework ends on
  the state script's answer at the session's stop, never on a model's reading: `state A` or
  `state B` ends the goal and lets the session stop, `not yet` blocks the stop with the checks
  that failed, and a fourth consecutive `not yet` whose whole answer repeats the last ends the
  goal paused.» (SPEC-008 R14)
- **`--compose`** otherwise. Over a citation, `--arm` composes and does not arm: what the person
  would arm is the text the script writes, and they read that file before an invocation naming it
  arms it.

Either way the script checks what `/deliver-scope` would refuse before its first step — the
specification, changes pending under the roots the route writes or in the trace and
`siegard-reconcile/` it commits, a closed slug, an id the plan does not hold — and pins where
`HEAD` stands, the plugin's version and every change already pending elsewhere, which the goal
leaves untouched. Keep its whole output: the report quotes it.

## Report, and stop

Every outcome is handed through the handoff record, so the person reads the same shape every
time. «The state a handoff opens with is a script's line, never the session's» (SPEC-006 R10).
Run `python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/handoff.py --prepare --skill siegard-goal --project
<project-root> --slug <slug> --target <target> --language <en or pt-BR, the session's>`. It prepares
a report: write the full report through `bin/handoff.py --save-report <path>` to the path its
`report` names, fill `body`, and hand the person what `handoff.py --render` prints — the opening
«A handoff opens with what needs the person, and explains after» (SPEC-006 R1) states — followed
by the blocks below. A refusal is answered by rewriting the field it names; a state it says has
moved, by running `--prepare` again and carrying its `state` and `state_from` whole. Where the goal
was armed, the state `--prepare` printed is the armed goal's own first line.

`body` is two or three sentences in the session's language, for a person who knows the project but
not this framework: what happened, what the goal does, and what the person does next. It carries
no flag, script name, slug or state letter — those belong in the blocks, where `handoff.py --check`
reads no fence as prose. Nothing after the rendered handoff asks a question: the record is a report.

**Armed.** `body`: the goal is armed and starts at once; it carries the scope through delivery,
review and measurement, one commit per step, and ends by itself — delivered, or stopped where only
the person can move it. Then, each in its own fenced block: the line that follows the run,
`/siegard:siegard-progress <project-root> <slug>`, and the line that ends it,
`! python3 -B <the resolved plugin root>/bin/goal.py --disarm <project-root>`.

**Composed.** `body`: the goal is composed and not armed yet, and nothing was written but the
objective's file. Then one line saying why neither way is recommended — both hold the same route,
both can be ended, and no command printed a cost — and what each assumes, followed by each way in
its own fenced block, whole, so that copying the block arms it:

- through the framework — the end is the state command's answer at every stop, and it assumes
  this session runs with this plugin's hooks: `/siegard:siegard-goal --arm <project-root> --slug
  <slug> --target <target>`, then the scope exactly as composing took it — `--scope <id>` for each
  id, or `--objective-file` naming the file the `objective:` line names, joined to the project
  root — and every `--budget`, `--correct` and `--specify` composing took;
- through the harness — it assumes nothing beyond the paste: `/goal ` and the condition the script
  printed, whole, because `/goal` with anything else, the objective alone among them, names no
  route and `/deliver-scope` refuses it.

Where the scope was a citation, the line before the blocks says the person reads the objective's
file first, by its path: what they arm is that text.

**Refused.** `body`: nothing was armed or composed, how many reasons the script gave, and that each
is below with what resolves it. Then the script's reasons, verbatim, in one fenced block, and each
resolution the script printed that is a command in its own fenced block. What resolves a reason is
what the script printed beside it, never a route described here: another entry point's
requirements are stated in its own file, and a summary written here is a second copy that drifts.

**Stopped before the script.** A stop from reading the invocation — no scope, two scopes, an
ambiguous citation, a slug that cannot be decided, no project file — writes nothing and runs no
script. Where a project root resolves, it is handed as a refused report, with the slug and target where
known, whose block quotes what was received and gives the invocation's forms; where none resolves, as plain text saying the same.

**The full report** holds, in this order: the outcome; what the goal will do, in the session's
words; every value decided rather than told — the root, the slug, the target — each with where it
came from; every line the script printed under `checked:`, verbatim; the condition, whole and
unedited; and, over a citation, the objective's file, whole.

Never invite an edit of the objective: an objective the person wants changed is a new invocation
of this skill.

## What you never do

- Arm a goal but under an invocation whose first argument is `--arm`; run `goal.py --arm` on a
  later message, a yes, or any word but that argument; paste `/goal` or this skill's invocation for
  the person; or run `/deliver-scope` — the condition becomes an ask only when the person pastes it
  or arms it.
- Hand the script an objective other than the person's words: summarized, translated, corrected,
  completed, or quoted through a shell that could alter it.
- Edit, shorten or add to the condition the script printed: a rule written into it is a second copy
  of one a skill already holds, and the evaluator reads it as something to verify.
- Write, commit or change any file but the ones the script writes: the objective, verbatim, under
  the telemetry root, and the armed record.
