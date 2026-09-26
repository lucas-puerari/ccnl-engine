"""Contractual calendar entitlements and missing surtax tables."""

from __future__ import annotations

from decimal import Decimal

import pytest

from ccnl_engine import (
    CalculationStatus,
    CalendarOverride,
    CalendarOverrideReason,
    InvalidInputError,
    PayrollYearRequest,
)
from ccnl_engine.payroll.domain.calendar import WorkCalendar
from tests.acceptance.legal_scenarios._support import COMMERCIO, ENGINE, regular_period

pytestmark = pytest.mark.legal_scenario


def test_commercio_standard_calendar_pays_fourteen_runs() -> None:
    """CCNL Terziario Confcommercio grants tredicesima and quattordicesima.

    12 regular runs plus 2 extra-month runs = 14 runs, derived from the CCNL
    without passing a calendar.
    """
    year = ENGINE.calculate_year(
        PayrollYearRequest(year=2026, ccnl_slug=COMMERCIO, level_code="4")
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
        ENGINE.calculate_year(
            PayrollYearRequest(
                year=2026, ccnl_slug=COMMERCIO, level_code="4", calendar=override
            )
        )


def test_known_surtax_tables_are_withheld() -> None:
    """Control: Emilia-Romagna and Modena (F257) tables exist for 2026."""
    result = regular_period(regione="IT-45", comune_belfiore="F257")

    assert result.closing_state.tax.surtax > Decimal(0)
    assert result.status is CalculationStatus.FINAL
    reasons = {d.capability: d.reason_code for d in result.decisions}
    assert reasons == {
        "addizionale_regionale": "table_applied",
        "addizionale_comunale": "advance_applied",
    }


def test_unknown_surtax_tables_make_the_result_not_final() -> None:
    """Region and municipality without tables cannot yield a final payslip.

    Observed on 26 September 2026, before surtax decisions were kept:
    surtax 0.00 and net 1,489.92, identical to a run without region or
    municipality; the result status was final.  Now nothing is withheld,
    but the result is incomplete and names both unknown tables.
    """
    result = regular_period(regione="IT-99", comune_belfiore="Z999")

    assert result.status is CalculationStatus.INCOMPLETE
    assert result.closing_state.tax.surtax == Decimal(0)
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
