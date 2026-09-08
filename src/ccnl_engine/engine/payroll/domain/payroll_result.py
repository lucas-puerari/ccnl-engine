"""PayrollResult — the output record of compute()."""

from __future__ import annotations

import dataclasses
import json
import types
import typing
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date as _date
from decimal import Decimal
from typing import Literal

from ccnl_engine.engine.payroll.domain.fiscal import FiscalSimplification
from ccnl_engine.engine.provenance.domain.chain import RuleProvenance

_ZERO = Decimal(0)


def _serialise_tuple_item(v: object) -> object:
    """Serialise one item from a tuple field for JSON output.

    Pydantic models use ``model_dump``; plain dataclasses use ``asdict``;
    everything else is returned as-is.

    Returns:
        A JSON-native representation of *v*.
    """
    if hasattr(v, "model_dump"):
        return v.model_dump(mode="json")
    if dataclasses.is_dataclass(v):
        return dataclasses.asdict(v)  # type: ignore[arg-type]
    return v


@dataclass(frozen=True)
class ScopeItem:
    """One entry in the calculation scope list.

    Attributes:
        feature: Engine feature name (e.g. ``"overtime"``, ``"irpef"``).
        status: Whether it was computed, excluded, or not available.
    """

    feature: str
    status: Literal["verified", "excluded", "not_computed"]


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


