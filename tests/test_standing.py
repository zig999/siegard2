"""`deliver.py --standing` reports the standard findings whose quoted source still stands (SPEC-007 R7).

«The standard findings of a target's past reviews whose quoted source still stands are a report,
never a verdict.» Each finding is held to the lines its evidence quotes: the review's commit must
have held them, and the file holding them still is what stands.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "src/claude/bin/deliver.py"

FEES = """def late_fee_cents(days_late):
    return days_late * 100


def renewal_limit():
    return 1
"""


def git(home: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(home), *args], check=True, capture_output=True)


def finding(file: str, rule: str, evidence: str, correction: str = "name it") -> dict:
    return {"pass": "standard", "file": file, "where": "line 2", "evidence": evidence,
            "cost": "the next reader guesses", "correction": correction, "cites": rule}


def review(home: Path, initiative: str, name: str, target: str, findings: list[dict]) -> None:
    front = {"target": target, "reviewed": ["lending/fees.py"], "findings": findings}
    path = home / "delivery" / initiative / "review" / f"{name}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("---\n" + yaml.safe_dump(front, sort_keys=False) + "---\n\nbody\n",
                    encoding="utf-8")


def project(tmp_path: Path, findings: list[dict], target: str = "app") -> Path:
    home = tmp_path / "project"
    (home / "app/lending").mkdir(parents=True)
    (home / "app/lending/fees.py").write_text(FEES, encoding="utf-8")
    (home / "app/lending/gone.py").write_text("    return 'a removed literal value'\n",
                                              encoding="utf-8")
    review(home, "lending", "first", target, findings)
    git(home, "init", "-q")
    git(home, "add", "--", ".")
    git(home, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "seed")
    return home


def run(home: Path, *extra: str, target: str = "app") -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(SCRIPT), "--standing",
                           str(home / "delivery/lending"), target, str(home / "app"), *extra],
                          capture_output=True, text=True)


FOUR = [
    finding("lending/fees.py", "TYP-04", "    return days_late * 100", "a named cent constant"),
    finding("lending/fees.py", "MNT-03", "def renewal_limit():\n    return 1"),
    finding("lending/gone.py", "TYP-04", "    return 'a removed literal value'"),
    finding("lending/fees.py", "TYP-04", "x = 1 [...] y"),
]


def test_each_finding_is_counted_by_what_its_quoted_lines_say_now(tmp_path):
    home = project(tmp_path, FOUR)
    (home / "app/lending/fees.py").write_text(FEES.replace("def renewal_limit():",
                                                           "def renewal_limit_of(loan):"),
                                              encoding="utf-8")
    (home / "app/lending/gone.py").unlink()
    done = run(home)
    assert done.returncode == 0, done.stderr
    lines = done.stdout.splitlines()
    assert lines[0] == ("standing: 1 finding(s) of target app stand in 1 file(s); 1 changed since, "
                        "1 in files since removed, 1 not decidable from their evidence — over 1 "
                        "review(s)")
    assert lines[1] == "- lending/fees.py — TYP-04 (1 finding(s))"
    assert lines[2] == "    TYP-04 (first): return days_late * 100 → a named cent constant"
    assert len(lines) == 3


def test_a_quoted_line_the_review_s_commit_did_not_hold_is_not_decidable(tmp_path):
    home = project(tmp_path, [finding("lending/fees.py", "TYP-04", "    return a paraphrase of it")])
    assert run(home).stdout.splitlines()[0].endswith(
        "1 not decidable from their evidence — over 1 review(s)")


def test_one_finding_two_reviews_recorded_is_one(tmp_path):
    home = project(tmp_path, FOUR[:1])
    review(home, "catalog", "second", "app", FOUR[:1])
    git(home, "add", "--", ".")
    git(home, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "second")
    assert run(home).stdout.startswith("standing: 1 finding(s) of target app stand in 1 file(s);")
    assert "over 2 review(s)" in run(home).stdout.splitlines()[0]


def test_files_are_grouped_most_findings_first_and_narrowed_by_rule_and_file(tmp_path):
    home = project(tmp_path, FOUR[:3])
    lines = run(home).stdout.splitlines()
    assert lines[1] == "- lending/fees.py — MNT-03, TYP-04 (2 finding(s))"
    assert [line for line in lines if line.startswith("- ")][1] == \
        "- lending/gone.py — TYP-04 (1 finding(s))"
    narrowed = run(home, "--rule", "MNT-03").stdout.splitlines()
    assert narrowed[0].startswith("standing: 1 finding(s)") and len(narrowed) == 3
    narrowed = run(home, "--file", "lending/gone.py").stdout.splitlines()
    assert narrowed[1] == "- lending/gone.py — TYP-04 (1 finding(s))" and len(narrowed) == 3


def test_only_the_named_target_s_reviews_are_read(tmp_path):
    home = project(tmp_path, FOUR[:1], target="web")
    assert run(home).stdout.splitlines() == [
        "standing: 0 finding(s) of target app stand in 0 file(s); 0 changed since, 0 in files "
        "since removed, 0 not decidable from their evidence — over 0 review(s)"]


def test_it_refuses_only_what_it_cannot_read(tmp_path):
    home = project(tmp_path, FOUR)
    bad = subprocess.run([sys.executable, "-B", str(SCRIPT), "--standing", str(tmp_path / "x"),
                          "app", str(home / "app")], capture_output=True, text=True)
    assert bad.returncode == 2
    short = subprocess.run([sys.executable, "-B", str(SCRIPT), "--standing",
                            str(home / "delivery/lending"), "app"], capture_output=True, text=True)
    assert short.returncode == 2
