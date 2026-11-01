---
name: siegard-goal
description: Use when a person wants one scope — an objective in prose, an epic, or a set of tasks of a live plan — carried end to end with nobody asked anything along the way. Composes the condition of a Claude Code goal that drives /deliver-scope over that scope, after checking everything the route would refuse before its first step, and hands it to paste after /goal, beside the invocation of this skill that arms it through the framework. The goal ends when a script reads state A (delivered, proven, reviewed, measured) or state B (stopped where only a person moves it) from disk, so it always ends. It writes only the objective, verbatim, to a file the condition names, and arms only where the person's invocation opens with --arm; closed to the model, so its arguments are the person's own words. Not for delivering anything now (that is /deliver-scope), and not for watching a run (that is /siegard-progress).
argument-hint: "[--arm] [objective in prose | epic/<name> | task/<epic>/<name> ... | --objective-file <path>] [--slug <slug>] [--target <key>] [--budget <n>] [--correct contradicts] [--specify]"
disable-model-invocation: true
effort: low
---

You compose one goal condition, arm it where the invocation says to, and stop. The condition is
short on purpose: it names the route, the authorization, the scope and one command, and states no
rule — «A goal condition names the route, the authorization, the scope and the invocation that
answers its state, and states no rule: the rules are those of the plugin version the invocation
pins.» (SPEC-008 R6). Every rule the run follows is in the skills of that version, and the command
decides when the goal is over.

This skill is closed to the model's invocation: only the person types it, so every argument it
receives is the person's own words — the scope, the objective, and the word to arm. That is the
gate R6 places here, and no other component runs `goal.py --arm`.

## Required inputs

A missing input is a stop, not a default:

1. **the project root** — where `siegard.json` lives. Named by the human; inferred rather than
   named, its absence is a stop.
2. **the scope** — the person's own words, one of four forms:
   - an **objective** in prose: what the system must come to do. It is handed to the script verbatim — never summarized, translated or completed — and the script writes it to a file the condition names by path and digest, because the ask `/deliver-scope` requires is the person's own words, and a paraphrase is an ask nobody made;
   - a **citation**: the person points at text already in this conversation — "parts 2 and 3
     above", "the scope you wrote" — and adopts it as theirs. Pointing is the person's act, and
     the text pointed at becomes the objective: copied character for character, as the
     conversation holds it, and handed to the script on stdin with `--objective-file -`, so no
     file but the one the script writes exists. A pointer that does not name one span of text without doubt — "the
     parts above" over a message holding several — is a stop that quotes each candidate and asks
     which. Where the text pointed at holds a part this route does not carry — a fact the
     specification does not state yet, which `/analyse` takes before any goal; an edit to the
     project's standard or to `siegard.json`, which are the person's own files — the copy is not
     cut to fit: it is a stop that names each such part, what carries it instead, and asks the
     person to point again at the parts the route carries;
   - **`--objective-file <path>`**, naming a file an earlier composition wrote under the
     telemetry root, as the invocation that report hands to paste names it: the objective is that
     file, named as it stands;
   - an **epic**, `epic/<name>`, of a live plan;
   - **tasks**, `task/<epic>/<name>`, of a live plan.
3. **the initiative's slug** — named by the human, `--slug <slug>`, or decided and disclosed: for
   an epic or tasks, the one live initiative under `work_root` whose plan holds them, where exactly
   one does; for an objective, a new kebab-case slug of at most five words taken from the
   objective's own terms, naming no directory under `work_root`.
4. **the target** — by the key `siegard.json`'s `targets` names it, `--target <key>`; where it
   declares exactly one, that key, decided and disclosed.

Two optional inputs, both the person's and never proposed here: **the budget**, `--budget <n>` —
how many judged doors the run may take, each only as the door decider returns it; none where the
person names none, so a choice no fact decides ends the run — and **the findings policy**,
`--correct contradicts` — which findings the run corrects by a corrective increment, once.
`contradicts` is the one kind a route corrects; the script refuses another, and the refusal is the
report.

A third, the person's alone and only over an objective: **to specify**, `--specify` —
`/deliver-scope` runs `/analyse` once over the objective before the plan, decides what the
specification does not state and commits it apart, and the person reviews that specification after
the goal rather than before. Where the objective changes a fact of the business — a status, a
refusal, what the system tells someone, who may see what — and the person has not asked for it,
the report says the goal will stop at the first fact the specification does not hold, and that
`--specify` is the person's to add; it is never added for them.

