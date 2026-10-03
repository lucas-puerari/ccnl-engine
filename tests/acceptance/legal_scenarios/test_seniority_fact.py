"""Recognised seniority: unknown, zero, below, at and above the threshold.

Expected amounts are computed by hand from the CCNL tables, never read
from the engine.

Servizi Postali in Appalto FISE, CCNL text (bundled source
``ccnl-servizi-postali-versione-stampa-250624``, slp-cisl.it, Art. 35 and
tabella retributiva from 1 December 2025), level 2 in June 2026:

- base 1,650.74 + IND-INT 63.33 + EDR 10.33 = 1,724.40 without seniority;
- operai (Art. 35A): one increment of 56.66 after 24 months of service, at
  most one: 1,724.40 + 56.66 = 1,781.06;
- impiegati (Art. 35B): first increment after 48 months, then one every 24
  months, 62.62 each: one at 48 months, 1,787.02; two at 72 months,
  1,724.40 + 2 x 62.62 = 1,849.64.

Contoterzismo in agricoltura CAI-Agromec (bundled source: tabella
retributiva 2024-2027 published by redigo.info), level 6 operaio, June 2026:
base 1,466.56 from 1 June 2026, no seniority increment, a continuity premium
of 50.00 a month from 60 months of service: 1,516.56 at 60 months.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine import (
    BlockerCode,
    CalculationStatus,
    CompetenceYearPlan,
    Employment,
    EmploymentPeriod,
    PayrollRun,
    PeriodResult,
    SeniorityFact,
    SenioritySource,
    WorkerCategory,
)
from tests.acceptance.legal_scenarios._support import (
    EMPLOYER,
    ENGINE,
    PA_FUNZIONI_CENTRALI,
    POSTAL_FISE,
    regular_period,
)

pytestmark = pytest.mark.legal_scenario

_JUNE = date(2026, 6, 1)
_CONTOTERZISMO = "contoterzismo-caiagromec.json"
_FISE_L2 = Decimal("1724.40")


def _months(months: int) -> SeniorityFact:
    """Return ``months`` of recognised service on 1 June 2026.

    Returns:
        The fact, read from the employer records.
    """
    return SeniorityFact(months, _JUNE, SenioritySource.EMPLOYER_RECORDS)


def _june(employment: Employment) -> PeriodResult:
    return regular_period(employment=employment, month=6)


def _postal(category: WorkerCategory, seniority: SeniorityFact | None) -> PeriodResult:
    return _june(
        Employment(
            ccnl_slug=POSTAL_FISE,
            level_code="2",
            category=category,
            seniority=seniority,
        )
    )


def _seniority(result: PeriodResult) -> tuple[str, Decimal | None]:
    (decision,) = (d for d in result.decisions if d.capability == "seniority")
    return decision.reason_code, decision.amount


def _missing_seniority(result: PeriodResult) -> bool:
    return any(
        b.code is BlockerCode.MISSING_FACT and b.detail == "seniority"
        for b in result.blockers
    )


def test_unknown_seniority_is_not_paid_as_zero() -> None:
    """Operaio, level 2, seniority not given: the increment is undetermined.

    The run shows the pay without the increment, 1,724.40, as a simulation:
    the decision carries no amount and the result is not payable.
    """
    result = _postal(WorkerCategory.OPERAIO, None)

    assert _seniority(result) == ("required_fact_missing", None)
    assert _missing_seniority(result)
    assert result.assurance.calculation is CalculationStatus.INCOMPLETE
    assert result.is_payable is False
    assert result.period_gross == _FISE_L2
    (issue,) = (i for i in result.issues if i.fact == "seniority")
    assert issue.code == "seniority_unknown"


@pytest.mark.parametrize(
    ("category", "months", "reason", "increment"),
    [
        (WorkerCategory.OPERAIO, 0, "zero_confirmed", Decimal("0.00")),
        (WorkerCategory.OPERAIO, 23, "zero_confirmed", Decimal("0.00")),
        (WorkerCategory.OPERAIO, 24, "increments_applied", Decimal("56.66")),
        (WorkerCategory.OPERAIO, 25, "increments_applied", Decimal("56.66")),
        (WorkerCategory.OPERAIO, 120, "increments_applied", Decimal("56.66")),
        (WorkerCategory.IMPIEGATO, 47, "zero_confirmed", Decimal("0.00")),
        (WorkerCategory.IMPIEGATO, 48, "increments_applied", Decimal("62.62")),
        (WorkerCategory.IMPIEGATO, 49, "increments_applied", Decimal("62.62")),
        (WorkerCategory.IMPIEGATO, 71, "increments_applied", Decimal("62.62")),
        (WorkerCategory.IMPIEGATO, 72, "increments_applied", Decimal("125.24")),
    ],
    ids=str,
)
def test_known_seniority_around_each_threshold(
    category: WorkerCategory, months: int, reason: str, increment: Decimal
) -> None:
    """Known seniority below, at and above each increment threshold."""
    result = _postal(category, _months(months))

    assert _seniority(result) == (reason, increment)
    assert not _missing_seniority(result)
    assert result.period_gross == _FISE_L2 + increment


def test_seniority_ages_to_each_run_of_the_year() -> None:
    """Service recognised from 15 June 2024: 24 months on 15 June 2026.

    The June run counts the 23 months completed by 1 June; the increment
    is paid from July, when 24 months are complete on the first day.
    """
    employment = Employment(
        ccnl_slug=POSTAL_FISE,
        level_code="2",
        category=WorkerCategory.OPERAIO,
        seniority=SeniorityFact.since(date(2024, 6, 15), SenioritySource.PAYSLIP),
    )
    year = ENGINE.calculate_competence_year(
        CompetenceYearPlan(year=2026, employment=employment, employer=EMPLOYER)
    )
    gross = {
        result.run.month: result.period_gross
        for result in year.period_results
        if result.run in {PayrollRun.regular(2026, 6), PayrollRun.regular(2026, 7)}
    }

    assert gross == {6: _FISE_L2, 7: _FISE_L2 + Decimal("56.66")}


def test_seniority_from_a_mid_month_hire_counts_zero_in_the_hire_month() -> None:
    """Hired on 15 March 2026 with seniority recognised from that day.

    The March run counts zero months, not an error: the service starts
    within the month.  The operaio increment matures after 24 months, so no
    run of 2026 pays it.
    """
    employment = Employment(
        ccnl_slug=POSTAL_FISE,
        level_code="2",
        category=WorkerCategory.OPERAIO,
        employment_period=EmploymentPeriod(started_on=date(2026, 3, 15)),
        seniority=SeniorityFact.since(date(2026, 3, 15), SenioritySource.PAYSLIP),
    )
    year = ENGINE.calculate_competence_year(
        CompetenceYearPlan(year=2026, employment=employment, employer=EMPLOYER)
    )
    reasons = {
        (result.period_id.month, _seniority(result)[0])
        for result in year.period_results
        if result.run == PayrollRun.regular(2026, result.period_id.month)
    }

    assert reasons == {(month, "zero_confirmed") for month in range(3, 13)}


def test_contract_without_increments_needs_no_seniority() -> None:
    """Funzioni Centrali (ARAN) pays no seniority increment.

    The decision says the capability does not apply, and an unknown
    seniority is not a missing fact.
    """
    result = _june(Employment(ccnl_slug=PA_FUNZIONI_CENTRALI, level_code="FUNZIONARI"))

    assert _seniority(result) == ("not_applicable_by_contract", Decimal("0.00"))
    assert not _missing_seniority(result)
    assert all(i.fact != "seniority" for i in result.issues)


@pytest.mark.parametrize(
    ("seniority", "reason", "gross"),
    [
        (None, "required_fact_missing", Decimal("1466.56")),
        (_months(59), "not_applicable_by_contract", Decimal("1466.56")),
        (_months(60), "not_applicable_by_contract", Decimal("1516.56")),
    ],
    ids=["unknown", "59_months", "60_months"],
)
def test_allowance_gated_by_service_needs_the_seniority(
    seniority: SeniorityFact | None, reason: str, gross: Decimal
) -> None:
    """Contoterzismo level 6: no increment, but a premium from 60 months.

    Without the seniority the premium is undetermined: the run names the
    missing fact.  With it the premium follows the threshold.
    """
    result = _june(
        Employment(ccnl_slug=_CONTOTERZISMO, level_code="6", seniority=seniority)
    )

    assert _seniority(result)[0] == reason
    assert _missing_seniority(result) is (seniority is None)
    assert result.period_gross == gross
