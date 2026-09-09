"""`tools/migrate_delivery_targets.py`: the one-time rewrite a consumer runs across the 4.0.0
major, held to what it promises — derive the key, stamp it textually, respell a standard spelled
from the wrong root, re-pin the proofs whose implementation it rewrote, touch nothing while any
record is undecided, and do nothing the second time.

The fixture is `tests/fixtures/backend-baseline`, un-migrated by hand: its records carry `target`
because the script already ran over them once, so the test strips the line, re-pins the proof to
the stripped implementation and hands the script exactly what a 3.x consumer holds."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "tools/migrate_delivery_targets.py"
DELIVER = REPO / "src/claude/bin/deliver.py"
BASELINE = REPO / "tests/fixtures/backend-baseline"

IMPLEMENTATION = "delivery/troubleshooting/implementation/troubleshooting/record-case.md"
PROOF = "delivery/troubleshooting/proof/troubleshooting/record-case.md"
REVIEW = "delivery/troubleshooting/review/first.md"


def run(*args: str | Path) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(SCRIPT), *map(str, args)],
                          capture_output=True, text=True)


def pin_of(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def set_pin(proof: Path, pin: str, quoted: bool = False) -> None:
    text = proof.read_text(encoding="utf-8")
    value = f'"{pin}"' if quoted else pin
    text, count = re.subn(r"^implementation: .*$", f"implementation: {value}", text,
                          count=1, flags=re.M)
    assert count == 1
    proof.write_text(text, encoding="utf-8")


def strip_target(path: Path) -> None:
    lines = path.read_text(encoding="utf-8").split("\n")
    assert lines[1].startswith("target: "), f"{path} carries no target line to strip"
    del lines[1]
    path.write_text("\n".join(lines), encoding="utf-8")


def digests(home: Path) -> dict[str, str]:
    return {p.relative_to(home).as_posix(): pin_of(p)
            for p in sorted(home.rglob("*")) if p.is_file() and ".git" not in p.parts}


@pytest.fixture
def home(tmp_path: Path) -> Path:
    """The baseline consumer as a 3.x install held it: no `target` on any record, every proof pin
    current, and under git so deliver.py finds the project file at the toplevel."""
    where = tmp_path / "consumer"
    shutil.copytree(BASELINE, where)
    for name in (IMPLEMENTATION, PROOF, REVIEW):
        strip_target(where / name)
    set_pin(where / PROOF, pin_of(where / IMPLEMENTATION))
    subprocess.run(["git", "init", "-q", str(where)], check=True, capture_output=True)
    return where


def test_a_dry_run_reports_and_writes_nothing(home):
    before = digests(home)
    done = run(home)
    assert done.returncode == 0, done.stdout + done.stderr
    assert "3 record(s) that would be stamped (3 by files" in done.stdout
    assert "dry run; pass --write to apply" in done.stdout
    assert digests(home) == before


def test_write_stamps_every_record_and_repins_the_proof(home):
    done = run(home, "--write")
    assert done.returncode == 0, done.stdout + done.stderr
    assert "stamped 3 record(s); re-pinned 1 proof(s)" in done.stdout
    for name in (IMPLEMENTATION, PROOF, REVIEW):
        assert (home / name).read_text(encoding="utf-8").startswith("---\ntarget: backend\n")
    proof = (home / PROOF).read_text(encoding="utf-8")
    assert f"implementation: {pin_of(home / IMPLEMENTATION)}" in proof


def test_the_migrated_delivery_validates_and_its_index_is_untouched(home):
    index = (home / "delivery/troubleshooting/delivery.json").read_bytes()
    assert run(home, "--write").returncode == 0
    checked = subprocess.run(
        [sys.executable, "-B", str(DELIVER), "--check", home / "delivery/troubleshooting",
         home / "work/troubleshooting", home / "backend", home / "specification"],
        capture_output=True, text=True)
    assert checked.returncode == 0, checked.stdout + checked.stderr
    assert (home / "delivery/troubleshooting/delivery.json").read_bytes() == index


def test_running_twice_is_running_once(home):
    assert run(home, "--write").returncode == 0
    after_first = digests(home)
    again = run(home, "--write")
    assert again.returncode == 0, again.stdout + again.stderr
    assert "3 already carry target" in again.stdout
    assert "nothing to do" in again.stdout
    assert digests(home) == after_first


def test_a_quoted_pin_is_repinned_with_its_quotes(home):
    set_pin(home / PROOF, pin_of(home / IMPLEMENTATION), quoted=True)
    done = run(home, "--write")
    assert done.returncode == 0, done.stdout + done.stderr
    assert "re-pinned 1 proof(s)" in done.stdout
    proof = (home / PROOF).read_text(encoding="utf-8")
    assert f'implementation: "{pin_of(home / IMPLEMENTATION)}"' in proof


def test_a_pin_already_stale_stops_the_whole_run_and_writes_nothing(home):
    """A stale pin is a pre-existing defect this run did not cause; it is caught before any file
    is touched, exactly like an undecided record, and the run writes nothing at all."""
    stale = "sha256:" + "0" * 64
    before = digests(home)
    set_pin(home / PROOF, stale)
    before[PROOF] = pin_of(home / PROOF)
    done = run(home, "--write")
    assert done.returncode == 1, done.stdout + done.stderr
    assert f"STALE {PROOF}: pinned {stale}" in done.stdout
    assert "nothing written" in done.stdout
    assert digests(home) == before


def test_a_dry_run_reports_a_pin_already_stale_before_any_write(home):
    """The staleness is a fact of the unmigrated tree, readable without writing anything — a dry
    run says so exactly as `--write` would, per the docstring's own promise."""
    stale = "sha256:" + "0" * 64
    before = digests(home)
    set_pin(home / PROOF, stale)
    before[PROOF] = pin_of(home / PROOF)
    done = run(home)
    assert done.returncode == 1, done.stdout + done.stderr
    assert f"STALE {PROOF}: pinned {stale}" in done.stdout
    assert digests(home) == before