**To arm** is the invocation's first argument, `--arm`, and nothing else: the word in any other
place — inside an objective, after the scope, in a later message — arms nothing. A later message
asking to arm is answered with the invocation to paste that the composing report handed, never by
running `goal.py --arm`.

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
2. **Arm, where the invocation opens with `--arm` and the scope is no citation.** Run, from the
   project root:

   ```
   python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/goal.py --arm <project-root> --slug <slug> [--target <key>] (--scope <id> [--scope <id>]... | --objective "<the objective, verbatim>" | --objective-file <path>) [--budget <n>] [--correct contradicts] [--specify]
   ```

   The script runs every check composing runs and refuses where they refuse, refuses a project
   that already holds an armed goal, and records the condition for the plugin's `Stop` hook: «A
   goal the person arms through the framework ends on the state script's answer at the session's
   stop, never on a model's reading: `state A` or `state B` ends the goal and lets the session
   stop, `not yet` blocks the stop with the checks that failed, and a fourth consecutive `not yet`
   whose whole answer repeats the last ends the goal paused.» (SPEC-008 R14) Report, and end the
   turn: the stop that ends it is the hook's first answer, and the condition it repeats is the ask
   `/deliver-scope` runs under. A refusal is the report, with what resolves it.

   Over a citation, `--arm` composes and does not arm: what the person would arm is the text the
   script writes, and they read that file before an invocation naming it arms it. The report says
   so, and step 3 runs.
3. **Compose, otherwise:**

   ```
   python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/goal.py --compose <project-root> --slug <slug> [--target <key>] (--scope <id> [--scope <id>]... | --objective "<the objective, verbatim>" | --objective-file <path> | --objective-file - <<'OBJECTIVE' … the citation, verbatim … OBJECTIVE) [--budget <n>] [--correct contradicts] [--specify]
   ```

   The script checks what `/deliver-scope` would refuse before its first step — the
   specification, changes pending under the roots the route writes or in the trace and
   `siegard-reconcile/` it commits, a closed slug, an id the plan
   does not hold — and pins where `HEAD` stands, the plugin's version and every change already
   pending elsewhere, which the goal leaves untouched. A refusal is the report: every reason it
   printed, verbatim, each with what resolves it. Report, and stop.

## Report, and stop

«The state a handoff opens with is a script's line, never the session's» (SPEC-006 R10). Run
`python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/handoff.py --prepare --skill siegard-goal --project
<project-root> --slug <slug> --target <target> --language <en or pt-BR, the session's>`. It
prepares a report, which holds no decision and no line to paste: write the full report below
through `bin/handoff.py --save-report <path>`, to the path its `report` names, fill a short `body`
in the session's language — what the goal will do, in a person's words, carrying no flag, script
name or slug — and hand the person what `handoff.py --render` prints: the opening «A handoff opens with what needs the person, and explains after» (SPEC-006 R1) states. A refusal is answered by
rewriting the field it names; a state it says has moved, by running `--prepare` again and carrying
its `state` and `state_from` whole. Where the goal was armed in this invocation, the state
`--prepare` printed is the armed goal's own first line, and nothing follows the rendered handoff.

The full report says, in the session's own words, what the goal will do: carry the scope through
`/deliver-scope`, commit each step that skill defines, and end when the state command answers
`state A` or `state B`, both of which end it. Where the objective was a citation, the file the
script wrote, whole: what the person arms is that text, and they read it before they arm it. Then
what was decided rather than told — the slug, the target — and every line the script printed
under `checked:`, verbatim, and the condition it printed, whole and unedited.

Where the goal was composed and not armed, the rendered handoff is followed by the two ways to
arm it, none recommended: no rung of the ladder separates them. One line in the session's language
says why — both hold the same route, both can be ended, and no command printed a cost — and what
each assumes; the record `--prepare` made is a report, so that line hands no question. Then each
way in its own fenced block, whole, so that copying the block arms it — a fence is where a line
to paste belongs, and `handoff.py --check` reads no fence as prose:

- through the framework — the end is the state command's answer at every stop, and it assumes
  this session runs with this plugin's hooks: `/siegard:siegard-goal --arm <project-root> --slug
  <slug> --target <target>`, then the scope exactly as composing took it — `--scope <id>` for each
  id, or `--objective-file` naming the file the `objective:` line names, joined to the project
  root — and every `--budget`, `--correct` and `--specify` composing took;
- through the harness — it assumes nothing beyond the paste: `/goal ` and the condition the script
  printed, whole, because `/goal` with anything else, the objective alone among them, names no
  route and `/deliver-scope` refuses it.

Where the script refused, the report opens instead with each reason and what resolves it, ready
to paste where it is a command, and no condition. What resolves a reason is what the script
printed beside it, never a route described here: another entry point's requirements are stated
in its own file, and a summary of them written here is a second copy that drifts from it.

Nothing follows the two blocks. Never invite an edit of the objective after them: an objective the
person wants changed is a new invocation of this skill.

## What you never do

- Arm a goal but by step 2, under an invocation whose first argument is `--arm`; run
  `goal.py --arm` on a later message, a yes, or any word but that argument; paste `/goal` or this
  skill's invocation for the person; or run `/deliver-scope` — the condition becomes an ask only
  when the person pastes it or arms it.
- Edit, shorten or add to the condition the script printed: a rule written into it is a second
  copy of one a skill already holds, and the evaluator reads it as something to verify.
- Write, commit or change any file but the ones the script writes: the objective, verbatim, under
  the telemetry root, which the condition names by path and digest, and the armed record.
