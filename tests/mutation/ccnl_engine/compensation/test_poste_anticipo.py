"""The anticipo of the Poste renewal of 23 July 2024 (Allegato 10, p. 178).

"Le somme sopraindicate, maturate pro quota per ogni mese di servizio o
frazione di esso superiore a 15 giorni per il periodo dal 1 luglio 2024 al 31
agosto 2025, verranno corrisposte a titolo di anticipo [...] esclusivamente al
personale con contratto a tempo indeterminato in servizio alla data di
sottoscrizione del presente CCNL. L'erogazione [...] avverrà con le
competenze del mese di settembre 2024." Level C: 700,00.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from typing import TYPE_CHECKING, cast

import pytest

from ccnl_engine.catalog.loaders import load_ccnl
from ccnl_engine.compensation.una_tantum.rules import una_tantum_events
from ccnl_engine.inputs import EmploymentPeriod, FixedTerm, Permanent
from ccnl_engine.run.models import RunKind
from ccnl_engine.run.types import PeriodId

if TYPE_CHECKING:
    from ccnl_engine.period.requests import PeriodCalculationRequest

_POSTE = load_ccnl("poste-italiane-k700")


def _events(hired: date, contract: object) -> list[tuple[PeriodId | None, Decimal]]:
    request = cast(
        "PeriodCalculationRequest",
        SimpleNamespace(
            period_id=PeriodId(year=2024, month=9),
            payment_date=date(2024, 9, 27),
            level_code="C",
            employment_period=EmploymentPeriod(hired),
            weekly_hours=None,
            full_time_weekly_hours=None,
            contract_type=contract,
        ),
    )
    events, _ = una_tantum_events(request, _POSTE, RunKind.REGULAR)
    return [(e.reference_period, e.amount) for e in events]


@pytest.mark.parametrize("hired", [date(2020, 1, 1), date(2024, 7, 10)])
def test_a_permanent_worker_in_service_at_signature_takes_it_whole(
    hired: date,
) -> None:
    """The 14 months to August 2025, paid with September 2024 and taxed then."""
    assert _events(hired, Permanent()) == [(PeriodId(2024, 9), Decimal("700.00"))]


def test_a_hire_after_signature_takes_nothing() -> None:
    """Not in service on 23 July 2024."""
    assert _events(date(2024, 7, 24), Permanent()) == []


def test_a_fixed_term_worker_takes_nothing() -> None:
    """'esclusivamente al personale con contratto a tempo indeterminato'."""
    assert _events(date(2020, 1, 1), FixedTerm()) == []
