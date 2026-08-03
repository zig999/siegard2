"""`graph_edit` — the door, and the four rules it applies that the layers below do not.

A node is written inside a change or not at all; it is validated before it lands; it is not deleted
while anything points at it; and a change does not close while the graph does not hold together.
"""
from __future__ import annotations

import pytest

import graph_edit as door
import graph_query
import node_io


@pytest.fixture
def opened(root):
    door.open_change(root, requirement="rq_0042")
    return root


@pytest.fixture
def base(opened, sample):
    """A subdomain, a context in it, and a definition in that — written and closed."""
    for key in ("subdomain", "context", "definition"):
        node_id, frontmatter = sample[key]
        door.create_node(opened, node_id, frontmatter, "## Answer\nx.\n")
    door.close_change(opened)
    return opened


@pytest.mark.parametrize("call", ["create", "edit", "delete", "close"])
def test_the_door_refuses_outside_a_change(root, sample, call):
    node_id, frontmatter = sample["definition"]
    actions = {
        "create": lambda: door.create_node(root, node_id, frontmatter, "b"),
        "edit": lambda: door.edit_node(root, node_id, frontmatter, "b"),
        "delete": lambda: door.delete_node(root, node_id),
        "close": lambda: door.close_change(root),
    }
    with pytest.raises(door.GraphEditError):
        actions[call]()


def test_an_invalid_node_is_neither_written_nor_recorded(opened, node):
    """Refusing at the write is the last point where the error still names the object that caused
    it, rather than arriving as a later sweep over everything."""
    node_id = "dm.definition.sales.broken"
    incomplete = node(node_id, "definition", ddd="value-object")  # no boundary, no gap naming one
    with pytest.raises(door.GraphEditError):
        door.create_node(opened, node_id, incomplete, "b")
    assert node_io.exists(opened, node_id) is False
    assert door.touched(opened) == []


def test_a_ddd_outside_its_kinds_vocabulary_is_refused(opened, node):
    node_id = "dm.definition.sales.order"
    wrong = node(node_id, "definition", ddd="saga", boundary="dm.context.sales",
                 attributes=[{"name": "t", "type": "money"}])
    with pytest.raises(door.GraphEditError):
        door.create_node(opened, node_id, wrong, "b")


def test_a_cross_kind_prohibition_is_enforced(opened, node):
    """A scope belongs to no scope, and its lack of a boundary is what identifies a partition
    root."""
    node_id = "dm.subdomain.other"
    scope = node(node_id, "subdomain", subdomain_type="core", boundary="dm.context.sales")
    with pytest.raises(door.GraphEditError):
        door.create_node(opened, node_id, scope, "b")


def test_a_string_attribute_missing_its_parameter_is_refused(opened, node):
    node_id = "dm.definition.sales.order"
    unbounded = node(node_id, "definition", ddd="value-object", boundary="dm.context.sales",
                     attributes=[{"name": "reference", "type": "string"}])
    with pytest.raises(door.GraphEditError):
        door.create_node(opened, node_id, unbounded, "b")


def test_what_the_door_writes_is_recorded_in_order(base, sample):
    assert node_io.every_node(base) == sorted(node_id for node_id, _ in sample.values())


def test_creating_over_an_existing_node_is_refused(base, sample):
    door.open_change(base)
    node_id, frontmatter = sample["definition"]
    with pytest.raises(door.GraphEditError, match="already"):
        door.create_node(base, node_id, frontmatter, "b")


def test_editing_an_absent_node_is_refused(opened, node):
    node_id = "dm.definition.sales.ghost"
    ghost = node(node_id, "definition", ddd="value-object", boundary="dm.context.sales",
                 attributes=[{"name": "t", "type": "money"}])
    with pytest.raises(door.GraphEditError, match="holds no"):
        door.edit_node(opened, node_id, ghost, "b")


