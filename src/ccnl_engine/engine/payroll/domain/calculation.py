"""Calculation provenance: what a payroll computation used and how to replay it.

A :class:`Calculation` wraps the
:class:`~ccnl_engine.engine.payroll.domain.payroll_result.PayrollResult` with everything
needed to reproduce it later: the engine version that ran it, the
identity/version of every ruleset it consumed, and a serialisable snapshot of
the raw inputs. The snapshot can be serialised to JSON and, given the same
(possibly re-loaded) knowledge-base rulesets, replayed through ``compute`` to
yield an identical result years later.
"""

from __future__ import annotations

import dataclasses
import json
import typing
from dataclasses import dataclass, fields
from datetime import date as _date
from decimal import Decimal
from enum import Enum
from types import UnionType
from typing import TYPE_CHECKING, Any, cast, get_origin

from ccnl_engine.engine.payroll.domain.employee import Employee
from ccnl_engine.engine.payroll.domain.employer import Employer
from ccnl_engine.engine.payroll.domain.payroll_result import PayrollResult

if TYPE_CHECKING:
    from ccnl_engine.engine.contract.domain.ccnl import CCNL, TaxSector
    from ccnl_engine.engine.surtax.domain.rules import SurtaxRules
    from ccnl_engine.engine.tax.domain.rules import YearRules

# ---------------------------------------------------------------------------
# JSON-native serialisation of the frozen input dataclasses
# ---------------------------------------------------------------------------

#: Sentinel returned by :func:`_try_union_member` when a member rejects a raw.
_NO_MATCH: object = object()


def _dump_frozenset(value: frozenset[object]) -> list[str]:
    """Serialise a frozenset to a sorted list of strings.

    Returns:
        A sorted list of the string representations of *value*'s members.
    """
    return sorted(str(v) for v in value)


def _dump_dataclass(value: object) -> dict[str, object]:
    """Serialise a dataclass to a ``$type``-tagged dict.

    Returns:
        A dict with ``$type`` set to the class name, plus every field.
    """
    out: dict[str, object] = {"$type": type(value).__name__}
    out.update({
        f.name: _dump(getattr(value, f.name))
        for f in dataclasses.fields(value)  # type: ignore[arg-type]
    })
    return out


def _dump_dict(value: dict[str, object]) -> dict[str, object]:
    """Recursively serialise a dict.

    Returns:
        A new dict with every value serialised via :func:`_dump`.
    """
    return {k: _dump(v) for k, v in value.items()}


def _dump(value: object) -> object:  # ruff: ignore[too-many-return-statements]
    """Convert an input value to a JSON-native object (lossless round-trip).

    Any key named ``source_hash`` is not special here; this helper only shapes
    values for :class:`InputSnapshot`, mirroring :meth:`PayrollResult.to_dict` for
    the richer input dataclasses.

    Returns:
        A JSON-native value: ``str``/``int``/``bool``/``None`` scalars pass
        through, ``Decimal`` becomes its ``str`` form, dates become ISO
        strings, ``Enum`` members become their value, dataclasses become dicts
        tagged with a ``$type`` marker, pydantic models are dumped first.

    Raises:
        TypeError: If *value* is not JSON-serialisable by any of the above.
    """
    if value is None or isinstance(value, (str, int, bool)):
        return value
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, _date):
        return value.isoformat()
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, frozenset):
        return _dump_frozenset(value)
    if isinstance(value, (list, tuple)):
        return [_dump(v) for v in value]
    if dataclasses.is_dataclass(value):
        return _dump_dataclass(value)
    if hasattr(value, "model_dump"):
        return _dump(value.model_dump(mode="json"))
    if isinstance(value, dict):
        return _dump_dict(value)
    msg = f"Cannot serialise input value of type {type(value)!r}"
    raise TypeError(msg)


def _coerce_scalar(raw: object, hint: type) -> object:
    """Coerce a JSON-native *raw* value to the type described by *hint*.

    Returns:
        The coerced value; plain scalars pass through unchanged.
    """
    if hint is Decimal:
        return Decimal(str(raw))
    if hint is _date:
        return _date.fromisoformat(str(raw))
    if isinstance(hint, type) and issubclass(hint, Enum):
        return hint(raw)
    return raw


