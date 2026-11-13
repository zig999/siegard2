---
name: siegard-grant
description: Use when a person wants the framework to take the decisions its stops hand back — a door, a commit of the route's own work, the closing of the initiative — for one live initiative, under limits the person states, without being asked at each stop. Records the person's words verbatim and arms the grant through `bin/grant.py`; a session then asks the script at each stop, and the script's gates decide what the grant lets it do. Closed to the model, so every argument is the person's own words. Not for delivering anything now (that is /deliver-scope), and not for a run that ends by itself (that is /siegard-goal).
argument-hint: "[<project-root>] --slug <slug> [--target <key>] [--doors <skill>,...] [--budget <n>] [--commits] [--close] <the person's words>"
disable-model-invocation: true
effort: low
---

You arm one grant and stop. «A grant is armed only by the person's own invocation of
`/siegard-grant`, a skill closed to the model, whose arguments are the person's words.» (SPEC-011 R1) `bin/grant.py` records the words, checks every bound and writes every file; this skill reads the
invocation, hands the script exactly what the person said, and reports what the script printed.

`${CLAUDE_PLUGIN_ROOT}` is set where this skill runs as an installed plugin. Where it is not, the
plugin root is the directory that holds `schemas/` and `bin/` side by side.

## Reading the invocation

Read the arguments once, and decide nothing they do not say:

| What | How it is recognised | If absent |
|---|---|---|
| **Project root** | the first argument, where it is a directory holding `siegard.json` | the git toplevel of the working directory the invocation was typed in, disclosed: `python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/project.py --here` |
| **Slug** | `--slug <slug>`, a live initiative | a stop naming the live initiatives `work_root` holds |
| **Target** | `--target <key>` | the one key `siegard.json` declares, disclosed; more than one is a stop |
| **Doors** | `--doors`, a comma list from `plan-work`, `implement-task`, `review-change`, `reconcile`, `deliver-scope` | none |
| **Budget** | `--budget <n>`, a whole number of judged doors | none: a judged choice is then a stop |
| **Commits** | `--commits` | none |
| **Close** | `--close` | none |
| **The words** | every other word, whole and in order, once the flags are out | a stop that asks for them |

The words are the person's own and are handed to the script verbatim — never summarized,
translated, completed or corrected — because with `--close` they are the reason the initiative is
closed under, and a paraphrase is a reason nobody gave. They travel on stdin, under a heredoc
delimiter their text does not contain, so no quote, newline or character in them is altered by a
shell.

## Running the script

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/grant.py --arm <project-root> --slug <slug> [--target <key>] [--doors a,b] [--budget <n>] [--commits] [--close] --words-file - <<'WORDS'
… the person's words, verbatim …
WORDS
```

The record it writes is held to the contract `${CLAUDE_PLUGIN_ROOT}/schemas/grant.json` before it
is written. The script refuses a second grant, an initiative that is not live, an entry point outside the list,
a budget without doors, and an arming with no clause; it prints every reason. Keep its whole
output: the report quotes it.

## Report, and stop

Run `python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/handoff.py --prepare --skill siegard-grant --project
<project-root> --slug <slug> --target <target> --language <en or pt-BR, the conversation's>`. It
prepares a report: write the full report through `bin/handoff.py --save-report <path>` to the path
its `report` names, fill `body`, and hand the person what `handoff.py --render` prints — the opening
«A handoff opens with what needs the person, and explains after» (SPEC-006 R1) states. `body` is
two or three sentences for a person who knows the project but not this framework: what the grant
lets a session take at a stop and what it never does, and what the person does to end it. It
carries no flag, script name or slug. Then, in its own fenced block, the line that ends the grant:
`! python3 -B <the resolved plugin root>/bin/grant.py --disarm <project-root>`.

**Armed.** What the grant takes, from the clauses the script recorded: a door whose every other
door its own check excluded; a door the door decider chooses, within the budget; the commits of
what the route wrote; the closing, once everything is delivered, proven and reviewed. And what it
never takes, whatever the words say: a choice only the person makes, a push, a branch, an edit by
a session outside a skill, `/analyse`, a file of the project file, a standard or `CLAUDE.md`, and
anything outside this project.

**Refused.** `body`: nothing was armed, how many reasons the script gave, and that each is below.
Then the script's reasons, verbatim, in one fenced block.

## What you never do

- Arm a grant but under an invocation of this skill; run `grant.py --arm` on a later message, a
  yes, or any word the person did not type as this skill's arguments.
- Hand the script words other than the person's: summarized, translated, corrected or completed.
- Write, commit or change any file but the ones the script writes: the words, verbatim, under the
  telemetry root, and the armed record.