def test_a_standard_spelled_from_another_root_is_respelled_from_the_files_root(home):
    """A record whose files stand under `web` and whose standard resolves only under `backend`
    was written from the wrong root; the files decide, and the standard is respelled from `web`."""
    declared = json.loads((home / "siegard.json").read_text(encoding="utf-8"))
    declared["targets"]["web"] = "web"
    (home / "siegard.json").write_text(json.dumps(declared), encoding="utf-8")
    (home / "web/src").mkdir(parents=True)
    (home / "web/src/page.ts").write_text("export {}\n", encoding="utf-8")
    text = (home / IMPLEMENTATION).read_text(encoding="utf-8")
    assert "- path: src/troubleshooting/case.ts" in text and "\nstandard:" not in text
    text = text.replace("- path: src/troubleshooting/case.ts", "- path: src/page.ts")
    text = text.replace("\nfiles:\n", f"\nstandard:\n  at: standard.yaml\n"
                                    f"  pin: {pin_of(home / 'backend/standard.yaml')}\nfiles:\n", 1)
    assert "  at: standard.yaml" in text
    (home / IMPLEMENTATION).write_text(text, encoding="utf-8")
    set_pin(home / PROOF, pin_of(home / IMPLEMENTATION))
    done = run(home, "--write")
    assert done.returncode == 0, done.stdout + done.stderr
    assert (f"respell {IMPLEMENTATION}: standard.at standard.yaml -> ../backend/standard.yaml "
            f"(files stand under web)") in done.stdout
    migrated = (home / IMPLEMENTATION).read_text(encoding="utf-8")
    assert migrated.startswith("---\ntarget: web\n")
    assert "  at: ../backend/standard.yaml" in migrated


def test_an_undecided_record_stops_every_write(home):
    """One record nothing decides — paths under no root, no standard, no decided sibling in its
    own delivery root — and the whole run writes nothing, naming it."""
    lonely = home / "delivery/lonely/implementation/lonely/nowhere.md"
    lonely.parent.mkdir(parents=True)
    lonely.write_text("---\ntitle: Nowhere\nsummary: Files under no root.\n"
                      "files:\n- path: elsewhere/thing.ts\n  effect: none\n---\n"
                      "## What it is\nNone.\n## Notes\nNone.\n", encoding="utf-8")
    before = digests(home)
    done = run(home, "--write")
    assert done.returncode == 1, done.stdout + done.stderr
    assert "1 undecided" in done.stdout
    assert "UNDECIDED delivery/lonely/implementation/lonely/nowhere.md" in done.stdout
    assert "nothing written" in done.stdout
    assert digests(home) == before


