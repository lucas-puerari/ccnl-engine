"""Payroll sub-object components: Earnings, Contributions, Taxes, EmployerCost.

Also contains the scope/status enums and ScopeItem, plus the private
serialisation helpers shared across all payroll result types.
"""

from __future__ import annotations

import dataclasses
import typing
from dataclasses import dataclass
from datetime import date as _date
from decimal import Decimal
from enum import StrEnum
from typing import cast

from ccnl_engine.engine.payroll.domain.fiscal import FiscalSimplification
from ccnl_engine.engine.serialization.codec import (
    _STRICT_PRIMITIVES,
    _validate_primitive,
)
from ccnl_engine.engine.serialization.result_codec import (
    _has_default as _has_default,  # noqa: PLC0414
)
from ccnl_engine.engine.serialization.result_codec import (
    _serialise_dataclass as _serialise_dataclass,  # noqa: PLC0414
)
from ccnl_engine.engine.serialization.result_codec import (
    _serialise_value as _serialise_value,  # noqa: PLC0414
)
from ccnl_engine.engine.serialization.result_codec import (
    _unwrap_optional as _unwrap_optional,  # noqa: PLC0414
)

_ZERO = Decimal(0)


# ---------------------------------------------------------------------------
# Status enums and ScopeItem
# ---------------------------------------------------------------------------


class CalculationStatus(StrEnum):
    """Whether the engine computed the feature."""

    COMPUTED = "computed"
    PARTIAL = "partial"
    NOT_COMPUTED = "not_computed"
    EXCLUDED = "excluded"


class EligibilityStatus(StrEnum):
    """Verification level of the inputs that triggered the computation."""

    ENGINE_VERIFIED = "engine_verified"
    CALLER_DECLARED = "caller_declared"
    UNKNOWN = "unknown"
    N_A = "n_a"


class SourceQuality(StrEnum):
    """Quality of the normative data source behind the computation."""

    VERIFIED_PRIMARY = "verified_primary"
    UNVERIFIED = "unverified"
    ESTIMATED = "estimated"
    N_A = "n_a"


@dataclass(frozen=True)
class ScopeItem:
    """One entry in the calculation scope list.

    ``calculation_status``
        Whether the engine computed the feature (``"computed"``), partially
        computed it (``"partial"``), could not compute it (``"not_computed"``),
        or the caller did not request it (``"excluded"``).

    Integration axes (``gross_integrated``, ``contribution_integrated``,
    ``tax_integrated``, ``net_integrated``, ``cost_integrated``)
        One boolean per accounting axis.  ``True`` means the feature's amount
        flows into that axis of the period totals.  All axes are ``False`` for
        informational-only features (computed but not wired into any total) and
        for excluded or not-computed features.

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
    calculation_status: CalculationStatus
    gross_integrated: bool = False
    contribution_integrated: bool = False
    tax_integrated: bool = False
    net_integrated: bool = False
    cost_integrated: bool = False
    eligibility_status: EligibilityStatus = EligibilityStatus.N_A
    source_quality: SourceQuality = SourceQuality.N_A
    assumptions: tuple[str, ...] = ()


# ---------------------------------------------------------------------------
# Private serialisation helpers
# ---------------------------------------------------------------------------


def _coerce_scope_item(raw: dict[str, object]) -> ScopeItem:
    """Reconstruct a :class:`ScopeItem` from a dict, validating field types.

    Returns:
        A new :class:`ScopeItem` with validated axis fields.

    Raises:
        TypeError: When ``feature`` is not a ``str``.
        ValueError: When any status field holds an invalid enum value.
    """
    feature = raw["feature"]
    if not isinstance(feature, str):
        msg = f"ScopeItem.feature must be str, got {type(feature).__name__!r}"
        raise TypeError(msg)
    try:
        calc = CalculationStatus(str(raw["calculation_status"]))
    except ValueError:
        valid = sorted(m.value for m in CalculationStatus)
        msg = f"ScopeItem.calculation_status must be one of {valid!r}"
        raise ValueError(msg) from None
    try:
        elig = EligibilityStatus(str(raw["eligibility_status"]))
    except ValueError:
        valid = sorted(m.value for m in EligibilityStatus)
        msg = f"ScopeItem.eligibility_status must be one of {valid!r}"
        raise ValueError(msg) from None
    try:
        qual = SourceQuality(str(raw["source_quality"]))
    except ValueError:
        valid = sorted(m.value for m in SourceQuality)
        msg = f"ScopeItem.source_quality must be one of {valid!r}"
        raise ValueError(msg) from None
    raw_assumptions = raw.get("assumptions") or []
    assumptions = tuple(str(a) for a in raw_assumptions)  # type: ignore[attr-defined]
    return ScopeItem(
        feature=feature,
        calculation_status=calc,
        gross_integrated=bool(raw.get("gross_integrated")),
        contribution_integrated=bool(raw.get("contribution_integrated")),
        tax_integrated=bool(raw.get("tax_integrated")),
        net_integrated=bool(raw.get("net_integrated")),
        cost_integrated=bool(raw.get("cost_integrated")),
        eligibility_status=elig,
        source_quality=qual,
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


# ---------------------------------------------------------------------------
# Sub-object component types
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
    inps_employer_exemption_annual: Decimal
    maternity_inps_indemnity_annual: Decimal
    workplace_injury_inail_indemnity_annual: Decimal
    termination_tfr_liquidation_annual: Decimal
    employer_funds_annual: Decimal
    tfr_annual: Decimal
    bilateral_employee_annual: Decimal
    bilateral_employer_annual: Decimal
    health_fund_employee_annual: Decimal
    health_fund_employer_annual: Decimal

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
    conguaglio_annual: Decimal
    termination_residual_leave_payout_annual: Decimal
    contract_renewal_arrears_annual: Decimal
    una_tantum_annual: Decimal
    personal_withholdings_annual: Decimal
    additional_irpef_base_annual: Decimal
    territorial_supplement_annual: Decimal
    company_supplement_annual: Decimal

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
