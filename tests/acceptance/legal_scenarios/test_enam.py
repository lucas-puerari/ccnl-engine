"""Contribution of a teacher to the Gestione Assistenza Magistrale (ex ENAM).

L. 93/1957 art. 3 c. 1 lett. a: "un contributo mensile a carico degli
iscritti pari all'1 per cento dell'ammontare lordo dello stipendio", on
80% of it (INPS: "ENAM 1 -- 1"), for the permanent teachers of the scuola
dell'infanzia and primaria.

Docente infanzia e primaria, January 2026, 1724.65: base 80% = 1379.72,
1% = 13.7972 -> 13.80.  The stipendio should leave out the IIS conglobata,
which the bundle does not give apart: the run has the open limitation
``enam_base``.  The diplomato of the secondaria and a fixed term owe none.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine import Employment
from ccnl_engine.inputs import (
    FixedTerm,
    NaspiExclusion,
    NoPensionFund,
    Permanent,
    PublicEndOfService,
)
from tests.acceptance.legal_scenarios._support import regular_period
from tests.fixtures.current_year import employment_only
from tests.fixtures.seniority import new_hire

if TYPE_CHECKING:
    from ccnl_engine import PeriodResult

pytestmark = pytest.mark.legal_scenario

_ENAM_BASE = "istruzione-ricerca-aran/enam_base"


def _january(level: str, contract: Permanent | FixedTerm | None = None) -> PeriodResult:
    employment = Employment(
        ccnl_slug="istruzione-ricerca-aran.json",
        level_code=level,
        seniority=new_hire(),
        pension_fund=NoPensionFund(),
        contract_type=contract or Permanent(),
        public_end_of_service=PublicEndOfService.TFR_INPS,
    )
    return regular_period(employment=employment, current_year=employment_only())


def _enam(result: PeriodResult) -> Decimal | None:
    return {c.name: c.amount for c in result.contribution_breakdown.components}.get(
        "enam_employee"
    )


def test_permanent_teacher_of_infanzia_and_primaria() -> None:
    """13.80, with the open limitation of the base."""
    result = _january("DOCENTE_INFANZIA_PRIMARIA")
    assert _enam(result) == Decimal("13.80")
    assert _ENAM_BASE in {limitation.id for limitation in result.assurance.limitations}
    assert not result.is_payable


@pytest.mark.parametrize(
    ("level", "contract"),
    [
        ("DOCENTE_DIPLOMATO_SECONDARIA", Permanent()),
        (
            "DOCENTE_INFANZIA_PRIMARIA",
            FixedTerm(renewals=0, naspi_exclusion=NaspiExclusion.NONE),
        ),
    ],
    ids=["diplomato_secondaria", "fixed_term"],
)
def test_others_owe_none(level: str, contract: Permanent | FixedTerm) -> None:
    """Same minimum, no ENAM, no limitation."""
    result = _january(level, contract)
    assert _enam(result) is None
    assert _ENAM_BASE not in {
        limitation.id for limitation in result.assurance.limitations
    }
