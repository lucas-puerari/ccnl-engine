"""A result is final only when every amount it exposes can be paid.

Today ``CalculationStatus.FINAL`` is the only signal an integration reads to
pay an amount.  These tests state the contract the engine does not meet yet:
a result with an unknown fact, an incomplete coverage or a known wrong
amount must not be final.  Each case is a strict ``xfail`` pinned to the
assertion it breaks today.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine import (
    BonusEvent,
    CalculationStatus,
    ContributionCeilingStatus,
    EmployerProfile,
    Employment,
    EmploymentPeriod,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodFacts,
    PeriodInput,
    PeriodResult,
    WorkerCategory,
    YearInput,
)

_ENGINE = PayrollEngine.bundled()
_EMPLOYER = EmployerProfile(headcount=Headcount(50))
_METALMECCANICO = "metalmeccanico-federmeccanica.json"
_POSTAL_FISE = "servizi-postali-appalto-fise.json"


def _january(employment: Employment, facts: PeriodFacts | None = None) -> PeriodResult:
    return _ENGINE.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(2026, 1),
            payment_date=date(2026, 1, 27),
            employment=employment,
            employer=_EMPLOYER,
            facts=facts or PeriodFacts(),
        )
    )


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="final status ignores capability gaps and assumed rule sources",
)
def test_incomplete_coverage_is_not_final() -> None:
    """Metalmeccanico C3, January 2026, an ordinary month.

    The capability report is ``incomplete`` with 14 ``feature_absent`` gaps
    and ``base_salary`` and ``somma_esente`` come from ``assumed`` rules, yet
    the result is ``final``.  The engine holds the evidence to block it.
    """
    result = _january(Employment(ccnl_slug=_METALMECCANICO, level_code="C3"))

    assert result.status is not CalculationStatus.FINAL


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="unknown IVS ceiling eligibility computes the uncapped branch as final",
)
def test_unknown_ivs_ceiling_eligibility_is_not_final() -> None:
    """A 200,000 EUR bonus crosses the 2026 IVS massimale of 122,295 EUR.

    Whether the massimale applies depends on the first enrolment date
    (L. 335/1995 art. 2 c. 18): it is a fact, not a default.  With
    ``UNKNOWN`` the engine computes the uncapped branch, employee INPS
    20,644.15 as with ``NOT_APPLICABLE`` against 12,506.09 with
    ``POST_1995``, and marks the result ``final``.
    """
    employment = Employment(
        ccnl_slug=_METALMECCANICO,
        level_code="C3",
        ceiling_status=ContributionCeilingStatus.UNKNOWN,
    )
    bonus = BonusEvent(event_date=date(2026, 1, 15), amount=Decimal(200_000))

    result = _january(employment, PeriodFacts(events=(bonus,)))

    assert result.status is not CalculationStatus.FINAL


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="unknown seniority is computed as zero seniority and marked final",
)
def test_unknown_seniority_is_not_final() -> None:
    """Servizi postali appalto FISE, level 2, operaio, seniority not given.

    The CCNL grants seniority increments: 120 months add 56.66 EUR.  With
    ``seniority_months=None`` the engine pays 1,724.40 as for zero months,
    records no seniority decision and marks the result ``final``.
    """
    employment = Employment(
        ccnl_slug=_POSTAL_FISE,
        level_code="2",
        category=WorkerCategory.OPERAIO,
        seniority_months=None,
    )

    result = _january(employment)

    assert result.status is not CalculationStatus.FINAL


def _march(started_on: date) -> PeriodResult:
    """Return the March 2026 run of a C3 hired on ``started_on``.

    Returns:
        The regular run of March 2026.
    """
    employment = Employment(
        ccnl_slug=_METALMECCANICO,
        level_code="C3",
        employment_period=EmploymentPeriod(started_on=started_on),
    )
    year = _ENGINE.calculate_year(
        YearInput(year=2026, employment=employment, employer=_EMPLOYER)
    )
    (march,) = [
        result
        for result in year.period_results
        if result.run == PayrollRun.regular(2026, 3)
    ]
    return march


@pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="a month started on the 15th still exposes the full monthly pay",
)
def test_partial_hire_month_does_not_expose_full_month_pay() -> None:
    """Metalmeccanico C3 hired on 15 March 2026 against one hired on 1 March.

    Seventeen of the thirty-one days of March cannot be paid as a full
    month: the amount must be prorated by the CCNL rule or left
    undetermined.  Differential oracle: today both runs carry 2,158.26, the
    later one with a ``partial_month_not_prorated`` issue.
    """
    full_month = _march(date(2026, 3, 1))
    partial_month = _march(date(2026, 3, 15))

    assert partial_month.period_gross != full_month.period_gross
