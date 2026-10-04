"""Art. 12 TUIR family deductions through the public API.

Every run is the tredicesima of Metalmeccanico C3 paid on 18 December 2026,
the last withholding run of the year, so the employment income of the year
is the opening taxable plus the tredicesima and nothing is projected:

    opening taxable = employment income - taxable of the tredicesima

The reddito complessivo adds the income of
:class:`~ccnl_engine.inputs.CurrentYearTaxFacts`.  Expected deductions are computed
by hand from the text quoted in
:mod:`tests.fixtures.legal_examples.family_2026`.
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
    PeriodFacts,
    PeriodInput,
    PeriodResult,
)
from ccnl_engine.inputs import (
    CurrentYearTaxFacts,
    Dependent,
    DependentRelationship,
    FamilyComposition,
    IncomeEstimateQuality,
    OpeningBalances,
    PeriodState,
)
from ccnl_engine.results import BlockerCode, CalculationDecision, CalculationStatus
from tests.fixtures.legal_examples.metalmeccanico_c3_2026 import (
    C3_MINIMUM_FROM_JUNE_2026,
    employee_taxable,
)
from tests.fixtures.seniority import new_hire
from tests.fixtures.withholding import paid_before

_D = Decimal
_ENGINE = PayrollEngine.bundled()
_RUN = PayrollRun.thirteenth(2026, 12)
_DAY = date(2026, 1, 15)
_SPOUSE = FamilyComposition(
    dependents=(Dependent(relationship=DependentRelationship.SPOUSE),)
)
_EMPLOYMENT = Employment(
    ccnl_slug="metalmeccanico-federmeccanica.json",
    level_code="C3",
    seniority=new_hire(),
)


def _facts(
    other_employment: str = "0",
    other: str = "0",
    main_dwelling: str = "0",
    quality: IncomeEstimateQuality = IncomeEstimateQuality.DECLARED,
    tax_year: int = 2026,
) -> CurrentYearTaxFacts:
    return CurrentYearTaxFacts(
        tax_year=tax_year,
        other_employment_income=_D(other_employment),
        other_income=_D(other),
        main_dwelling_income=_D(main_dwelling),
        estimated_on=_DAY,
        quality=quality,
    )


def _conguaglio(
    employment_income: Decimal,
    family: FamilyComposition,
    current_year: CurrentYearTaxFacts | None,
) -> PeriodResult:
    opening = PayrollEngine.import_opening_balances(
        OpeningBalances(
            tax_year=2026,
            payments=paid_before(_RUN, day=18),
            taxable=employment_income - employee_taxable(C3_MINIMUM_FROM_JUNE_2026),
        )
    )
    result = _ENGINE.calculate_period(
        PeriodInput(
            run=_RUN,
            payment_date=date(2026, 12, 18),
            employment=_EMPLOYMENT,
            employer=EmployerProfile(headcount=Headcount(50)),
            facts=PeriodFacts(family_composition=family),
            current_year=current_year,
            opening_state=opening,
        )
    )
    assert result.closing_state.cash.earnings.taxable == employment_income
    return result


def _family_decision(result: PeriodResult) -> CalculationDecision:
    (decision,) = [d for d in result.decisions if d.capability == "family_deductions"]
    return decision


def _missing_facts(result: PeriodResult) -> list[str]:
    return [b.detail for b in result.blockers if b.code is BlockerCode.MISSING_FACT]


class TestReddito:
    """The deductions read the reddito complessivo, not this job alone."""

    def test_other_employer_moves_the_band(self) -> None:
        """29,000 here + 1,000 elsewhere = 30,000: band 2), 690 + 20."""
        decision = _family_decision(
            _conguaglio(_D(29000), _SPOUSE, _facts(other_employment="1000"))
        )
        assert decision.amount == _D(710)
        assert decision.inputs["reddito_complessivo"] == _D(30000)
        assert decision.status is CalculationStatus.FINAL

    def test_same_job_alone_stays_flat(self) -> None:
        """29,000 is not above 29,000: 690, no increase."""
        decision = _family_decision(_conguaglio(_D(29000), _SPOUSE, _facts()))
        assert decision.amount == _D(690)

    @pytest.mark.parametrize(
        ("main_dwelling", "expected"),
        [
            # 29,000 + 6,000 - 300 = 34,700: band 2), 710
            ("300", "710"),
            # 29,000 + 6,000 - 299.99 = 34,700.01: band 3), 720
            ("299.99", "720"),
        ],
    )
    def test_non_employment_income_net_of_the_main_dwelling(
        self, main_dwelling: str, expected: str
    ) -> None:
        """Other income counts, the main dwelling does not (c. 4-bis)."""
        decision = _family_decision(
            _conguaglio(
                _D(29000), _SPOUSE, _facts(other="6000", main_dwelling=main_dwelling)
            )
        )
        assert decision.amount == _D(expected)


class TestMonthlyEntitlement:
    """Dependency and age are evaluated month by month (c. 3)."""

    def test_child_turning_21_in_may(self) -> None:
        """R 50,000: 950 x 0.4736 = 449.92 a year, May-December 299.95."""
        child = Dependent(
            relationship=DependentRelationship.CHILD, birth_date=date(2005, 5, 10)
        )
        decision = _family_decision(
            _conguaglio(_D(50000), FamilyComposition(dependents=(child,)), _facts())
        )
        assert decision.amount == _D("299.95")
        assert decision.inputs["months"] == "child:8"

    def test_child_turning_30_in_september(self) -> None:
        """R 50,000: January-September, 449.92 x 9 / 12 = 337.44."""
        child = Dependent(
            relationship=DependentRelationship.CHILD, birth_date=date(1996, 9, 20)
        )
        decision = _family_decision(
            _conguaglio(_D(50000), FamilyComposition(dependents=(child,)), _facts())
        )
        assert decision.amount == _D("337.44")

    def test_spouse_from_mid_june(self) -> None:
        """R 30,000: married on 15 June, 710 x 7 / 12 = 414.17."""
        spouse = Dependent(
            relationship=DependentRelationship.SPOUSE,
            dependent_from=date(2026, 6, 15),
        )
        decision = _family_decision(
            _conguaglio(_D(30000), FamilyComposition(dependents=(spouse,)), _facts())
        )
        assert decision.amount == _D("414.17")

    def test_ascendant_leaving_mid_year(self) -> None:
        """R 40,000: cohabiting until 10 April, 375 x 4 / 12 = 125.00."""
        parent = Dependent(
            relationship=DependentRelationship.ASCENDANT,
            dependent_until=date(2026, 4, 10),
        )
        decision = _family_decision(
            _conguaglio(_D(40000), FamilyComposition(dependents=(parent,)), _facts())
        )
        assert decision.amount == _D("125.00")


class TestUnknownIncome:
    """Missing income is a blocker, never an assumed zero."""

    def test_missing_facts_make_the_run_not_payable(self) -> None:
        """The decision has no amount and names the missing fact."""
        result = _conguaglio(_D(30000), _SPOUSE, None)
        decision = _family_decision(result)
        assert decision.status is CalculationStatus.PROVISIONAL
        assert decision.reason_code == "required_fact_missing"
        assert decision.amount is None
        assert decision.inputs["simulated_amount"] == _D(710)
        assert decision.inputs["reddito_complessivo"] == "undetermined"
        (issue,) = [i for i in result.issues if i.code == "family_income_unknown"]
        assert issue.fact == "current_year"
        assert "current_year" in _missing_facts(result)
        assert not result.is_payable
        assert result.assurance.calculation is CalculationStatus.INCOMPLETE
        # The simulation read the table: its ruleset and source stay listed.
        assert "tax/2026/family-deductions" in [r.id for r in result.rulesets]
        assert "family_deductions" in result.capability_report.rule_sources

    def test_facts_of_another_tax_year_are_not_used(self) -> None:
        """Facts of 2025 say nothing about the reddito complessivo of 2026."""
        result = _conguaglio(_D(30000), _SPOUSE, _facts(tax_year=2025))
        assert _family_decision(result).amount is None
        assert "current_year" in _missing_facts(result)

    def test_no_entitled_dependent_needs_no_income(self) -> None:
        """A child under 21 gives no deduction whatever the income."""
        child = Dependent(
            relationship=DependentRelationship.CHILD, birth_date=date(2012, 3, 1)
        )
        result = _conguaglio(_D(30000), FamilyComposition(dependents=(child,)), None)
        decision = _family_decision(result)
        assert decision.status is CalculationStatus.FINAL
        assert decision.reason_code == "no_deduction_due"
        assert decision.amount == _D(0)
        assert "current_year" not in _missing_facts(result)

    def test_income_past_every_phase_out_needs_no_more_income(self) -> None:
        """80,000.01 here: the spouse deduction is zero whatever comes on top."""
        result = _conguaglio(_D("80000.01"), _SPOUSE, None)
        decision = _family_decision(result)
        assert decision.status is CalculationStatus.FINAL
        assert decision.amount == _D(0)
        assert "current_year" not in _missing_facts(result)

    def test_income_just_inside_the_phase_out_needs_the_facts(self) -> None:
        """At 79,000 the spouse still has 690 x 0.025 = 17.25: facts needed."""
        result = _conguaglio(_D(79000), _SPOUSE, None)
        assert _family_decision(result).inputs["simulated_amount"] == _D("17.25")
        assert "current_year" in _missing_facts(result)


class TestEstimateQuality:
    """An estimated income is enough during the year, not for the conguaglio."""

    def test_estimate_on_the_conguaglio_is_provisional(self) -> None:
        """The conguaglio settles the year on final figures."""
        result = _conguaglio(
            _D(30000), _SPOUSE, _facts(quality=IncomeEstimateQuality.ESTIMATED)
        )
        decision = _family_decision(result)
        assert decision.status is CalculationStatus.PROVISIONAL
        assert decision.reason_code == "estimated_income_at_conguaglio"
        assert decision.amount == _D(710)
        assert decision.inputs["estimate_quality"] == "estimated"
        assert any(
            b.code is BlockerCode.CALCULATION_ISSUE and b.feature == "family_deductions"
            for b in result.blockers
        )

    def test_estimate_during_the_year_is_final(self) -> None:
        """A June run projects the year; the estimate is what it can know."""
        result = _ENGINE.calculate_period(
            PeriodInput(
                run=PayrollRun.regular(2026, 6),
                payment_date=date(2026, 6, 27),
                employment=_EMPLOYMENT,
                employer=EmployerProfile(headcount=Headcount(50)),
                facts=PeriodFacts(family_composition=_SPOUSE),
                current_year=_facts(quality=IncomeEstimateQuality.ESTIMATED),
                opening_state=PeriodState.zero(),
            )
        )
        decision = _family_decision(result)
        assert decision.status is CalculationStatus.FINAL
        assert decision.inputs["estimated_on"] == "2026-01-15"
