"""Calculation provenance: what a payroll computation used and how to replay it.

A :class:`Calculation` wraps the
:class:`~ccnl_engine.engine.payroll.domain.payroll_result.PayrollResult` with
everything needed to reproduce it later: the engine version that ran it, the
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
from enum import Enum, StrEnum
from types import UnionType
from typing import TYPE_CHECKING, Any, cast, get_origin

from ccnl_engine.engine.payroll.domain.payroll_result import PayrollResult
from ccnl_engine.engine.payroll.domain.scenario import PayrollScenario

if TYPE_CHECKING:
    from ccnl_engine.engine.contract.domain.ccnl import TaxSector

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
    values for :class:`InputSnapshot`, mirroring :meth:`PayrollResult.to_dict`
    for the richer input dataclasses.

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

    Fields with dataclass defaults are skipped when absent from *raw* so that
    old serialised snapshots remain readable after new defaulted fields are added.

    Returns:
        A new instance of *dc* built from the snapshot fields.

    Raises:
        TypeError: If *raw* is not a dict.
        ValueError: If a required field (no default) is missing from *raw*.
    """
    if not isinstance(raw, dict):
        msg = f"Expected dict to build {dc.__name__}, got {type(raw)!r}"
        raise TypeError(msg)
    hints = typing.get_type_hints(dc)
    kwargs: dict[str, object] = {}
    for f in fields(dc):
        if f.name not in raw:
            has_default = (
                f.default is not dataclasses.MISSING
                or f.default_factory is not dataclasses.MISSING
            )
            if has_default:
                continue
            msg = f"Missing field {f.name!r} in {dc.__name__} snapshot"
            raise ValueError(msg)
        kwargs[f.name] = _load_by_hint(hints[f.name], raw[f.name])
    return dc(**kwargs)


def _materialise(
    scenario_data: dict[str, object],
) -> PayrollScenario:
    """Rebuild the :class:`PayrollScenario` from the snapshot.

    Returns:
        The reconstructed :class:`PayrollScenario`.
    """
    return cast(PayrollScenario, _load_by_hint(PayrollScenario, scenario_data))


# ---------------------------------------------------------------------------
# Calculation trace
# ---------------------------------------------------------------------------


class TraceCategory(StrEnum):
    """Semantic category of a single payroll computation step."""

    # --- Gross chain (monthly amounts) ---
    BASE_SALARY = "base_salary"
    SENIORITY = "seniority"
    ALLOWANCE = "allowance"
    AD_PERSONAM = "ad_personam"
    SECOND_LEVEL = "second_level"
    RAL_OVERRIDE = "ral_override"
    GROSS = "gross"
    # Layer 3 supplement steps (sit after GROSS; do not alter its invariant)
    TIME_SUPPLEMENT = "time_supplement"
    SUPPLEMENT_TOTAL = "supplement_total"

    # --- Fiscal chain (annual amounts) ---
    INPS_EMPLOYEE = "inps_employee"
    INPS_EMPLOYER = "inps_employer"
    TFR = "tfr"
    EMPLOYER_FUNDS = "employer_funds"
    TAXABLE_INCOME = "taxable_income"
    IRPEF_GROSS = "irpef_gross"
    WORK_DEDUCTION = "work_deduction"
    FAMILY_DEDUCTION = "family_deduction"
    ART15_DEDUCTION = "art15_deduction"
    IRPEF_NET = "irpef_net"
    ADDIZIONALE_REGIONALE = "addizionale_regionale"
    ADDIZIONALE_COMUNALE = "addizionale_comunale"
    TRATTAMENTO_INTEGRATIVO = "trattamento_integrativo"
    NET = "net"


