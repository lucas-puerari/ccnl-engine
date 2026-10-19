"""Tagged JSON tree: writing, reading back, and one error per rejected node."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from enum import StrEnum
from types import MappingProxyType
from typing import TYPE_CHECKING

import pytest
from pydantic import BaseModel

from ccnl_engine.errors import InvalidInputError
from ccnl_engine.interchange.serializers import encode, loads, read_tree, reject

if TYPE_CHECKING:
    from collections.abc import Mapping


class Colour(StrEnum):
    """An enum of the tree."""

    RED = "red"


@dataclass(frozen=True)
class Leaf:
    """A dataclass that validates itself, as the inputs do."""

    amount: Decimal
    on: date | None = None

    def __post_init__(self) -> None:  # noqa: D105
        if self.amount < 0:
            msg = "Leaf.amount must be >= 0"
            raise InvalidInputError(msg, field="Leaf.amount", remediation="Fix it.")


@dataclass(frozen=True)
class Node:
    """A dataclass holding every kind of value."""

    leaves: tuple[Leaf, ...]
    tags: frozenset[str] = frozenset()
    by_key: Mapping[int | str, Leaf] = field(default_factory=dict)
    colour: Colour = Colour.RED
    note: str | None = None


@dataclass(frozen=True)
class Picky:
    """A dataclass that rejects with a field of another owner, or none."""

    mode: str

    def __post_init__(self) -> None:  # noqa: D105
        if self.mode == "other":
            msg = "rejected"
            raise InvalidInputError(msg, field="Elsewhere.mode")
        if self.mode == "whole":
            msg = "rejected"
            raise InvalidInputError(msg)
        if self.mode == "builtin":
            msg = "not a mode"
            raise ValueError(msg)


_TYPES: Mapping[str, type] = MappingProxyType({
    cls.__name__: cls for cls in (Colour, Leaf, Node, Picky)
})
_NAMES: Mapping[type, str] = MappingProxyType({v: k for k, v in _TYPES.items()})


def _read(tree: object) -> tuple[object, tuple[InvalidInputError, ...]]:
    return read_tree(tree, "Node", types=_TYPES, subject="the test", feature="test")


def _node() -> Node:
    return Node(
        leaves=(Leaf(Decimal("1.50"), date(2026, 1, 2)), Leaf(Decimal(0))),
        tags=frozenset({"b", "a"}),
        by_key={3: Leaf(Decimal(3)), "2026-12-thirteenth": Leaf(Decimal(4))},
        note="x",
    )


def test_a_tree_reads_back_equal_through_json() -> None:
    """Every kind of value survives a JSON round trip."""
    tree = json.loads(json.dumps(encode(_node(), _NAMES)))
    value, errors = _read(tree)
    assert errors == ()
    assert value == _node()


def test_values_are_written_with_their_tags() -> None:
    """Decimals as strings, dates ISO, sets sorted, maps as pairs."""
    tree = encode(_node(), _NAMES)
    assert isinstance(tree, dict)
    fields = tree["fields"]
    assert fields["leaves"]["$tuple"][0]["fields"] == {
        "amount": {"$decimal": "1.50"},
        "on": {"$date": "2026-01-02"},
    }
    assert fields["tags"] == {"$set": ["a", "b"]}
    assert [pair[0] for pair in fields["by_key"]["$map"]] == [3, "2026-12-thirteenth"]
    assert fields["colour"] == {"$enum": "Colour", "value": "red"}


def test_writing_a_type_outside_the_registry_is_a_defect() -> None:
    """A registry that forgot a type fails loudly."""
    with pytest.raises(TypeError, match="Leaf"):
        encode(Leaf(Decimal(1)), {})


class Model(BaseModel):
    """A Pydantic model, as some results hold."""

    amount: Decimal
    items: list[int]


def test_an_open_tree_tags_any_class_by_its_name() -> None:
    """Without a registry, dataclasses and Pydantic models are written."""
    assert encode(Model(amount=Decimal(1), items=[1])) == {
        "$type": "Model",
        "fields": {"amount": {"$decimal": "1"}, "items": {"$tuple": [1]}},
    }


def _leaf(amount: object) -> dict[str, object]:
    return {"$type": "Leaf", "fields": {"amount": amount}}


def _tree(*leaves: object, **fields: object) -> dict[str, object]:
    return {"$type": "Node", "fields": {"leaves": {"$tuple": list(leaves)}, **fields}}


def test_independent_errors_are_all_reported_at_their_paths() -> None:
    """A malformed leaf, a rejected value and an unknown field: three errors."""
    tree = _tree(
        _leaf({"$decimal": "x"}),
        _leaf({"$decimal": "-1"}),
        colour={"$enum": "Colour", "value": "blue"},
        extra=1,
    )
    _, errors = _read(tree)
    assert sorted(e.field or "" for e in errors) == [
        "Node.colour",
        "Node.extra",
        "Node.leaves[0].amount",
        "Node.leaves[1].amount",
    ]


def test_a_constructor_error_keeps_its_message_at_the_node_path() -> None:
    """The field of a constructor moves under the path of its node."""
    _, (error,) = _read(_tree(_leaf({"$decimal": "-1"})))
    assert error.field == "Node.leaves[0].amount"
    assert str(error) == "Leaf.amount must be >= 0"
    assert error.remediation == "Fix it."


def test_a_node_with_a_rejected_child_is_not_built() -> None:
    """The parent of a rejected value adds no consequential error."""
    _, errors = _read(_tree(_leaf({"$decimal": "-1"})))
    assert len(errors) == 1


@pytest.mark.parametrize(
    ("mode", "message"),
    [
        pytest.param("other", "rejected", id="field-of-another-owner"),
        pytest.param("whole", "rejected", id="no-field"),
        pytest.param("builtin", "rejected by Picky: not a mode", id="builtin-error"),
    ],
)
def test_a_constructor_error_without_a_field_of_its_own_is_at_the_node(
    mode: str, message: str
) -> None:
    """An error the node cannot place within itself is the node's."""
    _, (error,) = _read({"$type": "Picky", "fields": {"mode": mode}})
    assert error.field == "Node"
    assert message in str(error)


