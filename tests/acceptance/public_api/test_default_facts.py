"""A default left in a public input is not the fact it stands for.

Concia D2, June 2026, every other fact explicit
(:mod:`tests.fixtures.explicit_facts`) and opened with the state May closed:
its only blocker is ``rule_source_weak somma_esente``, so the blockers a
field adds or removes are visible.  Two properties of the payability
contract (:mod:`tests.acceptance.public_api.test_result_payability`): a
default that selects a monetary branch adds a blocker the explicit value
does not have, and the true value of a fact never has more blockers than
the default it replaces, otherwise the false default is the one path that
looks payable.  The residence left unknown is checked by
``test_unknown_residence_is_not_no_surtax`` of the legal scenarios.  The
properties that do not hold yet are strict xfails on their assertion.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal
from functools import cache
from typing import Any

import pytest

from ccnl_engine import (
    Employment,
    PayrollEngine,
    PayrollRun,
    PeriodFacts,
    PeriodInput,
    PeriodResult,
)
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
from tests.fixtures.dependents import declared_dependent
from tests.fixtures.explicit_facts import (
    CONCIA_D2,
    FACTS,
    competence_year,
    regular_run,
)

_ENGINE = PayrollEngine.bundled()


def _blocker_set(result: PeriodResult) -> set[tuple[BlockerCode, str | None]]:
    return {(b.code, b.feature) for b in result.blockers}


@cache
def _may_closing_state() -> PeriodState:
    """Return the state the May run of the explicit year closes with.

    Returns:
        The closing state of May 2026 of the Concia D2 hired on 1 January.
    """
    year = _ENGINE.calculate_competence_year(competence_year())
    return year.period_results[4].closing_state


def _june_with(
    employment: Employment = CONCIA_D2,
    facts: PeriodFacts = FACTS,
    opening_state: PeriodState | None = None,
) -> PeriodResult:
    """Return the June run opened with the history of its employment.

    ``opening_state`` left ``None`` is that history: the zero state for a
    hire in June, the state May closed otherwise.

    Returns:
        The June 2026 run.
    """
    if opening_state is None:
        period = employment.employment_period
        hired_in_june = period is not None and period.started_on.month == 6
        opening_state = PeriodState.zero() if hired_in_june else _may_closing_state()
    request = regular_run(
        employment=employment, facts=facts, opening_state=opening_state
    )
    return _ENGINE.calculate_period(request)


def _family_blockers(member: Dependent) -> set[tuple[BlockerCode, str | None]]:
    """Return the blockers of the June run with one dependant.

    Returns:
        The code and detail of every blocker of the run.
    """
    composition = FamilyComposition(dependents=(member,))
    result = _june_with(facts=replace(FACTS, family_composition=composition))
    return {(b.code, b.detail) for b in result.blockers}


def _unknown(dependent: Dependent, fact: str) -> Dependent:
    """Return ``dependent`` with the condition ``fact`` left unknown.

    Returns:
        A copy with ``fact`` set to ``None``.
    """
    fields: dict[str, Any] = {fact: None}
    return replace(dependent, **fields)


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
_ASCENDANT = declared_dependent(DependentRelationship.ASCENDANT)
_SPOUSE = declared_dependent(DependentRelationship.SPOUSE)
_CHILD = declared_dependent(DependentRelationship.CHILD, birth_date=date(2004, 3, 1))
_YOUNG_CHILD = declared_dependent(
    DependentRelationship.CHILD, birth_date=date(2015, 3, 1)
)
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

    def test_missing_opening_state_mid_year_is_not_a_zero_state(self) -> None:
        """June opened with the zero state adds a missing opening_state.

        The employment is open since 1 January: the withholding of art. 23
        DPR 600/1973 and the INPS massimale of L. 335/1995 art. 2 c. 18 are
        computed on the totals of the year, which the zero state drops.
        """
        default = _june_with(opening_state=PeriodState.zero())

        assert _blocker_set(default) - _blocker_set(_june_with()) == {
            (BlockerCode.MISSING_FACT, None)
        }
        assert {b.detail for b in default.blockers} >= {"opening_state"}
        assert not default.closing_state.history_known

    def test_unknown_base_of_other_employments_is_not_zero(self) -> None:
        """January without the current-year facts adds a missing other_employers.

        The January run of a hire on 1 January opens with the zero state, a
        fact; the INPS base of other employments of 2026 is not stated, and
        it counts toward the massimale (L. 335/1995 art. 2 c. 18).
        """
        stated = regular_run(1, opening_state=PeriodState.zero())
        unknown = replace(stated, current_year=None)

        def details(request: PeriodInput) -> set[str]:
            return {b.detail for b in _ENGINE.calculate_period(request).blockers}

        assert details(unknown) - details(stated) == {"other_employers"}

    @pytest.mark.parametrize(
        ("declared", "fact"),
        [
            pytest.param(_ASCENDANT, "cohabiting", id="cohabiting"),
            pytest.param(_SPOUSE, "residency_eligibility", id="residency_eligibility"),
            pytest.param(_SPOUSE, "own_income", id="own_income"),
            pytest.param(_CHILD, "allocation_pct", id="allocation_pct_child"),
            pytest.param(_ASCENDANT, "allocation_pct", id="allocation_pct_ascendant"),
        ],
    )
    def test_undeclared_dependent_condition_is_not_met(
        self, declared: Dependent, fact: str
    ) -> None:
        """A condition of art. 12 TUIR left unknown adds a missing fact.

        Own income (c. 2) and residency (c. 2-bis) condition every deduction
        of c. 1; cohabitation conditions the ascendant one (lett. d); the
        child (lett. c) and ascendant (lett. d) deductions are shared, the
        spouse one (lett. a) is not.
        """
        unknown = _family_blockers(_unknown(declared, fact))
        added = unknown - _family_blockers(declared)

        assert {d for code, d in added if code is BlockerCode.MISSING_FACT} == {fact}

    @pytest.mark.parametrize(
        ("dependent", "fact"),
        [
            pytest.param(_SPOUSE, "cohabiting", id="spouse_cohabiting"),
            pytest.param(_SPOUSE, "allocation_pct", id="spouse_allocation_pct"),
            pytest.param(_CHILD, "cohabiting", id="child_cohabiting"),
            pytest.param(_YOUNG_CHILD, "own_income", id="young_child_own_income"),
            pytest.param(
                replace(_ASCENDANT, cohabiting=False),
                "own_income",
                id="ascendant_not_cohabiting",
            ),
        ],
    )
    def test_condition_that_cannot_grant_a_deduction_adds_nothing(
        self, dependent: Dependent, fact: str
    ) -> None:
        """An unknown condition art. 12 TUIR does not read adds no blocker.

        Cohabitation is read only for an ascendant and the share only for a
        child or an ascendant; a child under 21 all year (lett. c) or an
        ascendant stated not cohabiting (lett. d) gives right to no
        deduction whatever its other conditions.
        """
        unknown = _family_blockers(_unknown(dependent, fact))
        assert unknown == _family_blockers(dependent)

    def test_dependency_interval_has_no_default(self) -> None:
        """The months of art. 12 c. 3 TUIR are never the whole year by default.

        ``None`` states an open end; leaving the interval out is an error.
        """
        with pytest.raises(TypeError, match="dependent_from"):
            Dependent(DependentRelationship.SPOUSE)  # type: ignore[call-arg]

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
