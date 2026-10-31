"""Sickness of the operai agricoli: INPS pays the fixed-term ones directly.

INPS, Indennità di malattia (scheda informativa): "è previsto il pagamento
diretto da parte dell'INPS (operai agricoli a tempo determinato, ...)".
The same episode, 2-13 March 2026, is deducted alike; the employer
advances the INPS share of the open-ended operaio only.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodFacts,
    PeriodInput,
)
from ccnl_engine.events import SicknessEpisode
from ccnl_engine.inputs import (
    EmploymentPeriod,
    FixedTerm,
    NoPensionFund,
    Permanent,
    SeniorityFact,
    SenioritySource,
    WorkerCategory,
)

if TYPE_CHECKING:
    from ccnl_engine.decision.models import CalculationDecision
    from ccnl_engine.period.results import PeriodResult

_HIRED = date(2026, 1, 1)


def _run(contract: FixedTerm | Permanent) -> PeriodResult:
    return PayrollEngine.bundled().calculate_period(
        PeriodInput(
            run=PayrollRun.regular(2026, 3),
            payment_date=date(2026, 3, 27),
            employment=Employment(
                ccnl_id="operai-agricoli-florovivaisti",
                level_code="Area1",
                category=WorkerCategory.OPERAIO,
                contract_type=contract,
                employment_period=EmploymentPeriod(_HIRED, None),
                seniority=SeniorityFact.since(_HIRED, SenioritySource.EMPLOYER_RECORDS),
                pension_fund=NoPensionFund(),
                tfr_treasury_fund=False,
            ),
            employer=EmployerProfile(headcount=Headcount(20)),
            facts=PeriodFacts(
                events=(SicknessEpisode("e1", date(2026, 3, 2), date(2026, 3, 13)),)
            ),
        )
    )


def _sickness(result: PeriodResult) -> CalculationDecision:
    return next(d for d in result.decisions if d.capability == "sickness")


def test_inps_pays_the_fixed_term_operaio_directly() -> None:
    """Nothing advanced, the days of D.L. 463/1983 art. 5 not asked."""
    fixed, open_ended = _run(FixedTerm()), _run(Permanent())
    issues = {i.code for i in fixed.issues}

    assert _sickness(fixed).inputs["inps_indemnity"] == Decimal(0)
    advanced = _sickness(open_ended).inputs["inps_indemnity"]
    assert isinstance(advanced, Decimal)
    assert advanced > 0
    assert _sickness(fixed).inputs["absence"] == _sickness(open_ended).inputs["absence"]
    assert "sickness_fixed_term_prior_work_unknown" not in issues
    assert "sickness_agricultural_fixed_term_days" in {
        lim.id for lim in fixed.limitations
    }
    assert "sickness_agricultural_fixed_term_days" not in {
        lim.id for lim in open_ended.limitations
    }
