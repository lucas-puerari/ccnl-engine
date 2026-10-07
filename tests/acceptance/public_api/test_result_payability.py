"""A result is payable only when every amount it exposes can be paid.

``result.is_payable`` is the one signal an integration reads to pay an
amount, and ``result.blockers`` says why not.  A result with an unknown
fact, an incomplete coverage or a known wrong amount must not be payable,
and an unknown fact must be named by its own blocker, not hidden behind an
unrelated one.  The cases the engine does not meet yet are strict ``xfail``
pinned to the assertion they break today.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from ccnl_engine import (
    CompetenceYearPlan,
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodFacts,
    PeriodInput,
    PeriodResult,
)
from ccnl_engine.events import BonusEvent
from ccnl_engine.inputs import (
    ContributableHours,
    EmploymentPeriod,
    FamilyComposition,
    TfrFundBalance,
    WeeklyHours,
    WorkerCategory,
)
from ccnl_engine.results import BlockerCode, CalculationStatus
from tests.fixtures.opening_state import fresh_tax_year
from tests.fixtures.residence import resident
from tests.fixtures.seniority import new_hire

_ENGINE = PayrollEngine.bundled()
_EMPLOYER = EmployerProfile(headcount=Headcount(50))
_METALMECCANICO = "metalmeccanico-federmeccanica.json"
_POSTAL_FISE = "servizi-postali-appalto-fise.json"
_MILAN_NO_DEPENDANT = PeriodFacts(
    regione="IT-25", comune_belfiore="F205", family_composition=FamilyComposition()
)


def _january(employment: Employment, facts: PeriodFacts | None = None) -> PeriodResult:
    """Return the January 2026 run, opening a tax year with nothing carried.

    Returns:
        The run, with no other employment of the worker in 2026.
    """
    return _ENGINE.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(2026, 1),
            payment_date=date(2026, 1, 27),
            employment=employment,
            employer=_EMPLOYER,
            facts=facts or PeriodFacts(),
            opening_state=fresh_tax_year(2026),
        )
    )


def _blocker_keys(result: PeriodResult) -> set[tuple[BlockerCode, str | None, str]]:
    return {(b.code, b.feature, b.detail) for b in result.blockers}


def test_incomplete_coverage_is_not_payable() -> None:
    """Metalmeccanico C3, last month of an employment ending on 30 January.

    The final payslip must settle the residual leave, a capability the
    engine does not compute: it applies to this run, so the report has an
    ``unsupported`` gap and the result is not payable.  So must it revalue
    the TFR fund at 31 December 2025 for January (art. 2120 c. 5 c.c.),
    which the engine reports as not computed: an ``unresolved`` gap.
    ``base_salary`` and ``somma_esente`` come from ``assumed`` rules: each
    is a blocker too.  January is the only payment of the employment, so
    the year's income is one month of pay and the somma esente is due on an
    assumed income.  The worker resides in Alghero, so the surtaxes leave no
    gap of their own.
    """
    period = EmploymentPeriod(started_on=date(2020, 1, 1), ended_on=date(2026, 1, 30))
    result = _january(
        Employment(
            ccnl_slug=_METALMECCANICO,
            level_code="C3",
            employment_period=period,
            seniority=new_hire(),
            tfr_fund=TfrFundBalance(2025, Decimal("8000.00")),
            tfr_treasury_fund=False,
        ),
        resident(),
    )

    gaps = {gap.feature: gap.kind for gap in result.capability_report.gaps}
    blocked = {
        b.feature
        for b in result.blockers
        if b.code is BlockerCode.CAPABILITY_NOT_COMPUTED
    }
    assert [i.code for i in result.issues] == ["somma_esente_income_unknown"]
    assert result.is_payable is False
    assert gaps == {
        "termination_residual_leave": "unsupported",
        "tfr_revaluation": "unresolved",
    }
    assert blocked == set(gaps)
    assert {
        (BlockerCode.RULE_SOURCE_WEAK, "base_salary", "assumed"),
        (BlockerCode.RULE_SOURCE_WEAK, "somma_esente", "assumed"),
    } <= _blocker_keys(result)


def test_ordinary_month_has_no_coverage_gap() -> None:
    """Metalmeccanico C3, January 2026, an ordinary month.

    No unsupported capability applies and the residence and the family are
    stated: the coverage is complete and no coverage blocker hides the
    evidence blockers that remain.
    """
    result = _january(
        Employment(ccnl_slug=_METALMECCANICO, level_code="C3", seniority=new_hire()),
        _MILAN_NO_DEPENDANT,
    )

    assert result.capability_report.gaps == ()
    assert result.assurance.coverage == "complete"
    assert not any(
        b.code is BlockerCode.CAPABILITY_NOT_COMPUTED for b in result.blockers
    )
    assert (BlockerCode.RULE_SOURCE_WEAK, "somma_esente", "assumed") in (
        _blocker_keys(result)
    )


def test_unknown_ivs_ceiling_eligibility_is_a_missing_fact() -> None:
    """A 200,000 EUR bonus crosses the 2026 IVS massimale of 122,295 EUR.

    Whether the massimale applies depends on the first enrolment date
    (L. 335/1995 art. 2 c. 18): it is a fact, not a default.  Without the
    contribution history neither branch is the answer: the eligibility
    decision is incomplete and the missing fact is named by its own
    blocker.  The result is already not payable for unrelated gaps, so the
    test asserts the blocker of its own fact.
    """
    employment = Employment(ccnl_slug=_METALMECCANICO, level_code="C3")
    bonus = BonusEvent(event_date=date(2026, 1, 15), amount=Decimal(200_000))

    result = _january(employment, PeriodFacts(events=(bonus,)))

    (decision,) = [
        d for d in result.decisions if d.capability == "ivs_ceiling_eligibility"
    ]
    assert decision.reason_code == "required_fact_missing"
    assert decision.amount is None
    assert (BlockerCode.MISSING_FACT, None, "contribution_history") in (
        _blocker_keys(result)
    )
    assert result.assurance.calculation is CalculationStatus.INCOMPLETE
    assert result.is_payable is False


def test_unknown_seniority_is_a_missing_fact() -> None:
    """Servizi postali appalto FISE, level 2, operaio, seniority not given.

    The CCNL grants operai one increment of 56.66 EUR after 24 months
    (Art. 35A): without the recognised seniority the increment is
    undetermined.  The seniority decision says so and carries no amount,
    the missing fact is named by its own blocker and the result is not
    payable.  The amounts shown leave the increment out: 1,650.74 base +
    63.33 + 10.33 = 1,724.40.
    """
    employment = Employment(
        ccnl_slug=_POSTAL_FISE,
        level_code="2",
        category=WorkerCategory.OPERAIO,
        seniority=None,
    )

    result = _january(employment)

    (decision,) = [d for d in result.decisions if d.capability == "seniority"]
    assert decision.reason_code == "required_fact_missing"
    assert decision.amount is None
    assert (BlockerCode.MISSING_FACT, None, "seniority") in _blocker_keys(result)
    assert result.assurance.calculation is CalculationStatus.INCOMPLETE
    assert result.period_gross == Decimal("1724.40")
    assert result.is_payable is False


def _march(started_on: date) -> PeriodResult:
    """Return the March 2026 run of a C3 hired on ``started_on``.

    Returns:
        The regular run of March 2026.
    """
    employment = Employment(
        ccnl_slug=_METALMECCANICO,
        level_code="C3",
        employment_period=EmploymentPeriod(started_on=started_on),
    )
    year = _ENGINE.calculate_competence_year(
        CompetenceYearPlan(year=2026, employment=employment, employer=_EMPLOYER)
    )
    (march,) = [
        result
        for result in year.period_results
        if result.run == PayrollRun.regular(2026, 3)
    ]
    return march


def test_partial_hire_month_does_not_expose_full_month_pay() -> None:
    """Metalmeccanico C3 hired on 15 March 2026 against one hired on 1 March.

    Seventeen of the thirty-one days of March cannot be paid as a full
    month.  The CCNL daily quota is one twenty-sixth: 15 March 2026 is a
    Sunday, 16-21, 23-28, 30 and 31 March are 14 payable days, so the run
    pays 2,158.26 x 14 / 26 = 1,162.14.
    """
    full_month = _march(date(2026, 3, 1))
    partial_month = _march(date(2026, 3, 15))

    assert full_month.period_gross == Decimal("2158.26")
    assert partial_month.period_gross == Decimal("1162.14")


def test_unknown_surtax_table_is_not_an_amount() -> None:
    """A Belfiore code without a 2026 table: the surtax is undetermined.

    The decision carries no amount rather than zero, and the result is not
    payable for that capability, whatever the other blockers.
    """
    employment = Employment(ccnl_slug=_METALMECCANICO, level_code="C3")

    result = _january(employment, PeriodFacts(comune_belfiore="Z999"))

    (decision,) = [
        d for d in result.decisions if d.capability == "addizionale_comunale"
    ]
    assert decision.amount is None
    assert (
        BlockerCode.CALCULATION_ISSUE,
        "addizionale_comunale",
        decision.reason_code,
    ) in _blocker_keys(result)
    assert result.is_payable is False


def test_unknown_family_is_not_an_empty_family() -> None:
    """Metalmeccanico C3, January 2026, resident in Milan.

    Left unknown, the family cannot rule out the art. 12 TUIR deductions:
    the result names the requirement; an empty ``FamilyComposition``
    states that there is no dependant and resolves it.
    """
    employment = Employment(
        ccnl_slug=_METALMECCANICO, level_code="C3", seniority=new_hire()
    )
    resident = PeriodFacts(regione="IT-25", comune_belfiore="F205")
    unresolved = (
        BlockerCode.REQUIREMENT_UNRESOLVED,
        "family_deductions",
        "facts.family_composition",
    )

    assert unresolved in _blocker_keys(_january(employment, resident))
    assert unresolved not in _blocker_keys(_january(employment, _MILAN_NO_DEPENDANT))


def test_household_employer_needs_no_residence() -> None:
    """Lavoro domestico B, January 2026, residence and family left unknown.

    A household employer is not a withholding agent (art. 23 c. 1 DPR
    600/1973): it decides that no surtax and no deduction is due, so the
    unknown residence and family leave no requirement unresolved.
    """
    result = _ENGINE.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(2026, 1),
            payment_date=date(2026, 1, 28),
            employment=Employment(
                ccnl_slug="lavoro-domestico-non-convivente.json",
                level_code="B",
                seniority=new_hire(),
                weekly_hours=WeeklyHours(25),
            ),
            employer=EmployerProfile(headcount=Headcount(1)),
            facts=PeriodFacts(contributable_hours=ContributableHours(Decimal(108))),
        )
    )

    assert result.capability_report.unresolved == ()
    assert BlockerCode.REQUIREMENT_UNRESOLVED not in {b.code for b in result.blockers}
