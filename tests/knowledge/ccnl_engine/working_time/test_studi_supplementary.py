"""The lavoro supplementare of the Studi professionali (Art. 42 c. 3).

"Le ore di lavoro supplementare verranno retribuite con la quota oraria
della retribuzione di fatto e la maggiorazione forfetaria convenzionalmente
determinata nella misura del 40%".
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from ccnl_engine.balance.models import PeriodState
from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.employer.inputs import EmployerProfile, Headcount
from ccnl_engine.event.facade import OvertimeEvent
from ccnl_engine.ledger.models import AccountKind
from ccnl_engine.period.requests import PeriodCalculationRequest
from ccnl_engine.period.results import PeriodResult
from ccnl_engine.period.services import (
    bundled_policies,
    bundled_repository,
    calculate_period,
)
from ccnl_engine.run.types import PeriodId
from ccnl_engine.working_time.inputs import OvertimeKind
from ccnl_engine.working_time.models import WorkKind

_SUPPL = OvertimeKind.SUPPLEMENTARY


def _tfr(events: tuple[OvertimeEvent, ...]) -> Decimal:
    result = calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(headcount=Headcount(10)),
            period_id=PeriodId(year=2026, month=3),
            payment_date=date(2026, 3, 27),
            ccnl_id="studi-professionali-confprofessioni",
            level_code="4",
            opening_state=PeriodState.zero(),
            roles=frozenset(),
            events=events,
        ),
        repo=bundled_repository(),
        resolver=bundled_policies(),
    )
    assert isinstance(result, PeriodResult)
    return sum(
        (
            e.amount
            for e in result.ledger_entries
            if e.account is AccountKind.TFR_ACCRUAL
        ),
        Decimal(0),
    )


def test_the_supplementary_hours_take_40_percent() -> None:
    """One band for the part-time supplementary hours, from the 2024 text."""
    work = load_ccnl("studi-professionali-confprofessioni").work_rules
    assert work is not None
    assert work.time_supplements is not None
    (band,) = [
        b
        for b in work.time_supplements.overtime_bands
        if WorkKind.SUPPLEMENTARE in b.applies_to_kinds
    ]

    assert band.rate.value_at(date(2024, 3, 1)) == Decimal("0.40")


def test_the_supplementary_pay_stays_out_of_the_tfr_base() -> None:
    """Art. 42 c. 4: no deferred pay, 'compreso il Trattamento di fine rapporto'.

    The accrual only falls by the 0.50% withheld on the larger INPS base.
    """
    plain = _tfr(())
    with_hours = _tfr((OvertimeEvent(date(2026, 3, 10), Decimal(4), kind=_SUPPL),))

    assert with_hours <= plain


def test_sanita_privata_pays_the_supplementary_hours_15_percent() -> None:
    """Art. 22 (CCNL 8 October 2020, p. 25): 'una maggiorazione pari al 15%'."""
    work = load_ccnl("sanita-privata-aiop-aris").work_rules
    assert work is not None
    assert work.time_supplements is not None
    (band,) = [
        b
        for b in work.time_supplements.overtime_bands
        if WorkKind.SUPPLEMENTARE in b.applies_to_kinds
    ]

    assert band.rate.value_at(date(2026, 3, 1)) == Decimal("0.15")
