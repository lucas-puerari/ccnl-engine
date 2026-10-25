"""Run the input packet of a validation packet through the engine.

The inputs of a packet are the facts of an observed payslip replay
(:data:`scripts.provenance.replay.check.INPUT_KEYS`), so the request is
built by the builder of the replay.  A scenario of one run computes that
run; ``annual_conguaglio`` and ``termination`` need the months before it,
so they compute the competence year and read the run the inputs name, and
so does any packet whose ``opening`` is ``zero_balances_at_january``: the
tax year opens with imported balances that carry nothing from the year
before (no INPS base of other employers, no recovery, no surtax
installment), and each run opens with the closing state of the one before.

The pilot packets are ``engine_provisional``: their values are what the
engine computes today, waiting for a payroll provider to compute the same
inputs.  They cover nothing, but they detect a change of the engine: run
this module to rewrite them after a change you meant::

    uv run python -m tests.knowledge.ccnl_engine.period.validation_packet.runner
"""

from __future__ import annotations

import json
from dataclasses import replace
from decimal import Decimal
from pathlib import Path
from typing import TYPE_CHECKING, Any, Final

from ccnl_engine import CompetenceYearPlan, PayrollEngine
from ccnl_engine.inputs import InpsBaseYtd, OpeningBalances
from tests.knowledge.ccnl_engine.period.services.test_observed_replay import (
    _READERS,
    _request,
)

if TYPE_CHECKING:
    from ccnl_engine import PeriodResult

__all__ = ["FOLDER", "READER_OF", "compute", "compute_result", "rewrite"]

FOLDER: Final = Path(__file__).parent
#: The replay reader of each total of the definition of done.
READER_OF: Final = {
    "base_salary": "base_salary",
    "gross": "period_gross",
    "employee_contributions": "employee_contributions",
    "employer_contributions": "employer_contributions",
    "tax": "period_tax",
    "net": "period_net",
    "tfr": "tfr_accrual",
    "employer_cost": "employer_cost",
}
_YEARLY: Final = frozenset({"annual_conguaglio", "termination"})
_ENGINE: Final = PayrollEngine.bundled()
_CENT: Final = Decimal("0.01")


def compute_result(inputs: dict[str, Any]) -> PeriodResult:
    """Return the run the inputs of a packet name, as the engine computes it.

    Returns:
        The result of the run.
    """
    facts = {k: v for k, v in inputs.items() if k != "scenario"}
    request = _request(facts)
    computed = inputs.get("opening") == "zero_balances_at_january"
    opening = (
        _ENGINE.import_opening_balances(
            OpeningBalances(
                tax_year=request.run.year,
                inps_bases=(InpsBaseYtd(request.run.year, Decimal(0), Decimal(0)),),
                recoveries=(),
                surtax_obligations=(),
            )
        )
        if computed
        else None
    )
    if inputs["scenario"] not in _YEARLY and not computed:
        return _ENGINE.calculate_period(request)
    year = _ENGINE.calculate_competence_year(
        CompetenceYearPlan(
            year=request.run.year,
            employment=request.employment,
            employer=request.employer,
            prior_year=request.prior_year,
            current_year=request.current_year,
            periods={request.run.run_id: request.facts},
            opening_state=opening,
            default_facts=replace(request.facts, events=()),
        )
    )
    return next(r for r in year.period_results if r.run == request.run)


def compute(inputs: dict[str, Any], outputs: list[str]) -> dict[str, Decimal]:
    """Return what the engine computes for each output of an input packet.

    Returns:
        The value of each output, rounded to the cent.
    """
    result = compute_result(inputs)
    return {
        output: _READERS[READER_OF[output]](result).quantize(_CENT)
        for output in outputs
    }


def rewrite(folder: Path = FOLDER) -> None:
    """Rewrite the values of every ``engine_provisional`` packet of ``folder``."""
    for path in sorted(folder.glob("*.json")):
        packet = json.loads(path.read_text(encoding="utf-8"))
        if packet["artifact"]["kind"] != "engine_provisional":
            continue
        names = [o["output"] for o in packet["outputs"]]
        values = compute(packet["inputs"], names)
        for output in packet["outputs"]:
            output["value"] = str(values[output["output"]])
        path.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    rewrite()
