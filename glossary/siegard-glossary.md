# Siegard glossary

A plain-language guide to the words Siegard uses: what each one means, where you meet it, and
what it looks like on disk or on the command line.

It describes Siegard **4.21.3**. Where this page and a skill's `SKILL.md`, a script's `--help`
or a schema under `schemas/` disagree, those files win: they are what actually runs. This page
explains them; it does not replace them.

---

## How to use this page

- **Section 1** is the one-minute picture. Read it first; every other term hangs off it.
- **Sections 2–9** group the terms by the moment you meet them: setting up a project, writing the
  specification, planning, delivering, reviewing, the trace, reconciliation, and the helper
  commands.
- **Section 10** lists every agent (the "judges" and "producers" Siegard delegates to).
- **Section 11** translates informal words people use in conversation (`unfold`, `refold`,
  `certificate`, "comment findings", "emitted-text findings") into the official terms.
- **Section 12** walks through one complete example, a hand-made fix, from start to finish.
- **Section 13** is an alphabetical index pointing back to each entry.

Commands are written the way the skills run them:

```sh
python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/<script>.py ...
```

`${CLAUDE_PLUGIN_ROOT}` is the folder where the Siegard plugin is installed (it holds `bin/`,
`schemas/`, `skills/`, `agents/` and `hooks/`). To keep things short, this page writes
`trace.py ...` where the full form is `python3 -B ${CLAUDE_PLUGIN_ROOT}/bin/trace.py ...`.

---

## Chapters

1. [The one-minute picture](siegard-glossary/01-the-one-minute-picture.md)
2. [Setting up a project](siegard-glossary/02-setting-up-a-project.md)
3. [The specification](siegard-glossary/03-the-specification.md)
4. [Planning (`/plan-work`)](siegard-glossary/04-planning.md)
5. [Delivering (`/implement-task`, `/deliver-scope`)](siegard-glossary/05-delivering.md)
6. [Reviewing (`/review-change`)](siegard-glossary/06-reviewing.md)
7. [The trace](siegard-glossary/07-the-trace.md)
8. [Reconciliation (`/reconcile`)](siegard-glossary/08-reconciliation.md)
9. [The other skills and helper scripts](siegard-glossary/09-the-other-skills-and-helper-scripts.md)
10. [The agents](siegard-glossary/10-the-agents.md)
11. [Informal words you may meet](siegard-glossary/11-informal-words-you-may-meet.md)
12. [One complete example: a hand fix](siegard-glossary/12-one-complete-example-a-hand-fix.md)
13. [Alphabetical index](siegard-glossary/13-alphabetical-index.md)

Each chapter is a file in `glossary/siegard-glossary/`. The section numbers (§) cited in the text are the chapters’ numbers.
