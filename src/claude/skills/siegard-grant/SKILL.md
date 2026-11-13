---
name: siegard-grant
description: Use when a person wants the framework to take the decisions its stops hand back — a door, a commit of the route's own work, the closing of an initiative — without asking at each stop, until the person clears it; or to clear a grant already armed. Records the person's words verbatim and arms the grant for the project, or for one initiative. Closed to the model, so every argument is the person's own words. Not for delivering anything now (that is /deliver-scope), and not for a run that ends by itself (that is /siegard-goal).
argument-hint: "[<project-root>] [--clear | [--slug <slug>] [--target <key>] [--doors <skill>,...|none] [--budget <n>] [--commits] [--close] <the person's words>]"
disable-model-invocation: true
effort: low
---

You arm one grant and stop. «A grant is armed only by the person's own invocation of
`/siegard-grant`, a skill closed to the model, whose arguments are the person's words.» (SPEC-011 R1)
`bin/grant.py` records the words, checks every bound and writes every file; this skill reads the
invocation, hands the script exactly what the person said, and reports what the script printed.

`${CLAUDE_PLUGIN_ROOT}` is set where this skill runs as an installed plugin. Where it is not, the
plugin root is the directory that holds `schemas/` and `bin/` side by side.

Two invocations, so you can tell which you hold:

```
/siegard:siegard-grant /path/to/project --commits --close Pode decidir as paradas do plano e fechar a iniciativa quando tudo estiver entregue.
/siegard:siegard-grant /path/to/project --clear
```

## Reading the invocation

Read the arguments once, and decide nothing they do not say:

| What | How it is recognised | If absent |
|---|---|---|
| **Project root** | the first argument, a directory holding `siegard.json` | the git toplevel of the directory the invocation was typed in, disclosed: `python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/project.py --here` |
| **Clear** | `--clear`, alone beside the root | the invocation arms |
| **Slug** | `--slug <slug>`, a live initiative | the grant covers every live initiative of the project |
| **Target** | `--target <key>` | the script takes the first key `siegard.json` declares and says so |
| **Doors** | `--doors`, a comma list from `plan-work`, `implement-task`, `review-change`, `reconcile`, `deliver-scope`, `analyse`; or `none` | all six, `analyse` among them |
| **Budget** | `--budget <n>`, a whole number of judged doors | zero: a choice between open doors stops until the person writes one |
| **Commits** | `--commits` | none |
| **Close** | `--close` | none |
| **The words** | every other word, whole and in order, once the flags are out | a stop that asks for them, before any script runs |

The words are the person's own and are handed to the script verbatim — never summarized,
translated, completed or corrected — because with `--close` they are the reason an initiative is
closed under, and a paraphrase is a reason nobody gave. A flag that appears inside the words is
part of the words. The grant without words is no grant: ask for them and run nothing.

## Clearing

Run `python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/grant.py --disarm <project-root>` and hand the person what
it printed, as a report. With no grant armed it says so, and that is the report. The project then
behaves as it did before the grant. `--clear` beside any other flag or any words is no clear: ask
which the person meant.

## Running the script

The words travel on stdin, under a heredoc delimiter that no line of them equals — pick another
where `WORDS` is one of their lines — so no quote, newline or character in them is altered by a
shell. The heredoc adds one final newline, and the digest covers the file as stored.

```
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/grant.py --arm <project-root> [--slug <slug>] [--target <key>] [--doors a,b|none] [--budget <n>] [--commits] [--close] --words-file - <<'WORDS'
… the person's words, verbatim …
WORDS
```

The record it writes is held to the contract `${CLAUDE_PLUGIN_ROOT}/schemas/grant.json` before it is
written. The script refuses a second grant, empty words, a slug that is not a live initiative, an
entry point outside the list, a budget without doors, and an arming with no clause; it prints every
reason. On success it prints what it recorded — what the grant covers, the doors, the budget, the
clauses, the words' digest, the target where it chose one, and the plugin's version — and the report
quotes those lines. The words file is left uncommitted under the telemetry root; the run's measure
commits that root.

## Report, and stop

Run `python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/handoff.py --prepare --skill siegard-grant --project
<project-root> [--slug <slug>, where the grant names one] --target <target> --language <en or pt-BR,
the conversation's>`. It prepares a report: write the full report through `bin/handoff.py
--save-report <path>` to the path its `report` names, fill `body`, and hand the person what
`handoff.py --render` prints — the opening «A handoff opens with what needs the person, and explains
after» (SPEC-006 R1) states. `body` is two or three sentences for a person who knows the project but
not this framework: what the grant lets a session take at a stop, what it never does, and how the
person ends it. It carries no flag, script name or slug. Then, in its own fenced block, the line that
ends the grant: `/siegard:siegard-grant <project-root> --clear`.

**Armed.** What the grant takes, from the lines the script printed: a door whose every other door
its own check excluded; a door the door decider chooses, within the budget — none where the budget
is zero, which the report says; the commits of what the route wrote; the closing of an initiative,
once everything in it is delivered, proven and reviewed. Where `analyse` is among the doors, the
specification it writes is disclosed and the person reads it afterwards. What it never takes,
whatever the words say: a choice only the person makes, a push, a branch, an edit by a session
outside a skill, a file of the project file, a standard or `CLAUDE.md`, and anything outside this
project.

**Refused.** `body`: nothing was armed, how many reasons the script gave, and that each is below.
Then the script's reasons, verbatim, in one fenced block.

## What you never do

- Arm a grant but under an invocation of this skill; run `grant.py --arm` on a later message, a
  yes, or any word the person did not type as this skill's arguments.
- Hand the script words other than the person's: summarized, translated, corrected or completed.
- Write, commit or change any file but the ones the script writes: the words, verbatim, under the
  telemetry root, and the armed record.
