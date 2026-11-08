"""Extra months of a worker paid by the fixed-term pay of the CCNL.

Operai agricoli, art. 52-53: "Per gli operai a tempo determinato la
tredicesima [quattordicesima] mensilità è compresa nella percentuale
relativa al terzo elemento": an extra-month run of an OTD is refused.
"""

from __future__ import annotations

from datetime import date

import pytest

from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.employer.inputs import EmployerProfile, Headcount
from ccnl_engine.employment.category.models import WorkerCategory
from ccnl_engine.employment.inputs import FixedTerm, Permanent
from ccnl_engine.employment.period.inputs import EmploymentPeriod
from ccnl_engine.errors import OutOfScopeError
from ccnl_engine.extra_month.services import run_accrual
from ccnl_engine.period.requests import PeriodCalculationRequest
from ccnl_engine.run.models import PayrollRun
from ccnl_engine.run.types import PeriodId
from tests.knowledge.ccnl_engine.seniority.builders import new_hire

_CCNL = load_ccnl("operai-agricoli-florovivaisti")
_RUN = PayrollRun.thirteenth(2026, 12)


def _request(
    contract: object, category: WorkerCategory | None, level: str = "Area2"
) -> PeriodCalculationRequest:
    return PeriodCalculationRequest(
        employer=EmployerProfile(headcount=Headcount(10)),
        period_id=PeriodId(year=2026, month=12),
        payment_date=date(2026, 12, 15),
        ccnl_id="operai-agricoli-florovivaisti",
        level_code=level,
        seniority=new_hire(),
        contract_type=contract,  # type: ignore[arg-type]
        category=category,
        run=_RUN,
        employment_period=EmploymentPeriod(date(2026, 1, 1), None),
    )


def test_the_thirteenth_of_an_otd_is_refused() -> None:
    """The error names the reason, the feature, the ruleset and the kind."""
    request = _request(FixedTerm(), WorkerCategory.OPERAIO)
    with pytest.raises(OutOfScopeError) as raised:
        run_accrual(request, _CCNL, date(2026, 12, 1))
    error = raised.value
    assert error.reason == "extra_month_in_percentage"
    assert error.feature == "base_salary"
    assert error.ruleset == "operai-agricoli-florovivaisti"
    assert str(error).startswith(
        "'operai-agricoli-florovivaisti' pays this worker's thirteenth in a percentage"
    )
    assert error.remediation == "Do not run the extra month: the hours already pay it."


@pytest.mark.parametrize(
    ("contract", "category"),
    [
        (Permanent(), WorkerCategory.OPERAIO),
        (FixedTerm(), WorkerCategory.IMPIEGATO),
        (FixedTerm(), None),
    ],
)
def test_other_workers_accrue_the_thirteenth(
    contract: object, category: WorkerCategory | None
) -> None:
    """An OTI, a fixed-term impiegato or an unstated category accrues it."""
    accrual = run_accrual(_request(contract, category), _CCNL, date(2026, 12, 1))
    assert accrual is not None
    assert accrual.accrued == 12


def test_the_category_of_the_level_counts() -> None:
    """A level that fixes the operai category needs no stated category."""
    level = _CCNL.levels[0].model_copy(update={"category": WorkerCategory.OPERAIO})
    ccnl = _CCNL.model_copy(update={"levels": (level, *_CCNL.levels[1:])})
    with pytest.raises(OutOfScopeError, match="in a percentage"):
        run_accrual(_request(FixedTerm(), None, level.code), ccnl, date(2026, 12, 1))
