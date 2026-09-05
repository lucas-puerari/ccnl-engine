"""Gross-to-net and employer cost computation."""

from __future__ import annotations

from dataclasses import dataclass, replace
from decimal import Decimal
from typing import TYPE_CHECKING, Protocol

from ccnl_engine.engine import contributions as _contrib
from ccnl_engine.engine import irpef as _irpef
from ccnl_engine.engine.payslip import Payslip
from ccnl_engine.engine.rounding import money
from ccnl_engine.models.apprenticeship import ApprenticeshipPercentage
from ccnl_engine.models.employment import Apprentice, FixedTerm

if TYPE_CHECKING:
    from collections.abc import Sequence
    from datetime import date

    from ccnl_engine.models.apprenticeship import ApprenticeshipTrack
    from ccnl_engine.models.ccnl import (
        CCNL,
        Allowance,
        Level,
        LevelCategory,
        SeniorityIncrements,
    )
    from ccnl_engine.models.employment import Employment
    from ccnl_engine.tax.models import YearRules

_ONE = Decimal(1)
_ZERO = Decimal(0)
_TWO = Decimal(2)


class _MonthPeriod(Protocol):
    months_from: int
    months_until: int | None


@dataclass(frozen=True)
class _MonthlyPayChain:
    """Full-time monthly pay components of one level on one date."""

    base: Decimal
    seniority: Decimal
    allowances: tuple[tuple[Allowance, Decimal], ...]

    def scaled(self, factor: Decimal) -> _MonthlyPayChain:
        return _MonthlyPayChain(
            base=money(self.base * factor),
            seniority=money(self.seniority * factor),
            allowances=tuple((a, money(v * factor)) for a, v in self.allowances),
        )

    def scaled_selective(
        self, base_factor: Decimal, apprenticeship_pct: Decimal
    ) -> _MonthlyPayChain:
        """Scale for a percentage-based apprentice.

        ``base_factor`` (part-time fraction) applies to every component.
        ``apprenticeship_pct`` additionally applies to all components
        *except* allowances whose ``apprenticeship_pct_relevant`` flag is
        ``False`` — those are paid at their full part-time value.

        Returns:
            A new chain with selectively scaled components.
        """
        combined = base_factor * apprenticeship_pct

        def _scale(a: Allowance, v: Decimal) -> Decimal:
            f = combined if a.apprenticeship_pct_relevant else base_factor
            return money(v * f)

        return _MonthlyPayChain(
            base=money(self.base * combined),
            seniority=money(self.seniority * combined),
            allowances=tuple((a, _scale(a, v)) for a, v in self.allowances),
        )

    @property
    def allowances_total(self) -> Decimal:
        return money(sum((v for _, v in self.allowances), _ZERO))


@dataclass(frozen=True)
class _AnnualisedPay:
    gross: Decimal
    excluded_from_contributions: Decimal
    excluded_from_tfr: Decimal


