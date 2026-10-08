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
second property runs on every ``requires_fact`` field of the registry of
input defaults, with one or more request pairs per field
(:mod:`tests.fixtures.default_cases`).
"""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from functools import cache
from typing import Any

import pytest

from ccnl_engine import (
    CompetenceYearPlan,
    CompetenceYearResult,
    Employment,
    PayrollEngine,
    PeriodFacts,
    PeriodInput,
    PeriodResult,
    TaxYearResult,
)
from ccnl_engine.inputs import (
    Dependent,
    DependentRelationship,
    FamilyComposition,
    PeriodState,
)
from ccnl_engine.results import BlockerCode
from tests.fixtures.default_cases import DEFAULT_CASES, DefaultCase, Request
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


_ASCENDANT = declared_dependent(DependentRelationship.ASCENDANT)
_SPOUSE = declared_dependent(DependentRelationship.SPOUSE)
_CHILD = declared_dependent(DependentRelationship.CHILD, birth_date=date(2004, 3, 1))
_YOUNG_CHILD = declared_dependent(
    DependentRelationship.CHILD, birth_date=date(2015, 3, 1)
)


class TestDefaultIsNotAFact:
    """A field left to its default must not pass as the fact it stands for."""

    def test_explicit_scenario_is_blocked_only_by_weak_sources(self) -> None:
        """The premise: with every fact given, only assumed rules block.

        The somma esente bands and the rules of the rulesets that declare
        ``source_type`` ``estimated`` are assumed; no blocker names a fact.
        """
        blockers = _blocker_set(_june_with())
        assert (BlockerCode.RULE_SOURCE_WEAK, "somma_esente") in blockers
        assert {code for code, _ in blockers} == {BlockerCode.RULE_SOURCE_WEAK}

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


def _triples(request: Request) -> set[tuple[BlockerCode, str | None, str]]:
    """Return the blockers of ``request`` through the public facade.

    Returns:
        The code, feature and detail of every blocker of the result.
    """
    if isinstance(request, PeriodInput):
        result: PeriodResult | CompetenceYearResult | TaxYearResult = (
            _ENGINE.calculate_period(request)
        )
    elif isinstance(request, CompetenceYearPlan):
        result = _ENGINE.calculate_competence_year(request)
    else:
        result = _ENGINE.calculate_tax_year(request)
    return {(b.code, b.feature, b.detail) for b in result.blockers}


_CASES = [
    pytest.param(case, id=f"{field}[{index}]")
    for field, cases in DEFAULT_CASES.items()
    for index, case in enumerate(cases)
]
_NAMING_CASES = [
    pytest.param(case, id=f"{field}[{index}]")
    for field, cases in DEFAULT_CASES.items()
    for index, case in enumerate(cases)
    if case.names is not None
]


class TestTrueFactHasNoMoreBlockers:
    """Stating a fact never looks less payable than leaving it to its default.

    Otherwise the false default is the one path that looks payable.  Each
    ``requires_fact`` field of the registry of input defaults has a case
    (:mod:`tests.fixtures.default_cases`); a field honoured by a blocker
    also shows the blocker its default adds.
    """

    @pytest.mark.parametrize("case", _CASES)
    def test_true_fact_has_no_more_blockers(self, case: DefaultCase) -> None:
        """The run stating the fact has at most the blockers of the default."""
        assert len(_triples(case.true)) <= len(_triples(case.default))

    @pytest.mark.parametrize("case", _NAMING_CASES)
    def test_default_names_the_fact(self, case: DefaultCase) -> None:
        """The default adds a blocker naming the fact the true run states."""
        added = _triples(case.default) - _triples(case.true)
        assert case.names in {detail for _, _, detail in added}
