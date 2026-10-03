"""Collection validators of the public inputs."""

from __future__ import annotations

from types import MappingProxyType

import pytest
from hypothesis import given
from hypothesis import strategies as st

from ccnl_engine.shared.domain.collection_validation import (
    frozenset_of,
    items_of_type,
    mapping_of,
    tuple_of,
)
from ccnl_engine.shared.domain.errors import InvalidInputError
from ccnl_engine.shared.domain.validation import require_str

_FEATURE = "test_feature"
_INTS = items_of_type(int, feature=_FEATURE)


def _text(value: object, path: str) -> str:
    require_str(value, path, feature=_FEATURE, non_blank=True)
    return str(value)


class TestTupleOf:
    """Tuples and lists, validated element by element."""

    def test_normalises_a_list_to_a_tuple(self) -> None:
        """A list is accepted and returned as a tuple, in order."""
        assert tuple_of([1, 2], "t", _INTS, feature=_FEATURE) == (1, 2)
        assert tuple_of((), "t", _INTS, feature=_FEATURE) == ()

    @pytest.mark.parametrize("value", [None, {1, 2}, "12", {1: 2}], ids=repr)
    def test_rejects_what_is_not_a_tuple_or_a_list(self, value: object) -> None:
        """Sets, strings and mappings are not ordered collections."""
        with pytest.raises(InvalidInputError, match="a tuple or a list") as raised:
            tuple_of(value, "t", _INTS, feature=_FEATURE)
        assert raised.value.field == "t"

    @given(
        before=st.lists(st.integers(), max_size=4),
        after=st.lists(st.integers(), max_size=4),
        bad=st.one_of(st.text(), st.floats(), st.none()),
    )
    def test_reports_the_position_of_an_invalid_element(
        self, before: list[int], after: list[int], bad: object
    ) -> None:
        """First, middle or last: the error names the element's index."""
        with pytest.raises(InvalidInputError) as raised:
            tuple_of([*before, bad, *after], "t", _INTS, feature=_FEATURE)
        assert raised.value.field == f"t[{len(before)}]"


class TestFrozensetOf:
    """Frozensets only, validated element by element."""

    def test_accepts_a_frozenset(self) -> None:
        """Valid elements are kept."""
        assert frozenset_of(frozenset({"a"}), "s", _text, feature=_FEATURE) == {"a"}

    @pytest.mark.parametrize("value", [{"a"}, ["a"], ("a",), None], ids=repr)
    def test_rejects_a_mutable_set_and_sequences(self, value: object) -> None:
        """The input is immutable: a set is rejected like a list."""
        with pytest.raises(InvalidInputError, match="a frozenset"):
            frozenset_of(value, "s", _text, feature=_FEATURE)

    def test_reports_the_invalid_element(self) -> None:
        """An element is reported by its value."""
        with pytest.raises(InvalidInputError) as raised:
            frozenset_of(frozenset({"a", ""}), "s", _text, feature=_FEATURE)
        assert raised.value.field == "s['']"


class TestMappingOf:
    """Mappings, validated key by key and value by value."""

    def test_returns_a_dict_in_order(self) -> None:
        """Any mapping is accepted and returned as a dict."""
        entries = mapping_of(
            MappingProxyType({"b": 2, "a": 1}), "m", _text, _INTS, feature=_FEATURE
        )
        assert list(entries.items()) == [("b", 2), ("a", 1)]

    def test_rejects_what_is_not_a_mapping(self) -> None:
        """A list of pairs is not a mapping."""
        with pytest.raises(InvalidInputError, match="a mapping"):
            mapping_of([("a", 1)], "m", _text, _INTS, feature=_FEATURE)

    @pytest.mark.parametrize(
        ("entries", "field"),
        [({"": 1}, "m['']"), ({"a": "x"}, "m['a']")],
    )
    def test_reports_the_key_of_an_invalid_entry(
        self, entries: dict[object, object], field: str
    ) -> None:
        """A bad key or a bad value is reported by its key."""
        with pytest.raises(InvalidInputError) as raised:
            mapping_of(entries, "m", _text, _INTS, feature=_FEATURE)
        assert raised.value.field == field


def test_items_of_type_names_the_expected_element() -> None:
    """The element description defaults to the type names."""
    named = items_of_type((int, str), feature=_FEATURE, name="a token")
    with pytest.raises(InvalidInputError, match="must be a token"):
        named(1.5, "x")
    with pytest.raises(InvalidInputError, match="must be an int or a str"):
        items_of_type((int, str), feature=_FEATURE)(1.5, "x")
