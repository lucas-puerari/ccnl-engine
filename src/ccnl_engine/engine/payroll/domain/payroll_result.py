"""AnnualEstimate and PeriodPayroll — result types of compute()."""

from __future__ import annotations

import dataclasses
import json
import types
import typing
from dataclasses import dataclass, field
from datetime import date as _date
from decimal import Decimal
from typing import TYPE_CHECKING, Literal, cast

from ccnl_engine.engine.metadata.domain.rules import RulesetIdentity
from ccnl_engine.engine.payroll.domain.fiscal import FiscalSimplification
from ccnl_engine.engine.provenance.domain.chain import RuleProvenance
from ccnl_engine.engine.serialization.codec import (
    _STRICT_PRIMITIVES,
    _validate_primitive,
)

if TYPE_CHECKING:
    from ccnl_engine.engine.payroll.domain.scenario import PeriodPayrollInput

_ZERO = Decimal(0)


@dataclass(frozen=True)
class ScopeItem:
    """One entry in the calculation scope list.

    Four orthogonal axes describe how a feature was handled:

    ``calculation_status``
        Whether the engine computed the feature (``"computed"``), partially
        computed it (``"partial"``), could not compute it (``"not_computed"``),
        or the caller did not request it (``"excluded"``).

    ``integration_status``
        How the computed amount relates to the period totals:
        ``"included_in_totals"`` when it affects net/gross, ``"informational_only"``
        when it is reported but not wired into the net formula, ``"n_a"`` for
        excluded or not-computed features.

    ``eligibility_status``
        Verification level of the inputs that triggered the computation:
        ``"engine_verified"`` when the engine could check all inputs,
        ``"caller_declared"`` when the caller asserted conditions the engine
        cannot verify (e.g. dependent eligibility, disability certification),
        ``"unknown"`` when the engine has no schema to check against, ``"n_a"``
        otherwise.

    ``source_quality``
        Quality of the normative data source behind the computation:
        ``"verified_primary"`` for a verified primary source, ``"unverified"``
        for an unverified or secondary source, ``"estimated"`` for a derived or
        estimated rule, ``"n_a"`` when no source applies.

    ``assumptions``
        Typed simplification flags active for this feature (e.g.
        ``"partial_detrazioni_art15"``).
    """

    feature: str
    calculation_status: Literal["computed", "partial", "not_computed", "excluded"]
    integration_status: Literal["included_in_totals", "informational_only", "n_a"]
    eligibility_status: Literal["engine_verified", "caller_declared", "unknown", "n_a"]
    source_quality: Literal["verified_primary", "unverified", "estimated", "n_a"]
    assumptions: tuple[str, ...] = ()


def _unwrap_optional(raw: object, hint: type) -> tuple[object, type]:
    """If *hint* is ``X | None``, return (raw, X) — or (None, hint) when raw is None.

    Returns:
        A (raw, concrete_hint) pair with the ``None`` arm stripped.
    """
    origin = typing.get_origin(hint)
    args = typing.get_args(hint)
    if origin in {typing.Union, types.UnionType} and type(None) in args:
        if raw is None:
            return None, hint
        return raw, next(a for a in args if a is not type(None))
    return raw, hint


_CALC_STATUSES = frozenset({"computed", "partial", "not_computed", "excluded"})
_INTEG_STATUSES = frozenset({"included_in_totals", "informational_only", "n_a"})
_ELIG_STATUSES = frozenset({"engine_verified", "caller_declared", "unknown", "n_a"})
_QUAL_STATUSES = frozenset({"verified_primary", "unverified", "estimated", "n_a"})


