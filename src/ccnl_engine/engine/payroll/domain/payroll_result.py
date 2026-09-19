"""PayrollResult — the output record of compute()."""

from __future__ import annotations

import dataclasses
import json
import types
import typing
from dataclasses import dataclass
from datetime import date as _date
from decimal import Decimal
from typing import Literal, cast

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
_STRICT_PRIMITIVES: frozenset[type] = frozenset({bool, int, str})


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


def _validate_primitive(raw: object, hint: type) -> object:
    """Validate *raw* against a strict primitive *hint* and return it unchanged.

    ``bool`` is checked before ``int`` because ``bool`` is a subclass of
    ``int`` in Python and the two must not be confused.

    Returns:
        *raw* when it matches *hint* exactly.

    Raises:
        TypeError: When *raw* does not match the exact primitive *hint*.
    """
    if hint is bool:
        if not isinstance(raw, bool):
            msg = f"expected bool, got {type(raw).__name__!r}"
            raise TypeError(msg)
    elif hint is int:
        if not isinstance(raw, int) or isinstance(raw, bool):
            msg = f"expected int, got {type(raw).__name__!r}"
            raise TypeError(msg)
    elif not isinstance(raw, str):
        msg = f"expected str, got {type(raw).__name__!r}"
        raise TypeError(msg)
    return raw


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
        return frozenset(FiscalSimplification(v) for v in raw)  # type: ignore[attr-defined]
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
        year: Calendar year of the pay period (``as_of.year``).  This is
            always the year of the calculation date, regardless of any
            explicit ``tax_year`` override.  To find the fiscal year used
            to load IRPEF brackets and contribution rules, see
            :attr:`~ccnl_engine.engine.payroll.domain.calculation\
.InputSnapshot.year`.

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
        bilateral_employee_annual: Employee contribution to scenario-level
            bilateral funds (fondi bilaterali). Zero when
            ``scenario.bilateral_funds`` is empty. Reduces ``net_annual``
            post-tax.
        bilateral_employer_annual: Employer contribution to scenario-level
            bilateral funds. Zero when ``scenario.bilateral_funds`` is
            empty. Enters ``employer_cost_annual``.

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

        somma_esente: Somma esente bonus (L. 207/2024): flat-rate net bonus
            added for reddito complessivo up to 20 000 EUR; ``0`` when not
            applicable or when the tax data file does not carry the parameters.
        trattamento_integrativo: Trattamento integrativo bonus (Art. 1 D.L.
            3/2020), if computed; ``0`` when not applicable or when the tax
            data file does not carry the required parameters.
        fiscal_simplifications: Set of fiscal elements omitted from this
            computation. Callers can check membership to know which items are
            absent from the net figure.

        net_annual: Annual net pay (``gross_annual`` minus
            ``inps_employee_annual`` minus ``irpef_net`` minus
            ``addizionale_regionale_annual`` minus
            ``addizionale_comunale_annual`` plus ``trattamento_integrativo``
            plus ``somma_esente``).
        net_monthly: Monthly net pay (``net_annual / additional_months``).
            Rounded to two decimal places; for contracts with fractional
            additional-months divisors (e.g. 13.5 or 14), a sub-cent
            remainder is absorbed by the rounding — the sum of monthly
            figures may differ from ``net_annual`` by up to EUR 0.01.

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
    bilateral_employee_annual: Decimal
    bilateral_employer_annual: Decimal

    taxable_income: Decimal
    irpef_gross: Decimal
    work_income_deduction: Decimal
    irpef_net: Decimal
    employer_withholds_irpef: bool

    addizionale_regionale_annual: Decimal
    addizionale_comunale_annual: Decimal

    ulteriore_detrazione_lavoro: Decimal
    somma_esente: Decimal
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
    # This is the pre-clawback Art. 15 credit; the sterilizzazione reduction
    # (Art. 1 c. 3-4 L. 199/2025) is captured in sterilizzazione_clawback_annual.
    art15_deduction_annual: Decimal = _ZERO
    unused_art15_deduction_annual: Decimal = _ZERO
    # Art. 1 c. 3-4 L. 199/2025 sterilizzazione: EUR 440 clawback applied to
    # Art. 15 TUIR oneri detraibili al 19 % (lett. a, b, d, e; not spese
    # sanitarie lett. c) when reddito complessivo > EUR 200 000.
    # Zero for taxpayers below the threshold.
    sterilizzazione_clawback_annual: Decimal = _ZERO

    # --- L3: time supplements (informational; not in gross_annual/net_annual) ---
    base_monthly_full_time: Decimal = _ZERO
    overtime_supplement_monthly: Decimal = _ZERO
    night_supplement_monthly: Decimal = _ZERO
    holiday_supplement_monthly: Decimal = _ZERO
    time_supplements_monthly: Decimal = _ZERO
    time_supplements_annual_projection: Decimal = _ZERO

    # --- Serialisation metadata ---
    schema_version: str = "1"

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
            TypeError: If *data* contains unexpected keys.
            ValueError: If a required field is absent from ``data``.
        """
        allowed = frozenset(f.name for f in dataclasses.fields(cls))
        extra = set(data) - allowed
        if extra:
            msg = f"PayrollResult.from_dict: unexpected keys: {sorted(extra)}"
            raise TypeError(msg)
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

    @property
    def effective_net_monthly(self) -> Decimal:
        """Monthly take-home adjusted for L3 events.

        Adjusts the structural ``net_monthly`` (annualized net / months) for
        the period-specific events that actually occurred: unpaid absences
        reduce the figure while overtime and sick-pay amounts add to it.
        IRPEF is not recomputed on the delta; the adjustment is a best-effort
        approximation suited for monthly payslip presentation.

        Returns:
            ``net_monthly`` minus ``absence_deduction_monthly`` plus
            ``time_supplements_monthly``, ``sick_inps_indemnity_monthly``,
            and ``sick_company_integration_monthly``.
        """
        return (
            self.net_monthly
            - self.absence_deduction_monthly
            + self.time_supplements_monthly
            + self.sick_inps_indemnity_monthly
            + self.sick_company_integration_monthly
        )

    @property
    def pay(self) -> PayrollPay:
        """Employee gross and net pay breakdown."""
        return PayrollPay.from_result(self)

    @property
    def tax(self) -> PayrollTax:
        """IRPEF chain, deductions, and fiscal metadata."""
        return PayrollTax.from_result(self)

    @property
    def employer(self) -> PayrollEmployer:
        """Employer cost breakdown and contributions."""
        return PayrollEmployer.from_result(self)

    @property
    def quality(self) -> PayrollQuality:
        """Computation quality metadata."""
        return PayrollQuality.from_result(self)


@dataclass(frozen=True)
class PayrollPay:
    """Employee pay components, gross breakdown, and L3 event amounts."""

    seniority_count: int
    base_monthly: Decimal
    seniority_monthly: Decimal
    allowances_monthly: Decimal
    ad_personam_monthly: Decimal
    second_level_monthly: Decimal
    gross_monthly: Decimal
    gross_annual: Decimal
    hourly_rate: Decimal
    inps_employee_annual: Decimal
    bilateral_employee_annual: Decimal
    net_annual: Decimal
    net_monthly: Decimal
    absence_deduction_monthly: Decimal
    effective_gross_monthly: Decimal
    leave_accrued_days_monthly: Decimal
    leave_taken_days_monthly: Decimal
    leave_balance_days: Decimal
    sick_days_monthly: Decimal
    sick_carenza_days_monthly: Decimal
    sick_inps_indemnity_monthly: Decimal
    sick_company_integration_monthly: Decimal
    fringe_benefit_annual: Decimal
    fringe_benefit_threshold_annual: Decimal
    fringe_benefit_taxable_annual: Decimal
    welfare_annual: Decimal
    bonus_annual: Decimal
    bonus_pdr_flat_tax_annual: Decimal
    bonus_ordinary_taxable_annual: Decimal
    base_monthly_full_time: Decimal
    overtime_supplement_monthly: Decimal
    night_supplement_monthly: Decimal
    holiday_supplement_monthly: Decimal
    time_supplements_monthly: Decimal
    time_supplements_annual_projection: Decimal
    effective_net_monthly: Decimal

    @classmethod
    def from_result(cls, r: PayrollResult) -> PayrollPay:
        """Build a :class:`PayrollPay` from a :class:`PayrollResult`.

        Returns:
            A new :class:`PayrollPay` populated from *r*.
        """
        return cls(
            seniority_count=r.seniority_count,
            base_monthly=r.base_monthly,
            seniority_monthly=r.seniority_monthly,
            allowances_monthly=r.allowances_monthly,
            ad_personam_monthly=r.ad_personam_monthly,
            second_level_monthly=r.second_level_monthly,
            gross_monthly=r.gross_monthly,
            gross_annual=r.gross_annual,
            hourly_rate=r.hourly_rate,
            inps_employee_annual=r.inps_employee_annual,
            bilateral_employee_annual=r.bilateral_employee_annual,
            net_annual=r.net_annual,
            net_monthly=r.net_monthly,
            absence_deduction_monthly=r.absence_deduction_monthly,
            effective_gross_monthly=r.effective_gross_monthly,
            leave_accrued_days_monthly=r.leave_accrued_days_monthly,
            leave_taken_days_monthly=r.leave_taken_days_monthly,
            leave_balance_days=r.leave_balance_days,
            sick_days_monthly=r.sick_days_monthly,
            sick_carenza_days_monthly=r.sick_carenza_days_monthly,
            sick_inps_indemnity_monthly=r.sick_inps_indemnity_monthly,
            sick_company_integration_monthly=r.sick_company_integration_monthly,
            fringe_benefit_annual=r.fringe_benefit_annual,
            fringe_benefit_threshold_annual=r.fringe_benefit_threshold_annual,
            fringe_benefit_taxable_annual=r.fringe_benefit_taxable_annual,
            welfare_annual=r.welfare_annual,
            bonus_annual=r.bonus_annual,
            bonus_pdr_flat_tax_annual=r.bonus_pdr_flat_tax_annual,
            bonus_ordinary_taxable_annual=r.bonus_ordinary_taxable_annual,
            base_monthly_full_time=r.base_monthly_full_time,
            overtime_supplement_monthly=r.overtime_supplement_monthly,
            night_supplement_monthly=r.night_supplement_monthly,
            holiday_supplement_monthly=r.holiday_supplement_monthly,
            time_supplements_monthly=r.time_supplements_monthly,
            time_supplements_annual_projection=r.time_supplements_annual_projection,
            effective_net_monthly=r.effective_net_monthly,
        )


@dataclass(frozen=True)
class PayrollTax:
    """IRPEF chain, addizionali, and fiscal deductions."""

    taxable_income: Decimal
    irpef_gross: Decimal
    work_income_deduction: Decimal
    irpef_net: Decimal
    employer_withholds_irpef: bool
    addizionale_regionale_annual: Decimal
    addizionale_comunale_annual: Decimal
    ulteriore_detrazione_lavoro: Decimal
    somma_esente: Decimal
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

    @classmethod
    def from_result(cls, r: PayrollResult) -> PayrollTax:
        """Build a :class:`PayrollTax` from a :class:`PayrollResult`.

        Returns:
            A new :class:`PayrollTax` populated from *r*.
        """
        return cls(
            taxable_income=r.taxable_income,
            irpef_gross=r.irpef_gross,
            work_income_deduction=r.work_income_deduction,
            irpef_net=r.irpef_net,
            employer_withholds_irpef=r.employer_withholds_irpef,
            addizionale_regionale_annual=r.addizionale_regionale_annual,
            addizionale_comunale_annual=r.addizionale_comunale_annual,
            ulteriore_detrazione_lavoro=r.ulteriore_detrazione_lavoro,
            somma_esente=r.somma_esente,
            trattamento_integrativo=r.trattamento_integrativo,
            fiscal_simplifications=r.fiscal_simplifications,
            family_deduction_spouse_annual=r.family_deduction_spouse_annual,
            family_deduction_children_annual=r.family_deduction_children_annual,
            family_deduction_other_annual=r.family_deduction_other_annual,
            family_deduction_annual=r.family_deduction_annual,
            unused_family_deduction_annual=r.unused_family_deduction_annual,
            art15_deduction_annual=r.art15_deduction_annual,
            unused_art15_deduction_annual=r.unused_art15_deduction_annual,
            sterilizzazione_clawback_annual=r.sterilizzazione_clawback_annual,
        )


@dataclass(frozen=True)
class PayrollEmployer:
    """Employer cost breakdown and social contributions."""

    inps_employer_annual: Decimal
    employer_funds_annual: Decimal
    tfr_annual: Decimal
    bilateral_employer_annual: Decimal
    employer_cost_annual: Decimal

    @classmethod
    def from_result(cls, r: PayrollResult) -> PayrollEmployer:
        """Build a :class:`PayrollEmployer` from a :class:`PayrollResult`.

        Returns:
            A new :class:`PayrollEmployer` populated from *r*.
        """
        return cls(
            inps_employer_annual=r.inps_employer_annual,
            employer_funds_annual=r.employer_funds_annual,
            tfr_annual=r.tfr_annual,
            bilateral_employer_annual=r.bilateral_employer_annual,
            employer_cost_annual=r.employer_cost_annual,
        )


@dataclass(frozen=True)
class PayrollQuality:
    """Computation quality and coverage metadata."""

    status: Literal["partial", "complete"]
    confidence: Literal["low", "medium", "high"]
    calculation_scope: tuple[ScopeItem, ...]
    warnings: tuple[str, ...]

    @classmethod
    def from_result(cls, r: PayrollResult) -> PayrollQuality:
        """Build a :class:`PayrollQuality` from a :class:`PayrollResult`.

        Returns:
            A new :class:`PayrollQuality` populated from *r*.
        """
        return cls(
            status=r.status,
            confidence=r.confidence,
            calculation_scope=r.calculation_scope,
            warnings=r.warnings,
        )