@dataclass(frozen=True)
class Scenario:
    """Scenario parameters for a single ``compute()`` call.

    Attributes:
        level_code: Classification level code as defined in the CCNL
            (e.g. ``"D3"``). Must match a level in the provided CCNL.
        as_of: Reference date for time-series values (base pay, seniority
            amounts, allowances). Determines which entry in each ``TimeSeries``
            is active.
        employment: Employment contract type — ``Permanent``, ``FixedTerm``,
            or ``Apprentice``.
        part_time_pct: Part-time coefficient in the range ``(0, 1]``. A
            full-time worker uses the default ``1``. Gross pay, INPS, and TFR
            are all scaled by this value; ``ad_personam_monthly`` is not.
        seniority_count: Explicit number of seniority increments (*scatti*)
            already accrued. Mutually exclusive with ``seniority_months``; when
            neither is given, no increment applies.
        seniority_months: Months of service elapsed; the engine derives the
            increment count from CCNL cadence rules. Mutually exclusive with
            ``seniority_count``.
        negotiated_ral: Individual gross annual salary (RAL) agreed outside
            the CCNL tables. Replaces the CCNL-derived figure for any
            employment type and is used as-is (not scaled). Mutually exclusive
            with ``negotiated_destination_ral``.
        negotiated_destination_ral: Destination-level RAL for
            percentage-based apprentices. The engine applies
            ``apprenticeship_pct`` to this value to produce the apprentice's
            actual pay. Mutually exclusive with ``negotiated_ral``; only valid
            for ``Apprentice`` employment on a percentage track.
        roles: Set of role identifiers the worker holds (e.g. ``{"capoturno"}``).
            Selects role-restricted allowances defined in the CCNL level.
        ad_personam_monthly: Individual frozen monthly element added directly
            to gross (e.g. a pre-abolition seniority increment). Not scaled by
            ``part_time_pct``. Must be ``>= 0``.
        category: Worker category override (``"operaio"``, ``"impiegato"``,
            ``"quadro"``, ``"dirigente"``). Required when a level hosts
            multiple categories (e.g. edilizia level 3). Defaults to the
            level's own category.
        ivs_ceiling_applies: Set to ``True`` when the worker's gross is above
            the IVS ceiling and only the IVS-specific contribution rate should
            apply (rather than the full rate). Defaults to ``False``.
        weekly_hours: Contractual weekly hours. Required when the tax-rules
            file uses ``domestic_contributions`` (lavoro domestico).
        num_employees: Total headcount of the employer. Used to select the
            correct INPS contribution-rate tier when calling
            :func:`~ccnl_engine.tax.loaders.load_year_rules`. Must be >= 1.
    """

    level_code: str
    as_of: date
    employment: Employment
    num_employees: int
    part_time_pct: Decimal = _ONE
    seniority_count: int | None = None
    seniority_months: int | None = None
    negotiated_ral: Decimal | None = None
    negotiated_destination_ral: Decimal | None = None
    roles: frozenset[str] = frozenset()
    ad_personam_monthly: Decimal = _ZERO
    category: LevelCategory | None = None
    ivs_ceiling_applies: bool = False
    weekly_hours: Decimal | None = None

    def __post_init__(self) -> None:
        """Validate num_employees is at least 1.

        Raises:
            ValueError: If num_employees is less than 1.
        """
        if self.num_employees < 1:
            msg = f"num_employees must be >= 1, got {self.num_employees}"
            raise ValueError(msg)