def test_a_record_with_no_surviving_path_takes_its_siblings_key(home):
    """The files of an old record may be gone; the delivery root it sits in still says where."""
    text = (home / REVIEW).read_text(encoding="utf-8")
    text = text.replace("- src/troubleshooting/case.ts", "- src/troubleshooting/gone.ts")
    text = re.sub(r"(?ms)^standard:\n(?:  .*\n)+", "", text)
    (home / REVIEW).write_text(text, encoding="utf-8")
    done = run(home, "--write")
    assert done.returncode == 0, done.stdout + done.stderr
    assert "1 by siblings" in done.stdout
    assert (home / REVIEW).read_text(encoding="utf-8").startswith("---\ntarget: backend\n")


def test_a_record_takes_its_key_from_a_sibling_already_migrated(home):
    """A root migrated in two passes — one record already carrying `target` by hand, one still
    undecided — is exactly the state the UNDECIDED message's own remedy produces."""
    lines = (home / PROOF).read_text(encoding="utf-8").split("\n")
    lines.insert(1, "target: backend")
    (home / PROOF).write_text("\n".join(lines), encoding="utf-8")
    text = (home / REVIEW).read_text(encoding="utf-8")
    text = text.replace("- src/troubleshooting/case.ts", "- src/troubleshooting/gone.ts")
    text = re.sub(r"(?ms)^standard:\n(?:  .*\n)+", "", text)
    (home / REVIEW).write_text(text, encoding="utf-8")
    # PROOF already carries target; REVIEW's files are gone and it names no standard, so only a
    # decided sibling — PROOF — can settle it.
    done = run(home, "--write")
    assert done.returncode == 0, done.stdout + done.stderr
    assert "1 by siblings" in done.stdout
    assert (home / REVIEW).read_text(encoding="utf-8").startswith("---\ntarget: backend\n")


def test_a_proof_is_rewritten_once_and_carries_both_its_target_and_its_new_pin(home):
    """The proof is itself a decided record (it gains `target`) and the record whose pin this run
    re-stamps; the final file carries both edits, not just whichever write happened last."""
    done = run(home, "--write")
    assert done.returncode == 0, done.stdout + done.stderr
    proof = (home / PROOF).read_text(encoding="utf-8")
    assert proof.startswith("---\ntarget: backend\n")
    assert f"implementation: {pin_of(home / IMPLEMENTATION)}" in proof


def test_the_proof_implementation_pairing_ignores_an_ancestor_directory_named_proof(tmp_path):
    """The pairing is computed from the record's path relative to the project root, never from
    the absolute path on disk — an ancestor directory that happens to be named `proof` must not
    steer which file this run treats as the implementation."""
    home = tmp_path / "proof" / "consumer"
    shutil.copytree(BASELINE, home)
    for name in (IMPLEMENTATION, PROOF, REVIEW):
        strip_target(home / name)
    set_pin(home / PROOF, pin_of(home / IMPLEMENTATION))
    subprocess.run(["git", "init", "-q", str(home)], check=True, capture_output=True)
    done = run(home, "--write")
    assert done.returncode == 0, done.stdout + done.stderr
    assert "re-pinned 1 proof(s)" in done.stdout
    assert f"implementation: {pin_of(home / IMPLEMENTATION)}" in \
        (home / PROOF).read_text(encoding="utf-8")


def test_a_malformed_rewrite_stops_the_whole_run_before_anything_is_written(home):
    """A respell is owed (files decide `web`, the standard resolves only under `backend`), but
    this record spells its standard in flow style, which the `at:` regex does not match. The
    whole run stops before touching disk — not just this one record."""
    declared = json.loads((home / "siegard.json").read_text(encoding="utf-8"))
    declared["targets"]["web"] = "web"
    (home / "siegard.json").write_text(json.dumps(declared), encoding="utf-8")
    (home / "web/page.ts").parent.mkdir(parents=True, exist_ok=True)
    (home / "web/page.ts").write_text("", encoding="utf-8")
    text = (home / IMPLEMENTATION).read_text(encoding="utf-8")
    text = text.replace("- path: src/troubleshooting/case.ts", "- path: page.ts")
    task_line = ("task: sha256:fd8b6fdbd9585f0ebde1b6556b85954fb4c200fd03a9752367484953337fde76")
    standard_pin = pin_of(home / "backend/standard.yaml")
    text = text.replace(task_line,
                        f"{task_line}\nstandard: {{at: standard.yaml, pin: {standard_pin}}}")
    (home / IMPLEMENTATION).write_text(text, encoding="utf-8")
    before = digests(home)
    done = run(home, "--write")
    assert done.returncode == 1, done.stdout + done.stderr
    assert "MALFORMED" in done.stdout
    assert "nothing written" in done.stdout
    assert digests(home) == before
