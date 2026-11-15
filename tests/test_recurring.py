"""`deliver.py --recurring` reads back the rules a target's past reviews cite (SPEC-007 R6).

«A delivery's producers read first the rules of their target's standard that the target's past
reviews cite.» The count is read from review records alone, once per review, over the reviews of
the target named, and it orders what a producer reads first without deciding anything else.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "src/claude/bin/deliver.py"
STANDARD = REPO / "tests/fixtures/benchmarks/implement-task/project/app/standard.yaml"


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(SCRIPT), "--recurring", *args],
                          capture_output=True, text=True)


def review(root: Path, initiative: str, name: str, target: str, cites: list[str]) -> None:
    findings = [{"pass": "standard", "file": "lending/fees.py", "where": "line 1",
                 "evidence": "x", "cost": "y", "cites": rule} for rule in cites]
    findings.append({"pass": "conformance", "file": "lending/fees.py", "where": "line 2",
                     "evidence": "x", "cost": "y", "kind": "unstated"})
    front = {"target": target, "reviewed": ["lending/fees.py"], "findings": findings}
    path = root / initiative / "review" / f"{name}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("---\n" + yaml.safe_dump(front, sort_keys=False) + "---\n\nbody\n",
                    encoding="utf-8")


def statement(rule: str) -> str:
    rules = yaml.safe_load(STANDARD.read_text(encoding="utf-8"))["rules"]
    return " ".join(next(r for r in rules if r["id"] == rule)["statement"].split())


def test_each_rule_counts_once_per_review_most_cited_first_over_every_initiative(tmp_path):
    review(tmp_path, "lending", "one", "app", ["PY-01", "PY-01", "PY-02"])
    review(tmp_path, "lending", "two", "app", ["PY-02"])
    review(tmp_path, "catalog", "three", "app", ["PY-02"])
    done = run(str(tmp_path / "lending"), "app", str(STANDARD))
    assert done.returncode == 0, done.stderr
    assert done.stdout.splitlines() == [
        f"PY-02 — cited in 3 of 3 reviews of target app — {statement('PY-02')}",
        f"PY-01 — cited in 1 of 3 reviews of target app — {statement('PY-01')}",
    ]


def test_only_the_named_target_s_reviews_are_read(tmp_path):
    review(tmp_path, "lending", "one", "app", ["PY-01"])
    review(tmp_path, "lending", "two", "web", ["PY-02", "PY-02"])
    done = run(str(tmp_path / "lending"), "app", str(STANDARD))
    assert done.stdout.splitlines() == [
        f"PY-01 — cited in 1 of 1 reviews of target app — {statement('PY-01')}"]


def test_a_tie_is_ordered_by_identifier_and_a_rule_the_standard_lost_is_not_printed(tmp_path):
    review(tmp_path, "lending", "one", "app", ["PY-02", "PY-01", "XX-09"])
    done = run(str(tmp_path / "lending"), "app", str(STANDARD))
    assert [line.split(" — ")[0] for line in done.stdout.splitlines()] == ["PY-01", "PY-02"]


def test_nothing_is_printed_where_no_review_cites_a_rule(tmp_path):
    review(tmp_path, "lending", "one", "app", [])
    done = run(str(tmp_path / "lending"), "app", str(STANDARD))
    assert done.returncode == 0 and done.stdout == ""
    (tmp_path / "empty").mkdir()
    done = run(str(tmp_path / "empty"), "app", str(STANDARD))
    assert done.returncode == 0 and done.stdout == ""


def test_it_refuses_what_it_cannot_read(tmp_path):
    assert run(str(tmp_path / "absent"), "app", str(STANDARD)).returncode == 2
    assert run(str(tmp_path), "app", str(tmp_path / "absent.yaml")).returncode == 2
    assert run(str(tmp_path), "app").returncode == 2


def test_implement_task_hands_the_lines_to_both_producers():
    skill = (REPO / "src/claude/skills/implement-task/SKILL.md").read_text(encoding="utf-8")
    delegation = (REPO / "src/claude/skills/implement-task/references/delegation.md").read_text(
        encoding="utf-8")
    assert "`deliver.py --recurring <delivery-root> <target> <registry>`" in delegation
    assert delegation.count("recurring:") == 2
    assert "references/delegation.md" in skill
    for agent in ("task-implementer", "test-author"):
        text = (REPO / f"src/claude/agents/{agent}.md").read_text(encoding="utf-8")
        assert "- **recurring** — the standard's rules this target's reviews cite most" in text, agent