def compute(ccnl: CCNL, rules: YearRules, scenario: Scenario) -> Payslip:
    """Compute gross-to-net salary and employer cost for a given scenario.

    Args:
        ccnl: The CCNL contract model.
        rules: Tax and contribution rules for the relevant year.
        scenario: Scenario parameters (level, date, employment, options).

    Returns:
        Payslip with all gross, net, and cost figures.

    Raises:
        ValueError: If part_time_pct is not in (0, 1], ad_personam_monthly < 0,
            seniority arguments are invalid, negotiated_ral and
            negotiated_destination_ral are both supplied,
            negotiated_destination_ral is used with a non-Apprentice employment,
            or negotiated_destination_ral is used with an under-classification
            apprenticeship track.
    """
    if not (_ZERO < scenario.part_time_pct <= _ONE):
        msg = f"part_time_pct must be in (0, 1], got {scenario.part_time_pct}"
        raise ValueError(msg)
    if scenario.ad_personam_monthly < _ZERO:
        msg = f"ad_personam_monthly must be >= 0, got {scenario.ad_personam_monthly}"
        raise ValueError(msg)
    ral_override = _validate_negotiated_ral(
        scenario.negotiated_ral,
        scenario.negotiated_destination_ral,
        scenario.employment,
    )

    level = ccnl.level_by_code(scenario.level_code)
    worker_category = (
        scenario.category if scenario.category is not None else level.category
    )
    count = _resolve_seniority_count(
        ccnl.parameters.seniority_increments,
        scenario.level_code,
        scenario.seniority_count,
        scenario.seniority_months,
    )
    if worker_category in ccnl.parameters.seniority_increments.excluded_categories:
        count = 0
    additional_months = ccnl.parameters.additional_months.value_at(scenario.as_of)

    factor = scenario.part_time_pct
    apprenticeship_pct: Decimal | None = None
    under_level_code: str | None = None
    if isinstance(scenario.employment, Apprentice):
        chain_ft, apprenticeship_pct, under_level_code = _apprentice_chain(
            ccnl, level, scenario.employment, count, scenario.roles, scenario.as_of
        )
        if apprenticeship_pct is not None:
            factor *= apprenticeship_pct
        if (
            scenario.negotiated_destination_ral is not None
            and apprenticeship_pct is None
        ):
            msg = (
                "negotiated_destination_ral requires a percentage-based apprenticeship "
                "track; the resolved track uses under-classification"
            )
            raise ValueError(msg)
    else:
        chain_ft = _level_chain(
            ccnl, level, count, scenario.roles, scenario.as_of, is_apprentice=False
        )

    chain = (
        chain_ft.scaled_selective(scenario.part_time_pct, apprenticeship_pct)
        if apprenticeship_pct is not None
        else chain_ft.scaled(factor)
    )
    ad_personam = money(scenario.ad_personam_monthly)
    gross_monthly = money(
        chain.base + chain.seniority + chain.allowances_total + ad_personam
    )
    annual = _annualise(chain, ad_personam, additional_months)
    gross_annual = annual.gross

    gross_annual, gross_monthly = _override_gross(
        scenario.negotiated_ral,
        scenario.negotiated_destination_ral,
        apprenticeship_pct,
        gross_annual,
        gross_monthly,
        additional_months,
    )

    # The negotiated figure is the full RAL; CCNL exclusions don't apply to it.
    contribution_base = (
        gross_annual
        if ral_override
        else money(gross_annual - annual.excluded_from_contributions)
    )
    tfr_base = (
        gross_annual if ral_override else money(gross_annual - annual.excluded_from_tfr)
    )
    hourly_divisor = ccnl.parameters.hourly_divisor.value_at(scenario.as_of)
    inps_employee_annual, inps_employer_annual = _inps_contributions(
        rules,
        scenario,
        gross_monthly,
        hourly_divisor,
        contribution_base,
        worker_category,
    )
    employer_funds_annual = _employer_funds(
        ccnl, worker_category, contribution_base, scenario.as_of
    )
    tfr_annual = _contrib.tfr(tfr_base, rules)

    # Not modelled (scope of a separate fiscal library): addizionali
    # regionali/comunali; detrazioni per carichi di famiglia (Art. 12 TUIR);
    # trattamento integrativo (Art. 1 D.L. 3/2020); sterilization of
    # detrazioni for redditi > EUR 200k (Art. 1 c. 3-4 L. 199/2025).
    taxable_income = money(gross_annual - inps_employee_annual)
    irpef_gross = _irpef.irpef_gross(taxable_income, rules)
    work_income_deduction = _irpef.work_income_deduction(gross_annual, rules)
    # When the employer is not a sostituto d'imposta, irpef_net is zeroed;
    # irpef_gross and work_income_deduction remain as informational figures.
    employer_withholds_irpef = not ccnl.meta.withholding_exempt
    irpef_net = (
        money(max(_ZERO, irpef_gross - work_income_deduction))
        if employer_withholds_irpef
        else _ZERO
    )

    net_annual = money(gross_annual - inps_employee_annual - irpef_net)
    net_monthly = money(net_annual / additional_months)
    employer_cost_annual = money(
        gross_annual + inps_employer_annual + employer_funds_annual + tfr_annual
    )

    return Payslip(
        ccnl_id=ccnl.meta.id,
        level_code=scenario.level_code,
        employment_type=scenario.employment.type,
        part_time_pct=scenario.part_time_pct,
        as_of=scenario.as_of,
        year=scenario.as_of.year,
        seniority_count=count,
        base_monthly=chain.base,
        seniority_monthly=chain.seniority,
        allowances_monthly=chain.allowances_total,
        ad_personam_monthly=ad_personam,
        gross_monthly=gross_monthly,
        gross_annual=gross_annual,
        hourly_rate=money(gross_monthly / hourly_divisor),
        apprenticeship_pct=apprenticeship_pct,
        apprenticeship_under_level_code=under_level_code,
        inps_employee_annual=inps_employee_annual,
        inps_employer_annual=inps_employer_annual,
        employer_funds_annual=employer_funds_annual,
        tfr_annual=tfr_annual,
        taxable_income=taxable_income,
        irpef_gross=irpef_gross,
        work_income_deduction=work_income_deduction,
        irpef_net=irpef_net,
        employer_withholds_irpef=employer_withholds_irpef,
        net_annual=net_annual,
        net_monthly=net_monthly,
        employer_cost_annual=employer_cost_annual,
    )


