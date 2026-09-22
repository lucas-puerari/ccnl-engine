"""Coerce helpers and aggregate dataclasses: Earnings, Contributions, Taxes, Cost."""

from __future__ import annotations

import dataclasses
import typing
from dataclasses import dataclass
from datetime import date as _date
from decimal import Decimal
from typing import cast

from ccnl_engine.engine.payroll.domain.components._status import (
    CalculationStatus,
    EligibilityStatus,
    ScopeItem,
    SourceQuality,
)
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