def _coerce_scope_item(raw: dict[str, object]) -> ScopeItem:
    """Reconstruct a :class:`ScopeItem` from a dict, validating field types.

    Returns:
        A new :class:`ScopeItem` with validated axis fields.

    Raises:
        TypeError: When ``feature`` is not a ``str``.
        ValueError: When any axis field holds an invalid literal value.
    """
    feature = raw["feature"]
    if not isinstance(feature, str):
        msg = f"ScopeItem.feature must be str, got {type(feature).__name__!r}"
        raise TypeError(msg)
    calc = raw["calculation_status"]
    if calc not in _CALC_STATUSES:
        msg = f"ScopeItem.calculation_status must be one of {sorted(_CALC_STATUSES)!r}"
        raise ValueError(msg)
    integ = raw["integration_status"]
    if integ not in _INTEG_STATUSES:
        msg = f"ScopeItem.integration_status must be one of {sorted(_INTEG_STATUSES)!r}"
        raise ValueError(msg)
    elig = raw["eligibility_status"]
    if elig not in _ELIG_STATUSES:
        msg = f"ScopeItem.eligibility_status must be one of {sorted(_ELIG_STATUSES)!r}"
        raise ValueError(msg)
    qual = raw["source_quality"]
    if qual not in _QUAL_STATUSES:
        msg = f"ScopeItem.source_quality must be one of {sorted(_QUAL_STATUSES)!r}"
        raise ValueError(msg)
    raw_assumptions = raw.get("assumptions") or []
    assumptions = tuple(str(a) for a in raw_assumptions)  # type: ignore[attr-defined]
    return ScopeItem(
        feature=feature,
        calculation_status=calc,  # type: ignore[arg-type]
        integration_status=integ,  # type: ignore[arg-type]
        eligibility_status=elig,  # type: ignore[arg-type]
        source_quality=qual,  # type: ignore[arg-type]
        assumptions=assumptions,
    )


def _coerce_scalar(raw: object, hint: type) -> object:
    """Coerce a non-None *raw* to a scalar *hint* type.

    Primitive types (``bool``, ``int``, ``str``) are delegated to
    :func:`_validate_primitive`, which raises ``TypeError`` on mismatch.
    :class:`ScopeItem` reconstruction is delegated to
    :func:`_coerce_scope_item`.

    Returns:
        The coerced value, or *raw* when no coercion applies.
    """
    if hint is Decimal:
        return Decimal(str(raw))
    if hint is _date:
        return _date.fromisoformat(raw)  # type: ignore[arg-type]
    if isinstance(hint, type) and hasattr(hint, "model_validate"):
        return hint.model_validate(raw)
    if hint is ScopeItem and isinstance(raw, dict):
        return _coerce_scope_item(cast(dict[str, object], raw))
    if hint == frozenset[FiscalSimplification]:
        return frozenset(FiscalSimplification(v) for v in cast(list[str], raw))
    return _validate_primitive(raw, hint) if hint in _STRICT_PRIMITIVES else raw


def _coerce(raw: object, hint: type) -> object:
    """Coerce *raw* to the Python type described by the annotation *hint*.

    Handles ``X | None`` unions, ``Decimal``, ``date``,
    ``frozenset[FiscalSimplification]``, ``Literal``, and tuples of
    :class:`RuleProvenance`; everything else is returned as-is.

    Returns:
        The coerced value, or *raw* unchanged when no coercion applies.

    Raises:
        TypeError: When a tuple field value is not a JSON array.
        ValueError: When *raw* is not a member of a ``Literal`` hint.
    """
    raw, hint = _unwrap_optional(raw, hint)
    if raw is None:
        return None
    origin = typing.get_origin(hint)
    args = typing.get_args(hint)
    if origin is typing.Literal:
        if raw not in args:
            msg = f"expected one of {args!r}, got {raw!r}"
            raise ValueError(msg)
        return raw
    if origin is tuple and args:
        if not isinstance(raw, list):
            msg = f"expected a JSON array for tuple field, got {type(raw).__name__!r}"
            raise TypeError(msg)
        return tuple(_coerce(item, args[0]) for item in cast(list[object], raw))
    return _coerce_scalar(raw, hint)


def _serialise_value(value: object) -> object:  # noqa: PLR0911  # noqa: PLR0911
    """Recursively serialise a value to a JSON-native type.

    Returns:
        A JSON-serialisable representation of *value*.
    """
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, _date):
        return value.isoformat()
    if isinstance(value, frozenset):
        return sorted(str(v) for v in value)
    if isinstance(value, tuple):
        return [_serialise_value(v) for v in value]
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return _serialise_dataclass(value)
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    return value


def _serialise_dataclass(obj: object) -> dict[str, object]:
    """Serialise a dataclass instance to a plain dict.

    Returns:
        A dict with each field serialised via :func:`_serialise_value`.
    """
    out: dict[str, object] = {}
    for f in dataclasses.fields(obj):  # type: ignore[arg-type]
        out[f.name] = _serialise_value(getattr(obj, f.name))
    return out


