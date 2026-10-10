"""Art. 12 TUIR family deductions of one run, on the reddito complessivo.

The reddito complessivo is the employment income of the year this run
projects plus the income of :class:`~ccnl_engine.payroll.domain\
.current_year.CurrentYearTaxFacts`.  When no dependent gives right to a
deduction in any month, or this employment alone takes every deduction past
its phase-out, the deductions are zero whatever the other income and the
facts are not needed.  Otherwise, without facts of the tax year, the run
computes the deductions on its own income as a simulation, the provisional
decision carries no amount and an incomplete issue names the missing fact,
so the result is incomplete and not payable.  A dependant that may qualify
with a condition of art. 12 left unknown is handled the same way: it takes
no deduction in the simulation and an issue names each unknown condition.
An estimated income on the conguaglio leaves the decision provisional: the
conguaglio settles the year on final figures.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from typing import TYPE_CHECKING

from ccnl_engine.payroll.domain.current_year import IncomeEstimateQuality
from ccnl_engine.payroll.domain.decisions import (
    CalculationDecision,
    CalculationIssue,
    CalculationStatus,
)
from ccnl_engine.payroll.domain.family import DependentRelationship
from ccnl_engine.payroll.service.family.deductions import compute_family_deductions

if TYPE_CHECKING:
    from decimal import Decimal

    from ccnl_engine.payroll.domain.current_year import CurrentYearTaxFacts
    from ccnl_engine.payroll.domain.family import FamilyComposition
    from ccnl_engine.payroll.service.family.deductions import FamilyDeductions
    from ccnl_engine.tax.family.models import FamilyDeductionRules

__all__ = ["CAPABILITY", "FACT", "RunFamily", "resolve_family"]

CAPABILITY = "family_deductions"
FACT = "current_year"
REQUIRED_FACT_MISSING = "required_fact_missing"
_NONE = "none"


@dataclass(frozen=True)
class RunFamily:
    """Family deductions of the run and the income they were computed on.

    Attributes:
        family: Family composition of the request.
        rules: Art. 12 rules of the tax year.
        facts: Current-year facts of the request, if supplied.
        own_income: Employment income of the year projected by the run.
        conguaglio: Whether the run settles the tax year.
    """

    family: FamilyComposition
    rules: FamilyDeductionRules
    facts: CurrentYearTaxFacts | None
    own_income: Decimal
    conguaglio: bool

    @property
    def usable_facts(self) -> CurrentYearTaxFacts | None:
        """The facts when they are of the tax year of the run."""
        facts = self.facts
        return (
            facts if facts is not None and facts.tax_year == self.rules.year else None
        )

    def income(self, own_income: Decimal) -> Decimal:
        """Return the reddito complessivo with ``own_income`` from this job.

        Returns:
            ``own_income`` plus the external income of the facts; ``own_income``
            alone without usable facts (the simulation).
        """
        facts = self.usable_facts
        return own_income if facts is None else own_income + facts.external_income

    def deductions_at(self, own_income: Decimal) -> FamilyDeductions:
        """Return the deductions with ``own_income`` from this employment.

        Returns:
            The deductions of every dependent.
        """
        return compute_family_deductions(
            self.family, self.income(own_income), self.rules
        )

    @cached_property
    def deductions(self) -> FamilyDeductions:
        """Deductions on the projected income of the run."""
        return self.deductions_at(self.own_income)

    @property
    def undetermined(self) -> bool:
        """Whether the deductions depend on income the run does not know.

        Above zero, a deduction is zero only past its phase-out, where more
        income keeps it zero: when this employment alone exhausts every
        deduction, the other income cannot change them.
        """
        deductions = self.deductions
        exhausted = self.own_income > 0 and deductions.exhausted
        return self.usable_facts is None and deductions.entitled and not exhausted

    @property
    def missing_facts(self) -> tuple[str, ...]:
        """Conditions of art. 12 a dependant that may qualify leaves unknown."""
        return self.deductions.missing_facts

    @property
    def estimated_at_conguaglio(self) -> bool:
        """Whether the conguaglio rests on an estimated external income."""
        facts = self.usable_facts
        return (
            self.conguaglio
            and self.deductions.entitled
            and facts is not None
            and facts.quality is IncomeEstimateQuality.ESTIMATED
        )

    def issues(self) -> tuple[CalculationIssue, ...]:
        """Return the missing-fact issues of undetermined deductions.

        Returns:
            An incomplete issue naming ``current_year`` when the income is
            unknown, and one per unknown condition of a dependant.
        """
        income = self._income_issue()
        facts = tuple(_fact_issue(fact) for fact in self.missing_facts)
        return facts if income is None else (income, *facts)

    def _income_issue(self) -> CalculationIssue | None:
        if not self.undetermined:
            return None
        facts = self.facts
        found = (
            "no current-year facts"
            if facts is None
            else f"current-year facts of {facts.tax_year}"
        )
        return CalculationIssue(
            code="family_income_unknown",
            message=(
                "the art. 12 TUIR family deductions depend on the reddito "
                f"complessivo of {self.rules.year}, and the run has {found}: "
                "state the income beyond this employment (zero included); the "
                "deductions shown are a simulation on this employment alone"
            ),
            status=CalculationStatus.INCOMPLETE,
            fact=FACT,
        )

    def decision(self) -> CalculationDecision:
        """Return the decision of the family deductions of the run.

        Returns:
            A decision whose reason is ``deductions_applied``,
            ``no_deduction_due``, ``required_fact_missing`` (the income or
            a condition of a dependant unknown) or
            ``estimated_income_at_conguaglio``.
        """
        deductions = self.deductions
        total = deductions.total
        if self.undetermined or self.missing_facts:
            # Provisional, not incomplete, like the IVS and seniority
            # decisions: the run read the rules for its simulation, so they
            # stay in its rulesets; the incomplete issue blocks payment.
            status, reason, amount = (
                CalculationStatus.PROVISIONAL,
                REQUIRED_FACT_MISSING,
                None,
            )
        elif self.estimated_at_conguaglio:
            status, reason, amount = (
                CalculationStatus.PROVISIONAL,
                "estimated_income_at_conguaglio",
                total,
            )
        else:
            status = CalculationStatus.FINAL
            reason = "deductions_applied" if total else "no_deduction_due"
            amount = total
        ruleset = self.rules.ruleset
        return CalculationDecision(
            capability=CAPABILITY,
            status=status,
            reason_code=reason,
            rule=f"tax/{self.rules.year}/family-deductions"
            if ruleset is None
            else ruleset.id,
            rule_version=str(self.rules.year) if ruleset is None else ruleset.version,
            inputs=self._inputs(deductions),
            amount=amount,
        )

    def _inputs(self, deductions: FamilyDeductions) -> dict[str, Decimal | str]:
        facts = self.usable_facts
        inputs: dict[str, Decimal | str] = {
            "own_income": self.own_income,
            "reddito_complessivo": (
                "undetermined" if self.undetermined else self.income(self.own_income)
            ),
            "external_income": _NONE if facts is None else facts.external_income,
            "estimated_on": _NONE if facts is None else facts.estimated_on.isoformat(),
            "estimate_quality": _NONE if facts is None else facts.quality.value,
            "months": ",".join(
                f"{d.dependent.relationship.value}:{d.months}"
                for d in deductions.dependents
            ),
        }
        for kind in DependentRelationship:
            inputs[kind.value] = deductions.of(kind)
        if self.missing_facts:
            inputs["missing_facts"] = ",".join(self.missing_facts)
        if self.undetermined:
            inputs["simulated_amount"] = deductions.total
        return inputs


def _fact_issue(fact: str) -> CalculationIssue:
    return CalculationIssue(
        code="dependent_condition_unknown",
        message=(
            f"a dependant may give right to an art. 12 TUIR deduction and "
            f"leaves Dependent.{fact} unknown: state it; until then the "
            "dependant takes no deduction"
        ),
        status=CalculationStatus.INCOMPLETE,
        fact=fact,
    )


def resolve_family(
    family: FamilyComposition | None,
    rules: FamilyDeductionRules | None,
    facts: CurrentYearTaxFacts | None,
    own_income: Decimal,
    *,
    conguaglio: bool,
) -> RunFamily | None:
    """Return the family deductions of a run.

    Returns:
        ``None`` without a family composition or its rules: the deductions
        were not computed.
    """
    if family is None or rules is None:
        return None
    return RunFamily(family, rules, facts, own_income, conguaglio)
