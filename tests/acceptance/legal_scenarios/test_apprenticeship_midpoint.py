"""Under-classification midpoint: the mean of the whole pay of two levels.

CCNL Aziende Termali Federterme 2024-2027, Art. 13 lett. g: an apprentice
destined to level 5 is paid level 6 for the first half of the training and
then "il trattamento economico sarà maggiorato di un importo pari al 50% del
differenziale previsto tra il 5° e il 6° livello".

Regular run of March 2026 (tranche from 2025-12-01, Art. 82-83), track
``L5-terme-18m`` at month 12, no matured seniority:

- level 6: minimo 825.28 + contingenza 510.89 + EDR 10.33 = 1346.50;
- level 5: minimo 940.47 + contingenza 513.32 + EDR 10.33 = 1464.12;
- pay: 1346.50 + 50% x 117.62 = 1346.50 + 58.81 = 1405.31.

Split by component: contingenza (510.89 + 513.32) / 2 = 512.105, rounded
half up to 512.11; EDR 10.33; the minimo takes the rest,
1405.31 - 512.11 - 10.33 = 882.87.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

from ccnl_engine import Employment
from ccnl_engine.inputs import Apprentice
from tests.acceptance.legal_scenarios._support import regular_period
from tests.fixtures.seniority import new_hire

if TYPE_CHECKING:
    from ccnl_engine import PeriodResult

pytestmark = pytest.mark.legal_scenario

_D = Decimal
_RUN_TAG = "_2026-03-regular"


def _run(months_elapsed: int) -> PeriodResult:
    return regular_period(
        month=3,
        employment=Employment(
            ccnl_slug="aziende-termali-federterme.json",
            level_code="5",
            contract_type=Apprentice(months_elapsed=months_elapsed),
            seniority=new_hire(),
        ),
    )


def _lines(result: PeriodResult) -> dict[str, Decimal]:
    lines = {
        item.item_id.removeprefix("allowance_").removesuffix(_RUN_TAG): item.amount
        for item in result.pay_items
        if item.kind == "fixed_allowance_earning"
    }
    (base,) = (i for i in result.pay_items if i.kind == "base_salary_earning")
    return {"base_salary": base.amount, **lines}


def test_midpoint_averages_every_component() -> None:
    """Minimo, contingenza and EDR add up to the CCNL midpoint, 1405.31."""
    lines = _lines(_run(12))
    assert lines == {
        "base_salary": _D("882.87"),
        "CONTINGENZA": _D("512.11"),
        "EDR": _D("10.33"),
    }
    assert sum(lines.values()) == _D("1405.31")


def test_first_half_pays_the_lower_level() -> None:
    """Before month 9 the apprentice is paid level 6 in full: 1346.50."""
    assert _lines(_run(0)) == {
        "base_salary": _D("825.28"),
        "CONTINGENZA": _D("510.89"),
        "EDR": _D("10.33"),
    }


def test_sourced_midpoint_records_no_open_limitation() -> None:
    """The Federterme clause states the components: no midpoint limitation."""
    ids = {lim.id for lim in _run(12).assurance.limitations if lim.blocks}
    assert not any(i.startswith("apprentice") for i in ids)
    assert "aziende-termali-federterme/apprenticeship_midpoint_components" not in ids
