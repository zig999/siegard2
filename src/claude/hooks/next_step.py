#!/usr/bin/env python3
"""Places one line of context beside a person's message that asks what comes next, in a Siegard
project.

The harness runs this on `UserPromptSubmit`, as `hooks/hooks.json` declares. «Where a person's
message in a project that declares `siegard.json` asks what comes next, the plugin's
`UserPromptSubmit` hook places one line of context beside it» (SPEC-008 R20): the answer is given
by `/siegard-status`, whose close a standing grant answers as it answers a stop, and the person is
handed what `bin/handoff.py --render` prints. The line reaches the turn in which the question is
asked, where an instruction placed at the session's start is far behind.

A message asks what comes next where a clause of it that is a question carries one of `PHRASES`,
data in each language the handoff record admits, matched without case or accents; a message that
opens with a slash command or with a word of going ahead hands the step and gains nothing. Reads the harness's event record on stdin
for the prompt and the working directory, and prints one JSON object whose `additionalContext` is
`LINE`. It never blocks a message: every path out exits 0, and every failure — a project it cannot
resolve, a record it cannot read — prints nothing.
"""
from __future__ import annotations

import json
import re
import sys
import unicodedata
from pathlib import Path

HOOKS = Path(__file__).resolve().parent
EVENT = "UserPromptSubmit"
GIT_TIMEOUT_SECONDS = 10
PHRASES = {
    "pt-BR": ("e agora", "e ai", "e depois", "qual caminho", "qual o caminho", "proximo passo",
              "proximos passos", "qual a proxima", "qual o proximo", "qual recomenda",
              "qual voce recomenda", "qual vc recomenda", "o que voce recomenda",
              "o que recomenda", "qual a recomendacao", "o que fazer agora", "oq fazer"),
    "en": ("what now", "what next", "whats next", "next step", "next steps", "which way",
           "what do you recommend"),
}
GO_WORDS = ("sim", "siga", "segue", "seguir", "pode", "vai", "faca", "rode", "continue",
            "continua", "prossiga", "yes", "go", "proceed", "do")
LINE = ("The person asks what comes next: answer by invoking /siegard-status and hand them what "
        "`bin/handoff.py --render` prints, never a free-text answer.")


def plain(text: str) -> str:
    folded = unicodedata.normalize("NFKD", text.casefold())
    return re.sub(r"\s+", " ", "".join(c for c in folded if not unicodedata.combining(c)))


def asks_what_next(prompt: str) -> bool:
    """Whether a message asks what comes next: a phrase of `PHRASES` inside a clause that is a
    question, or a clause that is the phrase alone; never a message that opens with a slash
    command or a word of going ahead, which hands the next step rather than asking it."""
    text = plain(prompt).replace("'", "").replace(",", " ")
    first = re.match(r"\s*(\S+)", text)
    if text.lstrip().startswith("/") or (first and first.group(1).strip("!.?:") in GO_WORDS):
        return False
    phrases = [phrase for language in PHRASES.values() for phrase in language]
    for clause in re.split(r"[.!;\n]+", text):
        bare = clause.strip(" ?")
        for phrase in phrases:
            if re.search(r"(?<!\w)" + re.escape(phrase) + r"(?!\w)", clause) \
                    and ("?" in clause or bare == phrase):
                return True
    return False


def in_a_siegard_project(record: dict) -> bool:
    where = record.get("cwd")
    try:
        start = Path(where) if isinstance(where, str) and where else Path.cwd()
        if not start.is_dir():
            return False
        sys.path.insert(0, str(HOOKS.parent / "bin"))
        from project import PROJECT_FILE, toplevel_of
        return (toplevel_of(start, timeout=GIT_TIMEOUT_SECONDS) / PROJECT_FILE).is_file()
    except (Exception, SystemExit):
        return False


def main() -> int:
    try:
        record = json.loads(sys.stdin.buffer.read().decode("utf-8", "replace") or "{}")
    except json.JSONDecodeError:
        return 0
    if not isinstance(record, dict) or not isinstance(record.get("prompt"), str):
        return 0
    if not asks_what_next(record["prompt"]) or not in_a_siegard_project(record):
        return 0
    print(json.dumps({"hookSpecificOutput": {"hookEventName": EVENT, "additionalContext": LINE}}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