@dataclass(frozen=True)
class TraceStep:
    """One step in a payroll computation chain.

    Attributes:
        category: Semantic category of the step.
        label: Human-readable label (e.g. ``"Base retributiva"``,
            ``"IRPEF netta"``).
        amount: Amount contributed by this step, post-scaling.
            Gross-chain steps are monthly; fiscal-chain steps are annual.
            Check ``period`` to know which applies.
        detail: Optional machine-readable reference (e.g. allowance code,
            ``"scatti=3"``, ``"IV@H011"``).
        period: Whether ``amount`` is a monthly or annual figure.
            Defaults to ``"monthly"`` for backward compatibility with
            serialised gross-chain traces.
    """

    category: TraceCategory
    label: str
    amount: Decimal
    detail: str | None = None
    period: str = "monthly"  # Literal["monthly", "annual"]

    def to_dict(self) -> dict[str, object]:
        """Serialise to a JSON-native dict.

        Returns:
            A dict with ``str``/``None`` values; ``amount`` as its string
            form to avoid floating-point loss.
        """
        return {
            "category": self.category.value,
            "label": self.label,
            "amount": str(self.amount),
            "detail": self.detail,
            "period": self.period,
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> TraceStep:
        """Reconstruct from a :meth:`to_dict` dict.

        Older serialised steps without ``period`` default to ``"monthly"``.

        Args:
            data: A dict as produced by :meth:`to_dict`.

        Returns:
            A new :class:`TraceStep` equal to the original.
        """
        raw_detail = data.get("detail")
        return cls(
            category=TraceCategory(str(data["category"])),
            label=str(data["label"]),
            amount=Decimal(str(data["amount"])),
            detail=str(raw_detail) if raw_detail is not None else None,
            period=str(data.get("period", "monthly")),
        )


@dataclass(frozen=True)
class CalculationTrace:
    """Ordered record of the gross and fiscal computation steps.

    **Gross chain** (``steps``): monthly amounts from base salary through to
    the gross total.  The ``GROSS`` step is always last and equals the sum of
    all preceding entries — the engine enforces this invariant at construction
    time.  L3 supplement steps sit in ``supplement_steps`` and do not alter
    the ``GROSS`` invariant.

    **Fiscal chain** (``fiscal_steps``): annual amounts from gross through to
    net.  This is a *derivation* chain, not a sum: each step shows the
    derivation formula rather than a contribution. The canonical identity is::

        net_annual = gross_annual
                   - inps_employee_annual
                   - irpef_net
                   - addizionale_regionale_annual
                   - addizionale_comunale_annual
                   + trattamento_integrativo

    Steps that were omitted (e.g. addizionali when no jurisdiction was
    supplied) are still emitted with ``amount=0`` so the skeleton is stable
    across runs and diffs cleanly.

    Attributes:
        steps: Ordered gross-chain steps (monthly), ending with ``GROSS``.
        supplement_steps: Optional L3 supplement steps (monthly). Empty when
            no supplement input is provided.
        fiscal_steps: Ordered fiscal-chain steps (annual). Empty when not
            yet emitted (pre-2025 serialised calculations).
    """

    steps: tuple[TraceStep, ...]
    supplement_steps: tuple[TraceStep, ...] = ()
    fiscal_steps: tuple[TraceStep, ...] = ()

    def to_dict(self) -> dict[str, object]:
        """Serialise to a JSON-native dict.

        Returns:
            A dict with ``steps``, ``supplement_steps``, and ``fiscal_steps``
            lists.  Empty optional sequences are omitted.
        """
        out: dict[str, object] = {"steps": [s.to_dict() for s in self.steps]}
        if self.supplement_steps:
            out["supplement_steps"] = [s.to_dict() for s in self.supplement_steps]
        if self.fiscal_steps:
            out["fiscal_steps"] = [s.to_dict() for s in self.fiscal_steps]
        return out

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> CalculationTrace:
        """Reconstruct from a :meth:`to_dict` dict.

        Older serialised calculations without ``supplement_steps`` or
        ``fiscal_steps`` yield empty tuples for those fields.

        Args:
            data: A dict as produced by :meth:`to_dict`.

        Returns:
            A new :class:`CalculationTrace` equal to the original.
        """
        return cls(
            steps=tuple(
                TraceStep.from_dict(cast(dict[str, object], s))
                for s in cast(list[object], data.get("steps", []))
            ),
            supplement_steps=tuple(
                TraceStep.from_dict(cast(dict[str, object], s))
                for s in cast(list[object], data.get("supplement_steps", []))
            ),
            fiscal_steps=tuple(
                TraceStep.from_dict(cast(dict[str, object], s))
                for s in cast(list[object], data.get("fiscal_steps", []))
            ),
        )


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
        scenario: JSON-native serialisation of the :class:`PayrollScenario`.
    """

    ccnl_id: str
    tax_sector: str
    year: int
    uses_surtax: bool
    scenario: dict[str, object]

    @classmethod
    def capture(
        cls,
        scenario: PayrollScenario,
        ccnl_id: str,
        tax_sector: TaxSector,
        year: int,
        uses_surtax: bool,
    ) -> InputSnapshot:
        """Build a snapshot from a live :class:`PayrollScenario`.

        Returns:
            A new snapshot carrying the JSON-native copy of the scenario.
        """
        return cls(
            ccnl_id=ccnl_id,
            tax_sector=str(tax_sector),
            year=year,
            uses_surtax=uses_surtax,
            scenario=cast(dict[str, object], _dump(scenario)),
        )

    def materialise(self) -> PayrollScenario:
        """Rebuild the :class:`PayrollScenario` from the snapshot.

        Returns:
            The reconstructed :class:`PayrollScenario`.
        """
        return _materialise(self.scenario)

    def to_dict(self) -> dict[str, object]:
        """Serialise the snapshot to a JSON-native dict.

        Returns:
            A dictionary with ``str``/``int``/``bool``/``dict`` values.
        """
        return {
            "ccnl_id": self.ccnl_id,
            "tax_sector": self.tax_sector,
            "year": self.year,
            "uses_surtax": self.uses_surtax,
            "scenario": self.scenario,
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
            scenario=cast(dict[str, object], data["scenario"]),
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
        trace: Step-by-step record of the monthly gross computation chain.
            An empty trace signals that the calculation was produced by an
            older engine version that did not emit one.
    """

    engine_version: str
    ruleset_version: dict[str, str]
    input_snapshot: InputSnapshot
    result: PayrollResult
    trace: CalculationTrace = dataclasses.field(
        default_factory=lambda: CalculationTrace(steps=())
    )

    def __getattr__(self, name: str) -> Any:  # ruff: ignore[any-type] - delegation
        """Forward unknown attribute reads to ``result`` (the PayrollResult).

        Accessing ``Calculation.net_annual`` therefore reads
        ``Calculation.result.net_annual``, keeping call sites that treat the
        output as a :class:`PayrollResult` working unchanged.

        Returns:
            The attribute value read from :attr:`result`.
        """
        return getattr(self.result, name)

    def reproduce(self) -> Calculation:
        """Replay this calculation using the scenario stored in the snapshot.

        The :class:`PayrollScenario` is rebuilt from the snapshot and passed
        back through :func:`~ccnl_engine.engine.payroll.service.orchestrator\
.compute`, which re-loads the rulesets from the currently installed knowledge
        base. The returned :class:`Calculation` will carry the same inputs and
        an identical :attr:`result` when the knowledge base has not changed.

        Returns:
            A new :class:`Calculation` equal to the original.
        """
        from ccnl_engine.engine.payroll.service.orchestrator import (  # ruff: ignore[import-outside-top-level] - import cycle
            compute,
        )

        scenario = self.input_snapshot.materialise()
        return compute(scenario)

    def to_dict(self) -> dict[str, object]:
        """Serialise the full calculation to a JSON-native dict.

        Returns:
            A dictionary with the provenance fields, the input snapshot,
            the payroll result, and the computation trace.
        """
        return {
            "engine_version": self.engine_version,
            "ruleset_version": dict(sorted(self.ruleset_version.items())),
            "input_snapshot": self.input_snapshot.to_dict(),
            "result": self.result.to_dict(),
            "trace": self.trace.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> Calculation:
        """Reconstruct a calculation from a dictionary (see :meth:`to_dict`).

        Older serialised calculations that pre-date the trace field are
        accepted: a missing ``trace`` key yields an empty
        :class:`CalculationTrace`.

        Args:
            data: A dictionary as produced by :meth:`to_dict`.

        Returns:
            A new :class:`Calculation` equal to the original.
        """
        raw_trace = data.get("trace")
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
            trace=(
                CalculationTrace.from_dict(cast(dict[str, object], raw_trace))
                if raw_trace is not None
                else CalculationTrace(steps=())
            ),
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