def _coerce_scalar(raw: object, hint: type) -> object:
    """Coerce a non-None *raw* to a scalar *hint* type.

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
        return ScopeItem(
            feature=str(raw["feature"]),
            status=raw["status"],
        )
    if hint == frozenset[FiscalSimplification]:
        return frozenset(FiscalSimplification(v) for v in raw)  # type: ignore[attr-defined]
    return raw


def _coerce(raw: object, hint: type) -> object:
    """Coerce *raw* to the Python type described by the annotation *hint*.

    Handles ``X | None`` unions, ``Decimal``, ``date``,
    ``frozenset[FiscalSimplification]`` and tuples of
    :class:`RuleProvenance`; everything else is returned as-is.

    Returns:
        The coerced value, or *raw* unchanged when no coercion applies.
    """
    raw, hint = _unwrap_optional(raw, hint)
    if raw is None:
        return None
    origin = typing.get_origin(hint)
    args = typing.get_args(hint)
    if origin is tuple and args:
        items = typing.cast(Iterable[object], raw)
        return tuple(_coerce(item, args[0]) for item in items)
    return _coerce_scalar(raw, hint)


@dataclass(frozen=True)
class PayrollResult:
    """Full gross-to-net and employer-cost breakdown for one payroll computation.

    Monthly components (``base_monthly``, ``seniority_monthly``,
    ``allowances_monthly``, ``ad_personam_monthly``) are already scaled by
    ``part_time_pct`` and sum to ``gross_monthly``.

    All ``Decimal`` amounts are in EUR. Annual figures assume the contract-wide
    ``additional_months`` pay structure (typically 13 or 14 months).

    Attributes:
        ccnl_id: Identifier of the CCNL used (from ``CCNLMeta.id``).
        level_code: Classification level code used for the computation.
        employment_type: String tag of the employment type
            (``"permanent"``, ``"fixed_term"``, or ``"apprentice"``).
        part_time_pct: Part-time coefficient applied to gross and
            contribution bases. ``1`` for a full-time worker.
        as_of: Reference date used to resolve all time-series values.
        year: Calendar year derived from ``as_of``; used to select IRPEF
            brackets and contribution rules.

        seniority_count: Number of seniority increments (*scatti di
            anzianità*) applied. ``0`` when no seniority applies.
        base_monthly: Base monthly pay from the CCNL table, scaled by
            ``part_time_pct``.
        seniority_monthly: Monthly seniority increment amount, scaled by
            ``part_time_pct``.
        allowances_monthly: Sum of all applicable fixed monthly allowances,
            scaled by ``part_time_pct``.
        ad_personam_monthly: Individual frozen monthly element (e.g.
            pre-abolition seniority) added directly to gross, **not** scaled
            by ``part_time_pct``.  Contrast with ``second_level_monthly``,
            which is the collective supplement scaled by ``part_time_pct``.
        second_level_monthly: Total scaled monthly amount from second-level
            (territorial or company) agreements — the sum of all
            :class:`~ccnl_engine.domain.ccnl.SupplementaryAllowance` items
            passed via ``Scenario.second_level_allowances``, each scaled by
            ``part_time_pct`` (and optionally by the apprenticeship percentage).
            Zero when no second-level allowances are provided.
        gross_monthly: Total monthly gross pay (sum of the five monthly
            components: ``base_monthly``, ``seniority_monthly``,
            ``allowances_monthly``, ``ad_personam_monthly``,
            ``second_level_monthly``).
        gross_annual: Annual gross pay, accounting for additional months
            (``gross_monthly * additional_months``).
        hourly_rate: Hourly gross rate derived from the contractual weekly
            hours and the standard number of months per year.

        apprenticeship_pct: Percentage applied to destination-level pay for
            percentage-track apprentices (e.g. ``Decimal("0.80")``). ``None``
            for non-apprentice or under-classification contracts.
        apprenticeship_under_level_code: Destination level code for
            under-classification apprentices. ``None`` otherwise.

        inps_employee_annual: Employee INPS contribution for the year.
        inps_employer_annual: Employer INPS contribution for the year,
            including any NASpI addizionale for fixed-term contracts.
        employer_funds_annual: Employer contribution to contractual funds
            (e.g. Cassa Edile, Fondapi) for the year.
        tfr_annual: TFR (*Trattamento di Fine Rapporto*) accrual for the
            year (Art. 2120 c.c.).

        taxable_income: IRPEF taxable base (``gross_annual``
            minus ``inps_employee_annual``).
        irpef_gross: IRPEF before work-income deduction (Art. 11 TUIR).
        work_income_deduction: Work-income tax deduction (Art. 13 TUIR).
        irpef_net: IRPEF actually withheld (``irpef_gross``
            minus ``work_income_deduction``, floored at zero).
        employer_withholds_irpef: ``False`` when the employer is not a
            *sostituto d'imposta* (e.g. lavoro domestico); in that case
            ``irpef_gross`` and ``work_income_deduction`` are informational
            only and ``irpef_net`` is zero.

        addizionale_regionale_annual: Annual addizionale regionale IRPEF
            (Art. 50 TUIR), computed from the regional marginal bracket table.
            Zero when ``Scenario.regione`` is ``None`` or no
            :class:`~ccnl_engine.engine.surtax.models.SurtaxRules` was passed to
            :func:`~ccnl_engine.engine.compute.compute`.
        addizionale_comunale_annual: Annual addizionale comunale IRPEF
            (Art. 1 D.Lgs. 360/1998), computed from the municipal bracket
            table and exemption threshold.  Zero when
            ``Scenario.comune_belfiore`` is ``None`` or no
            :class:`~ccnl_engine.engine.surtax.models.SurtaxRules` was passed.

        trattamento_integrativo: Trattamento integrativo bonus (Art. 1 D.L.
            3/2020), if computed; ``0`` when not applicable or when the tax
            data file does not carry the required parameters.
        fiscal_simplifications: Set of fiscal elements omitted from this
            computation. Callers can check membership to know which items are
            absent from the net figure.

        net_annual: Annual net pay (``gross_annual`` minus
            ``inps_employee_annual`` minus ``irpef_net`` minus
            ``addizionale_regionale_annual`` minus
            ``addizionale_comunale_annual`` plus ``trattamento_integrativo``).
        net_monthly: Monthly net pay (``net_annual / additional_months``).

        employer_cost_annual: Total annual employer cost
            (``gross_annual`` + ``inps_employer_annual``
            + ``employer_funds_annual`` + ``tfr_annual``).
    """

    ccnl_id: str
    level_code: str
    employment_type: str
    part_time_pct: Decimal
    as_of: _date
    year: int

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

    inps_employee_annual: Decimal
    inps_employer_annual: Decimal
    employer_funds_annual: Decimal
    tfr_annual: Decimal

    taxable_income: Decimal
    irpef_gross: Decimal
    work_income_deduction: Decimal
    irpef_net: Decimal
    employer_withholds_irpef: bool

    addizionale_regionale_annual: Decimal
    addizionale_comunale_annual: Decimal

    trattamento_integrativo: Decimal
    fiscal_simplifications: frozenset[FiscalSimplification]

    net_annual: Decimal
    net_monthly: Decimal

    employer_cost_annual: Decimal

    provenance: tuple[RuleProvenance, ...] = ()

    # --- Status and warnings ---
    status: Literal["partial", "complete"] = "partial"
    confidence: Literal["low", "medium", "high"] = "medium"
    calculation_scope: tuple[ScopeItem, ...] = ()
    warnings: tuple[str, ...] = ()

    # --- L3: absence (informational; gross_annual/net_annual not mutated) ---
    absence_deduction_monthly: Decimal = _ZERO
    effective_gross_monthly: Decimal = _ZERO

    # --- L3: leave (informational; gross_annual/net_annual not mutated) ---
    leave_accrued_days_monthly: Decimal = _ZERO
    leave_taken_days_monthly: Decimal = _ZERO
    leave_balance_days: Decimal = _ZERO

    # --- L3: sickness (informational; gross_annual/net_annual not mutated) ---
    sick_days_monthly: Decimal = _ZERO
    sick_carenza_days_monthly: Decimal = _ZERO
    sick_inps_indemnity_monthly: Decimal = _ZERO
    sick_company_integration_monthly: Decimal = _ZERO

    # --- L3: fringe benefits (informational; taxable_income not mutated) ---
    fringe_benefit_annual: Decimal = _ZERO
    fringe_benefit_threshold_annual: Decimal = _ZERO
    fringe_benefit_taxable_annual: Decimal = _ZERO

    # --- L3: welfare (informational; always tax-exempt) ---
    welfare_annual: Decimal = _ZERO

    # --- L3: bonus / PdR (informational; IRPEF chain not extended) ---
    bonus_annual: Decimal = _ZERO
    bonus_pdr_flat_tax_annual: Decimal = _ZERO
    bonus_ordinary_taxable_annual: Decimal = _ZERO

    # --- L3: family deductions (Art. 12 TUIR; mutates irpef_net/net_annual) ---
    # Unlike other L3 features these are NOT informational: they reduce irpef_net.
    family_deduction_spouse_annual: Decimal = _ZERO
    family_deduction_children_annual: Decimal = _ZERO
    family_deduction_other_annual: Decimal = _ZERO
    family_deduction_annual: Decimal = _ZERO
    unused_family_deduction_annual: Decimal = _ZERO

    # --- L3: Art. 15 deductions (mutates irpef_net/net_annual) ---
    # NOT informational: the credit reduces irpef_net directly.
    # Art. 1 c. 3-4 L. 199/2025 sterilizzazione does NOT apply here.
    art15_deduction_annual: Decimal = _ZERO
    unused_art15_deduction_annual: Decimal = _ZERO

    # --- L3: time supplements (informational; not in gross_annual/net_annual) ---
    base_monthly_full_time: Decimal = _ZERO
    overtime_supplement_monthly: Decimal = _ZERO
    night_supplement_monthly: Decimal = _ZERO
    holiday_supplement_monthly: Decimal = _ZERO
    time_supplements_monthly: Decimal = _ZERO
    time_supplements_annual_projection: Decimal = _ZERO

    def to_dict(self) -> dict[str, object]:
        """Serialise the payroll to a plain Python dictionary.

        All ``Decimal`` amounts are converted to ``str`` to avoid floating-point
        loss. ``date`` is serialised as an ISO-8601 string. ``frozenset`` fields
        are converted to sorted lists of strings for deterministic output.

        Returns:
            A dictionary with only JSON-native types (``str``, ``int``, ``bool``,
            ``list``, ``None``).
        """
        out: dict[str, object] = {}
        for field in dataclasses.fields(self):
            value = getattr(self, field.name)
            if isinstance(value, Decimal):
                out[field.name] = str(value)
            elif isinstance(value, _date):
                out[field.name] = value.isoformat()
            elif isinstance(value, frozenset):
                out[field.name] = sorted(str(v) for v in value)
            elif isinstance(value, tuple):
                out[field.name] = [_serialise_tuple_item(v) for v in value]
            else:
                out[field.name] = value
        return out

    def to_json(self) -> str:
        """Serialise the payroll to a JSON string.

        Returns:
            A compact JSON string. See :meth:`to_dict` for the encoding rules.
        """
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> PayrollResult:
        """Reconstruct a :class:`PayrollResult` from a ``to_dict()`` dict.

        Args:
            data: A dictionary as produced by :meth:`to_dict`.

        Returns:
            A new :class:`PayrollResult` with all fields restored to
            their original types.

        Raises:
            ValueError: If a required field is absent from ``data``.
        """
        hints = typing.get_type_hints(cls)
        kwargs: dict[str, object] = {}
        for field in dataclasses.fields(cls):
            if field.name not in data:
                has_default = (
                    field.default is not dataclasses.MISSING
                    or field.default_factory is not dataclasses.MISSING
                )
                if has_default:
                    continue  # let the dataclass constructor supply the default
                msg = f"Missing field: {field.name!r}"
                raise ValueError(msg) from None
            kwargs[field.name] = _coerce(data[field.name], hints[field.name])
        return cls(**kwargs)  # type: ignore[arg-type]

    @classmethod
    def from_json(cls, raw: str) -> PayrollResult:
        """Reconstruct a :class:`PayrollResult` from a JSON string.

        Args:
            raw: A JSON string as returned by :meth:`to_json`.

        Returns:
            A new :class:`PayrollResult` with all fields restored to
            their original types.
        """
        return cls.from_dict(json.loads(raw))
