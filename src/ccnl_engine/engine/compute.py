"""Gross-to-net and employer cost computation."""

from __future__ import annotations

from dataclasses import dataclass, replace
from decimal import Decimal
from typing import TYPE_CHECKING, Protocol

from ccnl_engine.engine import contributions as _contrib
from ccnl_engine.engine import irpef as _irpef
from ccnl_engine.engine.result import ComputationResult
from ccnl_engine.engine.rounding import money
from ccnl_engine.models.apprenticeship import ApprenticeshipPercentage
from ccnl_engine.models.employment import Apprentice

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
class _Chain:
    """Full-time monthly pay components of one level on one date."""

    base: Decimal
    seniority: Decimal
    allowances: tuple[tuple[Allowance, Decimal], ...]

    def scaled(self, factor: Decimal) -> _Chain:
        return _Chain(
            base=money(self.base * factor),
            seniority=money(self.seniority * factor),
            allowances=tuple((a, money(v * factor)) for a, v in self.allowances),
        )

    @property
    def allowances_total(self) -> Decimal:
        return money(sum((v for _, v in self.allowances), _ZERO))


@dataclass(frozen=True)
class _Annual:
    gross: Decimal
    excluded_from_contributions: Decimal
    excluded_from_tfr: Decimal


def compute(
    ccnl: CCNL,
    level_code: str,
    as_of: date,
    rules: YearRules,
    employment: Employment,
    part_time_pct: Decimal = _ONE,
    seniority_count: int | None = None,
    seniority_months: int | None = None,
    negotiated_ral: Decimal | None = None,
    negotiated_destination_ral: Decimal | None = None,
    roles: frozenset[str] = frozenset(),
    ad_personam_monthly: Decimal = _ZERO,
    category: LevelCategory | None = None,
) -> ComputationResult:
    """Compute gross-to-net salary and employer cost for a given scenario.

    ``seniority_count`` and ``seniority_months`` are mutually exclusive; when
    neither is given no seniority increment applies. ``roles`` selects the
    role-restricted allowances the worker is entitled to. ``ad_personam_monthly``
    is an individual frozen element (e.g. pre-abolition seniority) added to
    gross as given, not scaled by ``part_time_pct``. ``category`` overrides the
    level's worker category when a level hosts several categories (e.g.
    operai and impiegati sharing level 3 in edilizia).

    ``negotiated_ral`` replaces the CCNL-derived gross for any employment type
    and is taken as-is (no further scaling).  ``negotiated_destination_ral``
    is the destination-level RAL for percentage-based apprentices: the engine
    applies ``apprenticeship_pct`` to it, producing the actual apprentice pay.
    The two fields are mutually exclusive.

    Returns:
        ComputationResult with all gross, net, and cost figures.

    Raises:
        ValueError: If part_time_pct is not in (0, 1], ad_personam_monthly < 0,
            seniority arguments are invalid, negotiated_ral and
            negotiated_destination_ral are both supplied,
            negotiated_destination_ral is used with a non-Apprentice employment,
            or negotiated_destination_ral is used with an under-classification
            apprenticeship track.
    """
    if not (_ZERO < part_time_pct <= _ONE):
        msg = f"part_time_pct must be in (0, 1], got {part_time_pct}"
        raise ValueError(msg)
    if ad_personam_monthly < _ZERO:
        msg = f"ad_personam_monthly must be >= 0, got {ad_personam_monthly}"
        raise ValueError(msg)
    _validate_negotiated_ral(negotiated_ral, negotiated_destination_ral, employment)

    level = ccnl.level_by_code(level_code)
    worker_category = category if category is not None else level.category
    count = _resolve_seniority_count(
        ccnl.parameters.seniority_increments,
        level_code,
        seniority_count,
        seniority_months,
    )
    if worker_category in ccnl.parameters.seniority_increments.excluded_categories:
        count = 0
    additional_months = ccnl.parameters.additional_months.value_at(as_of)

    factor = part_time_pct
    apprenticeship_pct: Decimal | None = None
    under_level_code: str | None = None
    if isinstance(employment, Apprentice):
        chain_ft, apprenticeship_pct, under_level_code = _apprentice_chain(
            ccnl, level, employment, count, roles, as_of
        )
        if apprenticeship_pct is not None:
            factor *= apprenticeship_pct
        if negotiated_destination_ral is not None and apprenticeship_pct is None:
            msg = (
                "negotiated_destination_ral requires a percentage-based apprenticeship "
                "track; the resolved track uses under-classification"
            )
            raise ValueError(msg)
    else:
        chain_ft = _level_chain(ccnl, level, count, roles, as_of, apprentice=False)

    chain = chain_ft.scaled(factor)
    ad_personam = money(ad_personam_monthly)
    gross_monthly = money(
        chain.base + chain.seniority + chain.allowances_total + ad_personam
    )
    annual = _annualise(chain, ad_personam, additional_months)
    gross_annual = annual.gross

    gross_annual, gross_monthly = _override_gross(
        negotiated_ral,
        negotiated_destination_ral,
        apprenticeship_pct,
        gross_annual,
        gross_monthly,
        additional_months,
    )

    # The negotiated figure is the full RAL; CCNL exclusions don't apply to it.
    ral_override = negotiated_ral is not None or negotiated_destination_ral is not None
    contribution_base = (
        gross_annual
        if ral_override
        else money(gross_annual - annual.excluded_from_contributions)
    )
    tfr_base = (
        gross_annual if ral_override else money(gross_annual - annual.excluded_from_tfr)
    )
    rates = _contrib.resolve_rates(rules, employment, worker_category)
    inps_employee_annual = _contrib.inps_contribution(
        contribution_base, rates.employee_rate, rules
    )
    inps_employer_annual = _contrib.inps_contribution(
        contribution_base, rates.employer_rate, rules
    )
    employer_funds_annual = _employer_funds(
        ccnl, worker_category, contribution_base, as_of
    )
    tfr_annual = _contrib.tfr(tfr_base, rules)

    # SIMPLIFICATION: no addizionali regionali/comunali; no detrazioni per
    # carichi di famiglia; no sterilization mechanism for incomes > EUR 200k
    # (Art. 1 c. 3-4 L. 199/2025).
    taxable_income = money(gross_annual - inps_employee_annual)
    irpef_gross_val = _irpef.irpef_gross(taxable_income, rules)
    work_income_deduction_val = _irpef.work_income_deduction(gross_annual, rules)
    irpef_net = money(max(_ZERO, irpef_gross_val - work_income_deduction_val))

    net_annual = money(gross_annual - inps_employee_annual - irpef_net)
    net_monthly = money(net_annual / additional_months)
    employer_cost_annual = money(
        gross_annual + inps_employer_annual + employer_funds_annual + tfr_annual
    )
    hourly_divisor = ccnl.parameters.hourly_divisor.value_at(as_of)

    return ComputationResult(
        ccnl_id=ccnl.meta.id,
        level_code=level_code,
        employment_type=employment.type,
        part_time_pct=part_time_pct,
        as_of=as_of,
        year=as_of.year,
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
        irpef_gross=irpef_gross_val,
        work_income_deduction=work_income_deduction_val,
        irpef_net=irpef_net,
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
) -> None:
    if negotiated_ral is not None and negotiated_destination_ral is not None:
        msg = "negotiated_ral and negotiated_destination_ral are mutually exclusive"
        raise ValueError(msg)
    if negotiated_destination_ral is not None and not isinstance(
        employment, Apprentice
    ):
        msg = "negotiated_destination_ral is only valid for Apprentice employment"
        raise ValueError(msg)


