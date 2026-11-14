"""Unionalimentari panificazione industriale: the pay of the sector's levels.

"Il trattamento economico dei lavoratori dipendenti da panifici ad indirizzo
produttivo industriale comprende: a) paga base; b) indennità di contingenza
al 1.11.1991; c) premio di produzione nazionale; d) scatti di anzianità"
(text signed 18 March 2026, art. 47 and 47 bis, PDF p. 144-145), with the
premio per obiettivi of the sector paid by a firm without one.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.balance.models import PeriodState
from ccnl_engine.employer.inputs import EmployerProfile, Headcount
from ccnl_engine.inputs import SeniorityFact, SenioritySource
from ccnl_engine.period.requests import PeriodCalculationRequest
from ccnl_engine.period.services import (
    bundled_policies,
    bundled_repository,
    calculate_period,
)
from ccnl_engine.regime.models import EmploymentSector
from ccnl_engine.run.types import PeriodId

if TYPE_CHECKING:
    from ccnl_engine.period.results import PeriodResult


def _run(seniority: SeniorityFact | None = None) -> PeriodResult:
    return calculate_period(
        PeriodCalculationRequest(
            employer=EmployerProfile(
                headcount=Headcount(20),
                subsector="panificazione_industriale",
                second_level_premium=False,
            ),
            period_id=PeriodId(2026, 3),
            payment_date=date(2026, 3, 27),
            ccnl_id="alimentari-pmi-unionalimentari",
            level_code="P3B",
            opening_state=PeriodState.zero(),
            events=(),
            sector=EmploymentSector.PRIVATE,
            seniority=seniority,
        ),
        repo=bundled_repository(),
        resolver=bundled_policies(),
    )


def _items(result: PeriodResult) -> dict[str, Decimal]:
    return {
        i.item_id.removesuffix("_2026-03-regular"): i.amount for i in result.pay_items
    }


def test_a_3b_baker_is_paid_the_sector_elements() -> None:
    """Paga base, contingenza, premio di produzione and premio per obiettivi."""
    items = _items(_run())
    assert items["base_salary"] == Decimal("1476.40")
    assert items["allowance_CONTINGENZA"] == Decimal("522.81")
    assert items["allowance_PREMIO_PRODUZIONE"] == Decimal("28.04")
    assert items["allowance_PREMIO_OBIETTIVI_PANIFICAZIONE"] == Decimal("19.84")


def test_the_premi_stay_out_of_the_tfr() -> None:
    """Art. 59 lists the TFR elements: paga base and contingenza only here."""
    items = _items(_run())
    base = Decimal("1476.40") + Decimal("522.81")
    gross = base + Decimal("28.04") + Decimal("19.84")
    expected = (base / Decimal("13.5") - gross * Decimal("0.005")).quantize(
        Decimal("0.01")
    )
    assert items["tfr"] == expected


def test_scatti_take_the_frozen_sector_amount() -> None:
    """Two bienni at the 3B amount frozen on 1 August 1997, EUR 27.24."""
    seniority = SeniorityFact(48, date(2026, 3, 1), SenioritySource.PAYSLIP)
    items = _items(_run(seniority))
    assert sum(v for k, v in items.items() if "seniority" in k) == Decimal("54.48")
