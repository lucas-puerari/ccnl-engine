"""Oracle cases of a competence year: the extra months paid in their own run.

Each case is verified against the computation chain; expected values are frozen
and must NOT be auto-updated from the engine.  A failing assertion means a
computation-affecting change was made without reviewing these oracle cases.

Source for values: hand-traced payroll computation chains and CCNL source data.
All monetary amounts in EUR.
"""

from __future__ import annotations

from decimal import Decimal

from ccnl_engine import (
    CompetenceYearPlan,
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
)
from tests.fixtures.seniority import new_hire

engine = PayrollEngine.bundled()


# ---------------------------------------------------------------------------
# Mensilità aggiuntive (area: tredicesima)
# ---------------------------------------------------------------------------


def test_tredicesima_commercio_level4() -> None:
    """Tredicesima for commercio level 4, computed via full-year run.

    The standard calendar is derived from the CCNL: tredicesima and
    quattordicesima, 14 runs.
    """
    yr = engine.calculate_competence_year(
        CompetenceYearPlan(
            year=2026,
            employment=Employment(
                ccnl_slug="commercio-confcommercio.json",
                level_code="4",
                seniority=new_hire(),
            ),
            employer=EmployerProfile(headcount=Headcount(50)),
        )
    )
    tredicesima = next(
        r
        for r in yr.period_results
        if r.run is not None and r.run.run_id == "2026-12-thirteenth"
    )
    assert tredicesima.period_gross == Decimal("1818.75")
    assert len(yr.period_results) == 14