def test_a_missing_required_field_is_named() -> None:
    """A field the constructor requires is reported, not a TypeError."""
    _, (error,) = _read({"$type": "Node", "fields": {}})
    assert error.field == "Node.leaves"
    assert "missing" in str(error)


@pytest.mark.parametrize(
    ("tree", "path"),
    [
        pytest.param([1], "Node", id="bare-list"),
        pytest.param({"x": 1}, "Node", id="untagged"),
        pytest.param({"$decimal": 1}, "Node", id="decimal-not-text"),
        pytest.param({"$date": "2026-13-01"}, "Node", id="date-malformed"),
        pytest.param({"$date": None}, "Node", id="date-not-text"),
        pytest.param({"$tuple": {}}, "Node", id="tuple-not-a-list"),
        pytest.param({"$set": {}}, "Node", id="set-not-a-list"),
        pytest.param({"$set": [[1]]}, "Node[0]", id="set-of-a-list"),
        pytest.param({"$map": {}}, "Node", id="map-not-a-list"),
        pytest.param({"$map": [[True, 1]]}, "Node[0]", id="map-bool-key"),
        pytest.param({"$map": [[1]]}, "Node[0]", id="map-not-a-pair"),
        pytest.param({"$map": [[1, [2]]]}, "Node[1]", id="map-bad-value"),
        pytest.param({"$enum": "Missing", "value": 1}, "Node", id="unknown-enum"),
        pytest.param({"$enum": "Leaf", "value": 1}, "Node", id="type-as-enum"),
        pytest.param({"$type": "Colour", "fields": {}}, "Node", id="enum-as-type"),
        pytest.param({"$type": 1, "fields": {}}, "Node", id="tag-not-a-string"),
        pytest.param({"$type": "Node", "fields": []}, "Node", id="fields-a-list"),
    ],
)
def test_a_malformed_node_is_one_error_at_its_path(tree: object, path: str) -> None:
    """Each malformed shape is an InvalidInputError naming its node."""
    _, (error,) = _read(tree)
    assert error.field == path
    assert error.feature == "test"
    assert str(error).startswith("cannot read the test: ")


def test_a_tree_nested_too_deeply_is_rejected() -> None:
    """Nesting beyond the recursion limit is input, not a crash."""
    tree: object = 1
    for _ in range(5000):
        tree = {"$tuple": [tree]}
    _, (error,) = _read(tree)
    assert "nested too deeply" in str(error)


@pytest.mark.parametrize("text", ["not json", "[1]", "[" * 100_000])
def test_a_text_that_is_not_a_json_object_is_rejected(text: str) -> None:
    """The envelope must be a JSON object."""
    with pytest.raises(InvalidInputError, match="cannot read the test"):
        loads(text, subject="the test", feature="test")


def test_a_json_object_is_loaded() -> None:
    """A JSON object is returned as a dict."""
    assert loads('{"a": 1}', subject="the test", feature="test") == {"a": 1}


def test_rejecting_a_text_names_no_field() -> None:
    """An envelope error concerns the whole text."""
    with pytest.raises(InvalidInputError) as caught:
        reject("the test", "too old", feature="test")
    assert caught.value.field is None
    assert str(caught.value) == "cannot read the test: too old"
