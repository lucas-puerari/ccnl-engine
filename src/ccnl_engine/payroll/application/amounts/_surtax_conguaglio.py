"""The surtax a conguaglio determines, and the decisions of its installments.

The conguaglio of tax year N takes the annual surtax of N
(:func:`~ccnl_engine.payroll.service.fiscal_surtax.compute_surtax`) and:

- regional: the whole amount, deferred to eleven installments of N+1
  (D.Lgs. 446/1997 art. 50 c. 4);
- municipal saldo: the municipal surtax of N less the acconto withheld in
  N, deferred like the regional (D.Lgs. 360/1998 art. 1 c. 5); an acconto
  withheld above the surtax due is given back now;
- municipal acconto of N+1: 30% (``SurtaxRules.comunale_advance_fraction``)
  of the municipal surtax computed on the taxable income of N with the
  rate and threshold in force in N (art. 1 c. 4), deferred to nine
  installments from March of N+1 (art. 1 c. 5).

On the last run of the employment nothing is deferred: the regional
surtax and the municipal saldo are withheld on the run and no acconto of
N+1 is determined.  The CU 2026 instructions (points 26 to 29) state that
at the cessazione "è necessario effettuare il calcolo dell'addizionale
effettivamente dovuta sugli ammontari erogati nell'anno", that an acconto
certified above the surtax due is withheld "al netto ... di quanto
eventualmente restituito", and that point 29 (acconto of the next year)
"non dovrà essere compilato".
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.domain.decisions import CalculationDecision, CalculationStatus
from ccnl_engine.payroll.domain.rounding import money
from ccnl_engine.payroll.domain.surtax_obligations import (
    SURTAX_WINDOWS,
    SurtaxComponent,
    SurtaxObligation,
    SurtaxPart,
)
from ccnl_engine.payroll.service.fiscal_surtax import (
    MUNICIPAL_SURTAX,
    REGIONAL_SURTAX,
)

if TYPE_CHECKING:
    from ccnl_engine.payroll.domain.recovery_plan import PostedInstallment
    from ccnl_engine.payroll.domain.ytd_accounts import TaxYtd
    from ccnl_engine.payroll.service.fiscal_surtax import SurtaxOutcome

__all__ = ["ConguaglioSurtax", "conguaglio_surtax", "installment_decision"]

_ZERO = Decimal(0)


@dataclass(frozen=True)
class ConguaglioSurtax:
    """What the conguaglio of the tax year withholds, defers and refunds.

    Attributes:
        parts: Surtax withheld on the run: only on the last run of the
            employment.
        obligations: Surtax deferred to the next tax year.
        refund: Surtax already withheld in the year above what is due,
            given back.
        decisions: One decision per component with a non-zero amount.
        regional_settled: Change of ``TaxYtd.regional_settled``.
        municipal_settled: Change of ``TaxYtd.municipal_settled``.
        advance_refunded: Part of ``refund`` taken from the acconto
            withheld in the year.
    """

    parts: tuple[SurtaxPart, ...] = ()
    obligations: tuple[SurtaxObligation, ...] = ()
    refund: Decimal = _ZERO
    decisions: tuple[CalculationDecision, ...] = ()
    regional_settled: Decimal = _ZERO
    municipal_settled: Decimal = _ZERO
    advance_refunded: Decimal = _ZERO


def installment_decision(
    obligation: SurtaxObligation, posted: PostedInstallment
) -> CalculationDecision:
    """Return the decision recording an installment of ``obligation``.

    Returns:
        A final decision of the regional or municipal surtax capability
        whose amount is the (positive) amount withheld.
    """
    window, plan = obligation.window, obligation.plan
    return CalculationDecision(
        capability=window.capability,
        status=CalculationStatus.FINAL,
        reason_code=posted.reason,
        rule=window.rule,
        rule_version=str(obligation.tax_year),
        inputs={
            "component": obligation.component.value,
            "reference_year": str(obligation.reference_year),
            "jurisdiction": obligation.jurisdiction,
            "installment_number": Decimal(plan.installments_posted + 1),
            "installments_total": Decimal(plan.installments_total),
            "residual_before": plan.residual,
        },
        amount=posted.amount,
    )


@dataclass(frozen=True)
class _Component:
    """One component of the conguaglio, with the annual decision it follows."""

    component: SurtaxComponent
    status: CalculationStatus
    tax_year: int
    jurisdiction: str
    amount: Decimal

    def decide(self, reason: str, **extra: Decimal | str) -> CalculationDecision:
        window = SURTAX_WINDOWS[self.component]
        reference = (
            self.tax_year + 1
            if self.component is SurtaxComponent.MUNICIPAL_ADVANCE
            else self.tax_year
        )
        return CalculationDecision(
            capability=window.capability,
            status=self.status,
            reason_code=reason,
            rule=window.rule,
            rule_version=str(self.tax_year),
            inputs={
                "component": self.component.value,
                "reference_year": str(reference),
                "jurisdiction": self.jurisdiction,
                **extra,
            },
            amount=self.amount,
        )


def _components(
    annual: SurtaxOutcome, year: int, tax: TaxYtd, *, final: bool, fraction: Decimal
) -> list[_Component]:
    """Return the components the conguaglio still has to settle.

    A component is determined only for a jurisdiction whose annual decision
    has an amount: an unknown table defers and refunds nothing.  The surtax
    of the year an earlier final conguaglio of the year withheld, and the
    acconto withheld, are deducted, so a second conguaglio in the year (a
    termination run after the last withholding slot) settles only the
    difference; a negative amount is withheld above what is due.

    Returns:
        The regional and municipal balance components, then the acconto of
        the next year when the employment continues.
    """
    decided = {d.capability: d for d in annual.decisions if d.amount is not None}
    components: list[_Component] = []
    regional = decided.get(REGIONAL_SURTAX)
    if regional is not None:
        components.append(
            _Component(
                SurtaxComponent.REGIONAL_BALANCE,
                regional.status,
                year,
                str(regional.inputs["code"]),
                annual.regional - tax.regional_settled,
            )
        )
    municipal = decided.get(MUNICIPAL_SURTAX)
    if municipal is None:
        return components
    status, comune = municipal.status, str(municipal.inputs["code"])
    balance = annual.municipal - tax.municipal_advance - tax.municipal_settled
    components.append(
        _Component(SurtaxComponent.MUNICIPAL_BALANCE, status, year, comune, balance)
    )
    if not final:
        advance = money(annual.municipal * fraction)
        components.append(
            _Component(SurtaxComponent.MUNICIPAL_ADVANCE, status, year, comune, advance)
        )
    return components


@dataclass
class _Settlement:
    """Accumulator of :func:`conguaglio_surtax`."""

    tax: TaxYtd
    parts: list[SurtaxPart] = field(default_factory=list)
    obligations: list[SurtaxObligation] = field(default_factory=list)
    decisions: list[CalculationDecision] = field(default_factory=list)
    refund: Decimal = _ZERO
    regional_settled: Decimal = _ZERO
    municipal_settled: Decimal = _ZERO
    advance_refunded: Decimal = _ZERO

    def settle(self, component: SurtaxComponent, amount: Decimal) -> None:
        """Record ``amount`` of a balance withheld (positive) or refunded."""
        if component is SurtaxComponent.REGIONAL_BALANCE:
            self.regional_settled += amount
            return
        from_saldo = max(amount, -self.tax.municipal_settled)
        self.municipal_settled += from_saldo
        self.advance_refunded += from_saldo - amount

    def result(self) -> ConguaglioSurtax:
        return ConguaglioSurtax(
            tuple(self.parts),
            tuple(self.obligations),
            self.refund,
            tuple(self.decisions),
            self.regional_settled,
            self.municipal_settled,
            self.advance_refunded,
        )


def conguaglio_surtax(
    annual: SurtaxOutcome,
    year: int,
    tax: TaxYtd,
    *,
    final: bool,
    fraction: Decimal,
) -> ConguaglioSurtax:
    """Withhold, defer or refund the annual surtax determined by the run.

    Args:
        annual: Annual surtax of the tax year.
        year: Tax year of the conguaglio.
        tax: Tax withheld in the year before the run.
        final: Whether the run is the last one of the employment.
        fraction: Share of the municipal surtax due as the acconto of the
            next tax year.

    Returns:
        On the last run of the employment the regional surtax and the
        positive municipal balance as parts of the run; otherwise the
        obligations of the next tax year.  A negative balance is refunded
        in both cases, the municipal one from the saldo withheld first.
    """
    out = _Settlement(tax)
    for c in _components(annual, year, tax, final=final, fraction=fraction):
        extra = (
            {"advance_withheld": tax.municipal_advance}
            if c.component is SurtaxComponent.MUNICIPAL_BALANCE
            else {}
        )
        if c.amount < _ZERO:
            out.refund -= c.amount
            out.settle(c.component, c.amount)
            out.decisions.append(c.decide("surtax_refunded", **extra))
        elif c.amount > _ZERO and final:
            out.parts.append(SurtaxPart(c.component, c.tax_year, c.amount))
            out.settle(c.component, c.amount)
            out.decisions.append(c.decide("withheld_at_termination", **extra))
        elif c.amount > _ZERO:
            obligation = SurtaxObligation.open(
                c.component, c.tax_year, c.jurisdiction, c.amount
            )
            out.obligations.append(obligation)
            installments = Decimal(obligation.plan.installments_total)
            out.decisions.append(
                c.decide(
                    "deferred_to_installments", installments_total=installments, **extra
                )
            )
    return out.result()
