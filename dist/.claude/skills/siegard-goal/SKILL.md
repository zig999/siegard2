---
name: siegard-goal
description: Use when a person wants one scope — an objective in prose, an epic, or a set of tasks of a live plan — carried end to end with nobody asked anything along the way. Composes the condition of a Claude Code goal that drives /deliver-scope over that scope, after checking everything the route would refuse before its first step, and prints it for the person to paste after /goal. The goal it composes ends when a script reads state A (delivered, proven, reviewed, measured) or state B (stopped where only a person moves it) from disk, so it always ends. It writes nothing and never arms a goal itself — pasting the condition is the person's act and the authorization the route needs. Not for delivering anything now (that is /deliver-scope), and not for watching a run (that is /siegard-progress).
argument-hint: "[objective in prose | epic/<name> | task/<epic>/<name> ...]"
effort: low
---

You compose one goal condition and stop. The condition is short on purpose: it names the route,
the authorization, the scope and one command, and states no rule — «A goal condition names the
route, the authorization, the scope and the invocation that answers its state, and states no rule:
the rules are those of the plugin version the invocation pins.» (SPEC-008 R6). Every rule the run
follows is in the skills of that version, and the command decides when the goal is over.

## Required inputs

A missing input is a stop, not a default:

1. **the project root** — where `siegard.json` lives. Named by the human; inferred rather than
   named, its absence is a stop.
2. **the scope** — the person's own words, one of three forms:
   - an **objective** in prose: what the system must come to do. It is carried into the condition
     verbatim — never summarized, translated or completed — because the condition is the ask
     `/deliver-scope` requires in the person's own words, and a paraphrase is an ask nobody made;
   - an **epic**, `epic/<name>`, of a live plan;
   - **tasks**, `task/<epic>/<name>`, of a live plan.
3. **the initiative's slug** — named by the human, or decided and disclosed: for an epic or tasks,
   the one live initiative under `work_root` whose plan holds them, where exactly one does; for an
   objective, a new kebab-case slug of at most five words taken from the objective's own terms,
   naming no directory under `work_root`.
4. **the target** — by the key `siegard.json`'s `targets` names it; where it declares exactly one,
   that key, decided and disclosed.

Two optional inputs, both the person's and never proposed here: **the budget** — how many judged
doors the run may take, each only as the door decider returns it; none where the person names
none, so a choice no fact decides ends the run — and **the findings policy** — which findings
the run corrects by a corrective increment, once. `contradicts` is the one kind a route corrects;
the script refuses another, and the refusal is the report.

Run `python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/project.py <project-root>` once, before anything else.
Every root answers only from there; a field the file does not declare is a stop, and the report
carries the `/siegard-config` invocation ready to paste — that skill is closed to model
invocation, so the paste is the human's.

`${CLAUDE_PLUGIN_ROOT}` is set where this skill runs as an installed plugin. Where it is not, the
plugin root is the directory that holds `schemas/` and `bin/` side by side.

## The order

1. To decide a slug for an epic or tasks, read the `plan.json` of each initiative under
   `work_root` without `closure.md` — the index whose contract is
   `${CLAUDE_PLUGIN_ROOT}/schemas/plan.json` — and take the one whose nodes hold every id named.
   None, or more than one, is a stop naming what was found.
2. Compose:

   ```
   python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/goal.py --compose <project-root> --slug <slug> [--target <key>] (--scope <id> [--scope <id>]... | --objective "<the objective, verbatim>") [--budget <n>] [--correct contradicts]
   ```

   The script checks what `/deliver-scope` would refuse before its first step — the
   specification, changes pending under the roots the route writes, a closed slug, an id the plan
   does not hold — and pins where `HEAD` stands, the plugin's version and every change already
   pending elsewhere, which the goal leaves untouched. A refusal is the report: every reason it
   printed, verbatim, each with what resolves it.
3. Report, and stop.

## Report, and stop

Open as «A handoff opens with what needs the person, and explains after» (SPEC-006 R1) states.
The one decision is the person's: whether to arm the goal. Open with it — the condition the script
printed, whole and unedited, in one fenced block preceded by `/goal `, so that copying the block
arms it — and then, in the session's own words, what the goal will do: carry the scope through
`/deliver-scope`, commit each step that skill defines, and end when the state command answers
`state A` or `state B`, both of which end it. Then what was decided rather than told — the slug,
the target — and every line the script printed under `checked:`, verbatim.

Where the script refused, the report opens instead with each reason and what resolves it, ready
to paste where it is a command, and no condition.

## What you never do

- Arm a goal, or run `/deliver-scope` — the condition becomes an ask only when the person pastes
  it.
- Edit, shorten or add to the condition the script printed: a rule written into it is a second
  copy of one a skill already holds, and the evaluator reads it as something to verify.
- Write, commit or change any file.
