---
name: siegard-goal
description: Use when a person wants one scope — an objective in prose, an epic, or a set of tasks of a live plan — carried end to end with nobody asked anything along the way. Composes the condition of a Claude Code goal that drives /deliver-scope over that scope, after checking everything the route would refuse before its first step, and prints it for the person to paste after /goal. The goal it composes ends when a script reads state A (delivered, proven, reviewed, measured) or state B (stopped where only a person moves it) from disk, so it always ends. It writes only the objective, verbatim, to a file the condition names, and arms a goal only on the person's own word to arm it — then through the framework, whose Stop hook answers each stop from the state script — or leaves the condition for the person to paste after /goal; either is the person's act and the authorization the route needs. Not for delivering anything now (that is /deliver-scope), and not for watching a run (that is /siegard-progress).
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
   - an **objective** in prose: what the system must come to do. It is handed to the script verbatim — never summarized, translated or completed — and the script writes it to a file the condition names by path and digest, because the ask `/deliver-scope` requires is the person's own words, and a paraphrase is an ask nobody made;
      - a **citation**: the person points at text already in this conversation — "parts 2 and 3
     above", "the scope you wrote" — and adopts it as theirs. Pointing is the person's act, and
     the text pointed at becomes the objective: copied character for character, as the
     conversation holds it, into a file of its own, and handed to the script with
     `--objective-file`. A pointer that does not name one span of text without doubt — "the
     parts above" over a message holding several — is a stop that quotes each candidate and asks
     which. Where the text pointed at holds a part this route does not carry — a fact the
     specification does not state yet, which `/analyse` takes before any goal; an edit to the
     project's standard or to `siegard.json`, which are the person's own files — the copy is not
     cut to fit: it is a stop that names each such part, what carries it instead, and asks the
     person to point again at the parts the route carries;
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

A third, the person's alone and only over an objective: **to specify** — `/deliver-scope` runs
`/analyse` once over the objective before the plan, decides what the specification does not state
and commits it apart, and the person reviews that specification after the goal rather than
before. Where the objective changes a fact of the business — a status, a refusal, what the system
tells someone, who may see what — and the person has not asked for it, the report says the goal
will stop at the first fact the specification does not hold, and that `--specify` is the
person's to add; it is never added for them.

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
   python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/goal.py --compose <project-root> --slug <slug> [--target <key>] (--scope <id> [--scope <id>]... | --objective "<the objective, verbatim>" | --objective-file <the citation's copy>) [--budget <n>] [--correct contradicts] [--specify]
   ```

   The script checks what `/deliver-scope` would refuse before its first step — the
   specification, changes pending under the roots the route writes or in the trace and
   `siegard-reconcile/` it commits, a closed slug, an id the plan
   does not hold — and pins where `HEAD` stands, the plugin's version and every change already
   pending elsewhere, which the goal leaves untouched. A refusal is the report: every reason it
   printed, verbatim, each with what resolves it.
3. Report, and stop.
4. **Arm, only on the person's own word.** Where a later message of the person's says, in their
   own words, to arm this goal through the framework — not a paste of `/goal`, not a yes to
   something else — run, with exactly the arguments step 2 ran, and, for an objective, with
   `--objective-file` naming the file step 2 wrote:

   ```
   python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/goal.py --arm <project-root> --slug <slug> [--target <key>] (--scope <id> [--scope <id>]... | --objective-file <the file step 2 wrote>) [--budget <n>] [--correct contradicts] [--specify]
   ```

   The script runs every check step 2 ran again, refuses a project that already holds an armed
   goal, and records the condition for the plugin's `Stop` hook: «A goal the person arms through
   the framework ends on the state script's answer at the session's stop, never on a model's
   reading: `state A` or `state B` ends the goal and lets the session stop, `not yet` blocks the
   stop with the checks that failed, and a fourth consecutive `not yet` whose whole answer
   repeats the last ends the goal paused.» (SPEC-008 R14) Report what it printed, verbatim, and
   end the turn: the stop that ends it is the hook's first answer, and the condition it repeats
   is the ask `/deliver-scope` runs under. A refusal is the report, with what resolves it.

## Report, and stop

Open as «A handoff opens with what needs the person, and explains after» (SPEC-006 R1) states.
The one decision is the person's: whether to arm the goal, and how — recommended, by judgment
because the two hold the same route, through the framework: they say so in their own words and
step 4 runs, and the end is the state command's answer at every stop rather than an evaluator's
reading of the session; or through the harness, by pasting the block that closes this report —
whole, because `/goal` with anything else, the objective alone among them, names no route and
`/deliver-scope` refuses it. What would change it: a project whose sessions run without this
plugin's hooks, where only the harness's goal answers a stop. Then, in the session's own words,
what the goal will do:
carry the scope through `/deliver-scope`, commit each step that skill defines, and end when the
state command answers `state A` or `state B`, both of which end it. Where the objective was a
citation, the file the script wrote, whole: what the person arms is that text, and they read it
before they paste. Then what was decided rather than told — the slug, the target — and every line
the script printed under `checked:`, verbatim. Last, the condition the script printed, whole and
unedited, in one fenced block preceded by `/goal `, so that copying the block arms it.

Where the script refused, the report opens instead with each reason and what resolves it, ready
to paste where it is a command, and no condition. What resolves a reason is what the script
printed beside it, never a route described here: another entry point's requirements are stated
in its own file, and a summary of them written here is a second copy that drifts from it.

Nothing follows the block. Never invite an edit of the objective after it: an objective the
person wants changed is a new invocation of this skill.

## What you never do

- Arm a goal but by step 4, on the person's own word to arm it; paste `/goal` for them; or run
  `/deliver-scope` — the condition becomes an ask only when the person pastes it or says to arm
  it.
- Edit, shorten or add to the condition the script printed: a rule written into it is a second
  copy of one a skill already holds, and the evaluator reads it as something to verify.
- Write, commit or change any file but the ones the script writes: the objective, verbatim, under
  the telemetry root, which the condition names by path and digest, and the armed record.
