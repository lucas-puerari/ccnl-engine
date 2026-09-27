"""Contributions to a complementary pension fund of the CCNL.

Rules, D.Lgs. 252/2005 unless stated:

- the fund is financed by the worker, the employer and the TFR (art. 8
  c. 1); the CCNL sets the rates (art. 8 c. 2).  The bundle stores them as
  a fraction of the INPS contribution base
  (:class:`~ccnl_engine.contract.domain.compensation.EmployerFund`);
- the employee and employer contributions are deductible from the income
  up to an annual cap (art. 8 c. 4; TUIR art. 10 c. 1 lett. e-bis): the
  employee part withheld and the employer part within the cap do not form
  employment income (TUIR art. 51 c. 2 lett. h), the employer part beyond
  it does.  The TFR paid to the fund does not count towards the cap;
- the employer contributions, the TFR excluded, bear the INPS solidarity
  contribution (art. 16 c. 1; art. 9-bis D.L. 103/1991, conv. L.
  166/1991) and stay outside the INPS contribution base.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.domain.pension_fund import PENSION_FEATURE
from ccnl_engine.payroll.domain.rounding import money
from ccnl_engine.shared.domain.errors import InvalidInputError

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.contract.domain.category import WorkerCategory
    from ccnl_engine.contract.domain.compensation import EmployerFund
    from ccnl_engine.contract.domain.identity import CCNL
    from ccnl_engine.contract.domain.validity import TimeSeries, ValidityPeriod
    from ccnl_engine.payroll.domain.pension_fund import PensionFundEnrolment
    from ccnl_engine.tax.domain.pension_rules import ComplementaryPensionRules

_ZERO = Decimal(0)

#: Catalog feature of the pension fund contributions.
CAPABILITY = "pension_fund_contribution"

#: Reason code of a run whose worker is not enrolled in a fund of the CCNL.
NOT_ENROLLED = "not_enrolled"


@dataclass(frozen=True)
class PensionFundTerms:
    """Rates of the fund the worker is enrolled in, on the competence date.

    Attributes:
        fund: The fund of the CCNL.
        rate_period: Period of the employer rate in force.
        employer_rate: Employer rate on the INPS contribution base.
        employee_rate: Employee rate the worker chose.
        employee_min_rate: Minimum employee rate of the CCNL, ``None`` when
            the bundle records none.
        tfr_to_fund: Whether the TFR accrued is paid to the fund.
        rules: Deduction cap and solidarity rate of the tax year.
    """

    fund: EmployerFund
    rate_period: ValidityPeriod
    employer_rate: Decimal
    employee_rate: Decimal
    employee_min_rate: Decimal | None
    tfr_to_fund: bool
    rules: ComplementaryPensionRules


@dataclass(frozen=True)
class PensionContribution:
    """Contributions of one run to the fund.

    Attributes:
        terms: Rates they were computed with.
        base: INPS contribution base of the run.
        employer: Employer contribution.
        employee: Employee contribution, withheld from the pay.
        solidarity: INPS solidarity contribution on ``employer``.
        deductible: Part of ``employer + employee`` deducted from the
            taxable income of the run, within the cap left.
    """

    terms: PensionFundTerms
    base: Decimal
    employer: Decimal
    employee: Decimal
    solidarity: Decimal
    deductible: Decimal

    @property
    def taxable_adjustment(self) -> Decimal:
        """Change of the taxable income of the run due to the fund.

        The employer part enters the income and the deductible part leaves
        it: within the cap the change is minus the employee part.
        """
        return self.employer - self.deductible


def _fund_of(ccnl: CCNL, code: str) -> EmployerFund:
    """Return the fund ``code`` of ``ccnl``.

    Returns:
        The fund whose code is ``code``.

    Raises:
        InvalidInputError: When the CCNL has no fund with that code.
    """
    funds = ccnl.parameters.employer_funds
    for fund in funds:
        if fund.code == code:
            return fund
    known = [f.code for f in funds]
    msg = (
        f"pension fund {code!r} is not a fund of CCNL {ccnl.meta.ccnl_id}; "
        f"its funds are {known}"
    )
    raise InvalidInputError(msg, feature=PENSION_FEATURE)


def _in_force(
    series: TimeSeries | None, day: date
) -> tuple[ValidityPeriod, Decimal] | None:
    """Return the period of ``series`` in force on ``day`` with its value.

    Returns:
        ``None`` without a series, before it starts or on a gap.
    """
    period = None if series is None else series.period_at(day)
    if period is None or period.value is None:
        return None
    return period, period.value


def _check_category(fund: EmployerFund, category: WorkerCategory | None) -> None:
    """Reject a worker outside the categories the fund covers.

    Raises:
        InvalidInputError: When the fund is restricted and the category is
            unknown or not among those it covers.
    """
    allowed = fund.applies_to_categories
    if allowed is None or category in allowed:
        return
    msg = (
        f"pension fund {fund.code} covers the categories "
        f"{[c.value for c in allowed]}; the worker category is "
        f"{None if category is None else category.value!r}"
    )
    raise InvalidInputError(msg, feature=PENSION_FEATURE)


def resolve_terms(
    ccnl: CCNL,
    enrolment: PensionFundEnrolment,
    category: WorkerCategory | None,
    day: date,
    rules: ComplementaryPensionRules | None,
) -> PensionFundTerms:
    """Return the rates of the enrolment on ``day``.

    Returns:
        The terms of the fund for the run.

    Raises:
        InvalidInputError: When the fund is not in the CCNL, excludes the
            worker category or has no rate on ``day``, when the employee
            rate is below the CCNL minimum, or when the tax year has no
            complementary pension rules.
    """
    fund = _fund_of(ccnl, enrolment.fund_code)
    _check_category(fund, category)
    in_force = _in_force(fund.rate, day)
    if in_force is None:
        msg = f"pension fund {fund.code} has no employer rate on {day}"
        raise InvalidInputError(msg, feature=PENSION_FEATURE)
    minimum = _in_force(fund.employee_min_rate, day)
    min_rate = None if minimum is None else minimum[1]
    if min_rate is not None and enrolment.employee_rate < min_rate:
        msg = (
            f"employee_rate {enrolment.employee_rate} is below the minimum "
            f"{min_rate} of pension fund {fund.code}"
        )
        raise InvalidInputError(msg, feature=PENSION_FEATURE)
    if rules is None:
        msg = f"no complementary pension rules for the tax year of {day}"
        raise InvalidInputError(msg, feature=PENSION_FEATURE)
    return PensionFundTerms(
        fund=fund,
        rate_period=in_force[0],
        employer_rate=in_force[1],
        employee_rate=enrolment.employee_rate,
        employee_min_rate=min_rate,
        tfr_to_fund=enrolment.tfr_to_fund,
        rules=rules,
    )


def contribute(
    terms: PensionFundTerms, base: Decimal, deducted_ytd: Decimal
) -> PensionContribution:
    """Return the contributions of a run with INPS base ``base``.

    Args:
        terms: Rates of the enrolment.
        base: INPS contribution base of the run.
        deducted_ytd: Contributions already deducted this tax year.

    Returns:
        Employer, employee and solidarity contributions and the part
        deducted within the cap left.
    """
    employer = money(base * terms.employer_rate)
    employee = money(base * terms.employee_rate)
    headroom = max(_ZERO, terms.rules.deduction_cap - deducted_ytd)
    return PensionContribution(
        terms=terms,
        base=base,
        employer=employer,
        employee=employee,
        solidarity=money(employer * terms.rules.solidarity_rate),
        deductible=min(employer + employee, headroom),
    )


def upcoming_adjustment(
    terms: PensionFundTerms, upcoming_base: Decimal, deducted: Decimal
) -> Decimal:
    """Return the taxable change of the fund on the runs still to come.

    Args:
        terms: Rates of the enrolment.
        upcoming_base: INPS base projected on the runs still to come.
        deducted: Contributions deducted up to and including this run.

    Returns:
        The employer part less the part deductible within the cap left.
    """
    upcoming = contribute(terms, upcoming_base, deducted)
    return upcoming.taxable_adjustment