# ---------------------------------------------------------------------------
# Sub-objects
# ---------------------------------------------------------------------------


@dataclass(frozen=True, kw_only=True)
class Earnings:
    """Gross pay breakdown: base, seniority, allowances, and summary totals."""

    seniority_count: int
    base_monthly: Decimal
    seniority_monthly: Decimal
    allowances_monthly: Decimal
    ad_personam_monthly: Decimal
    second_level_monthly: Decimal
    gross_monthly: Decimal
    gross_annual: Decimal
    hourly_rate: Decimal
    apprenticeship_pct: Decimal | None
    apprenticeship_under_level_code: str | None

    def to_dict(self) -> dict[str, object]:
        """Serialise to a plain dict.

        Returns:
            Dict with Decimal fields as strings, None preserved.
        """
        return _serialise_dataclass(self)

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> Earnings:
        """Reconstruct from a serialised dict.

        Returns:
            A new :class:`Earnings` with all fields restored.
        """
        hints = typing.get_type_hints(cls)
        fields = {
            f.name: _coerce(data[f.name], hints[f.name])
            for f in dataclasses.fields(cls)
        }
        return cls(**fields)  # type: ignore[arg-type]


@dataclass(frozen=True, kw_only=True)
class Contributions:
    """Employee and employer social contributions for the year."""

    inps_employee_annual: Decimal
    inps_employer_annual: Decimal
    inail_employer_annual: Decimal
    employer_funds_annual: Decimal
    tfr_annual: Decimal
    bilateral_employee_annual: Decimal
    bilateral_employer_annual: Decimal

    def to_dict(self) -> dict[str, object]:
        """Serialise to a plain dict.

        Returns:
            Dict with Decimal fields as strings.
        """
        return _serialise_dataclass(self)

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> Contributions:
        """Reconstruct from a serialised dict.

        Returns:
            A new :class:`Contributions` with all fields restored.
        """
        hints = typing.get_type_hints(cls)
        fields = {
            f.name: _coerce(data[f.name], hints[f.name])
            for f in dataclasses.fields(cls)
        }
        return cls(**fields)  # type: ignore[arg-type]


@dataclass(frozen=True, kw_only=True)
class Taxes:
    """IRPEF chain, addizionali, and fiscal deductions."""

    taxable_income: Decimal
    irpef_gross: Decimal
    work_income_deduction: Decimal
    ulteriore_detrazione_lavoro: Decimal
    somma_esente: Decimal
    irpef_net: Decimal
    employer_withholds_irpef: bool
    addizionale_regionale_annual: Decimal
    addizionale_comunale_annual: Decimal
    trattamento_integrativo: Decimal
    fiscal_simplifications: frozenset[FiscalSimplification]
    family_deduction_spouse_annual: Decimal
    family_deduction_children_annual: Decimal
    family_deduction_other_annual: Decimal
    family_deduction_annual: Decimal
    unused_family_deduction_annual: Decimal
    art15_deduction_annual: Decimal
    unused_art15_deduction_annual: Decimal
    sterilizzazione_clawback_annual: Decimal

    def to_dict(self) -> dict[str, object]:
        """Serialise to a plain dict.

        Returns:
            Dict with Decimal fields as strings, frozenset as sorted list.
        """
        return _serialise_dataclass(self)

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> Taxes:
        """Reconstruct from a serialised dict.

        Returns:
            A new :class:`Taxes` with all fields restored.
        """
        hints = typing.get_type_hints(cls)
        fields = {
            f.name: _coerce(data[f.name], hints[f.name])
            for f in dataclasses.fields(cls)
        }
        return cls(**fields)  # type: ignore[arg-type]


@dataclass(frozen=True, kw_only=True)
class EmployerCost:
    """Total annual employer cost."""

    employer_cost_annual: Decimal

    def to_dict(self) -> dict[str, object]:
        """Serialise to a plain dict.

        Returns:
            Dict with employer_cost_annual as string.
        """
        return _serialise_dataclass(self)

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> EmployerCost:
        """Reconstruct from a serialised dict.

        Returns:
            A new :class:`EmployerCost` with all fields restored.
        """
        hints = typing.get_type_hints(cls)
        fields = {
            f.name: _coerce(data[f.name], hints[f.name])
            for f in dataclasses.fields(cls)
        }
        return cls(**fields)  # type: ignore[arg-type]


