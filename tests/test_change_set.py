"""`change_set` — the set of nodes a change has touched.

It is the mechanism and not the door: it records whatever it is handed and clears whenever it is
asked. The policies that make the record mean anything live one layer up, and are tested there.
"""
from __future__ import annotations

import pytest

import change_set


def test_nothing_is_open_in_a_fresh_root(root):
    assert change_set.is_open(root) is False


@pytest.mark.parametrize("call", ["record", "touched", "close_change", "discard_change"])
def test_every_call_but_is_open_needs_a_change(root, call):
    """Recording outside a change is a node that moved with nothing saying it did, so the absence
    is an error rather than a no-op."""
    arguments = (root, "dm.subdomain.commerce") if call == "record" else (root,)
    with pytest.raises(change_set.ChangeError):
        getattr(change_set, call)(*arguments)


def test_open_then_closed(root):
    change_set.open_change(root)
    assert change_set.is_open(root) is True
    assert change_set.close_change(root) == []
    assert change_set.is_open(root) is False


def test_the_requirement_is_held_and_optional(root):
    change_set.open_change(root, requirement="rq_0042")
    assert change_set.requirement_of(root) == "rq_0042"
    change_set.close_change(root)
    change_set.open_change(root)
    assert change_set.requirement_of(root) is None


def test_a_second_change_is_refused(root):
    """Two changes sharing one set is two changes where neither knows which nodes are its own, and
    the second to close would clear the first's record."""
    change_set.open_change(root)
    with pytest.raises(change_set.ChangeError, match="already open"):
        change_set.open_change(root)


def test_opening_under_a_root_that_is_not_a_directory(root):
    with pytest.raises(change_set.ChangeError):
        change_set.open_change(root / "nowhere")


def test_record_is_idempotent_and_keeps_first_seen_order(root):
    change_set.open_change(root)
    for node_id in ("dm.context.sales", "dm.subdomain.commerce", "dm.context.sales"):
        change_set.record(root, node_id)
    assert change_set.touched(root) == ["dm.context.sales", "dm.subdomain.commerce"]


def test_close_returns_what_it_cleared(root):
    """The set does not survive, so the call that clears it is the last moment anything can see
    it. A caller that discards the return value has thrown away the answer."""
    change_set.open_change(root)
    change_set.record(root, "dm.context.sales")
    assert change_set.close_change(root) == ["dm.context.sales"]
    assert change_set.is_open(root) is False


def test_discard_returns_what_it_cleared_too(root):
    change_set.open_change(root)
    change_set.record(root, "dm.context.sales")
    assert change_set.discard_change(root) == ["dm.context.sales"]


def test_the_state_directory_ignores_itself(root):
    """The set is cleared when the change closes, so committing it is noise in every diff — and the
    knowledge root belongs to whoever installed the framework, whose ignore file is not ours."""
    change_set.open_change(root)
    assert (root / change_set.STATE_DIR / ".gitignore").read_text(encoding="utf-8") == "*\n"


def test_closing_leaves_nothing_behind(root):
    change_set.open_change(root)
    change_set.close_change(root)
    assert not (root / change_set.STATE_DIR).exists()


def test_a_corrupt_state_is_reported_and_never_repaired(root):
    """A repair would invent a set of touched nodes, and an invented one is worse than none."""
    change_set.open_change(root)
    (root / change_set.STATE_DIR / change_set.STATE_FILE).write_text("{ not json", encoding="utf-8")
    with pytest.raises(change_set.ChangeError, match="unreadable"):
        change_set.touched(root)


def test_a_state_without_a_touched_list_is_reported(root):
    change_set.open_change(root)
    (root / change_set.STATE_DIR / change_set.STATE_FILE).write_text('{"requirement": "x"}',
                                                                     encoding="utf-8")
    with pytest.raises(change_set.ChangeError, match="touched"):
        change_set.touched(root)