def _override_gross(
    negotiated_ral: Decimal | None,
    negotiated_destination_ral: Decimal | None,
    apprenticeship_pct: Decimal | None,
    gross_annual: Decimal,
    gross_monthly: Decimal,
    additional_months: Decimal,
) -> tuple[Decimal, Decimal]:
    """Return (gross_annual, gross_monthly) after applying any negotiated-RAL override.

    Returns:
        Tuple of (gross_annual, gross_monthly). Unchanged when no override is given.
    """
    if negotiated_ral is not None:
        # Actual agreed salary; taken as-is.
        gross_annual = money(negotiated_ral)
    elif negotiated_destination_ral is not None:
        # Destination-level RAL; apprenticeship_pct is guaranteed non-None here.
        gross_annual = money(negotiated_destination_ral * apprenticeship_pct)  # type: ignore[operator]
    else:
        return gross_annual, gross_monthly
    return gross_annual, money(gross_annual / additional_months)


def _validate_negotiated_ral(
    negotiated_ral: Decimal | None,
    negotiated_destination_ral: Decimal | None,
    employment: Employment,
) -> bool:
    """Validate the negotiated-RAL arguments and return whether an override is active.

    Returns:
        True when either negotiated_ral or negotiated_destination_ral is set.

    Raises:
        ValueError: If both fields are given, or if negotiated_destination_ral
            is used with a non-Apprentice employment type.
    """
    if negotiated_ral is not None and negotiated_destination_ral is not None:
        msg = "negotiated_ral and negotiated_destination_ral are mutually exclusive"
        raise ValueError(msg)
    if negotiated_destination_ral is not None and not isinstance(
        employment, Apprentice
    ):
        msg = "negotiated_destination_ral is only valid for Apprentice employment"
        raise ValueError(msg)
    return negotiated_ral is not None or negotiated_destination_ral is not None


def _resolve_seniority_count(
    seniority_rules: SeniorityIncrements,
    level_code: str,
    seniority_count: int | None,
    seniority_months: int | None,
) -> int:
    """Resolve the seniority increment count from either explicit input.

    Returns:
        The resolved seniority increment count, clamped to the level maximum.

    Raises:
        ValueError: If both seniority_count and seniority_months are given,
            or if either value is negative, or if seniority_count exceeds the maximum.
    """
    if seniority_count is not None and seniority_months is not None:
        msg = "seniority_count and seniority_months are mutually exclusive"
        raise ValueError(msg)
    maximum = seniority_rules.maximum_for(level_code)
    if seniority_months is not None:
        if seniority_months < 0:
            msg = f"seniority_months must be >= 0, got {seniority_months}"
            raise ValueError(msg)
        first = seniority_rules.first_cadence_for(level_code)
        if seniority_months < first:
            return 0
        count = 1 + (seniority_months - first) // seniority_rules.cadence_months
        return min(count, maximum)
    count = seniority_count or 0
    if count < 0:
        msg = f"seniority_count must be >= 0, got {count}"
        raise ValueError(msg)
    if count > maximum:
        msg = (
            f"seniority_count {count} exceeds the maximum of {maximum} "
            f"for level {level_code!r}"
        )
        raise ValueError(msg)
    return count


