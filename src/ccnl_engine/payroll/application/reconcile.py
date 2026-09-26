"""Reconciliation invariants for PeriodResult.

Each invariant is a pure function that accepts a result (and, where needed,
the opening :class:`~ccnl_engine.payroll.domain.period.PeriodState` and the
:class:`RunFacts` of the run) and returns a list of
:class:`ReconciliationViolation` instances coded with an
:class:`InvariantCode`.

:func:`reconcile` runs all invariants and returns a
:class:`ReconciliationResult`; :func:`check_period` raises
``DataIntegrityError`` when one fails.  A violation is an engine error: a
caller input that cannot produce a payslip is rejected with
``InvalidInputError`` before reconciliation.

Invariants, by module:

- ``ledger_invariants``: ``pay_item_posted``,
  ``earning_contribution_exclusive``, ``net_identity``,
  ``irpef_withheld_continuity``, ``employer_cost_identity``,
  ``gross_identity``, ``ledger_entry_unique``.
- ``sign_invariants``: ``gross_non_negative``,
  ``employee_deduction_non_negative``, ``substitute_tax_non_negative``,
  ``ordinary_tax_non_negative``, ``employee_contribution_non_negative``,
  ``employer_contribution_non_negative``, ``net_pay_non_negative``.
- ``state_invariants``: ``run_counters_advance``, ``ytd_continuity``,
  ``credit_recovery_bounds``, ``carried_recovery_advance``.
- ``decision_invariants``: ``substitute_tax_plafond``,
  ``substitute_tax_eligibility``, ``decision_provenance``.
- ``lifecycle_invariants``: ``run_within_employment``,
  ``extra_month_accrual_limit``.
- ``withholding_invariants``: ``contribution_ceiling``,
  ``irpef_annual_reconciliation``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ccnl_engine.engine.errors import DataIntegrityError
from ccnl_engine.payroll.application._reconcile_types import (
    InvariantCode,
    ReconciliationViolation,
    RunFacts,
)
from ccnl_engine.payroll.application.decision_invariants import (
    check_decision_provenance,
    check_substitute_tax_eligibility,
    check_substitute_tax_plafond,
)
from ccnl_engine.payroll.application.ledger_invariants import (
    check_earning_contribution_exclusive,
    check_employer_cost_identity,
    check_gross_identity,
    check_irpef_withheld_continuity,
    check_ledger_entry_unique,
    check_net_identity,
    check_pay_item_posted,
)
from ccnl_engine.payroll.application.lifecycle_invariants import (
    check_extra_month_accrual_limit,
    check_run_within_employment,
)
from ccnl_engine.payroll.application.sign_invariants import check_signs
from ccnl_engine.payroll.application.state_invariants import (
    check_carried_recovery_advance,
    check_credit_recovery_bounds,
    check_run_counters,
    check_ytd_continuity,
)
from ccnl_engine.payroll.application.withholding_invariants import (
    check_contribution_ceiling,
    check_irpef_annual_reconciliation,
)

if TYPE_CHECKING:
    from ccnl_engine.payroll.domain.period import (
        PeriodResult,
        PeriodState,
    )

__all__ = [
    "InvariantCode",
    "ReconciliationResult",
    "ReconciliationViolation",
    "RunFacts",
    "check_period",
    "reconcile",
]


@dataclass(frozen=True)
class ReconciliationResult:
    """Outcome of running all reconciliation invariants on one result.

    Attributes:
        violations: Tuple of :class:`ReconciliationViolation` instances,
            empty when every invariant passes.
    """

    violations: tuple[ReconciliationViolation, ...]

    @property
    def ok(self) -> bool:
        """``True`` when no invariant was violated.

        Returns:
            ``True`` if :attr:`violations` is empty.
        """
        return len(self.violations) == 0


def reconcile(
    result: PeriodResult,
    opening: PeriodState,
    facts: RunFacts | None = None,
) -> ReconciliationResult:
    """Run all reconciliation invariants on *result* and return findings.

    Args:
        result: The completed period calculation result to verify.
        opening: The state that was passed into the calculation.
        facts: Facts of the run the result does not carry.  ``None`` skips
            the checks that need them (employment, massimale, PdR limit,
            ratei, projected taxable income).

    Returns:
        A :class:`ReconciliationResult` whose :attr:`~ReconciliationResult.ok`
        property is ``True`` when every invariant passes.
    """
    run_facts = facts if facts is not None else RunFacts()
    violations: list[ReconciliationViolation] = []
    violations.extend(check_pay_item_posted(result))
    violations.extend(check_earning_contribution_exclusive(result))
    violations.extend(check_net_identity(result))
    violations.extend(check_irpef_withheld_continuity(result, opening))
    violations.extend(check_employer_cost_identity(result))
    violations.extend(check_gross_identity(result))
    violations.extend(check_ledger_entry_unique(result))
    violations.extend(check_signs(result))
    violations.extend(check_run_counters(result, opening))
    violations.extend(check_ytd_continuity(result, opening))
    violations.extend(check_credit_recovery_bounds(result))
    violations.extend(check_carried_recovery_advance(result, opening))
    violations.extend(check_substitute_tax_plafond(result, opening, run_facts))
    violations.extend(check_substitute_tax_eligibility(result))
    violations.extend(check_decision_provenance(result))
    violations.extend(check_run_within_employment(result, run_facts))
    violations.extend(check_extra_month_accrual_limit(run_facts))
    violations.extend(check_contribution_ceiling(result, opening, run_facts))
    violations.extend(check_irpef_annual_reconciliation(result, opening, run_facts))
    return ReconciliationResult(violations=tuple(violations))


def check_period(
    result: PeriodResult,
    opening: PeriodState,
    facts: RunFacts,
) -> None:
    """Raise when ``result`` breaks a reconciliation invariant.

    Raises:
        DataIntegrityError: When :func:`reconcile` reports a violation; the
            message lists each one as ``[code] message``.
    """
    rec = reconcile(result, opening, facts)
    if not rec.ok:
        msgs = "; ".join(f"[{v.invariant_id}] {v.message}" for v in rec.violations)
        msg = f"Period reconciliation failed: {msgs}"
        raise DataIntegrityError(msg)
