"""`node_io` — the only module that opens a node file.

What it knows is arithmetic. The three refusals on write are one fact from three sides: the
identifier in the frontmatter is the one being written, the kind in the frontmatter is the kind in
that identifier, and the identifier computes to the path. A write is the only moment any of them can
break, and this is the only place a write happens.
"""
from __future__ import annotations

from pathlib import Path

import pytest

import node_io


@pytest.mark.parametrize("node_id, path", [
    ("dm.subdomain.sales", "subdomain/sales.md"),
    ("dm.context.sales", "context/sales.md"),
    ("dm.definition.sales.order", "definition/sales/order.md"),
    ("dm.rule.sales.total-is-positive", "rule/sales/total-is-positive.md"),
])
def test_identifier_and_path_compute_to_each_other(node_id, path):
    assert node_io.path_of(node_id) == Path(path)
    assert node_io.id_of(path) == node_id


@pytest.mark.parametrize("node_id", [
    "dm.subdomain",                     # a scope kind needs a slug
    "dm.a.b.c.d",                       # nothing has four segments
    "dm.definition.Sales.order",        # a slug is kebab-case
    "dm.definition.sales.",             # and non-empty
    "definition.sales.order",           # the prefix is not optional
    "",
])
def test_a_malformed_identifier_computes_to_no_path(node_id):
    with pytest.raises(node_io.NodeIOError):
        node_io.path_of(node_id)


@pytest.mark.parametrize("path", ["README.md", "a/b/c/d.md", "definition/Sales/order.md"])
def test_a_file_that_is_not_a_node_computes_to_no_identifier(path):
    with pytest.raises(node_io.NodeIOError):
        node_io.id_of(path)


def test_reading_an_absent_node_is_an_error_and_not_an_empty_one(root, sample):
    node_id, _ = sample["definition"]
    assert node_io.exists(root, node_id) is False
    with pytest.raises(node_io.NodeIOError):
        node_io.read(root, node_id)


def test_write_creates_the_scope_directory(root, sample):
    node_id, frontmatter = sample["definition"]
    written = node_io.write(root, node_id, frontmatter, "## Answer\nx.\n")
    assert written.relative_to(root) == Path("definition/sales/order.md")
    assert node_io.exists(root, node_id)


def test_the_body_comes_back_verbatim(root, sample):
    node_id, frontmatter = sample["definition"]
    body = "## Answer\n\nx.\n\n## Invariants\n\nNone.\n"
    node_io.write(root, node_id, frontmatter, body)
    assert node_io.read(root, node_id)[1] == body


def test_read_then_write_is_byte_identical(root, sample):
    """A node rewritten without being altered produces no diff, so a reader cannot mistake a
    round trip for a change."""
    node_id, frontmatter = sample["definition"]
    path = node_io.write(root, node_id, frontmatter, "## Answer\nx.\n")
    before = path.read_bytes()
    node_io.write(root, node_id, *node_io.read(root, node_id))
    assert path.read_bytes() == before


def test_write_refuses_an_identifier_the_frontmatter_disagrees_with(root, sample):
    _, frontmatter = sample["definition"]
    with pytest.raises(node_io.NodeIOError, match="id"):
        node_io.write(root, "dm.definition.sales.other", frontmatter, "")


def test_write_refuses_a_kind_the_identifier_disagrees_with(root, node):
    node_id = "dm.definition.sales.order"
    with pytest.raises(node_io.NodeIOError, match="kind"):
        node_io.write(root, node_id, node(node_id, "rule"), "")


def test_write_refuses_frontmatter_that_is_not_a_mapping(root):
    with pytest.raises(node_io.NodeIOError):
        node_io.write(root, "dm.definition.sales.order", ["not", "a", "mapping"], "")


def test_a_file_with_no_fence_is_reported_rather_than_read_as_empty(root):
    path = root / "definition" / "sales"
    path.mkdir(parents=True)
    (path / "order.md").write_text("no frontmatter here\n", encoding="utf-8")
    with pytest.raises(node_io.NodeIOError, match="fence"):
        node_io.read(root, "dm.definition.sales.order")


def test_every_node_reads_the_tree_and_skips_what_is_not_one(root, sample):
    for node_id, frontmatter in sample.values():
        node_io.write(root, node_id, frontmatter, "")
    (root / "notes.md").write_text("stray", encoding="utf-8")
    (root / "system.md").write_text("stray", encoding="utf-8")
    assert node_io.every_node(root) == sorted(node_id for node_id, _ in sample.values())


def test_remove_takes_the_scope_directory_it_empties(root, sample):
    """An empty `definition/sales/` asserts a scope that holds nothing, and the next reader cannot
    tell it from one whose contents were never written."""
    node_id, frontmatter = sample["definition"]
    node_io.write(root, node_id, frontmatter, "")
    node_io.remove(root, node_id)
    assert not (root / "definition").exists()


def test_remove_keeps_a_scope_directory_that_still_holds_something(root, node):
    for slug in ("order", "invoice"):
        node_id = f"dm.definition.sales.{slug}"
        node_io.write(root, node_id, node(node_id, "definition"), "")
    node_io.remove(root, "dm.definition.sales.order")
    assert (root / "definition" / "sales" / "invoice.md").is_file()


def test_removing_an_absent_node_is_an_error(root):
    with pytest.raises(node_io.NodeIOError):
        node_io.remove(root, "dm.definition.sales.order")
