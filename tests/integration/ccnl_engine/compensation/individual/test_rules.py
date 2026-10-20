"""Individual pay elements through a run of Commercio Confcommercio, 4th level.

Paga base 1,222.46 EUR from 1 March 2025, 1,257.46 from 1 November 2025,
1,292.46 from 1 November 2026 (Art. 23 as renewed on 22 March 2024).
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodInput,
    PeriodResult,
)
from ccnl_engine.agreement.validity.rules import TimeSeries, ValidityPeriod
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.compensation.individual.rules import (
    monthly_on,
    with_individual_elements,
)
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.inputs import (
    EmploymentPeriod,
    IndividualElement,
    NoPensionFund,
    Permanent,
    SeniorityFact,
    SenioritySource,
)
from ccnl_engine.results import AccountKind

_HIRED = date(2025, 1, 1)
_CCNL = "commercio-confcommercio"


def _run(*elements: IndividualElement, run: PayrollRun | None = None) -> PeriodResult:
    return PayrollEngine.bundled().calculate_period(
        PeriodInput(
            run=run or PayrollRun.regular(2026, 12),
            payment_date=date(2026, 12, 18),
            employment=Employment(
                ccnl_id=_CCNL,
                level_code="4",
                contract_type=Permanent(),
                employment_period=EmploymentPeriod(_HIRED, None),
                seniority=SeniorityFact.since(_HIRED, SenioritySource.EMPLOYER_RECORDS),
                pension_fund=NoPensionFund(),
                individual_elements=elements,
            ),
            employer=EmployerProfile(
                headcount=Headcount(60), provincial_pay_element=False
            ),
        )
    )


def _tfr(result: PeriodResult) -> Decimal:
    return sum(
        (
            e.amount
            for e in result.ledger_entries
            if e.account is AccountKind.TFR_ACCRUAL
        ),
        Decimal(0),
    )


def test_a_non_absorbable_element_stays_whole() -> None:
    """An assegno ad personam of 80 EUR is paid whole after the renewal."""
    result = _run(IndividualElement("ad_personam", Decimal(80)))

    items = [i.amount for i in result.pay_items if "ad_personam" in i.item_id]
    assert items == [Decimal("80.00")]
    (decision,) = [
        d for d in result.decisions if d.reason_code.startswith("individual")
    ]
    assert decision.reason_code == "individual_element_paid"
    assert "as_of" not in decision.inputs


def test_an_element_out_of_the_extra_months() -> None:
    """``extra_months`` false: the tredicesima leaves it out."""
    plain = _run(run=PayrollRun.thirteenth(2026, 12))
    with_it = _run(
        IndividualElement("premio", Decimal(80), extra_months=False),
        run=PayrollRun.thirteenth(2026, 12),
    )

    assert with_it.period_gross == plain.period_gross


def test_an_element_out_of_the_tfr() -> None:
    """``tfr_relevant`` false: no TFR quota on it.

    The additional 0.50% IVS on its INPS base still comes off the TFR (L.
    297/1982 art. 3 c. 15-16).
    """
    plain = _run()
    with_it = _run(IndividualElement("premio", Decimal(80), tfr_relevant=False))

    assert with_it.period_gross - plain.period_gross == Decimal(80)
    assert _tfr(plain) - _tfr(with_it) == Decimal("0.40")


def test_an_increase_larger_than_the_element_absorbs_it_whole() -> None:
    """Stated on 1 January 2025, 30 EUR: the 70 EUR of increases leave zero."""
    element = IndividualElement(
        "superminimo", Decimal(30), absorbable=True, as_of=date(2025, 1, 1)
    )
    result = _run(element)

    (decision,) = [
        d for d in result.decisions if d.reason_code.startswith("individual")
    ]
    assert decision.reason_code == "individual_element_absorbed"
    assert decision.amount == Decimal(0)


def test_a_cut_of_the_minimo_does_not_raise_the_element() -> None:
    """A lower minimo on the run than on ``as_of`` leaves the stated amount."""
    level = load_ccnl(_CCNL).level_by_code("4")
    cut = level.model_copy(
        update={
            "base_salary": TimeSeries(
                periods=(
                    ValidityPeriod(
                        valid_from=date(2025, 1, 1),
                        valid_until=date(2026, 1, 1),
                        value=Decimal(1300),
                    ),
                    ValidityPeriod(
                        valid_from=date(2026, 1, 1),
                        valid_until=None,
                        value=Decimal(1200),
                    ),
                )
            )
        }
    )
    element = IndividualElement(
        "superminimo", Decimal(100), absorbable=True, as_of=date(2025, 6, 1)
    )

    assert monthly_on(element, cut, date(2026, 6, 1)) == Decimal(100)


def test_an_as_of_before_the_tables_is_rejected() -> None:
    """The level has no minimo in 1990 to absorb from."""
    element = IndividualElement(
        "superminimo", Decimal(100), absorbable=True, as_of=date(1990, 1, 1)
    )

    with pytest.raises(InvalidInputError, match="no minimo"):
        _run(element)


def test_no_elements_or_another_level_leave_the_ccnl_as_it_is() -> None:
    """Only the level of the run takes the elements."""
    ccnl = load_ccnl(_CCNL)
    element = IndividualElement("ad_personam", Decimal(10))

    assert with_individual_elements(ccnl, "4", (), date(2026, 6, 1)) is ccnl
    changed = with_individual_elements(ccnl, "4", (element,), date(2026, 6, 1))
    assert changed.level_by_code("5") == ccnl.level_by_code("5")
    codes = [a.code for a in changed.level_by_code("4").fixed_allowances]
    assert codes[-1] == "ad_personam"
