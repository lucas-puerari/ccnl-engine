"""Employment deductions and credits a conguaglio must apply.

Art. 13 TUIR and D.L. 3/2020 decide how much of the gross tax of the year is
deducted or credited back.  The expected values come from the oracles in
:mod:`tests.fixtures.normative_oracles` (:mod:`.irpef_2026`,
:mod:`.family_2026`, :mod:`.withholding_2026`), written from the sources;
every other fact of the runs is explicit
(:mod:`tests.fixtures.explicit_facts`).  A rule the engine does not apply
yet is a strict xfail on the assertion it breaks.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine import InvalidInputError, PayrollRun
from ccnl_engine.inputs import (
    DependentRelationship,
    EmploymentPeriod,
    FamilyComposition,
    FixedTerm,
    PeriodState,
    Permanent,
)
from tests.acceptance.legal_scenarios._support import COMMERCIO, ENGINE
from tests.fixtures.dependents import declared_dependent
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
from tests.fixtures.normative_oracles.irpef_2026 import (
    EMPLOYMENT_DEDUCTION_FLOOR,
    FIXED_TERM_EMPLOYMENT_DEDUCTION_FLOOR,
    employment_deduction,
    gross_irpef,
    net_irpef,
)
from tests.fixtures.normative_oracles.withholding_2026 import (
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
    from ccnl_engine.results import CalculationDecision

pytestmark = pytest.mark.legal_scenario

_CENT = Decimal("0.01")
_ZERO = Decimal("0.00")
_FLAT = Decimal(1_955)
#: Reason of the decision on the minimum left to the tax return.
_MINIMUM_REASON = "minimum_proportioned_to_days"
_METALMECCANICO = "metalmeccanico-federmeccanica.json"


def _year(
    employment: Employment, facts: PeriodFacts | None = None
) -> CompetenceYearResult:
    return ENGINE.calculate_competence_year(
        replace(competence_year(employment=employment), default_facts=facts or FACTS)
    )


def _irpef_decisions(result: PeriodResult) -> list[CalculationDecision]:
    return [d for d in result.decisions if d.capability == "irpef"]


def _irpef_inputs(result: PeriodResult) -> Mapping[str, object]:
    (decision,) = (
        d for d in _irpef_decisions(result) if d.reason_code != _MINIMUM_REASON
    )
    return decision.inputs


def _minimum_inputs(result: PeriodResult) -> Mapping[str, object]:
    (decision,) = (
        d for d in _irpef_decisions(result) if d.reason_code == _MINIMUM_REASON
    )
    return decision.inputs


_C3 = replace(CONCIA_D2, ccnl_slug=_METALMECCANICO, level_code="C3")


#: Metalmeccanico C3 for about three months, settled by the termination run:
#: 1 March to 31 May (31 + 30 + 31 = 92 days) or 10 July to 20 September
#: (22 + 31 + 20 = 73 days), each open-ended or fixed-term.
_SHORT_EMPLOYMENTS = pytest.mark.parametrize(
    ("contract", "started_on", "ended_on", "days"),
    [
        pytest.param(
            Permanent(), date(2026, 3, 1), date(2026, 5, 31), 92, id="permanent-92"
        ),
        pytest.param(
            FixedTerm(), date(2026, 3, 1), date(2026, 5, 31), 92, id="fixed-term-92"
        ),
        pytest.param(
            Permanent(), date(2026, 7, 10), date(2026, 9, 20), 73, id="permanent-73"
        ),
        pytest.param(
            FixedTerm(), date(2026, 7, 10), date(2026, 9, 20), 73, id="fixed-term-73"
        ),
    ],
)
_TRATTAMENTO_FULL_YEAR = Decimal(1_200)
_TRATTAMENTO_CORRECTIVE = Decimal(75)


def _short_year(
    contract: Permanent | FixedTerm, started_on: date, ended_on: date
) -> CompetenceYearResult:
    return _year(
        replace(
            _C3,
            contract_type=contract,
            employment_period=EmploymentPeriod(started_on, ended_on),
        )
    )


def _floor(contract: Permanent | FixedTerm) -> Decimal:
    return (
        FIXED_TERM_EMPLOYMENT_DEDUCTION_FLOOR
        if isinstance(contract, FixedTerm)
        else EMPLOYMENT_DEDUCTION_FLOOR
    )


def _for_days(amount: Decimal, days: int) -> Decimal:
    return (amount * days / 365).quantize(_CENT, rounding=ROUND_HALF_UP)


@_SHORT_EMPLOYMENTS
def test_short_employment_withholding_proportions_the_floor(
    contract: Permanent | FixedTerm, started_on: date, ended_on: date, days: int
) -> None:
    """The conguaglio deducts the floor for the days, the rest is left to the 730.

    Three months of pay are under 15,000 EUR, so lett. a) applies.  The
    withholding agent "deve ragguagliare anche la detrazione minima al
    periodo di lavoro" (istruzioni CU 2026, punto 367, p. 33): the floor
    for the days, 690 x 92 / 365 = 173.92 or 1,380 x 92 / 365 = 347.84 (92
    days), 690 x 73 / 365 = 138.00 or 1,380 x 73 / 365 = 276.00 (73 days),
    is below 1,955 x 92 / 365 = 492.77 or 1,955 x 73 / 365 = 391.00, which
    is the deduction.  The tax return grants the whole floor (Allegato C
    730/2026, par. 19.9.1): the decision records 690 or 1,380 less the
    deduction, e.g. 690 - 391.00 = 299.00 and 1,380 - 391.00 = 989.00.
    """
    result = _short_year(contract, started_on, ended_on).period_results[-1]
    inputs = _irpef_inputs(result)
    taxable = inputs["projected_taxable"]
    fixed_term = isinstance(contract, FixedTerm)
    deduction = _for_days(_FLAT, days)

    assert isinstance(taxable, Decimal)
    assert taxable <= Decimal(15_000)
    assert _for_days(_floor(contract), days) < deduction
    assert inputs["work_deduction"] == deduction
    assert deduction == employment_deduction(taxable, days, fixed_term=fixed_term)
    minimum = _minimum_inputs(result)
    assert minimum["minimum"] == _floor(contract)
    assert minimum["tax_return_balance"] == _floor(contract) - deduction


@_SHORT_EMPLOYMENTS
def test_short_employment_trattamento_compares_the_withheld_deduction(
    contract: Permanent | FixedTerm, started_on: date, ended_on: date, days: int
) -> None:
    """The trattamento test compares the gross tax with the withheld deduction.

    D.L. 3/2020 art. 1 c. 1, first period, as restated by Allegato C to the
    730/2026 instructions, par. 8.2.4: up to 15,000 EUR the credit is due
    when the gross tax exceeds the art. 13 deduction due less 75 x days /
    365, and is then 1,200 x days / 365.  The deduction of the withholding
    is 1,955 x days / 365, the floor for the days being lower: 492.77 - 18.90
    = 473.87 (92 days) and 391.00 - 15.00 = 376.00 (73 days).  The gross tax
    of the year, about 1,460 EUR (92 days) or 1,213 EUR (73 days), exceeds
    both, so every case, fixed term included, gets 1,200 x 92 / 365 =
    302.47 or 1,200 x 73 / 365 = 240.00.  The net IRPEF is the gross tax
    less the deduction: no ulteriore detrazione under 20,000 EUR.
    """
    cash = _short_year(contract, started_on, ended_on).closing_state.cash
    taxable = cash.earnings.taxable
    gross = gross_irpef(taxable)
    deduction = _for_days(_FLAT, days)
    threshold = deduction - _for_days(_TRATTAMENTO_CORRECTIVE, days)
    credit = _for_days(_TRATTAMENTO_FULL_YEAR, days) if gross > threshold else _ZERO

    assert taxable <= Decimal(15_000)
    assert credit > _ZERO
    assert cash.trattamento.recognized == credit
    assert cash.tax.irpef == max(_ZERO, gross - deduction)
    assert cash.tax.irpef == net_irpef(
        taxable, days, fixed_term=isinstance(contract, FixedTerm)
    )


def _decision_inputs(result: PeriodResult, capability: str) -> Mapping[str, object]:
    (decision,) = (d for d in result.decisions if d.capability == capability)
    return decision.inputs


def _chain(employment: Employment, months: range) -> PeriodState | None:
    state = None
    for month in months:
        run = regular_run(month, employment=employment, opening_state=state)
        state = ENGINE.calculate_period(run).closing_state
    return state


def _rehire(
    first: Employment, months: range, second: Employment, month: int
) -> PeriodResult:
    # The run of ``month`` of ``second``, opened with the state ``first`` closed.
    state = _chain(first, months)
    return ENGINE.calculate_period(
        regular_run(month, employment=second, opening_state=state)
    )


def test_rehire_counts_the_days_of_the_income_it_projects() -> None:
    """Metalmeccanico C3 from 1 January to 31 March, rehired on 1 June 2026.

    The June run starts from the state closed by March, so its projection
    holds both incomes, as the one CU of the employer does (istruzioni CU
    2026: one certificate "anche in presenza di più rapporti di lavoro ...
    per il medesimo periodo d'imposta"; punto 721: the days of "tutti i
    rapporti di lavoro conguagliati").  Days: 31 + 28 + 31 = 90 and 1 June
    to 31 December 214, 304 in all.  The deduction must be the art. 13
    formula on the projected income for 304 days, within a cent, and the
    ulteriore detrazione and the trattamento count the same days.
    """
    first = replace(
        _C3, employment_period=EmploymentPeriod(date(2026, 1, 1), date(2026, 3, 31))
    )
    second = replace(_C3, employment_period=EmploymentPeriod(date(2026, 6, 1)))
    june = _rehire(first, range(1, 4), second, 6)
    inputs = _irpef_inputs(june)
    taxable = inputs["projected_taxable"]

    assert isinstance(taxable, Decimal)
    deduction = inputs["work_deduction"]
    assert isinstance(deduction, Decimal)
    assert abs(deduction - employment_deduction(taxable, 304)) <= _CENT
    for capability in ("ulteriore_detrazione_lavoro", "trattamento_integrativo"):
        assert _decision_inputs(june, capability)["eligible_work_days"] == "304"


@pytest.mark.parametrize(
    ("contract", "floor"),
    [
        pytest.param(FixedTerm(), FIXED_TERM_EMPLOYMENT_DEDUCTION_FLOOR, id="fixed"),
        pytest.param(Permanent(), EMPLOYMENT_DEDUCTION_FLOOR, id="permanent"),
    ],
)
def test_rehire_takes_the_fixed_term_minimum_of_the_year(
    contract: FixedTerm | Permanent, floor: Decimal
) -> None:
    """C3 from 1 January to 28 February, rehired open-ended 1 May to 30 June.

    31 + 28 = 59 and 31 + 30 = 61 days, 120 in all: 1,955 x 120 / 365 =
    642.74.  Four months of C3 pay are under 15,000 EUR, so the minimum of
    lett. a) applies, 1,380 EUR when one employment of the year is
    fixed-term: Allegato C to the 730/2026 instructions, par. 19.9.1, "se
    nella casella di colonna 2 dei righi da C1 a C3 è presente in almeno un
    rigo il codice 2".  The June run is open-ended; its minimum follows the
    first employment.  The withholding proportions it (istruzioni CU 2026,
    punto 367): 1,380 x 120 / 365 = 453.70 or 690 x 120 / 365 = 226.85,
    below 642.74, which is deducted.  The tax return grants the rest of the
    minimum: 1,380 - 642.74 = 737.26 or 690 - 642.74 = 47.26.
    """
    first = replace(
        _C3,
        contract_type=contract,
        employment_period=EmploymentPeriod(date(2026, 1, 1), date(2026, 2, 28)),
    )
    second = replace(
        _C3, employment_period=EmploymentPeriod(date(2026, 5, 1), date(2026, 6, 30))
    )
    june = _rehire(first, range(1, 3), second, 6)
    inputs = _irpef_inputs(june)
    taxable = inputs["projected_taxable"]
    deduction = _for_days(_FLAT, 120)

    assert isinstance(taxable, Decimal)
    assert taxable <= Decimal(15_000)
    assert inputs["work_deduction"] == deduction
    minimum = _minimum_inputs(june)
    assert minimum["minimum"] == floor
    assert minimum["tax_return_balance"] == floor - deduction


def test_rehire_after_a_termination_run_opens_a_new_employment() -> None:
    """C3 terminated by the run of 31 March, rehired on 1 June 2026.

    The termination run ended the employment, so the June run cannot close
    on its state: the error names it instead of an order of months.  From
    the zero state the June run is the first of a new employment whose start
    is stated, with no ``opening_state`` blocker, and its withholding counts
    its own days, 1 June to 31 December: 214.
    """
    first = replace(
        _C3, employment_period=EmploymentPeriod(date(2026, 1, 1), date(2026, 3, 31))
    )
    termination = replace(
        regular_run(3, employment=first, opening_state=_chain(first, range(1, 3))),
        # RunKind is not public: the constructor normalises its value.
        run=PayrollRun(run_kind="termination", month=3, year=2026),  # type: ignore[arg-type]
        payment_date=date(2026, 3, 31),
    )
    closed = ENGINE.calculate_period(termination).closing_state
    second = replace(_C3, employment_period=EmploymentPeriod(date(2026, 6, 1)))

    with pytest.raises(InvalidInputError, match="'2026-03-termination' ended"):
        ENGINE.calculate_period(regular_run(employment=second, opening_state=closed))
    june = ENGINE.calculate_period(
        regular_run(employment=second, opening_state=PeriodState.zero())
    )
    assert "opening_state" not in {b.detail for b in june.blockers}
    for capability in ("ulteriore_detrazione_lavoro", "trattamento_integrativo"):
        assert _decision_inputs(june, capability)["eligible_work_days"] == "214"


#: Spouse and two children of 25 and 23 in 2026, all dependent all year.
_FAMILY = FamilyComposition(
    dependents=(
        declared_dependent(DependentRelationship.SPOUSE),
        declared_dependent(DependentRelationship.CHILD, birth_date=date(2001, 5, 1)),
        declared_dependent(DependentRelationship.CHILD, birth_date=date(2003, 5, 1)),
    )
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
