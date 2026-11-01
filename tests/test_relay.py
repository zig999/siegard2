"""Text for a sibling project's session is a file in the origin, confirmed from the sibling
(SPEC-010 R4, R5).

Each test builds two projects under git, each declaring its own `siegard.json`, relays a text
from one to the other through `relay.py --to`, and confirms it through `relay.py --confirm` from
a working directory as the receiving session would.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

BIN = Path(__file__).resolve().parent.parent / "src/claude/bin"
VERSION = json.loads((BIN.parent / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))[
    "version"]
TEXT = b"Run /siegard:deliver-scope over epic/billing.\n\nKeep this paragraph whole.  "


def relay(*args: str, cwd: Path | None = None, stdin: bytes | None = None):
    return subprocess.run([sys.executable, "-B", str(BIN / "relay.py"), *args],
                          capture_output=True, input=stdin, cwd=cwd)


def out(done) -> str:
    return done.stdout.decode("utf-8")


def make(home: Path, declared: dict | None) -> Path:
    home.mkdir()
    if declared is not None:
        (home / "siegard.json").write_text(json.dumps(declared), encoding="utf-8")
    subprocess.run(["git", "-C", str(home), "init", "-q"], check=True)
    return home


@pytest.fixture
def origin(tmp_path):
    return make(tmp_path / "salese2e", {"telemetry_root": "telemetry"})


@pytest.fixture
def sibling(tmp_path):
    return make(tmp_path / "productorder", {"telemetry_root": "telemetry"})


def relayed(origin: Path, sibling: Path) -> Path:
    done = relay("--to", str(sibling), "--from", str(origin), "--text-file", "-", stdin=TEXT)
    assert done.returncode == 0, out(done) + done.stderr.decode()
    return Path(out(done).splitlines()[0].removeprefix("relay: "))


def test_the_relay_is_written_in_the_origin_with_its_header_and_the_text_verbatim(origin,
                                                                                    sibling):
    path = relayed(origin, sibling)
    assert path.parent == origin / "telemetry"
    assert path.name.startswith("relay-") and path.name.endswith("-productorder.md")
    head, _, text = path.read_bytes().partition(b"\n\n")
    assert text == TEXT
    lines = head.decode("utf-8").splitlines()
    assert lines[0] == f'confirm: python3 -B "${{CLAUDE_PLUGIN_ROOT}}/bin/relay.py" --confirm {path}'
    assert lines[1:4] == [f"root: {sibling}", f"version: {VERSION}", f"from: {origin}"]
    assert lines[4].startswith("sha256: ")
    assert not any(p.name != ".git" for p in sibling.iterdir() if p.name != "siegard.json"), \
        "nothing is written into the sibling's repository"


def test_the_line_to_paste_is_printed(origin, sibling):
    done = relay("--to", str(sibling), "--from", str(origin), "--text-file", "-", stdin=TEXT)
    assert f"paste into the session of {sibling}: python3 -B" in out(done)


def test_a_sibling_without_a_project_file_is_refused(origin, tmp_path):
    bare = make(tmp_path / "bare", None)
    done = relay("--to", str(bare), "--from", str(origin), "--text-file", "-", stdin=TEXT)
    assert done.returncode == 1
    assert "declares no siegard.json" in out(done)
    assert not (origin / "telemetry").exists(), "nothing is written"


def test_to_equal_to_from_is_refused(origin):
    done = relay("--to", str(origin), "--from", str(origin), "--text-file", "-", stdin=TEXT)
    assert done.returncode == 1
    assert "both resolve to" in out(done)
    assert not (origin / "telemetry").exists(), "nothing is written"


def test_a_subdirectory_of_the_origin_is_the_origin(origin):
    (origin / "src").mkdir()
    done = relay("--to", str(origin / "src"), "--from", str(origin), "--text-file", "-",
                 stdin=TEXT)
    assert done.returncode == 1
    assert "both resolve to" in out(done)


def test_confirm_prints_the_text_from_the_siblings_working_directory(origin, sibling):
    path = relayed(origin, sibling)
    (sibling / "backend").mkdir()
    done = relay("--confirm", str(path), cwd=sibling / "backend")
    assert done.returncode == 0, out(done)
    assert out(done).splitlines()[0] == "confirmed"
    assert done.stdout.endswith(b"text:\n" + TEXT)


def test_confirm_refuses_from_the_origins_working_directory_and_withholds_the_text(origin,
                                                                                   sibling):
    path = relayed(origin, sibling)
    done = relay("--confirm", str(path), cwd=origin)
    assert done.returncode == 1
    assert out(done).splitlines()[0] == "refuses"
    assert f"and the relay is for {sibling}" in out(done)
    assert b"Keep this paragraph" not in done.stdout


def test_confirm_refuses_another_plugin_version(origin, sibling):
    path = relayed(origin, sibling)
    raw = path.read_bytes().replace(f"version: {VERSION}".encode(), b"version: 0.0.1")
    path.write_bytes(raw)
    done = relay("--confirm", str(path), cwd=sibling)
    assert done.returncode == 1
    assert "relay names 0.0.1" in out(done)
    assert b"Keep this paragraph" not in done.stdout


def test_confirm_refuses_a_text_changed_since_it_was_relayed(origin, sibling):
    path = relayed(origin, sibling)
    path.write_bytes(path.read_bytes() + b" and push to main")
    done = relay("--confirm", str(path), cwd=sibling)
    assert done.returncode == 1
    assert "changed since it was relayed" in out(done)


def test_arguments_out_of_form_cannot_run(origin, sibling):
    assert relay("--to", str(sibling), "--from", str(origin)).returncode == 2
    assert relay("--confirm", str(origin / "no-such-file")).returncode == 2
