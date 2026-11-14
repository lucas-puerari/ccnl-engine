"""The conguaglio takes in an earlier employment of the year (art. 23 c. 4).

Chimica D1, hired 1 April 2026, for a worker employed elsewhere from 1
January to 31 March 2026: the CU of that employment certifies 3000.00 of
taxable income and 2000.00 of IRPEF withheld.  The same year without the
request keeps the income in ``other_employment_income``.  Both totals stay
in the first bracket, so the gross tax of the conguaglio grows by
3000.00 x 23% = 690.00; the work deduction counts the 365 days of the two
employments; the IRPEF the other payer withheld counts as withheld.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine import (
    CompetenceYearPlan,
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PeriodFacts,
    PeriodResult,
)
from ccnl_engine.employment.spell.models import EmploymentSpell
from ccnl_engine.errors import InvalidInputError
from ccnl_engine.inputs import (
    CurrentYearTaxFacts,
    EmploymentPeriod,
    EmploymentSector,
    FamilyComposition,
    IncomeEstimateQuality,
    NoPensionFund,
    Permanent,
    PriorYearTaxFacts,
    SeniorityFact,
    SenioritySource,
    WorkerCategory,
)
from ccnl_engine.irpef.prior.inputs import PriorEmployerIncome

_HIRED = date(2026, 4, 1)
_ENGINE = PayrollEngine.bundled()
_PRIOR = PriorEmployerIncome(
    spell=EmploymentSpell(date(2026, 1, 1), date(2026, 3, 31), fixed_term=False),
    taxable=Decimal(3000),
    irpef_withheld=Decimal(2000),
    trattamento_paid=Decimal(0),
    regional_surtax_withheld=Decimal(0),
    municipal_advance_withheld=Decimal(0),
    municipal_surtax_withheld=Decimal(0),
    somma_esente_paid=Decimal(0),
)


def _facts(prior: tuple[PriorEmployerIncome, ...]) -> CurrentYearTaxFacts:
    return CurrentYearTaxFacts(
        tax_year=2026,
        other_employment_income=Decimal(3000),
        other_employment_inps_base=Decimal(3000),
        other_income=Decimal(0),
        main_dwelling_income=Decimal(0),
        exempt_regime_income=Decimal(0),
        estimated_on=_HIRED,
        quality=IncomeEstimateQuality.DECLARED,
        prior_employers=prior,
    )


def _conguaglio(prior: tuple[PriorEmployerIncome, ...]) -> PeriodResult:
    year = _ENGINE.calculate_competence_year(
        CompetenceYearPlan(
            year=2026,
            employment=Employment(
                ccnl_id="chimica-farmaceutica-federchimica",
                level_code="D1",
                contract_type=Permanent(),
                category=WorkerCategory.IMPIEGATO,
                employment_period=EmploymentPeriod(_HIRED, None),
                seniority=SeniorityFact.since(_HIRED, SenioritySource.EMPLOYER_RECORDS),
                roles=frozenset(),
                sector=EmploymentSector.PRIVATE,
                pension_fund=NoPensionFund(),
                tfr_treasury_fund=True,
            ),
            employer=EmployerProfile(
                headcount=Headcount(60), provincial_pay_element=False
            ),
            prior_year=PriorYearTaxFacts(employment_income=Decimal(30000)),
            current_year=_facts(prior),
            default_facts=PeriodFacts(
                regione="IT-25",
                comune_belfiore="F205",
                family_composition=FamilyComposition(),
            ),
        )
    )
    return year.period_results[-1]


def _component(result: PeriodResult, name: str) -> Decimal:
    (item,) = (c for c in result.tax_computation.components if c.name == name)
    return item.amount


def test_the_conguaglio_taxes_the_earlier_income_with_this_one() -> None:
    """Gross tax +690.00, more deduction days, the other withholding counted."""
    taken, kept = _conguaglio((_PRIOR,)), _conguaglio(())

    assert _component(taken, "irpef_gross") - _component(
        kept, "irpef_gross"
    ) == Decimal("690.00")
    assert _component(taken, "work_deduction") > _component(kept, "work_deduction")
    assert taken.tax_computation.withholding_due < kept.tax_computation.withholding_due


def test_the_certified_income_must_be_in_the_other_employment_income() -> None:
    """The CU income is part of the income beyond this employment."""
    with pytest.raises(InvalidInputError) as error:
        CurrentYearTaxFacts(
            tax_year=2026,
            other_employment_income=Decimal(100),
            other_employment_inps_base=Decimal(0),
            other_income=Decimal(0),
            main_dwelling_income=Decimal(0),
            exempt_regime_income=Decimal(0),
            estimated_on=_HIRED,
            quality=IncomeEstimateQuality.DECLARED,
            prior_employers=(_PRIOR,),
        )
    assert error.value.field == "CurrentYearTaxFacts.prior_employers"


@pytest.mark.parametrize(
    "field",
    [
        "taxable",
        "irpef_withheld",
        "trattamento_paid",
        "regional_surtax_withheld",
        "municipal_advance_withheld",
        "municipal_surtax_withheld",
        "somma_esente_paid",
    ],
)
def test_a_negative_certified_amount_is_rejected(field: str) -> None:
    """Every CU amount is non-negative."""
    values = {
        "spell": _PRIOR.spell,
        "taxable": Decimal(1),
        "irpef_withheld": Decimal(1),
        "trattamento_paid": Decimal(1),
        "regional_surtax_withheld": Decimal(1),
        "municipal_advance_withheld": Decimal(1),
        "municipal_surtax_withheld": Decimal(1),
        "somma_esente_paid": Decimal(1),
    } | {field: Decimal(-1)}
    with pytest.raises(InvalidInputError) as error:
        PriorEmployerIncome(**values)  # type: ignore[arg-type]
    assert error.value.field == f"PriorEmployerIncome.{field}"


def test_the_trattamento_the_other_payer_paid_is_recovered() -> None:
    """100.00 paid and not due on the total: recovered in eight installments.

    D.L. 3/2020: a trattamento recovered above 60.00 is withheld in eight
    installments, 12.50 on the conguaglio; the year's account counts it.
    """
    paid = replace(_PRIOR, trattamento_paid=Decimal(100))
    result = _conguaglio((paid,))

    assert result.tax_computation.trattamento_integrativo == Decimal("-12.50")
    account = result.closing_state.cash.trattamento
    assert account.recognized == Decimal(100)
    assert account.recovered == Decimal("12.50")


def _balance(result: PeriodResult, component: str) -> Decimal | None:
    (decision,) = (
        d
        for d in result.decisions
        if d.reason_code == "deferred_to_installments"
        and d.inputs["component"] == component
    )
    return decision.amount


def test_the_surtax_of_the_total_less_what_the_other_payer_withheld() -> None:
    """Milano: 23080.00 of income; 30.00 and 10.00 withheld before (CU 546, 548).

    The regional 312.16 and municipal 184.64 of the total are left at
    282.16 and 174.64 for the installments.
    """
    withheld = replace(
        _PRIOR,
        regional_surtax_withheld=Decimal(30),
        municipal_surtax_withheld=Decimal(10),
    )
    taken, plain = _conguaglio((withheld,)), _conguaglio((_PRIOR,))

    assert _balance(plain, "regional_balance") == Decimal("312.16")
    assert _balance(taken, "regional_balance") == Decimal("282.16")
    assert _balance(plain, "municipal_balance") == Decimal("184.64")
    assert _balance(taken, "municipal_balance") == Decimal("174.64")


def test_the_somma_esente_the_other_payer_paid_is_recovered() -> None:
    """100.00 paid and not due on the total: recovered in ten installments.

    L. 207/2024 art. 1 c. 4: a somma esente recovered above 60.00 is
    withheld in ten installments, 10.00 on the conguaglio.
    """
    result = _conguaglio((replace(_PRIOR, somma_esente_paid=Decimal(100)),))

    account = result.closing_state.cash.somma_esente
    assert account.recognized == Decimal(100)
    assert account.recovered == Decimal("10.00")
    assert account.reason == "overpayment_recovery_opened"
