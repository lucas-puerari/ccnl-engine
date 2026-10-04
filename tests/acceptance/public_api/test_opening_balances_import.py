"""Opening balances are imported with a dedicated command and follow competence.

The IVS massimale (L. 335/1995 art. 2 c. 18) caps the INPS base of a
worker in a calendar year across every employment: the base of an earlier
or simultaneous employment counts toward it (INPS circ. 237/2016 par. 3.1).
INPS contributions follow competence (same circolare, par. 2.1): December
2026 paid on 13 January 2027 is IRPEF income of 2027 but INPS base of 2026.

Hand computation, Metalmeccanico C3 of September 2026 (gross 2,211.43, the
minimo of the fixture ``metalmeccanico_c3_2026``), industrial employer with
50 employees, worker first enrolled in 2001 (the massimale applies), INPS
2026 bundle rules: massimale 122,295.00, employee IVS 9.19%, other employee
rate 0.30%, additional 1% above 56,224.00 up to the massimale.

- Base of the earlier employer: 121,000.00; headroom 1,295.00.
- IVS employee: 1,295.00 x 9.19% = 119.0105 -> 119.01.
- Other employee rate: 2,211.43 x 0.30% = 6.63429 -> 6.63.
- Additional 1%: (122,295.00 - 56,224.00) - (121,000.00 - 56,224.00) =
  1,295.00 x 1% = 12.95.
- Employee INPS: 119.01 + 6.63 + 12.95 = 138.59.

Without the import the same run pays 2,211.43 x 9.49% = 209.86.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    InvalidInputError,
    PayrollEngine,
    PayrollRun,
    PeriodInput,
    PeriodResult,
)
from ccnl_engine.inputs import (
    ContributionHistory,
    EmploymentPeriod,
    InpsBaseYtd,
    OpeningBalances,
    PayrollRunId,
    PeriodState,
)
from tests.fixtures.next_year_repository import NextYearRepository
from tests.fixtures.normative_oracles.payslips.metalmeccanico_c3_2026 import (
    C3_MINIMUM_FROM_JUNE_2026,
)
from tests.fixtures.seniority import new_hire

_ENGINE = PayrollEngine.bundled()
_C3 = Employment(
    ccnl_slug="metalmeccanico-federmeccanica.json",
    level_code="C3",
    employment_period=EmploymentPeriod(date(2026, 9, 1)),
    seniority=new_hire(),
    contribution_history=ContributionHistory(first_enrolled_on=date(2001, 9, 1)),
)
_EMPLOYER = EmployerProfile(headcount=Headcount(50))


def _september(opening: PeriodState) -> PeriodResult:
    return _ENGINE.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(2026, 9),
            payment_date=date(2026, 9, 28),
            employment=_C3,
            employer=_EMPLOYER,
            opening_state=opening,
        )
    )


def _employee_components(result: PeriodResult) -> dict[str, Decimal]:
    return {
        c.name: c.amount
        for c in result.contribution_breakdown.components
        if not c.name.endswith("employer")
    }


def _imported(base: InpsBaseYtd) -> PeriodState:
    return _ENGINE.import_opening_balances(
        OpeningBalances(tax_year=2026, inps_bases=(base,))
    )


class TestInpsBaseOfOtherEmployers:
    """The massimale is cumulative across the worker's employments."""

    def test_earlier_employer_base_caps_the_new_employment(self) -> None:
        """121,000.00 elsewhere leaves 1,295.00 of IVS base: 138.59 employee."""
        result = _september(
            _imported(InpsBaseYtd(2026, other_employers=Decimal("121000.00")))
        )

        assert result.period_gross == C3_MINIMUM_FROM_JUNE_2026
        assert _employee_components(result) == {
            "ivs_employee": Decimal("119.01"),
            "non_ivs_employee": Decimal("6.63"),
            "addizionale_1pct": Decimal("12.95"),
        }
        assert result.contribution_breakdown.employee == Decimal("138.59")
        base = result.closing_state.accrual.inps_base(2026)
        assert base.own == C3_MINIMUM_FROM_JUNE_2026
        assert base.other_employers == Decimal("121000.00")

    def test_other_employers_count_as_this_employer_would(self) -> None:
        """Differential: the same base held by this employer gives the same run."""
        other = _september(
            _imported(InpsBaseYtd(2026, other_employers=Decimal(121000)))
        )
        own = _september(_imported(InpsBaseYtd(2026, own=Decimal(121000))))

        assert other.contribution_breakdown == own.contribution_breakdown

    def test_without_the_import_the_run_is_uncapped(self) -> None:
        """No other employment: 2,211.43 x 9.49% = 209.86."""
        result = _september(PeriodState.zero())

        assert result.contribution_breakdown.employee == Decimal("209.86")

    def test_the_import_is_the_only_entry_point_for_external_totals(self) -> None:
        """The command checks its argument like every facade method."""
        with pytest.raises(InvalidInputError) as info:
            _ENGINE.import_opening_balances({"tax_year": 2026})  # type: ignore[arg-type]

        assert info.value.field == "balances"


class TestCompetence:
    """A late December counts toward the INPS base of its own year."""

    def test_late_december_adds_to_the_base_of_its_competence_year(self) -> None:
        """December 2026 paid in 2027 grows the 2026 base, not the 2027 one."""
        engine = PayrollEngine(repository=NextYearRepository())
        earlier = tuple(
            PayrollRunId.parse(f"2026-{m:02d}-regular") for m in range(1, 12)
        )
        opening = engine.import_opening_balances(
            OpeningBalances(
                tax_year=2027,
                competence_runs=earlier,
                inps_bases=(InpsBaseYtd(2026, own=Decimal("30000.00")),),
            )
        )

        result = engine.calculate_period(
            PeriodInput(
                run=PayrollRun.regular(2026, 12),
                payment_date=date(2027, 1, 13),
                employment=Employment(
                    ccnl_slug="commercio-confcommercio.json", level_code="4"
                ),
                employer=_EMPLOYER,
                opening_state=opening,
            )
        )

        accrual = result.closing_state.accrual
        assert result.closing_state.tax_year == 2027
        assert accrual.inps_base(2026).own == Decimal("30000.00") + result.period_gross
        assert accrual.inps_base(2027).total == 0
        assert accrual.regular_months(2026) == 12

    def test_imported_competence_run_is_not_paid_again(self) -> None:
        """A run closed in an earlier tax year is rejected in the next one."""
        november = PayrollRunId.parse("2026-11-regular")
        engine = PayrollEngine(repository=NextYearRepository())
        opening = engine.import_opening_balances(
            OpeningBalances(tax_year=2027, competence_runs=(november,))
        )

        with pytest.raises(InvalidInputError, match="already closed"):
            engine.calculate_period(
                PeriodInput(
                    run=PayrollRun.of(november),
                    payment_date=date(2027, 1, 13),
                    employment=Employment(
                        ccnl_slug="commercio-confcommercio.json", level_code="4"
                    ),
                    employer=_EMPLOYER,
                    opening_state=opening,
                )
            )
