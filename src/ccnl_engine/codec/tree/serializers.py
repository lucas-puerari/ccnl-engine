"""Reading back a tagged JSON tree through the constructors of a registry.

:func:`read_tree` reads a tree :func:`~ccnl_engine.codec.serializers.encode`
wrote, building each node with its constructor so every invariant is checked
again, and collects one :class:`~ccnl_engine.errors.InvalidInputError` per
rejected node with the path of the node.
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from enum import Enum
from types import MappingProxyType
from typing import TYPE_CHECKING, Any

from ccnl_engine.errors import InvalidInputError

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping

__all__ = ["read_tree"]


def read_tree(
    value: object,
    path: str,
    *,
    types: Mapping[str, type],
    subject: str,
    feature: str,
) -> tuple[Any, tuple[InvalidInputError, ...]]:
    """Read a tree written by :func:`encode` with the tags of ``types``.

    Every node is read: a node whose children are rejected is not built,
    so each error is independent of the others, and a constructor that
    rejects a value reports it at the path of its node.

    Args:
        value: The tree, as decoded by ``json.loads``.
        path: Path of the root, e.g. ``"PeriodInput"``.
        types: The types a tree may hold, keyed by tag.
        subject: What the tree holds, e.g. ``"the request"``, for messages.
        feature: Feature of the rejected input.

    Returns:
        The value, and every error found; the value is meaningless when
        there is an error.
    """
    reader = _Reader(types=types, subject=subject, feature=feature)
    try:
        result = reader.read(value, path)
    except RecursionError:
        result = reader.fail(path, "nested too deeply")
    return result, tuple(reader.errors)


#: What a rejected node reads as: never a value of a tree.
_INVALID = object()


@dataclass
class _Reader:
    types: Mapping[str, type]
    subject: str
    feature: str
    errors: list[InvalidInputError] = field(default_factory=list)

    def read(self, value: object, path: str) -> Any:  # noqa: ANN401
        if isinstance(value, list):
            return self.fail(path, "a list outside a $tuple, a $set or a $map")
        if not isinstance(value, dict):
            return value
        read = _READERS.get(frozenset(value))
        if read is None:
            keys = sorted(value)
            return self.fail(path, f"an object with keys {keys!r}, not a tagged value")
        return read(self, value, path)

    def fail(self, path: str, reason: str) -> object:
        msg = f"cannot read {self.subject}: {path} is {reason}"
        self.errors.append(InvalidInputError(msg, field=path, feature=self.feature))
        return _INVALID

    def resolve(self, name: object, path: str, *, enum: bool) -> type[Any] | None:
        cls = self.types.get(name) if isinstance(name, str) else None
        if cls is None or issubclass(cls, Enum) != enum:
            kind = "an enum" if enum else "a dataclass"
            self.fail(path, f"tagged {name!r}, not {kind} of {self.subject}")
            return None
        return cls

    def items(self, values: object, path: str, tag: str) -> list[Any] | None:
        if not isinstance(values, list):
            self.fail(path, f"a {tag} that is not a list")
            return None
        before = len(self.errors)
        items = [self.read(item, f"{path}[{i}]") for i, item in enumerate(values)]
        return None if len(self.errors) > before else items

    def build(self, cls: type[Any], fields: dict[str, Any], path: str) -> object:
        init = {f.name: f for f in dataclasses.fields(cls) if f.init}
        before = len(self.errors)
        for name in fields.keys() - init.keys():
            self.fail(f"{path}.{name}", f"not a field of {cls.__name__}")
        for name in init.keys() - fields.keys():
            if _required(init[name]):
                self.fail(f"{path}.{name}", f"missing: {cls.__name__} requires it")
        kwargs = {
            name: self.read(value, f"{path}.{name}")
            for name, value in fields.items()
            if name in init
        }
        if len(self.errors) > before:
            return _INVALID
        try:
            return cls(**kwargs)
        except InvalidInputError as exc:
            self.errors.append(_rebased(exc, cls.__name__, path))
        except (ArithmeticError, LookupError, TypeError, ValueError) as exc:
            self.fail(path, f"rejected by {cls.__name__}: {exc}")
        return _INVALID


def _required(spec: dataclasses.Field[Any]) -> bool:
    return (
        spec.default is dataclasses.MISSING
        and spec.default_factory is dataclasses.MISSING
    )


def _rebased(exc: InvalidInputError, owner: str, path: str) -> InvalidInputError:
    """Return ``exc`` with its field moved from ``owner`` to ``path``.

    A constructor names a field after its own class, e.g.
    ``"OvertimeEvent.hours"``; within a tree it is
    ``"PeriodInput.facts.events[1].hours"``.  A field of another owner, or
    none, becomes the path of the node.

    Returns:
        The same error, at its path within the tree.
    """
    rebased = path
    found = exc.field
    if found is not None and (
        found == owner or found.startswith((f"{owner}.", f"{owner}["))
    ):
        rebased = path + found[len(owner) :]
    return InvalidInputError(
        str(exc),
        field=rebased,
        feature=exc.feature,
        ruleset=exc.ruleset,
        remediation=exc.remediation,
    )


def _text(reader: _Reader, value: object, path: str, tag: str) -> str | None:
    if not isinstance(value, str):
        reader.fail(path, f"a {tag} that is not a string")
        return None
    return value


def _decimal(reader: _Reader, value: dict[str, Any], path: str) -> object:
    text = _text(reader, value["$decimal"], path, "$decimal")
    if text is None:
        return _INVALID
    try:
        return Decimal(text)
    except ArithmeticError:
        return reader.fail(path, f"a $decimal {text!r} that is not a number")


def _date(reader: _Reader, value: dict[str, Any], path: str) -> object:
    text = _text(reader, value["$date"], path, "$date")
    if text is None:
        return _INVALID
    try:
        return date.fromisoformat(text)
    except ValueError:
        return reader.fail(path, f"a $date {text!r} that is not an ISO date")


def _tuple(reader: _Reader, value: dict[str, Any], path: str) -> object:
    items = reader.items(value["$tuple"], path, "$tuple")
    return _INVALID if items is None else tuple(items)


def _set(reader: _Reader, value: dict[str, Any], path: str) -> object:
    items = reader.items(value["$set"], path, "$set")
    return _INVALID if items is None else frozenset(items)


def _map(reader: _Reader, value: dict[str, Any], path: str) -> object:
    pairs = value["$map"]
    if not isinstance(pairs, list):
        return reader.fail(path, "a $map that is not a list")
    before = len(reader.errors)
    entries: dict[int | str, Any] = {}
    for i, pair in enumerate(pairs):
        if not _is_entry(pair):
            reader.fail(f"{path}[{i}]", "not an [int or str key, value] pair")
            continue
        key, item = pair
        entries[key] = reader.read(item, f"{path}[{key!r}]")
    return _INVALID if len(reader.errors) > before else entries


def _is_entry(pair: object) -> bool:
    return (
        isinstance(pair, list)
        and len(pair) == 2
        and isinstance(pair[0], (int, str))
        and not isinstance(pair[0], bool)
    )


def _enum(reader: _Reader, value: dict[str, Any], path: str) -> object:
    cls = reader.resolve(value["$enum"], path, enum=True)
    if cls is None:
        return _INVALID
    try:
        return cls(value["value"])
    except ValueError:
        return reader.fail(path, f"{value['value']!r}, not a value of {cls.__name__}")


def _dataclass(reader: _Reader, value: dict[str, Any], path: str) -> object:
    fields = value["fields"]
    if not isinstance(fields, dict):
        return reader.fail(path, "a $type whose fields are not an object")
    cls = reader.resolve(value["$type"], path, enum=False)
    if cls is None:
        return _INVALID
    return reader.build(cls, fields, path)


#: Readers of each tagged shape, keyed by the exact keys of the object.
_READERS: Mapping[frozenset[str], Callable[[_Reader, dict[str, Any], str], object]] = (
    MappingProxyType({
        frozenset({"$decimal"}): _decimal,
        frozenset({"$date"}): _date,
        frozenset({"$tuple"}): _tuple,
        frozenset({"$set"}): _set,
        frozenset({"$map"}): _map,
        frozenset({"$enum", "value"}): _enum,
        frozenset({"$type", "fields"}): _dataclass,
    })
)