def _unwrap_annotated(hint: type) -> type:
    """Strip ``Annotated[...]`` wrappers, returning the inner type.

    Returns:
        The unwrapped type, or *hint* unchanged if it is not annotated.
    """
    if get_origin(hint) is typing.Annotated:
        hint, *_ = typing.get_args(hint)
    return hint


def _load_union_hint(hint: type, raw: object) -> object:
    """Load *raw* through a ``Union``/``Optional`` type hint.

    Returns:
        The reconstructed value for the first matching union member.
    """
    args = typing.get_args(hint)
    if type(None) in args and raw is None:
        return None
    non_none = [a for a in args if a is not type(None)]
    if len(non_none) == 1:
        return _load_by_hint(non_none[0], raw)
    return _load_union(non_none, raw)


def _load_collection_hint(hint: type, origin: type, raw: object) -> object:
    """Load *raw* through a ``list``/``tuple``/``frozenset`` type hint.

    Returns:
        The reconstructed collection with every element loaded via
        :func:`_load_by_hint`.
    """
    if origin is frozenset:
        return frozenset(str(item) for item in cast(list[object], raw))
    args = typing.get_args(hint)
    elem_hint = args[0]
    items = [_load_by_hint(elem_hint, item) for item in cast(list[object], raw)]
    if origin is tuple:
        return tuple(items)
    return items


def _load_by_hint(hint: type, raw: object) -> object:
    """Reconstruct an object from a JSON-native *raw* guided by *hint*.

    Returns:
        The reconstructed value for the given type hint.
    """
    hint = _unwrap_annotated(hint)
    origin = get_origin(hint)
    if origin is typing.Union or origin is UnionType:
        return _load_union_hint(hint, raw)
    if origin is not None:
        return _load_collection_hint(hint, origin, raw)
    if dataclasses.is_dataclass(hint):
        return _load_dataclass(hint, raw)
    if isinstance(hint, type) and hasattr(hint, "model_validate"):
        return hint.model_validate(raw)
    return _coerce_scalar(raw, hint)


def _try_union_member(hint: type, raw: object) -> object:
    """Try to load *raw* as *hint*, reporting failure without exceptions.

    Returns:
        The reconstructed value, or :data:`_NO_MATCH` when *hint* rejects the
        input payload.
    """
    if dataclasses.is_dataclass(hint):
        try:
            return _load_dataclass(hint, raw)
        except (TypeError, ValueError):
            return _NO_MATCH
    if isinstance(hint, type) and hasattr(hint, "model_validate"):
        try:
            return hint.model_validate(raw)
        except Exception:  # ruff: ignore[blind-except] - union trial
            return _NO_MATCH
    return _NO_MATCH


def _load_union(member_hints: list[type], raw: object) -> object:
    """Reconstruct a union value from *raw*.

    Dataclass members are matched by the ``$type`` tag recorded by
    :func:`_dump` when present, falling back to trial-loading. Pydantic
    members use their discriminator field via ``model_validate``.

    Returns:
        The first member that successfully loads *raw*.

    Raises:
        ValueError: If no union member accepts the input payload.
    """
    if isinstance(raw, dict):
        tag = raw.get("$type")
        if isinstance(tag, str):
            for hint in member_hints:
                if dataclasses.is_dataclass(hint) and hint.__name__ == tag:
                    return _load_dataclass(hint, raw)
    for hint in member_hints:
        loaded = _try_union_member(hint, raw)
        if loaded is not _NO_MATCH:
            return loaded
    msg = f"No union member matched the input payload for {member_hints!r}."
    raise ValueError(msg)


