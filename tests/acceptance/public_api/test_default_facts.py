"""A default left in a public input is not the fact it stands for.

Concia D2, June 2026, every other fact explicit
(:mod:`tests.fixtures.explicit_facts`): its only blocker is
``rule_source_weak somma_esente``, so the blockers a field adds or removes
are visible.  Two properties of the payability contract
(:mod:`tests.acceptance.public_api.test_result_payability`): a default that
selects a monetary branch adds a blocker the explicit value does not have,
and the true value of a fact never has more blockers than the default it
replaces, otherwise the false default is the one path that looks payable.
The residence left unknown is checked by
``test_unknown_residence_is_not_no_surtax`` of the legal scenarios.  None
of the properties below holds today: each is a strict xfail on its
assertion.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine import Employment, PayrollEngine, PayrollRun, PeriodFacts, PeriodResult
from ccnl_engine.events import AbsenceEvent
from ccnl_engine.inputs import (
    Dependent,
    DependentRelationship,
    EmploymentPeriod,
    FamilyComposition,
    PensionFundEnrolment,
    PeriodState,
    WeeklyHours,
)
from ccnl_engine.results import BlockerCode
from tests.fixtures.explicit_facts import (
    CONCIA_D2,
    FACTS,
    competence_year,
    regular_run,
)

_ENGINE = PayrollEngine.bundled()


def _blocker_set(result: PeriodResult) -> set[tuple[BlockerCode, str | None]]:
    return {(b.code, b.feature) for b in result.blockers}


def _june_with(
    employment: Employment = CONCIA_D2,
    facts: PeriodFacts = FACTS,
    opening_state: PeriodState | None = None,
) -> PeriodResult:
    request = regular_run(
        employment=employment, facts=facts, opening_state=opening_state
    )
    return _ENGINE.calculate_period(request)


def _thirteenth(suspends_accrual: bool) -> PeriodResult:
    """Return the tredicesima of a Concia D2 on unpaid leave all March.

    Returns:
        The tredicesima run of the 2026 competence year.
    """
    leave = AbsenceEvent(
        date(2026, 3, 2),
        Decimal(173),
        Decimal("11.86"),
        end_date=date(2026, 3, 31),
        suspends_accrual=suspends_accrual,
    )
    year = _ENGINE.calculate_competence_year(
        competence_year(periods={3: replace(FACTS, events=(leave,))})
    )
    return next(r for r in year.period_results if r.run == _THIRTEENTH)


_THIRTEENTH = PayrollRun.thirteenth(2026, 12)
_ASCENDANT = Dependent(DependentRelationship.ASCENDANT)
_SPOUSE = Dependent(DependentRelationship.SPOUSE)
_TABACCO_3A = replace(CONCIA_D2, ccnl_slug="tabacco-apti.json", level_code="3A")
_INVERSION = (
    "declaring the true fact adds a blocker the default does not have: part "
    "time and a hire on 15 June (somma_esente_income_assumed), enrolment in "
    "the CCNL fund ALIFOND (pension_fund_contribution not computed), unpaid "
    "leave that suspends accrual (tredicesima issue); the default full time, "
    "full month, no fund and full accrual look more payable than the truth"
)


class TestDefaultIsNotAFact:
    """A field left to its default must not pass as the fact it stands for."""

    def test_explicit_scenario_has_one_blocker(self) -> None:
        """The premise: with every fact given, only the somma esente blocks."""
        assert _blocker_set(_june_with()) == {
            (BlockerCode.RULE_SOURCE_WEAK, "somma_esente")
        }

    @pytest.mark.xfail(
        strict=True,
        raises=AssertionError,
        reason=(
            "the default opening state is a zero state, so a June run of an "
            "employment open since 1 January restarts the progressive totals "
            "from zero without a blocker; the withholding of art. 23 DPR "
            "600/1973 and the INPS ceilings of L. 335/1995 art. 2 c. 18 are "
            "computed on the year's totals"
        ),
    )
    def test_missing_opening_state_mid_year_is_not_a_zero_state(self) -> None:
        """June without the state closed by May adds a blocker."""
        year = _ENGINE.calculate_competence_year(competence_year())
        may = year.period_results[4].closing_state
        default = _blocker_set(_june_with())
        chained = _blocker_set(_june_with(opening_state=may))
        assert default - chained

    @pytest.mark.xfail(
        strict=True,
        raises=AssertionError,
        reason=(
            "Dependent defaults cohabiting and residency_eligibility to True "
            "and own_income to 0, so an undeclared condition grants the "
            "art. 12 TUIR deduction (c. 1 lett. d, c. 2, c. 2-bis) without a "
            "blocker"
        ),
    )
    @pytest.mark.parametrize(
        ("dependent", "explicit"),
        [
            pytest.param(
                _ASCENDANT, replace(_ASCENDANT, cohabiting=True), id="cohabiting"
            ),
            pytest.param(
                _SPOUSE,
                replace(_SPOUSE, residency_eligibility=True),
                id="residency_eligibility",
            ),
            pytest.param(
                _SPOUSE, replace(_SPOUSE, own_income=Decimal(0)), id="own_income"
            ),
        ],
    )
    def test_undeclared_dependent_condition_is_not_met(
        self, dependent: Dependent, explicit: Dependent
    ) -> None:
        """A dependant whose condition is not declared adds a blocker."""

        def family(member: Dependent) -> PeriodResult:
            composition = FamilyComposition(dependents=(member,))
            return _june_with(facts=replace(FACTS, family_composition=composition))

        assert _blocker_set(family(dependent)) - _blocker_set(family(explicit))

    @pytest.mark.xfail(
        strict=True,
        raises=AssertionError,
        reason=_INVERSION,
    )
    @pytest.mark.parametrize(
        ("true", "default"),
        [
            pytest.param(
                replace(CONCIA_D2, weekly_hours=WeeklyHours(20)),
                replace(CONCIA_D2, weekly_hours=None, full_time_weekly_hours=None),
                id="part_time",
            ),
            pytest.param(
                replace(
                    CONCIA_D2, employment_period=EmploymentPeriod(date(2026, 6, 15))
                ),
                replace(CONCIA_D2, employment_period=None),
                id="hire_mid_month",
            ),
            pytest.param(
                replace(
                    _TABACCO_3A,
                    pension_fund=PensionFundEnrolment(
                        "ALIFOND", Decimal("0.01"), tfr_to_fund=False
                    ),
                ),
                _TABACCO_3A,
                id="pension_fund",
            ),
        ],
    )
    def test_true_employment_fact_has_no_more_blockers(
        self, true: Employment, default: Employment
    ) -> None:
        """The June run with the true fact has at most the default's blockers."""
        blockers = _blocker_set(_june_with(employment=true))
        assert len(blockers) <= len(_blocker_set(_june_with(employment=default)))

    @pytest.mark.xfail(strict=True, raises=AssertionError, reason=_INVERSION)
    def test_leave_suspending_accrual_has_no_more_blockers(self) -> None:
        """The tredicesima after a leave that suspends accrual blocks no more."""
        blockers = _blocker_set(_thirteenth(suspends_accrual=True))
        assert len(blockers) <= len(_blocker_set(_thirteenth(suspends_accrual=False)))
