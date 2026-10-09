"""Contributions to the end-of-service fund and the credit of a public employee.

INPS Gestione Dipendenti Pubblici finances the TFS and the TFR of the
public employees with a contribution on 80% of the pay: ENPAS for the
State, INADEL for the enti locali and the health service
(:class:`~ccnl_engine.tax.domain.contribution_rules.EndOfServiceRates`).
Under the TFS the worker pays 2.50% of the base and the administration the
rest.  Under the TFR at INPS the administration pays the whole contribution
and "la retribuzione lorda viene ridotta in misura pari al contributo
previdenziale obbligatorio soppresso" (DPCM 20 dicembre 1999 art. 1 c. 3):
the run posts that reduction as a negative earning of the gross
(:mod:`~ccnl_engine.payroll.application.period._public_tfr_reduction`), so
the net, the IRPEF taxable and the cost of the administration equal those
of the TFS ("La soppressione del contributo non determina effetti sulla
retribuzione imponibile ai fini fiscali", c. 2), while the INPS and the
end-of-service bases keep the unreduced pay (the recupero of c. 3).  An
employer that keeps the TFR itself (c. 6 and 8) pays the Gestione nothing.
"""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.domain.contributions import ContributionComponent
from ccnl_engine.payroll.domain.decisions import CalculationIssue, CalculationStatus
from ccnl_engine.payroll.domain.employment_facts import PublicEndOfService
from ccnl_engine.payroll.domain.rounding import money

if TYPE_CHECKING:
    from ccnl_engine.payroll.application.amounts._types import _AmountsInput
    from ccnl_engine.payroll.domain.contributions import ContributionBreakdown
    from ccnl_engine.tax.domain.contribution_rules import EndOfServiceRates

__all__ = [
    "END_OF_SERVICE_UNKNOWN",
    "end_of_service_base",
    "end_of_service_employee_rate",
    "end_of_service_issue",
    "with_end_of_service",
    "with_public_credit",
]

_ZERO = Decimal(0)
#: A public employee needs the end-of-service regime to be stated.
END_OF_SERVICE_UNKNOWN = CalculationIssue(
    code="public_end_of_service_unknown",
    message=(
        "the contributions of a public employee to INPS Gestione Dipendenti "
        "Pubblici and the accrual of the TFR depend on the end-of-service "
        "regime (TFS, TFR at INPS or TFR at the employer), which the "
        "employment does not state: the amounts shown leave the "
        "contributions out; state Employment.public_end_of_service"
    ),
    status=CalculationStatus.INCOMPLETE,
    fact="public_end_of_service",
)


def end_of_service_issue(inp: _AmountsInput) -> CalculationIssue | None:
    """Return the missing-fact issue of a public employee without a regime.

    Returns:
        :data:`END_OF_SERVICE_UNKNOWN` when the year has end-of-service
        rates for the CCNL and the regime is not stated, else ``None``.
    """
    rates = None if inp.rules.inps is None else inp.rules.inps.end_of_service
    if rates is None or inp.public_end_of_service is not None:
        return None
    return END_OF_SERVICE_UNKNOWN


def _component(name: str, base: Decimal, rate: Decimal) -> ContributionComponent:
    return ContributionComponent(name, base, rate, money(base * rate))


def _components(
    inp: _AmountsInput,
) -> tuple[tuple[ContributionComponent, ...], tuple[ContributionComponent, ...]]:
    """Return the employee and employer components of the run.

    Returns:
        Nothing without rates or a regime with contributions to the
        Gestione, or on a tredicesima the fund leaves out of the base.
    """
    rates = None if inp.rules.inps is None else inp.rules.inps.end_of_service
    regime = inp.public_end_of_service
    pay = inp.tfr_pay
    base = end_of_service_base(rates, regime, pay, extra=inp.additional_month)
    if rates is None or base is None:
        return (), ()
    if regime is PublicEndOfService.TFS:
        return (
            (_component("tfs_employee", base, rates.tfs_employee_rate),),
            (_component("tfs_employer", base, rates.tfs_employer_rate),),
        )
    return (), (_component("tfr_employer", base, rates.tfr_employer_rate),)


def end_of_service_base(
    rates: EndOfServiceRates | None,
    regime: PublicEndOfService | None,
    pay: Decimal,
    *,
    extra: bool,
) -> Decimal | None:
    """Return the end-of-service base of a run, ``None`` when it has none.

    Args:
        rates: End-of-service rates of the CCNL's fund, ``None`` outside the
            public administrations.
        regime: End-of-service regime of the worker.
        pay: TFR base of the run, the unreduced pay (DPCM art. 1 c. 3).
        extra: Whether the run pays a tredicesima or a quattordicesima.

    Returns:
        80% of ``pay`` under the TFS or the TFR at INPS, unless the fund
        leaves the extra month out of its base.
    """
    at_inps = regime in {PublicEndOfService.TFS, PublicEndOfService.TFR_INPS}
    if rates is None or not at_inps or (extra and not rates.thirteenth):
        return None
    return money(pay * rates.base_share)


def with_end_of_service(
    inp: _AmountsInput, breakdown: ContributionBreakdown
) -> ContributionBreakdown:
    """Return ``breakdown`` with the end-of-service contributions of the run.

    Returns:
        The breakdown with the employee and employer components added to
        its totals, employee components before the employer ones.
    """
    employee, employer = _components(inp)
    return _added(breakdown, employee, employer)


def _added(
    breakdown: ContributionBreakdown,
    employee: tuple[ContributionComponent, ...],
    employer: tuple[ContributionComponent, ...] = (),
) -> ContributionBreakdown:
    """Return ``breakdown`` with components added, employee ones first.

    Returns:
        The breakdown with the amounts added to its totals.
    """
    if not employee and not employer:
        return breakdown
    components = breakdown.components
    split = next(
        (i for i, c in enumerate(components) if c.name.endswith("_employer")),
        len(components),
    )
    return replace(
        breakdown,
        employee=breakdown.employee + sum((c.amount for c in employee), _ZERO),
        employer=breakdown.employer + sum((c.amount for c in employer), _ZERO),
        components=(*components[:split], *employee, *components[split:], *employer),
    )


def end_of_service_employee_rate(inp: _AmountsInput) -> Decimal:
    """Return the share of the gross the worker gives up for the fund.

    Returns:
        The 2.50% of the worker times the share of the base, under the TFS
        (a contribution) or the TFR at INPS (a reduction of the gross); zero
        otherwise.  It projects the taxable of the slots still to come.
    """
    rates = None if inp.rules.inps is None else inp.rules.inps.end_of_service
    pay = inp.tfr_pay
    base = end_of_service_base(rates, inp.public_end_of_service, pay, extra=False)
    if rates is None or base is None:
        return _ZERO
    return rates.tfs_employee_rate * rates.base_share


def with_public_credit(
    inp: _AmountsInput, breakdown: ContributionBreakdown, pension_base: Decimal
) -> tuple[ContributionBreakdown, Decimal]:
    """Return ``breakdown`` with the credit contribution of a public employee.

    L. 662/1996 art. 1 c. 242: 0.35% of the "retribuzione contributiva e
    pensionabile", the pension base of the run, whatever the regime.

    Returns:
        The breakdown with the ``credit_employee`` component, and its rate;
        ``breakdown`` and zero outside the public administrations.
    """
    credit = None if inp.rules.inps is None else inp.rules.inps.public_credit
    if credit is None:
        return breakdown, _ZERO
    component = _component("credit_employee", pension_base, credit.employee_rate)
    return _added(breakdown, (component,)), credit.employee_rate
