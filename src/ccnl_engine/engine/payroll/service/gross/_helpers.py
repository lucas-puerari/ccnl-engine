"""Internal helpers for gross pay resolution."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.engine.errors import InvalidInputError
from ccnl_engine.engine.payroll.domain.employee import (
    DestinationRalOverride,
    RalOverride,
)
from ccnl_engine.engine.payroll.domain.employment import Apprentice, FixedTerm
from ccnl_engine.engine.payroll.service.apprenticeship import _apprentice_chain
from ccnl_engine.engine.payroll.service.chain import _level_chain
from ccnl_engine.engine.payroll.service.rounding import money
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
    from ccnl_engine.engine.payroll.domain._internal_scenario import _InternalScenario
    from ccnl_engine.engine.payroll.domain.employee import RalOverrideMode
    from ccnl_engine.engine.payroll.domain.employment import (
        Permanent,
    )

_ZERO = Decimal(0)


def _resolve_worker_category(
    scenario: _InternalScenario,
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
    scenario: _InternalScenario,
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
        InvalidInputError: If DestinationRalOverride is used with an
            under-classification apprenticeship track (no percentage factor).
    """
    effective_factor = scenario.employee.part_time_ratio
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
            remediation = (
                "Use RalOverride instead of DestinationRalOverride for "
                "under-classification tracks."
            )
            raise InvalidInputError(
                msg,
                feature="apprenticeship",
                remediation=remediation,
            )
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
    scenario: _InternalScenario,
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
        InvalidInputError: When ``second_level_allowances`` is non-empty and a
            RAL override is also set.
    """
    if second_level_allowances and ral_override_mode is not None:
        msg = (
            "second_level_allowances cannot be combined with a RAL override: "
            "the negotiated figure already represents the full agreed salary"
        )
        remediation = (
            "Remove the RAL override or the second_level_allowances from the scenario."
        )
        raise InvalidInputError(msg, remediation=remediation)


def _validate_ral_override(
    ral_override: RalOverrideMode | None,
    contract: Permanent | FixedTerm | Apprentice,
) -> bool:
    """Validate the RAL-override mode and return whether an override is active.

    Returns:
        True when a RAL override is set.

    Raises:
        InvalidInputError: If ``DestinationRalOverride`` is used with a
            non-Apprentice contract type.
    """
    if isinstance(ral_override, DestinationRalOverride) and not isinstance(
        contract, Apprentice
    ):
        msg = "DestinationRalOverride is only valid for Apprentice employment"
        raise InvalidInputError(
            msg,
            feature="apprenticeship",
            remediation="Use RalOverride for non-apprentice contracts.",
        )
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
    part_time_ratio: Decimal,
    apprenticeship_pct: Decimal | None,
) -> tuple[tuple[tuple[Decimal, SupplementaryAllowance], ...], Decimal]:
    """Scale second-level allowances by part_time_ratio and apprenticeship_pct.

    All applicable scaling factors (part-time, then apprenticeship when present
    and relevant) are combined *before* a single ``money()`` rounding call.
    This matches the CCNL chain policy: the product of all factors is computed
    first, then the result is rounded once to the nearest cent.

    Returns:
        A tuple of (scaled pairs, monthly total) where scaled pairs are a
        frozen tuple of (scaled_monthly, allowance) items and monthly total
        is their rounded sum.
    """
    items: list[tuple[Decimal, SupplementaryAllowance]] = []
    total = _ZERO
    for sl in allowances:
        raw = sl.monthly * part_time_ratio
        if apprenticeship_pct is not None and sl.apprenticeship_pct_relevant:
            raw *= apprenticeship_pct
        scaled = money(raw)
        items.append((scaled, sl))
        total += scaled
    return tuple(items), money(total)


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
