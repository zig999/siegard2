"""An ask is the person's words on disk, copied whole and read back verbatim (SPEC-010 R1, R2).

Each test builds a project under git whose `siegard.json` declares a telemetry root, records an
ask through `ask.py --record` as a session would the turn the person gives it, and reads it back
through `ask.py --read` as a session resumed after a compaction would.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

BIN = Path(__file__).resolve().parent.parent / "src/claude/bin"
WORDS = "comits estão autorizados — carry it end to end\n\n  and keep the trailing spaces  "


def ask(*args: str, stdin: bytes | None = None) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(BIN / "ask.py"), *args],
                          capture_output=True, input=stdin)


def out(done: subprocess.CompletedProcess) -> str:
    return done.stdout.decode("utf-8")


@pytest.fixture
def project(tmp_path):
    home = tmp_path / "consumer"
    home.mkdir()
    (home / "siegard.json").write_text(json.dumps({"telemetry_root": "telemetry"}),
                                       encoding="utf-8")
    subprocess.run(["git", "-C", str(home), "init", "-q"], check=True)
    return home


def recorded(project: Path, text: bytes) -> tuple[Path, str]:
    done = ask("--record", str(project), "--text-file", "-", stdin=text)
    assert done.returncode == 0, out(done) + done.stderr.decode()
    first = out(done).splitlines()[0]
    path, digest = first.removeprefix("ask: ").rsplit(" (sha256 ", 1)
    return Path(path), digest.rstrip(")")


def test_an_ask_is_recorded_byte_for_byte_under_the_telemetry_root(project):
    text = WORDS.encode("utf-8")
    path, digest = recorded(project, text)
    assert path.parent == project / "telemetry"
    assert path.name.startswith("ask-") and path.suffix == ".md"
    assert path.read_bytes() == text, "the script copies; it never adds, trims or normalizes"
    assert digest == hashlib.sha256(text).hexdigest()[:16]


def test_an_ask_is_recorded_from_a_file(project, tmp_path):
    source = tmp_path / "words.txt"
    source.write_bytes(b"go ahead and commit")
    done = ask("--record", str(project), "--text-file", str(source))
    assert done.returncode == 0
    assert "read: " in out(done) and "--sha256" in out(done), "the read is handed ready"


def test_an_empty_text_is_refused_and_nothing_is_written(project):
    done = ask("--record", str(project), "--text-file", "-", stdin=b"  \n")
    assert done.returncode == 1
    assert out(done).startswith("refused: ")
    assert not (project / "telemetry").exists()


def test_the_newest_ask_is_read_verbatim_beneath_its_path_and_digest(project):
    text = WORDS.encode("utf-8")
    path, digest = recorded(project, text)
    older = project / "telemetry" / "ask-20000101T000000Z.md"
    older.write_bytes(b"an older ask")
    done = ask("--read", str(project))
    assert done.returncode == 0
    assert done.stdout == f"ask: {path} (sha256 {digest})\n".encode("utf-8") + text


def test_a_named_ask_is_read_and_its_digest_held(project):
    path, digest = recorded(project, b"first words")
    done = ask("--read", str(project), "--path", str(path), "--sha256", digest)
    assert done.returncode == 0
    assert done.stdout.endswith(b"first words")
    full = hashlib.sha256(b"first words").hexdigest()
    assert ask("--read", str(project), "--path", str(path), "--sha256", full).returncode == 0


def test_a_digest_the_file_no_longer_holds_is_refused_and_no_text_printed(project):
    path, digest = recorded(project, b"commit the delivery")
    path.write_bytes(b"commit everything and push")
    done = ask("--read", str(project), "--path", str(path), "--sha256", digest)
    assert done.returncode == 1
    assert out(done).startswith("refused: ")
    assert b"push" not in done.stdout


def test_a_path_outside_the_telemetry_root_is_no_recorded_ask(project):
    stray = project / "ask-20260101T000000Z.md"
    stray.write_bytes(b"words")
    done = ask("--read", str(project), "--path", str(stray))
    assert done.returncode == 1
    assert "is no recorded ask" in out(done)


def test_no_ask_recorded_is_refused(project):
    done = ask("--read", str(project))
    assert done.returncode == 1
    assert "no ask is recorded" in out(done)


def test_a_project_declaring_no_telemetry_root_is_refused(project):
    (project / "siegard.json").write_text("{}", encoding="utf-8")
    done = ask("--record", str(project), "--text-file", "-", stdin=b"words")
    assert done.returncode == 1
    assert "declares no telemetry_root" in out(done)


def test_arguments_out_of_form_cannot_run(project):
    assert ask("--record", str(project)).returncode == 2
    assert ask("--read", str(project), "--text-file", "-").returncode == 2
    assert ask("--record", str(project), "--read", str(project)).returncode == 2