def _level_chain(
    ccnl: CCNL,
    level: Level,
    count: int,
    roles: frozenset[str],
    as_of: date,
    *,
    is_apprentice: bool,
) -> _MonthlyPayChain:
    seniority_rules = ccnl.parameters.seniority_increments
    # SIMPLIFICATION: apprentices accrue only the CCNL apprentice-specific
    # increment (if any); the level increments start after qualification.
    if is_apprentice:
        amount = (
            seniority_rules.apprentice_amount.value_at(as_of)
            if seniority_rules.apprentice_amount is not None
            else _ZERO
        )
    elif level.code in seniority_rules.amount_by_level:
        amount = seniority_rules.amount_by_level[level.code].value_at(as_of)
    else:
        amount = _ZERO
    allowances = tuple(
        (a, a.monthly.value_at(as_of))
        for a in level.fixed_allowances
        if a.role is None or a.role in roles
    )
    return _MonthlyPayChain(
        base=level.base_salary.value_at(as_of),
        seniority=money(amount * count),
        allowances=allowances,
    )


def _apprentice_chain(
    ccnl: CCNL,
    level: Level,
    employment: Apprentice,
    count: int,
    roles: frozenset[str],
    as_of: date,
) -> tuple[_MonthlyPayChain, Decimal | None, str | None]:
    track = _select_track(ccnl, level, employment)
    period_index = _find_period_index(track.periods, employment.months_elapsed)
    if isinstance(track, ApprenticeshipPercentage):
        reference = (
            ccnl.level_by_code(track.reference_level)
            if track.reference_level is not None
            else level
        )
        chain = _level_chain(ccnl, reference, count, roles, as_of, is_apprentice=True)
        return chain, track.periods[period_index].percentage, None
    period = track.periods[period_index]
    pay_level = ccnl.level_by_order(level.order - period.levels_below)
    chain = _level_chain(ccnl, pay_level, count, roles, as_of, is_apprentice=True)
    if period.midpoint_to_destination:
        # SIMPLIFICATION: the midpoint applies to the base salary only;
        # allowances are those of the pay level.
        dest_base = level.base_salary.value_at(as_of)
        chain = replace(chain, base=money((chain.base + dest_base) / _TWO))
    return chain, None, pay_level.code


def _select_track(
    ccnl: CCNL, level: Level, employment: Apprentice
) -> ApprenticeshipTrack:
    if employment.track is not None:
        track = ccnl.apprenticeship_track_named(employment.track)
        if level.code not in track.destination_levels:
            msg = (
                f"apprenticeship track {track.name!r} does not cover destination "
                f"level {level.code!r} (covers {track.destination_levels})"
            )
            raise ValueError(msg)
        return track
    candidates = ccnl.apprenticeship_tracks_for(level.code)
    if len(candidates) == 1:
        return candidates[0]
    if not candidates:
        eligible = _eligible_destination_levels(ccnl)
        msg = (
            f"CCNL '{ccnl.meta.id}' has no apprenticeship track for destination "
            f"level {level.code!r} (coverage.layer_2 is {ccnl.coverage.layer_2}; "
            f"eligible destination levels: {eligible})"
        )
        raise ValueError(msg)
    names = [t.name for t in candidates]
    msg = (
        f"destination level {level.code!r} is covered by several apprenticeship "
        f"tracks {names}; set Apprentice.track to choose one"
    )
    raise ValueError(msg)


