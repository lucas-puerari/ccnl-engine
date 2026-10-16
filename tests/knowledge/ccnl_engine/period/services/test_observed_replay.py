"""Observed payslips replayed through the public API of the engine.

Each record of ``observed_payslip/`` states in ``replay`` whether it can be
replayed:

- ``full``: the request states every fact the payslip rests on;
- ``partial``: some facts have no field in the request; ``unknown_inputs``
  names them and only the values they do not touch are compared;
- ``not_replayable``: ``reason`` says why (a period before the tax years of
  the bundle, a level not printed).

A replayable record builds its request from the observed facts alone
(``inputs``) and pins each value it compares in ``expected``, with the field
of the payslip it was read from and a tolerance.  A difference fails unless
``known_differences`` lists it with its reason, its owner and the date
until which it is accepted: a new divergence never passes silently, and an
accepted one expires.  The runner computes nothing itself; it reads the
result of :meth:`~ccnl_engine.PayrollEngine.calculate_period`.
"""

from __future__ import annotations

import json
from datetime import UTC, date, datetime
from decimal import Decimal
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest

from ccnl_engine import (
    EmployerProfile,
    Employment,
    Headcount,
    PayrollEngine,
    PayrollRun,
    PeriodInput,
)
from ccnl_engine.inputs import Permanent, WorkerCategory
from scripts.provenance.reference_case.check import AXES

if TYPE_CHECKING:
    from collections.abc import Callable

    from ccnl_engine import PeriodResult

_DIR = Path(__file__).resolve().parents[1] / "observed_payslip"
_RECORDS = {
    path.stem: json.loads(path.read_text("utf-8"))
    for path in sorted(_DIR.glob("*.json"))
}
_REPLAYABILITY = frozenset({"full", "partial", "not_replayable"})
_ENGINE = PayrollEngine.bundled()
#: Day the accepted differences are checked against.
_TODAY = datetime.now(tz=UTC).date()


def _items(kind: str) -> Callable[[PeriodResult], Decimal]:
    def read(result: PeriodResult) -> Decimal:
        return sum((i.amount for i in result.pay_items if i.kind == kind), Decimal(0))

    return read


def _employee_inps_rate(result: PeriodResult) -> Decimal:
    components = result.contribution_breakdown.components
    return sum((c.rate for c in components if c.name.endswith("_employee")), Decimal(0))


#: Each value a record can compare, its axis and how the result gives it.
_READERS: dict[str, tuple[str, Callable[[PeriodResult], Decimal]]] = {
    "base_salary": ("base_salary", _items("base_salary_earning")),
    "fixed_allowances": ("gross", _items("fixed_allowance_earning")),
    "employee_inps_rate": ("contributions", _employee_inps_rate),
}


def _replayable() -> list[str]:
    return [
        pid
        for pid, r in _RECORDS.items()
        if r["replay"]["replayability"] != "not_replayable"
    ]


def _run(inputs: dict[str, Any]) -> PeriodResult:
    year, month = int(inputs["year"]), int(inputs["month"])
    category = inputs.get("category")
    return _ENGINE.calculate_period(
        PeriodInput(
            run=PayrollRun.regular(year, month),
            payment_date=date(year, month, 27),
            employment=Employment(
                ccnl_slug=inputs["ccnl_slug"],
                level_code=inputs["level_code"],
                contract_type=Permanent(),
                category=None if category is None else WorkerCategory(category),
            ),
            employer=EmployerProfile(headcount=Headcount(int(inputs["headcount"]))),
        )
    )


@pytest.mark.parametrize("pid", sorted(_RECORDS))
def test_every_record_states_its_replayability(pid: str) -> None:
    """A record is replayable with inputs and expected values, or says why not."""
    replay = _RECORDS[pid]["replay"]

    assert replay["replayability"] in _REPLAYABILITY
    assert replay["reason"]
    if replay["replayability"] == "not_replayable":
        assert set(replay) == {"replayability", "reason"}
        return
    assert replay["inputs"]["contract_type"] == "permanent"
    if replay["replayability"] == "partial":
        assert replay["unknown_inputs"]
    assert replay["expected"]
    for key, value in replay["expected"].items():
        assert key in _READERS, key
        assert _READERS[key][0] in AXES
        assert {"value", "tolerance", "printed"} <= set(value)
    for known in replay["known_differences"]:
        assert known["key"] in replay["expected"]
        assert known["reason"]
        assert known["owner"]
        assert date.fromisoformat(known["accepted_until"]) >= _TODAY, known


@pytest.mark.parametrize("pid", _replayable())
def test_the_engine_reproduces_the_observed_values(pid: str) -> None:
    """Each compared value is within its tolerance, or a listed difference."""
    replay = _RECORDS[pid]["replay"]
    result = _run(replay["inputs"])
    known = {d["key"] for d in replay["known_differences"]}

    diff = {
        key: (_READERS[key][1](result), Decimal(spec["value"]))
        for key, spec in replay["expected"].items()
        if abs(_READERS[key][1](result) - Decimal(spec["value"]))
        > Decimal(spec["tolerance"])
    }

    assert set(diff) == known, diff


def test_the_replayable_records_cover_the_sectors_of_the_production_ccnls() -> None:
    """Terziario, industria and edilizia payslips of 2026 are replayed."""
    ccnls = {_RECORDS[pid]["replay"]["inputs"]["ccnl_slug"] for pid in _replayable()}

    assert len(_replayable()) >= 9
    assert ccnls == {
        "commercio-confcommercio.json",
        "edilizia-ance.json",
        "metalmeccanico-federmeccanica.json",
    }
