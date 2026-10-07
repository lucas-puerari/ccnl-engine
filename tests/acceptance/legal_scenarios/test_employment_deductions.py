"""Employment deductions and credits a conguaglio must apply.

Art. 13 TUIR and D.L. 3/2020 decide how much of the gross tax of the year is
deducted or credited back.  The expected values come from the oracles in
:mod:`tests.fixtures.normative_oracles` (:mod:`.irpef_2026`,
:mod:`.family_2026`, :mod:`.withholding_2026`), written from the sources;
every other fact of the runs is explicit
(:mod:`tests.fixtures.explicit_facts`).  None of these rules holds today:
each test is a strict xfail on the assertion it breaks.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine.inputs import (
    Dependent,
    DependentRelationship,
    EmploymentPeriod,
    FamilyComposition,
    FixedTerm,
    Permanent,
)
from tests.acceptance.legal_scenarios._support import COMMERCIO, ENGINE
from tests.fixtures.explicit_facts import (
    CONCIA_D2,
    FACTS,
    competence_year,
    regular_run,
)
from tests.fixtures.normative_oracles.family_2026 import (
    child_deduction,
    spouse_deduction,
)
from tests.fixtures.normative_oracles.irpef_2026 import employment_deduction
from tests.fixtures.normative_oracles.withholding_2026 import (
    EMPLOYMENT_DEDUCTION_FLOOR,
    FIXED_TERM_EMPLOYMENT_DEDUCTION_FLOOR,
    trattamento_integrativo_above_15000,
)

if TYPE_CHECKING:
    from collections.abc import Mapping

    from ccnl_engine import (
        CompetenceYearResult,
        Employment,
        PeriodFacts,
        PeriodResult,
    )

pytestmark = pytest.mark.legal_scenario

_CENT = Decimal("0.01")
_METALMECCANICO = "metalmeccanico-federmeccanica.json"


def _year(
    employment: Employment, facts: PeriodFacts | None = None
) -> CompetenceYearResult:
    return ENGINE.calculate_competence_year(
        replace(competence_year(employment=employment), default_facts=facts or FACTS)
    )


def _irpef_inputs(result: PeriodResult) -> Mapping[str, object]:
    (decision,) = (d for d in result.decisions if d.capability == "irpef")
    return decision.inputs


_C3 = replace(CONCIA_D2, ccnl_slug=_METALMECCANICO, level_code="C3")


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason=(
        "the art. 13 deduction proportioned to the days has no floor; art. 13 "
        "c. 1 lett. a) TUIR sets 690 EUR, 1,380 EUR for a fixed term, not "
        "proportioned to the days (Allegato C 730/2026)"
    ),
)
@pytest.mark.parametrize(
    ("contract", "started_on", "ended_on", "floor"),
    [
        pytest.param(
            Permanent(),
            date(2026, 3, 1),
            date(2026, 5, 31),
            EMPLOYMENT_DEDUCTION_FLOOR,
            id="permanent-92-days",
        ),
        pytest.param(
            FixedTerm(),
            date(2026, 3, 1),
            date(2026, 5, 31),
            FIXED_TERM_EMPLOYMENT_DEDUCTION_FLOOR,
            id="fixed-term-92-days",
        ),
        pytest.param(
            Permanent(),
            date(2026, 7, 10),
            date(2026, 9, 20),
            EMPLOYMENT_DEDUCTION_FLOOR,
            id="permanent-73-days",
        ),
        pytest.param(
            FixedTerm(),
            date(2026, 7, 10),
            date(2026, 9, 20),
            FIXED_TERM_EMPLOYMENT_DEDUCTION_FLOOR,
            id="fixed-term-73-days",
        ),
    ],
)
def test_short_employment_deduction_is_not_below_the_floor(
    contract: Permanent | FixedTerm, started_on: date, ended_on: date, floor: Decimal
) -> None:
    """Metalmeccanico C3 for three months, settled by the termination run.

    Three months of pay are under 15,000 EUR, so lett. a) applies: 1,955 x
    92 / 365 = 492.77 (1 March to 31 May) or 1,955 x 73 / 365 = 391.00
    (10 July to 20 September, 22 + 31 + 20 days), both below the floor of
    the contract.  The deduction of the conguaglio is the floor.  With a
    fixed term the gross tax of the 73-day case (about 1,213 EUR) is below
    1,380, so the net IRPEF of the year is zero.
    """
    employment = replace(
        _C3,
        contract_type=contract,
        employment_period=EmploymentPeriod(started_on, ended_on),
    )
    inputs = _irpef_inputs(_year(employment).period_results[-1])
    taxable = inputs["projected_taxable"]

    assert isinstance(taxable, Decimal)
    assert taxable <= Decimal(15_000)
    assert inputs["work_deduction"] == floor


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason=(
        "a worker rehired in the same year projects the income of both "
        "employments but the days of the second only (214 of 304); art. 13 "
        "c. 1 TUIR proportions the deduction to the days of the income it "
        "is computed on"
    ),
)
def test_rehire_counts_the_days_of_the_income_it_projects() -> None:
    """Metalmeccanico C3 from 1 January to 31 March, rehired on 1 June 2026.

    The June run starts from the state closed by March, so its projection
    holds both incomes: 31 + 28 + 31 = 90 days and 1 June to 31 December
    214 days, 304 in all.  The deduction must be the art. 13 formula on
    the projected income for 304 days, within a cent.
    """
    first = replace(
        _C3, employment_period=EmploymentPeriod(date(2026, 1, 1), date(2026, 3, 31))
    )
    state = None
    for month in (1, 2, 3):
        run = regular_run(month, employment=first, opening_state=state)
        state = ENGINE.calculate_period(run).closing_state
    second = replace(_C3, employment_period=EmploymentPeriod(date(2026, 6, 1)))
    june = ENGINE.calculate_period(regular_run(employment=second, opening_state=state))
    inputs = _irpef_inputs(june)
    taxable = inputs["projected_taxable"]

    assert isinstance(taxable, Decimal)
    deduction = inputs["work_deduction"]
    assert isinstance(deduction, Decimal)
    assert abs(deduction - employment_deduction(taxable, 304)) <= _CENT


#: Spouse and two children of 25 and 23 in 2026, all dependent all year.
_FAMILY = FamilyComposition(
    dependents=(
        Dependent(DependentRelationship.SPOUSE),
        Dependent(DependentRelationship.CHILD, birth_date=date(2001, 5, 1)),
        Dependent(DependentRelationship.CHILD, birth_date=date(2003, 5, 1)),
    )
)


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason=(
        "the trattamento integrativo between 15,000 and 28,000 EUR compares "
        "the gross tax with the art. 13 deduction alone; D.L. 3/2020 art. 1 "
        "c. 1 compares it with the sum of the art. 12 and art. 13 "
        "deductions"
    ),
)
@pytest.mark.parametrize("level_code", ["7", "6"])
def test_trattamento_integrativo_counts_the_family_deductions(
    level_code: str,
) -> None:
    """Commercio level 7 or 6, full year 2026, spouse and two children.

    Art. 12 c. 1 lett. c): children of 21 to 29 give 950 x (110,000 -
    income) / 110,000 each, two children raising the ceiling by 15,000, in
    full to the worker whose spouse is dependent; lett. a): 690 for the
    spouse between 15,000 and 40,000.  On the year's taxable (about 17,200
    EUR at level 7, 19,000 at level 6) art. 12 + art. 13 exceed the gross
    tax, so the credit is their difference capped at 1,200, computed by
    :func:`~tests.fixtures.normative_oracles.withholding_2026.trattamento_integrativo_above_15000`.
    """
    employment = replace(CONCIA_D2, ccnl_slug=COMMERCIO, level_code=level_code)
    year = _year(employment, replace(FACTS, family_composition=_FAMILY))
    cash = year.closing_state.cash
    income = cash.earnings.taxable
    family = spouse_deduction(income) + 2 * child_deduction(income, children=2)
    expected = trattamento_integrativo_above_15000(income, family)

    assert expected > 0
    assert abs(cash.trattamento.recognized - expected) <= _CENT
