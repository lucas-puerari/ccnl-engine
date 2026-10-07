"""Contractual calendar entitlements, missing surtax tables and residence."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine import CompetenceYearPlan, Employment, InvalidInputError, PeriodFacts
from ccnl_engine.inputs import (
    CalendarOverride,
    CalendarOverrideReason,
    EmploymentPeriod,
    FamilyComposition,
    Permanent,
    WorkCalendar,
)
from ccnl_engine.results import BlockerCode, CalculationStatus
from tests.acceptance.legal_scenarios._support import (
    COMMERCIO,
    EMPLOYER,
    ENGINE,
    regular_period,
)
from tests.fixtures.imported_surtax import (
    MUNICIPAL_BALANCE_2025,
    REGIONAL_2025,
    opening_with_2025_surtax,
)
from tests.fixtures.opening_state import fresh_tax_year
from tests.fixtures.seniority import new_hire

if TYPE_CHECKING:
    from ccnl_engine import CompetenceYearResult, PeriodResult
    from ccnl_engine.results import CalculationDecision

_COMMERCIO_4 = Employment(
    ccnl_slug=COMMERCIO, level_code="4", contract_type=Permanent()
)
_SURTAXES = {
    "addizionale_regionale": "facts.regione",
    "addizionale_comunale": "facts.comune_belfiore",
}

pytestmark = pytest.mark.legal_scenario


def test_commercio_standard_calendar_pays_fourteen_runs() -> None:
    """CCNL Terziario Confcommercio grants tredicesima and quattordicesima.

    12 regular runs plus 2 extra-month runs = 14 runs, derived from the CCNL
    without passing a calendar.
    """
    year = ENGINE.calculate_competence_year(
        CompetenceYearPlan(year=2026, employment=_COMMERCIO_4, employer=EMPLOYER)
    )

    assert len(year.period_results) == 14


def test_empty_calendar_that_drops_extra_months_is_rejected() -> None:
    """A calendar without the two CCNL extra months must not be accepted.

    Observed on 26 September 2026, before overrides were validated: 12 runs,
    annual gross 21,475.00 instead of 25,077.50, no error.
    """
    override = CalendarOverride(
        calendar=WorkCalendar(year=2026),
        reason=CalendarOverrideReason.PAYMENT_MONTH,
        note="no extra months",
    )
    with pytest.raises(InvalidInputError, match="drops or lowers the thirteenth"):
        ENGINE.calculate_competence_year(
            CompetenceYearPlan(
                year=2026,
                employment=_COMMERCIO_4,
                employer=EMPLOYER,
                calendar_override=override,
            )
        )


def test_known_surtax_tables_are_withheld() -> None:
    """Control: Emilia-Romagna and Modena (F257) tables exist for 2026.

    January withholds the first installment of the 2025 surtax (30.00
    regional, 10.00 municipal saldo, imported); the 2026 surtax waits for
    the conguaglio, so both tables are only checked: final, amount 0.
    """
    result = regular_period(
        regione="IT-45",
        comune_belfiore="F257",
        opening_state=opening_with_2025_surtax("IT-45", "F257"),
    )

    assert result.closing_state.cash.tax.surtax == Decimal("40.00")
    assert result.assurance.calculation is CalculationStatus.FINAL
    reasons = {
        d.capability: d.reason_code
        for d in result.decisions
        if d.capability.startswith("addizionale_") and "component" not in d.inputs
    }
    assert reasons == {
        "addizionale_regionale": "determined_at_conguaglio",
        "addizionale_comunale": "determined_at_conguaglio",
    }


def test_unknown_surtax_tables_make_the_result_not_final() -> None:
    """Region and municipality without tables cannot yield a final payslip.

    Observed on 26 September 2026, before surtax decisions were kept:
    surtax 0.00 and net 1,489.92, identical to a run without region or
    municipality; the result status was final.  Now nothing is withheld,
    but the result is incomplete and names both unknown tables.
    """
    result = regular_period(
        regione="IT-99", comune_belfiore="Z999", opening_state=fresh_tax_year()
    )

    assert result.assurance.calculation is CalculationStatus.INCOMPLETE
    assert result.closing_state.cash.tax.surtax == Decimal(0)
    assert {issue.code for issue in result.issues} == {
        "regional_surtax_unknown",
        "municipal_surtax_unknown",
    }


@pytest.mark.parametrize(
    ("regione", "comune_belfiore"),
    [
        ("LOM", None),
        ("Lombardia", None),
        ("ER", None),
        ("IT-32", None),
        (None, "F25"),
        ("IT-45", "f257"),
    ],
)
def test_malformed_surtax_codes_are_rejected(
    regione: str | None, comune_belfiore: str | None
) -> None:
    """A malformed code is an input error, not an unknown table."""
    with pytest.raises(InvalidInputError, match=r"regione|comune_belfiore"):
        regular_period(regione=regione, comune_belfiore=comune_belfiore)


def _annual_surtax(result: PeriodResult) -> dict[str, CalculationDecision]:
    """Return the decision on the surtax of the tax year, by capability.

    Returns:
        The decisions without ``inputs["component"]``, by capability.
    """
    return {
        d.capability: d
        for d in result.decisions
        if d.capability in _SURTAXES and "component" not in d.inputs
    }


def _assert_residence_unknown(result: PeriodResult, *capabilities: str) -> None:
    """Each surtax in ``capabilities`` is undetermined for lack of residence.

    The surtax is due to the region and municipality of the domicilio
    fiscale on 1 January (D.Lgs. 446/1997 art. 50 c. 5, D.Lgs. 360/1998
    art. 1 c. 4): without it the scope is unknown, never not applicable,
    so the decision names the fact, carries no amount and is incomplete,
    and the fact is a ``requirement_unresolved`` blocker as well.
    """
    annual = _annual_surtax(result)
    blockers = {(b.code, b.feature, b.detail) for b in result.blockers}
    for capability in capabilities:
        decision = annual[capability]
        assert decision.reason_code == "residence_unknown"
        assert decision.status is CalculationStatus.INCOMPLETE
        assert decision.amount is None
        assert decision.inputs["fact"] == _SURTAXES[capability]
        assert (
            BlockerCode.REQUIREMENT_UNRESOLVED,
            capability,
            _SURTAXES[capability],
        ) in blockers
    assert result.assurance.calculation is CalculationStatus.INCOMPLETE
    assert not result.is_payable


def test_unknown_residence_leaves_the_surtax_undetermined() -> None:
    """January without residence: both surtaxes undetermined, 2025 still withheld.

    The 2025 debts keep the jurisdiction that determined them, so their
    first installments are withheld all the same: 330.00 / 11 = 30.00
    regional (3802) and 110.00 / 11 = 10.00 municipal saldo (3848),
    D.Lgs. 446/1997 art. 50 c. 4 and D.Lgs. 360/1998 art. 1 c. 5; the
    acconto starts in March.
    """
    result = regular_period(opening_state=opening_with_2025_surtax("IT-45", "F257"))

    _assert_residence_unknown(result, *_SURTAXES)
    first = REGIONAL_2025 / 11 + MUNICIPAL_BALANCE_2025 / 11
    assert result.closing_state.cash.tax.surtax == first


def test_region_alone_leaves_only_the_municipal_surtax_undetermined() -> None:
    """A stated region decides the regional surtax; the municipality stays open."""
    result = regular_period(regione="IT-88")

    _assert_residence_unknown(result, "addizionale_comunale")
    regional = _annual_surtax(result)["addizionale_regionale"]
    assert regional.reason_code == "determined_at_conguaglio"
    assert regional.status is CalculationStatus.FINAL


def test_termination_without_residence_determines_no_surtax_of_the_year() -> None:
    """The conguaglio of a March termination cannot determine the 2026 surtax.

    Ended 31 March 2026: the March run is the last of the employment and
    its conguaglio.  The residual 2025 debts are withheld at once (art. 50
    c. 4, art. 1 c. 5): 330.00 - 2 x 30.00 = 270.00 regional and
    110.00 - 2 x 10.00 = 90.00 municipal, after the January and February
    installments.  No 2026 surtax is determined, withheld or refunded.
    """
    year = ENGINE.calculate_competence_year(
        CompetenceYearPlan(
            year=2026,
            employment=Employment(
                ccnl_slug=COMMERCIO,
                level_code="4",
                seniority=new_hire(),
                employment_period=EmploymentPeriod(date(2020, 1, 1), date(2026, 3, 31)),
                contract_type=Permanent(),
            ),
            employer=EMPLOYER,
            default_facts=PeriodFacts(family_composition=FamilyComposition()),
            opening_state=opening_with_2025_surtax("IT-45", "F257"),
        )
    )
    closing = year.period_results[-1]
    installment = REGIONAL_2025 / 11, MUNICIPAL_BALANCE_2025 / 11

    _assert_residence_unknown(closing, *_SURTAXES)
    settled = {
        d.capability: d.amount
        for d in closing.decisions
        if d.reason_code == "settled_at_termination"
    }
    assert settled == {
        "addizionale_regionale": REGIONAL_2025 - 2 * installment[0],
        "addizionale_comunale": MUNICIPAL_BALANCE_2025 - 2 * installment[1],
    }
    assert not {d.reason_code for d in closing.decisions} & {
        "table_applied",
        "withheld_at_termination",
        "deferred_to_installments",
        "surtax_refunded",
    }


def _year_2026(facts: PeriodFacts) -> CompetenceYearResult:
    """Commercio 4 employed since 2020, 2026 with the imported 2025 surtax.

    Returns:
        The year result, its conguaglio last.
    """
    return ENGINE.calculate_competence_year(
        CompetenceYearPlan(
            year=2026,
            employment=Employment(
                ccnl_slug=COMMERCIO,
                level_code="4",
                seniority=new_hire(),
                employment_period=EmploymentPeriod(date(2020, 1, 1)),
                contract_type=Permanent(),
            ),
            employer=EMPLOYER,
            default_facts=facts,
            opening_state=opening_with_2025_surtax("IT-45", "F257"),
        )
    )


def test_conguaglio_without_residence_cannot_open_the_next_year() -> None:
    """The 2026 conguaglio without residence leaves 2027 without its surtax.

    The conguaglio of N determines the regional surtax and the municipal
    saldo of N, withheld in N+1, and the municipal acconto of N+1 (D.Lgs.
    446/1997 art. 50 c. 4, D.Lgs. 360/1998 art. 1 cc. 4-5).  Without the
    domicilio fiscale it determines none of them, so the state it closes
    misses what 2027 must withhold: it is not chainable, and the state
    close_tax_year() opens from it is not either.
    """
    year = _year_2026(PeriodFacts(family_composition=FamilyComposition()))
    results = year.period_results
    conguaglio = results[-1]

    _assert_residence_unknown(conguaglio, *_SURTAXES)
    assert all(r.closing_state.history_known for r in results[:-1])
    assert not conguaglio.closing_state.history_known
    assert not ENGINE.close_tax_year(conguaglio.closing_state).history_known
    assert not year.next_opening_state.history_known


def test_conguaglio_with_residence_opens_the_next_year() -> None:
    """Control: the same year with the residence closes a chainable state."""
    year = _year_2026(
        PeriodFacts(
            family_composition=FamilyComposition(),
            regione="IT-45",
            comune_belfiore="F257",
        )
    )

    assert year.next_opening_state.history_known