def _load_dataclass(dc: type, raw: object) -> object:
    """Reconstruct a frozen dataclass from a JSON-native *raw* dict.

    Returns:
        A new instance of *dc* built from the snapshot fields.

    Raises:
        TypeError: If *raw* is not a dict.
        ValueError: If a required field is missing from *raw*.
    """
    if not isinstance(raw, dict):
        msg = f"Expected dict to build {dc.__name__}, got {type(raw)!r}"
        raise TypeError(msg)
    hints = typing.get_type_hints(dc)
    kwargs: dict[str, object] = {}
    for f in fields(dc):
        if f.name not in raw:
            msg = f"Missing field {f.name!r} in {dc.__name__} snapshot"
            raise ValueError(msg)
        kwargs[f.name] = _load_by_hint(hints[f.name], raw[f.name])
    return dc(**kwargs)


def _materialise(
    employee_data: dict[str, object],
    employer_data: dict[str, object] | None,
) -> tuple[Employee, Employer | None]:
    """Rebuild the :class:`Employee` and :class:`Employer` from the snapshot.

    Returns:
        The reconstructed (employee, employer) pair.
    """
    employee = cast(Employee, _load_by_hint(Employee, employee_data))
    employer = cast(
        Employer | None,
        _load_by_hint(Employer, employer_data) if employer_data else None,
    )
    return employee, employer


# ---------------------------------------------------------------------------
# Public snapshot and calculation records
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class InputSnapshot:
    """Serialisable, lossless copy of the inputs to one payroll computation.

    Attributes:
        ccnl_id: Identifier of the CCNL used (mirrors ``PayrollResult.ccnl_id``).
        tax_sector: INPS tax-sector classification used to load tax rules.
        year: Fiscal/tax year of the computation (from ``YearRules.year``).
        uses_surtax: ``True`` when addizionale rules were applied.
        employee: JSON-native serialisation of the :class:`Employee`.
        employer: JSON-native serialisation of the :class:`Employer`, or
            ``None`` when no employer-side inputs were given.
    """

    ccnl_id: str
    tax_sector: str
    year: int
    uses_surtax: bool
    employee: dict[str, object]
    employer: dict[str, object] | None = None

    @classmethod
    def capture(
        cls,
        employee: Employee,
        employer: Employer | None,
        ccnl_id: str,
        tax_sector: TaxSector,
        year: int,
        uses_surtax: bool,
    ) -> InputSnapshot:
        """Build a snapshot from live input objects.

        Returns:
            A new snapshot carrying the JSON-native copies of the inputs.
        """
        return cls(
            ccnl_id=ccnl_id,
            tax_sector=str(tax_sector),
            year=year,
            uses_surtax=uses_surtax,
            employee=cast(dict[str, object], _dump(employee)),
            employer=(
                cast(dict[str, object], _dump(employer))
                if employer is not None
                else None
            ),
        )

    def materialise(self) -> tuple[Employee, Employer | None]:
        """Rebuild the :class:`Employee` and :class:`Employer` objects.

        Returns:
            The tuple ``(employee, employer)`` restored from the snapshot.
        """
        return _materialise(self.employee, self.employer)

    def to_dict(self) -> dict[str, object]:
        """Serialise the snapshot to a JSON-native dict.

        Returns:
            A dictionary with ``str``/``int``/``bool``/``dict``/``None`` values.
        """
        return {
            "ccnl_id": self.ccnl_id,
            "tax_sector": self.tax_sector,
            "year": self.year,
            "uses_surtax": self.uses_surtax,
            "employee": self.employee,
            "employer": self.employer,
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> InputSnapshot:
        """Reconstruct a snapshot from a dictionary (see :meth:`to_dict`).

        Args:
            data: A dictionary as produced by :meth:`to_dict`.

        Returns:
            A new :class:`InputSnapshot` equal to the original.
        """
        return cls(
            ccnl_id=str(data["ccnl_id"]),
            tax_sector=str(data["tax_sector"]),
            year=int(str(data["year"])),
            uses_surtax=bool(data["uses_surtax"]),
            employee=cast(dict[str, object], data["employee"]),
            employer=cast(dict[str, object] | None, data.get("employer")),
        )

    def to_json(self) -> str:
        """Serialise the snapshot to a JSON string.

        Returns:
            A compact JSON string (see :meth:`to_dict` for the encoding).
        """
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, raw: str) -> InputSnapshot:
        """Reconstruct a snapshot from a JSON string.

        Args:
            raw: JSON returned by :meth:`to_json`.

        Returns:
            A new :class:`InputSnapshot` equal to the original.
        """
        return cls.from_dict(json.loads(raw))


