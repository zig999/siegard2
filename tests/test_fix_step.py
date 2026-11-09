"""A registry's `fix` step: the form a check holds, written by the run and never by hand.

«A step whose role is `fix` rewrites the tree into the form the registry's checks hold: a delivery
runs every such step after the install and before every check, in its build and its suite alike,
and owes it as it owes a check; it runs neither at setup nor in a review's or a reconciliation's
run, it decides no rule, and a file it changes is held to the delivery's records like any other
the delivery wrote.» (SPEC-007 R5)

The case this holds against, read on 2026-11-09: a delivery's producers hold no shell, so a
format check red on a file they wrote went back to them to reformat by hand — configurator ended a
run `gave-up` after three suites on one test file, partymgmt after three builds on one source file.
The end-to-end tests below run `bin/run.py` and `deliver.py --unrecorded` as a delivery does, over
a stand-in formatter whose check fails on a line with trailing spaces and whose fix strips them.
"""
from __future__ import annotations

import json
import shlex
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

import deliver

REPO = Path(__file__).resolve().parent.parent
BIN = REPO / "src/claude/bin"
CHECK = (f"{shlex.quote(sys.executable)} -c \"import pathlib,sys; "
         f"bad=[p for p in pathlib.Path('src').rglob('*.ts') if ' \\n' in p.read_text()]; "
         f"print(*bad); sys.exit(1 if bad else 0)\"")
FIX = (f"{shlex.quote(sys.executable)} -c \"import pathlib; "
       f"[p.write_text(p.read_text().replace(' \\n', '\\n')) "
       f"for p in pathlib.Path('src').rglob('*.ts') if ' \\n' in p.read_text()]\"")


def registry(fix: bool = True) -> dict:
    commands = [{"step": "install", "command": "true", "timeout_seconds": 60, "role": "install"}]
    if fix:
        commands.append({"step": "format-fix", "command": FIX, "timeout_seconds": 60,
                         "role": "fix"})
    commands += [{"step": "format", "command": CHECK, "timeout_seconds": 60},
                 {"step": "test", "command": "true", "timeout_seconds": 60, "role": "suite"}]
    return {"contract_version": "siegard-standard/1", "standard": "fixture",
            "summary": "A stand-in formatter and its check.",
            "rules": [{"id": "FMT-01", "statement": "Source carries no trailing spaces.",
                       "because": "A diff of whitespace hides the change it rides on.",
                       "decided_by": "tool", "tool": "format",
                       "applies_to": [{"under": "src", "suffix": ".ts", "nested": True}]}],
            "commands": commands}


def git(home: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(home), "-c", "user.email=t@t", "-c", "user.name=t", *args],
                   check=True, capture_output=True)


@pytest.fixture
def project(tmp_path: Path) -> Path:
    """A consumer whose target is formatted at `HEAD`, as both measured consumers' were."""
    home = tmp_path / "consumer"
    (home / "app" / "src").mkdir(parents=True)
    (home / "app" / "src" / "kept.ts").write_text("export const kept = 1;\n", encoding="utf-8")
    (home / "siegard.json").write_text(json.dumps(
        {"specification_root": "spec", "work_root": "work", "delivery_root": "delivery",
         "telemetry_root": "telemetry", "targets": {"app": "app"}}), encoding="utf-8")
    git(home, "init", "-q")
    git(home, "add", "-A")
    git(home, "commit", "-qm", "base")
    (home / "delivery" / "s").mkdir(parents=True)
    return home


def phase(data: dict, name: str) -> list[str]:
    return [c["step"] for c in deliver.phase_steps(data["commands"], name)]


def build_line(data: dict) -> list[str]:
    """The `--step` arguments of the build line `deliver.py --standard` prints."""
    return [arg for c in deliver.phase_steps(data["commands"], "build")
            for arg in ("--step", f"{c['step']}={c['command']}")]


def run(home: Path, name: str, data: dict) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(BIN / "run.py"), str(home / "delivery" / "s"),
                           "--run", name, "--cwd", str(home / "app"), "--timeout-seconds", "60",
                           *build_line(data)], capture_output=True, text=True)


def unrecorded(home: Path, files: list[str]) -> subprocess.CompletedProcess:
    record = home / "delivery" / "s" / "implementation" / "e" / "t.md"
    record.parent.mkdir(parents=True, exist_ok=True)
    front = {"target": "app", "files": [{"path": p, "effect": "written"} for p in files]}
    record.write_text(f"---\n{yaml.safe_dump(front)}---\n## What it is\nProse.\n",
                      encoding="utf-8")
    return subprocess.run([sys.executable, "-B", str(BIN / "deliver.py"), "--unrecorded",
                           str(home / "app"), str(record)], capture_output=True, text=True)


