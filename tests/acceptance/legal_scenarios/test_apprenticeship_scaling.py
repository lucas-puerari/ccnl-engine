"""Percentage apprentices: only the components the CCNL lists are reduced.

Each scenario is a regular run of March 2026 for an apprentice at month 0 of
a percentage track.  The expected gross is computed by hand: the percentage
of the track times the minimo and each allowance flagged
``apprenticeship_pct_relevant``, each rounded to the cent (ROUND_HALF_UP),
plus the other allowances at full value.  No seniority is declared.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine import Employment
from ccnl_engine.inputs import Apprentice
from tests.acceptance.legal_scenarios._support import COMMERCIO, regular_period

if TYPE_CHECKING:
    from ccnl_engine import PeriodResult
    from ccnl_engine.results import CalculationDecision

pytestmark = pytest.mark.legal_scenario

_D = Decimal
_RUN_TAG = "_2026-03-regular"


def _apprentice_run(slug: str, level: str, track: str | None = None) -> PeriodResult:
    return regular_period(
        month=3,
        employment=Employment(
            ccnl_slug=slug,
            level_code=level,
            contract_type=Apprentice(months_elapsed=0, track=track),
        ),
    )


def _allowances(result: PeriodResult) -> dict[str, Decimal]:
    """Return the fixed allowance lines by code, read from their item ids.

    Returns:
        Mapping of allowance code to the amount paid in the run.
    """
    return {
        item.item_id.removeprefix("allowance_").removesuffix(_RUN_TAG): item.amount
        for item in result.pay_items
        if item.kind == "fixed_allowance_earning"
    }


def _base_salary(result: PeriodResult) -> Decimal:
    (item,) = (i for i in result.pay_items if i.kind == "base_salary_earning")
    return item.amount


def _scaling(result: PeriodResult) -> CalculationDecision:
    (decision,) = (
        d for d in result.decisions if d.capability == "apprenticeship_scaling"
    )
    return decision


def test_trasporto_aereo_pays_edr_in_full() -> None:
    """Trasporto Aereo (Gestori Aeroportuali) level 4, 36-month track, month 0.

    Source: CCNL Parte Specifica Gestori Aeroportuali of 4 June 2025.
    Art. G14 c. 16 applies the percentage to "minimi tabellari in vigore,
    indennità di contingenza"; the EDR is not listed and Art. G22 c. 1
    grants it to apprentices, so it is paid in full.

    Steps (level 4, March 2026):

    1. Percentage, 36-month column, 1st semester: 75%.
    2. Minimo from 1 July 2025 (Art. G20 c. 5): 1307.47 x 0.75 = 980.6025,
       rounded 980.60.
    3. Contingenza (Art. G21 c. 2): 522.19 x 0.75 = 391.6425, rounded 391.64.
    4. EDR (Art. G22 c. 2): 41.85, not reduced.
    5. Gross: 980.60 + 391.64 + 41.85 = 1414.09.
    """
    result = _apprentice_run(
        "trasporto-aereo-assaeroporti.json", "4", "professionalizzante_36m"
    )

    assert _base_salary(result) == _D("980.60")
    assert _allowances(result) == {"CONTINGENZA": _D("391.64"), "EDR": _D("41.85")}
    assert result.period_gross == _D("1414.09")
    decision = _scaling(result)
    assert decision.inputs["percentage"] == _D("0.75")
    assert decision.inputs["scaled"] == "base_salary,CONTINGENZA"
    assert decision.inputs["unscaled"] == "EDR"


def test_energia_petrolio_pays_edr_and_funzione_in_full() -> None:
    """Energia e Petrolio level 4-2, track ``livello_4``, month 0.

    The bundled CCNL applies the percentage to "minimo tabellare e relativo
    CREA"; the EDR IPCA and the indennità di funzione are paid in full.

    Steps (level 4-2, March 2026, bundled salary table):

    1. Percentage, first 12 months: 90%.
    2. Minimo from 1 January 2026: 2596.61 x 0.90 = 2336.949, rounded
       2336.95.
    3. EDR IPCA from 1 January 2026: 51.00, not reduced.
    4. Indennità di funzione, second step: 106.79, not reduced.
    5. Gross: 2336.95 + 51.00 + 106.79 = 2494.74.
    """
    result = _apprentice_run("energia-petrolio-confindustria.json", "4-2")

    assert _base_salary(result) == _D("2336.95")
    assert _allowances(result) == {
        "EDR_IPCA": _D("51.00"),
        "INDENNITA_FUNZIONE": _D("106.79"),
    }
    assert result.period_gross == _D("2494.74")
    decision = _scaling(result)
    assert decision.inputs["scaled"] == "base_salary"
    assert decision.inputs["unscaled"] == "EDR_IPCA,INDENNITA_FUNZIONE"


def test_igiene_ambientale_pays_edr_and_integrativa_in_full() -> None:
    """Igiene Ambientale (Utilitalia) level D1, track ``30m-80-90``, month 0.

    The bundled CCNL records Art. 14 punto 8: the indennità integrativa of
    Art. 32 is paid in full from the first training period.  Art. 14 does
    not cite the EDR: its full value rests on the bundled flag, not on a
    text checked here.

    Steps (level D1, March 2026, bundled salary table):

    1. Percentage, first 15 months: 80%.
    2. Minimo from 1 February 2026: 1807.21 x 0.80 = 1445.768, rounded
       1445.77.
    3. EDR: 10.33, not reduced.
    4. Indennità integrativa: 50.00, not reduced.
    5. Gross: 1445.77 + 10.33 + 50.00 = 1506.10.
    """
    result = _apprentice_run("igiene-ambientale-utilitalia.json", "D1")

    assert _base_salary(result) == _D("1445.77")
    assert _allowances(result) == {"EDR": _D("10.33"), "INDEMN_INT": _D("50.00")}
    assert result.period_gross == _D("1506.10")
    assert _scaling(result).inputs["unscaled"] == "EDR,INDEMN_INT"


def test_under_classification_track_records_no_scaling() -> None:
    """Commercio level 4 apprentice: under-classification, no percentage.

    The apprentice is paid at a lower level, so no percentage is applied
    and no scaling decision is recorded.
    """
    result = _apprentice_run(COMMERCIO, "4")

    assert not [d for d in result.decisions if d.capability == "apprenticeship_scaling"]
