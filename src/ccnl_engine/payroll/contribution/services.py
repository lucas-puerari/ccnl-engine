"""INPS contributions and TFR accrual of one run."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import TYPE_CHECKING

from ccnl_engine.payroll.amount.policies_rounding import contribution_base, money
from ccnl_engine.payroll.assurance.models_decision import (
    CalculationIssue,
    CalculationStatus,
)
from ccnl_engine.payroll.contribution.rules import resolve_contributions
from ccnl_engine.payroll.contribution.rules_rate import resolve_rates
from ccnl_engine.payroll.contribution.services_domestic import (
    compute_domestic_breakdown,
)
from ccnl_engine.payroll.contribution.services_public_end_of_service import (
    end_of_service_employee_rate,
    with_enam,
    with_end_of_service,
    with_life_insurance,
    with_public_credit,
)
from ccnl_engine.payroll.contribution.services_solidarity_fund import (
    with_solidarity_fund,
)
from ccnl_engine.payroll.employment.inputs import Apprentice
from ccnl_engine.payroll.employment.inputs_fact import PublicEndOfService
from ccnl_engine.payroll.ledger.models import AccountKind
from ccnl_engine.payroll.period.services_shared import _ZERO

if TYPE_CHECKING:
    from decimal import Decimal

    from ccnl_engine.payroll.amount.types import _AmountsInput
    from ccnl_engine.payroll.contribution.results import ContributionBreakdown

#: An employer of up to five employees in the FIS must say whether its rate
#: is cut (D.Lgs. 148/2015 art. 29 c. 8-bis).
FIS_REDUCTION_UNKNOWN = CalculationIssue(
    code="fis_reduction_unknown",
    message=(
        "an employer of the fondo di integrazione salariale with up to five "
        "employees pays 40% less FIS when it has not applied for the assegno "
        "di integrazione salariale for twenty-four months (D.Lgs. 148/2015 "
        "art. 29 c. 8-bis); the amounts shown charge the full rate; state "
        "EmployerProfile.fis_reduction"
    ),
    status=CalculationStatus.INCOMPLETE,
    fact="fis_reduction",
)

#: An agricultural employer must say the zone its contributions are cut in.
AGRICULTURAL_ZONE_UNKNOWN = CalculationIssue(
    code="agricultural_zone_unknown",
    message=(
        "an agricultural employer of a zona svantaggiata pays 68% less "
        "employer contributions, of a zona particolarmente svantaggiata 75% "
        "less (INPS circ. 43/2026 par. 7); the amounts shown charge the full "
        "rates; state EmployerProfile.agricultural_zone"
    ),
    status=CalculationStatus.INCOMPLETE,
    fact="agricultural_zone",
)


def _raised(inp: _AmountsInput, base: Decimal) -> Decimal:
    """Return ``base`` raised to the minimum INPS base of the run.

    Returns:
        ``base``, or the minimum when one is determined and higher, rounded
        to the whole euro (:func:`contribution_base`).
    """
    minimum = inp.inps_minimum
    whole_euro = inp.rules.inps is None or inp.rules.inps.base_whole_euro
    return contribution_base(
        base if minimum is None else max(base, minimum), whole_euro=whole_euro
    )


def _ordinary_breakdown(inp: _AmountsInput, base: Decimal) -> ContributionBreakdown:
    """Return the ordinary INPS breakdown of ``base`` for the run.

    Returns:
        The breakdown with the YTD INPS base, the IVS ceiling and the
        additional 1% IVS position of the run.
    """
    return resolve_contributions(
        base,
        inp.rules,
        inp.contract_type,
        inp.category,
        ytd_inps_base=inp.ytd_inps_base,
        ivs_ceiling_applies=inp.ivs_ceiling_applies,
        additional=inp.additional_ivs,
    )


def run_contributions(inp: _AmountsInput) -> tuple[ContributionBreakdown, Decimal]:
    """Return the INPS breakdown of the run and the employee rate for IRPEF.

    Domestic CCNLs have no ordinary INPS rules: their flat per-hour
    contributions apply and no employee rate is projected on the slots
    still to come.

    Returns:
        ``(breakdown, employee_rate)``.
    """
    if inp.rules.inps is not None:
        base = _raised(inp, inp.monthly_gross + inp.event_inps_base)
        breakdown = with_end_of_service(inp, _ordinary_breakdown(inp, base))
        breakdown, credit = with_public_credit(inp, breakdown, base)
        breakdown, life = with_life_insurance(inp, breakdown, base)
        breakdown, enam = with_enam(inp, breakdown)
        breakdown, fund = with_solidarity_fund(inp, breakdown)
        rates = resolve_rates(inp.rules, inp.contract_type, inp.category)
        public = end_of_service_employee_rate(inp) + credit + life + enam
        employee = rates.employee_rate + public + fund
        return breakdown, employee
    breakdown = compute_domestic_breakdown(
        inp.rules,
        inp.weekly_hours,
        inp.contributable_hours,
        inp.domestic_hourly_rate,
        inp.contract_type,
    )
    return breakdown, _ZERO


#: Regimes whose TFR the employer does not accrue.
_AT_INPS = frozenset({PublicEndOfService.TFS, PublicEndOfService.TFR_INPS})
#: Code of the issue of a TFR whose Fondo Tesoreria destination is unknown.
TFR_TREASURY_FUND_CODE = "tfr_treasury_fund_unknown"


@dataclass(frozen=True)
class TfrAccrual:
    """The TFR of one run: the art. 2120 c.c. quota less the additional IVS.

    Attributes:
        quota: TFR base of the run over the accrual divisor, rounded.
        ivs_base: Employer IVS base of the run the additional IVS is
            charged on, zero when no deduction applies.
        ivs_rate: Additional IVS rate of L. 297/1982 art. 3 c. 15, zero
            when no deduction applies.
        deduction: Additional IVS deducted from the quota under c. 16,
            never above the quota.
        to_pension_fund: The TFR is paid to the complementary pension fund
            the worker is enrolled in.
        treasury_fund: The TFR not paid to a pension fund is paid to the
            Fondo Tesoreria INPS (L. 296/2006 art. 1 c. 756); ``None`` when
            the request does not say.
        public: End-of-service regime of a public employee: under the TFS
            no TFR accrues, under the TFR at INPS it accrues notionally at
            INPS (DPCM 20 dicembre 1999 art. 1 c. 6); neither is posted.
    """

    quota: Decimal
    ivs_base: Decimal = _ZERO
    ivs_rate: Decimal = _ZERO
    deduction: Decimal = _ZERO
    to_pension_fund: bool = False
    treasury_fund: bool | None = False
    public: PublicEndOfService | None = None

    @property
    def notional(self) -> bool:
        """Whether INPS, not the employer, accrues the TFR of the run."""
        return self.public in _AT_INPS

    @property
    def conferred(self) -> bool:
        """Whether the TFR of the run leaves the company for a fund.

        True when it goes to the pension fund or to the Fondo Tesoreria;
        False when it stays in the company, when INPS accrues it and while
        the Fondo Tesoreria destination is unknown.
        """
        return not self.notional and (
            self.to_pension_fund or self.treasury_fund is True
        )

    @property
    def amount(self) -> Decimal:
        """TFR accrued on the run, in the company or paid to a fund."""
        return _ZERO if self.notional else self.quota - self.deduction

    @property
    def destination(self) -> str:
        """Where the TFR of the run goes: an account, or the INPS regime."""
        if self.public is PublicEndOfService.TFS:
            return "tfs"
        return "inps_notional" if self.notional else self.account.value

    @property
    def account(self) -> AccountKind:
        """Account the TFR of the run is posted to.

        The pension fund when the worker pays the TFR to it, else the
        Fondo Tesoreria when the employer pays it there, else the company
        accrual (also while the Fondo Tesoreria destination is unknown).
        """
        if self.to_pension_fund:
            return AccountKind.PENSION_FUND_TFR
        if self.treasury_fund:
            return AccountKind.TFR_TREASURY_FUND
        return AccountKind.TFR_ACCRUAL

    def issues(self) -> tuple[CalculationIssue, ...]:
        """Return the issue of a TFR whose destination is unknown.

        Returns:
            One ``missing_fact`` issue for ``tfr_treasury_fund`` when a
            non-zero TFR stays out of a pension fund and the request does
            not say whether it goes to the Fondo Tesoreria; nothing else.
        """
        if self.to_pension_fund or self.treasury_fund is not None or not self.amount:
            return ()
        return (
            CalculationIssue(
                code=TFR_TREASURY_FUND_CODE,
                message=(
                    "tfr: whether the TFR goes to the Fondo Tesoreria INPS "
                    "(L. 296/2006 art. 1 c. 756) is not known; it is posted to "
                    "tfr_accrual: set Employment.tfr_treasury_fund"
                ),
                status=CalculationStatus.PROVISIONAL,
                fact="tfr_treasury_fund",
            ),
        )


def _tfr_paid_to_fund(inp: _AmountsInput) -> bool:
    """Return whether the TFR of the run is paid to the pension fund.

    A public employee's TFR conferred to the fund is not paid: INPS
    Gestione Dipendenti Pubblici accrues it notionally and pays it at the
    termination (Perseo Sirio and Espero, Scheda 'I destinatari e i
    contributi'), so it stays where the run accrues it.

    Returns:
        True when the worker confers the TFR and it is paid to the fund.
    """
    pension = inp.pension
    return pension is not None and pension.tfr_to_fund and not pension.tfr_notional


def _ivs_employer_base(breakdown: ContributionBreakdown) -> Decimal:
    """Return the employer IVS base of the run, zero without an IVS share.

    Returns:
        The base of the ``ivs_employer`` component, capped at the
        massimale when it applies.
    """
    return next(
        (c.base for c in breakdown.components if c.name == "ivs_employer"), _ZERO
    )


def tfr_accrual(inp: _AmountsInput, breakdown: ContributionBreakdown) -> TfrAccrual:
    """Return the TFR accrued on the run.

    L. 297/1982 art. 3 c. 16: the employer deducts from the TFR quota of
    the period the 0.50% additional IVS contribution of c. 15, charged on
    the IVS base of the same period; when the TFR goes to a pension fund
    the deduction reduces the TFR paid to it.  A quota smaller than the
    contribution is deducted down to zero.  Sectors with no additional
    IVS rule accrue the whole quota; so do apprentices, for whom the
    contribution is not due (INPS circ. 70/2007, note 5).  The Fondo
    Tesoreria takes the quota net of the deduction (L. 296/2006 art. 1
    c. 756).  The base counts the benefits provided in kind (CCNL lavoro
    domestico art. 41 c. 1: the valore convenzionale of board and lodging).

    Returns:
        The quota over the accrual divisor, the deduction taken from it and
        its destination.
    """
    tfr = inp.rules.tfr
    base = inp.tfr_pay
    quota = money(base / tfr.accrual_divisor)
    public = inp.public.end_of_service
    accrual = TfrAccrual(
        quota=_ZERO if public is PublicEndOfService.TFS else quota,
        to_pension_fund=_tfr_paid_to_fund(inp),
        treasury_fund=inp.tfr_treasury_fund,
        public=public,
    )
    extra = tfr.additional_ivs
    if extra is None or isinstance(inp.contract_type, Apprentice):
        return accrual
    ivs_base = _ivs_employer_base(breakdown)
    deduction = min(quota, money(ivs_base * extra.rate))
    return replace(accrual, ivs_base=ivs_base, ivs_rate=extra.rate, deduction=deduction)
