"""Domestic-work contributions of a period: flat hourly INPS amounts.

The domestic CCNLs pay INPS per contributable hour, on an hours bracket
above 24 weekly hours and on wage brackets below it, with a higher employer
rate for fixed-term contracts; both hour facts are mandatory.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from ccnl_engine.errors import MissingRequiredFactError
from ccnl_engine.payroll.application.calculate_period import calculate_period
from ccnl_engine.payroll.domain.employment import FixedTerm, Permanent
from ccnl_engine.payroll.domain.fixed_term import NaspiExclusion
from tests.fixtures.period_requests import period_request

_ZERO = Decimal(0)


# ---------------------------------------------------------------------------
# Domestic-work contributions silently zero
#
# calculate_period routes domestic CCNLs through a zero-contribution path
# (now fixed).  The result has period_gross > 0 but contribution_breakdown
# employee == employer == 0.  This is a silent incorrect result.
# ---------------------------------------------------------------------------


def test_domestic_contributions_nonzero() -> None:
    """Lavoro domestico must produce employee and employer INPS contributions > 0.

    Uses the hours bracket (weekly_hours=30 > 24
    threshold): employee 0.31/h, employer 0.93/h on 130 contributable hours.
    Expected: contribution_breakdown.employee > 0 and employer > 0.
    """
    result = calculate_period(
        period_request(
            month=6,
            ccnl="lavoro-domestico-convivente.json",
            level="BS",
            weekly_hours=30,
            contributable_hours=Decimal(130),
        )
    )

    assert result.contribution_breakdown.employee > _ZERO, (
        f"Domestic worker employee contributions must be > 0; "
        f"got {result.contribution_breakdown.employee}."
    )
    assert result.contribution_breakdown.employer > _ZERO, (
        f"Domestic worker employer contributions must be > 0; "
        f"got {result.contribution_breakdown.employer}."
    )


# ---------------------------------------------------------------------------
# lavoro-domestico-convivente.json raises TypeError
#
# calculate_period invokes resolve_rates which requires standard INPS rates.
# The domestic CCNL uses flat per-hour contributions and is incompatible with
# the standard rate path.  Any call with a domestic CCNL slug must not raise
# TypeError; it must return a valid PeriodResult.
# ---------------------------------------------------------------------------


def test_domestic_work_no_type_error() -> None:
    """calculate_period with a domestic CCNL returns a valid result.

    Source: CCNL lavoro domestico (CNEL A221).  Expected: valid result with
    period_gross > 0 and non-zero domestic INPS contributions.
    """
    req = period_request(
        month=6,
        ccnl="lavoro-domestico-convivente.json",
        level="BS",
        weekly_hours=30,
        contributable_hours=Decimal(130),
    )
    result = calculate_period(req)
    assert result.period_gross > _ZERO, (
        "calculate_period for lavoro-domestico-convivente.json must return a "
        f"valid result with period_gross > 0; got {result.period_gross}."
    )
    assert result.contribution_breakdown.employee > _ZERO, (
        "Domestic CCNL must produce non-zero employee INPS contributions."
    )


# ---------------------------------------------------------------------------
# Domestic contribution: MissingRequiredFactError on absent mandatory facts
# ---------------------------------------------------------------------------


def test_domestic_missing_weekly_hours_raises() -> None:
    """calculate_period raises MissingRequiredFactError when weekly_hours is absent."""
    with pytest.raises(MissingRequiredFactError, match="weekly_hours"):
        calculate_period(
            period_request(
                month=6,
                ccnl="lavoro-domestico-convivente.json",
                level="BS",
                contributable_hours=Decimal(130),
            )
        )


def test_domestic_missing_contributable_hours_raises() -> None:
    """calculate_period raises MissingRequiredFactError when contributable_hours absent.

    Source: domestic contribution path requires both weekly_hours and
    contributable_hours; absent contributable_hours raises the error.
    """
    with pytest.raises(MissingRequiredFactError, match="contributable_hours"):
        calculate_period(
            period_request(
                month=6,
                ccnl="lavoro-domestico-convivente.json",
                level="BS",
                weekly_hours=30,
            )
        )


def test_domestic_contributions_wage_bracket() -> None:
    """Domestic contributions use wage brackets when weekly_hours <= threshold.

    weekly_hours=20 <= 24 threshold; BS monthly gross ~1053 EUR, hourly_divisor
    234 gives ~4.50 EUR/h → first wage bracket (up to 9.61 EUR/h):
    employee 0.43/h, employer 1.27/h.
    """
    result = calculate_period(
        period_request(
            month=6,
            ccnl="lavoro-domestico-convivente.json",
            level="BS",
            weekly_hours=20,
            contributable_hours=Decimal(86),
        )
    )
    assert result.contribution_breakdown.employee > _ZERO
    assert result.contribution_breakdown.employer > _ZERO
    names = {c.name for c in result.contribution_breakdown.components}
    assert "domestic_employee_per_hour" in names
    assert "domestic_employer_per_hour" in names


def test_domestic_contributions_fixed_term_hours_bracket() -> None:
    """Fixed-term domestic contract uses employer_per_hour_fixed_term for hours bracket.

    weekly_hours=30 > 24 threshold uses hours_bracket; FixedTerm selects
    the higher fixed-term employer rate (1.01/h vs 0.93/h for permanent).
    """
    result = calculate_period(
        period_request(
            month=6,
            ccnl="lavoro-domestico-convivente.json",
            level="BS",
            weekly_hours=30,
            contributable_hours=Decimal(130),
            contract_type=FixedTerm(renewals=0, naspi_exclusion=NaspiExclusion.NONE),
        )
    )
    assert result.contribution_breakdown.employer > _ZERO


def test_domestic_contributions_fixed_term_wage_bracket() -> None:
    """Fixed-term domestic contract uses employer_per_hour_fixed_term for wage bracket.

    weekly_hours=20 <= 24 threshold uses wage_bracket; FixedTerm selects
    the higher fixed-term employer rate (1.39/h vs 1.27/h for permanent).
    """
    result = calculate_period(
        period_request(
            month=6,
            ccnl="lavoro-domestico-convivente.json",
            level="BS",
            weekly_hours=20,
            contributable_hours=Decimal(86),
            contract_type=FixedTerm(renewals=0, naspi_exclusion=NaspiExclusion.NONE),
        )
    )
    assert result.contribution_breakdown.employer > _ZERO


@pytest.mark.parametrize("weekly_hours", [20, 30])
def test_domestic_replacement_worker_takes_the_permanent_hourly_rate(
    weekly_hours: int,
) -> None:
    """A fixed term replacing an absent worker owes no NASpI surcharge.

    L. 92/2012 art. 2 c. 29 lett. a: the hourly employer rate is the one of
    a permanent contract, in both kinds of bracket.
    """

    def employer(contract: FixedTerm | Permanent) -> Decimal:
        return calculate_period(
            period_request(
                month=6,
                ccnl="lavoro-domestico-convivente.json",
                level="BS",
                weekly_hours=weekly_hours,
                contributable_hours=Decimal(86),
                contract_type=contract,
            )
        ).contribution_breakdown.employer

    replacement = FixedTerm(naspi_exclusion=NaspiExclusion.REPLACEMENT)
    charged = FixedTerm(renewals=3, naspi_exclusion=NaspiExclusion.NONE)
    assert employer(replacement) == employer(Permanent())
    assert employer(charged) > employer(Permanent())
