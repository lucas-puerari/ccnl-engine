"""The injury integration of apprentices (Confesercenti art. 189, Sport art. 105).

"Per gli apprendisti le misure previste dai punti 2) e 3) del precedente
comma sono fissate rispettivamente nell'80% e nel 90%": the bands of
points 2) and 3) drop from 90% and 100% to 80% and 90%; the waiting days
of point 1) stay at 60%.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodFacts,
    PeriodInput,
)
from ccnl_engine.absence.insured.injury_models import InjuryIntegrationBand
from ccnl_engine.absence.insured.loaders import load_insured_absence_rates
from ccnl_engine.absence.insured.models import InjuryRules
from ccnl_engine.absence.insured.rules import MonthPay, injury_pay
from ccnl_engine.absence.models import DailyDivisorMethod
from ccnl_engine.calendar.holiday.loaders import load_national_holidays
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.compensation.element.types import MonthlyPayChain
from ccnl_engine.events import WorkInjuryEvent
from ccnl_engine.inputs import (
    Apprentice,
    EmploymentPeriod,
    NoPensionFund,
    Permanent,
    SeniorityFact,
    SenioritySource,
)
from ccnl_engine.sickness.holiday.rules import covered_target_holidays
from ccnl_engine.sickness.term.rules import DailyQuota

_PAY = MonthPay(
    chain=MonthlyPayChain(base=Decimal(3000), seniority=Decimal(0), allowances=()),
    quota=DailyQuota(DailyDivisorMethod.BY_30, Decimal(30)),
    extra_months=1,
    employee_rate=Decimal("0.0919"),
)
_HIRED = date(2025, 1, 1)


def _rules(name: str) -> InjuryRules:
    work = load_ccnl(name).work_rules
    assert work is not None
    assert work.insured_absence is not None
    rules = work.insured_absence.injury
    assert rules is not None
    return rules


@pytest.mark.parametrize("name", ["terziario-confesercenti", "impianti-sportivi-sport"])
def test_apprentice_month_uses_the_80_and_90_bands(name: str) -> None:
    """January injury of an apprentice: integration 422.13.

    Waiting days 2-4 pay 3*60 = 180; INAIL pays 27*60 = 1620 from day 5.
    The target is 16*80 + 10*90 = 2180 (January 31 is outside the BY_30
    quota); the net-basis INAIL offset is 1620 / .9081 = 1783.94, and the
    January 6 holiday adds 100 - (60 + 80 - 60/.9081) = 26.07:
    2180 - 1783.94 + 26.07 = 422.13, against 672.13 of a non-apprentice.
    """
    clause = _rules(name)
    apprentice = clause.for_worker(apprentice=True)
    assert [(b.day_from, b.rate) for b in apprentice.integration_bands] == [
        (4, Decimal("0.80")),
        (20, Decimal("0.90")),
    ]
    assert clause.for_worker(apprentice=False) is clause
    paid = injury_pay(
        date(2026, 1, 1),
        date(2026, 1, 31),
        date(2026, 1, 1),
        _PAY,
        Decimal(200),
        Decimal(40),
        load_insured_absence_rates().injury,
        apprentice,
        covered_target_holidays(clause.holiday, load_national_holidays(), 2026),
    )
    assert (paid.carenza, paid.indemnity, paid.integration) == (
        Decimal("180.00"),
        Decimal("1620.00"),
        Decimal("422.13"),
    )


def test_rules_without_apprentice_bands_keep_the_general_bands() -> None:
    """An apprentice of a clause without apprentice bands has the general ones."""
    clause = _rules("ced-assoced")
    assert clause.apprentice_bands == ()
    assert clause.for_worker(apprentice=True) is clause


def test_apprentice_bands_need_general_bands_in_day_order() -> None:
    """Apprentice bands replace general bands, and keep their day order."""
    provenance = _rules("terziario-confesercenti").provenance
    band = InjuryIntegrationBand(day_from=4, rate=Decimal("0.8"))
    late = InjuryIntegrationBand(day_from=20, rate=Decimal("0.9"))
    with pytest.raises(ValueError, match="replace integration bands"):
        InjuryRules(apprentice_bands=(band,), provenance=provenance)
    with pytest.raises(ValueError, match="day order"):
        InjuryRules(
            integration_bands=(band,),
            apprentice_bands=(late, band),
            provenance=provenance,
        )


def _intg(contract: Permanent | Apprentice) -> Decimal:
    result = PayrollEngine.bundled().calculate_period(
        PeriodInput(
            run=PayrollRun.regular(2026, 3),
            payment_date=date(2026, 3, 27),
            employment=Employment(
                ccnl_id="terziario-confesercenti",
                level_code="IV",
                contract_type=contract,
                employment_period=EmploymentPeriod(_HIRED, None),
                seniority=SeniorityFact.since(_HIRED, SenioritySource.EMPLOYER_RECORDS),
                pension_fund=NoPensionFund(),
            ),
            employer=EmployerProfile(headcount=Headcount(10)),
            facts=PeriodFacts(
                events=(WorkInjuryEvent(date(2026, 3, 2), date(2026, 3, 31)),)
            ),
        )
    )
    lines = {i.item_id.rsplit("_", 1)[-1]: i.amount for i in result.pay_items}
    return lines["intg"]


def test_the_run_selects_the_apprentice_bands() -> None:
    """The same March injury tops up an apprentice less than a permanent worker."""
    assert _intg(Apprentice(months_elapsed=6, track="standard")) < _intg(Permanent())
