"""Envelope-level helpers: reproduce a Calculation from its stored snapshot."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ccnl_engine.engine.payroll.service.pipeline import compute
from ccnl_engine.version import __version__ as _current_engine_version

if TYPE_CHECKING:
    from ccnl_engine.engine.payroll.domain.calculation import Calculation


def reproduce(
    calculation: Calculation,
    *,
    allow_version_drift: bool = False,
) -> Calculation:
    """Replay *calculation* using the scenario stored in its input snapshot.

    The :class:`~ccnl_engine.engine.payroll.domain.scenario.PayrollScenario`
    is rebuilt from the snapshot and passed back through
    :func:`~ccnl_engine.engine.payroll.service.orchestrator.compute`, which
    re-loads the rulesets from the currently installed knowledge base. The
    returned :class:`~ccnl_engine.engine.payroll.domain.calculation.Calculation`
    will carry the same inputs and an identical ``result`` when the knowledge
    base has not changed.

    Args:
        calculation: The calculation to replay.
        allow_version_drift: When ``True``, proceed even if the engine version
            or ruleset identities differ from those recorded in *calculation*;
            the divergence is recorded in the returned
            :class:`~ccnl_engine.engine.payroll.domain.calculation.Calculation`
            but no error is raised. Defaults to ``False``.

    Returns:
        A new :class:`~ccnl_engine.engine.payroll.domain.calculation.Calculation`
        equal to the original when no drift has occurred.

    Raises:
        ValueError: When *allow_version_drift* is ``False`` and either the
            installed engine version or any ruleset identity does not match
            the values recorded in *calculation*.
    """
    scenario = calculation.input_snapshot.materialise()
    new_calc = compute(scenario)

    drift: list[str] = []
    if calculation.engine_version != _current_engine_version:
        drift.append(
            f"engine_version: recorded={calculation.engine_version!r}, "
            f"current={_current_engine_version!r}"
        )
    for key, recorded_ver in calculation.ruleset_version.items():
        current_ver = new_calc.ruleset_version.get(key)
        if current_ver != recorded_ver:
            drift.append(
                f"ruleset {key!r}: recorded={recorded_ver!r}, current={current_ver!r}"
            )
    drift.extend(
        f"ruleset {key!r}: recorded=<absent>, current={new_calc.ruleset_version[key]!r}"
        for key in new_calc.ruleset_version
        if key not in calculation.ruleset_version
    )

    if drift and not allow_version_drift:
        lines = "\n  ".join(drift)
        msg = (
            "reproduce() detected version drift; pass "
            "allow_version_drift=True to proceed:\n  " + lines
        )
        raise ValueError(msg)

    return new_calc
