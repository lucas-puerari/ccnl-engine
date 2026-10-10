"""Rows of the surtax tables: amounts, decisions and issues of one code.

:class:`SurtaxTable` builds the decision and the issues for the row found
(or not found) for one region or Belfiore code;
:func:`regional_surtax_amount` applies a regional row: its brackets, its
whole-income rate and its income-only deductions.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from ccnl_engine.payroll.amount.policies_rounding import money
from ccnl_engine.payroll.assurance.models_decision import (
    CalculationDecision,
    CalculationIssue,
    CalculationStatus,
)
from ccnl_engine.payroll.family.inputs import DependentRelationship
from ccnl_engine.payroll.taxation import rules_irpef as _irpef

if TYPE_CHECKING:
    from ccnl_engine.payroll.family.inputs import FamilyComposition
    from ccnl_engine.provenance.ruleset.models import RulesetIdentity
    from ccnl_engine.tax.surtax.models_table import RegionalDeduction, RegionaleEntry

__all__ = [
    "DEPENDENT_PROVISIONS_ISSUE",
    "PRIOR_YEAR_RATES_ISSUE",
    "SPECIFIC_EXEMPTIONS_ISSUE",
    "SurtaxTable",
    "has_dependent_child_or_disability",
    "regional_surtax_amount",
]

_ZERO = Decimal(0)
_ONE = Decimal(1)

#: Issue of a municipal surtax computed on the rates of an earlier year.
PRIOR_YEAR_RATES_ISSUE = "municipal_surtax_prior_year_rates"
#: Issue of a regional row whose provisions for dependents are not applied.
DEPENDENT_PROVISIONS_ISSUE = "regional_surtax_dependent_provisions_not_applied"
#: Issue of a municipal row whose category-specific exemptions are not applied.
SPECIFIC_EXEMPTIONS_ISSUE = "municipal_surtax_specific_exemptions_not_applied"


@dataclass(frozen=True, slots=True)
class SurtaxTable:
    """The bundled table of one jurisdiction, as looked up for a code.

    Attributes:
        capability: Capability of the decision (regional or municipal).
        unknown_issue: Issue code of a code without a row in the table.
        code: Region or Belfiore code supplied by the caller.
        name: Name of the row found, ``None`` when the code has none.
        ruleset: Identity of the bundled table, when recorded.
        tax_year: Tax year of the table.
        taxable_income: Annual taxable income the surtax is computed on.
    """

    capability: str
    unknown_issue: str
    code: str
    name: str | None
    ruleset: RulesetIdentity | None
    tax_year: int
    taxable_income: Decimal

    def decide(
        self,
        reason_code: str,
        amount: Decimal | None,
        status: CalculationStatus = CalculationStatus.FINAL,
        **extra: Decimal | str,
    ) -> CalculationDecision:
        """Return the decision of this code with the given reason.

        A decision without an amount is ``incomplete`` whatever ``status``.

        Returns:
            The decision, with the code, row, tax year and income as inputs.
        """
        default_rule = f"surtax/{self.tax_year}/{self.capability}"
        return CalculationDecision(
            capability=self.capability,
            status=status if amount is not None else CalculationStatus.INCOMPLETE,
            reason_code=reason_code,
            rule=default_rule if self.ruleset is None else self.ruleset.id,
            rule_version=(
                str(self.tax_year) if self.ruleset is None else self.ruleset.version
            ),
            inputs={
                "code": self.code,
                "table": "unknown" if self.name is None else self.name,
                "tax_year": str(self.tax_year),
                "taxable_income": self.taxable_income,
                **extra,
            },
            amount=amount,
        )

    def issues_of(
        self, decision: CalculationDecision, *extra: CalculationIssue
    ) -> tuple[CalculationIssue, ...]:
        """Return the issues of ``decision``, followed by ``extra``.

        Returns:
            The prior-year-rates issue, the unknown-table issue (``extra``
            is then dropped: nothing was computed) or only ``extra``.
        """
        if decision.reason_code == "prior_year_rates_applied":
            rates_year = decision.inputs.get("rates_year", str(self.tax_year - 1))
            issue = CalculationIssue(
                code=PRIOR_YEAR_RATES_ISSUE,
                message=(
                    f"{self.capability}: the bundled table holds the rates "
                    f"of {rates_year} for code {self.code!r}; the surtax of "
                    f"{self.tax_year} and the acconto of {self.tax_year + 1} "
                    "are computed on them until the rates of the tax year "
                    "are bundled"
                ),
                status=CalculationStatus.PROVISIONAL,
            )
            return (issue, *extra)
        if decision.amount is not None:
            return extra
        issue = CalculationIssue(
            code=self.unknown_issue,
            message=(
                f"{self.capability}: no {self.tax_year} table for code "
                f"{self.code!r}; the surtax is not withheld and the result "
                "must not be paid as is"
            ),
            status=CalculationStatus.INCOMPLETE,
        )
        return (issue,)

    def provisional_issue(self, code: str, detail: str) -> CalculationIssue:
        """Return a provisional issue of this code.

        Returns:
            The issue, its message prefixed with capability and code.
        """
        return CalculationIssue(
            code=code,
            message=f"{self.capability} for code {self.code!r}: {detail}",
            status=CalculationStatus.PROVISIONAL,
        )


def has_dependent_child_or_disability(family: FamilyComposition | None) -> bool:
    """Whether a regional provision for dependents may apply to the worker.

    Returns:
        ``True`` when the family declares a child or a disabled dependent.
    """
    if family is None:
        return False
    return any(
        d.relationship is DependentRelationship.CHILD or d.disabled
        for d in family.dependents
    )


def _regional_deduction(income: Decimal, deduction: RegionalDeduction) -> Decimal:
    if income <= deduction.income_above:
        return _ZERO
    if deduction.income_up_to is not None and income > deduction.income_up_to:
        return _ZERO
    if deduction.phase_in is None:
        return deduction.amount
    share = min(_ONE, (income - deduction.income_above) / deduction.phase_in)
    return money(deduction.amount * share)


def regional_surtax_amount(income: Decimal, entry: RegionaleEntry) -> Decimal:
    """Compute the regional surtax of one row on the annual taxable income.

    The row's whole-income rate replaces its brackets up to its limit; the
    income-only deductions are then subtracted and the result floored at
    zero (the regional deductions never create a credit).  The exemption
    threshold is checked by the caller.

    Args:
        income: Annual IRPEF taxable income.
        entry: Row of the regional table.

    Returns:
        The annual regional surtax, rounded to two decimal places.
    """
    whole = entry.whole_income_rate
    if whole is not None and income <= whole.income_up_to:
        gross = money(income * whole.rate)
    else:
        gross = _irpef.surtax_from_brackets(income, entry.brackets)
    deducted = sum((_regional_deduction(income, d) for d in entry.deductions), _ZERO)
    return money(max(_ZERO, gross - deducted))
