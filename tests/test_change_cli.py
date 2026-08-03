"""`change.py` as a command, run as one.

Exit codes are the interface here, so they are read from a real process. An earlier version of this
suite read them through a pipe and was reporting `sed`'s status; the numbers it printed meant
nothing, which is why the command is spawned directly.
"""
from __future__ import annotations

import subprocess
import sys

import pytest

import graph_edit as door

CANNOT_RUN = 2


@pytest.fixture
def change(bin_dir):
    def run(*args) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, str(bin_dir / "change.py"), *args],
                              capture_output=True, text=True)
    return run


@pytest.fixture
def populated(root, change, sample):
    """A change open over a root holding two nodes, written through the door."""
    change("open", str(root), "--requirement=rq_0042")
    for key in ("subdomain", "context"):
        node_id, frontmatter = sample[key]
        door.create_node(root, node_id, frontmatter, "## Answer\nx.\n")
    return root


@pytest.mark.parametrize("args", [
    (),                                    # no command, no root
    ("bogus", "."),                        # a command that is not one
    ("status",),                           # a command with no root
    ("status", ".", "extra"),              # one positional too many
])
def test_bad_arguments_cannot_run(change, args):
    assert change(*args).returncode == CANNOT_RUN


def test_a_root_that_is_not_a_directory_cannot_run(change, root):
    assert change("status", str(root / "nowhere")).returncode == CANNOT_RUN


def test_the_usage_line_names_every_command(change):
    printed = change().stderr
    assert all(command in printed for command in ("open", "status", "close", "discard"))


def test_status_outside_a_change_answers_rather_than_failing(change, root):
    """Being outside a change is a state, not a failure, and a caller that needs to branch on it
    has the Python API."""
    done = change("status", str(root))
    assert done.returncode == 0
    assert "no change is open" in done.stdout


def test_open_names_the_requirement_back(change, root):
    done = change("open", str(root), "--requirement=rq_0042")
    assert done.returncode == 0
    assert "rq_0042" in done.stdout


def test_a_second_open_is_refused_on_stderr(change, root):
    change("open", str(root))
    done = change("open", str(root))
    assert done.returncode == 1
    assert "already open" in done.stderr


def test_status_lists_what_the_door_recorded_in_order(change, populated, sample):
    done = change("status", str(populated))
    assert done.returncode == 0
    listed = [line.strip() for line in done.stdout.splitlines()[1:]]
    assert listed == [sample["subdomain"][0], sample["context"][0]]


def test_close_prints_the_set_it_clears(change, populated, sample):
    """That call is the last moment anything can see it, so a close whose output is discarded has
    thrown away the answer the change was opened to get."""
    done = change("close", str(populated))
    assert done.returncode == 0
    assert "2 node(s) touched" in done.stdout
    assert sample["context"][0] in done.stdout
    assert "no change is open" in change("status", str(populated)).stdout


def test_close_over_an_incoherent_graph_is_refused_and_keeps_the_set(change, populated, sample):
    node_id, frontmatter = sample["subdomain"]
    door.edit_node(populated, node_id, dict(frontmatter, depends_on=["dm.definition.a.b"]), "x")
    done = change("close", str(populated))
    assert done.returncode == 1
    assert "dm.definition.a.b" in done.stderr
    assert "still open" in done.stderr
    assert "2 node(s) touched" in change("status", str(populated)).stdout


def test_discard_succeeds_where_close_refuses(change, populated, sample):
    node_id, frontmatter = sample["subdomain"]
    door.edit_node(populated, node_id, dict(frontmatter, depends_on=["dm.definition.a.b"]), "x")
    assert change("close", str(populated)).returncode == 1
    done = change("discard", str(populated))
    assert done.returncode == 0
    assert "nothing is rolled back" in done.stdout


@pytest.mark.parametrize("command", ["close", "discard"])
def test_ending_a_change_that_is_not_open(change, root, command):
    assert change(command, str(root)).returncode == 1
