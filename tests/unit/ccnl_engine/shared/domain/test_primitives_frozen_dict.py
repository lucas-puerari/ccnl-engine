"""Tests for FrozenDict — the immutable serializable dict primitive."""

import copy

import pytest

from ccnl_engine.shared.domain.primitives import FrozenDict


class TestFrozenDictMutation:
    """Every in-place mutation method must raise TypeError."""

    def _fd(self) -> FrozenDict[str, int]:
        return FrozenDict({"a": 1, "b": 2})

    def test_setitem_raises(self) -> None:
        """Item assignment raises TypeError."""
        fd = self._fd()
        with pytest.raises(TypeError, match="does not support item assignment"):
            fd["c"] = 3

    def test_delitem_raises(self) -> None:
        """Item deletion raises TypeError."""
        fd = self._fd()
        with pytest.raises(TypeError, match="does not support item deletion"):
            del fd["a"]

    def test_update_raises(self) -> None:
        """update() raises TypeError."""
        fd = self._fd()
        with pytest.raises(TypeError, match="does not support update"):
            fd.update({"c": 3})

    def test_pop_raises(self) -> None:
        """pop() raises TypeError."""
        fd = self._fd()
        with pytest.raises(TypeError, match="does not support pop"):
            fd.pop("a")

    def test_popitem_raises(self) -> None:
        """popitem() raises TypeError."""
        fd = self._fd()
        with pytest.raises(TypeError, match="does not support popitem"):
            fd.popitem()

    def test_clear_raises(self) -> None:
        """clear() raises TypeError."""
        fd = self._fd()
        with pytest.raises(TypeError, match="does not support clear"):
            fd.clear()

    def test_setdefault_raises(self) -> None:
        """setdefault() raises TypeError."""
        fd = self._fd()
        with pytest.raises(TypeError, match="does not support setdefault"):
            fd.setdefault("c", 0)

    def test_ior_raises(self) -> None:
        """In-place |= raises TypeError."""
        fd: FrozenDict[str, int] = self._fd()
        with pytest.raises(TypeError, match=r"does not support \|="):
            fd |= {"c": 3}


class TestFrozenDictRead:
    """FrozenDict must behave as a normal Mapping for reads."""

    def test_getitem(self) -> None:
        """Item access works normally."""
        fd: FrozenDict[str, int] = FrozenDict({"x": 42})
        assert fd["x"] == 42

    def test_len(self) -> None:
        """len() returns the element count."""
        assert len(FrozenDict({"a": 1, "b": 2})) == 2

    def test_iter(self) -> None:
        """Iteration yields all keys."""
        fd: FrozenDict[str, int] = FrozenDict({"a": 1, "b": 2})
        assert set(fd) == {"a", "b"}

    def test_contains(self) -> None:
        """Membership test works."""
        fd: FrozenDict[str, int] = FrozenDict({"a": 1})
        assert "a" in fd
        assert "z" not in fd

    def test_repr(self) -> None:
        """Repr identifies the type."""
        fd: FrozenDict[str, int] = FrozenDict({"a": 1})
        assert repr(fd).startswith("FrozenDict")

    def test_empty(self) -> None:
        """Empty FrozenDict is falsy."""
        assert not FrozenDict()


class TestFrozenDictCopy:
    """FrozenDict supports deepcopy and model_copy (N15)."""

    def test_deepcopy_produces_frozen_dict(self) -> None:
        """copy.deepcopy returns a FrozenDict."""
        fd: FrozenDict[str, int] = FrozenDict({"a": 1})
        cloned = copy.deepcopy(fd)
        assert isinstance(cloned, FrozenDict)

    def test_deepcopy_values_are_equal(self) -> None:
        """Deepcopied values equal originals."""
        fd: FrozenDict[str, int] = FrozenDict({"a": 1, "b": 2})
        cloned = copy.deepcopy(fd)
        assert dict(cloned) == {"a": 1, "b": 2}

    def test_deepcopy_result_is_frozen(self) -> None:
        """Deepcopied FrozenDict still blocks mutation."""
        fd: FrozenDict[str, int] = FrozenDict({"a": 1})
        cloned = copy.deepcopy(fd)
        with pytest.raises(TypeError):
            cloned["b"] = 2

    def test_nested_deepcopy(self) -> None:
        """Nested FrozenDicts survive deepcopy."""
        inner: FrozenDict[str, int] = FrozenDict({"x": 1})
        outer: FrozenDict[str, FrozenDict[str, int]] = FrozenDict({"inner": inner})
        cloned = copy.deepcopy(outer)
        assert isinstance(cloned["inner"], FrozenDict)
        assert cloned["inner"]["x"] == 1


class TestFrozenDictLimitations:
    """Document known non-guarantees of the FrozenDict subclass approach."""

    def test_dict_setitem_bypass_is_known_behaviour(self) -> None:
        """dict.__setitem__ bypasses the override — documented non-guarantee.

        FrozenDict guards against accidental mutation (``fd["k"] = v`` raises
        TypeError) but is not an absolute security boundary.  Direct base-class
        access bypasses all overrides and is intentionally not blocked; see
        the class docstring for the rationale.
        """
        fd: FrozenDict[str, int] = FrozenDict({"a": 1})
        dict.__setitem__(fd, "a", 99)  # noqa: PLC2801
        assert fd["a"] == 99  # base-class bypass is a known non-guarantee
