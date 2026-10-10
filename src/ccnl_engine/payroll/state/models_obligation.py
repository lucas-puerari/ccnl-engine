"""Obligations of the employment that survive the change of tax year.

Unlike the payments and YTD accounts of
:class:`~ccnl_engine.payroll.state.models_tax_cash.TaxCashState`, which
carries them, nothing here restarts on 1 January: an installment
recovery opened by the conguaglio of year N keeps running on the payslips
of year N+1 until its last installment (D.L. 3/2020 art. 1 c. 3 for the
trattamento integrativo, L. 207/2024 art. 1 c. 7 for the somma esente and the ulteriore
detrazione).  On the last run of the employment the whole residual is
recovered instead (:meth:`~ccnl_engine.payroll.withholding.models_recovery_plan\
.RecoveryPlan.post`), so no recovery outlives the employment.  The surtax a
conguaglio of year N determines is withheld the same way on the payslips of
N+1 (:mod:`~ccnl_engine.payroll.state.models_surtax_obligation`), and so is the
IRPEF of a conguaglio the worker asked in writing to defer
(:mod:`~ccnl_engine.payroll.withholding.inputs_shortfall_deferral`).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, final

from ccnl_engine.payroll.withholding.models_recovery_plan import RecoveryPlan
from ccnl_engine.validation import (
    reject,
    require_instance,
    require_int,
)

if TYPE_CHECKING:
    from ccnl_engine.payroll.state.models_surtax_obligation import SurtaxObligation
    from ccnl_engine.payroll.withholding.inputs_shortfall_deferral import (
        DeferredShortfall,
    )
    from ccnl_engine.payroll.withholding.models_recovery_plan import (
        InstallmentRun,
        PostedInstallment,
    )

__all__ = [
    "RECOVERY_RULES",
    "SOMMA_ESENTE_RECOVERY",
    "TRATTAMENTO_RECOVERY",
    "ULTERIORE_RECOVERY",
    "EmploymentObligations",
    "RecoveryObligation",
    "RecoveryRule",
    "carried_item_id",
]

#: ``RecoveryPlan.kind`` of the trattamento integrativo recovery.
TRATTAMENTO_RECOVERY = "trattamento_integrativo"
#: ``RecoveryPlan.kind`` of the somma esente recovery.
SOMMA_ESENTE_RECOVERY = "somma_esente"
#: ``RecoveryPlan.kind`` of the ulteriore detrazione recovery.
ULTERIORE_RECOVERY = "ulteriore_detrazione_lavoro"
_MIN_TAX_YEAR = 2020


@final
@dataclass(frozen=True)
class RecoveryRule:
    """How the over-payment of one credit is recovered.

    Attributes:
        rule: Identifier of the norm, recorded on each installment decision.
        installments: Number of equal installments above the threshold.
    """

    rule: str
    installments: int


#: Recovery rule per recovered credit.  Every credit recovers up to 60 EUR on
#: one payslip; above it the installments differ.
RECOVERY_RULES: dict[str, RecoveryRule] = {
    TRATTAMENTO_RECOVERY: RecoveryRule(rule="dl3-2020-art1-c3", installments=8),
    SOMMA_ESENTE_RECOVERY: RecoveryRule(rule="l207-2024-art1-c7", installments=10),
    ULTERIORE_RECOVERY: RecoveryRule(rule="l207-2024-art1-c7", installments=10),
}


@final
@dataclass(frozen=True)
class RecoveryObligation:
    """An installment recovery and the tax year of the credit it recovers.

    Attributes:
        tax_year: Tax year whose conguaglio found the credit not due.  The
            installments posted in that year enter the ``recovered`` total
            of its :class:`~ccnl_engine.payroll.state.models_ytd_account\
.CreditAccount`; those posted in a later year are carried: they are
            deducted on the payslip but belong to no account of the later
            year.
        plan: The installment plan, with the installments still to post.
    """

    tax_year: int
    plan: RecoveryPlan

    def __post_init__(self) -> None:
        """Validate the origin tax year and the recovered credit.

        Only the recoveries of :data:`RECOVERY_RULES` are modelled; a plan of
        another kind is rejected rather than carried without effect.

        A ``tax_year`` before 2020 or a ``plan.kind`` that is not a key of
        :data:`RECOVERY_RULES` raises
        :class:`~ccnl_engine.errors.InvalidInputError`.
        """
        feature = "recovery"
        require_int(
            self.tax_year,
            "RecoveryObligation.tax_year",
            feature=feature,
            minimum=_MIN_TAX_YEAR,
        )
        require_instance(
            self.plan, RecoveryPlan, "RecoveryObligation.plan", feature=feature
        )
        if self.plan.kind not in RECOVERY_RULES:
            reject(
                "RecoveryObligation.plan.kind",
                f"one of {sorted(RECOVERY_RULES)}",
                self.plan.kind,
                feature=feature,
            )

    def post(
        self, run: InstallmentRun
    ) -> tuple[PostedInstallment, RecoveryObligation | None]:
        """Return what ``run`` recovers and the obligation after it.

        Returns:
            :meth:`RecoveryPlan.post` of the plan and the obligation still
            running, ``None`` once the plan is settled.
        """
        posted = self.plan.post(run)
        if posted.remaining is None:
            return posted, None
        return posted, RecoveryObligation(tax_year=self.tax_year, plan=posted.remaining)


@final
@dataclass(frozen=True)
class EmploymentObligations:
    """Obligations carried from run to run across tax years.

    Attributes:
        recoveries: Active installment recoveries, at most one per credit
            kind and origin tax year, in the order they were opened.
        surtax: Surtax still to withhold, at most one per component and
            tax year of the conguaglio that determined it, oldest first.
        deferred_shortfall: IRPEF of a conguaglio deferred on the worker's
            written request, at most one per tax year of the conguaglio.
    """

    recoveries: tuple[RecoveryObligation, ...] = ()
    surtax: tuple[SurtaxObligation, ...] = ()
    deferred_shortfall: tuple[DeferredShortfall, ...] = ()

    def __post_init__(self) -> None:
        """Reject two recoveries of the same credit opened in the same year.

        Raises:
            ValueError: When two recoveries share ``tax_year`` and kind, two
                surtax obligations share ``tax_year`` and component, or two
                deferred shortfalls share ``tax_year``.
        """
        deferred = [d.tax_year for d in self.deferred_shortfall]
        if len(set(deferred)) != len(deferred):
            msg = (
                "EmploymentObligations.deferred_shortfall holds two deferrals "
                f"of the same tax year: {deferred}"
            )
            raise ValueError(msg)
        surtax = [(o.tax_year, o.component) for o in self.surtax]
        if len(set(surtax)) != len(surtax):
            msg = (
                "EmploymentObligations.surtax holds two obligations of the "
                f"same component determined in the same tax year: {surtax}"
            )
            raise ValueError(msg)
        keys = [(r.tax_year, r.plan.kind) for r in self.recoveries]
        if len(set(keys)) != len(keys):
            msg = (
                "EmploymentObligations.recoveries holds two recoveries of the "
                f"same credit opened in the same tax year: {keys}"
            )
            raise ValueError(msg)

    @property
    def latest_tax_year(self) -> int | None:
        """Latest origin tax year of any obligation, ``None`` without one."""
        years = [r.tax_year for r in self.recoveries]
        years.extend(o.tax_year for o in self.surtax)
        years.extend(d.tax_year for d in self.deferred_shortfall)
        return max(years, default=None)

    def deferred_of(self, tax_year: int) -> DeferredShortfall | None:
        """Return the IRPEF deferred by the conguaglio of ``tax_year``.

        Returns:
            The deferred shortfall, or ``None``.
        """
        return next(
            (d for d in self.deferred_shortfall if d.tax_year == tax_year), None
        )

    def recovery_of(self, tax_year: int, kind: str) -> RecoveryPlan | None:
        """Return the plan of credit ``kind`` opened in ``tax_year``, if any.

        Returns:
            The matching plan, or ``None``.
        """
        return next(
            (
                r.plan
                for r in self.recoveries
                if r.tax_year == tax_year and r.plan.kind == kind
            ),
            None,
        )

    def carried_into(self, tax_year: int) -> tuple[RecoveryObligation, ...]:
        """Return the recoveries opened before ``tax_year``.

        Returns:
            The recoveries whose origin year is earlier than ``tax_year``,
            in their stored order.
        """
        return tuple(r for r in self.recoveries if r.tax_year < tax_year)


def carried_item_id(obligation: RecoveryObligation, run_id: str) -> str:
    """Return the pay item id of a carried installment on ``run_id``.

    Returns:
        ``"{kind}_recovery_{origin year}_{run_id}"``.
    """
    return f"{obligation.plan.kind}_recovery_{obligation.tax_year}_{run_id}"
