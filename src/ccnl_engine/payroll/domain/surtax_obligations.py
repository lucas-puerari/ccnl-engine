"""Surtax determined by the conguaglio and withheld in the next tax year.

The conguaglio of tax year N determines the regional surtax and the
municipal saldo of N and the municipal acconto of N+1; all three are
withheld on the payslips of N+1:

- regional surtax: "trattenuto in un numero massimo di undici rate, a
  partire dal periodo di paga successivo a quello in cui le stesse sono
  effettuate e non oltre quello relativamente al quale le ritenute sono
  versate nel mese di dicembre" (D.Lgs. 446/1997 art. 50 c. 4);
- municipal saldo: the same eleven installments (D.Lgs. 360/1998 art. 1
  c. 5, second sentence);
- municipal acconto: "trattenuto in un numero massimo di nove rate
  mensili, effettuate a partire dal mese di marzo" (art. 1 c. 5, first
  sentence).

The withholding tax remitted in December is the one of the November pay
period (due by the 16th of the following month), so the last installment
falls on the November payslip: January to November for the balances,
March to November for the acconto, the conguaglio being on the last
payslip of N.  An installment is posted on each regular (monthly) payslip
of its window; extra-month, termination and adjustment payslips post none,
except that the last run of the employment withholds every residual at
once ("in caso di cessazione del rapporto l'importo è trattenuto in unica
soluzione", art. 50 c. 4; "l'addizionale residua dovuta è prelevata in
unica soluzione", art. 1 c. 5).  The installment arithmetic is the one of
:class:`~ccnl_engine.payroll.domain.recovery_plan.RecoveryPlan`.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum
from types import MappingProxyType
from typing import TYPE_CHECKING, final

from ccnl_engine.payroll.domain.recovery_plan import (
    InstallmentRun,
    PostedInstallment,
    RecoveryPlan,
)
from ccnl_engine.payroll.domain.remittance import (
    MUNICIPAL_SURTAX_ADVANCE,
    MUNICIPAL_SURTAX_BALANCE,
    REGIONAL_SURTAX,
)
from ccnl_engine.shared.domain.validation import (
    parse_enum,
    reject,
    require_instance,
    require_int,
    require_str,
)

if TYPE_CHECKING:
    from collections.abc import Mapping

__all__ = [
    "SURTAX_WINDOWS",
    "InstallmentWindow",
    "SurtaxComponent",
    "SurtaxObligation",
    "SurtaxPart",
]

_CENTS = Decimal(100)
_MIN_TAX_YEAR = 2020
_LAST_INSTALLMENT = "last_installment_posted"


class SurtaxComponent(StrEnum):
    """Part of the surtax a conguaglio determines."""

    REGIONAL_BALANCE = "regional_balance"
    """Regional surtax of the tax year (it has no acconto)."""
    MUNICIPAL_BALANCE = "municipal_balance"
    """Municipal surtax of the tax year less the acconto withheld in it."""
    MUNICIPAL_ADVANCE = "municipal_advance"
    """Municipal acconto of the next tax year."""


@final
@dataclass(frozen=True)
class InstallmentWindow:
    """When and under which rule the installments of a component fall.

    Attributes:
        first_month: Month of the first installment.
        last_month: Month of the last one, which takes the residual.
        rule: Identifier of the norm, recorded on each decision.
        remittance_code: F24 codice tributo of the amount withheld.
        capability: Capability of the decisions, as named in the catalog.
    """

    first_month: int
    last_month: int
    rule: str
    remittance_code: str
    capability: str

    @property
    def installments(self) -> int:
        """Number of monthly installments in the window."""
        return self.last_month - self.first_month + 1


#: Window of each component; see the module docstring for the sources.
SURTAX_WINDOWS: Mapping[SurtaxComponent, InstallmentWindow] = MappingProxyType({
    SurtaxComponent.REGIONAL_BALANCE: InstallmentWindow(
        1, 11, "dlgs446-1997-art50-c4", REGIONAL_SURTAX, "addizionale_regionale"
    ),
    SurtaxComponent.MUNICIPAL_BALANCE: InstallmentWindow(
        1,
        11,
        "dlgs360-1998-art1-c5",
        MUNICIPAL_SURTAX_BALANCE,
        "addizionale_comunale",
    ),
    SurtaxComponent.MUNICIPAL_ADVANCE: InstallmentWindow(
        3,
        11,
        "dlgs360-1998-art1-c5",
        MUNICIPAL_SURTAX_ADVANCE,
        "addizionale_comunale",
    ),
})


@final
@dataclass(frozen=True)
class SurtaxPart:
    """Surtax of one component a run withholds, before the pay cap.

    Attributes:
        component: What the amount is.
        reference_year: Tax year the surtax is due for.
        amount: Amount due on the run, positive.
    """

    component: SurtaxComponent
    reference_year: int
    amount: Decimal

    @property
    def stem(self) -> str:
        """Pay item and entry id stem, before the run tag."""
        return f"surtax_{self.component.value}_{self.reference_year}"

    @property
    def remittance_code(self) -> str:
        """F24 codice tributo of the component."""
        return SURTAX_WINDOWS[self.component].remittance_code


@final
@dataclass(frozen=True)
class SurtaxObligation:
    """Surtax a conguaglio determined, still to withhold in the next year.

    Attributes:
        component: What the amount is.
        tax_year: Tax year whose conguaglio determined it; it is withheld
            in ``tax_year + 1``.
        jurisdiction: Region code (ISO 3166-2:IT) or Belfiore code of the
            municipality it is due to: the one of the tax year of the
            conguaglio, not of the year it is withheld in.
        plan: The installments still to post; ``plan.kind`` is the
            component value.
    """

    component: SurtaxComponent
    tax_year: int
    jurisdiction: str
    plan: RecoveryPlan

    def __post_init__(self) -> None:
        """Validate the tax year, the jurisdiction and the plan.

        A ``tax_year`` before 2020, an empty ``jurisdiction``, a
        ``plan.kind`` other than the component value or a plan with more
        installments than the window raises
        :class:`~ccnl_engine.shared.domain.errors.InvalidInputError`.
        """
        owner, feature = "SurtaxObligation", "surtax_recovery"
        component = parse_enum(
            self.component, SurtaxComponent, f"{owner}.component", feature=feature
        )
        object.__setattr__(self, "component", component)
        require_int(
            self.tax_year, f"{owner}.tax_year", feature=feature, minimum=_MIN_TAX_YEAR
        )
        require_str(
            self.jurisdiction, f"{owner}.jurisdiction", feature=feature, non_blank=True
        )
        require_instance(self.plan, RecoveryPlan, f"{owner}.plan", feature=feature)
        if self.plan.kind != component.value:
            reject(
                f"{owner}.plan.kind",
                repr(component.value),
                self.plan.kind,
                feature=feature,
            )
        if self.plan.installments_total > self.window.installments:
            reject(
                f"{owner}.plan.installments_total",
                f"at most {self.window.installments} for {component.value}",
                self.plan.installments_total,
                feature=feature,
            )

    @property
    def window(self) -> InstallmentWindow:
        """Installment window of the component."""
        return SURTAX_WINDOWS[self.component]

    @property
    def withheld_in(self) -> int:
        """Tax year whose payslips withhold the installments."""
        return self.tax_year + 1

    @property
    def reference_year(self) -> int:
        """Tax year the surtax is due for: the next one for the acconto."""
        if self.component is SurtaxComponent.MUNICIPAL_ADVANCE:
            return self.withheld_in
        return self.tax_year

    @classmethod
    def open(
        cls,
        component: SurtaxComponent,
        tax_year: int,
        jurisdiction: str,
        amount: Decimal,
    ) -> SurtaxObligation:
        """Return the obligation of ``amount`` over the window.

        An amount below one cent per installment runs over fewer
        installments, so that none is zero.

        Returns:
            The obligation with no installment posted.

        Raises:
            ValueError: When ``amount`` is below one cent.
        """
        count = min(SURTAX_WINDOWS[component].installments, int(amount * _CENTS))
        if count < 1:
            msg = f"SurtaxObligation amount must be >= 0.01; got {amount}"
            raise ValueError(msg)
        return cls(
            component,
            tax_year,
            jurisdiction,
            RecoveryPlan.create(component.value, amount, count),
        )

    def part(self, amount: Decimal) -> SurtaxPart:
        """Return ``amount`` withheld of this obligation as a run part.

        Returns:
            The part of the component and reference year.
        """
        return SurtaxPart(self.component, self.reference_year, amount)

    def post(
        self, run: InstallmentRun, *, year: int, month: int, regular: bool
    ) -> tuple[PostedInstallment | None, SurtaxObligation | None]:
        """Return what a run of ``year`` and ``month`` withholds of it.

        The last run of the employment withholds the residual.  Otherwise a
        regular run of the window withholds the next installment, and the
        one of the last month, or any regular run after the window, the
        residual; nothing is withheld before the window, on another kind of
        run, or before :attr:`withheld_in`.

        Returns:
            What the run withholds, ``None`` when nothing, and the
            obligation after it, ``None`` once settled.
        """
        if year < self.withheld_in:
            return None, self
        if run.final:
            return self.plan.post(run), None
        window = self.window
        if not regular or (year == self.withheld_in and month < window.first_month):
            return None, self
        if year > self.withheld_in or month >= window.last_month:
            return PostedInstallment(self.plan.residual, _LAST_INSTALLMENT, None), None
        posted = self.plan.post(run)
        if posted.remaining is None:
            return posted, None
        return posted, SurtaxObligation(
            self.component, self.tax_year, self.jurisdiction, posted.remaining
        )
