"""Contractual pay resolution, scaling and annualisation."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.engine.payroll.domain.employee import (
    DestinationRalOverride,
    RalOverride,
)
from ccnl_engine.engine.payroll.domain.employment import Apprentice, FixedTerm
from ccnl_engine.engine.payroll.service.apprenticeship import _apprentice_chain
from ccnl_engine.engine.payroll.service.chain import _level_chain
from ccnl_engine.engine.payroll.service.rounding import money
from ccnl_engine.engine.payroll.service.seniority import _resolve_seniority_count
from ccnl_engine.engine.payroll.service.types import AnnualisedPay, MonthlyPayChain

if TYPE_CHECKING:
    from collections.abc import Sequence
    from datetime import date

    from ccnl_engine.engine.contract.domain.ccnl import (
        CCNL,
        Allowance,
        Level,
        LevelCategory,
        SupplementaryAllowance,
    )
    from ccnl_engine.engine.payroll.domain.employee import RalOverrideMode
    from ccnl_engine.engine.payroll.domain.employment import (
        Permanent,
    )
    from ccnl_engine.engine.payroll.domain.scenario import PayrollScenario

_ZERO = Decimal(0)


def _resolve_worker_category(
    scenario: PayrollScenario,
    level: Level,
) -> LevelCategory | None:
    """Return the effective worker category.

    Prefers an explicit override from the scenario; falls back to the
    level's own category.

    Returns:
        The resolved :class:`~ccnl_engine.engine.contract.domain.ccnl\
.LevelCategory`, or ``None``.
    """
    if scenario.employee.category is not None:
        return scenario.employee.category
    return level.category


def _resolve_chain_and_apprenticeship(
    ccnl: CCNL,
    level: Level,
    contract: Permanent | FixedTerm | Apprentice,
    count: int,
    scenario: PayrollScenario,
    as_of: date,
    worker_category: LevelCategory | None,
    seniority_months_val: int | None,
    ral_override_mode: RalOverrideMode | None,
) -> tuple[MonthlyPayChain, Decimal | None, str | None, Decimal]:
    """Build the pay chain and resolve apprenticeship factors.

    Returns:
        A 4-tuple of:
        - ``chain_full_time``: the full-time monthly pay chain
        - ``apprenticeship_pct``: the percentage factor (``None`` when not
          a percentage-track apprentice)
        - ``under_level_code``: the under-classification level code (``None``
          when not an under-classification apprentice)
        - ``effective_factor``: the combined part-time and apprenticeship
          scaling factor used for ``chain.scaled(...)``

    Raises:
        ValueError: If DestinationRalOverride is used with an
            under-classification apprenticeship track (no percentage factor).
    """
    effective_factor = scenario.employee.part_time_pct
    apprenticeship_pct: Decimal | None = None
    under_level_code: str | None = None
    if isinstance(contract, Apprentice):
        chain_full_time, apprenticeship_pct, under_level_code = _apprentice_chain(
            ccnl,
            level,
            contract,
            count,
            scenario.employee.roles,
            as_of,
            worker_category=worker_category,
            seniority_months=seniority_months_val,
        )
        if apprenticeship_pct is not None:
            effective_factor *= apprenticeship_pct
        if (
            isinstance(ral_override_mode, DestinationRalOverride)
            and apprenticeship_pct is None
        ):
            msg = (
                "DestinationRalOverride requires a percentage-based "
                "apprenticeship track; the resolved track uses under-classification"
            )
            raise ValueError(msg)
    else:
        chain_full_time = _level_chain(
            ccnl,
            level,
            count,
            scenario.employee.roles,
            as_of,
            worker_category=worker_category,
            is_apprentice=False,
            seniority_months=seniority_months_val,
        )
    return chain_full_time, apprenticeship_pct, under_level_code, effective_factor


def _extract_ral_override(
    scenario: PayrollScenario,
) -> RalOverrideMode | None:
    """Extract the RAL-override mode from the scenario's agreement.

    Returns:
        The ``ral_override`` from the :class:`~ccnl_engine.engine.payroll\
.domain.scenario.Agreement`, or ``None`` when no agreement is set.
    """
    agreement = scenario.employee.agreement
    return agreement.ral_override if agreement is not None else None


def _guard_ral_conflict(
    second_level_allowances: tuple[SupplementaryAllowance, ...],
    ral_override_mode: RalOverrideMode | None,
) -> None:
    """Raise if second-level allowances are combined with a RAL override.

    Raises:
        ValueError: When ``second_level_allowances`` is non-empty and a RAL
            override is also set.
    """
    if second_level_allowances and ral_override_mode is not None:
        msg = (
            "second_level_allowances cannot be combined with a RAL override: "
            "the negotiated figure already represents the full agreed salary"
        )
        raise ValueError(msg)


def _validate_ral_override(
    ral_override: RalOverrideMode | None,
    contract: Permanent | FixedTerm | Apprentice,
) -> bool:
    """Validate the RAL-override mode and return whether an override is active.

    Returns:
        True when a RAL override is set.

    Raises:
        ValueError: If ``DestinationRalOverride`` is used with a non-Apprentice
            contract type.
    """
    if isinstance(ral_override, DestinationRalOverride) and not isinstance(
        contract, Apprentice
    ):
        msg = "DestinationRalOverride is only valid for Apprentice employment"
        raise ValueError(msg)  # ruff: ignore[type-check-without-type-error]
    return ral_override is not None


def _override_gross(
    ral_override_mode: RalOverrideMode | None,
    apprenticeship_pct: Decimal | None,
    gross_annual: Decimal,
    gross_monthly: Decimal,
    additional_months: Decimal,
) -> tuple[Decimal, Decimal]:
    """Return (gross_annual, gross_monthly) after applying any RAL override.

    Returns:
        Tuple of (gross_annual, gross_monthly). Unchanged when no override is
        given.
    """
    if isinstance(ral_override_mode, RalOverride):
        # Actual agreed salary; taken as-is.
        gross_annual = money(ral_override_mode.value)
    elif isinstance(ral_override_mode, DestinationRalOverride):
        # Destination-level RAL; apprenticeship_pct is guaranteed non-None here.
        gross_annual = money(
            ral_override_mode.value * apprenticeship_pct  # type: ignore[operator]
        )
    else:
        return gross_annual, gross_monthly
    return gross_annual, money(gross_annual / additional_months)


def _scale_second_level(
    allowances: Sequence[SupplementaryAllowance],
    part_time_pct: Decimal,
    apprenticeship_pct: Decimal | None,
) -> tuple[list[tuple[Decimal, SupplementaryAllowance]], Decimal]:
    """Scale second-level allowances by part_time_pct and optionally apprenticeship_pct.

    Each item is multiplied by ``part_time_pct``; the apprenticeship percentage
    is applied on top only when ``apprenticeship_pct`` is not ``None`` and the
    item's ``apprenticeship_pct_relevant`` flag is ``True``.

    Returns:
        A tuple of (scaled pairs, monthly total) where scaled pairs are
        (scaled_monthly, allowance) items and monthly total is their rounded sum.
    """
    result: list[tuple[Decimal, SupplementaryAllowance]] = []
    total = _ZERO
    for sl in allowances:
        scaled = money(sl.monthly * part_time_pct)
        if apprenticeship_pct is not None and sl.apprenticeship_pct_relevant:
            scaled = money(scaled * apprenticeship_pct)
        result.append((scaled, sl))
        total += scaled
    return result, money(total)


def _annualise(
    chain: MonthlyPayChain,
    ad_personam: Decimal,
    additional_months: Decimal,
    second_level: Sequence[tuple[Decimal, SupplementaryAllowance]] = (),
) -> AnnualisedPay:
    """Annualise the monthly pay chain into gross and exclusion amounts.

    ``second_level`` carries already-scaled monthly amounts paired with their
    :class:`~ccnl_engine.engine.contract.domain.ccnl.SupplementaryAllowance`
    descriptors so that ``months_per_year``, ``contribution_relevant``, and
    ``tfr_relevant`` can be honoured just like CCNL-level allowances.

    Returns:
        An :class:`AnnualisedPay` with rounded gross and exclusion totals.
    """
    gross = (chain.base + chain.seniority + ad_personam) * additional_months
    excluded_contrib = _ZERO
    excluded_tfr = _ZERO

    # Normalise both allowance sequences to (monthly, item) so they can be
    # processed in a single loop.  chain.allowances stores (Allowance, monthly)
    # (reversed order compared to second_level).
    combined: list[tuple[Decimal, Allowance | SupplementaryAllowance]] = [
        (monthly, a) for a, monthly in chain.allowances
    ] + [(monthly, sl) for monthly, sl in second_level]

    for monthly, item in combined:
        months = (
            Decimal(item.months_per_year)
            if item.months_per_year is not None
            else additional_months
        )
        annual = monthly * months
        gross += annual
        if not item.contribution_relevant:
            excluded_contrib += annual
        if not item.tfr_relevant:
            excluded_tfr += annual

    return AnnualisedPay(
        gross=money(gross),
        excluded_from_contributions=money(excluded_contrib),
        excluded_from_tfr=money(excluded_tfr),
    )


@dataclass(frozen=True)
class GrossPay:
    """Resolved contractual pay, scaling factors and annual contribution bases."""

    level: Level
    worker_category: LevelCategory | None
    count: int
    chain_full_time: MonthlyPayChain
    chain: MonthlyPayChain
    apprenticeship_pct: Decimal | None
    under_level_code: str | None
    ad_personam: Decimal
    scaled_second_level: list[tuple[Decimal, SupplementaryAllowance]]
    second_level_monthly_total: Decimal
    additional_months: Decimal
    hourly_divisor: Decimal
    gross_monthly: Decimal
    gross_annual: Decimal
    contribution_base: Decimal
    tfr_base: Decimal


def compute_gross(scenario: PayrollScenario, ccnl: CCNL) -> GrossPay:
    """Resolve contractual pay and agreed overrides.

    Returns:
        Gross components and bases, before contributions or tax.
    """
    as_of = scenario.employment.calculation_date
    # Resolve inputs
    contract = scenario.employment.contract
    second_level_allowances = scenario.employment.employer.second_level_allowances
    ral_override_mode = _extract_ral_override(scenario)
    _guard_ral_conflict(second_level_allowances, ral_override_mode)

    ral_override = _validate_ral_override(ral_override_mode, contract)

    level = ccnl.level_by_code(scenario.employee.level_code)
    worker_category = _resolve_worker_category(scenario, level)

    seniority_count_val = scenario.employee.seniority_count
    seniority_months_val = scenario.employee.seniority_months_as_of(as_of)
    count = _resolve_seniority_count(
        ccnl.parameters.seniority_increments,
        scenario.employee.level_code,
        seniority_count_val,
        seniority_months_val,
        worker_category=worker_category,
    )
    additional_months = ccnl.parameters.additional_months.value_at(as_of)

    chain_full_time, apprenticeship_pct, under_level_code, effective_factor = (
        _resolve_chain_and_apprenticeship(
            ccnl,
            level,
            contract,
            count,
            scenario,
            as_of,
            worker_category,
            seniority_months_val,
            ral_override_mode,
        )
    )

    chain = (
        chain_full_time.scaled_selective(
            scenario.employee.part_time_pct, apprenticeship_pct
        )
        if apprenticeship_pct is not None
        else chain_full_time.scaled(effective_factor)
    )
    agreement = scenario.employee.agreement
    ad_personam = money(
        agreement.ad_personam_monthly if agreement is not None else _ZERO
    )
    scaled_second_level, second_level_monthly_total = _scale_second_level(
        second_level_allowances, scenario.employee.part_time_pct, apprenticeship_pct
    )

    gross_monthly = money(
        chain.base
        + chain.seniority
        + chain.allowances_total
        + ad_personam
        + second_level_monthly_total
    )
    annual = _annualise(chain, ad_personam, additional_months, scaled_second_level)
    gross_annual = annual.gross

    gross_annual, gross_monthly = _override_gross(
        ral_override_mode,
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
    hourly_divisor = ccnl.parameters.hourly_divisor.value_at(as_of)

    return GrossPay(
        level=level,
        worker_category=worker_category,
        count=count,
        chain_full_time=chain_full_time,
        chain=chain,
        apprenticeship_pct=apprenticeship_pct,
        under_level_code=under_level_code,
        ad_personam=ad_personam,
        scaled_second_level=scaled_second_level,
        second_level_monthly_total=second_level_monthly_total,
        additional_months=additional_months,
        hourly_divisor=hourly_divisor,
        gross_monthly=gross_monthly,
        gross_annual=gross_annual,
        contribution_base=contribution_base,
        tfr_base=tfr_base,
    )