def _resolve_seniority_count(
    rules: SeniorityIncrements,
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
    maximum = rules.maximum_for(level_code)
    if seniority_months is not None:
        if seniority_months < 0:
            msg = f"seniority_months must be >= 0, got {seniority_months}"
            raise ValueError(msg)
        first = rules.first_cadence_for(level_code)
        if seniority_months < first:
            return 0
        count = 1 + (seniority_months - first) // rules.cadence_months
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
    apprentice: bool,
) -> _Chain:
    rules = ccnl.parameters.seniority_increments
    # SIMPLIFICATION: apprentices accrue only the CCNL apprentice-specific
    # increment (if any); the level increments start after qualification.
    if apprentice:
        amount = (
            rules.apprentice_amount.value_at(as_of)
            if rules.apprentice_amount is not None
            else _ZERO
        )
    elif level.code in rules.amount_by_level:
        amount = rules.amount_by_level[level.code].value_at(as_of)
    else:
        amount = _ZERO
    allowances = tuple(
        (a, a.monthly.value_at(as_of))
        for a in level.fixed_allowances
        if a.role is None or a.role in roles
    )
    return _Chain(
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
) -> tuple[_Chain, Decimal | None, str | None]:
    track = _select_track(ccnl, level, employment)
    period_index = _find_period_index(track.periods, employment.months_elapsed)
    if isinstance(track, ApprenticeshipPercentage):
        reference = (
            ccnl.level_by_code(track.reference_level)
            if track.reference_level is not None
            else level
        )
        chain = _level_chain(ccnl, reference, count, roles, as_of, apprentice=True)
        return chain, track.periods[period_index].percentage, None
    period = track.periods[period_index]
    pay_level = ccnl.level_by_order(level.order - period.levels_below)
    chain = _level_chain(ccnl, pay_level, count, roles, as_of, apprentice=True)
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
        eligible = sorted({
            c for t in ccnl.apprenticeship for c in t.destination_levels
        })
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


def _find_period_index(periods: Sequence[_MonthPeriod], months_elapsed: int) -> int:
    for i, period in enumerate(periods):
        if period.months_from <= months_elapsed and (
            period.months_until is None or months_elapsed < period.months_until
        ):
            return i
    msg = f"no apprenticeship period covers months_elapsed={months_elapsed}"
    raise ValueError(msg)


def _annualise(
    chain: _Chain, ad_personam: Decimal, additional_months: Decimal
) -> _Annual:
    gross = (chain.base + chain.seniority + ad_personam) * additional_months
    excluded_contrib = _ZERO
    excluded_tfr = _ZERO
    for allowance, monthly in chain.allowances:
        months = (
            Decimal(allowance.months_per_year)
            if allowance.months_per_year is not None
            else additional_months
        )
        annual = money(monthly * months)
        gross += annual
        if not allowance.contribution_relevant:
            excluded_contrib += annual
        if not allowance.tfr_relevant:
            excluded_tfr += annual
    return _Annual(
        gross=money(gross),
        excluded_from_contributions=excluded_contrib,
        excluded_from_tfr=excluded_tfr,
    )


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
