"""A run of a year left out because its pay rules are not in force."""

from __future__ import annotations

from datetime import date

from ccnl_engine.payroll.domain.assurance import BlockerCode
from ccnl_engine.payroll.domain.payment import PaymentId
from ccnl_engine.payroll.domain.run import PayrollRunId, RunKind
from ccnl_engine.payroll.domain.uncovered_run import UncoveredRun
from ccnl_engine.shared.domain.errors import MissingRuleError

_PAYMENT = PaymentId(
    PayrollRunId(year=2026, month=1, kind=RunKind.REGULAR), date(2026, 1, 27)
)


def _error(remediation: str | None) -> MissingRuleError:
    return MissingRuleError(
        "the rule starts on 2026-03-01",
        as_of=date(2026, 1, 1),
        feature="base_salary",
        ruleset="anas",
        remediation=remediation,
    )


def test_the_blocker_names_the_run_and_the_rule() -> None:
    """The blocker is ``run_not_computed`` on the rule, detail the run id."""
    blocker = UncoveredRun(_PAYMENT, _error("compute from 2026-03-01")).blocker

    assert blocker.code is BlockerCode.RUN_NOT_COMPUTED
    assert blocker.feature == "base_salary"
    assert blocker.detail == "2026-01-regular"
    assert blocker.remediation == "compute from 2026-03-01"


def test_without_a_remediation_the_blocker_tells_why() -> None:
    """An error with no remediation explains the gap instead."""
    blocker = UncoveredRun(_PAYMENT, _error(None)).blocker

    assert blocker.remediation == "the rule starts on 2026-03-01"