@dataclass(frozen=True)
class Calculation:
    """A payroll computation together with everything needed to replay it.

    Attributes:
        engine_version: Version of the engine library that produced this
            calculation (see :mod:`ccnl_engine.version`).
        ruleset_version: Mapping of ruleset kind (``ccnl``, ``tax``, ``surtax``)
            to the ``id@version`` identity of the ruleset that was used.
        input_snapshot: Lossless copy of the raw inputs.
        result: The resulting :class:`PayrollResult`.
    """

    engine_version: str
    ruleset_version: dict[str, str]
    input_snapshot: InputSnapshot
    result: PayrollResult

    def __getattr__(self, name: str) -> Any:  # ruff: ignore[any-type] - delegation
        """Forward unknown attribute reads to ``result`` (the PayrollResult).

        Accessing ``Calculation.net_annual`` therefore reads
        ``Calculation.result.net_annual``, keeping call sites that treat the
        output as a :class:`PayrollResult` working unchanged.

        Returns:
            The attribute value read from :attr:`result`.
        """
        return getattr(self.result, name)

    def reproduce(
        self,
        ccnl: CCNL,
        rules: YearRules,
        surtax: SurtaxRules | None = None,
    ) -> Calculation:
        """Replay this calculation against the given (re-loaded) rulesets.

        ``ccnl``, ``rules`` and ``surtax`` must be loaded from the knowledge
        base at the versions recorded in :attr:`ruleset_version`; the
        :class:`Employee` and :class:`Employer` are rebuilt from the snapshot.
        The returned :class:`Calculation` will carry the same inputs and an
        identical :attr:`result`.

        Args:
            ccnl: The CCNL ruleset to replay against.
            rules: The tax/INPS ruleset to replay against.
            surtax: The surtax ruleset to replay against, or ``None`` if the
                original calculation did not use one.

        Returns:
            A new :class:`Calculation` equal to the original.
        """
        from ccnl_engine.engine.payroll.service.orchestrator import (  # ruff: ignore[import-outside-top-level] - import cycle
            compute,
        )

        employee, employer = self.input_snapshot.materialise()
        return compute(
            ccnl,
            rules,
            employee,
            employer=employer,
            surtax=surtax,
        )

    def to_dict(self) -> dict[str, object]:
        """Serialise the full calculation to a JSON-native dict.

        Returns:
            A dictionary with the provenance fields, the input snapshot and
            the payroll result.
        """
        return {
            "engine_version": self.engine_version,
            "ruleset_version": dict(sorted(self.ruleset_version.items())),
            "input_snapshot": self.input_snapshot.to_dict(),
            "result": self.result.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> Calculation:
        """Reconstruct a calculation from a dictionary (see :meth:`to_dict`).

        Args:
            data: A dictionary as produced by :meth:`to_dict`.

        Returns:
            A new :class:`Calculation` equal to the original.
        """
        return cls(
            engine_version=str(data["engine_version"]),
            ruleset_version={
                str(k): str(v)
                for k, v in cast(dict[str, object], data["ruleset_version"]).items()
            },
            input_snapshot=InputSnapshot.from_dict(
                cast(dict[str, object], data["input_snapshot"])
            ),
            result=PayrollResult.from_dict(cast(dict[str, object], data["result"])),
        )

    def to_json(self) -> str:
        """Serialise the calculation to a JSON string.

        Returns:
            A compact JSON string (see :meth:`to_dict` for the encoding).
        """
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, raw: str) -> Calculation:
        """Reconstruct a calculation from a JSON string.

        Args:
            raw: JSON returned by :meth:`to_json`.

        Returns:
            A new :class:`Calculation` equal to the original.
        """
        return cls.from_dict(json.loads(raw))