def _eligible_destination_levels(ccnl: CCNL) -> list[str]:
    """Return sorted destination-level codes across all apprenticeship tracks.

    Returns:
        Sorted list of level codes covered by at least one apprenticeship track.
    """
    return sorted({c for t in ccnl.apprenticeship for c in t.destination_levels})


def _find_period_index(periods: Sequence[_MonthPeriod], months_elapsed: int) -> int:
    for i, period in enumerate(periods):
        if period.months_from <= months_elapsed and (
            period.months_until is None or months_elapsed < period.months_until
        ):
            return i
    msg = f"no apprenticeship period covers months_elapsed={months_elapsed}"
    raise ValueError(msg)


def _annualise(
    chain: _MonthlyPayChain, ad_personam: Decimal, additional_months: Decimal
) -> _AnnualisedPay:
    gross = (chain.base + chain.seniority + ad_personam) * additional_months
    excluded_contrib = _ZERO
    excluded_tfr = _ZERO
    for allowance, monthly in chain.allowances:
        months = (
            Decimal(allowance.months_per_year)
            if allowance.months_per_year is not None
            else additional_months
        )
        annual = monthly * months  # unrounded; rounding deferred to _annualise below
        gross += annual
        if not allowance.contribution_relevant:
            excluded_contrib += annual
        if not allowance.tfr_relevant:
            excluded_tfr += annual
    return _AnnualisedPay(
        gross=money(gross),
        excluded_from_contributions=money(excluded_contrib),
        excluded_from_tfr=money(excluded_tfr),
    )


def _inps_contributions(
    rules: YearRules,
    scenario: Scenario,
    gross_monthly: Decimal,
    hourly_divisor: Decimal,
    contribution_base: Decimal,
    worker_category: LevelCategory | None,
) -> tuple[Decimal, Decimal]:
    """Return (inps_employee_annual, inps_employer_annual) for the scenario.

    Routes to the flat per-hour domestic model when
    ``rules.domestic_contributions`` is set, otherwise uses the standard
    percentage model via :func:`~ccnl_engine.engine.contributions.resolve_rates`.

    Returns:
        A tuple of (employee annual INPS contribution, employer annual
        INPS contribution), both rounded to two decimal places.

    Raises:
        ValueError: If the domestic model is active and ``scenario.weekly_hours``
            is None.
    """
    if rules.domestic_contributions is not None:
        if scenario.weekly_hours is None:
            msg = "weekly_hours is required when rules.domestic_contributions is set"
            raise ValueError(msg)
        hourly_rate_for_bracket = money(gross_monthly / hourly_divisor)
        is_fixed_term = isinstance(scenario.employment, FixedTerm)
        emp_ph, er_ph = rules.domestic_contributions.resolve(
            hourly_rate_for_bracket,
            scenario.weekly_hours,
            is_fixed_term=is_fixed_term,
        )
        annual_hours = scenario.weekly_hours * 52
        return money(emp_ph * annual_hours), money(er_ph * annual_hours)
    rates = _contrib.resolve_rates(rules, scenario.employment, worker_category)
    employee = _contrib.inps_contribution(
        contribution_base,
        rates.employee_rate,
        rates.employee_ivs_rate,
        rules,
        ivs_ceiling_applies=scenario.ivs_ceiling_applies,
    )
    employer = _contrib.inps_contribution(
        contribution_base,
        rates.employer_rate,
        rates.employer_ivs_rate,
        rules,
        ivs_ceiling_applies=scenario.ivs_ceiling_applies,
    )
    return employee, employer


def _employer_funds(
    ccnl: CCNL,
    category: LevelCategory | None,
    contribution_base: Decimal,
    as_of: date,
) -> Decimal:
    total = _ZERO
    for fund in ccnl.parameters.employer_funds:
        if fund.applies_to(category):
            total += money(contribution_base * fund.rate.value_at(as_of))
    return money(total)