@dataclass(frozen=True, kw_only=True)
class Coverage:
    """Computation quality and coverage metadata.

    ``consumed_rulesets`` records the exact identity of every policy consumed
    during the computation.  A ``None`` entry means a ruleset was consumed but
    its identity is absent or incomplete (treated as unverified).
    """

    status: Literal["partial", "complete"]
    confidence: Literal["low", "medium", "high"]
    calculation_scope: tuple[ScopeItem, ...]
    warnings: tuple[str, ...]
    consumed_rulesets: tuple[RulesetIdentity | None, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, object]:
        """Serialise to a plain dict.

        Returns:
            Dict with tuples serialised as lists.
        """
        return _serialise_dataclass(self)

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> Coverage:
        """Reconstruct from a serialised dict.

        Returns:
            A new :class:`Coverage` with all fields restored.
        """
        hints = typing.get_type_hints(cls)
        kwargs: dict[str, object] = {}
        for f in dataclasses.fields(cls):
            if f.name not in data:
                continue  # use dataclass default
            kwargs[f.name] = _coerce(data[f.name], hints[f.name])
        return cls(**kwargs)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------


def _has_default(f: dataclasses.Field[object]) -> bool:
    no_default = f.default is dataclasses.MISSING
    no_factory = f.default_factory is dataclasses.MISSING
    return not (no_default and no_factory)


_SUB_OBJECT_DECODERS: dict[
    str, type[Earnings | Contributions | Taxes | EmployerCost | Coverage]
] = {
    "earnings": Earnings,
    "contributions": Contributions,
    "taxes": Taxes,
    "employer_cost": EmployerCost,
    "coverage": Coverage,
}


def _decode_field(
    name: str,
    raw: object,
    hint: type,
    extra_decoders: dict[str, object] | None = None,
) -> object:
    """Coerce *raw* to the type expected for field *name*.

    Returns:
        The decoded value from a sub-object decoder or :func:`_coerce`.
    """
    if isinstance(raw, dict):
        decoder = _SUB_OBJECT_DECODERS.get(name)
        if decoder is not None:
            return decoder.from_dict(cast(dict[str, object], raw))
        if extra_decoders:
            extra = extra_decoders.get(name)
            if callable(extra):
                return extra(raw)
    return _coerce(raw, hint)


