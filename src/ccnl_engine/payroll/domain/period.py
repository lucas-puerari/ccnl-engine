"""Domain types for the period-first payroll engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.engine.payroll.domain.employment import Permanent

if TYPE_CHECKING:
    from datetime import date

    from ccnl_engine.engine.capability_catalog import CapabilityReport
    from ccnl_engine.engine.payroll.domain.employment import Apprentice, FixedTerm
    from ccnl_engine.engine.payroll.domain.family import FamilyComposition
    from ccnl_engine.engine.payroll.domain.ledger import LedgerEntry
    from ccnl_engine.engine.payroll.domain.pay_items import PayItem
    from ccnl_engine.engine.payroll.domain.period_payroll import PeriodId
    from ccnl_engine.payroll.domain.benefit import BenefitBreakdown
    from ccnl_engine.payroll.domain.contributions import ContributionBreakdown
    from ccnl_engine.payroll.domain.events import WorkEvent
    from ccnl_engine.payroll.domain.tax import TaxComputation

_ZERO = Decimal(0)


@dataclass(frozen=True)
class PeriodState:
    """Minimal YTD state entering a period-first payroll calculation.

    Pass :meth:`zero` for January (no prior periods closed this tax year).

    Attributes:
        months_closed: Number of payroll periods already closed this tax
            year before this calculation runs.
        irpef_withheld_ytd: IRPEF already withheld this tax year.
        inps_employee_ytd: Employee INPS contributions withheld YTD.
        gross_ytd: Gross earnings accumulated YTD.
        inps_base_ytd: Total INPS contribution base accumulated YTD.
            Used to enforce the IVS massimale ceiling across periods.
        taxable_ytd: Total IRPEF taxable income accumulated YTD.
        fringe_ytd: Total fringe benefit value accumulated YTD.
            Used to enforce the annual Art. 51 c. 3 TUIR threshold.
        fringe_taxed_ytd: Cumulative fringe base already subject to IRPEF/INPS
            this tax year.  Updated retroactively when the threshold is crossed.
    """

    months_closed: int = 0
    irpef_withheld_ytd: Decimal = _ZERO
    inps_employee_ytd: Decimal = _ZERO
    gross_ytd: Decimal = _ZERO
    inps_base_ytd: Decimal = _ZERO
    taxable_ytd: Decimal = _ZERO
    fringe_ytd: Decimal = _ZERO
    fringe_taxed_ytd: Decimal = _ZERO

    @classmethod
    def zero(cls) -> PeriodState:
        """Return a zero-valued state for the first period of the year.

        Returns:
            A :class:`PeriodState` with all counters and accumulators at zero.
        """
        return cls()


@dataclass(frozen=True)
class PeriodCalculationRequest:
    """Input for a single period-first payroll calculation.

    Attributes:
        period_id: The competence period (year, month). Governs all
            temporal lookups: salary table, tax rules, INPS rates.
        payment_date: Date on which the payment is made. Propagated to
            every ledger entry and pay item.
        ccnl_slug: Knowledge-bundle CCNL filename, e.g.
            ``metalmeccanico-federmeccanica.json``.
        level_code: Worker's contractual level code, e.g. ``C3``.
        opening_state: YTD state entering this period. Use
            :meth:`PeriodState.zero` for January.
        num_employees: Employer headcount used to resolve INPS rates
            (some rates differ by firm size). Defaults to 50.
        events: Variable work events (overtime, absences, bonuses, etc.)
            that occurred in this period. Defaults to no events.
        has_dependent_children: Whether the worker has at least one
            fiscally dependent child (figlio a carico).  Selects the
            higher fringe-benefit exemption threshold under Art. 51 c. 3
            TUIR.  Defaults to ``False``.
    """

    period_id: PeriodId
    payment_date: date
    ccnl_slug: str
    level_code: str
    opening_state: PeriodState = field(default_factory=PeriodState.zero)
    contract_type: Permanent | Apprentice | FixedTerm = field(default_factory=Permanent)
    num_employees: int = 50
    events: tuple[WorkEvent, ...] = field(default_factory=tuple)
    regione: str | None = None
    comune_belfiore: str | None = None
    family_composition: FamilyComposition | None = None
    has_dependent_children: bool = False


@dataclass(frozen=True)
class PeriodCalculationResult:
    """Result of one period-first payroll calculation.

    Attributes:
        period_id: The competence period, identical to the request.
        payment_date: Payment date, identical to the request.
        period_gross: Gross earnings for this period only.
        period_net: Net pay for this period only.
        period_employer_cost: Total employer cost for this period only.
        closing_state: YTD state after closing this period. Pass as
            ``opening_state`` to the next period's request.
        pay_items: All pay items produced for this period.
        ledger_entries: All ledger entries posted for this period.
        contribution_breakdown: Per-component INPS breakdown for audit
            and compliance tracing.
        benefit_breakdown: Per-axis fringe/welfare benefit breakdown for
            audit and cost-centre reporting.
    """

    period_id: PeriodId
    payment_date: date
    period_gross: Decimal
    period_net: Decimal
    period_employer_cost: Decimal
    closing_state: PeriodState
    pay_items: tuple[PayItem, ...]
    ledger_entries: tuple[LedgerEntry, ...]
    capability_report: CapabilityReport
    contribution_breakdown: ContributionBreakdown
    tax_computation: TaxComputation
    benefit_breakdown: BenefitBreakdown
