"""GrossPay dataclass and compute_gross entry point."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.engine.payroll.service.gross._helpers import (
    _annualise,
    _extract_ral_override,
    _guard_ral_conflict,
    _override_gross,
    _resolve_chain_and_apprenticeship,
    _resolve_worker_category,
    _scale_second_level,
    _validate_ral_override,
)
from ccnl_engine.engine.payroll.service.rounding import money
from ccnl_engine.engine.payroll.service.seniority import _resolve_seniority_count

if TYPE_CHECKING:
    from ccnl_engine.engine.contract.domain.ccnl import (
        CCNL,
        Level,
        LevelCategory,
        SupplementaryAllowance,
    )
    from ccnl_engine.engine.payroll.domain._internal_scenario import _InternalScenario
    from ccnl_engine.engine.payroll.service.types import MonthlyPayChain

_ZERO = Decimal(0)


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
    scaled_second_level: tuple[tuple[Decimal, SupplementaryAllowance], ...]
    second_level_monthly_total: Decimal
    additional_months: Decimal
    hourly_divisor: Decimal
    gross_monthly: Decimal
    gross_annual: Decimal
    contribution_base: Decimal
    tfr_base: Decimal


def compute_gross(scenario: _InternalScenario, ccnl: CCNL) -> GrossPay:
    """Resolve contractual pay and agreed overrides.

    Returns:
        Gross components and bases, before contributions or tax.
    """
    as_of = scenario.employment.as_of
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
            scenario.employee.part_time_ratio, apprenticeship_pct
        )
        if apprenticeship_pct is not None
        else chain_full_time.scaled(effective_factor)
    )
    agreement = scenario.employee.agreement
    ad_personam = money(
        agreement.ad_personam_monthly if agreement is not None else _ZERO
    )
    scaled_second_level, second_level_monthly_total = _scale_second_level(
        second_level_allowances, scenario.employee.part_time_ratio, apprenticeship_pct
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
