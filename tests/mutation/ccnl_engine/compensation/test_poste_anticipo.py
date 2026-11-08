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


@pytest.mark.parametrize(
    ("hired", "vacanza"),
    [(date(2020, 1, 1), True), (date(2024, 7, 10), False)],
)
def test_a_permanent_worker_in_service_at_signature_takes_it_whole(
    hired: date, vacanza: bool
) -> None:
    """The 14-month anticipo is EUR 700; only first-semester service earns arrears."""
    expected = [(PeriodId(2024, 9), Decimal("700.00"))]
    if vacanza:
        expected.append((PeriodId(2024, 6), Decimal("150.00")))
    assert _events(hired, Permanent()) == expected


def test_vacanza_full_semester_pays_six_twelfths() -> None:
    """Level C: EUR 300 / 12 * 6 = 150, plus EUR 700 anticipo = 850."""
    assert _events(date(2020, 1, 1), Permanent()) == [
        (PeriodId(2024, 9), Decimal("700.00")),
        (PeriodId(2024, 6), Decimal("150.00")),
    ]


def test_vacanza_mid_semester_hire_pays_qualifying_months() -> None:
    """Hired 10 April: April-June = 3 months, 300 / 12 * 3 = 75; total 775."""
    assert _events(date(2024, 4, 10), Permanent()) == [
        (PeriodId(2024, 9), Decimal("700.00")),
        (PeriodId(2024, 6), Decimal("75.00")),
    ]


def test_a_hire_after_signature_takes_nothing() -> None:
    """Not in service on 23 July 2024."""
    assert _events(date(2024, 7, 24), Permanent()) == []


def test_a_fixed_term_worker_takes_nothing() -> None:
    """'esclusivamente al personale con contratto a tempo indeterminato'."""
    assert _events(date(2020, 1, 1), FixedTerm()) == []