@dataclass(frozen=True, kw_only=True)
class AnnualEstimate:
    """Annual gross-to-net and employer-cost estimate for one payroll scenario.

    All monetary amounts are in EUR. Annual figures assume the contract-wide
    ``additional_months`` pay structure (typically 13 or 14 months).

    Attributes:
        ccnl_id: Identifier of the CCNL used (from ``CCNLMeta.id``).
        level_code: Classification level code used for the computation.
        employment_type: String tag of the employment type
            (``"permanent"``, ``"fixed_term"``, or ``"apprentice"``).
        part_time_pct: Part-time coefficient applied to gross and
            contribution bases.  ``1`` for a full-time worker.
        as_of: Reference date used to resolve all time-series values.
        year: Calendar year of the pay period.
        contract_effective_date: Date from which the applicable CCNL
            salary rates are effective.  Equal to ``as_of`` when the
            contract rate period started on or before the reference date.
        tax_rule_year: Calendar year used to load IRPEF brackets and
            contribution rules.  May differ from ``year`` when an explicit
            ``tax_year`` override was passed to the scenario.
        earnings: Gross pay breakdown: base, seniority, allowances, total.
        contributions: Employee and employer social contributions.
        taxes: IRPEF chain, addizionali, and fiscal deductions.
        employer_cost: Total annual employer cost.
        coverage: Computation quality, scope, and consumed-policy identity.
        provenance: Ordered provenance of salary rules consumed.
        net_annual: Annual net pay.
        net_monthly: Monthly net pay (``net_annual / additional_months``).
        schema_version: Serialisation schema version.
    """

    ccnl_id: str
    level_code: str
    employment_type: str
    part_time_pct: Decimal
    as_of: _date
    year: int
    contract_effective_date: _date
    tax_rule_year: int

    earnings: Earnings
    contributions: Contributions
    taxes: Taxes
    employer_cost: EmployerCost
    coverage: Coverage
    provenance: tuple[RuleProvenance, ...]

    net_annual: Decimal
    net_monthly: Decimal

    schema_version: str = field(default="2")

    def to_dict(self) -> dict[str, object]:
        """Serialise to a plain Python dictionary.

        All ``Decimal`` amounts are converted to ``str``.  ``date`` fields are
        ISO-8601 strings.  Sub-objects are serialised as nested dicts.
        ``RuleProvenance`` entries use ``model_dump(mode="json")``.

        Returns:
            A dictionary with only JSON-native types.
        """
        out: dict[str, object] = {}
        for f in dataclasses.fields(self):
            value = getattr(self, f.name)
            out[f.name] = _serialise_value(value)
        return out

    def to_json(self) -> str:
        """Serialise to a JSON string.

        Returns:
            A compact JSON string. See :meth:`to_dict` for encoding rules.
        """
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> AnnualEstimate:
        """Reconstruct from a ``to_dict()`` dict.

        Args:
            data: A dictionary as produced by :meth:`to_dict`.

        Returns:
            A new :class:`AnnualEstimate` with all fields restored.

        Raises:
            TypeError: If *data* contains unexpected keys.
            ValueError: If a required field is absent from *data*.
        """
        allowed = frozenset(f.name for f in dataclasses.fields(cls))
        extra = set(data) - allowed
        if extra:
            msg = f"AnnualEstimate.from_dict: unexpected keys: {sorted(extra)}"
            raise TypeError(msg)
        hints = typing.get_type_hints(cls)
        kwargs: dict[str, object] = {}
        for f in dataclasses.fields(cls):
            if f.name not in data:
                if _has_default(f):
                    continue
                msg = f"Missing field: {f.name!r}"
                raise ValueError(msg) from None
            kwargs[f.name] = _decode_field(f.name, data[f.name], hints[f.name])
        return cls(**kwargs)  # type: ignore[arg-type]

    @classmethod
    def from_json(cls, raw: str) -> AnnualEstimate:
        """Reconstruct from a JSON string.

        Args:
            raw: A JSON string as returned by :meth:`to_json`.

        Returns:
            A new :class:`AnnualEstimate` equal to the original.
        """
        return cls.from_dict(json.loads(raw))


