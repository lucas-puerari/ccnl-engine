"""Regional and municipal surtax withheld on one run.

The surtax of tax year N is determined once, by the conguaglio (the run
that closes the last withholding slot of N, or the last run of the
employment), and withheld on the payslips of N+1 by statutory
installments (:mod:`~ccnl_engine.payroll.domain.surtax_obligations`).  A
run therefore withholds:

- the installments due on it of the surtax determined by an earlier
  conguaglio, carried in the opening obligations;
- on the last run of the employment, the whole surtax of its own tax year
  as well (:mod:`~ccnl_engine.payroll.application.amounts._surtax_conguaglio`);
- the surtax an earlier run of the year could not withhold for lack of
  pay, first.

Surtax withheld in the year above what the conguaglio finds due (usually
the municipal acconto) is given back on a separate refund line.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.application.amounts._surtax_conguaglio import (
    ConguaglioSurtax,
    conguaglio_surtax,
    installment_decision,
)
from ccnl_engine.payroll.domain.surtax_obligations import (
    SurtaxComponent,
    SurtaxPart,
)
from ccnl_engine.payroll.service.fiscal_surtax import SurtaxOutcome, compute_surtax

if TYPE_CHECKING:
    from ccnl_engine.payroll.application.amounts._types import _AmountsInput
    from ccnl_engine.payroll.domain.decisions import (
        CalculationDecision,
        CalculationIssue,
    )
    from ccnl_engine.payroll.domain.surtax_obligations import SurtaxObligation

__all__ = ["RunSurtax", "run_surtax"]

_ZERO = Decimal(0)


@dataclass(frozen=True)
class RunSurtax:
    """What one run withholds and determines of the surtax.

    Attributes:
        annual: The annual surtax the conguaglio determined, or the
            ``determined_at_conguaglio`` decisions of another run.
        parts: Surtax due on the run by component, in withholding order.
        carried_in: Surtax of earlier runs not withheld for lack of pay.
        refund: Surtax given back by the conguaglio.
        obligations: Surtax still to withhold after the run.
        decisions: Installment and conguaglio decisions, after those of
            ``annual``.
        conguaglio: What the conguaglio of the run settled, empty on any
            other run.
    """

    annual: SurtaxOutcome = field(default_factory=SurtaxOutcome)
    parts: tuple[SurtaxPart, ...] = ()
    carried_in: Decimal = _ZERO
    refund: Decimal = _ZERO
    obligations: tuple[SurtaxObligation, ...] = ()
    decisions: tuple[CalculationDecision, ...] = ()
    conguaglio: ConguaglioSurtax = field(default_factory=ConguaglioSurtax)

    @property
    def due(self) -> Decimal:
        """Surtax the run must withhold before the pay cap."""
        return self.carried_in + sum((p.amount for p in self.parts), _ZERO)

    @property
    def issues(self) -> tuple[CalculationIssue, ...]:
        """Issues of the annual surtax tables."""
        return self.annual.issues

    @property
    def all_decisions(self) -> tuple[CalculationDecision, ...]:
        """Annual decisions, then the installment and conguaglio ones."""
        return self.annual.decisions + self.decisions

    def allocate(
        self, withheld: Decimal
    ) -> tuple[tuple[SurtaxPart | None, Decimal], ...]:
        """Split the surtax withheld after the cap over what was due.

        The surtax carried in is withheld first, then the parts in order;
        what the pay does not cover is the shortfall of the run.

        Returns:
            ``(part, amount)`` pairs, ``None`` for the surtax carried in,
            each amount at most what was due on it.
        """
        left = withheld
        shares: list[tuple[SurtaxPart | None, Decimal]] = []
        for part, due in (
            (None, self.carried_in),
            *((p, p.amount) for p in self.parts),
        ):
            share = min(due, left)
            left -= share
            shares.append((part, share))
        return tuple(shares)

    def advance_withheld(self, withheld: Decimal, tax_year: int) -> Decimal:
        """Return the acconto of ``tax_year`` among the surtax withheld.

        Returns:
            The share of ``withheld`` allocated to the municipal acconto
            due for ``tax_year``.
        """
        return sum(
            (
                amount
                for part, amount in self.allocate(withheld)
                if part is not None
                and part.component is SurtaxComponent.MUNICIPAL_ADVANCE
                and part.reference_year == tax_year
            ),
            _ZERO,
        )


def _installments(
    inp: _AmountsInput,
) -> tuple[list[SurtaxPart], list[SurtaxObligation], list[CalculationDecision]]:
    """Post the installments of the surtax obligations the run opened with.

    On the conguaglio the acconto of the tax year is not posted: the
    conguaglio deducts what was withheld of it from the municipal surtax.
    Nor is the surtax an earlier conguaglio of the same year deferred (a
    termination run after the last withholding slot): nothing of it was
    withheld, and the conguaglio determines it again.

    Returns:
        The parts withheld, the obligations still running and one decision
        per installment.
    """
    year = inp.rules.year
    parts: list[SurtaxPart] = []
    remaining: list[SurtaxObligation] = []
    decisions: list[CalculationDecision] = []
    for obligation in inp.surtax_obligations:
        if inp.conguaglio and (
            obligation.tax_year == year
            or (
                obligation.component is SurtaxComponent.MUNICIPAL_ADVANCE
                and obligation.reference_year == year
            )
        ):
            continue
        posted, after = obligation.post(
            inp.installment_run,
            year=year,
            month=inp.run_month,
            regular=inp.regular_run,
        )
        if posted is not None:
            parts.append(obligation.part(posted.amount))
            decisions.append(installment_decision(obligation, posted))
        if after is not None:
            remaining.append(after)
    return parts, remaining, decisions


def run_surtax(inp: _AmountsInput, taxable: Decimal, irpef_due: Decimal) -> RunSurtax:
    """Return the surtax the run withholds and determines.

    D.Lgs. 446/1997 art. 50 c. 2 and D.Lgs. 360/1998 art. 1 c. 4: the
    surtax is due only when the IRPEF net of its deductions is due.

    Args:
        inp: Inputs of the run.
        taxable: Annual taxable income; final on the conguaglio.
        irpef_due: Annual IRPEF net of the deductions.

    Returns:
        The installments, the conguaglio and the surtax carried in; no
        annual decision without surtax rules.
    """
    parts, remaining, decisions = _installments(inp)
    carried_in = inp.opening.shortfall.surtax
    if inp.surtax_rules is None:
        return RunSurtax(
            parts=tuple(parts),
            carried_in=carried_in,
            obligations=tuple(remaining),
            decisions=tuple(decisions),
        )
    annual = compute_surtax(
        taxable,
        inp.surtax_rules,
        regione=inp.regione,
        comune_belfiore=inp.comune_belfiore,
        irpef_due=irpef_due,
        at_conguaglio=inp.conguaglio,
        family_composition=inp.family_composition,
    )
    if not inp.conguaglio:
        return RunSurtax(
            annual, tuple(parts), carried_in, _ZERO, tuple(remaining), tuple(decisions)
        )
    settled = conguaglio_surtax(
        annual,
        inp.rules.year,
        inp.opening.tax,
        final=inp.installment_run.final,
        fraction=inp.surtax_rules.comunale_advance_fraction,
    )
    return RunSurtax(
        annual,
        (*parts, *settled.parts),
        carried_in,
        settled.refund,
        (*remaining, *settled.obligations),
        (*decisions, *settled.decisions),
        settled,
    )