def test_the_fix_step_runs_after_the_install_and_before_every_check_and_never_in_a_review():
    data = registry()
    assert phase(data, "setup") == ["install"]
    assert phase(data, "build") == ["install", "format-fix", "format"]
    assert phase(data, "suite") == ["install", "format-fix", "format", "test"]
    assert phase(data, "review") == ["install", "format", "test"]


def test_the_standard_prints_where_the_fix_runs(tmp_path):
    path = tmp_path / "standard.yaml"
    path.write_text(yaml.safe_dump(registry(), sort_keys=False), encoding="utf-8")
    done = subprocess.run([sys.executable, "-B", str(BIN / "deliver.py"), "--standard", str(path)],
                          capture_output=True, text=True)
    assert done.returncode == 0, done.stdout + done.stderr
    lines = {line.split(":", 1)[0].strip(): line for line in done.stdout.splitlines()
             if line.strip().startswith(("setup:", "build:", "suite:", "review:"))}
    assert "format-fix=" in lines["build"] and "format-fix=" in lines["suite"]
    assert "format-fix=" not in lines["setup"] and "format-fix=" not in lines["review"]
    assert lines["build"].index("install=") < lines["build"].index("format-fix=") \
        < lines["build"].index("format=")
    assert "fixes with format-fix" in done.stdout


def test_several_steps_may_carry_fix_and_none_decides_a_rule(tmp_path):
    data = registry()
    data["commands"].insert(2, {"step": "lint-fix", "command": "true", "timeout_seconds": 60,
                                "role": "fix"})
    path = tmp_path / "two.yaml"
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    from jsonschema import Draft202012Validator
    validator = Draft202012Validator(json.loads(
        (REPO / "src/claude/schemas/standard.json").read_text(encoding="utf-8")))
    loaded, problems = deliver.load_standard(path, validator)
    assert problems == [] and loaded is not None, problems
    data["rules"][0]["tool"] = "format-fix"
    deciding = tmp_path / "deciding.yaml"
    deciding.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    loaded, problems = deliver.load_standard(deciding, validator)
    assert loaded is None
    assert any("that step's role is `fix`" in p for p in problems), problems


def test_a_file_the_producer_left_unformatted_passes_the_build_the_fix_runs(project):
    """The configurator and partymgmt shape: a delivered file the check refuses. Without a `fix`
    step the build is red at the check and only a producer reformatting by hand answers it; with
    one, the same run rewrites the file and the check passes, and the record naming the file is
    all `--unrecorded` asks."""
    (project / "app" / "src" / "written.ts").write_text("export const a = 1; \n",
                                                        encoding="utf-8")
    without = run(project, "e-t-build", registry(fix=False))
    assert without.returncode != 0, "the check refuses the trailing space"
    done = run(project, "e-t-build-2", registry())
    assert done.returncode == 0, done.stdout + done.stderr
    assert (project / "app" / "src" / "written.ts").read_text(encoding="utf-8") == \
        "export const a = 1;\n"
    held = unrecorded(project, ["src/written.ts"])
    assert held.returncode == 0, held.stdout + held.stderr


def test_a_fix_that_rewrote_a_file_no_record_names_is_refused(project):
    """«a file it changes is held to the delivery's records like any other the delivery wrote»
    (SPEC-007 R5): a target not formatted at `HEAD` is rewritten beyond the delivery, and the
    tree check names what nobody recorded."""
    (project / "app" / "src" / "kept.ts").write_text("export const kept = 1; \n", encoding="utf-8")
    git(project, "commit", "-qam", "an unformatted commit")
    (project / "app" / "src" / "written.ts").write_text("export const a = 1;\n", encoding="utf-8")
    done = run(project, "e-t-build", registry())
    assert done.returncode == 0, done.stdout + done.stderr
    held = unrecorded(project, ["src/written.ts"])
    assert held.returncode == 1
    assert "unrecorded: src/kept.ts" in held.stdout


def flat(path: str) -> str:
    return " ".join((REPO / path).read_text(encoding="utf-8").split())


def test_the_skills_run_the_fix_where_the_specification_says_and_nowhere_else():
    """The review composes its own run from the registry's listing, so its text is what keeps a
    `fix` out of it; the registry's author is told the role exists; and the delivery that meets a
    check red with no `fix` declared says which step would have answered it."""
    review = flat("src/claude/skills/review-change/SKILL.md")
    assert "every step the standard declares but a `fix`" in review
    assert "`review:` line" in review
    standard = flat("src/claude/skills/siegard-standard/SKILL.md")
    assert "as a step whose `role` is `fix`, and never as a rule's `tool`" in standard
    red = flat("src/claude/skills/implement-task/references/red-build.md")
    assert "A form a `fix` step could write is never sent back by hand" in red