@dataclass(frozen=True, kw_only=True)
class PeriodPayroll(AnnualEstimate):
    """Period-specific payroll: annual estimate enriched with L3 event amounts.

    Extends :class:`AnnualEstimate` with the period-specific inputs and
    informational breakdown fields.  The L3 amounts (absence deductions,
    overtime supplements, sick-pay indemnities, fringe benefits, etc.) do
    **not** flow into ``net_annual`` or ``employer_cost`` in this version —
    those remain annualised structural estimates.

    Attributes:
        pay_period: The period-specific events that were merged into the
            structural scenario.
        base_monthly_full_time: Full-time equivalent base monthly pay before
            part-time scaling.
        overtime_supplement_monthly: Estimated monthly overtime supplement.
        night_supplement_monthly: Estimated monthly night-shift supplement.
        holiday_supplement_monthly: Estimated monthly holiday supplement.
        time_supplements_monthly: Sum of all time-based supplements.
        time_supplements_annual_projection: Annualised projection of
            ``time_supplements_monthly``.
        absence_deduction_monthly: Pay reduction for unpaid absence days.
        effective_gross_monthly: Gross monthly adjusted for absence deduction.
        leave_accrued_days_monthly: Leave days accrued in this period.
        leave_taken_days_monthly: Leave days consumed in this period.
        leave_balance_days: Remaining leave balance after this period.
        sick_days_monthly: Total sick-leave days in this period.
        sick_carenza_days_monthly: Unpaid waiting-period sick days.
        sick_inps_indemnity_monthly: INPS sick-pay indemnity for this period.
        sick_company_integration_monthly: Employer top-up on INPS indemnity.
        fringe_benefit_annual: Total fringe-benefit amount (informational).
        fringe_benefit_threshold_annual: Applicable tax-free threshold.
        fringe_benefit_taxable_annual: Taxable fringe-benefit amount.
        welfare_annual: Welfare contribution amount (tax-exempt).
        bonus_annual: Total bonus / PdR amount (informational).
        bonus_pdr_flat_tax_annual: PdR flat-tax amount.
        bonus_ordinary_taxable_annual: Ordinary taxable bonus portion.
    """

    pay_period: PeriodPayrollInput

    base_monthly_full_time: Decimal = field(default=_ZERO)
    overtime_supplement_monthly: Decimal = field(default=_ZERO)
    night_supplement_monthly: Decimal = field(default=_ZERO)
    holiday_supplement_monthly: Decimal = field(default=_ZERO)
    time_supplements_monthly: Decimal = field(default=_ZERO)
    time_supplements_annual_projection: Decimal = field(default=_ZERO)
    absence_deduction_monthly: Decimal = field(default=_ZERO)
    effective_gross_monthly: Decimal = field(default=_ZERO)
    leave_accrued_days_monthly: Decimal = field(default=_ZERO)
    leave_taken_days_monthly: Decimal = field(default=_ZERO)
    leave_balance_days: Decimal = field(default=_ZERO)
    sick_days_monthly: Decimal = field(default=_ZERO)
    sick_carenza_days_monthly: Decimal = field(default=_ZERO)
    sick_inps_indemnity_monthly: Decimal = field(default=_ZERO)
    sick_company_integration_monthly: Decimal = field(default=_ZERO)
    fringe_benefit_annual: Decimal = field(default=_ZERO)
    fringe_benefit_threshold_annual: Decimal = field(default=_ZERO)
    fringe_benefit_taxable_annual: Decimal = field(default=_ZERO)
    welfare_annual: Decimal = field(default=_ZERO)
    bonus_annual: Decimal = field(default=_ZERO)
    bonus_pdr_flat_tax_annual: Decimal = field(default=_ZERO)
    bonus_ordinary_taxable_annual: Decimal = field(default=_ZERO)

    @property
    def effective_net_monthly(self) -> Decimal:
        """Monthly take-home adjusted for L3 events.

        Returns:
            ``net_monthly`` minus absence deduction plus time supplements
            and sick-pay amounts.
        """
        return (
            self.net_monthly
            - self.absence_deduction_monthly
            + self.time_supplements_monthly
            + self.sick_inps_indemnity_monthly
            + self.sick_company_integration_monthly
        )

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> PeriodPayroll:
        """Reconstruct from a ``to_dict()`` dict.

        Args:
            data: A dictionary as produced by :meth:`to_dict`.

        Returns:
            A new :class:`PeriodPayroll` with all fields restored.

        Raises:
            TypeError: If *data* contains unexpected keys.
            ValueError: If a required field is absent from *data*.
        """
        from ccnl_engine.engine.payroll.domain.scenario import (  # noqa: PLC0415
            PeriodPayrollInput,
        )

        allowed = frozenset(f.name for f in dataclasses.fields(cls))
        extra = set(data) - allowed
        if extra:
            msg = f"PeriodPayroll.from_dict: unexpected keys: {sorted(extra)}"
            raise TypeError(msg)
        hints = typing.get_type_hints(
            cls, localns={"PeriodPayrollInput": PeriodPayrollInput}
        )
        extra_decoders: dict[str, object] = {
            "pay_period": PeriodPayrollInput.model_validate
        }
        kwargs: dict[str, object] = {}
        for f in dataclasses.fields(cls):
            if f.name not in data:
                if _has_default(f):
                    continue
                msg = f"Missing field: {f.name!r}"
                raise ValueError(msg) from None
            kwargs[f.name] = _decode_field(
                f.name, data[f.name], hints[f.name], extra_decoders
            )
        return cls(**kwargs)  # type: ignore[arg-type]

    @classmethod
    def from_json(cls, raw: str) -> PeriodPayroll:
        """Reconstruct from a JSON string.

        Args:
            raw: A JSON string as returned by :meth:`to_json`.

        Returns:
            A new :class:`PeriodPayroll` equal to the original.
        """
        return cls.from_dict(json.loads(raw))