def test_editing_a_node_twice_records_it_once(base, sample):
    node_id, frontmatter = sample["definition"]
    door.open_change(base)
    door.edit_node(base, node_id, dict(frontmatter, title="Renamed"), "## Answer\ny.\n")
    door.edit_node(base, node_id, dict(frontmatter, title="Renamed twice"), "## Answer\nz.\n")
    assert door.touched(base) == [node_id]
    assert node_io.read(base, node_id)[0]["title"] == "Renamed twice"


def test_close_is_refused_over_a_dangling_reference(base, sample):
    """Closing clears the set, so a change allowed to close over an unresolved edge takes with it
    the only record of where to look."""
    node_id, frontmatter = sample["definition"]
    door.open_change(base)
    door.edit_node(base, node_id, dict(frontmatter, depends_on=["dm.definition.sales.nowhere"]), "x")
    with pytest.raises(door.GraphEditError, match="nowhere"):
        door.close_change(base)
    assert door.touched(base) == [node_id]


def test_close_succeeds_once_the_reference_is_repaired(base, sample):
    node_id, frontmatter = sample["definition"]
    door.open_change(base)
    door.edit_node(base, node_id, dict(frontmatter, depends_on=["dm.definition.sales.nowhere"]), "x")
    with pytest.raises(door.GraphEditError):
        door.close_change(base)
    door.edit_node(base, node_id, frontmatter, "x")
    assert door.close_change(base) == [node_id]


def test_discard_is_allowed_over_a_graph_close_refuses(base, sample):
    """Abandoning a change is a different statement from finishing one, and has a different call."""
    node_id, frontmatter = sample["definition"]
    door.open_change(base)
    door.edit_node(base, node_id, dict(frontmatter, depends_on=["dm.definition.a.b"]), "x")
    assert door.discard_change(base) == [node_id]


def test_deletion_is_refused_while_anything_arrives(base, sample):
    """Refused at the delete, the graph is coherent after every operation — so a change abandoned
    halfway leaves a base somebody else can still work in."""
    context_id, _ = sample["context"]
    door.open_change(base)
    with pytest.raises(door.GraphEditError, match="edge"):
        door.delete_node(base, context_id)
    assert door.touched(base) == []
    assert node_io.exists(base, context_id) is True


def test_the_refusal_names_every_edge_that_arrives(base, sample):
    context_id, _ = sample["context"]
    definition_id, _ = sample["definition"]
    door.open_change(base)
    with pytest.raises(door.GraphEditError) as refused:
        door.delete_node(base, context_id)
    assert definition_id in str(refused.value)
    assert "boundary" in str(refused.value)


def test_leaf_then_scope_deletes_and_closes(base, sample):
    definition_id, _ = sample["definition"]
    context_id, _ = sample["context"]
    door.open_change(base)
    door.delete_node(base, definition_id)
    door.delete_node(base, context_id)
    assert door.close_change(base) == [definition_id, context_id]
    assert node_io.every_node(base) == [sample["subdomain"][0]]


def test_deleting_an_absent_node_is_refused(opened):
    with pytest.raises(door.GraphEditError, match="holds no"):
        door.delete_node(opened, "dm.definition.sales.ghost")


@pytest.mark.parametrize("target, expected", [
    ("context", [("dm.definition.sales.order", "boundary")]),
    ("subdomain", [("dm.context.sales", "subdomain")]),
    ("definition", []),
])
def test_references_to_finds_what_arrives(base, sample, target, expected):
    assert graph_query.references_to(base, sample[target][0]) == expected


def test_references_to_finds_a_content_edge(base, sample):
    subdomain_id, frontmatter = sample["subdomain"]
    definition_id, _ = sample["definition"]
    door.open_change(base)
    door.edit_node(base, subdomain_id, dict(frontmatter, depends_on=[definition_id]), "x")
    assert graph_query.references_to(base, definition_id) == [(subdomain_id, "depends_on[0]")]


def test_references_to_never_counts_the_node_itself(base, sample):
    for node_id, _ in sample.values():
        assert all(source != node_id for source, _ in graph_query.references_to(base, node_id))
